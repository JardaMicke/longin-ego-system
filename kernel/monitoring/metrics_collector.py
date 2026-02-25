"""
Pokročilý systém metrik pro LONGIN EGO
Integruje Prometheus metriky s MSCA architekturou pro komplexní monitoring
"""

import time
import psutil
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import threading
from prometheus_client import Counter, Histogram, Gauge, Info, Enum, start_http_server
import redis.asyncio as redis
import GPUtil
from abc import ABC, abstractmethod

from kernel.core.exceptions import MetricsError
from kernel.core.config import Config

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Systémové metriky pro LONGIN EGO"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    gpu_utilization: Optional[float] = None
    gpu_memory_used_gb: Optional[float] = None
    gpu_memory_total_gb: Optional[float] = None
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    process_count: int = 0
    thread_count: int = 0

@dataclass
class ApplicationMetrics:
    """Aplikační metriky pro LONGIN EGO"""
    timestamp: datetime
    active_sessions: int
    total_requests: int
    error_rate: float
    average_response_time: float
    auth_success_rate: float
    memory_cache_hit_rate: float
    orchestration_queue_size: int
    scanner_queue_size: int
    api_requests_per_second: float
    active_websockets: int
    redis_connections: int
    database_connections: int

@dataclass
class MSCAMetrics:
    """MSCA (Module-Sentinel-Connector-Adapter) metriky"""
    timestamp: datetime
    module_count: int
    sentinel_count: int
    connector_count: int
    adapter_count: int
    module_health_score: float
    sentinel_alert_count: int
    connector_throughput: float
    adapter_error_rate: float
    chronos_cycle_duration: float
    memory_module_usage: float
    orchestration_module_usage: float
    scanner_module_usage: float

@dataclass
class ERTDSDMetrics:
    """ERTDSD (EGO Ruled Test-Driven Self-Development) metriky"""
    timestamp: datetime
    meeting_phase_active: bool
    architect_phase_active: bool
    grind_phase_active: bool
    presentation_phase_active: bool
    meeting_success_rate: float
    architect_test_coverage: float
    grind_build_success_rate: float
    presentation_merge_success_rate: float
    autonomous_cycles_per_hour: float
    code_quality_score: float
    test_execution_time: float
    contract_compliance_rate: float

class MetricsCollector(ABC):
    """Abstraktní base class pro metriky kolektory"""
    
    @abstractmethod
    async def collect(self) -> Dict[str, Any]:
        """Shromáždění metrik"""
        pass
    
    @abstractmethod
    def get_metric_names(self) -> List[str]:
        """Získání názvů metrik"""
        pass

class SystemMetricsCollector(MetricsCollector):
    """Kolektor systémových metrik"""
    
    def __init__(self, collection_interval: int = 5):
        self.collection_interval = collection_interval
        self.last_network_stats = None
        self.gpu_available = self._check_gpu_availability()
        
        # Prometheus metriky
        self.cpu_usage = Gauge('longin_ego_cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = Gauge('longin_ego_memory_usage_percent', 'Memory usage percentage')
        self.memory_used = Gauge('longin_ego_memory_used_gb', 'Memory used in GB')
        self.memory_total = Gauge('longin_ego_memory_total_gb', 'Total memory in GB')
        self.disk_usage = Gauge('longin_ego_disk_usage_percent', 'Disk usage percentage')
        self.disk_used = Gauge('longin_ego_disk_used_gb', 'Disk used in GB')
        self.disk_total = Gauge('longin_ego_disk_total_gb', 'Total disk in GB')
        self.gpu_utilization = Gauge('longin_ego_gpu_utilization_percent', 'GPU utilization percentage')
        self.gpu_memory_used = Gauge('longin_ego_gpu_memory_used_gb', 'GPU memory used in GB')
        self.gpu_memory_total = Gauge('longin_ego_gpu_memory_total_gb', 'Total GPU memory in GB')
        self.network_sent = Counter('longin_ego_network_sent_mb_total', 'Total network data sent in MB')
        self.network_recv = Counter('longin_ego_network_recv_mb_total', 'Total network data received in MB')
        self.process_count = Gauge('longin_ego_process_count', 'Number of processes')
        self.thread_count = Gauge('longin_ego_thread_count', 'Number of threads')
    
    def _check_gpu_availability(self) -> bool:
        """Kontrola dostupnosti GPU"""
        try:
            GPUtil.getGPUs()
            return True
        except:
            return False
    
    async def collect(self) -> SystemMetrics:
        """Shromáždění systémových metrik"""
        try:
            # CPU a paměť
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Síťové statistiky
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / 1024 / 1024
            network_recv_mb = network.bytes_recv / 1024 / 1024
            
            # GPU metriky
            gpu_utilization = None
            gpu_memory_used_gb = None
            gpu_memory_total_gb = None
            
            if self.gpu_available:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # Používáme první GPU
                        gpu_utilization = gpu.load * 100
                        gpu_memory_used_gb = gpu.memoryUsed / 1024
                        gpu_memory_total_gb = gpu.memoryTotal / 1024
                except Exception as e:
                    logger.warning(f"Chyba při čtení GPU metrik: {e}")
            
            # Procesy a vlákna
            process_count = len(psutil.pids())
            current_process = psutil.Process()
            thread_count = current_process.num_threads()
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_gb=memory.used / 1024 / 1024 / 1024,
                memory_total_gb=memory.total / 1024 / 1024 / 1024,
                disk_percent=disk.percent,
                disk_used_gb=disk.used / 1024 / 1024 / 1024,
                disk_total_gb=disk.total / 1024 / 1024 / 1024,
                gpu_utilization=gpu_utilization,
                gpu_memory_used_gb=gpu_memory_used_gb,
                gpu_memory_total_gb=gpu_memory_total_gb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                process_count=process_count,
                thread_count=thread_count
            )
            
            # Aktualizace Prometheus metrik
            self._update_prometheus_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Chyba při sběru systémových metrik: {e}")
            raise MetricsError(f"Systémové metriky selhaly: {e}")
    
    def _update_prometheus_metrics(self, metrics: SystemMetrics):
        """Aktualizace Prometheus metrik"""
        self.cpu_usage.set(metrics.cpu_percent)
        self.memory_usage.set(metrics.memory_percent)
        self.memory_used.set(metrics.memory_used_gb)
        self.memory_total.set(metrics.memory_total_gb)
        self.disk_usage.set(metrics.disk_percent)
        self.disk_used.set(metrics.disk_used_gb)
        self.disk_total.set(metrics.disk_total_gb)
        
        if metrics.gpu_utilization is not None:
            self.gpu_utilization.set(metrics.gpu_utilization)
        if metrics.gpu_memory_used_gb is not None:
            self.gpu_memory_used.set(metrics.gpu_memory_used_gb)
        if metrics.gpu_memory_total_gb is not None:
            self.gpu_memory_total.set(metrics.gpu_memory_total_gb)
        
        self.process_count.set(metrics.process_count)
        self.thread_count.set(metrics.thread_count)
    
    def get_metric_names(self) -> List[str]:
        """Získání názvů metrik"""
        return [
            'cpu_percent', 'memory_percent', 'memory_used_gb', 'memory_total_gb',
            'disk_percent', 'disk_used_gb', 'disk_total_gb', 'gpu_utilization',
            'gpu_memory_used_gb', 'gpu_memory_total_gb', 'network_sent_mb',
            'network_recv_mb', 'process_count', 'thread_count'
        ]

class ApplicationMetricsCollector(MetricsCollector):
    """Kolektor aplikačních metrik"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        
        # Prometheus metriky
        self.active_sessions = Gauge('longin_ego_active_sessions', 'Number of active sessions')
        self.total_requests = Counter('longin_ego_requests_total', 'Total number of requests', ['method', 'endpoint', 'status'])
        self.request_duration = Histogram('longin_ego_request_duration_seconds', 'Request duration in seconds', ['method', 'endpoint'])
        self.error_rate = Gauge('longin_ego_error_rate_percent', 'Error rate percentage')
        self.auth_success_rate = Gauge('longin_ego_auth_success_rate_percent', 'Authentication success rate percentage')
        self.memory_cache_hit_rate = Gauge('longin_ego_cache_hit_rate_percent', 'Memory cache hit rate percentage')
        self.orchestration_queue_size = Gauge('longin_ego_orchestration_queue_size', 'Orchestration queue size')
        self.scanner_queue_size = Gauge('longin_ego_scanner_queue_size', 'Scanner queue size')
        self.api_requests_per_second = Gauge('longin_ego_requests_per_second', 'API requests per second')
        self.active_websockets = Gauge('longin_ego_active_websockets', 'Number of active WebSocket connections')
        self.redis_connections = Gauge('longin_ego_redis_connections', 'Number of Redis connections')
        self.database_connections = Gauge('longin_ego_database_connections', 'Number of database connections')
    
    async def collect(self) -> ApplicationMetrics:
        """Shromáždění aplikačních metrik"""
        try:
            # Session metriky
            active_sessions = await self._get_active_sessions()
            
            # Request metriky
            total_requests = sum(self.request_counts.values())
            error_rate = self._calculate_error_rate()
            avg_response_time = self._calculate_average_response_time()
            requests_per_second = self._calculate_requests_per_second()
            
            # Auth metriky
            auth_success_rate = await self._calculate_auth_success_rate()
            
            # Cache metriky
            cache_hit_rate = await self._calculate_cache_hit_rate()
            
            # Queue metriky
            orchestration_queue = await self._get_queue_size("orchestration")
            scanner_queue = await self._get_queue_size("scanner")
            
            # Connection metriky
            redis_connections = await self._get_redis_connections()
            database_connections = await self._get_database_connections()
            
            # WebSocket metriky
            active_websockets = await self._get_active_websockets()
            
            metrics = ApplicationMetrics(
                timestamp=datetime.now(),
                active_sessions=active_sessions,
                total_requests=total_requests,
                error_rate=error_rate,
                average_response_time=avg_response_time,
                auth_success_rate=auth_success_rate,
                memory_cache_hit_rate=cache_hit_rate,
                orchestration_queue_size=orchestration_queue,
                scanner_queue_size=scanner_queue,
                api_requests_per_second=requests_per_second,
                active_websockets=active_websockets,
                redis_connections=redis_connections,
                database_connections=database_connections
            )
            
            # Aktualizace Prometheus metrik
            self._update_prometheus_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Chyba při sběru aplikačních metrik: {e}")
            raise MetricsError(f"Aplikační metriky selhaly: {e}")
    
    async def _get_active_sessions(self) -> int:
        """Získání počtu aktivních relací"""
        try:
            # Počítáme aktivní session klíče v Redis
            session_keys = await self.redis_client.keys("session:*")
            return len(session_keys)
        except:
            return 0
    
    def _calculate_error_rate(self) -> float:
        """Výpočet míry chyb"""
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())
        
        if total_requests == 0:
            return 0.0
        
        return (total_errors / total_requests) * 100
    
    def _calculate_average_response_time(self) -> float:
        """Výpočet průměrné doby odezvy"""
        all_times = []
        for times in self.response_times.values():
            all_times.extend(times)
        
        if not all_times:
            return 0.0
        
        return sum(all_times) / len(all_times)
    
    def _calculate_requests_per_second(self) -> float:
        """Výpočet požadavků za sekundu"""
        # Zjednodušený výpočet - v reálné implementaci by se použil časový okno
        total_requests = sum(self.request_counts.values())
        return total_requests / 60  # Předpokládáme minutové okno
    
    async def _calculate_auth_success_rate(self) -> float:
        """Výpočet úspěšnosti autentizace"""
        try:
            # Z Redis získáme auth statistiky
            auth_success = await self.redis_client.get("auth:success_count") or 0
            auth_failure = await self.redis_client.get("auth:failure_count") or 0
            
            total_auth = int(auth_success) + int(auth_failure)
            if total_auth == 0:
                return 100.0
            
            return (int(auth_success) / total_auth) * 100
        except:
            return 100.0
    
    async def _calculate_cache_hit_rate(self) -> float:
        """Výpočet úspěšnosti cache"""
        try:
            cache_hits = await self.redis_client.get("cache:hits") or 0
            cache_misses = await self.redis_client.get("cache:misses") or 0
            
            total_cache = int(cache_hits) + int(cache_misses)
            if total_cache == 0:
                return 0.0
            
            return (int(cache_hits) / total_cache) * 100
        except:
            return 0.0
    
    async def _get_queue_size(self, queue_name: str) -> int:
        """Získání velikosti fronty"""
        try:
            queue_key = f"queue:{queue_name}"
            return await self.redis_client.llen(queue_key) or 0
        except:
            return 0
    
    async def _get_redis_connections(self) -> int:
        """Získání počtu Redis připojení"""
        try:
            info = await self.redis_client.info()
            return info.get("connected_clients", 0)
        except:
            return 0
    
    async def _get_database_connections(self) -> int:
        """Získání počtu databázových připojení"""
        # TODO: Implementovat skutečné čtení DB připojení
        return 0
    
    async def _get_active_websockets(self) -> int:
        """Získání počtu aktivních WebSocket připojení"""
        try:
            return await self.redis_client.scard("active_websockets") or 0
        except:
            return 0
    
    def _update_prometheus_metrics(self, metrics: ApplicationMetrics):
        """Aktualizace Prometheus metrik"""
        self.active_sessions.set(metrics.active_sessions)
        self.error_rate.set(metrics.error_rate)
        self.auth_success_rate.set(metrics.auth_success_rate)
        self.memory_cache_hit_rate.set(metrics.memory_cache_hit_rate)
        self.orchestration_queue_size.set(metrics.orchestration_queue_size)
        self.scanner_queue_size.set(metrics.scanner_queue_size)
        self.api_requests_per_second.set(metrics.api_requests_per_second)
        self.active_websockets.set(metrics.active_websockets)
        self.redis_connections.set(metrics.redis_connections)
        self.database_connections.set(metrics.database_connections)
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Zaznamenání HTTP požadavku"""
        self.total_requests.labels(method=method, endpoint=endpoint, status=status_code).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        
        # Uložení pro interní statistiky
        key = f"{method}:{endpoint}"
        self.request_counts[key] += 1
        
        if status_code >= 400:
            self.error_counts[key] += 1
        
        self.response_times[key].append(duration)
        
        # Omezení velikosti seznamu
        if len(self.response_times[key]) > 1000:
            self.response_times[key] = self.response_times[key][-1000:]
    
    def get_metric_names(self) -> List[str]:
        """Získání názvů metrik"""
        return [
            'active_sessions', 'total_requests', 'error_rate', 'average_response_time',
            'auth_success_rate', 'memory_cache_hit_rate', 'orchestration_queue_size',
            'scanner_queue_size', 'api_requests_per_second', 'active_websockets',
            'redis_connections', 'database_connections'
        ]

class MSCAMetricsCollector(MetricsCollector):
    """Kolektor MSCA (Module-Sentinel-Connector-Adapter) metrik"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        
        # Prometheus metriky
        self.module_count = Gauge('longin_ego_module_count', 'Number of active modules')
        self.sentinel_count = Gauge('longin_ego_sentinel_count', 'Number of active sentinels')
        self.connector_count = Gauge('longin_ego_connector_count', 'Number of active connectors')
        self.adapter_count = Gauge('longin_ego_adapter_count', 'Number of active adapters')
        self.module_health_score = Gauge('longin_ego_module_health_score', 'Module health score (0-100)')
        self.sentinel_alert_count = Counter('longin_ego_sentinel_alerts_total', 'Total number of sentinel alerts')
        self.connector_throughput = Gauge('longin_ego_connector_throughput_per_second', 'Connector throughput per second')
        self.adapter_error_rate = Gauge('longin_ego_adapter_error_rate_percent', 'Adapter error rate percentage')
        self.chronos_cycle_duration = Histogram('longin_ego_chronos_cycle_duration_seconds', 'Chronos cycle duration in seconds')
        self.memory_module_usage = Gauge('longin_ego_memory_module_usage_percent', 'Memory module usage percentage')
        self.orchestration_module_usage = Gauge('longin_ego_orchestration_module_usage_percent', 'Orchestration module usage percentage')
        self.scanner_module_usage = Gauge('longin_ego_scanner_module_usage_percent', 'Scanner module usage percentage')
    
    async def collect(self) -> MSCAMetrics:
        """Shromáždění MSCA metrik"""
        try:
            # Počty komponent
            module_count = await self._get_component_count("module")
            sentinel_count = await self._get_component_count("sentinel")
            connector_count = await self._get_component_count("connector")
            adapter_count = await self._get_component_count("adapter")
            
            # Health score
            health_score = await self._calculate_module_health_score()
            
            # Alert count
            alert_count = await self._get_alert_count()
            
            # Throughput
            connector_throughput = await self._calculate_connector_throughput()
            
            # Error rate
            adapter_error_rate = await self._calculate_adapter_error_rate()
            
            # Chronos cycle
            chronos_duration = await self._get_chronos_cycle_duration()
            
            # Usage percentages
            memory_usage = await self._get_module_usage("memory")
            orchestration_usage = await self._get_module_usage("orchestration")
            scanner_usage = await self._get_module_usage("scanner")
            
            metrics = MSCAMetrics(
                timestamp=datetime.now(),
                module_count=module_count,
                sentinel_count=sentinel_count,
                connector_count=connector_count,
                adapter_count=adapter_count,
                module_health_score=health_score,
                sentinel_alert_count=alert_count,
                connector_throughput=connector_throughput,
                adapter_error_rate=adapter_error_rate,
                chronos_cycle_duration=chronos_duration,
                memory_module_usage=memory_usage,
                orchestration_module_usage=orchestration_usage,
                scanner_module_usage=scanner_usage
            )
            
            # Aktualizace Prometheus metrik
            self._update_prometheus_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Chyba při sběru MSCA metrik: {e}")
            raise MetricsError(f"MSCA metriky selhaly: {e}")
    
    async def _get_component_count(self, component_type: str) -> int:
        """Získání počtu komponent"""
        try:
            keys = await self.redis_client.keys(f"{component_type}:*")
            return len(keys)
        except:
            return 0
    
    async def _calculate_module_health_score(self) -> float:
        """Výpočet health score modulů"""
        # TODO: Implementovat skutečný výpočet health score
        return 85.0
    
    async def _get_alert_count(self) -> int:
        """Získání počtu alertů"""
        try:
            return await self.redis_client.scard("sentinel:alerts") or 0
        except:
            return 0
    
    async def _calculate_connector_throughput(self) -> float:
        """Výpočet throughput pro connectory"""
        # TODO: Implementovat skutečný výpočet throughput
        return 42.5
    
    async def _calculate_adapter_error_rate(self) -> float:
        """Výpočet error rate pro adaptéry"""
        # TODO: Implementovat skutečný výpočet error rate
        return 2.3
    
    async def _get_chronos_cycle_duration(self) -> float:
        """Získání délky Chronos cyklu"""
        try:
            duration = await self.redis_client.get("chronos:last_cycle_duration") or 15.0
            return float(duration)
        except:
            return 15.0
    
    async def _get_module_usage(self, module_name: str) -> float:
        """Získání využití modulu"""
        # TODO: Implementovat skutečné čtení využití modulu
        usage_map = {
            "memory": 45.2,
            "orchestration": 23.8,
            "scanner": 67.1
        }
        return usage_map.get(module_name, 0.0)
    
    def _update_prometheus_metrics(self, metrics: MSCAMetrics):
        """Aktualizace Prometheus metrik"""
        self.module_count.set(metrics.module_count)
        self.sentinel_count.set(metrics.sentinel_count)
        self.connector_count.set(metrics.connector_count)
        self.adapter_count.set(metrics.adapter_count)
        self.module_health_score.set(metrics.module_health_score)
        self.connector_throughput.set(metrics.connector_throughput)
        self.adapter_error_rate.set(metrics.adapter_error_rate)
        self.memory_module_usage.set(metrics.memory_module_usage)
        self.orchestration_module_usage.set(metrics.orchestration_module_usage)
        self.scanner_module_usage.set(metrics.scanner_module_usage)
    
    def get_metric_names(self) -> List[str]:
        """Získání názvů metrik"""
        return [
            'module_count', 'sentinel_count', 'connector_count', 'adapter_count',
            'module_health_score', 'sentinel_alert_count', 'connector_throughput',
            'adapter_error_rate', 'chronos_cycle_duration', 'memory_module_usage',
            'orchestration_module_usage', 'scanner_module_usage'
        ]

class ERTDSDMetricsCollector(MetricsCollector):
    """Kolektor ERTDSD (EGO Ruled Test-Driven Self-Development) metrik"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        
        # Prometheus metriky
        self.meeting_phase_active = Gauge('longin_ego_meeting_phase_active', 'Meeting phase is active (0/1)')
        self.architect_phase_active = Gauge('longin_ego_architect_phase_active', 'Architect phase is active (0/1)')
        self.grind_phase_active = Gauge('longin_ego_grind_phase_active', 'Grind phase is active (0/1)')
        self.presentation_phase_active = Gauge('longin_ego_presentation_phase_active', 'Presentation phase is active (0/1)')
        self.meeting_success_rate = Gauge('longin_ego_meeting_success_rate_percent', 'Meeting phase success rate percentage')
        self.architect_test_coverage = Gauge('longin_ego_architect_test_coverage_percent', 'Architect phase test coverage percentage')
        self.grind_build_success_rate = Gauge('longin_ego_grind_build_success_rate_percent', 'Grind phase build success rate percentage')
        self.presentation_merge_success_rate = Gauge('longin_ego_presentation_merge_success_rate_percent', 'Presentation phase merge success rate percentage')
        self.autonomous_cycles_per_hour = Gauge('longin_ego_autonomous_cycles_per_hour', 'Autonomous cycles per hour')
        self.code_quality_score = Gauge('longin_ego_code_quality_score', 'Code quality score (0-100)')
        self.test_execution_time = Histogram('longin_ego_test_execution_time_seconds', 'Test execution time in seconds')
        self.contract_compliance_rate = Gauge('longin_ego_contract_compliance_rate_percent', 'Contract compliance rate percentage')
    
    async def collect(self) -> ERTDSDMetrics:
        """Shromáždění ERTDSD metrik"""
        try:
            # Stav fází
            meeting_active = await self._is_phase_active("meeting")
            architect_active = await self._is_phase_active("architect")
            grind_active = await self._is_phase_active("grind")
            presentation_active = await self._is_phase_active("presentation")
            
            # Úspěšnosti fází
            meeting_success = await self._get_phase_success_rate("meeting")
            architect_coverage = await self._get_architect_test_coverage()
            grind_success = await self._get_grind_build_success_rate()
            presentation_success = await self._get_presentation_merge_success_rate()
            
            # Autonomní cykly
            cycles_per_hour = await self._get_autonomous_cycles_per_hour()
            
            # Kvalita kódu
            code_quality = await self._get_code_quality_score()
            contract_compliance = await self._get_contract_compliance_rate()
            
            # Čas testů
            test_execution_time = await self._get_test_execution_time()
            
            metrics = ERTDSDMetrics(
                timestamp=datetime.now(),
                meeting_phase_active=meeting_active,
                architect_phase_active=architect_active,
                grind_phase_active=grind_active,
                presentation_phase_active=presentation_active,
                meeting_success_rate=meeting_success,
                architect_test_coverage=architect_coverage,
                grind_build_success_rate=grind_success,
                presentation_merge_success_rate=presentation_success,
                autonomous_cycles_per_hour=cycles_per_hour,
                code_quality_score=code_quality,
                test_execution_time=test_execution_time,
                contract_compliance_rate=contract_compliance
            )
            
            # Aktualizace Prometheus metrik
            self._update_prometheus_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Chyba při sběru ERTDSD metrik: {e}")
            raise MetricsError(f"ERTDSD metriky selhaly: {e}")
    
    async def _is_phase_active(self, phase_name: str) -> bool:
        """Kontrola zda je fáze aktivní"""
        try:
            active = await self.redis_client.get(f"ertdsd:{phase_name}:active") or "0"
            return active == "1"
        except:
            return False
    
    async def _get_phase_success_rate(self, phase_name: str) -> float:
        """Získání úspěšnosti fáze"""
        try:
            success_key = f"ertdsd:{phase_name}:success_count"
            failure_key = f"ertdsd:{phase_name}:failure_count"
            
            success = int(await self.redis_client.get(success_key) or 0)
            failure = int(await self.redis_client.get(failure_key) or 0)
            
            total = success + failure
            if total == 0:
                return 0.0
            
            return (success / total) * 100
        except:
            return 0.0
    
    async def _get_architect_test_coverage(self) -> float:
        """Získání test coverage z architect fáze"""
        try:
            coverage = await self.redis_client.get("ertdsd:architect:test_coverage") or 0
            return float(coverage)
        except:
            return 0.0
    
    async def _get_grind_build_success_rate(self) -> float:
        """Získání build success rate z grind fáze"""
        return await self._get_phase_success_rate("grind")
    
    async def _get_presentation_merge_success_rate(self) -> float:
        """Získání merge success rate z presentation fáze"""
        return await self._get_phase_success_rate("presentation")
    
    async def _get_autonomous_cycles_per_hour(self) -> float:
        """Získání počtu autonomních cyklů za hodinu"""
        try:
            cycles = await self.redis_client.get("ertdsd:autonomous_cycles_per_hour") or 0
            return float(cycles)
        except:
            return 0.0
    
    async def _get_code_quality_score(self) -> float:
        """Získání skóre kvality kódu"""
        try:
            quality = await self.redis_client.get("ertdsd:code_quality_score") or 75.0
            return float(quality)
        except:
            return 75.0
    
    async def _get_test_execution_time(self) -> float:
        """Získání času spuštění testů"""
        try:
            execution_time = await self.redis_client.get("ertdsd:test_execution_time") or 30.0
            return float(execution_time)
        except:
            return 30.0
    
    async def _get_contract_compliance_rate(self) -> float:
        """Získání míry dodržení kontraktů"""
        try:
            compliance = await self.redis_client.get("ertdsd:contract_compliance_rate") or 85.0
            return float(compliance)
        except:
            return 85.0
    
    def _update_prometheus_metrics(self, metrics: ERTDSDMetrics):
        """Aktualizace Prometheus metrik"""
        self.meeting_phase_active.set(1 if metrics.meeting_phase_active else 0)
        self.architect_phase_active.set(1 if metrics.architect_phase_active else 0)
        self.grind_phase_active.set(1 if metrics.grind_phase_active else 0)
        self.presentation_phase_active.set(1 if metrics.presentation_phase_active else 0)
        self.meeting_success_rate.set(metrics.meeting_success_rate)
        self.architect_test_coverage.set(metrics.architect_test_coverage)
        self.grind_build_success_rate.set(metrics.grind_build_success_rate)
        self.presentation_merge_success_rate.set(metrics.presentation_merge_success_rate)
        self.autonomous_cycles_per_hour.set(metrics.autonomous_cycles_per_hour)
        self.code_quality_score.set(metrics.code_quality_score)
        self.contract_compliance_rate.set(metrics.contract_compliance_rate)
    
    def record_test_execution_time(self, duration: float):
        """Zaznamenání času spuštění testů"""
        self.test_execution_time.observe(duration)
    
    def get_metric_names(self) -> List[str]:
        """Získání názvů metrik"""
        return [
            'meeting_phase_active', 'architect_phase_active', 'grind_phase_active',
            'presentation_phase_active', 'meeting_success_rate', 'architect_test_coverage',
            'grind_build_success_rate', 'presentation_merge_success_rate',
            'autonomous_cycles_per_hour', 'code_quality_score', 'test_execution_time',
            'contract_compliance_rate'
        ]

class AdvancedMetricsManager:
    """Hlavní manažer pro pokročilé metriky"""
    
    def __init__(self, config: Config, redis_client: redis.Redis):
        self.config = config
        self.redis_client = redis_client
        
        # Kolektory metrik
        self.system_collector = SystemMetricsCollector()
        self.application_collector = ApplicationMetricsCollector(redis_client)
        self.msca_collector = MSCAMetricsCollector(redis_client)
        self.ertdsd_collector = ERTDSDMetricsCollector(redis_client)
        
        # Historie metrik
        self.metrics_history = {
            'system': deque(maxlen=1000),
            'application': deque(maxlen=1000),
            'msca': deque(maxlen=1000),
            'ertdsd': deque(maxlen=1000)
        }
        
        # Konfigurace sběru
        self.collection_intervals = {
            'system': 5,      # 5 sekund
            'application': 10, # 10 sekund
            'msca': 15,       # 15 sekund
            'ertdsd': 30      # 30 sekund
        }
        
        # Stav sběru
        self.is_collecting = False
        self.collection_tasks = []
        
        # Inicializace Prometheus
        self._init_prometheus()
    
    def _init_prometheus(self):
        """Inicializace Prometheus serveru"""
        try:
            # Spuštění Prometheus HTTP serveru
            prometheus_port = self.config.api.port + 1000  # Offset 1000 od API portu
            start_http_server(prometheus_port)
            logger.info(f"✓ Prometheus metrics server spuštěn na portu {prometheus_port}")
        except Exception as e:
            logger.error(f"Chyba při spouštění Prometheus serveru: {e}")
    
    async def start_collection(self):
        """Spuštění sběru metrik"""
        if self.is_collecting:
            logger.warning("Sběr metrik již běží")
            return
        
        logger.info("Spouštím sběr pokročilých metrik...")
        self.is_collecting = True
        
        # Vytvoření úloh pro sběr
        self.collection_tasks = [
            asyncio.create_task(self._collect_system_metrics()),
            asyncio.create_task(self._collect_application_metrics()),
            asyncio.create_task(self._collect_msca_metrics()),
            asyncio.create_task(self._collect_ertdsd_metrics())
        ]
        
        logger.info("✓ Sběr pokročilých metrik spuštěn")
    
    async def stop_collection(self):
        """Zastavení sběru metrik"""
        if not self.is_collecting:
            return
        
        logger.info("Zastavuji sběr pokročilých metrik...")
        self.is_collecting = False
        
        # Zrušení úloh
        for task in self.collection_tasks:
            task.cancel()
        
        # Počkat na dokončení
        await asyncio.gather(*self.collection_tasks, return_exceptions=True)
        self.collection_tasks.clear()
        
        logger.info("✓ Sběr pokročilých metrik zastaven")
    
    async def _collect_system_metrics(self):
        """Sběr systémových metrik"""
        while self.is_collecting:
            try:
                metrics = await self.system_collector.collect()
                self.metrics_history['system'].append(metrics)
                
                # Uložení do Redis pro rychlý přístup
                await self._store_metrics_to_redis('system', metrics)
                
                await asyncio.sleep(self.collection_intervals['system'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Chyba při sběru systémových metrik: {e}")
                await asyncio.sleep(self.collection_intervals['system'])
    
    async def _collect_application_metrics(self):
        """Sběr aplikačních metrik"""
        while self.is_collecting:
            try:
                metrics = await self.application_collector.collect()
                self.metrics_history['application'].append(metrics)
                
                # Uložení do Redis
                await self._store_metrics_to_redis('application', metrics)
                
                await asyncio.sleep(self.collection_intervals['application'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Chyba při sběru aplikačních metrik: {e}")
                await asyncio.sleep(self.collection_intervals['application'])
    
    async def _collect_msca_metrics(self):
        """Sběr MSCA metrik"""
        while self.is_collecting:
            try:
                metrics = await self.msca_collector.collect()
                self.metrics_history['msca'].append(metrics)
                
                # Uložení do Redis
                await self._store_metrics_to_redis('msca', metrics)
                
                await asyncio.sleep(self.collection_intervals['msca'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Chyba při sběru MSCA metrik: {e}")
                await asyncio.sleep(self.collection_intervals['msca'])
    
    async def _collect_ertdsd_metrics(self):
        """Sběr ERTDSD metrik"""
        while self.is_collecting:
            try:
                metrics = await self.ertdsd_collector.collect()
                self.metrics_history['ertdsd'].append(metrics)
                
                # Uložení do Redis
                await self._store_metrics_to_redis('ertdsd', metrics)
                
                await asyncio.sleep(self.collection_intervals['ertdsd'])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Chyba při sběru ERTDSD metrik: {e}")
                await asyncio.sleep(self.collection_intervals['ertdsd'])
    
    async def _store_metrics_to_redis(self, metrics_type: str, metrics):
        """Uložení metrik do Redis"""
        try:
            key = f"metrics:{metrics_type}:latest"
            value = json.dumps(metrics.__dict__, default=str)
            await self.redis_client.setex(key, 3600, value)  # 1 hodina TTL
        except Exception as e:
            logger.warning(f"Chyba při ukládání metrik do Redis: {e}")
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Získání aktuálních metrik"""
        try:
            system_metrics = await self.system_collector.collect()
            application_metrics = await self.application_collector.collect()
            msca_metrics = await self.msca_collector.collect()
            ertdsd_metrics = await self.ertdsd_collector.collect()
            
            return {
                'system': system_metrics,
                'application': application_metrics,
                'msca': msca_metrics,
                'ertdsd': ertdsd_metrics,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Chyba při získávání aktuálních metrik: {e}")
            raise MetricsError(f"Získání metrik selhalo: {e}")
    
    def get_metrics_history(self, metrics_type: str, limit: int = 100) -> List[Any]:
        """Získání historie metrik"""
        if metrics_type not in self.metrics_history:
            return []
        
        history = list(self.metrics_history[metrics_type])
        return history[-limit:] if limit > 0 else history
    
    def get_all_metric_names(self) -> Dict[str, List[str]]:
        """Získání všech názvů metrik"""
        return {
            'system': self.system_collector.get_metric_names(),
            'application': self.application_collector.get_metric_names(),
            'msca': self.msca_collector.get_metric_names(),
            'ertdsd': self.ertdsd_collector.get_metric_names()
        }
    
    async def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Zaznamenání HTTP požadavku"""
        self.application_collector.record_request(method, endpoint, status_code, duration)
    
    async def record_test_execution_time(self, duration: float):
        """Zaznamenání času spuštění testů"""
        self.ertdsd_collector.record_test_execution_time(duration)

# Singleton instance
_metrics_manager: Optional[AdvancedMetricsManager] = None

async def get_metrics_manager(config: Optional[Config] = None, redis_client: Optional[redis.Redis] = None) -> AdvancedMetricsManager:
    """Získání singleton instance AdvancedMetricsManager"""
    global _metrics_manager
    
    if _metrics_manager is None:
        if config is None:
            from kernel.core.config import get_config
            config = get_config()
        
        if redis_client is None:
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        _metrics_manager = AdvancedMetricsManager(config, redis_client)
    
    return _metrics_manager