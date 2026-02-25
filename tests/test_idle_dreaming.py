"""
Testy pro Idle Dreaming System - Kognitivní konsolidace během nečinnosti

Testuje všechny komponenty Idle Dreaming System včetně:
- Cognitive Comfort Calculator
- Performance Analyzer
- Memory Consolidator
- Dreaming Orchestrator
- Dreaming Service
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch

import pytest
import redis.asyncio as redis

# Přidání cesty k projektu
sys.path.append('..')

from kernel.cognition.idle_dreaming import (
    IdleDreamingConfig,
    CognitiveComfortCalculator,
    PerformanceAnalyzer,
    MemoryConsolidator,
    IdleDreamingOrchestrator,
    DreamingSession,
    DreamingPhase,
    CognitiveSubAgent,
    PerformanceInsight,
    OptimizationRecommendation
)
from kernel.cognition.dreaming_service import IdleDreamingService
from kernel.monitoring.metrics_collector import AdvancedMetricsManager
from memory.postgres.client import PostgresClient
from kernel.bus.redis_bus import RedisBus
from kernel.security.auth_manager import AuthManager


# Konfigurace testovacího prostředí
TEST_CONFIG = {
    'idle_dreaming': {
        'enabled': True,
        'min_idle_time_seconds': 60,  # 1 minuta pro testy
        'max_session_duration_seconds': 300,  # 5 minut pro testy
        'cpu_threshold_percent': 50.0,
        'memory_threshold_percent': 60.0,
        'gpu_threshold_percent': 40.0,
        'min_insights_per_session': 2,
        'max_recommendations_per_session': 5,
        'cognitive_comfort_threshold': 0.6,
        'memory_consolidation_interval_hours': 1,
        'performance_baseline_days': 1
    },
    'check_interval': 30  # 30 sekund pro testy
}


class TestIdleDreamingConfig:
    """Testy pro konfiguraci Idle Dreaming"""
    
    def test_config_creation(self):
        """Test vytvoření konfigurace"""
        config = IdleDreamingConfig(**TEST_CONFIG['idle_dreaming'])
        
        assert config.enabled is True
        assert config.min_idle_time_seconds == 60
        assert config.max_session_duration_seconds == 300
        assert config.cpu_threshold_percent == 50.0
        assert config.memory_threshold_percent == 60.0
        assert config.gpu_threshold_percent == 40.0
        assert config.cognitive_comfort_threshold == 0.6
    
    def test_config_validation(self):
        """Test validace konfigurace"""
        # Test s neplatnými hodnotami
        with pytest.raises(ValueError):
            IdleDreamingConfig(
                enabled=True,
                min_idle_time_seconds=-1,  # Záporná hodnota
                max_session_duration_seconds=300,
                cpu_threshold_percent=50.0,
                memory_threshold_percent=60.0,
                gpu_threshold_percent=40.0,
                cognitive_comfort_threshold=0.6
            )
    
    def test_config_defaults(self):
        """Test výchozích hodnot konfigurace"""
        config = IdleDreamingConfig()
        
        assert config.enabled is True
        assert config.min_idle_time_seconds == 300
        assert config.max_session_duration_seconds == 1800
        assert config.cpu_threshold_percent == 20.0
        assert config.memory_threshold_percent == 30.0
        assert config.gpu_threshold_percent == 15.0


class TestCognitiveComfortCalculator:
    """Testy pro Cognitive Comfort Calculator"""
    
    @pytest.fixture
    def mock_metrics_manager(self):
        """Mock pro metrics manager"""
        metrics = Mock(spec=AdvancedMetricsManager)
        
        # Mock pro různé typy metrik
        async def mock_get_metrics(metric_type, start_time, end_time):
            if metric_type == 'response_time':
                return [{'value': 0.5}, {'value': 0.7}, {'value': 0.3}]
            elif metric_type == 'error_rate':
                return [{'value': 0.02}, {'value': 0.01}, {'value': 0.03}]
            elif metric_type == 'memory_usage':
                return [{'value': 0.4}, {'value': 0.5}, {'value': 0.3}]
            elif metric_type == 'gpu_usage':
                return [{'value': 0.2}, {'value': 0.3}, {'value': 0.1}]
            else:
                return []
        
        metrics.get_metrics_by_type = AsyncMock(side_effect=mock_get_metrics)
        return metrics
    
    @pytest.fixture
    def comfort_calculator(self, mock_metrics_manager):
        """Fixture pro comfort calculator"""
        return CognitiveComfortCalculator(mock_metrics_manager)
    
    @pytest.mark.asyncio
    async def test_calculate_comfort_score_basic(self, comfort_calculator, mock_metrics_manager):
        """Test základního výpočtu komfortního skóre"""
        score = await comfort_calculator.calculate_comfort_score()
        
        # Skóre by mělo být mezi 0 a 1
        assert 0.0 <= score <= 1.0
        
        # S dobrými metrikami by mělo být skóre relativně vysoké
        assert score > 0.5
    
    @pytest.mark.asyncio
    async def test_calculate_comfort_score_with_bad_metrics(self, comfort_calculator, mock_metrics_manager):
        """Test výpočtu s špatnými metrikami"""
        # Mock špatných metrik
        async def mock_bad_metrics(metric_type, start_time, end_time):
            if metric_type == 'response_time':
                return [{'value': 10.0}, {'value': 15.0}]  # Velmi vysoké doby odezvy
            elif metric_type == 'error_rate':
                return [{'value': 0.5}, {'value': 0.8}]  # Vysoká chybovost
            elif metric_type == 'memory_usage':
                return [{'value': 0.9}, {'value': 0.95}]  # Vysoké využití paměti
            elif metric_type == 'gpu_usage':
                return [{'value': 0.9}, {'value': 1.0}]  # Vysoké využití GPU
            else:
                return []
        
        mock_metrics_manager.get_metrics_by_type = AsyncMock(side_effect=mock_bad_metrics)
        
        score = await comfort_calculator.calculate_comfort_score()
        
        # S špatnými metrikami by mělo být skóre nízké
        assert 0.0 <= score < 0.5
    
    @pytest.mark.asyncio
    async def test_calculate_comfort_score_exception_handling(self, comfort_calculator, mock_metrics_manager):
        """Test handling výjimek při výpočtu"""
        # Mock výjimky
        mock_metrics_manager.get_metrics_by_type = AsyncMock(side_effect=Exception("Test exception"))
        
        score = await comfort_calculator.calculate_comfort_score()
        
        # Při chybě by mělo být střední skóre
        assert score == 0.5
    
    @pytest.mark.asyncio
    async def test_model_quality_comfort(self, comfort_calculator):
        """Test výpočtu kvality modelů"""
        # Test základní implementace (placeholder)
        score = await comfort_calculator._calculate_model_quality_comfort()
        
        assert 0.0 <= score <= 1.0


class TestPerformanceAnalyzer:
    """Testy pro Performance Analyzer"""
    
    @pytest.fixture
    def mock_metrics_manager(self):
        """Mock pro metrics manager"""
        metrics = Mock(spec=AdvancedMetricsManager)
        
        async def mock_get_metrics(metric_type, start_time, end_time):
            # Simulace různých metrik podle typu
            if metric_type == 'response_time':
                return [
                    {'value': 0.5, 'timestamp': datetime.now()},
                    {'value': 0.7, 'timestamp': datetime.now()},
                    {'value': 0.3, 'timestamp': datetime.now()}
                ]
            elif metric_type == 'error_rate':
                return [
                    {'value': 0.02, 'timestamp': datetime.now()},
                    {'value': 0.01, 'timestamp': datetime.now()}
                ]
            elif metric_type == 'memory_usage':
                return [
                    {'value': 0.4, 'timestamp': datetime.now()},
                    {'value': 0.5, 'timestamp': datetime.now()}
                ]
            elif metric_type == 'gpu_usage':
                return [
                    {'value': 0.2, 'timestamp': datetime.now()},
                    {'value': 0.3, 'timestamp': datetime.now()}
                ]
            elif metric_type == 'throughput':
                return [
                    {'value': 100, 'timestamp': datetime.now()},
                    {'value': 120, 'timestamp': datetime.now()}
                ]
            else:
                return []
        
        metrics.get_metrics_by_type = AsyncMock(side_effect=mock_get_metrics)
        return metrics
    
    @pytest.fixture
    def mock_postgres(self):
        """Mock pro postgres client"""
        postgres = Mock(spec=PostgresClient)
        return postgres
    
    @pytest.fixture
    def performance_analyzer(self, mock_metrics_manager, mock_postgres):
        """Fixture pro performance analyzer"""
        return PerformanceAnalyzer(mock_metrics_manager, mock_postgres)
    
    @pytest.mark.asyncio
    async def test_analyze_performance_basic(self, performance_analyzer):
        """Test základní analýzy výkonu"""
        insights = await performance_analyzer.analyze_performance()
        
        # Měli bychom dostat nějaké poznatky
        assert isinstance(insights, list)
        
        # Zkontrolovat strukturu poznatků
        for insight in insights:
            assert isinstance(insight, PerformanceInsight)
            assert insight.category in ['performance', 'reliability', 'resources']
            assert insight.severity in ['low', 'medium', 'high', 'critical']
            assert isinstance(insight.current_value, float)
            assert isinstance(insight.baseline_value, float)
            assert isinstance(insight.deviation, float)
            assert len(insight.recommendation) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_performance_no_data(self, performance_analyzer, mock_metrics_manager):
        """Test analýzy bez dat"""
        # Mock prázdných dat
        mock_metrics_manager.get_metrics_by_type = AsyncMock(return_value=[])
        
        insights = await performance_analyzer.analyze_performance()
        
        # Bez dat bychom měli dostat prázdný seznam
        assert insights == []
    
    @pytest.mark.asyncio
    async def test_response_time_analysis(self, performance_analyzer):
        """Test analýzy doby odezvy"""
        # Test s vysokými dobami odezvy
        insights = await performance_analyzer.analyze_performance()
        
        # Najdeme poznatek o response time
        response_insights = [i for i in insights if i.metric == 'response_time']
        
        # Pokud jsou doby odezvy signifikantně odlišné, měli bychom dostat poznatek
        if response_insights:
            assert response_insights[0].severity in ['medium', 'high']
            assert 'optimalizaci' in response_insights[0].recommendation.lower()
    
    @pytest.mark.asyncio
    async def test_error_rate_analysis(self, performance_analyzer):
        """Test analýzy chybovosti"""
        insights = await performance_analyzer.analyze_performance()
        
        # Najdeme poznatek o error rate
        error_insights = [i for i in insights if i.metric == 'error_rate']
        
        # S nízkou chybovostí by neměl být kritický poznatek
        for insight in error_insights:
            assert insight.severity != 'critical'


class TestMemoryConsolidator:
    """Testy pro Memory Consolidator"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock pro Redis"""
        redis_mock = Mock(spec=redis.Redis)
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.set = AsyncMock()
        redis_mock.delete = AsyncMock()
        return redis_mock
    
    @pytest.fixture
    def mock_postgres(self):
        """Mock pro Postgres"""
        postgres = Mock(spec=PostgresClient)
        postgres.get_episodic_memories = AsyncMock(return_value=[])
        postgres.store_consolidated_memory = AsyncMock()
        return postgres
    
    @pytest.fixture
    def memory_consolidator(self, mock_redis, mock_postgres):
        """Fixture pro memory consolidator"""
        return MemoryConsolidator(mock_redis, mock_postgres)
    
    @pytest.fixture
    def sample_session(self):
        """Ukázková dreaming session"""
        return DreamingSession(
            session_id="test_session_123",
            start_time=datetime.now(),
            phase=DreamingPhase.ANALYSIS,
            sub_agents={CognitiveSubAgent.ANALYZER}
        )
    
    @pytest.mark.asyncio
    async def test_consolidate_memory_basic(self, memory_consolidator, sample_session):
        """Test základní konsolidace paměti"""
        consolidations = await memory_consolidator.consolidate_memory(sample_session)
        
        # Měli bychom dostat seznam konsolidací
        assert isinstance(consolidations, list)
        
        # Zkontrolovat strukturu konsolidací
        for consolidation in consolidations:
            assert 'type' in consolidation
            assert 'timestamp' in consolidation
    
    @pytest.mark.asyncio
    async def test_consolidate_memory_exception_handling(self, memory_consolidator, sample_session):
        """Test handling výjimek při konsolidaci"""
        # Mock výjimky
        memory_consolidator._consolidate_episodic_memory = AsyncMock(side_effect=Exception("Test exception"))
        
        consolidations = await memory_consolidator.consolidate_memory(sample_session)
        
        # Při chybě bychom měli dostat prázdný seznam nebo částečné výsledky
        assert isinstance(consolidations, list)
    
    @pytest.mark.asyncio
    async def test_space_estimation(self, memory_consolidator):
        """Test odhadu ušetřeného místa"""
        original = [{"data": "x" * 1000}] * 10  # Velké objemy dat
        consolidated = [{"summary": "x" * 100}] * 2  # Konsolidované
        
        space_saved = memory_consolidator._estimate_space_saved(original, consolidated)
        
        # Měli bychom dostat procento úspory
        assert "%" in space_saved
        assert float(space_saved.replace("%", "")) > 0


class TestIdleDreamingOrchestrator:
    """Testy pro Idle Dreaming Orchestrator"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock pro všechny dependencies"""
        config = IdleDreamingConfig(**TEST_CONFIG['idle_dreaming'])
        
        # Mock Redis
        redis_mock = Mock(spec=redis.Redis)
        redis_mock.ping = AsyncMock()
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.set = AsyncMock()
        redis_mock.keys = AsyncMock(return_value=[])
        
        # Mock Postgres
        postgres_mock = Mock(spec=PostgresClient)
        postgres_mock.test_connection = AsyncMock()
        postgres_mock.insert_dreaming_session = AsyncMock()
        
        # Mock Metrics Manager
        metrics_mock = Mock(spec=AdvancedMetricsManager)
        metrics_mock.get_metrics_by_type = AsyncMock(return_value=[])
        
        # Mock Auth Manager
        auth_mock = Mock(spec=AuthManager)
        
        return {
            'config': config,
            'redis': redis_mock,
            'postgres': postgres_mock,
            'metrics': metrics_mock,
            'auth': auth_mock
        }
    
    @pytest.fixture
    def orchestrator(self, mock_dependencies):
        """Fixture pro orchestrator"""
        return IdleDreamingOrchestrator(
            mock_dependencies['config'],
            mock_dependencies['redis'],
            mock_dependencies['postgres'],
            mock_dependencies['metrics'],
            mock_dependencies['auth']
        )
    
    @pytest.mark.asyncio
    async def test_should_start_dreaming_basic(self, orchestrator):
        """Test základní kontroly podmínek pro snění"""
        # Mock nízkého vytížení systému
        orchestrator._get_cpu_usage = AsyncMock(return_value=10.0)
        orchestrator._get_memory_usage = AsyncMock(return_value=20.0)
        orchestrator._get_gpu_usage = AsyncMock(return_value=10.0)
        orchestrator._get_active_user_count = AsyncMock(return_value=0)
        
        should_start = await orchestrator.should_start_dreaming()
        
        # Při nízkém vytížení by mělo být snění povoleno
        assert should_start is True
    
    @pytest.mark.asyncio
    async def test_should_start_dreaming_high_cpu(self, orchestrator):
        """Test kontroly při vysokém CPU vytížení"""
        # Mock vysokého CPU vytížení
        orchestrator._get_cpu_usage = AsyncMock(return_value=80.0)
        orchestrator._get_memory_usage = AsyncMock(return_value=20.0)
        orchestrator._get_gpu_usage = AsyncMock(return_value=10.0)
        orchestrator._get_active_user_count = AsyncMock(return_value=0)
        
        should_start = await orchestrator.should_start_dreaming()
        
        # Při vysokém vytížení by mělo být snění zakázáno
        assert should_start is False
    
    @pytest.mark.asyncio
    async def test_start_dreaming_session(self, orchestrator):
        """Test zahájení snovací relace"""
        # Mock podmínek pro snění
        orchestrator.should_start_dreaming = AsyncMock(return_value=True)
        
        session = await orchestrator.start_dreaming_session()
        
        # Měli bychom dostat session objekt
        assert isinstance(session, DreamingSession)
        assert session.session_id.startswith("dream_")
        assert session.phase == DreamingPhase.ANALYSIS
        assert len(session.sub_agents) > 0
        
        # Orchestrator by měl být v režimu snění
        assert orchestrator.is_dreaming is True
        assert orchestrator.current_session is not None
    
    @pytest.mark.asyncio
    async def test_cognitive_agents(self, orchestrator):
        """Test kognitivních agentů"""
        # Test kritického agenta
        sample_insights = [
            PerformanceInsight(
                category="performance",
                metric="response_time",
                current_value=5.0,
                baseline_value=1.0,
                deviation=400.0,
                severity="critical",
                recommendation="Okamžitě optimalizujte"
            )
        ]
        
        critic_insights = await orchestrator._critic_agent(sample_insights)
        
        assert isinstance(critic_insights, list)
        assert len(critic_insights) > 0
        assert critic_insights[0]['agent'] == 'critic'
        assert 'critical' in critic_insights[0]['type']
    
    @pytest.mark.asyncio
    async def test_dreaming_status(self, orchestrator):
        """Test získání statusu snění"""
        status = orchestrator.get_dreaming_status()
        
        assert isinstance(status, dict)
        assert 'is_dreaming' in status
        assert 'current_session' in status
        assert 'config' in status
        assert status['is_dreaming'] is False  # Na začátku není aktivní snění


class TestIdleDreamingService:
    """Testy pro Idle Dreaming Service"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock pro všechny dependencies service"""
        # Mock Redis
        redis_mock = Mock(spec=redis.Redis)
        redis_mock.ping = AsyncMock()
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.set = AsyncMock()
        redis_mock.setex = AsyncMock()
        redis_mock.keys = AsyncMock(return_value=[])
        
        # Mock Postgres
        postgres_mock = Mock(spec=PostgresClient)
        postgres_mock.test_connection = AsyncMock()
        postgres_mock.get_dreaming_session = AsyncMock(return_value=None)
        
        # Mock Metrics Manager
        metrics_mock = Mock(spec=AdvancedMetricsManager)
        metrics_mock.record_metric = AsyncMock()
        
        # Mock Auth Manager
        auth_mock = Mock(spec=AuthManager)
        
        # Mock Redis Bus
        bus_mock = Mock(spec=RedisBus)
        bus_mock.subscribe = AsyncMock()
        bus_mock.publish = AsyncMock()
        
        return {
            'redis': redis_mock,
            'postgres': postgres_mock,
            'metrics': metrics_mock,
            'auth': auth_mock,
            'bus': bus_mock
        }
    
    @pytest.fixture
    def dreaming_service(self, mock_dependencies):
        """Fixture pro dreaming service"""
        return IdleDreamingService(
            config=TEST_CONFIG,
            redis_client=mock_dependencies['redis'],
            postgres=mock_dependencies['postgres'],
            metrics_manager=mock_dependencies['metrics'],
            auth_manager=mock_dependencies['auth'],
            redis_bus=mock_dependencies['bus']
        )
    
    @pytest.mark.asyncio
    async def test_service_start_stop(self, dreaming_service):
        """Test spuštění a zastavení služby"""
        # Spuštění služby
        success = await dreaming_service.start_service()
        assert success is True
        assert dreaming_service.service_active is True
        
        # Zastavení služby
        success = await dreaming_service.stop_service()
        assert success is True
        assert dreaming_service.service_active is False
    
    @pytest.mark.asyncio
    async def test_service_status(self, dreaming_service):
        """Test získání statusu služby"""
        await dreaming_service.start_service()
        
        status = dreaming_service.get_service_status()
        
        assert status.service_active is True
        assert status.dreaming_active is False
        assert status.total_sessions == 0
        assert status.average_comfort_score == 0.0
        assert status.next_scheduled_check is not None
    
    @pytest.mark.asyncio
    async def test_get_recent_sessions(self, dreaming_service):
        """Test získání nedávných relací"""
        sessions = await dreaming_service.get_recent_sessions(limit=5)
        
        assert isinstance(sessions, list)
        # Na začátku by měl být prázdný seznam
        assert len(sessions) == 0
    
    @pytest.mark.asyncio
    async def test_get_optimization_recommendations(self, dreaming_service):
        """Test získání optimalizačních doporučení"""
        recommendations = await dreaming_service.get_optimization_recommendations(limit=5)
        
        assert isinstance(recommendations, list)
        # Na začátku by měl být prázdný seznam
        assert len(recommendations) == 0
    
    @pytest.mark.asyncio
    async def test_get_performance_insights(self, dreaming_service):
        """Test získání poznatků o výkonu"""
        insights = await dreaming_service.get_performance_insights(time_range="24h")
        
        assert isinstance(insights, list)
        # Na začátku by měl být prázdný seznam
        assert len(insights) == 0
    
    @pytest.mark.asyncio
    async def test_trigger_manual_dreaming_service_not_active(self, dreaming_service):
        """Test manuálního spuštění snění když služba není aktivní"""
        result = await dreaming_service.trigger_manual_dreaming("test_reason")
        
        # Když služba není aktivní, mělo by to selhat
        assert result is None
    
    @pytest.mark.asyncio
    async def test_average_comfort_score(self, dreaming_service):
        """Test výpočtu průměrného komfortního skóre"""
        # Bez skóre by měl být výsledek 0.0
        assert dreaming_service.get_average_comfort_score() == 0.0
        
        # Přidání několika skóre
        dreaming_service.comfort_scores = [0.7, 0.8, 0.9]
        
        average = dreaming_service.get_average_comfort_score()
        assert average == 0.8


class TestIntegration:
    """Integrační testy pro Idle Dreaming System"""
    
    @pytest.mark.asyncio
    async def test_full_dreaming_cycle(self):
        """Test kompletního cyklu snění"""
        # Vytvoření reálných mock dependencies
        config = IdleDreamingConfig(**TEST_CONFIG['idle_dreaming'])
        
        # Redis mock
        redis_mock = Mock(spec=redis.Redis)
        redis_mock.ping = AsyncMock()
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.set = AsyncMock()
        redis_mock.setex = AsyncMock()
        redis_mock.keys = AsyncMock(return_value=[])
        
        # Postgres mock
        postgres_mock = Mock(spec=PostgresClient)
        postgres_mock.test_connection = AsyncMock()
        postgres_mock.insert_dreaming_session = AsyncMock()
        postgres_mock.get_dreaming_session = AsyncMock(return_value=None)
        
        # Metrics mock
        metrics_mock = Mock(spec=AdvancedMetricsManager)
        metrics_mock.get_metrics_by_type = AsyncMock(return_value=[])
        metrics_mock.record_metric = AsyncMock()
        
        # Auth mock
        auth_mock = Mock(spec=AuthManager)
        
        # Bus mock
        bus_mock = Mock(spec=RedisBus)
        bus_mock.subscribe = AsyncMock()
        bus_mock.publish = AsyncMock()
        
        # Vytvoření service
        service = IdleDreamingService(
            config=TEST_CONFIG,
            redis_client=redis_mock,
            postgres=postgres_mock,
            metrics_manager=metrics_mock,
            auth_manager=auth_mock,
            redis_bus=bus_mock
        )
        
        # Spuštění služby
        success = await service.start_service()
        assert success is True
        
        # Test statusu
        status = service.get_service_status()
        assert status.service_active is True
        
        # Zastavení služby
        success = await service.stop_service()
        assert success is True
    
    @pytest.mark.asyncio
    async def test_service_with_mock_metrics(self):
        """Test služby s mock metrikami"""
        # Vytvoření metrics manageru s mock daty
        metrics_mock = Mock(spec=AdvancedMetricsManager)
        
        # Simulace různých metrik
        async def mock_get_metrics(metric_type, start_time, end_time):
            if metric_type == 'response_time':
                return [{'value': 0.5}, {'value': 0.7}]
            elif metric_type == 'error_rate':
                return [{'value': 0.01}, {'value': 0.02}]
            elif metric_type == 'memory_usage':
                return [{'value': 0.3}, {'value': 0.4}]
            elif metric_type == 'gpu_usage':
                return [{'value': 0.1}, {'value': 0.2}]
            else:
                return []
        
        metrics_mock.get_metrics_by_type = AsyncMock(side_effect=mock_get_metrics)
        metrics_mock.record_metric = AsyncMock()
        
        # Test comfort calculatoru s reálnými metrikami
        comfort_calc = CognitiveComfortCalculator(metrics_mock)
        score = await comfort_calc.calculate_comfort_score()
        
        assert 0.0 <= score <= 1.0
        
        # Test performance analyzeru
        postgres_mock = Mock(spec=PostgresClient)
        performance_analyzer = PerformanceAnalyzer(metrics_mock, postgres_mock)
        
        insights = await performance_analyzer.analyze_performance()
        
        assert isinstance(insights, list)


# Pomocné funkce pro testování

def run_basic_tests():
    """Spustí základní testy bez pytest framework"""
    print("=== Spouštím základní testy Idle Dreaming System ===")
    
    # Test konfigurace
    print("\n1. Test konfigurace...")
    try:
        config = IdleDreamingConfig(**TEST_CONFIG['idle_dreaming'])
        print("✓ Konfigurace vytvořena úspěšně")
        print(f"  - Min idle time: {config.min_idle_time_seconds}s")
        print(f"  - Max session duration: {config.max_session_duration_seconds}s")
        print(f"  - CPU threshold: {config.cpu_threshold_percent}%")
    except Exception as e:
        print(f"✗ Chyba při vytváření konfigurace: {e}")
        return False
    
    # Test dreaming fází
    print("\n2. Test dreaming fází...")
    try:
        phases = [DreamingPhase.ANALYSIS, DreamingPhase.REFLECTION, DreamingPhase.PLANNING]
        for phase in phases:
            print(f"✓ Fáze {phase.value} je platná")
    except Exception as e:
        print(f"✗ Chyba při testování fází: {e}")
        return False
    
    # Test kognitivních agentů
    print("\n3. Test kognitivních agentů...")
    try:
        agents = [CognitiveSubAgent.CRITIC, CognitiveSubAgent.PLANNER, CognitiveSubAgent.CODER]
        for agent in agents:
            print(f"✓ Agent {agent.value} je platný")
    except Exception as e:
        print(f"✗ Chyba při testování agentů: {e}")
        return False
    
    # Test session
    print("\n4. Test dreaming session...")
    try:
        session = DreamingSession(
            session_id="test_123",
            start_time=datetime.now(),
            phase=DreamingPhase.ANALYSIS,
            sub_agents={CognitiveSubAgent.ANALYZER}
        )
        print(f"✓ Session vytvořena: {session.session_id}")
        print(f"  - Fáze: {session.phase.value}")
        print(f"  - Agenti: {len(session.sub_agents)}")
    except Exception as e:
        print(f"✗ Chyba při vytváření session: {e}")
        return False
    
    print("\n=== Základní testy dokončeny úspěšně ===")
    return True


if __name__ == "__main__":
    # Spuštění základních testů
    success = run_basic_tests()
    
    if success:
        print("\n✓ Všechny základní testy prošly!")
        print("Pro spuštění plných testů použijte: pytest test_idle_dreaming.py -v")
    else:
        print("\n✗ Některé základní testy selhaly!")
        sys.exit(1)