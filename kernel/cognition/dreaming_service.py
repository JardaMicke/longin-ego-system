"""
Idle Dreaming Service - Integrační služba pro kognitivní konsolidaci

Poskytuje rozhraní pro integraci Idle Dreaming System s hlavním systémem LONGIN EGO.
Zajišťuje automatické spouštění snovacích relací během nečinnosti a koordinaci s ostatními komponenty.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import redis.asyncio as redis
from kernel.bus.redis_bus import RedisBus
from memory.postgres.client import PostgresClient
from kernel.monitoring.metrics_collector import AdvancedMetricsManager
from kernel.security.auth_manager import AuthManager
from kernel.cognition.idle_dreaming import (
    IdleDreamingOrchestrator,
    IdleDreamingConfig,
    DreamingSession,
    PerformanceInsight,
    OptimizationRecommendation
)


@dataclass
class DreamingServiceStatus:
    """Status služby Idle Dreaming"""
    service_active: bool
    dreaming_active: bool
    last_session: Optional[str]
    last_session_time: Optional[datetime]
    total_sessions: int
    total_insights: int
    total_recommendations: int
    average_comfort_score: float
    next_scheduled_check: datetime


class IdleDreamingService:
    """Hlavní služba pro Idle Dreaming System"""
    
    def __init__(self, config: Dict[str, Any], redis_client: redis.Redis,
                 postgres: PostgresClient, metrics_manager: AdvancedMetricsManager,
                 auth_manager: AuthManager, redis_bus: RedisBus):
        
        # Konfigurace
        self.config = IdleDreamingConfig(**config.get('idle_dreaming', {}))
        
        # Klienti
        self.redis = redis_client
        self.postgres = postgres
        self.metrics = metrics_manager
        self.auth = auth_manager
        self.bus = redis_bus
        
        # Orchestrátor
        self.orchestrator = IdleDreamingOrchestrator(
            self.config, redis_client, postgres, metrics_manager, auth_manager
        )
        
        # Stav služby
        self.service_active = False
        self.check_interval = config.get('check_interval', 60)  # sekundy
        self.max_consecutive_failures = config.get('max_failures', 3)
        self.consecutive_failures = 0
        
        # Monitoring
        self.total_sessions = 0
        self.total_insights = 0
        self.total_recommendations = 0
        self.comfort_scores = []
        
        # Task management
        self.check_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Redis keys
        self.status_key = "service:dreaming:status"
        self.stats_key = "service:dreaming:stats"
        self.last_session_key = "service:dreaming:last_session"
        
        logging.info("Idle Dreaming Service inicializován")
    
    async def start_service(self) -> bool:
        """Spustí službu Idle Dreaming"""
        try:
            if self.service_active:
                logging.warning("Služba již běží")
                return True
            
            logging.info("Spouštím Idle Dreaming Service...")
            
            # Test připojení k databázím
            await self._test_connections()
            
            # Inicializace statistik
            await self._initialize_stats()
            
            # Spuštění hlavní smyčky
            self.service_active = True
            self.check_task = asyncio.create_task(self._dreaming_check_loop())
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Registrace event handlerů
            await self._register_event_handlers()
            
            logging.info("Idle Dreaming Service úspěšně spuštěn")
            return True
            
        except Exception as e:
            logging.error(f"Chyba při spouštění služby: {e}")
            self.service_active = False
            self.consecutive_failures += 1
            return False
    
    async def stop_service(self) -> bool:
        """Zastaví službu Idle Dreaming"""
        try:
            if not self.service_active:
                logging.warning("Služba již zastavena")
                return True
            
            logging.info("Zastavuji Idle Dreaming Service...")
            
            self.service_active = False
            
            # Zastavení tasků
            if self.check_task:
                self.check_task.cancel()
                try:
                    await self.check_task
                except asyncio.CancelledError:
                    pass
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Uložení finálních statistik
            await self._save_final_stats()
            
            logging.info("Idle Dreaming Service zastaven")
            return True
            
        except Exception as e:
            logging.error(f"Chyba při zastavování služby: {e}")
            return False
    
    async def _dreaming_check_loop(self) -> None:
        """Hlavní smyčka pro kontrolu a spouštění snění"""
        while self.service_active:
            try:
                # Kontrola, zda by mělo začít snění
                if await self.orchestrator.should_start_dreaming():
                    logging.info("Podmínky pro snění splněny, zahajuji relaci...")
                    
                    # Zahájení snovací relace
                    session = await self.orchestrator.start_dreaming_session()
                    
                    if session:
                        # Čekání na dokončení relace (maximálně 30 minut)
                        timeout = self.config.max_session_duration_seconds
                        await asyncio.sleep(timeout)
                        
                        # Aktualizace statistik
                        await self._update_session_stats(session)
                        
                        # Reset počítadla chyb
                        self.consecutive_failures = 0
                        
                        logging.info(f"Snovací relace dokončena: {session.session_id}")
                    else:
                        logging.warning("Nepodařilo se zahájit snovací relaci")
                        self.consecutive_failures += 1
                
                # Čekání na další kontrolu
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                logging.info("Kontrolní smyčka zrušena")
                break
            except Exception as e:
                logging.error(f"Chyba v kontrolní smyčce: {e}")
                self.consecutive_failures += 1
                
                # Při příliš mnoha chybách zastavíme službu
                if self.consecutive_failures >= self.max_consecutive_failures:
                    logging.critical("Příliš mnoho po sobě jdoucích chyb, zastavuji službu")
                    self.service_active = False
                    break
                
                await asyncio.sleep(self.check_interval)
    
    async def _monitoring_loop(self) -> None:
        """Monitoringová smyčka pro sběr metrik"""
        while self.service_active:
            try:
                # Sběr metrik každých 30 sekund
                await self._collect_service_metrics()
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                logging.info("Monitoringová smyčka zrušena")
                break
            except Exception as e:
                logging.error(f"Chyba v monitoringové smyčce: {e}")
                await asyncio.sleep(30)
    
    async def _test_connections(self) -> None:
        """Testuje připojení k databázím"""
        try:
            # Test Redis připojení
            await self.redis.ping()
            logging.debug("Redis připojení OK")
            
            # Test PostgreSQL připojení
            await self.postgres.test_connection()
            logging.debug("PostgreSQL připojení OK")
            
        except Exception as e:
            raise RuntimeError(f"Test připojení selhal: {e}")
    
    async def _initialize_stats(self) -> None:
        """Inicializuje statistiky služby"""
        try:
            # Načtení existujících statistik z Redis
            stats_data = await self.redis.get(self.stats_key)
            if stats_data:
                stats = json.loads(stats_data)
                self.total_sessions = stats.get('total_sessions', 0)
                self.total_insights = stats.get('total_insights', 0)
                self.total_recommendations = stats.get('total_recommendations', 0)
                self.comfort_scores = stats.get('comfort_scores', [])
            
            # Načtení poslední relace
            last_session_data = await self.redis.get(self.last_session_key)
            if last_session_data:
                last_session_info = json.loads(last_session_data)
                # Zde bychom načetli detaily poslední relace
            
        except Exception as e:
            logging.warning(f"Chyba při inicializaci statistik: {e}")
    
    async def _update_session_stats(self, session: DreamingSession) -> None:
        """Aktualizuje statistiky po dokončení relace"""
        try:
            self.total_sessions += 1
            self.total_insights += len(session.insights)
            self.total_recommendations += len(session.recommendations)
            
            if session.cognitive_comfort_score > 0:
                self.comfort_scores.append(session.cognitive_comfort_score)
                # Uchováváme pouze posledních 100 skóre
                if len(self.comfort_scores) > 100:
                    self.comfort_scores = self.comfort_scores[-100:]
            
            # Uložení do Redis
            stats_data = {
                'total_sessions': self.total_sessions,
                'total_insights': self.total_insights,
                'total_recommendations': self.total_recommendations,
                'comfort_scores': self.comfort_scores,
                'last_updated': datetime.now().isoformat()
            }
            
            await self.redis.setex(
                self.stats_key,
                86400,  # 24 hodin
                json.dumps(stats_data, default=str)
            )
            
            # Uložení informací o poslední relaci
            last_session_info = {
                'session_id': session.session_id,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'phase': session.phase.value,
                'insights_count': len(session.insights),
                'recommendations_count': len(session.recommendations),
                'comfort_score': session.cognitive_comfort_score
            }
            
            await self.redis.setex(
                self.last_session_key,
                86400,  # 24 hodin
                json.dumps(last_session_info, default=str)
            )
            
        except Exception as e:
            logging.error(f"Chyba při aktualizaci statistik: {e}")
    
    async def _collect_service_metrics(self) -> None:
        """Sbírá metriky služby"""
        try:
            # Základní metriky služby
            service_metrics = {
                'service_active': self.service_active,
                'dreaming_active': self.orchestrator.is_dreaming,
                'consecutive_failures': self.consecutive_failures,
                'total_sessions': self.total_sessions,
                'average_comfort_score': self.get_average_comfort_score()
            }
            
            # Uložení metrik
            await self.redis.setex(
                self.status_key,
                300,  # 5 minut
                json.dumps(service_metrics, default=str)
            )
            
            # Odeslání do metrics collector
            await self.metrics.record_metric(
                'idle_dreaming_service_health',
                1.0 if self.service_active else 0.0,
                {'service': 'idle_dreaming'}
            )
            
        except Exception as e:
            logging.warning(f"Chyba při sběru metrik: {e}")
    
    async def _register_event_handlers(self) -> None:
        """Registruje event handlery pro Redis Bus"""
        try:
            # Registrace handleru pro system events
            await self.bus.subscribe("system.idle", self._handle_system_idle_event)
            await self.bus.subscribe("system.busy", self._handle_system_busy_event)
            await self.bus.subscribe("dreaming.request", self._handle_dreaming_request)
            
        except Exception as e:
            logging.warning(f"Chyba při registraci event handlerů: {e}")
    
    async def _handle_system_idle_event(self, event_data: Dict[str, Any]) -> None:
        """Handler pro system idle event"""
        try:
            logging.info("Přijat system idle event")
            
            # Okamžitá kontrola pro snění
            if await self.orchestrator.should_start_dreaming():
                session = await self.orchestrator.start_dreaming_session()
                if session:
                    logging.info(f"Zahájena snovací relace z idle eventu: {session.session_id}")
                    
                    # Odeslání notifikace
                    await self.bus.publish("dreaming.started", {
                        'session_id': session.session_id,
                        'trigger': 'system_idle'
                    })
            
        except Exception as e:
            logging.error(f"Chyba při zpracování idle eventu: {e}")
    
    async def _handle_system_busy_event(self, event_data: Dict[str, Any]) -> None:
        """Handler pro system busy event"""
        try:
            logging.info("Přijat system busy event")
            
            # Pokud probíhá snění, můžeme zvážit jeho přerušení
            if self.orchestrator.is_dreaming:
                logging.warning("Systém je vytížený, ale snění stále probíhá")
                # V budoucnu můžeme implementovat graceful shutdown snění
            
        except Exception as e:
            logging.error(f"Chyba při zpracování busy eventu: {e}")
    
    async def _handle_dreaming_request(self, event_data: Dict[str, Any]) -> None:
        """Handler pro explicitní požadavek na snění"""
        try:
            logging.info("Přijat dreaming request event")
            
            # Kontrola, zda není systém příliš vytížený
            if not await self.orchestrator.should_start_dreaming():
                logging.warning("Podmínky pro snění nejsou splněny")
                return
            
            # Zahájení snovací relace
            session = await self.orchestrator.start_dreaming_session()
            if session:
                logging.info(f"Zahájena snovací relace z requestu: {session.session_id}")
                
                # Odeslání notifikace
                await self.bus.publish("dreaming.started", {
                    'session_id': session.session_id,
                    'trigger': 'manual_request'
                })
            
        except Exception as e:
            logging.error(f"Chyba při zpracování dreaming requestu: {e}")
    
    async def _save_final_stats(self) -> None:
        """Uloží finální statistiky před vypnutím"""
        try:
            stats_data = {
                'total_sessions': self.total_sessions,
                'total_insights': self.total_insights,
                'total_recommendations': self.total_recommendations,
                'comfort_scores': self.comfort_scores,
                'service_shutdown_time': datetime.now().isoformat()
            }
            
            await self.redis.setex(
                self.stats_key,
                604800,  # 7 dní
                json.dumps(stats_data, default=str)
            )
            
        except Exception as e:
            logging.warning(f"Chyba při ukládání finálních statistik: {e}")
    
    # Veřejné API metody
    
    def get_service_status(self) -> DreamingServiceStatus:
        """Získá status služby"""
        return DreamingServiceStatus(
            service_active=self.service_active,
            dreaming_active=self.orchestrator.is_dreaming,
            last_session=self._get_last_session_id(),
            last_session_time=self._get_last_session_time(),
            total_sessions=self.total_sessions,
            total_insights=self.total_insights,
            total_recommendations=self.total_recommendations,
            average_comfort_score=self.get_average_comfort_score(),
            next_scheduled_check=datetime.now() + timedelta(seconds=self.check_interval)
        )
    
    def get_average_comfort_score(self) -> float:
        """Vypočítá průměrné kognitivní komfortní skóre"""
        if not self.comfort_scores:
            return 0.0
        return sum(self.comfort_scores) / len(self.comfort_scores)
    
    def _get_last_session_id(self) -> Optional[str]:
        """Získá ID poslední relace"""
        # Implementace získání ID poslední relace
        return None
    
    def _get_last_session_time(self) -> Optional[datetime]:
        """Získá čas poslední relace"""
        # Implementace získání času poslední relace
        return None
    
    async def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Získá seznam nedávných snovacích relací"""
        try:
            # Získání z Redis
            pattern = "dreaming:session:*"
            keys = await self.redis.keys(pattern)
            
            sessions = []
            for key in keys[:limit]:
                session_data = await self.redis.get(key)
                if session_data:
                    session_info = json.loads(session_data)
                    sessions.append(session_info)
            
            # Seřazení podle času
            sessions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
            
            return sessions
            
        except Exception as e:
            logging.error(f"Chyba při získávání relací: {e}")
            return []
    
    async def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Získá detaily konkrétní snovací relace"""
        try:
            # Získání z Redis
            session_key = f"dreaming:session:{session_id}"
            session_data = await self.redis.get(session_key)
            
            if session_data:
                return json.loads(session_data)
            
            # Pokud není v Redis, zkus PostgreSQL
            return await self.postgres.get_dreaming_session(session_id)
            
        except Exception as e:
            logging.error(f"Chyba při získávání detailů relace: {e}")
            return None
    
    async def trigger_manual_dreaming(self, reason: str = "manual_request") -> Optional[str]:
        """Manuálně spustí snovací relaci"""
        try:
            if not self.service_active:
                logging.error("Služba není aktivní")
                return None
            
            if self.orchestrator.is_dreaming:
                logging.warning("Snění již probíhá")
                return None
            
            # Odeslání eventu pro manuální spuštění
            await self.bus.publish("dreaming.request", {
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            })
            
            logging.info(f"Manuálně vyžádáno snění: {reason}")
            return "request_sent"
            
        except Exception as e:
            logging.error(f"Chyba při manuálním spuštění snění: {e}")
            return None
    
    async def get_optimization_recommendations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Získá optimalizační doporučení z nedávných relací"""
        try:
            sessions = await self.get_recent_sessions(limit * 2)  # Více relací pro větší šanci
            recommendations = []
            
            for session in sessions:
                session_recommendations = session.get('recommendations', [])
                recommendations.extend(session_recommendations)
            
            # Odstranění duplicit a seřazení podle priority
            unique_recommendations = []
            seen = set()
            
            for rec in recommendations:
                rec_id = f"{rec.get('type', '')}_{rec.get('description', '')}"
                if rec_id not in seen:
                    seen.add(rec_id)
                    unique_recommendations.append(rec)
            
            # Seřazení podle priority
            unique_recommendations.sort(
                key=lambda x: x.get('priority', 5),
                reverse=True
            )
            
            return unique_recommendations[:limit]
            
        except Exception as e:
            logging.error(f"Chyba při získávání doporučení: {e}")
            return []
    
    async def get_performance_insights(self, time_range: str = "24h") -> List[Dict[str, Any]]:
        """Získá poznatky o výkonu z nedávných relací"""
        try:
            # Převod časového rozsahu na počet relací
            time_limits = {
                "1h": 2,
                "6h": 5,
                "24h": 10,
                "7d": 50,
                "30d": 200
            }
            
            limit = time_limits.get(time_range, 10)
            sessions = await self.get_recent_sessions(limit)
            
            insights = []
            for session in sessions:
                session_insights = session.get('insights', [])
                insights.extend(session_insights)
            
            # Seřazení podle závažnosti a času
            insights.sort(key=lambda x: (
                {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x.get('severity', 'low'), 0),
                x.get('timestamp', '')
            ), reverse=True)
            
            return insights
            
        except Exception as e:
            logging.error(f"Chyba při získávání poznatků o výkonu: {e}")
            return []


# Pomocné funkce pro integraci

def create_dreaming_service(config: Dict[str, Any], redis_client: redis.Redis,
                           postgres: PostgresClient, metrics_manager: AdvancedMetricsManager,
                           auth_manager: AuthManager, redis_bus: RedisBus) -> IdleDreamingService:
    """Factory funkce pro vytvoření Idle Dreaming Service"""
    return IdleDreamingService(
        config=config,
        redis_client=redis_client,
        postgres=postgres,
        metrics_manager=metrics_manager,
        auth_manager=auth_manager,
        redis_bus=redis_bus
    )


async def initialize_dreaming_system(config: Dict[str, Any], **dependencies) -> Optional[IdleDreamingService]:
    """Inicializuje Idle Dreaming System s danou konfigurací"""
    try:
        # Vytvoření služby
        service = create_dreaming_service(config, **dependencies)
        
        # Spuštění služby
        success = await service.start_service()
        if success:
            logging.info("Idle Dreaming System úspěšně inicializován")
            return service
        else:
            logging.error("Nepodařilo se spustit Idle Dreaming Service")
            return None
            
    except Exception as e:
        logging.error(f"Chyba při inicializaci Idle Dreaming System: {e}")
        return None


# Export pro použití v dalších modulech
__all__ = [
    'IdleDreamingService',
    'DreamingServiceStatus',
    'create_dreaming_service',
    'initialize_dreaming_system'
]