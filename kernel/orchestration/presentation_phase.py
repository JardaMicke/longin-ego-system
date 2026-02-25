"""
Presentation Phase - ERTDSD Merge Workflow and UI Notifications
Integrates results from previous phases and presents them to the user with merge workflows and notifications
"""

import asyncio
import json
import logging
import time
import hashlib
import shutil
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import re
import subprocess
import tempfile

from redis_bus import RedisBus
from global_arbiter import GlobalArbiter
from identity_firewall import IdentityFirewall
from bikameral_memory import BikameralMemory
from chronos_heartbeat import ChronosHeartbeat

logger = logging.getLogger(__name__)

@dataclass
class MergeResult:
    """Result of code merge operation"""
    merge_id: str
    status: str  # success, conflict, failed
    merged_files: List[str]
    conflicts: List[Dict[str, Any]]
    validation_results: Dict[str, Any]
    merge_time: float
    rollback_available: bool

@dataclass
class UINotification:
    """UI notification for user"""
    notification_id: str
    type: str  # info, success, warning, error
    title: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    read: bool = False
    persistent: bool = False

@dataclass
class PresentationSession:
    """Presentation session tracking"""
    session_id: str
    contract_id: str
    implementation_session_id: str
    start_time: datetime
    merge_results: List[MergeResult]
    notifications: List[UINotification]
    final_report: Optional[Dict[str, Any]] = None
    completion_status: str = "pending"

class CodeMerger:
    """Handles code merging and conflict resolution"""
    
    def __init__(self, target_directory: str):
        self.target_directory = Path(target_directory)
        self.merge_strategies = {
            'overwrite': self._merge_overwrite,
            'append': self._merge_append,
            'prepend': self._merge_prepend,
            'smart': self._merge_smart,
            'manual': self._merge_manual
        }
        
    async def merge_implementation(self, implementation: Dict[str, Any], merge_strategy: str = 'smart') -> MergeResult:
        """Merge implementation into target codebase"""
        merge_id = hashlib.md5(f"{implementation['component_name']}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        start_time = time.time()
        
        try:
            logger.info(f"Starting merge for {implementation['component_name']} using strategy {merge_strategy}")
            
            # Validate implementation
            validation = await self._validate_implementation(implementation)
            if not validation['valid']:
                return MergeResult(
                    merge_id=merge_id,
                    status='failed',
                    merged_files=[],
                    conflicts=[],
                    validation_results=validation,
                    merge_time=time.time() - start_time,
                    rollback_available=False
                )
            
            # Create backup for rollback
            backup_created = await self._create_backup(implementation)
            
            # Perform merge
            if merge_strategy in self.merge_strategies:
                merge_result = await self.merge_strategies[merge_strategy](implementation)
            else:
                merge_result = await self._merge_smart(implementation)
            
            merge_result.merge_id = merge_id
            merge_result.merge_time = time.time() - start_time
            merge_result.rollback_available = backup_created
            
            # Validate merged code
            post_merge_validation = await self._validate_merged_code(merge_result)
            merge_result.validation_results = post_merge_validation
            
            logger.info(f"Merge completed for {implementation['component_name']}: {merge_result.status}")
            return merge_result
            
        except Exception as e:
            logger.error(f"Merge failed for {implementation['component_name']}: {e}")
            return MergeResult(
                merge_id=merge_id,
                status='failed',
                merged_files=[],
                conflicts=[],
                validation_results={'error': str(e)},
                merge_time=time.time() - start_time,
                rollback_available=False
            )
    
    async def _validate_implementation(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Validate implementation before merge"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check code content
        if not implementation.get('code_content'):
            validation['errors'].append('No code content provided')
            validation['valid'] = False
        
        # Check syntax
        try:
            import ast
            ast.parse(implementation['code_content'])
        except SyntaxError as e:
            validation['errors'].append(f'Syntax error in code: {e}')
            validation['valid'] = False
        
        # Check security
        security_issues = await self._check_security_issues(implementation['code_content'])
        if security_issues:
            validation['warnings'].extend(security_issues)
        
        return validation
    
    async def _check_security_issues(self, code_content: str) -> List[str]:
        """Check for security issues in code"""
        issues = []
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, code_content, re.IGNORECASE):
                issues.append('Potential hardcoded secret detected')
                break
        
        # Check for unsafe operations
        unsafe_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'os\.system\s*\('
        ]
        
        for pattern in unsafe_patterns:
            if re.search(pattern, code_content):
                issues.append('Potentially unsafe operation detected')
                break
        
        return issues
    
    async def _create_backup(self, implementation: Dict[str, Any]) -> bool:
        """Create backup for rollback"""
        try:
            backup_dir = self.target_directory / 'backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup existing files that will be overwritten
            component_name = implementation['component_name']
            target_file = self.target_directory / f"{component_name}.py"
            
            if target_file.exists():
                backup_file = backup_dir / f"{component_name}.py.backup"
                shutil.copy2(target_file, backup_file)
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False
    
    async def _merge_overwrite(self, implementation: Dict[str, Any]) -> MergeResult:
        """Merge by overwriting existing files"""
        component_name = implementation['component_name']
        target_file = self.target_directory / f"{component_name}.py"
        
        try:
            # Write new content
            target_file.write_text(implementation['code_content'])
            
            return MergeResult(
                merge_id="",
                status='success',
                merged_files=[str(target_file)],
                conflicts=[],
                validation_results={},
                merge_time=0.0,
                rollback_available=True
            )
            
        except Exception as e:
            return MergeResult(
                merge_id="",
                status='failed',
                merged_files=[],
                conflicts=[{'file': str(target_file), 'error': str(e)}],
                validation_results={},
                merge_time=0.0,
                rollback_available=False
            )
    
    async def _merge_append(self, implementation: Dict[str, Any]) -> MergeResult:
        """Merge by appending to existing files"""
        component_name = implementation['component_name']
        target_file = self.target_directory / f"{component_name}.py"
        
        try:
            if target_file.exists():
                existing_content = target_file.read_text()
                new_content = existing_content + "\n\n" + implementation['code_content']
            else:
                new_content = implementation['code_content']
            
            target_file.write_text(new_content)
            
            return MergeResult(
                merge_id="",
                status='success',
                merged_files=[str(target_file)],
                conflicts=[],
                validation_results={},
                merge_time=0.0,
                rollback_available=True
            )
            
        except Exception as e:
            return MergeResult(
                merge_id="",
                status='failed',
                merged_files=[],
                conflicts=[{'file': str(target_file), 'error': str(e)}],
                validation_results={},
                merge_time=0.0,
                rollback_available=False
            )
    
    async def _merge_prepend(self, implementation: Dict[str, Any]) -> MergeResult:
        """Merge by prepending to existing files"""
        component_name = implementation['component_name']
        target_file = self.target_directory / f"{component_name}.py"
        
        try:
            if target_file.exists():
                existing_content = target_file.read_text()
                new_content = implementation['code_content'] + "\n\n" + existing_content
            else:
                new_content = implementation['code_content']
            
            target_file.write_text(new_content)
            
            return MergeResult(
                merge_id="",
                status='success',
                merged_files=[str(target_file)],
                conflicts=[],
                validation_results={},
                merge_time=0.0,
                rollback_available=True
            )
            
        except Exception as e:
            return MergeResult(
                merge_id="",
                status='failed',
                merged_files=[],
                conflicts=[{'file': str(target_file), 'error': str(e)}],
                validation_results={},
                merge_time=0.0,
                rollback_available=False
            )
    
    async def _merge_smart(self, implementation: Dict[str, Any]) -> MergeResult:
        """Smart merge with conflict detection and resolution"""
        component_name = implementation['component_name']
        target_file = self.target_directory / f"{component_name}.py"
        
        try:
            if not target_file.exists():
                # New file - simple write
                target_file.write_text(implementation['code_content'])
                return MergeResult(
                    merge_id="",
                    status='success',
                    merged_files=[str(target_file)],
                    conflicts=[],
                    validation_results={},
                    merge_time=0.0,
                    rollback_available=True
                )
            
            # Existing file - perform smart merge
            existing_content = target_file.read_text()
            new_content = implementation['code_content']
            
            # Parse both files to AST
            import ast
            try:
                existing_ast = ast.parse(existing_content)
                new_ast = ast.parse(new_content)
            except SyntaxError as e:
                return MergeResult(
                    merge_id="",
                    status='failed',
                    merged_files=[],
                    conflicts=[{'file': str(target_file), 'error': f'Syntax error: {e}'}],
                    validation_results={},
                    merge_time=0.0,
                    rollback_available=False
                )
            
            # Analyze differences
            conflicts = await self._detect_conflicts(existing_ast, new_ast)
            
            if conflicts:
                # Handle conflicts
                resolved_content = await self._resolve_conflicts(existing_content, new_content, conflicts)
                if resolved_content:
                    target_file.write_text(resolved_content)
                    return MergeResult(
                        merge_id="",
                        status='conflict',
                        merged_files=[str(target_file)],
                        conflicts=conflicts,
                        validation_results={},
                        merge_time=0.0,
                        rollback_available=True
                    )
                else:
                    return MergeResult(
                        merge_id="",
                        status='failed',
                        merged_files=[],
                        conflicts=conflicts,
                        validation_results={},
                        merge_time=0.0,
                        rollback_available=False
                    )
            else:
                # No conflicts - merge successfully
                merged_content = await self._merge_contents(existing_content, new_content)
                target_file.write_text(merged_content)
                
                return MergeResult(
                    merge_id="",
                    status='success',
                    merged_files=[str(target_file)],
                    conflicts=[],
                    validation_results={},
                    merge_time=0.0,
                    rollback_available=True
                )
                
        except Exception as e:
            return MergeResult(
                merge_id="",
                status='failed',
                merged_files=[],
                conflicts=[{'file': str(target_file), 'error': str(e)}],
                validation_results={},
                merge_time=0.0,
                rollback_available=False
            )
    
    async def _detect_conflicts(self, existing_ast: ast.AST, new_ast: ast.AST) -> List[Dict[str, Any]]:
        """Detect conflicts between existing and new code"""
        conflicts = []
        
        # Get function definitions
        existing_functions = {node.name: node for node in ast.walk(existing_ast) if isinstance(node, ast.FunctionDef)}
        new_functions = {node.name: node for node in ast.walk(new_ast) if isinstance(node, ast.FunctionDef)}
        
        # Check for function conflicts
        for func_name in set(existing_functions.keys()) & set(new_functions.keys()):
            existing_func = existing_functions[func_name]
            new_func = new_functions[func_name]
            
            # Compare function signatures
            if not self._compare_function_signatures(existing_func, new_func):
                conflicts.append({
                    'type': 'function_signature',
                    'name': func_name,
                    'description': f'Function signature changed for {func_name}'
                })
            
            # Compare function bodies
            if not self._compare_function_bodies(existing_func, new_func):
                conflicts.append({
                    'type': 'function_body',
                    'name': func_name,
                    'description': f'Function body changed for {func_name}'
                })
        
        return conflicts
    
    def _compare_function_signatures(self, func1: ast.FunctionDef, func2: ast.FunctionDef) -> bool:
        """Compare function signatures"""
        # Compare argument names
        args1 = [arg.arg for arg in func1.args.args]
        args2 = [arg.arg for arg in func2.args.args]
        
        return args1 == args2
    
    def _compare_function_bodies(self, func1: ast.FunctionDef, func2: ast.FunctionDef) -> bool:
        """Compare function bodies"""
        # Simple comparison - in real implementation would be more sophisticated
        import ast
        return ast.dump(func1) == ast.dump(func2)
    
    async def _resolve_conflicts(self, existing_content: str, new_content: str, conflicts: List[Dict[str, Any]]) -> Optional[str]:
        """Resolve conflicts between existing and new content"""
        # Simple resolution strategy - prefer new content for conflicts
        # In real implementation, this would be more sophisticated
        
        try:
            # For now, just return new content
            # TODO: Implement intelligent conflict resolution
            return new_content
            
        except Exception as e:
            logger.error(f"Conflict resolution failed: {e}")
            return None
    
    async def _merge_contents(self, existing_content: str, new_content: str) -> str:
        """Merge contents without conflicts"""
        # Simple append strategy for non-conflicting content
        return existing_content + "\n\n" + new_content
    
    async def _merge_manual(self, implementation: Dict[str, Any]) -> MergeResult:
        """Manual merge requiring user intervention"""
        # Create conflict markers for manual resolution
        component_name = implementation['component_name']
        target_file = self.target_directory / f"{component_name}.py"
        
        try:
            if target_file.exists():
                existing_content = target_file.read_text()
                new_content = implementation['code_content']
                
                # Create conflict file
                conflict_content = f"""
<<<<<<< HEAD (Existing)
{existing_content}
=======
{new_content}
>>>>>>> NEW (Generated)
"""
                
                conflict_file = self.target_directory / f"{component_name}.py.conflict"
                conflict_file.write_text(conflict_content)
                
                return MergeResult(
                    merge_id="",
                    status='conflict',
                    merged_files=[],
                    conflicts=[{
                        'file': str(target_file),
                        'conflict_file': str(conflict_file),
                        'description': 'Manual merge required'
                    }],
                    validation_results={},
                    merge_time=0.0,
                    rollback_available=False
                )
            else:
                # New file - no conflict
                return await self._merge_overwrite(implementation)
                
        except Exception as e:
            return MergeResult(
                merge_id="",
                status='failed',
                merged_files=[],
                conflicts=[{'file': str(target_file), 'error': str(e)}],
                validation_results={},
                merge_time=0.0,
                rollback_available=False
            )
    
    async def _validate_merged_code(self, merge_result: MergeResult) -> Dict[str, Any]:
        """Validate merged code"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        for file_path in merge_result.merged_files:
            try:
                # Check file exists and is readable
                file_obj = Path(file_path)
                if not file_obj.exists():
                    validation['errors'].append(f'Merged file not found: {file_path}')
                    validation['valid'] = False
                    continue
                
                # Check syntax
                content = file_obj.read_text()
                try:
                    import ast
                    ast.parse(content)
                except SyntaxError as e:
                    validation['errors'].append(f'Syntax error in merged file {file_path}: {e}')
                    validation['valid'] = False
                
                # Check for security issues
                security_issues = await self._check_security_issues(content)
                if security_issues:
                    validation['warnings'].extend([f'{file_path}: {issue}' for issue in security_issues])
                
            except Exception as e:
                validation['errors'].append(f'Validation error for {file_path}: {e}')
                validation['valid'] = False
        
        return validation
    
    async def rollback_merge(self, merge_result: MergeResult) -> bool:
        """Rollback a merge operation"""
        try:
            if not merge_result.rollback_available:
                return False
            
            backup_dir = self.target_directory / 'backups'
            if not backup_dir.exists():
                return False
            
            # Find most recent backup for the files
            for file_path in merge_result.merged_files:
                backup_file = None
                
                # Look for backup files
                for backup_path in backup_dir.rglob(f"{Path(file_path).name}.backup"):
                    if backup_path.exists():
                        backup_file = backup_path
                        break
                
                if backup_file:
                    shutil.copy2(backup_file, file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

class UINotificationManager:
    """Manages UI notifications for the presentation phase"""
    
    def __init__(self, redis_bus: RedisBus):
        self.redis_bus = redis_bus
        self.notification_templates = {
            'implementation_complete': {
                'type': 'success',
                'title': 'Implementation Complete',
                'message': 'Code implementation completed successfully'
            },
            'merge_conflict': {
                'type': 'warning',
                'title': 'Merge Conflict',
                'message': 'Code merge encountered conflicts requiring resolution'
            },
            'security_issue': {
                'type': 'error',
                'title': 'Security Issue',
                'message': 'Security issues detected in implementation'
            },
            'performance_warning': {
                'type': 'warning',
                'title': 'Performance Warning',
                'message': 'Performance issues detected in implementation'
            },
            'ertdsd_cycle_complete': {
                'type': 'success',
                'title': 'ERTDSD Cycle Complete',
                'message': 'Complete ERTDSD development cycle finished successfully'
            }
        }
    
    async def create_notification(self, notification_type: str, details: Dict[str, Any] = None) -> UINotification:
        """Create a UI notification"""
        template = self.notification_templates.get(notification_type, {
            'type': 'info',
            'title': 'Notification',
            'message': 'General notification'
        })
        
        notification_id = hashlib.md5(f"{notification_type}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        notification = UINotification(
            notification_id=notification_id,
            type=template['type'],
            title=template['title'],
            message=template['message'],
            details=details or {},
            timestamp=datetime.now(),
            persistent=notification_type in ['security_issue', 'ertdsd_cycle_complete']
        )
        
        # Publish notification to Redis
        await self._publish_notification(notification)
        
        return notification
    
    async def create_custom_notification(self, notification_type: str, title: str, message: str, details: Dict[str, Any] = None) -> UINotification:
        """Create a custom UI notification"""
        notification_id = hashlib.md5(f"custom_{title}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        notification = UINotification(
            notification_id=notification_id,
            type=notification_type,
            title=title,
            message=message,
            details=details or {},
            timestamp=datetime.now(),
            persistent=False
        )
        
        await self._publish_notification(notification)
        return notification
    
    async def _publish_notification(self, notification: UINotification):
        """Publish notification to Redis bus"""
        event = {
            'event_type': 'ui_notification',
            'notification_id': notification.notification_id,
            'type': notification.type,
            'title': notification.title,
            'message': notification.message,
            'details': notification.details,
            'timestamp': notification.timestamp.isoformat(),
            'persistent': notification.persistent
        }
        
        await self.redis_bus.publish('ui.notifications', event)
    
    async def create_progress_notification(self, phase: str, progress: float, details: Dict[str, Any] = None) -> UINotification:
        """Create a progress notification"""
        title = f"ERTDSD Phase: {phase.title()}"
        message = f"Progress: {progress:.1f}%"
        
        progress_details = {
            'phase': phase,
            'progress': progress,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            progress_details.update(details)
        
        return await self.create_custom_notification(
            'info',
            title,
            message,
            progress_details
        )
    
    async def create_summary_notification(self, session_data: Dict[str, Any]) -> UINotification:
        """Create a summary notification for the complete session"""
        total_components = session_data.get('total_components', 0)
        successful_merges = session_data.get('successful_merges', 0)
        failed_merges = session_data.get('failed_merges', 0)
        
        if failed_merges == 0:
            title = "ERTDSD Cycle Complete - Success"
            message = f"All {total_components} components implemented and merged successfully"
            notification_type = 'success'
        elif failed_merges < total_components:
            title = "ERTDSD Cycle Complete - Partial Success"
            message = f"{successful_merges} of {total_components} components merged successfully, {failed_merges} failed"
            notification_type = 'warning'
        else:
            title = "ERTDSD Cycle Complete - Failed"
            message = f"All {total_components} component merges failed"
            notification_type = 'error'
        
        return await self.create_custom_notification(
            notification_type,
            title,
            message,
            session_data
        )

class ReportGenerator:
    """Generates comprehensive reports for the presentation phase"""
    
    def __init__(self):
        self.report_templates = {
            'implementation_summary': self._generate_implementation_summary,
            'merge_report': self._generate_merge_report,
            'performance_report': self._generate_performance_report,
            'security_report': self._generate_security_report,
            'complete_ertdsd_report': self._generate_complete_ertdsd_report
        }
    
    async def generate_report(self, report_type: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a specific type of report"""
        if report_type in self.report_templates:
            return await self.report_templates[report_type](session_data)
        else:
            return await self._generate_generic_report(session_data)
    
    async def _generate_implementation_summary(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate implementation summary report"""
        implementations = session_data.get('implementations', [])
        
        summary = {
            'report_type': 'implementation_summary',
            'generated_at': datetime.now().isoformat(),
            'total_implementations': len(implementations),
            'successful_implementations': len([impl for impl in implementations if impl.get('test_results', {}).get('status') == 'passed']),
            'failed_implementations': len([impl for impl in implementations if impl.get('test_results', {}).get('status') == 'failed']),
            'average_quality_score': sum(impl.get('quality_score', 0) for impl in implementations) / len(implementations) if implementations else 0,
            'implementations': []
        }
        
        for impl in implementations:
            impl_summary = {
                'component_name': impl.get('component_name'),
                'quality_score': impl.get('quality_score'),
                'implementation_time': impl.get('implementation_time'),
                'test_status': impl.get('test_results', {}).get('status'),
                'security_score': impl.get('security_scan_results', {}).get('security_score'),
                'performance_score': impl.get('performance_metrics', {}).get('performance_score')
            }
            summary['implementations'].append(impl_summary)
        
        return summary
    
    async def _generate_merge_report(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate merge report"""
        merge_results = session_data.get('merge_results', [])
        
        report = {
            'report_type': 'merge_report',
            'generated_at': datetime.now().isoformat(),
            'total_merges': len(merge_results),
            'successful_merges': len([merge for merge in merge_results if merge.status == 'success']),
            'conflicted_merges': len([merge for merge in merge_results if merge.status == 'conflict']),
            'failed_merges': len([merge for merge in merge_results if merge.status == 'failed']),
            'average_merge_time': sum(merge.merge_time for merge in merge_results) / len(merge_results) if merge_results else 0,
            'merges': []
        }
        
        for merge in merge_results:
            merge_info = {
                'merge_id': merge.merge_id,
                'status': merge.status,
                'merged_files': merge.merged_files,
                'conflicts': len(merge.conflicts),
                'merge_time': merge.merge_time,
                'rollback_available': merge.rollback_available
            }
            report['merges'].append(merge_info)
        
        return report
    
    async def _generate_performance_report(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance report"""
        implementations = session_data.get('implementations', [])
        
        report = {
            'report_type': 'performance_report',
            'generated_at': datetime.now().isoformat(),
            'total_implementations': len(implementations),
            'performance_metrics': {
                'total_implementation_time': sum(impl.get('implementation_time', 0) for impl in implementations),
                'average_implementation_time': sum(impl.get('implementation_time', 0) for impl in implementations) / len(implementations) if implementations else 0,
                'slowest_component': max(implementations, key=lambda x: x.get('implementation_time', 0)).get('component_name') if implementations else None,
                'fastest_component': min(implementations, key=lambda x: x.get('implementation_time', 0)).get('component_name') if implementations else None
            },
            'components': []
        }
        
        for impl in implementations:
            perf_data = impl.get('performance_metrics', {})
            component_perf = {
                'component_name': impl.get('component_name'),
                'implementation_time': impl.get('implementation_time'),
                'performance_score': perf_data.get('performance_score'),
                'performance_issues': len(perf_data.get('performance_issues', [])),
                'quality_score': impl.get('quality_score')
            }
            report['components'].append(component_perf)
        
        return report
    
    async def _generate_security_report(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security report"""
        implementations = session_data.get('implementations', [])
        
        report = {
            'report_type': 'security_report',
            'generated_at': datetime.now().isoformat(),
            'total_implementations': len(implementations),
            'security_summary': {
                'total_vulnerabilities': sum(impl.get('security_scan_results', {}).get('vulnerabilities_found', 0) for impl in implementations),
                'average_security_score': sum(impl.get('security_scan_results', {}).get('security_score', 0) for impl in implementations) / len(implementations) if implementations else 0,
                'high_risk_components': len([impl for impl in implementations if impl.get('security_scan_results', {}).get('security_score', 100) < 70])
            },
            'components': []
        }
        
        for impl in implementations:
            security_data = impl.get('security_scan_results', {})
            component_security = {
                'component_name': impl.get('component_name'),
                'security_score': security_data.get('security_score'),
                'vulnerabilities_found': security_data.get('vulnerabilities_found'),
                'security_issues': security_data.get('vulnerabilities', [])
            }
            report['components'].append(component_security)
        
        return report
    
    async def _generate_complete_ertdsd_report(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete ERTDSD cycle report"""
        # Generate all sub-reports
        implementation_summary = await self._generate_implementation_summary(session_data)
        merge_report = await self._generate_merge_report(session_data)
        performance_report = await self._generate_performance_report(session_data)
        security_report = await self._generate_security_report(session_data)
        
        complete_report = {
            'report_type': 'complete_ertdsd_report',
            'generated_at': datetime.now().isoformat(),
            'contract_id': session_data.get('contract_id'),
            'session_id': session_data.get('session_id'),
            'duration': session_data.get('duration', 0),
            'overall_status': self._determine_overall_status(session_data),
            'summary': {
                'total_components': implementation_summary.get('total_implementations', 0),
                'successful_implementations': implementation_summary.get('successful_implementations', 0),
                'successful_merges': merge_report.get('successful_merges', 0),
                'average_quality_score': implementation_summary.get('average_quality_score', 0),
                'average_security_score': security_report.get('security_summary', {}).get('average_security_score', 0),
                'total_vulnerabilities': security_report.get('security_summary', {}).get('total_vulnerabilities', 0)
            },
            'reports': {
                'implementation': implementation_summary,
                'merge': merge_report,
                'performance': performance_report,
                'security': security_report
            }
        }
        
        return complete_report
    
    async def _generate_generic_report(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate generic report"""
        return {
            'report_type': 'generic',
            'generated_at': datetime.now().isoformat(),
            'session_data': session_data,
            'summary': 'Generic report generated'
        }
    
    def _determine_overall_status(self, session_data: Dict[str, Any]) -> str:
        """Determine overall status of the ERTDSD cycle"""
        implementations = session_data.get('implementations', [])
        merge_results = session_data.get('merge_results', [])
        
        if not implementations:
            return 'no_implementations'
        
        successful_impl = len([impl for impl in implementations if impl.get('test_results', {}).get('status') == 'passed'])
        successful_merge = len([merge for merge in merge_results if merge.status == 'success'])
        
        total_impl = len(implementations)
        total_merge = len(merge_results)
        
        if successful_impl == total_impl and successful_merge == total_merge:
            return 'complete_success'
        elif successful_impl > 0 and successful_merge > 0:
            return 'partial_success'
        else:
            return 'failed'

class PresentationPhase:
    """
    Presentation Phase - ERTDSD Merge Workflow and UI Notifications
    
    This phase integrates results from Meeting, Architect, and Grind phases,
    handles code merging, generates reports, and provides UI notifications.
    """
    
    def __init__(self, 
                 redis_bus: RedisBus,
                 global_arbiter: GlobalArbiter,
                 identity_firewall: IdentityFirewall,
                 bikameral_memory: BikameralMemory,
                 chronos: ChronosHeartbeat,
                 target_directory: str = "./generated_code"):
        self.redis_bus = redis_bus
        self.global_arbiter = global_arbiter
        self.identity_firewall = identity_firewall
        self.bikameral_memory = bikameral_memory
        self.chronos = chronos
        self.code_merger = CodeMerger(target_directory)
        self.notification_manager = UINotificationManager(redis_bus)
        self.report_generator = ReportGenerator()
        
        logger.info("Presentation Phase initialized")
    
    async def present_results(self, grind_session: Dict[str, Any], presentation_context: Dict[str, Any]) -> PresentationSession:
        """
        Present results from implementation session
        
        Args:
            grind_session: Results from Grind Phase implementation
            presentation_context: Context for presentation
            
        Returns:
            Presentation session with merge results and notifications
        """
        try:
            logger.info(f"Starting Presentation Phase for contract {grind_session.get('contract_id')}")
            
            # 1. Create presentation session
            session = self._create_presentation_session(grind_session, presentation_context)
            
            # 2. Send progress notification
            await self.notification_manager.create_progress_notification('presentation', 0.0, {
                'contract_id': session.contract_id,
                'total_components': len(grind_session.get('implementations', []))
            })
            
            # 3. Merge implementations into target codebase
            merge_results = await self._merge_implementations(grind_session, session)
            session.merge_results = merge_results
            
            # 4. Generate comprehensive reports
            reports = await self._generate_reports(grind_session, merge_results)
            
            # 5. Create notifications based on results
            notifications = await self._create_result_notifications(grind_session, merge_results, reports)
            session.notifications = notifications
            
            # 6. Store final results in memory
            await self._store_presentation_results(session, reports)
            
            # 7. Update completion status
            session.completion_status = self._determine_completion_status(merge_results)
            session.final_report = reports.get('complete_ertdsd_report', {})
            
            # 8. Send completion notification
            await self.notification_manager.create_summary_notification({
                'contract_id': session.contract_id,
                'total_components': len(grind_session.get('implementations', [])),
                'successful_merges': len([m for m in merge_results if m.status == 'success']),
                'failed_merges': len([m for m in merge_results if m.status == 'failed']),
                'duration': (datetime.now() - session.start_time).total_seconds()
            })
            
            # 9. Publish completion event
            await self._publish_completion(session)
            
            logger.info(f"Presentation Phase completed for contract {session.contract_id}")
            return session
            
        except Exception as e:
            logger.error(f"Presentation Phase failed: {e}")
            await self._publish_error(grind_session.get('contract_id'), str(e))
            raise
    
    def _create_presentation_session(self, grind_session: Dict[str, Any], presentation_context: Dict[str, Any]) -> PresentationSession:
        """Create presentation session"""
        session_id = hashlib.md5(f"{grind_session['contract_id']}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        return PresentationSession(
            session_id=session_id,
            contract_id=grind_session['contract_id'],
            implementation_session_id=grind_session['session_id'],
            start_time=datetime.now(),
            merge_results=[],
            notifications=[]
        )
    
    async def _merge_implementations(self, grind_session: Dict[str, Any], session: PresentationSession) -> List[MergeResult]:
        """Merge all implementations into target codebase"""
        implementations = grind_session.get('implementations', [])
        merge_results = []
        total_components = len(implementations)
        
        for i, implementation in enumerate(implementations):
            # Update progress
            progress = (i / total_components) * 50.0  # 0-50% for merge phase
            await self.notification_manager.create_progress_notification('presentation', progress, {
                'current_component': implementation.get('component_name'),
                'components_merged': i,
                'total_components': total_components
            })
            
            # Determine merge strategy based on component type and quality
            merge_strategy = self._determine_merge_strategy(implementation)
            
            # Merge implementation
            merge_result = await self.code_merger.merge_implementation(implementation, merge_strategy)
            merge_results.append(merge_result)
            
            # Create notification for merge result
            if merge_result.status == 'success':
                await self.notification_manager.create_notification(
                    'implementation_complete',
                    {
                        'component_name': implementation.get('component_name'),
                        'merge_strategy': merge_strategy,
                        'merge_time': merge_result.merge_time
                    }
                )
            elif merge_result.status == 'conflict':
                await self.notification_manager.create_notification(
                    'merge_conflict',
                    {
                        'component_name': implementation.get('component_name'),
                        'conflicts': merge_result.conflicts,
                        'conflict_count': len(merge_result.conflicts)
                    }
                )
            else:  # failed
                await self.notification_manager.create_custom_notification(
                    'error',
                    'Merge Failed',
                    f"Failed to merge {implementation.get('component_name')}",
                    {
                        'component_name': implementation.get('component_name'),
                        'error': merge_result.validation_results.get('error', 'Unknown error')
                    }
                )
        
        return merge_results
    
    def _determine_merge_strategy(self, implementation: Dict[str, Any]) -> str:
        """Determine appropriate merge strategy based on implementation quality and type"""
        quality_score = implementation.get('quality_score', 0)
        component_name = implementation.get('component_name', '').lower()
        
        # High quality implementations use smart merge
        if quality_score >= 80:
            return 'smart'
        
        # Medium quality use append strategy
        elif quality_score >= 60:
            return 'append'
        
        # Low quality require manual intervention
        else:
            return 'manual'
    
    async def _generate_reports(self, grind_session: Dict[str, Any], merge_results: List[MergeResult]) -> Dict[str, Any]:
        """Generate comprehensive reports"""
        reports = {}
        
        # Create enhanced session data with merge results
        enhanced_session_data = {
            **grind_session,
            'merge_results': [self._merge_result_to_dict(merge) for merge in merge_results],
            'duration': (datetime.now() - datetime.fromisoformat(grind_session['start_time'])).total_seconds()
        }
        
        # Generate individual reports
        reports['implementation_summary'] = await self.report_generator.generate_report('implementation_summary', enhanced_session_data)
        reports['merge_report'] = await self.report_generator.generate_report('merge_report', enhanced_session_data)
        reports['performance_report'] = await self.report_generator.generate_report('performance_report', enhanced_session_data)
        reports['security_report'] = await self.report_generator.generate_report('security_report', enhanced_session_data)
        reports['complete_ertdsd_report'] = await self.report_generator.generate_report('complete_ertdsd_report', enhanced_session_data)
        
        return reports
    
    def _merge_result_to_dict(self, merge_result: MergeResult) -> Dict[str, Any]:
        """Convert MergeResult to dictionary"""
        return {
            'merge_id': merge_result.merge_id,
            'status': merge_result.status,
            'merged_files': merge_result.merged_files,
            'conflicts': merge_result.conflicts,
            'validation_results': merge_result.validation_results,
            'merge_time': merge_result.merge_time,
            'rollback_available': merge_result.rollback_available
        }
    
    async def _create_result_notifications(self, grind_session: Dict[str, Any], merge_results: List[MergeResult], reports: Dict[str, Any]) -> List[UINotification]:
        """Create notifications based on results"""
        notifications = []
        
        # Security notifications
        security_report = reports.get('security_report', {})
        total_vulnerabilities = security_report.get('security_summary', {}).get('total_vulnerabilities', 0)
        
        if total_vulnerabilities > 0:
            notification = await self.notification_manager.create_notification(
                'security_issue',
                {
                    'total_vulnerabilities': total_vulnerabilities,
                    'high_risk_components': security_report.get('security_summary', {}).get('high_risk_components', 0),
                    'average_security_score': security_report.get('security_summary', {}).get('average_security_score', 0)
                }
            )
            notifications.append(notification)
        
        # Performance notifications
        performance_report = reports.get('performance_report', {})
        performance_metrics = performance_report.get('performance_metrics', {})
        
        if performance_metrics.get('slowest_component'):
            notification = await self.notification_manager.create_custom_notification(
                'warning',
                'Performance Warning',
                f"Performance issues detected in {performance_metrics['slowest_component']}",
                performance_metrics
            )
            notifications.append(notification)
        
        # Merge conflict notifications
        conflicted_merges = [merge for merge in merge_results if merge.status == 'conflict']
        if conflicted_merges:
            notification = await self.notification_manager.create_notification(
                'merge_conflict',
                {
                    'conflicted_components': len(conflicted_merges),
                    'conflict_details': [{'component': merge.merged_files[0], 'conflicts': len(merge.conflicts)} for merge in conflicted_merges]
                }
            )
            notifications.append(notification)
        
        # Success notification if everything went well
        successful_merges = [merge for merge in merge_results if merge.status == 'success']
        failed_merges = [merge for merge in merge_results if merge.status == 'failed']
        
        if not failed_merges and not conflicted_merges:
            notification = await self.notification_manager.create_notification(
                'ertdsd_cycle_complete',
                {
                    'successful_components': len(successful_merges),
                    'total_components': len(merge_results),
                    'reports_generated': len(reports)
                }
            )
            notifications.append(notification)
        
        return notifications
    
    async def _store_presentation_results(self, session: PresentationSession, reports: Dict[str, Any]):
        """Store presentation results in memory"""
        presentation_data = {
            'session_id': session.session_id,
            'contract_id': session.contract_id,
            'implementation_session_id': session.implementation_session_id,
            'start_time': session.start_time.isoformat(),
            'completion_status': session.completion_status,
            'merge_results': [self._merge_result_to_dict(merge) for merge in session.merge_results],
            'notifications': [
                {
                    'notification_id': notif.notification_id,
                    'type': notif.type,
                    'title': notif.title,
                    'message': notif.message,
                    'details': notif.details,
                    'timestamp': notif.timestamp.isoformat(),
                    'read': notif.read,
                    'persistent': notif.persistent
                }
                for notif in session.notifications
            ],
            'reports': reports,
            'duration': (datetime.now() - session.start_time).total_seconds()
        }
        
        # Store in short-term memory
        await self.bikameral_memory.store_short_term(
            f"presentation_session:{session.session_id}",
            presentation_data,
            ttl=3600  # 1 hour TTL
        )
        
        # Store in long-term memory
        await self.bikameral_memory.store_long_term(
            f"presentation_session:{session.session_id}",
            presentation_data
        )
    
    def _determine_completion_status(self, merge_results: List[MergeResult]) -> str:
        """Determine overall completion status"""
        if not merge_results:
            return 'no_implementations'
        
        successful_merges = len([merge for merge in merge_results if merge.status == 'success'])
        conflicted_merges = len([merge for merge in merge_results if merge.status == 'conflict'])
        failed_merges = len([merge for merge in merge_results if merge.status == 'failed'])
        
        total_merges = len(merge_results)
        
        if failed_merges == 0 and conflicted_merges == 0:
            return 'complete_success'
        elif failed_merges == 0:
            return 'success_with_conflicts'
        elif successful_merges > 0:
            return 'partial_success'
        else:
            return 'failed'
    
    async def _publish_completion(self, session: PresentationSession):
        """Publish completion event to Redis bus"""
        event = {
            'event_type': 'presentation_phase_completed',
            'session_id': session.session_id,
            'contract_id': session.contract_id,
            'implementation_session_id': session.implementation_session_id,
            'timestamp': datetime.now().isoformat(),
            'completion_status': session.completion_status,
            'metrics': {
                'total_merges': len(session.merge_results),
                'successful_merges': len([merge for merge in session.merge_results if merge.status == 'success']),
                'conflicted_merges': len([merge for merge in session.merge_results if merge.status == 'conflict']),
                'failed_merges': len([merge for merge in session.merge_results if merge.status == 'failed']),
                'total_notifications': len(session.notifications)
            }
        }
        
        await self.redis_bus.publish('orchestration.events', event)
    
    async def _publish_error(self, contract_id: str, error_message: str):
        """Publish error event to Redis bus"""
        event = {
            'event_type': 'presentation_phase_error',
            'contract_id': contract_id,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.redis_bus.publish('orchestration.events', event)
    
    async def rollback_presentation(self, session_id: str) -> bool:
        """Rollback a presentation session"""
        try:
            # Retrieve session data
            session_data = await self.bikameral_memory.retrieve_data(f"presentation_session:{session_id}")
            if not session_data:
                return False
            
            # Rollback all merge operations
            merge_results = session_data.get('merge_results', [])
            rollback_success = True
            
            for merge_data in merge_results:
                if merge_data.get('rollback_available'):
                    # Reconstruct MergeResult object
                    merge_result = MergeResult(
                        merge_id=merge_data['merge_id'],
                        status=merge_data['status'],
                        merged_files=merge_data['merged_files'],
                        conflicts=merge_data['conflicts'],
                        validation_results=merge_data['validation_results'],
                        merge_time=merge_data['merge_time'],
                        rollback_available=merge_data['rollback_available']
                    )
                    
                    # Attempt rollback
                    if not await self.code_merger.rollback_merge(merge_result):
                        rollback_success = False
            
            return rollback_success
            
        except Exception as e:
            logger.error(f"Presentation rollback failed: {e}")
            return False

# Factory function for easy integration
def create_presentation_phase(runtime_context: Dict[str, Any]) -> PresentationPhase:
    """Factory function to create Presentation Phase instance"""
    return PresentationPhase(
        redis_bus=runtime_context['redis_bus'],
        global_arbiter=runtime_context['global_arbiter'],
        identity_firewall=runtime_context['identity_firewall'],
        bikameral_memory=runtime_context['bikameral_memory'],
        chronos=runtime_context['chronos_heartbeat'],
        target_directory=runtime_context.get('target_directory', './generated_code')
    )