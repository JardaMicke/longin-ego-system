"""
Idle Dreaming System - Kognitivní konsolidace během nečinnosti

Tento modul implementuje systém kognitivní konsolidace, který pracuje během 
nečinnosti LONGIN EGO systému. Provádí analýzu zkušeností, konsolidaci paměti,
generování nových poznatků a optimalizaci rozhodovacích procesů.

Autor: LONGIN EGO System
Verze: 1.0.0
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import numpy as np
from collections import defaultdict, deque
import threading
from queue import Queue, Empty
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
import psutil

# Konfigurace loggingu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metriky
DREAMING_CYCLES = Counter('dreaming_cycles_total', 'Total dreaming cycles', ['phase', 'status'])
DREAMING_DURATION = Histogram('dreaming_duration_seconds', 'Duration of dreaming cycles', ['phase'])
DREAMING_MEMORY_USAGE = Gauge('dreaming_memory_usage_bytes', 'Memory usage during dreaming')
DREAMING_INSIGHTS = Counter('dreaming_insights_total', 'Total insights generated', ['type'])
DREAMING_CONSOLIDATION_RATE = Gauge('dreaming_consolidation_rate', 'Rate of memory consolidation')

@dataclass
class ExperienceRecord:
    """Záznam o zkušenosti pro konsolidaci"""
    experience_id: str
    timestamp: datetime
    experience_type: str  # 'success', 'failure', 'neutral', 'learning'
    context: Dict[str, Any]
    emotional_weight: float  # 0.0 - 1.0
    importance_score: float  # 0.0 - 1.0
    tags: Set[str]
    related_patterns: List[str]
    outcome: Optional[str] = None
    lessons_learned: List[str] = None
    
    def __post_init__(self):
        if self.lessons_learned is None:
            self.lessons_learned = []

@dataclass
class ConsolidatedMemory:
    """Konsolidovaná paměť"""
    memory_id: str
    consolidation_timestamp: datetime
    experience_type: str
    summary: str
    key_insights: List[str]
    pattern_weights: Dict[str, float]
    emotional_signature: float
    confidence_score: float
    related_memories: List[str]
    applicability_score: float  # Jak dobře se dá použít v budoucnu
    
@dataclass
class DreamingInsight:
    """Poznatek vygenerovaný během snění"""
    insight_id: str
    generation_timestamp: datetime
    insight_type: str  # 'pattern', 'optimization', 'prediction', 'synthesis'
    content: str
    confidence: float
    evidence: List[str]
    applicability_context: Dict[str, Any]
    priority_score: float
    
class MemoryConsolidator:
    """Konsolidace paměťových záznamů"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.consolidation_threshold = config.get('consolidation_threshold', 0.7)
        self.pattern_similarity_threshold = config.get('pattern_similarity_threshold', 0.8)
        self.emotional_decay_factor = config.get('emotional_decay_factor', 0.95)
        
    def consolidate_experiences(self, experiences: List[ExperienceRecord]) -> List[ConsolidatedMemory]:
        """Konsolidace seznamu zkušeností"""
        try:
            if not experiences:
                return []
            
            # Skupinování podle typu a kontextu
            grouped_experiences = self._group_similar_experiences(experiences)
            
            consolidated_memories = []
            
            for group_key, group_experiences in grouped_experiences.items():
                if len(group_experiences) >= self.config.get('min_group_size', 3):
                    consolidated = self._consolidate_group(group_experiences, group_key)
                    if consolidated:
                        consolidated_memories.append(consolidated)
            
            logger.info(f"Konsolidováno {len(consolidated_memories)} pamětí z {len(experiences)} zkušeností")
            return consolidated_memories
            
        except Exception as e:
            logger.error(f"Chyba při konsolidaci paměti: {e}")
            return []
    
    def _group_similar_experiences(self, experiences: List[ExperienceRecord]) -> Dict[str, List[ExperienceRecord]]:
        """Seskupení podobných zkušeností"""
        groups = defaultdict(list)
        
        for experience in experiences:
            # Vytvoření klíče pro seskupení
            context_key = self._create_context_key(experience)
            groups[context_key].append(experience)
        
        return groups
    
    def _create_context_key(self, experience: ExperienceRecord) -> str:
        """Vytvoření klíče pro seskupení zkušeností"""
        # Zjednodušená verze - v reálné implementaci by používala sofistikovanější porovnání
        context_parts = []
        
        # Přidání typu zkušenosti
        context_parts.append(f"type:{experience.experience_type}")
        
        # Přidání hlavních tagů (prvních 3)
        main_tags = sorted(list(experience.tags))[:3]
        context_parts.append(f"tags:{','.join(main_tags)}")
        
        # Přidání kontextových klíčů
        if 'module_type' in experience.context:
            context_parts.append(f"module:{experience.context['module_type']}")
        
        if 'operation' in experience.context:
            context_parts.append(f"op:{experience.context['operation']}")
        
        return "|".join(context_parts)
    
    def _consolidate_group(self, experiences: List[ExperienceRecord], group_key: str) -> Optional[ConsolidatedMemory]:
        """Konsolidace skupiny podobných zkušeností"""
        try:
            if not experiences:
                return None
            
            # Výpočet agregovaných metrik
            avg_emotional_weight = np.mean([exp.emotional_weight for exp in experiences])
            avg_importance = np.mean([exp.importance_score for exp in experiences])
            
            # Identifikace společných vzorců
            common_patterns = self._find_common_patterns(experiences)
            
            # Generování souhrnu
            summary = self._generate_group_summary(experiences)
            
            # Extrakce klíčových poznatků
            key_insights = self._extract_key_insights(experiences)
            
            # Výpočet váhy vzorců
            pattern_weights = self._calculate_pattern_weights(experiences, common_patterns)
            
            # Výpočet celkové důvěry
            confidence = self._calculate_consolidation_confidence(experiences)
            
            # Výpočet aplikovatelnosti
            applicability = self._calculate_applicability_score(experiences)
            
            consolidated = ConsolidatedMemory(
                memory_id=f"consolidated_{int(time.time())}_{hash(group_key) % 10000}",
                consolidation_timestamp=datetime.now(),
                experience_type=experiences[0].experience_type,
                summary=summary,
                key_insights=key_insights,
                pattern_weights=pattern_weights,
                emotional_signature=avg_emotional_weight,
                confidence_score=confidence,
                related_memories=[],  # Bude naplněno později
                applicability_score=applicability
            )
            
            return consolidated
            
        except Exception as e:
            logger.error(f"Chyba při konsolidaci skupiny {group_key}: {e}")
            return None
    
    def _find_common_patterns(self, experiences: List[ExperienceRecord]) -> List[str]:
        """Nalezení společných vzorců v zkušenostech"""
        pattern_counter = defaultdict(int)
        
        for exp in experiences:
            for pattern in exp.related_patterns:
                pattern_counter[pattern] += 1
        
        # Vrácení vzorců, které se objevily alespoň v polovině zkušeností
        min_occurrences = max(1, len(experiences) // 2)
        common_patterns = [
            pattern for pattern, count in pattern_counter.items()
            if count >= min_occurrences
        ]
        
        return common_patterns
    
    def _generate_group_summary(self, experiences: List[ExperienceRecord]) -> str:
        """Generování souhrnu skupiny zkušeností"""
        exp_type = experiences[0].experience_type
        count = len(experiences)
        
        if exp_type == 'success':
            return f"Opakovaný úspěch v {count} případech se společnými charakteristikami"
        elif exp_type == 'failure':
            return f"Opakované selhání v {count} případech vyžadující pozornost"
        elif exp_type == 'learning':
            return f"Učební proces z {count} iterací s pozitivním trendem"
        else:
            return f"Konsolidovaná zkušenost z {count} případů"
    
    def _extract_key_insights(self, experiences: List[ExperienceRecord]) -> List[str]:
        """Extrakce klíčových poznatků ze zkušeností"""
        insights = []
        
        # Analýza výsledků
        outcomes = [exp.outcome for exp in experiences if exp.outcome]
        if outcomes:
            success_rate = outcomes.count('success') / len(outcomes)
            if success_rate > 0.8:
                insights.append("Vysoká míra úspěšnosti indikuje efektivní přístup")
            elif success_rate < 0.3:
                insights.append("Nízká úspěšnost vyžaduje změnu strategie")
        
        # Analýza lekcí
        all_lessons = []
        for exp in experiences:
            if exp.lessons_learned:
                all_lessons.extend(exp.lessons_learned)
        
        if all_lessons:
            # Četnost lekcí
            lesson_frequency = defaultdict(int)
            for lesson in all_lessons:
                lesson_frequency[lesson] += 1
            
            # Přidání nejčastějších lekcí
            most_common_lessons = sorted(
                lesson_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            for lesson, freq in most_common_lessons:
                if freq >= len(experiences) // 2:
                    insights.append(f"Opakovaná lekce: {lesson}")
        
        return insights
    
    def _calculate_pattern_weights(self, experiences: List[ExperienceRecord], patterns: List[str]) -> Dict[str, float]:
        """Výpočet vah vzorců"""
        weights = {}
        
        for pattern in patterns:
            # Výpočet váhy na základě frekvence a důležitosti
            total_weight = 0
            total_importance = 0
            
            for exp in experiences:
                if pattern in exp.related_patterns:
                    # Váha na základě důležitosti a emoční váhy
                    weight = exp.importance_score * (0.5 + exp.emotional_weight)
                    total_weight += weight
                    total_importance += exp.importance_score
            
            if total_importance > 0:
                weights[pattern] = total_weight / total_importance
            else:
                weights[pattern] = 0.5
        
        return weights
    
    def _calculate_consolidation_confidence(self, experiences: List[ExperienceRecord]) -> float:
        """Výpočet důvěry v konsolidaci"""
        if not experiences:
            return 0.0
        
        # Faktory ovlivňující důvěru
        sample_size_factor = min(1.0, len(experiences) / 10)  # Více zkušeností = vyšší důvěra
        consistency_factor = 1.0 - np.std([exp.importance_score for exp in experiences])  # Konzistence důležitosti
        recency_factor = self._calculate_recency_factor(experiences)
        
        # Vážený průměr faktorů
        confidence = (
            0.4 * sample_size_factor +
            0.3 * consistency_factor +
            0.3 * recency_factor
        )
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_recency_factor(self, experiences: List[ExperienceRecord]) -> float:
        """Výpočet faktoru aktuálnosti"""
        if not experiences:
            return 0.0
        
        now = datetime.now()
        max_age = timedelta(days=30)  # Maximální věk pro plnou váhu
        
        total_weight = 0
        for exp in experiences:
            age = now - exp.timestamp
            if age <= max_age:
                # Exponenciální pokles váhy s věkem
                weight = np.exp(-age.total_seconds() / max_age.total_seconds())
                total_weight += weight
            else:
                total_weight += 0.1  # Minimální váha pro staré zkušenosti
        
        return total_weight / len(experiences)
    
    def _calculate_applicability_score(self, experiences: List[ExperienceRecord]) -> float:
        """Výpočet skóre aplikovatelnosti"""
        if not experiences:
            return 0.0
        
        # Průměrná důležitost a emoční váha
        avg_importance = np.mean([exp.importance_score for exp in experiences])
        avg_emotional_weight = np.mean([exp.emotional_weight for exp in experiences])
        
        # Diverzita kontextu (čím více různých kontextů, tím širší aplikovatelnost)
        contexts = [tuple(sorted(exp.context.items())) for exp in experiences]
        unique_contexts = len(set(contexts))
        diversity_score = min(1.0, unique_contexts / len(experiences))
        
        # Kombinované skóre
        applicability = (
            0.4 * avg_importance +
            0.3 * avg_emotional_weight +
            0.3 * diversity_score
        )
        
        return max(0.0, min(1.0, applicability))

class InsightGenerator:
    """Generování poznatků během snění"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_confidence_threshold = config.get('min_insight_confidence', 0.6)
        self.max_insights_per_cycle = config.get('max_insights_per_cycle', 10)
        
    def generate_insights(self, consolidated_memories: List[ConsolidatedMemory], 
                         recent_experiences: List[ExperienceRecord]) -> List[DreamingInsight]:
        """Generování poznatků z konsolidovaných pamětí"""
        try:
            insights = []
            
            # Generování různých typů poznatků
            insights.extend(self._generate_pattern_insights(consolidated_memories))
            insights.extend(self._generate_optimization_insights(consolidated_memories))
            insights.extend(self._generate_prediction_insights(consolidated_memories, recent_experiences))
            insights.extend(self._generate_synthesis_insights(consolidated_memories))
            
            # Filtrování podle důvěry
            filtered_insights = [
                insight for insight in insights 
                if insight.confidence >= self.min_confidence_threshold
            ]
            
            # Seřazení podle priority
            filtered_insights.sort(key=lambda x: x.priority_score, reverse=True)
            
            # Omezení počtu poznatků
            final_insights = filtered_insights[:self.max_insights_per_cycle]
            
            logger.info(f"Vygenerováno {len(final_insights)} poznatků z {len(consolidated_memories)} pamětí")
            
            return final_insights
            
        except Exception as e:
            logger.error(f"Chyba při generování poznatků: {e}")
            return []
    
    def _generate_pattern_insights(self, memories: List[ConsolidatedMemory]) -> List[DreamingInsight]:
        """Generování poznatků o vzorcích"""
        insights = []
        
        # Hledání vzorců napříč pamětmi
        all_patterns = defaultdict(list)
        
        for memory in memories:
            for pattern, weight in memory.pattern_weights.items():
                all_patterns[pattern].append({
                    'memory_id': memory.memory_id,
                    'weight': weight,
                    'confidence': memory.confidence_score,
                    'applicability': memory.applicability_score
                })
        
        # Generování poznatků pro významné vzorce
        for pattern, occurrences in all_patterns.items():
            if len(occurrences) >= 3:  # Minimálně 3 výskyty
                avg_weight = np.mean([occ['weight'] for occ in occurrences])
                avg_confidence = np.mean([occ['confidence'] for occ in occurrences])
                
                if avg_weight > 0.6 and avg_confidence > 0.7:
                    insight = DreamingInsight(
                        insight_id=f"pattern_{int(time.time())}_{hash(pattern) % 1000}",
                        generation_timestamp=datetime.now(),
                        insight_type='pattern',
                        content=f"Opakující se vzorec '{pattern}' s vysokou vahou {avg_weight:.2f}",
                        confidence=avg_confidence,
                        evidence=[f"Vyskytuje se v {len(occurrences)} konsolidovaných pamětech"],
                        applicability_context={'pattern': pattern, 'frequency': len(occurrences)},
                        priority_score=avg_weight * avg_confidence
                    )
                    insights.append(insight)
        
        return insights
    
    def _generate_optimization_insights(self, memories: List[ConsolidatedMemory]) -> List[DreamingInsight]:
        """Generování optimalizačních poznatků"""
        insights = []
        
        # Analýza úspěšných a neúspěšných vzorců
        success_memories = [m for m in memories if m.experience_type == 'success' and m.confidence_score > 0.7]
        failure_memories = [m for m in memories if m.experience_type == 'failure' and m.confidence_score > 0.7]
        
        if success_memories and failure_memories:
            # Porovnání vzorců úspěchu a selhání
            success_patterns = set()
            for memory in success_memories:
                success_patterns.update(memory.pattern_weights.keys())
            
            failure_patterns = set()
            for memory in failure_memories:
                failure_patterns.update(memory.pattern_weights.keys())
            
            # Nalezení vzorců, které se liší mezi úspěchem a selháním
            success_only = success_patterns - failure_patterns
            failure_only = failure_patterns - success_patterns
            
            if success_only:
                insight = DreamingInsight(
                    insight_id=f"opt_success_{int(time.time())}",
                    generation_timestamp=datetime.now(),
                    insight_type='optimization',
                    content=f"Vzorce spojené s úspěchem: {', '.join(list(success_only)[:5])}",
                    confidence=0.8,
                    evidence=[f"Analýza {len(success_memories)} úspěšných a {len(failure_memories)} neúspěšných případů"],
                    applicability_context={'optimization_type': 'success_patterns', 'patterns': list(success_only)},
                    priority_score=0.8
                )
                insights.append(insight)
            
            if failure_only:
                insight = DreamingInsight(
                    insight_id=f"opt_failure_{int(time.time())}",
                    generation_timestamp=datetime.now(),
                    insight_type='optimization',
                    content=f"Vzorce k vyhnutí se: {', '.join(list(failure_only)[:5])}",
                    confidence=0.8,
                    evidence=[f"Analýza {len(success_memories)} úspěšných a {len(failure_memories)} neúspěšných případů"],
                    applicability_context={'optimization_type': 'avoid_patterns', 'patterns': list(failure_only)},
                    priority_score=0.8
                )
                insights.append(insight)
        
        return insights
    
    def _generate_prediction_insights(self, memories: List[ConsolidatedMemory], 
                                    recent_experiences: List[ExperienceRecord]) -> List[DreamingInsight]:
        """Generování prediktivních poznatků"""
        insights = []
        
        # Analýza trendů v recentních zkušenostech
        if len(recent_experiences) >= 5:
            # Časový trend
            recent_timestamps = [exp.timestamp for exp in recent_experiences[-10:]]
            recent_outcomes = [exp.outcome for exp in recent_experiences[-10:] if exp.outcome]
            
            if len(recent_outcomes) >= 3:
                success_trend = recent_outcomes.count('success') / len(recent_outcomes)
                
                if success_trend > 0.8:
                    insight = DreamingInsight(
                        insight_id=f"pred_trend_{int(time.time())}",
                        generation_timestamp=datetime.now(),
                        insight_type='prediction',
                        content=f"Trend zvyšující se úspěšnosti ({success_trend:.1%}) - očekávání pozitivního vývoje",
                        confidence=0.7,
                        evidence=[f"Posledních {len(recent_outcomes)} zkušeností má {success_trend:.1%} úspěšnost"],
                        applicability_context={'prediction_type': 'trend', 'success_rate': success_trend},
                        priority_score=0.7
                    )
                    insights.append(insight)
                elif success_trend < 0.3:
                    insight = DreamingInsight(
                        insight_id=f"pred_warning_{int(time.time())}",
                        generation_timestamp=datetime.now(),
                        insight_type='prediction',
                        content=f"Varovný trend klesající úspěšnosti ({success_trend:.1%}) - doporučena změna přístupu",
                        confidence=0.7,
                        evidence=[f"Posledních {len(recent_outcomes)} zkušeností má {success_trend:.1%} úspěšnost"],
                        applicability_context={'prediction_type': 'warning', 'success_rate': success_trend},
                        priority_score=0.8
                    )
                    insights.append(insight)
        
        return insights
    
    def _generate_synthesis_insights(self, memories: List[ConsolidatedMemory]) -> List[DreamingInsight]:
        """Generování syntetických poznatků"""
        insights = []
        
        # Hledání neočekávaných spojení mezi různými typy zkušeností
        different_types = set(memory.experience_type for memory in memories)
        
        if len(different_types) >= 3:  # Minimálně 3 různé typy
            # Analýza společných prvků napříč typy
            common_elements = self._find_cross_type_patterns(memories)
            
            if common_elements:
                insight = DreamingInsight(
                    insight_id=f"synth_cross_{int(time.time())}",
                    generation_timestamp=datetime.now(),
                    insight_type='synthesis',
                    content=f"Společné prvky napříč {len(different_types)} typy zkušeností: {', '.join(list(common_elements)[:5])}",
                    confidence=0.6,
                    evidence=[f"Analýza {len(memories)} konsolidovaných pamětí různých typů"],
                    applicability_context={'synthesis_type': 'cross_type', 'common_elements': list(common_elements)},
                    priority_score=0.6
                )
                insights.append(insight)
        
        return insights
    
    def _find_cross_type_patterns(self, memories: List[ConsolidatedMemory]) -> Set[str]:
        """Nalezení vzorců napříč různými typy zkušeností"""
        type_patterns = defaultdict(set)
        
        for memory in memories:
            type_patterns[memory.experience_type].update(memory.pattern_weights.keys())
        
        # Nalezení průniků mezi různými typy
        all_patterns = set()
        for patterns in type_patterns.values():
            all_patterns.update(patterns)
        
        common_patterns = set()
        for pattern in all_patterns:
            # Zkontrolovat, zda se vzorec objevuje ve více než polovině typů
            types_with_pattern = sum(1 for patterns in type_patterns.values() if pattern in patterns)
            if types_with_pattern >= len(type_patterns) / 2:
                common_patterns.add(pattern)
        
        return common_patterns

class DreamingOrchestrator:
    """Hlavní orchestrátor snění"""
    
    def __init__(self, config: Dict[str, Any], redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client
        self.consolidator = MemoryConsolidator(config.get('consolidation', {}))
        self.insight_generator = InsightGenerator(config.get('insight_generation', {}))
        
        # Úložiště
        self.experience_queue = deque(maxlen=config.get('max_experiences', 1000))
        self.consolidated_memories = []
        self.generated_insights = deque(maxlen=config.get('max_insights', 500))
        
        # Stavové proměnné
        self.is_dreaming = False
        self.last_dreaming_cycle = None
        self.dreaming_thread = None
        self.dreaming_queue = Queue(maxsize=config.get('dreaming_queue_size', 100))
        
        # Konfigurace cyklů
        self.dreaming_interval = config.get('dreaming_interval_hours', 4) * 3600  # Převod na sekundy
        self.min_experiences_for_dreaming = config.get('min_experiences_for_dreaming', 10)
        self.max_dreaming_duration = config.get('max_dreaming_duration_minutes', 30)
        
        # Inicializace uložiště
        self.storage_path = Path("dreaming_storage")
        self.storage_path.mkdir(exist_ok=True)
        
        # Redis kanály
        if self.redis_client:
            self.experience_channel = "dreaming:experiences"
            self.insight_channel = "dreaming:insights"
            self.status_channel = "dreaming:status"
    
    async def initialize(self):
        """Inicializace systému snění"""
        try:
            # Načtení existujících dat
            await self._load_existing_data()
            
            # Spuštění periodického snění
            self._start_periodic_dreaming()
            
            logger.info("Idle Dreaming System inicializován úspěšně")
            
        except Exception as e:
            logger.error(f"Chyba inicializace snění: {e}")
            raise
    
    async def add_experience(self, experience: ExperienceRecord):
        """Přidání zkušenosti pro pozdější konsolidaci"""
        try:
            # Přidání do fronty
            self.experience_queue.append(experience)
            
            # Publikování do Redis
            if self.redis_client:
                await self._publish_experience(experience)
            
            logger.debug(f"Přidána zkušenost {experience.experience_id} typu {experience.experience_type}")
            
        except Exception as e:
            logger.error(f"Chyba při přidávání zkušenosti: {e}")
    
    async def trigger_dreaming_cycle(self, force: bool = False):
        """Spuštění cyklu snění"""
        if self.is_dreaming and not force:
            logger.warning("Snění již probíhá")
            return
        
        if len(self.experience_queue) < self.min_experiences_for_dreaming and not force:
            logger.info(f"Nedostatek zkušeností pro snění ({len(self.experience_queue)} < {self.min_experiences_for_dreaming})")
            return
        
        # Spuštění snění v pozadí
        self.dreaming_thread = threading.Thread(target=self._dreaming_cycle_worker)
        self.dreaming_thread.daemon = True
        self.dreaming_thread.start()
    
    def _dreaming_cycle_worker(self):
        """Pracovní vlákno pro cyklus snění"""
        try:
            self.is_dreaming = True
            start_time = time.time()
            
            logger.info("Zahajuji cyklus kognitivního snění")
            
            # Spuštění asynchronního snění
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(self._perform_dreaming_cycle())
            finally:
                loop.close()
            
            duration = time.time() - start_time
            
            logger.info(f"Cyklus snění dokončen za {duration:.2f} sekund")
            
            # Metriky
            DREAMING_DURATION.labels(phase='total').observe(duration)
            
        except Exception as e:
            logger.error(f"Chyba během cyklu snění: {e}")
            DREAMING_CYCLES.labels(phase='total', status='error').inc()
        
        finally:
            self.is_dreaming = False
            self.last_dreaming_cycle = datetime.now()
    
    async def _perform_dreaming_cycle(self):
        """Hlavní cyklus kognitivního snění"""
        try:
            # Fáze 1: Příprava dat
            DREAMING_CYCLES.labels(phase='preparation', status='started').inc()
            experiences = list(self.experience_queue)
            recent_experiences = experiences[-50:] if len(experiences) > 50 else experiences
            
            logger.info(f"Zahajuji konsolidaci {len(experiences)} zkušeností")
            
            # Fáze 2: Konsolidace paměti
            DREAMING_CYCLES.labels(phase='consolidation', status='started').inc()
            consolidated_memories = self.consolidator.consolidate_experiences(experiences)
            
            if consolidated_memories:
                self.consolidated_memories.extend(consolidated_memories)
                
                # Aktualizace metrik
                consolidation_rate = len(consolidated_memories) / len(experiences) if experiences else 0
                DREAMING_CONSOLIDATION_RATE.set(consolidation_rate)
            
            # Fáze 3: Generování poznatků
            DREAMING_CYCLES.labels(phase='insight_generation', status='started').inc()
            insights = self.insight_generator.generate_insights(
                consolidated_memories, recent_experiences
            )
            
            # Fáze 4: Integrace poznatků
            DREAMING_CYCLES.labels(phase='integration', status='started').inc()
            for insight in insights:
                self.generated_insights.append(insight)
                
                # Publikování poznatku
                if self.redis_client:
                    await self._publish_insight(insight)
                
                # Metriky
                DREAMING_INSIGHTS.labels(type=insight.insight_type).inc()
            
            # Fáze 5: Vyčištění
            DREAMING_CYCLES.labels(phase='cleanup', status='started').inc()
            
            # Odstranění zpracovaných zkušeností
            if consolidated_memories:
                # Zachování nejnovějších zkušeností pro příští cyklus
                keep_count = min(50, len(experiences))  # Zachovat posledních 50
                self.experience_queue.clear()
                self.experience_queue.extend(experiences[-keep_count:])
            
            # Aktualizace metrik
            DREAMING_CYCLES.labels(phase='total', status='completed').inc()
            DREAMING_MEMORY_USAGE.set(psutil.Process().memory_info().rss)
            
            logger.info(f"Cyklus snění dokončen: {len(consolidated_memories)} konsolidovaných pamětí, {len(insights)} poznatků")
            
            # Publikování statusu
            if self.redis_client:
                await self._publish_status("completed", {
                    'consolidated_memories': len(consolidated_memories),
                    'generated_insights': len(insights),
                    'processed_experiences': len(experiences)
                })
            
        except Exception as e:
            logger.error(f"Chyba během cyklu snění: {e}")
            DREAMING_CYCLES.labels(phase='total', status='error').inc()
            
            if self.redis_client:
                await self._publish_status("error", {'error': str(e)})
    
    def _start_periodic_dreaming(self):
        """Spuštění periodického snění"""
        def dreaming_scheduler():
            while True:
                try:
                    time.sleep(self.dreaming_interval)
                    
                    # Kontrola, zda je dost zkušeností
                    if len(self.experience_queue) >= self.min_experiences_for_dreaming:
                        logger.info("Spouštím plánovaný cyklus snění")
                        self.trigger_dreaming_cycle()
                    else:
                        logger.debug(f"Nedostatek zkušeností pro plánované snění ({len(self.experience_queue)} < {self.min_experiences_for_dreaming})")
                
                except Exception as e:
                    logger.error(f"Chyba v plánovači snění: {e}")
        
        scheduler_thread = threading.Thread(target=dreaming_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logger.info(f"Plánovač snění spuštěn s intervalem {self.dreaming_interval / 3600} hodin")
    
    async def _load_existing_data(self):
        """Načtení existujících dat"""
        try:
            data_file = self.storage_path / "dreaming_data.json"
            
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Načtení konsolidovaných pamětí
                if 'consolidated_memories' in data:
                    for memory_data in data['consolidated_memories']:
                        memory = ConsolidatedMemory(**memory_data)
                        self.consolidated_memories.append(memory)
                
                # Načtení poznatků
                if 'insights' in data:
                    for insight_data in data['insights']:
                        insight = DreamingInsight(**insight_data)
                        self.generated_insights.append(insight)
                
                logger.info(f"Načteno {len(self.consolidated_memories)} konsolidovaných pamětí a {len(self.generated_insights)} poznatků")
            
        except Exception as e:
            logger.error(f"Chyba při načítání dat snění: {e}")
    
    async def save_data(self):
        """Uložení dat snění"""
        try:
            data = {
                'consolidated_memories': [asdict(memory) for memory in self.consolidated_memories[-100:]],  # Uložit posledních 100
                'insights': [asdict(insight) for insight in list(self.generated_insights)],
                'last_save': datetime.now().isoformat()
            }
            
            data_file = self.storage_path / "dreaming_data.json"
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info("Data snění úspěšně uložena")
            
        except Exception as e:
            logger.error(f"Chyba při ukládání dat snění: {e}")
    
    async def _publish_experience(self, experience: ExperienceRecord):
        """Publikování zkušenosti do Redis"""
        try:
            experience_data = {
                'experience_id': experience.experience_id,
                'timestamp': experience.timestamp.isoformat(),
                'experience_type': experience.experience_type,
                'context': experience.context,
                'emotional_weight': experience.emotional_weight,
                'importance_score': experience.importance_score,
                'tags': list(experience.tags),
                'related_patterns': experience.related_patterns
            }
            
            await self.redis_client.publish(self.experience_channel, json.dumps(experience_data))
            
        except Exception as e:
            logger.error(f"Chyba při publikování zkušenosti: {e}")
    
    async def _publish_insight(self, insight: DreamingInsight):
        """Publikování poznatku do Redis"""
        try:
            insight_data = {
                'insight_id': insight.insight_id,
                'generation_timestamp': insight.generation_timestamp.isoformat(),
                'insight_type': insight.insight_type,
                'content': insight.content,
                'confidence': insight.confidence,
                'evidence': insight.evidence,
                'applicability_context': insight.applicability_context,
                'priority_score': insight.priority_score
            }
            
            await self.redis_client.publish(self.insight_channel, json.dumps(insight_data, default=str))
            
        except Exception as e:
            logger.error(f"Chyba při publikování poznatku: {e}")
    
    async def _publish_status(self, status: str, data: Dict[str, Any] = None):
        """Publikování statusu snění"""
        try:
            status_data = {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'data': data or {}
            }
            
            await self.redis_client.publish(self.status_channel, json.dumps(status_data, default=str))
            
        except Exception as e:
            logger.error(f"Chyba při publikování statusu: {e}")
    
    async def get_dreaming_stats(self) -> Dict[str, Any]:
        """Získání statistik snění"""
        try:
            return {
                'is_dreaming': self.is_dreaming,
                'total_experiences': len(self.experience_queue),
                'total_consolidated_memories': len(self.consolidated_memories),
                'total_insights': len(self.generated_insights),
                'last_dreaming_cycle': self.last_dreaming_cycle.isoformat() if self.last_dreaming_cycle else None,
                'config': {
                    'dreaming_interval_hours': self.dreaming_interval / 3600,
                    'min_experiences_for_dreaming': self.min_experiences_for_dreaming,
                    'max_dreaming_duration_minutes': self.max_dreaming_duration
                },
                'memory_usage': psutil.Process().memory_info().rss
            }
            
        except Exception as e:
            logger.error(f"Chyba při získávání statistik: {e}")
            return {}
    
    async def get_recent_insights(self, limit: int = 10, insight_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Získání nedávných poznatků"""
        try:
            insights = list(self.generated_insights)
            
            if insight_type:
                insights = [insight for insight in insights if insight.insight_type == insight_type]
            
            # Seřazení podle času
            insights.sort(key=lambda x: x.generation_timestamp, reverse=True)
            
            # Vrácení jako slovníky
            result = []
            for insight in insights[:limit]:
                result.append({
                    'insight_id': insight.insight_id,
                    'generation_timestamp': insight.generation_timestamp.isoformat(),
                    'insight_type': insight.insight_type,
                    'content': insight.content,
                    'confidence': insight.confidence,
                    'priority_score': insight.priority_score
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Chyba při získávání poznatků: {e}")
            return []
    
    async def cleanup(self):
        """Vyčištění systému snění"""
        try:
            logger.info("Čistím Idle Dreaming System")
            
            # Zastavení snění
            self.is_dreaming = False
            
            # Uložení dat
            await self.save_data()
            
            # Vyčištění front
            self.experience_queue.clear()
            self.generated_insights.clear()
            
            logger.info("Idle Dreaming System vyčištěn")
            
        except Exception as e:
            logger.error(f"Chyba při čištění systému snění: {e}")

# Pomocné funkce
def create_dreaming_orchestrator(config: Optional[Dict[str, Any]] = None, 
                                redis_client: Optional[redis.Redis] = None) -> DreamingOrchestrator:
    """Vytvoření výchozí instance orchestrátoru snění"""
    default_config = {
        'dreaming_interval_hours': 4,
        'min_experiences_for_dreaming': 10,
        'max_dreaming_duration_minutes': 30,
        'max_experiences': 1000,
        'max_insights': 500,
        'dreaming_queue_size': 100,
        'consolidation': {
            'consolidation_threshold': 0.7,
            'pattern_similarity_threshold': 0.8,
            'min_group_size': 3
        },
        'insight_generation': {
            'min_insight_confidence': 0.6,
            'max_insights_per_cycle': 10
        }
    }
    
    if config:
        default_config.update(config)
    
    return DreamingOrchestrator(default_config, redis_client)

async def demo_dreaming():
    """Demo funkce pro testování systému snění"""
    try:
        # Vytvoření orchestrátoru
        orchestrator = create_dreaming_orchestrator()
        await orchestrator.initialize()
        
        print("🌙 Idle Dreaming System demo spuštěno")
        
        # Vytvoření testovacích zkušeností
        test_experiences = [
            ExperienceRecord(
                experience_id=f"test_{i}",
                timestamp=datetime.now() - timedelta(hours=i),
                experience_type=['success', 'failure', 'learning', 'neutral'][i % 4],
                context={'module_type': 'test_module', 'operation': f'op_{i % 3}'},
                emotional_weight=0.3 + (i % 7) * 0.1,
                importance_score=0.4 + (i % 6) * 0.1,
                tags={f'tag_{i % 5}', f'category_{i % 3}'},
                related_patterns=[f'pattern_{i % 4}', f'pattern_{(i + 1) % 4}'],
                outcome=['success', 'failure', 'neutral'][i % 3],
                lessons_learned=[f'Lekce {i}', f'Důležitý poznatek {i}']
            )
            for i in range(20)
        ]
        
        # Přidání zkušeností
        print("📥 Přidávám testovací zkušenosti...")
        for exp in test_experiences:
            await orchestrator.add_experience(exp)
        
        print(f"✅ Přidáno {len(test_experiences)} testovacích zkušeností")
        
        # Spuštění cyklu snění
        print("🌙 Spouštím cyklus kognitivního snění...")
        await orchestrator.trigger_dreaming_cycle(force=True)
        
        # Čekání na dokončení
        print("⏳ Čekám na dokončení snění...")
        while orchestrator.is_dreaming:
            await asyncio.sleep(1)
        
        # Získání výsledků
        print("\n📊 Výsledky snění:")
        stats = await orchestrator.get_dreaming_stats()
        print(f"   - Konsolidované paměti: {stats['total_consolidated_memories']}")
        print(f"   - Vygenerované poznatky: {stats['total_insights']}")
        print(f"   - Zpracované zkušenosti: {stats['total_experiences']}")
        
        # Získání nedávných poznatků
        recent_insights = await orchestrator.get_recent_insights(limit=5)
        print(f"\n💡 Nedávné poznatky ({len(recent_insights)}):")
        
        for i, insight in enumerate(recent_insights, 1):
            print(f"   {i}. [{insight['insight_type']}] {insight['content'][:80]}...")
            print(f"      Důvěra: {insight['confidence']:.2f}, Priorita: {insight['priority_score']:.2f}")
        
        # Vyčištění
        print("\n🧹 Vyčišťuji systém...")
        await orchestrator.cleanup()
        
        print("\n🎉 Demo kognitivního snění dokončeno!")
        
    except Exception as e:
        print(f"❌ Chyba při demo snění: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Spuštění demo
    asyncio.run(demo_dreaming())