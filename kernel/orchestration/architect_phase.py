"""
Architect Phase - ERTDSD Test Generation
Generates comprehensive test suites as specifications before any code implementation
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib
import re
from pathlib import Path

from redis_bus import RedisBus
from global_arbiter import GlobalArbiter
from identity_firewall import IdentityFirewall
from bikameral_memory import BikameralMemory
from chronos_heartbeat import ChronosHeartbeat
from msca import Module, Sentinel, Connector, Adapter

logger = logging.getLogger(__name__)

@dataclass
class TestSpecification:
    """Test specification for a component"""
    component_name: str
    test_type: str  # unit, integration, e2e, performance, security
    test_name: str
    description: str
    preconditions: List[str]
    steps: List[str]
    expected_results: List[str]
    test_data: Dict[str, Any]
    assertions: List[str]
    mock_dependencies: List[str]
    performance_requirements: Optional[Dict[str, float]] = None
    security_requirements: Optional[List[str]] = None

@dataclass
class ArchitectureBlueprint:
    """Architecture blueprint from meeting phase"""
    contract_id: str
    task_manifest: Dict[str, Any]
    components: List[str]
    interfaces: List[Dict[str, Any]]
    data_flows: List[Dict[str, Any]]
    resource_limits: Dict[str, Any]
    definition_of_done: List[str]

@dataclass
class TestSuite:
    """Generated test suite"""
    suite_id: str
    contract_id: str
    specifications: List[TestSpecification]
    coverage_metrics: Dict[str, float]
    complexity_score: float
    estimated_execution_time: float
    resource_requirements: Dict[str, Any]
    generated_at: datetime

class TestPatternGenerator:
    """Generates test patterns based on component types"""
    
    def __init__(self):
        self.patterns = {
            'api_endpoint': self._generate_api_tests,
            'database_model': self._generate_database_tests,
            'ui_component': self._generate_ui_tests,
            'algorithm': self._generate_algorithm_tests,
            'integration': self._generate_integration_tests,
            'security': self._generate_security_tests,
            'performance': self._generate_performance_tests,
            'memory_system': self._generate_memory_tests,
            'orchestration': self._generate_orchestration_tests,
            'scanner': self._generate_scanner_tests
        }
    
    def _generate_api_tests(self, component: str, interface: Dict[str, Any]) -> List[TestSpecification]:
        """Generate API endpoint tests"""
        tests = []
        
        # Basic CRUD tests
        if interface.get('methods'):
            for method in interface['methods']:
                test = TestSpecification(
                    component_name=component,
                    test_type='integration',
                    test_name=f"{component}_{method}_basic",
                    description=f"Test basic {method} operation for {component}",
                    preconditions=[
                        "API server is running",
                        "Database is accessible",
                        "Authentication is configured"
                    ],
                    steps=[
                        f"Send {method} request to {interface.get('path', '/')}",
                        "Validate response status code",
                        "Validate response body structure"
                    ],
                    expected_results=[
                        f"Response status matches expected for {method}",
                        "Response body contains required fields",
                        "No server errors occur"
                    ],
                    test_data={
                        'valid_payload': self._generate_valid_payload(interface),
                        'invalid_payload': self._generate_invalid_payload(interface)
                    },
                    assertions=[
                        "response.status_code in expected_range",
                        "required_fields in response.json()",
                        "response_time < 500ms"
                    ],
                    mock_dependencies=['external_api_calls']
                )
                tests.append(test)
        
        # Error handling tests
        error_test = TestSpecification(
            component_name=component,
            test_type='integration',
            test_name=f"{component}_error_handling",
            description=f"Test error handling for {component}",
            preconditions=["API server is running"],
            steps=[
                "Send request with invalid authentication",
                "Send request with malformed data",
                "Send request to non-existent endpoint"
            ],
            expected_results=[
                "Appropriate error status codes returned",
                "Error messages are user-friendly",
                "No sensitive information leaked"
            ],
            test_data={},
            assertions=[
                "400 <= error_response.status_code < 600",
                "'error' in error_response.json()",
                "'message' in error_response.json()"
            ],
            mock_dependencies=[]
        )
        tests.append(error_test)
        
        return tests
    
    def _generate_database_tests(self, component: str, interface: Dict[str, Any]) -> List[TestSpecification]:
        """Generate database model tests"""
        tests = []
        
        # CRUD operations
        crud_test = TestSpecification(
            component_name=component,
            test_type='unit',
            test_name=f"{component}_crud_operations",
            description=f"Test CRUD operations for {component}",
            preconditions=[
                "Database connection is established",
                "Test database is available"
            ],
            steps=[
                "Create new record with valid data",
                "Read the created record",
                "Update the record",
                "Delete the record"
            ],
            expected_results=[
                "Record is created successfully",
                "Record can be retrieved",
                "Record updates correctly",
                "Record is deleted"
            ],
            test_data={
                'create_data': self._generate_model_data(interface),
                'update_data': self._generate_update_data(interface)
            },
            assertions=[
                "created_record.id is not None",
                "retrieved_record.id == created_record.id",
                "updated_record.field == update_data.field"
            ],
            mock_dependencies=['database_connection']
        )
        tests.append(crud_test)
        
        # Data integrity tests
        integrity_test = TestSpecification(
            component_name=component,
            test_type='unit',
            test_name=f"{component}_data_integrity",
            description=f"Test data integrity constraints for {component}",
            preconditions=["Database schema is properly configured"],
            steps=[
                "Attempt to insert duplicate unique values",
                "Attempt to insert null values in required fields",
                "Attempt to insert invalid foreign keys"
            ],
            expected_results=[
                "Unique constraints are enforced",
                "Null constraints are enforced",
                "Foreign key constraints are enforced"
            ],
            test_data={},
            assertions=[
                "IntegrityError raised for invalid data",
                "Transaction is rolled back on error"
            ],
            mock_dependencies=[]
        )
        tests.append(integrity_test)
        
        return tests
    
    def _generate_ui_tests(self, component: str, interface: Dict[str, Any]) -> List[TestSpecification]:
        """Generate UI component tests"""
        tests = []
        
        # Rendering tests
        render_test = TestSpecification(
            component_name=component,
            test_type='unit',
            test_name=f"{component}_rendering",
            description=f"Test rendering of {component}",
            preconditions=[
                "Component is properly imported",
                "Required props are available"
            ],
            steps=[
                "Render component with default props",
                "Render component with custom props",
                "Render component in different states"
            ],
            expected_results=[
                "Component renders without errors",
                "Props are properly passed",
                "Component state is managed correctly"
            ],
            test_data={
                'default_props': interface.get('default_props', {}),
                'custom_props': interface.get('custom_props', {})
            },
            assertions=[
                "component.exists()",
                "component.props() == expected_props",
                "component.state() == expected_state"
            ],
            mock_dependencies=['child_components']
        )
        tests.append(render_test)
        
        # User interaction tests
        interaction_test = TestSpecification(
            component_name=component,
            test_type='unit',
            test_name=f"{component}_interactions",
            description=f"Test user interactions for {component}",
            preconditions=["Component is rendered"],
            steps=[
                "Simulate user click events",
                "Simulate user input events",
                "Simulate form submission"
            ],
            expected_results=[
                "Event handlers are called",
                "Component state updates correctly",
                "Callbacks are invoked properly"
            ],
            test_data={
                'click_events': ['button_click', 'link_click'],
                'input_events': ['text_input', 'select_change']
            },
            assertions=[
                "event_handler.called",
                "state_updated correctly",
                "callback_invoked with correct parameters"
            ],
            mock_dependencies=['event_handlers', 'callbacks']
        )
        tests.append(interaction_test)
        
        return tests
    
    def _generate_algorithm_tests(self, component: str, interface: Dict[str, Any]) -> List[TestSpecification]:
        """Generate algorithm tests"""
        tests = []
        
        # Correctness tests
        correctness_test = TestSpecification(
            component_name=component,
            test_type='unit',
            test_name=f"{component}_correctness",
            description=f"Test algorithm correctness for {component}",
            preconditions=["Algorithm implementation is available"],
            steps=[
                "Execute algorithm with known inputs",
                "Compare output with expected results",
                "Test edge cases"
            ],
            expected_results=[
                "Algorithm produces correct output",
                "Edge cases are handled properly",
                "Performance meets requirements"
            ],
            test_data={
                'test_cases': interface.get('test_cases', []),
                'edge_cases': interface.get('edge_cases', [])
            },
            assertions=[
                "output == expected_output",
                "algorithm.terminates()",
                "algorithm.complexity() <= expected_complexity"
            ],
            mock_dependencies=[],
            performance_requirements={
                'max_execution_time': interface.get('max_time', 1.0),
                'max_memory_usage': interface.get('max_memory', 100)
            }
        )
        tests.append(correctness_test)
        
        return tests
    
    def _generate_integration_tests(self, component: str, interface: Dict[str, Any]) -> List[TestSpecification]:
        """Generate integration tests"""
        tests = []
        
        # End-to-end workflow tests
        workflow_test = TestSpecification(
            component_name=component,
            test_type='integration',
            test_name=f"{component}_workflow",
            description=f"Test complete workflow for {component}",
            preconditions=[
                "All dependent services are running",
                "Database is populated with test data"
            ],
            steps=[
                "Initialize workflow with input data",
                "Process data through all stages",
                "Verify final output and state"
            ],
            expected_results=[
                "Workflow completes successfully",
                "Data integrity is maintained",
                "All components interact correctly"
            ],
            test_data={
                'workflow_input': interface.get('workflow_input', {}),
                'expected_output': interface.get('expected_output', {})
            },
            assertions=[
                "workflow.status == 'completed'",
                "output_data == expected_output",
                "no_errors_in_logs"
            ],
            mock_dependencies=['external_services']
        )
        tests.append(workflow_test)
        
        return tests
    
    def _generate_security_tests(self, component: str, interface: Dict[str, Any]) -> List[TestSpecification]:
        """Generate security tests"""
        tests = []
        
        # Authentication tests
        auth_test = TestSpecification(
            component_name=component,
            test_type='security',
            test_name=f"{component}_authentication",
            description=f"Test authentication for {component}",
            preconditions=["Security system is configured"],
            steps=[
                "Attempt access without credentials",
                "Attempt access with invalid credentials",
                "Access with valid credentials"
            ],
            expected_results=[
                "Unauthorized access is denied",
                "Invalid credentials are rejected",
                "Valid credentials grant access"
            ],
            test_data={},
            assertions=[
                "unauthorized_response.status_code == 401",
                "valid_response.status_code == 200",
                "session_created properly"
            ],
            mock_dependencies=['authentication_service'],
            security_requirements=[
                "No credentials in logs",
                "Rate limiting enforced",
                "Session timeout implemented"
            ]
        )
        tests.append(auth_test)
        
        return tests
    
    def _generate_performance_tests(self, component: str, interface: Dict[str, Any]) -> List[TestSpecification]:
        """Generate performance tests"""
        tests = []
        
        # Load tests
        load_test = TestSpecification(
            component_name=component,
            test_type='performance',
            test_name=f"{component}_load",
            description=f"Test load performance for {component}",
            preconditions=["Test environment is isolated"],
            steps=[
                "Generate concurrent load",
                "Measure response times",
                "Monitor resource usage"
            ],
            expected_results=[
                "Response times within SLA",
                "No memory leaks detected",
                "System remains stable"
            ],
            test_data={
                'concurrent_users': interface.get('concurrent_users', 100),
                'test_duration': interface.get('test_duration', 300)
            },
            assertions=[
                "avg_response_time < sla_threshold",
                "error_rate < acceptable_threshold",
                "memory_usage_stable"
            ],
            mock_dependencies=['load_generator'],
            performance_requirements={
                'max_response_time': interface.get('max_response_time', 2.0),
                'min_throughput': interface.get('min_throughput', 100),
                'max_error_rate': interface.get('max_error_rate', 0.01)
            }
        )
        tests.append(load_test)
        
        return tests
    
    def _generate_memory_tests(self, component: str, interface: Dict[str, Any]) -> List[TestSpecification]:
        """Generate memory system tests"""
        tests = []
        
        # Memory allocation tests
        allocation_test = TestSpecification(
            component_name=component,
            test_type='unit',
            test_name=f"{component}_memory_allocation",
            description=f"Test memory allocation for {component}",
            preconditions=[
                "Memory system is initialized",
                "Bikameral memory is available"
            ],
            steps=[
                "Allocate memory for test data",
                "Verify allocation in Redis",
                "Verify allocation in PostgreSQL"
            ],
            expected_results=[
                "Memory allocated successfully",
                "Redis contains short-term data",
                "PostgreSQL contains long-term data"
            ],
            test_data={
                'test_data_size': interface.get('data_size', 1024),
                'retention_policy': interface.get('retention', 'short_term')
            },
            assertions=[
                "memory_allocation_successful",
                "redis_data_exists",
                "postgres_data_exists"
            ],
            mock_dependencies=['redis_client', 'postgres_client']
        )
        tests.append(allocation_test)
        
        return tests
    
    def _generate_orchestration_tests(self, component: str, interface: Dict[str, Any]) -> List[TestSpecification]:
        """Generate orchestration tests"""
        tests = []
        
        # Phase transition tests
        transition_test = TestSpecification(
            component_name=component,
            test_type='integration',
            test_name=f"{component}_phase_transitions",
            description=f"Test phase transitions for {component}",
            preconditions=[
                "Global Arbiter is active",
                "Chronos Heartbeat is running"
            ],
            steps=[
                "Trigger phase transition",
                "Validate state changes",
                "Verify resource allocation"
            ],
            expected_results=[
                "Phase transitions correctly",
                "State is consistent",
                "Resources are managed properly"
            ],
            test_data={
                'from_phase': interface.get('from_phase', 'meeting'),
                'to_phase': interface.get('to_phase', 'architect')
            },
            assertions=[
                "current_phase == expected_phase",
                "previous_phase != current_phase",
                "resources_allocated properly"
            ],
            mock_dependencies=['global_arbiter', 'chronos_heartbeat']
        )
        tests.append(transition_test)
        
        return tests
    
    def _generate_scanner_tests(self, component: str, interface: Dict[str, Any]) -> List[TestSpecification]:
        """Generate scanner tests"""
        tests = []
        
        # Code analysis tests
        analysis_test = TestSpecification(
            component_name=component,
            test_type='unit',
            test_name=f"{component}_code_analysis",
            description=f"Test code analysis for {component}",
            preconditions=[
                "Scanner is initialized",
                "Code repository is accessible"
            ],
            steps=[
                "Analyze code structure",
                "Detect code smells",
                "Generate improvement suggestions"
            ],
            expected_results=[
                "Code structure is analyzed",
                "Issues are identified",
                "Suggestions are relevant"
            ],
            test_data={
                'code_sample': interface.get('code_sample', ''),
                'analysis_depth': interface.get('depth', 'comprehensive')
            },
            assertions=[
                "analysis_completed",
                "issues_detected properly",
                "suggestions_generated"
            ],
            mock_dependencies=['code_parser', 'ast_analyzer']
        )
        tests.append(analysis_test)
        
        return tests
    
    def _generate_valid_payload(self, interface: Dict[str, Any]) -> Dict[str, Any]:
        """Generate valid test payload"""
        payload = {}
        if 'parameters' in interface:
            for param, config in interface['parameters'].items():
                if config.get('required', False):
                    payload[param] = self._generate_sample_value(config.get('type', 'string'))
        return payload
    
    def _generate_invalid_payload(self, interface: Dict[str, Any]) -> Dict[str, Any]:
        """Generate invalid test payload"""
        payload = {}
        if 'parameters' in interface:
            for param, config in interface['parameters'].items():
                if config.get('required', False):
                    payload[param] = None  # Invalid null value
        return payload
    
    def _generate_sample_value(self, data_type: str) -> Any:
        """Generate sample value for data type"""
        samples = {
            'string': 'test_string',
            'integer': 42,
            'number': 3.14,
            'boolean': True,
            'array': [1, 2, 3],
            'object': {'key': 'value'}
        }
        return samples.get(data_type, 'sample_value')
    
    def _generate_model_data(self, interface: Dict[str, Any]) -> Dict[str, Any]:
        """Generate model test data"""
        data = {}
        if 'fields' in interface:
            for field, config in interface['fields'].items():
                data[field] = self._generate_sample_value(config.get('type', 'string'))
        return data
    
    def _generate_update_data(self, interface: Dict[str, Any]) -> Dict[str, Any]:
        """Generate update test data"""
        data = self._generate_model_data(interface)
        # Modify some values for update testing
        for key in list(data.keys())[:2]:  # Update first 2 fields
            if isinstance(data[key], str):
                data[key] = data[key] + '_updated'
            elif isinstance(data[key], (int, float)):
                data[key] = data[key] + 1
        return data

class TestValidator:
    """Validates generated test specifications"""
    
    def validate_test_suite(self, suite: TestSuite, blueprint: ArchitectureBlueprint) -> Tuple[bool, List[str]]:
        """Validate test suite against architecture blueprint"""
        errors = []
        
        # Check coverage
        component_coverage = self._check_component_coverage(suite, blueprint)
        if component_coverage < 0.8:  # 80% minimum coverage
            errors.append(f"Component coverage too low: {component_coverage:.2%}")
        
        # Check resource requirements
        resource_valid = self._validate_resource_requirements(suite, blueprint)
        if not resource_valid:
            errors.append("Resource requirements exceed limits")
        
        # Check test completeness
        completeness = self._check_test_completeness(suite)
        if completeness < 0.9:  # 90% minimum completeness
            errors.append(f"Test completeness too low: {completeness:.2%}")
        
        return len(errors) == 0, errors
    
    def _check_component_coverage(self, suite: TestSuite, blueprint: ArchitectureBlueprint) -> float:
        """Check test coverage of blueprint components"""
        tested_components = set()
        for spec in suite.specifications:
            tested_components.add(spec.component_name)
        
        blueprint_components = set(blueprint.components)
        if not blueprint_components:
            return 1.0
        
        coverage = len(tested_components.intersection(blueprint_components)) / len(blueprint_components)
        return coverage
    
    def _validate_resource_requirements(self, suite: TestSuite, blueprint: ArchitectureBlueprint) -> bool:
        """Validate resource requirements against limits"""
        suite_resources = suite.resource_requirements
        blueprint_limits = blueprint.resource_limits
        
        # Check memory requirements
        if suite_resources.get('memory_mb', 0) > blueprint_limits.get('memory_mb', 32768):
            return False
        
        # Check GPU requirements
        if suite_resources.get('gpu_memory_mb', 0) > blueprint_limits.get('gpu_memory_mb', 12288):
            return False
        
        # Check CPU requirements
        if suite_resources.get('cpu_cores', 0) > blueprint_limits.get('cpu_cores', 8):
            return False
        
        return True
    
    def _check_test_completeness(self, suite: TestSuite) -> float:
        """Check completeness of test specifications"""
        if not suite.specifications:
            return 0.0
        
        complete_tests = 0
        for spec in suite.specifications:
            if self._is_test_complete(spec):
                complete_tests += 1
        
        return complete_tests / len(suite.specifications)
    
    def _is_test_complete(self, spec: TestSpecification) -> bool:
        """Check if individual test specification is complete"""
        required_fields = [
            spec.component_name,
            spec.test_type,
            spec.test_name,
            spec.description,
            spec.preconditions,
            spec.steps,
            spec.expected_results,
            spec.assertions
        ]
        
        return all(field for field in required_fields)

class ArchitectPhase:
    """
    Architect Phase - Generates comprehensive test suites as specifications
    
    This phase takes the meeting results and generates complete test specifications
    that will drive the implementation in the Grind Phase.
    """
    
    def __init__(self, 
                 redis_bus: RedisBus,
                 global_arbiter: GlobalArbiter,
                 identity_firewall: IdentityFirewall,
                 bikameral_memory: BikameralMemory,
                 chronos: ChronosHeartbeat):
        self.redis_bus = redis_bus
        self.global_arbiter = global_arbiter
        self.identity_firewall = identity_firewall
        self.bikameral_memory = bikameral_memory
        self.chronos = chronos
        self.pattern_generator = TestPatternGenerator()
        self.test_validator = TestValidator()
        
        logger.info("Architect Phase initialized")
    
    async def generate_architecture(self, meeting_result: Dict[str, Any]) -> TestSuite:
        """
        Generate comprehensive test suite from meeting results
        
        Args:
            meeting_result: Result from Meeting Phase containing contract and task manifest
            
        Returns:
            Complete test suite specification
        """
        try:
            logger.info(f"Starting Architect Phase for contract {meeting_result.get('contract_id')}")
            
            # 1. Extract architecture blueprint from meeting results
            blueprint = self._extract_blueprint(meeting_result)
            
            # 2. Generate test specifications for each component
            specifications = await self._generate_specifications(blueprint)
            
            # 3. Validate resource requirements
            resource_requirements = self._calculate_resource_requirements(specifications)
            
            # 4. Create comprehensive test suite
            suite = TestSuite(
                suite_id=self._generate_suite_id(blueprint.contract_id),
                contract_id=blueprint.contract_id,
                specifications=specifications,
                coverage_metrics=self._calculate_coverage(specifications, blueprint),
                complexity_score=self._calculate_complexity(specifications),
                estimated_execution_time=self._estimate_execution_time(specifications),
                resource_requirements=resource_requirements,
                generated_at=datetime.now()
            )
            
            # 5. Validate test suite
            is_valid, errors = self.test_validator.validate_test_suite(suite, blueprint)
            if not is_valid:
                logger.error(f"Test suite validation failed: {errors}")
                raise ValueError(f"Invalid test suite: {errors}")
            
            # 6. Store test suite in memory
            await self._store_test_suite(suite)
            
            # 7. Publish completion event
            await self._publish_completion(suite)
            
            logger.info(f"Architect Phase completed for contract {blueprint.contract_id}")
            return suite
            
        except Exception as e:
            logger.error(f"Architect Phase failed: {e}")
            await self._publish_error(meeting_result.get('contract_id'), str(e))
            raise
    
    def _extract_blueprint(self, meeting_result: Dict[str, Any]) -> ArchitectureBlueprint:
        """Extract architecture blueprint from meeting results"""
        return ArchitectureBlueprint(
            contract_id=meeting_result['contract_id'],
            task_manifest=meeting_result['task_manifest'],
            components=meeting_result.get('components', []),
            interfaces=meeting_result.get('interfaces', []),
            data_flows=meeting_result.get('data_flows', []),
            resource_limits=meeting_result.get('resource_limits', {}),
            definition_of_done=meeting_result.get('definition_of_done', [])
        )
    
    async def _generate_specifications(self, blueprint: ArchitectureBlueprint) -> List[TestSpecification]:
        """Generate test specifications for each component"""
        specifications = []
        
        # Generate tests for each component
        for component in blueprint.components:
            component_specs = await self._generate_component_tests(component, blueprint)
            specifications.extend(component_specs)
        
        # Generate integration tests
        integration_specs = await self._generate_integration_tests(blueprint)
        specifications.extend(integration_specs)
        
        # Generate security tests
        security_specs = await self._generate_security_tests(blueprint)
        specifications.extend(security_specs)
        
        # Generate performance tests
        performance_specs = await self._generate_performance_tests(blueprint)
        specifications.extend(performance_specs)
        
        return specifications
    
    async def _generate_component_tests(self, component: str, blueprint: ArchitectureBlueprint) -> List[TestSpecification]:
        """Generate tests for individual component"""
        specifications = []
        
        # Find component interface
        interface = self._find_component_interface(component, blueprint)
        component_type = self._determine_component_type(component, interface)
        
        # Generate tests using appropriate pattern
        if component_type in self.pattern_generator.patterns:
            pattern_func = self.pattern_generator.patterns[component_type]
            component_tests = pattern_func(component, interface or {})
            specifications.extend(component_tests)
        
        # Generate additional component-specific tests
        additional_tests = await self._generate_additional_tests(component, blueprint)
        specifications.extend(additional_tests)
        
        return specifications
    
    def _find_component_interface(self, component: str, blueprint: ArchitectureBlueprint) -> Optional[Dict[str, Any]]:
        """Find interface definition for component"""
        for interface in blueprint.interfaces:
            if interface.get('component') == component:
                return interface
        return None
    
    def _determine_component_type(self, component: str, interface: Optional[Dict[str, Any]]) -> str:
        """Determine component type based on name and interface"""
        if interface and interface.get('type'):
            return interface['type']
        
        # Infer from component name
        if 'api' in component.lower() or 'endpoint' in component.lower():
            return 'api_endpoint'
        elif 'model' in component.lower() or 'database' in component.lower():
            return 'database_model'
        elif 'ui' in component.lower() or 'component' in component.lower():
            return 'ui_component'
        elif 'algorithm' in component.lower() or 'processor' in component.lower():
            return 'algorithm'
        elif 'memory' in component.lower():
            return 'memory_system'
        elif 'orchestration' in component.lower() or 'phase' in component.lower():
            return 'orchestration'
        elif 'scanner' in component.lower():
            return 'scanner'
        else:
            return 'integration'
    
    async def _generate_additional_tests(self, component: str, blueprint: ArchitectureBlueprint) -> List[TestSpecification]:
        """Generate additional component-specific tests"""
        additional_tests = []
        
        # Add tests based on Definition of Done
        for dod_item in blueprint.definition_of_done:
            if component.lower() in dod_item.lower():
                test = TestSpecification(
                    component_name=component,
                    test_type='integration',
                    test_name=f"{component}_dod_{len(additional_tests)}",
                    description=f"Test Definition of Done: {dod_item}",
                    preconditions=["Component is implemented"],
                    steps=[
                        f"Verify {dod_item}",
                        "Validate against acceptance criteria"
                    ],
                    expected_results=[
                        f"Definition of Done item '{dod_item}' is satisfied",
                        "All acceptance criteria are met"
                    ],
                    test_data={'dod_item': dod_item},
                    assertions=["dod_criteria_met"],
                    mock_dependencies=[]
                )
                additional_tests.append(test)
        
        return additional_tests
    
    async def _generate_integration_tests(self, blueprint: ArchitectureBlueprint) -> List[TestSpecification]:
        """Generate integration tests for data flows"""
        integration_tests = []
        
        for i, data_flow in enumerate(blueprint.data_flows):
            test = TestSpecification(
                component_name=f"integration_flow_{i}",
                test_type='integration',
                test_name=f"data_flow_{i}_integration",
                description=f"Test data flow: {data_flow.get('description', 'unnamed')}",
                preconditions=[
                    "All components in flow are implemented",
                    "Data sources are available"
                ],
                steps=[
                    "Initialize data at source",
                    "Trigger data flow",
                    "Verify data at each stage",
                    "Validate final output"
                ],
                expected_results=[
                    "Data flows through all stages",
                    "Data integrity is maintained",
                    "Final output is correct"
                ],
                test_data={
                    'source_data': data_flow.get('source_data', {}),
                    'expected_output': data_flow.get('expected_output', {})
                },
                assertions=[
                    "data_flow_completed",
                    "data_integrity_maintained",
                    "output_matches_expected"
                ],
                mock_dependencies=['external_data_sources']
            )
            integration_tests.append(test)
        
        return integration_tests
    
    async def _generate_security_tests(self, blueprint: ArchitectureBlueprint) -> List[TestSpecification]:
        """Generate security tests"""
        security_tests = []
        
        # Identity Firewall tests
        firewall_test = TestSpecification(
            component_name="identity_firewall",
            test_type='security',
            test_name="identity_firewall_protection",
            description="Test Identity Firewall protection mechanisms",
            preconditions=["Identity Firewall is active"],
            steps=[
                "Attempt unauthorized access to soul.md",
                "Attempt privilege escalation",
                "Test input validation"
            ],
            expected_results=[
                "Unauthorized access is blocked",
                "Privileges are properly enforced",
                "Malicious inputs are rejected"
            ],
            test_data={
                'unauthorized_request': {'type': 'soul_access', 'user': 'unauthorized'},
                'malicious_input': "'; DROP TABLE users; --"
            },
            assertions=[
                "access_denied_for_unauthorized",
                "input_sanitized_properly",
                "audit_log_created"
            ],
            mock_dependencies=['soul_md_file'],
            security_requirements=[
                "No sensitive data in logs",
                "All access attempts logged",
                "Rate limiting enforced"
            ]
        )
        security_tests.append(firewall_test)
        
        return security_tests
    
    async def _generate_performance_tests(self, blueprint: ArchitectureBlueprint) -> List[TestSpecification]:
        """Generate performance tests"""
        performance_tests = []
        
        # Resource limit tests
        resource_test = TestSpecification(
            component_name="resource_management",
            test_type='performance',
            test_name="resource_limit_enforcement",
            description="Test enforcement of resource limits",
            preconditions=["Resource limits are configured"],
            steps=[
                "Attempt to exceed memory limit (32GB)",
                "Attempt to exceed GPU memory limit (12GB)",
                "Attempt to exceed CPU core limit (8 cores)"
            ],
            expected_results=[
                "Memory allocation is limited to 32GB",
                "GPU memory is limited to 12GB",
                "CPU usage is limited to 8 cores"
            ],
            test_data={
                'memory_test_size': 35000,  # MB, exceeds 32GB limit
                'gpu_memory_test': 13000,   # MB, exceeds 12GB limit
                'cpu_test_cores': 10        # Exceeds 8 core limit
            },
            assertions=[
                "memory_allocation_limited_to_32gb",
                "gpu_memory_limited_to_12gb",
                "cpu_cores_limited_to_8"
            ],
            mock_dependencies=['system_resources'],
            performance_requirements={
                'max_memory_usage': 32768,  # 32GB in MB
                'max_gpu_memory': 12288,    # 12GB in MB
                'max_cpu_cores': 8
            }
        )
        performance_tests.append(resource_test)
        
        return performance_tests
    
    def _calculate_resource_requirements(self, specifications: List[TestSpecification]) -> Dict[str, Any]:
        """Calculate resource requirements for test suite"""
        total_memory = 0
        total_gpu_memory = 0
        max_cpu_cores = 0
        total_execution_time = 0
        
        for spec in specifications:
            # Estimate memory based on test type
            if spec.test_type == 'performance':
                total_memory += 2048  # 2GB for performance tests
                total_gpu_memory += 1024  # 1GB for GPU tests
                max_cpu_cores = max(max_cpu_cores, 4)
            elif spec.test_type == 'integration':
                total_memory += 1024  # 1GB for integration tests
                total_gpu_memory += 512   # 512MB for integration
                max_cpu_cores = max(max_cpu_cores, 2)
            else:  # unit tests
                total_memory += 256   # 256MB for unit tests
                total_gpu_memory += 128   # 128MB for unit tests
                max_cpu_cores = max(max_cpu_cores, 1)
            
            # Add execution time
            total_execution_time += spec.performance_requirements.get('max_execution_time', 1.0) if spec.performance_requirements else 1.0
        
        return {
            'memory_mb': total_memory,
            'gpu_memory_mb': total_gpu_memory,
            'cpu_cores': max_cpu_cores,
            'estimated_execution_time': total_execution_time
        }
    
    def _calculate_coverage(self, specifications: List[TestSpecification], blueprint: ArchitectureBlueprint) -> Dict[str, float]:
        """Calculate test coverage metrics"""
        coverage_by_type = {}
        
        for spec in specifications:
            test_type = spec.test_type
            if test_type not in coverage_by_type:
                coverage_by_type[test_type] = 0
            coverage_by_type[test_type] += 1
        
        # Calculate percentages
        total_tests = len(specifications)
        coverage_metrics = {}
        
        for test_type, count in coverage_by_type.items():
            coverage_metrics[f"{test_type}_coverage"] = count / total_tests
        
        # Overall coverage
        coverage_metrics['overall_coverage'] = min(1.0, total_tests / max(len(blueprint.components), 1))
        
        return coverage_metrics
    
    def _calculate_complexity(self, specifications: List[TestSpecification]) -> float:
        """Calculate complexity score of test suite"""
        complexity_factors = {
            'test_count': len(specifications) * 0.1,
            'integration_tests': len([s for s in specifications if s.test_type == 'integration']) * 0.3,
            'performance_tests': len([s for s in specifications if s.test_type == 'performance']) * 0.4,
            'security_tests': len([s for s in specifications if s.test_type == 'security']) * 0.5,
            'mock_dependencies': sum(len(s.mock_dependencies) for s in specifications) * 0.05
        }
        
        return sum(complexity_factors.values())
    
    def _estimate_execution_time(self, specifications: List[TestSpecification]) -> float:
        """Estimate total execution time for test suite"""
        base_times = {
            'unit': 0.1,        # 0.1 seconds per unit test
            'integration': 1.0, # 1 second per integration test
            'performance': 30.0, # 30 seconds per performance test
            'security': 2.0,    # 2 seconds per security test
            'e2e': 10.0         # 10 seconds per end-to-end test
        }
        
        total_time = 0
        for spec in specifications:
            test_type = spec.test_type
            base_time = base_times.get(test_type, 1.0)
            total_time += base_time
        
        # Add setup/teardown time
        total_time += len(specifications) * 0.05
        
        return total_time
    
    def _generate_suite_id(self, contract_id: str) -> str:
        """Generate unique test suite ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{contract_id}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    async def _store_test_suite(self, suite: TestSuite):
        """Store test suite in bikameral memory"""
        suite_data = {
            'suite_id': suite.suite_id,
            'contract_id': suite.contract_id,
            'specifications': [self._specification_to_dict(spec) for spec in suite.specifications],
            'coverage_metrics': suite.coverage_metrics,
            'complexity_score': suite.complexity_score,
            'estimated_execution_time': suite.estimated_execution_time,
            'resource_requirements': suite.resource_requirements,
            'generated_at': suite.generated_at.isoformat()
        }
        
        # Store in short-term memory (Redis) for immediate access
        await self.bikameral_memory.store_short_term(
            f"test_suite:{suite.suite_id}",
            suite_data,
            ttl=3600  # 1 hour TTL
        )
        
        # Store in long-term memory (PostgreSQL) for persistence
        await self.bikameral_memory.store_long_term(
            f"test_suite:{suite.suite_id}",
            suite_data
        )
    
    def _specification_to_dict(self, spec: TestSpecification) -> Dict[str, Any]:
        """Convert test specification to dictionary"""
        return {
            'component_name': spec.component_name,
            'test_type': spec.test_type,
            'test_name': spec.test_name,
            'description': spec.description,
            'preconditions': spec.preconditions,
            'steps': spec.steps,
            'expected_results': spec.expected_results,
            'test_data': spec.test_data,
            'assertions': spec.assertions,
            'mock_dependencies': spec.mock_dependencies,
            'performance_requirements': spec.performance_requirements,
            'security_requirements': spec.security_requirements
        }
    
    async def _publish_completion(self, suite: TestSuite):
        """Publish completion event to Redis bus"""
        event = {
            'event_type': 'architect_phase_completed',
            'contract_id': suite.contract_id,
            'suite_id': suite.suite_id,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'total_tests': len(suite.specifications),
                'complexity_score': suite.complexity_score,
                'estimated_execution_time': suite.estimated_execution_time
            }
        }
        
        await self.redis_bus.publish('orchestration.events', event)
    
    async def _publish_error(self, contract_id: str, error_message: str):
        """Publish error event to Redis bus"""
        event = {
            'event_type': 'architect_phase_error',
            'contract_id': contract_id,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.redis_bus.publish('orchestration.events', event)

# Factory function for easy integration
def create_architect_phase(runtime_context: Dict[str, Any]) -> ArchitectPhase:
    """Factory function to create Architect Phase instance"""
    return ArchitectPhase(
        redis_bus=runtime_context['redis_bus'],
        global_arbiter=runtime_context['global_arbiter'],
        identity_firewall=runtime_context['identity_firewall'],
        bikameral_memory=runtime_context['bikameral_memory'],
        chronos=runtime_context['chronos_heartbeat']
    )