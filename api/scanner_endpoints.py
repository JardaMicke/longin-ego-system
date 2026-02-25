from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging
from datetime import datetime
import json
import redis.asyncio as redis
import cv2
import numpy as np
import io
from PIL import Image

from kernel.scanner.advanced_scanner import AdvancedScanner, ScannerConfig, VisualChange
from kernel.security.auth_middleware import AuthMiddleware
from api.config import get_settings

# Konfigurace loggingu
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/scanner", tags=["scanner"])

# Globální instance skeneru (bude inicializována při startu aplikace)
scanner_instance: Optional[AdvancedScanner] = None

async def get_scanner():
    """Získání instance skeneru"""
    global scanner_instance
    if scanner_instance is None:
        settings = get_settings()
        redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        scanner_instance = AdvancedScanner(redis_client=redis_client)
        await scanner_instance.initialize()
    return scanner_instance

# Modely
class ScannerStatus(BaseModel):
    is_running: bool
    screenshot_count: int
    changes_detected: int
    memory_usage: int
    queue_size: int
    config: Dict[str, Any]

class VisualChangeResponse(BaseModel):
    change_id: str
    timestamp: str
    change_type: str
    confidence: float
    coordinates: List[int]
    area: int
    description: str
    text_content: Optional[str] = None
    element_type: Optional[str] = None
    screenshot_path: Optional[str] = None
    diff_image_path: Optional[str] = None

class TemplateMatch(BaseModel):
    x: int
    y: int
    width: int
    height: int
    score: float

# Endpoints
@router.post("/start", response_model=Dict[str, str])
async def start_scanner(
    background_tasks: BackgroundTasks,
    scanner: AdvancedScanner = Depends(get_scanner),
    # user: Dict = Depends(AuthMiddleware.require_role("admin"))  # Odkomentovat po integraci auth
):
    """Spuštění skeneru"""
    if scanner.is_running:
        return {"status": "already_running", "message": "Scanner is already running"}
    
    background_tasks.add_task(scanner.start_scanning)
    return {"status": "started", "message": "Scanner started successfully"}

@router.post("/stop", response_model=Dict[str, str])
async def stop_scanner(
    scanner: AdvancedScanner = Depends(get_scanner),
    # user: Dict = Depends(AuthMiddleware.require_role("admin"))
):
    """Zastavení skeneru"""
    await scanner.stop_scanning()
    return {"status": "stopped", "message": "Scanner stopped successfully"}

@router.get("/status", response_model=ScannerStatus)
async def get_status(
    scanner: AdvancedScanner = Depends(get_scanner),
    # user: Dict = Depends(AuthMiddleware.require_role("user"))
):
    """Získání stavu skeneru"""
    status_data = await scanner.get_scanner_status()
    return ScannerStatus(**status_data)

@router.get("/history", response_model=List[VisualChangeResponse])
async def get_history(
    limit: int = 100,
    scanner: AdvancedScanner = Depends(get_scanner),
    # user: Dict = Depends(AuthMiddleware.require_role("user"))
):
    """Získání historie změn"""
    history = await scanner.get_change_history(limit)
    
    # Konverze datetime na string a tuple na list
    result = []
    for item in history:
        # Převedení tuple souřadnic na list pro JSON
        item_copy = item.copy()
        item_copy['coordinates'] = list(item['coordinates'])
        result.append(VisualChangeResponse(**item_copy))
        
    return result

@router.post("/find-element", response_model=List[TemplateMatch])
async def find_element(
    file: UploadFile = File(...),
    threshold: float = 0.8,
    scanner: AdvancedScanner = Depends(get_scanner),
    # user: Dict = Depends(AuthMiddleware.require_role("user"))
):
    """Nalezení elementu podle obrázku (template matching)"""
    try:
        # Načtení nahraného obrázku
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        template_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Hledání
        matches = scanner.find_element_by_template(template_np, threshold)
        
        # Formátování výsledku
        result = []
        for match in matches:
            x1, y1, x2, y2, score = match
            result.append(TemplateMatch(
                x=x1,
                y=y1,
                width=x2-x1,
                height=y2-y1,
                score=score
            ))
            
        return result
        
    except Exception as e:
        logger.error(f"Chyba při hledání elementu: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding element: {str(e)}"
        )

@router.get("/screenshot")
async def get_current_screenshot(
    scanner: AdvancedScanner = Depends(get_scanner),
    # user: Dict = Depends(AuthMiddleware.require_role("user"))
):
    """Získání aktuálního screenshotu"""
    from fastapi.responses import StreamingResponse
    
    try:
        if scanner.last_screenshot is None:
            # Pokus o pořízení nového
            await scanner.screenshot_capture.capture_screenshot()
            
        if scanner.last_screenshot is None:
             raise HTTPException(status_code=404, detail="No screenshot available")
             
        # Konverze BGR na RGB a uložení do BytesIO
        img_rgb = cv2.cvtColor(scanner.last_screenshot, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img_rgb)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/png")
        
    except Exception as e:
        logger.error(f"Chyba při získávání screenshotu: {e}")
        raise HTTPException(status_code=500, detail=str(e))
