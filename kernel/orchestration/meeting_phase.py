"""
Meeting Phase pro ERTDSD cyklus

Účel: Definice a validace kontraktu mezi uživatelem a systémem
Implementuje "The Meeting" fázi z dokumentace ERTDSD
"""

import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import JsonOutputParser

from ..memory.postgres.client import PostgresMemoryClient
from ..security.identity_firewall import IdentityFirewall
from ..arbiter.core import GlobalArbiter
from ..bus.redis_bus import RedisBus

logger = logging.getLogger(__name__)

@dataclass
class MeetingResult:
    """Výsledek Meeting fáze"""
    task_manifest: Dict[str, Any]
    definition_of_done: List[str]
    memory_credits: Dict[str, int]
    technical_requirements: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    user_confirmation_required: bool
    estimated_duration: int  # v minutách
    complexity_score: float  # 0.0 - 1.0

@dataclass
class ContractTerms:
    """Podmínky kontraktu"""
    acceptance_criteria: List[str]
    interface_specification: Dict[str, Any]
    resource_requirements: Dict[str, int]  # RAM, VRAM, CPU
    timeout_limits: Dict[str, int]
    safety_constraints: List[str]
    rollback_conditions: List[str]

class ContractValidator:
    """Validuje technickou proveditelnost kontraktu"""
    
    def __init__(self, arbiter: GlobalArbiter):
        self.arbiter = arbiter
        self.max_ram_mb = 32768  # 32GB limit
        self.max_vram_mb = 12288  # 12GB RTX 3060 limit
        
    async def validate_contract(self, contract: ContractTerms) -> Dict[str, Any]:
        """Validuje kontrakt proti hardwarovým limitům"""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "resource_allocation": {}
        }
        
        # Kontrola RAM požadavků
        requested_ram = contract.resource_requirements.get("ram_mb", 0)
        if requested_ram > self.max_ram_mb:
            validation_result["errors"].append(
                f"Požadavek na RAM {requested_ram}MB překračuje limit {self.max_ram_mb}MB"
            )
            validation_result["valid"] = False
        elif requested_ram > self.max_ram_mb * 0.8:
            validation_result["warnings"].append(
                f"Vysoké využití RAM: {requested_ram}MB z {self.max_ram_mb}MB"
            )
            
        # Kontrola VRAM požadavků
        requested_vram = contract.resource_requirements.get("vram_mb", 0)
        if requested_vram > self.max_vram_mb:
            validation_result["errors"].append(
                f"Požadavek na VRAM {requested_vram}MB překračuje limit {self.max_vram_mb}MB"
            )
            validation_result["valid"] = False
            
        # Kontrola timeout limitů
        soft_timeout = contract.timeout_limits.get("soft_timeout", 60)
        hard_timeout = contract.timeout_limits.get("hard_timeout", 120)
        
        if soft_timeout > hard_timeout:
            validation_result["errors"].append(
                "Soft timeout nemůže být větší než hard timeout"
            )
            validation_result["valid"] = False
            
        # Kontrola bezpečnostních omezení
        safety_violations = await self._check_safety_constraints(contract)
        if safety_violations:
            validation_result["errors"].extend(safety_violations)
            validation_result["valid"] = False
            
        # Alokace zdrojů přes Arbitra
        if validation_result["valid"]:
            allocation_result = await self.arbiter.request_resource_allocation({
                "ram_mb": requested_ram,
                "vram_mb": requested_vram,
                "cpu_cores": contract.resource_requirements.get("cpu_cores", 1),
                "duration_minutes": contract.timeout_limits.get("estimated_duration", 30)
            })
            
            if allocation_result["approved"]:
                validation_result["resource_allocation"] = allocation_result
            else:
                validation_result["errors"].append(
                    f"Arbiter zamítl alokaci zdrojů: {allocation_result['reason']}"
                )
                validation_result["valid"] = False
                
        return validation_result
        
    async def _check_safety_constraints(self, contract: ContractTerms) -> List[str]:
        """Kontroluje bezpečnostní omezení"""
        violations = []
        
        # Zakázané operace
        forbidden_operations = [
            "network_access", "file_system_access", "system_calls",
            "privilege_escalation", "data_exfiltration"
        ]
        
        for constraint in contract.safety_constraints:
            if any(op in constraint.lower() for op in forbidden_operations):
                violations.append(f"Potenciálně nebezpečná operace: {constraint}")
                
        return violations

class RequirementExtractor:
    """Extrahuje a strukturuje požadavky z uživatelského vstupu"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        
    async def extract_requirements(self, user_request: str) -> Dict[str, Any]:
        """Extrahuje strukturované požadavky pomocí LLM"""
        
        prompt = ChatPromptTemplate.from_template("""
        Jako systém LONGIN EGO analyzuj uživatelský požadavek a extrahuj strukturované požadavky.
        
        Uživatelský požadavek: {user_request}
        
        Extrahuj následující informace:
        1. Hlavní cíl/purpose
        2. Funkční požadavky (co to má dělat)
        3. Nefunkční požadavky (výkon, bezpečnost, spolehlivost)
        4. Technické omezení (jazyk, framework, dependencies)
        5. Předpoklady a závislosti
        6. Přijatelná řešení/alternativy
        7. Rizika a omezení
        
        Vrať JSON s extrahovanými požadavky.
        """)
        
        chain = prompt | self.llm_client | JsonOutputParser()
        
        try:
            requirements = await chain.ainvoke({"user_request": user_request})
            return requirements
        except Exception as e:
            logger.error(f"Chyba při extrakci požadavků: {e}")
            return self._fallback_requirements_extraction(user_request)
            
    def _fallback_requirements_extraction(self, user_request: str) -> Dict[str, Any]:
        """Záložní extrakce při selhání LLM"""
        return {
            "purpose": user_request,
            "functional_requirements": ["implement user request"],
            "non_functional_requirements": ["reliable", "secure"],
            "technical_constraints": ["python", "local execution"],
            "assumptions": ["user provides clear requirements"],
            "acceptance_criteria": ["request is implemented"],
            "risks": ["ambiguous requirements"]
        }

class CreditCalculator:
    """Vypočítává memory credits potřebné pro úlohu"""
    
    def calculate_credits(self, requirements: Dict[str, Any], 
                         complexity_score: float) -> Dict[str, int]:
        """Vypočítá memory credits na základě požadavků a složitosti"""
        
        # Základní kredity
        base_credits = {
            "ram_mb": 512,      # Minimální RAM
            "vram_mb": 0,       # Žádná VRAM defaultně
            "cpu_cores": 1,     # Jeden CPU core
            "duration_minutes": 30  # 30 minut defaultně
        }
        
        # Úprava podle složitosti (0.0 - 1.0)
        complexity_multiplier = 1.0 + (complexity_score * 2.0)
        
        # Analýza požadavků
        if "machine_learning" in str(requirements).lower():
            base_credits["vram_mb"] = 4096  # 4GB VRAM pro ML
            base_credits["ram_mb"] = 4096   # 4GB RAM
            
        if "large_dataset" in str(requirements).lower():
            base_credits["ram_mb"] = 8192   # 8GB pro velké datasety
            
        if "real_time" in str(requirements).lower():
            base_credits["cpu_cores"] = 2    # Více CPU pro real-time
            base_credits["duration_minutes"] = 60
            
        # Aplikace complexity multiplier
        for key in base_credits:
            if key in ["ram_mb", "vram_mb"]:
                base_credits[key] = int(base_credits[key] * complexity_multiplier)
            elif key == "duration_minutes":
                base_credits[key] = int(base_credits[key] * (1.0 + complexity_score))
                
        return base_credits

class MeetingPhase:
    """Hlavní třída pro Meeting fázi ERTDSD cyklu"""
    
    def __init__(self, 
                 memory_client: PostgresMemoryClient,
                 identity_firewall: IdentityFirewall,
                 arbiter: GlobalArbiter,
                 redis_bus: RedisBus,
                 llm_client):
        self.memory_client = memory_client
        self.identity_firewall = identity_firewall
        self.arbiter = arbiter
        self.redis_bus = redis_bus
        self.llm_client = llm_client
        
        self.contract_validator = ContractValidator(arbiter)
        self.requirement_extractor = RequirementExtractor(llm_client)
        self.credit_calculator = CreditCalculator()
        
    async def negotiate_contract(self, user_request: str, 
                                user_context: Optional[Dict] = None) -> MeetingResult:
        """
        Hlavní metoda pro vyjednávání kontraktu
        
        Args:
            user_request: Původní uživatelský požadavek
            user_context: Kontext uživatele (volitelný)
            
        Returns:
            MeetingResult s definovaným kontraktem
        """
        
        logger.info(f"Zahajuji Meeting fázi pro požadavek: {user_request[:100]}...")
        
        # 1. Extrakce požadavků
        requirements = await self.requirement_extractor.extract_requirements(user_request)
        
        # 2. Analýza složitosti
        complexity_score = await self._calculate_complexity(requirements)
        
        # 3. Výpočet memory credits
        memory_credits = self.credit_calculator.calculate_credits(requirements, complexity_score)
        
        # 4. Vytvoření kontraktu
        contract_terms = await self._create_contract_terms(
            requirements, memory_credits, complexity_score
        )
        
        # 5. Validace kontraktu
        validation_result = await self.contract_validator.validate_contract(contract_terms)
        
        if not validation_result["valid"]:
            # Pokus o renegociaci s upravenými požadavky
            revised_contract = await self._renegotiate_contract(
                contract_terms, validation_result
            )
            contract_terms = revised_contract
            validation_result = await self.contract_validator.validate_contract(contract_terms)
            
        # 6. Generování task manifestu
        task_manifest = await self._generate_task_manifest(
            user_request, requirements, contract_terms, validation_result
        )
        
        # 7. Vytvoření Definition of Done
        definition_of_done = await self._generate_definition_of_done(
            requirements, contract_terms
        )
        
        # 8. Vyhodnocení rizik
        risk_assessment = await self._assess_risks(requirements, contract_terms)
        
        # 9. Uložení do paměti
        await self._store_contract_session({
            "user_request": user_request,
            "requirements": requirements,
            "contract_terms": contract_terms,
            "task_manifest": task_manifest,
            "definition_of_done": definition_of_done,
            "risk_assessment": risk_assessment,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # 10. Publikování události
        await self.redis_bus.publish("SYS:MEETING", {
            "phase": "completed",
            "complexity_score": complexity_score,
            "resource_requirements": memory_credits,
            "validation_status": validation_result["valid"]
        })
        
        result = MeetingResult(
            task_manifest=task_manifest,
            definition_of_done=definition_of_done,
            memory_credits=memory_credits,
            technical_requirements=requirements,
            risk_assessment=risk_assessment,
            user_confirmation_required=validation_result["valid"] and complexity_score > 0.7,
            estimated_duration=contract_terms.timeout_limits.get("estimated_duration", 30),
            complexity_score=complexity_score
        )
        
        logger.info(f"Meeting fáze dokončena. Složitost: {complexity_score:.2f}, "
                   f"Validace: {validation_result['valid']}")
        
        return result
        
    async def _calculate_complexity(self, requirements: Dict[str, Any]) -> float:
        """Vypočítává složitost úlohy (0.0 - 1.0)"""
        complexity_factors = {
            "ml_required": 0.3,
            "real_time": 0.2,
            "distributed": 0.2,
            "security_critical": 0.2,
            "large_dataset": 0.1
        }
        
        score = 0.0
        req_text = json.dumps(requirements).lower()
        
        for factor, weight in complexity_factors.items():
            if factor in req_text:
                score += weight
                
        # Normalizace na 0.0 - 1.0
        return min(score, 1.0)
        
    async def _create_contract_terms(self, requirements: Dict[str, Any], 
                                   memory_credits: Dict[str, int],
                                   complexity: float) -> ContractTerms:
        """Vytváří podmínky kontraktu"""
        
        # Odhady timeoutů podle složitosti
        base_duration = 30  # minut
        duration_multiplier = 1.0 + (complexity * 2.0)
        estimated_duration = int(base_duration * duration_multiplier)
        
        return ContractTerms(
            acceptance_criteria=requirements.get("acceptance_criteria", []),
            interface_specification=requirements.get("interface_specification", {}),
            resource_requirements=memory_credits,
            timeout_limits={
                "soft_timeout": min(60, estimated_duration),
                "hard_timeout": min(120, estimated_duration * 2),
                "estimated_duration": estimated_duration
            },
            safety_constraints=requirements.get("safety_constraints", []),
            rollback_conditions=requirements.get("rollback_conditions", [])
        )
        
    async def _renegotiate_contract(self, original_contract: ContractTerms,
                                   validation_result: Dict[str, Any]) -> ContractTerms:
        """Pokus o renegociaci kontraktu při nevalidních podmínkách"""
        
        # Snížení požadavků na zdroje
        revised_contract = ContractTerms(
            acceptance_criteria=original_contract.acceptance_criteria,
            interface_specification=original_contract.interface_specification,
            resource_requirements={
                "ram_mb": min(original_contract.resource_requirements["ram_mb"], 16384),  # Max 16GB
                "vram_mb": min(original_contract.resource_requirements["vram_mb"], 6144),   # Max 6GB
                "cpu_cores": min(original_contract.resource_requirements["cpu_cores"], 4),
                "duration_minutes": original_contract.resource_requirements["duration_minutes"]
            },
            timeout_limits={
                "soft_timeout": 60,  # Standardní limit
                "hard_timeout": 120,
                "estimated_duration": original_contract.timeout_limits["estimated_duration"]
            },
            safety_constraints=original_contract.safety_constraints,
            rollback_conditions=original_contract.rollback_conditions
        )
        
        return revised_contract
        
    async def _generate_task_manifest(self, user_request: str,
                                    requirements: Dict[str, Any],
                                    contract: ContractTerms,
                                    validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generuje task manifest pro další fáze"""
        
        return {
            "id": f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "user_request": user_request,
            "requirements": requirements,
            "contract_terms": {
                "acceptance_criteria": contract.acceptance_criteria,
                "resource_requirements": contract.resource_requirements,
                "timeout_limits": contract.timeout_limits,
                "safety_constraints": contract.safety_constraints
            },
            "validation_status": validation["valid"],
            "warnings": validation["warnings"],
            "resource_allocation": validation.get("resource_allocation", {}),
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending_approval" if validation["valid"] else "needs_revision"
        }
        
    async def _generate_definition_of_done(self, requirements: Dict[str, Any],
                                         contract: ContractTerms) -> List[str]:
        """Generuje Definition of Done na základě požadavků"""
        
        dod = []
        
        # Funkční kritéria
        for req in requirements.get("functional_requirements", []):
            dod.append(f"Implementováno: {req}")
            
        # Výkonnostní kritéria
        dod.extend([
            f"Paměťová spotřeba ≤ {contract.resource_requirements['ram_mb']}MB RAM",
            f"GPU spotřeba ≤ {contract.resource_requirements['vram_mb']}MB VRAM",
            f"Doba běhu ≤ {contract.timeout_limits['soft_timeout']}s (soft timeout)"
        ])
        
        # Bezpečnostní kritéria
        dod.extend([
            "Kód prošel Airlock validací",
            "Všechny testy úspěšně dokončeny",
            "Žádné bezpečnostní upozornění"
        ])
        
        # Technická kritéria
        dod.extend([
            "Kód je dokumentován",
            "Implementace používá Zero-Context SDK",
            "Výsledky jsou persistovány v systému"
        ])
        
        return dod
        
    async def _assess_risks(self, requirements: Dict[str, Any],
                          contract: ContractTerms) -> Dict[str, Any]:
        """Vyhodnocuje rizika implementace"""
        
        risks = {
            "technical_risks": [],
            "resource_risks": [],
            "safety_risks": [],
            "mitigation_strategies": []
        }
        
        # Technická rizika
        if "machine_learning" in str(requirements).lower():
            risks["technical_risks"].append("Vysoká spotřeba VRAM pro ML modely")
            risks["mitigation_strategies"].append("Použití kvantizovaných modelů")
            
        if "real_time" in str(requirements).lower():
            risks["technical_risks"].append("Přísné časové limity")
            risks["mitigation_strategies"].append("Optimalizace kódu a paralelizace")
            
        # Rizika zdrojů
        if contract.resource_requirements["ram_mb"] > 16384:  # >16GB
            risks["resource_risks"].append("Vysoká spotřeba RAM")
            risks["mitigation_strategies"].append("Agresivní memory management")
            
        # Bezpečnostní rizika
        if any("network" in str(req).lower() for req in contract.safety_constraints):
            risks["safety_risks"].append("Síťový přístup vyžaduje extra validaci")
            risks["mitigation_strategies"].append("Omezení na whitelisted domény")
            
        return risks
        
    async def _store_contract_session(self, session_data: Dict[str, Any]):
        """Ukládá session kontraktu do paměti"""
        
        try:
            await self.memory_client.store_memory(
                content=f"Meeting session: {session_data['user_request'][:100]}...",
                metadata={
                    "type": "meeting_session",
                    "session_data": session_data,
                    "timestamp": datetime.utcnow().isoformat()
                },
                embedding=None  # Bude automaticky vygenerováno
            )
        except Exception as e:
            logger.error(f"Chyba při ukládání session: {e}")

# Pomocné funkce pro integraci
def create_meeting_phase(runtime_context) -> MeetingPhase:
    """Factory funkce pro vytvoření MeetingPhase instance"""
    return MeetingPhase(
        memory_client=runtime_context.memory_client,
        identity_firewall=runtime_context.identity_firewall,
        arbiter=runtime_context.arbiter,
        redis_bus=runtime_context.redis_bus,
        llm_client=runtime_context.llm_client
    )