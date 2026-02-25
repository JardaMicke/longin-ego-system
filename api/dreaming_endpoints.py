"""
API Endpoints pro Idle Dreaming System

Poskytuje REST API pro ovládání a monitoring Idle Dreaming System - kognitivní konsolidace během nečinnosti.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from kernel.security.auth_middleware import get_current_user
from kernel.security.auth_manager import AuthManager, User
from kernel.cognition.dreaming_service import IdleDreamingService


# Pydantic modely pro API

class DreamingStatusResponse(BaseModel):
    """Odpověď pro status Idle Dreaming"""
    service_active: bool = Field(..., description="Zda je služba aktivní")
    dreaming_active: bool = Field(..., description="Zda právě probíhá snění")
    last_session: Optional[str] = Field(None, description="ID poslední snovací relace")
    last_session_time: Optional[datetime] = Field(None, description="Čas poslední relace")
    total_sessions: int = Field(..., description="Celkový počet relací")
    total_insights: int = Field(..., description="Celkový počet poznatků")
    total_recommendations: int = Field(..., description="Celkový počet doporučení")
    average_comfort_score: float = Field(..., description="Průměrné kognitivní komfortní skóre")
    next_scheduled_check: datetime = Field(..., description="Čas další kontroly")


class DreamingSessionResponse(BaseModel):
    """Odpověď pro detaily snovací relace"""
    session_id: str = Field(..., description="ID relace")
    start_time: datetime = Field(..., description="Čas zahájení")
    end_time: Optional[datetime] = Field(None, description="Čas ukončení")
    phase: str = Field(..., description="Aktuální fáze snění")
    insights_count: int = Field(..., description="Počet poznatků")
    recommendations_count: int = Field(..., description="Počet doporučení")
    memory_consolidations_count: int = Field(..., description="Počet konsolidací paměti")
    cognitive_comfort_score: float = Field(..., description="Kognitivní komfortní skóre")


class PerformanceInsightResponse(BaseModel):
    """Odpověď pro poznatek o výkonu"""
    category: str = Field(..., description="Kategorie výkonu")
    metric: str = Field(..., description="Konkrétní metrika")
    current_value: float = Field(..., description="Aktuální hodnota")
    baseline_value: float = Field(..., description="Základní hodnota")
    deviation: float = Field(..., description="Odchylka od baseline")
    severity: str = Field(..., description="Závažnost: low/medium/high/critical")
    recommendation: str = Field(..., description="Doporučení pro zlepšení")
    timestamp: datetime = Field(..., description="Čas pozorování")


class OptimizationRecommendationResponse(BaseModel):
    """Odpověď pro optimalizační doporučení"""
    type: str = Field(..., description="Typ optimalizace: memory/performance/security/structure")
    priority: int = Field(..., description="Priorita 1-10")
    description: str = Field(..., description="Popis doporučení")
    estimated_impact: str = Field(..., description="Odhadovaný dopad")
    implementation_complexity: str = Field(..., description="Složitost implementace")
    resource_requirements: Dict[str, float] = Field(default_factory=dict, description="Požadavky na prostředky")


class DreamingTriggerRequest(BaseModel):
    """Požadavek na manuální spuštění snění"""
    reason: str = Field("manual_request", description="Důvod spuštění snění")
    force: bool = Field(False, description="Vynutit spuštění i přes nevhodné podmínky")


class DreamingTriggerResponse(BaseModel):
    """Odpověď na požadavek na spuštění snění"""
    status: str = Field(..., description="Status: request_sent/ignored/failed")
    message: str = Field(..., description="Popis výsledku")
    session_id: Optional[str] = Field(None, description="ID relace pokud byla zahájena")


class RecentSessionsResponse(BaseModel):
    """Odpověď pro seznam nedávných relací"""
    sessions: List[DreamingSessionResponse] = Field(..., description="Seznam relací")
    total_count: int = Field(..., description="Celkový počet nalezených relací")
    limit: int = Field(..., description="Limit vrácených relací")


class InsightsResponse(BaseModel):
    """Odpověď pro poznatky o výkonu"""
    insights: List[PerformanceInsightResponse] = Field(..., description="Seznam poznatků")
    time_range: str = Field(..., description="Časový rozsah")
    total_count: int = Field(..., description="Celkový počet poznatků")


class RecommendationsResponse(BaseModel):
    """Odpověď pro optimalizační doporučení"""
    recommendations: List[OptimizationRecommendationResponse] = Field(..., description="Seznam doporučení")
    total_count: int = Field(..., description="Celkový počet doporučení")
    unique_count: int = Field(..., description="Počet unikátních doporučení")


# Hlavní router

router = APIRouter(prefix="/dreaming", tags=["Idle Dreaming"])

# Globální instance služby (bude inicializována při startu aplikace)
dreaming_service: Optional[IdleDreamingService] = None


def get_dreaming_service() -> IdleDreamingService:
    """Dependency pro získání instance Idle Dreaming Service"""
    if dreaming_service is None:
        raise HTTPException(
            status_code=503,
            detail="Idle Dreaming Service není inicializován"
        )
    return dreaming_service


def require_permission(permission: str):
    """Dependency pro kontrolu oprávnění"""
    async def dependency(current_user: User = Depends(get_current_user)):
        if not hasattr(current_user, 'permissions'):
            raise HTTPException(status_code=403, detail="Uživatel nemá žádná oprávnění")
        
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Uživatel nemá oprávnění '{permission}'"
            )
        return current_user
    return dependency


# API Endpoints

@router.get("/status", response_model=DreamingStatusResponse)
async def get_dreaming_status(
    dreaming_svc: IdleDreamingService = Depends(get_dreaming_service),
    current_user: User = Depends(get_current_user)
):
    """
    Získá aktuální status Idle Dreaming System.
    
    Vrací informace o:
    - Zda je služba aktivní
    - Zda právě probíhá snění
    - Statistiky relací
    - Průměrné kognitivní komfortní skóre
    """
    try:
        status = dreaming_svc.get_service_status()
        
        return DreamingStatusResponse(
            service_active=status.service_active,
            dreaming_active=status.dreaming_active,
            last_session=status.last_session,
            last_session_time=status.last_session_time,
            total_sessions=status.total_sessions,
            total_insights=status.total_insights,
            total_recommendations=status.total_recommendations,
            average_comfort_score=status.average_comfort_score,
            next_scheduled_check=status.next_scheduled_check
        )
        
    except Exception as e:
        logging.error(f"Chyba při získávání statusu dreaming: {e}")
        raise HTTPException(status_code=500, detail=f"Interní chyba: {str(e)}")


@router.post("/trigger", response_model=DreamingTriggerResponse)
async def trigger_dreaming(
    request: DreamingTriggerRequest,
    background_tasks: BackgroundTasks,
    dreaming_svc: IdleDreamingService = Depends(get_dreaming_service),
    current_user: User = Depends(require_permission("dreaming.trigger"))
):
    """
    Manuálně spustí snovací relaci.
    
    Vyžaduje oprávnění 'dreaming.trigger'.
    """
    try:
        # Kontrola, zda již neprobíhá snění
        status = dreaming_svc.get_service_status()
        if status.dreaming_active:
            return DreamingTriggerResponse(
                status="ignored",
                message="Snění již probíhá",
                session_id=None
            )
        
        # Pokus o spuštění snění
        result = await dreaming_svc.trigger_manual_dreaming(request.reason)
        
        if result:
            return DreamingTriggerResponse(
                status="request_sent",
                message=f"Požadavek na snění odeslán: {request.reason}",
                session_id=None  # Session ID bude k dispozici po zahájení
            )
        else:
            return DreamingTriggerResponse(
                status="failed",
                message="Nepodařilo se odeslat požadavek na snění",
                session_id=None
            )
            
    except Exception as e:
        logging.error(f"Chyba při spouštění dreaming: {e}")
        raise HTTPException(status_code=500, detail=f"Interní chyba: {str(e)}")


@router.get("/sessions", response_model=RecentSessionsResponse)
async def get_recent_sessions(
    limit: int = 10,
    dreaming_svc: IdleDreamingService = Depends(get_dreaming_service),
    current_user: User = Depends(get_current_user)
):
    """
    Získá seznam nedávných snovacích relací.
    
    Parametr 'limit' určuje maximální počet vrácených relací (max 100).
    """
    try:
        # Omezení limitu
        limit = min(max(1, limit), 100)
        
        sessions = await dreaming_svc.get_recent_sessions(limit)
        
        # Konverze na response model
        session_responses = []
        for session_data in sessions:
            session_responses.append(DreamingSessionResponse(
                session_id=session_data.get('session_id', ''),
                start_time=datetime.fromisoformat(session_data.get('start_time', '')),
                end_time=datetime.fromisoformat(session_data['end_time']) if session_data.get('end_time') else None,
                phase=session_data.get('phase', 'unknown'),
                insights_count=session_data.get('insights_count', 0),
                recommendations_count=session_data.get('recommendations_count', 0),
                memory_consolidations_count=session_data.get('memory_consolidations_count', 0),
                cognitive_comfort_score=session_data.get('cognitive_comfort_score', 0.0)
            ))
        
        return RecentSessionsResponse(
            sessions=session_responses,
            total_count=len(sessions),
            limit=limit
        )
        
    except Exception as e:
        logging.error(f"Chyba při získávání relací: {e}")
        raise HTTPException(status_code=500, detail=f"Interní chyba: {str(e)}")


@router.get("/sessions/{session_id}", response_model=DreamingSessionResponse)
async def get_session_details(
    session_id: str,
    dreaming_svc: IdleDreamingService = Depends(get_dreaming_service),
    current_user: User = Depends(get_current_user)
):
    """
    Získá detaily konkrétní snovací relace.
    """
    try:
        session_data = await dreaming_svc.get_session_details(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Relace nenalezena")
        
        return DreamingSessionResponse(
            session_id=session_data.get('session_id', session_id),
            start_time=datetime.fromisoformat(session_data.get('start_time', '')),
            end_time=datetime.fromisoformat(session_data['end_time']) if session_data.get('end_time') else None,
            phase=session_data.get('phase', 'unknown'),
            insights_count=session_data.get('insights_count', 0),
            recommendations_count=session_data.get('recommendations_count', 0),
            memory_consolidations_count=session_data.get('memory_consolidations_count', 0),
            cognitive_comfort_score=session_data.get('cognitive_comfort_score', 0.0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Chyba při získávání detailů relace: {e}")
        raise HTTPException(status_code=500, detail=f"Interní chyba: {str(e)}")


@router.get("/insights", response_model=InsightsResponse)
async def get_performance_insights(
    time_range: str = "24h",
    dreaming_svc: IdleDreamingService = Depends(get_dreaming_service),
    current_user: User = Depends(get_current_user)
):
    """
    Získá poznatky o výkonu z nedávných snovacích relací.
    
    Parametr 'time_range' může být: 1h, 6h, 24h, 7d, 30d
    """
    try:
        # Validace time_range
        valid_ranges = ["1h", "6h", "24h", "7d", "30d"]
        if time_range not in valid_ranges:
            raise HTTPException(
                status_code=400,
                detail=f"Neplatný time_range. Použijte jeden z: {', '.join(valid_ranges)}"
            )
        
        insights = await dreaming_svc.get_performance_insights(time_range)
        
        # Konverze na response model
        insight_responses = []
        for insight in insights:
            insight_responses.append(PerformanceInsightResponse(
                category=insight.get('category', ''),
                metric=insight.get('metric', ''),
                current_value=insight.get('current_value', 0.0),
                baseline_value=insight.get('baseline_value', 0.0),
                deviation=insight.get('deviation', 0.0),
                severity=insight.get('severity', 'low'),
                recommendation=insight.get('recommendation', ''),
                timestamp=datetime.fromisoformat(insight.get('timestamp', datetime.now().isoformat()))
            ))
        
        return InsightsResponse(
            insights=insight_responses,
            time_range=time_range,
            total_count=len(insights)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Chyba při získávání poznatků: {e}")
        raise HTTPException(status_code=500, detail=f"Interní chyba: {str(e)}")


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_optimization_recommendations(
    limit: int = 10,
    dreaming_svc: IdleDreamingService = Depends(get_dreaming_service),
    current_user: User = Depends(get_current_user)
):
    """
    Získá optimalizační doporučení z nedávných snovacích relací.
    
    Parametr 'limit' určuje maximální počet vrácených doporučení (max 50).
    """
    try:
        # Omezení limitu
        limit = min(max(1, limit), 50)
        
        recommendations = await dreaming_svc.get_optimization_recommendations(limit)
        
        # Konverze na response model
        recommendation_responses = []
        for rec in recommendations:
            recommendation_responses.append(OptimizationRecommendationResponse(
                type=rec.get('type', ''),
                priority=rec.get('priority', 5),
                description=rec.get('description', ''),
                estimated_impact=rec.get('estimated_impact', ''),
                implementation_complexity=rec.get('implementation_complexity', ''),
                resource_requirements=rec.get('resource_requirements', {})
            ))
        
        return RecommendationsResponse(
            recommendations=recommendation_responses,
            total_count=len(recommendations),
            unique_count=len(set(r.description for r in recommendation_responses))
        )
        
    except Exception as e:
        logging.error(f"Chyba při získávání doporučení: {e}")
        raise HTTPException(status_code=500, detail=f"Interní chyba: {str(e)}")


@router.get("/health")
async def get_dreaming_health(
    dreaming_svc: IdleDreamingService = Depends(get_dreaming_service)
):
    """
    Získá health check status Idle Dreaming System.
    
    Vrácí základní informace o zdraví služby.
    """
    try:
        status = dreaming_svc.get_service_status()
        
        # Určení celkového health status
        if not status.service_active:
            health_status = "unhealthy"
            health_score = 0.0
        elif status.dreaming_active:
            health_status = "dreaming"
            health_score = 0.8
        elif status.total_sessions == 0:
            health_status = "idle"
            health_score = 0.9
        else:
            health_status = "healthy"
            health_score = min(1.0, status.average_comfort_score + 0.2)
        
        return {
            "status": health_status,
            "health_score": health_score,
            "service_active": status.service_active,
            "dreaming_active": status.dreaming_active,
            "total_sessions": status.total_sessions,
            "average_comfort_score": status.average_comfort_score,
            "last_session_time": status.last_session_time,
            "next_check": status.next_scheduled_check
        }
        
    except Exception as e:
        logging.error(f"Chyba při health check dreaming: {e}")
        return {
            "status": "error",
            "health_score": 0.0,
            "error": str(e)
        }


# Pomocná funkce pro inicializaci routeru s dreaming service

def initialize_dreaming_router(dreaming_svc: IdleDreamingService) -> APIRouter:
    """Inicializuje dreaming router s konkrétní instancí služby"""
    global dreaming_service
    dreaming_service = dreaming_svc
    return router


# Export pro použití v hlavní aplikaci
__all__ = [
    'router',
    'initialize_dreaming_router',
    'DreamingStatusResponse',
    'DreamingSessionResponse',
    'PerformanceInsightResponse',
    'OptimizationRecommendationResponse',
    'DreamingTriggerRequest',
    'DreamingTriggerResponse',
    'RecentSessionsResponse',
    'InsightsResponse',
    'RecommendationsResponse'
]