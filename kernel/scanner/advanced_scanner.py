"""
Advanced Scanner - Computer Vision Fallback System

Tento modul implementuje pokročilý skener s počítačovým viděním jako fallback,
který monitoruje UI změny a detekuje vizuální rozdíly při selhání standardních metod.

Autor: LONGIN EGO System
Verze: 1.0.0
"""

import asyncio
import cv2
import numpy as np
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import hashlib
import base64
from io import BytesIO
from PIL import Image, ImageChops, ImageDraw, ImageFont
import torch
import torchvision.transforms as transforms
from sklearn.cluster import DBSCAN
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
import psutil
import threading
from queue import Queue

# Konfigurace loggingu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metriky
SCANNER_OPERATIONS = Counter('scanner_operations_total', 'Total scanner operations', ['type', 'status'])
SCANNER_LATENCY = Histogram('scanner_operation_latency_seconds', 'Scanner operation latency', ['type'])
SCANNER_MEMORY_USAGE = Gauge('scanner_memory_usage_bytes', 'Scanner memory usage')
SCANNER_GPU_USAGE = Gauge('scanner_gpu_usage_percent', 'Scanner GPU usage')
SCANNER_QUEUE_SIZE = Gauge('scanner_queue_size', 'Scanner processing queue size')

@dataclass
class VisualChange:
    """Reprezentuje vizuální změnu detekovanou skenerem"""
    change_id: str
    timestamp: datetime
    change_type: str  # 'added', 'removed', 'modified', 'moved'
    confidence: float
    coordinates: Tuple[int, int, int, int]  # x1, y1, x2, y2
    area: int
    similarity_score: float
    description: str
    text_content: Optional[str] = None
    element_type: Optional[str] = None
    screenshot_path: Optional[str] = None
    diff_image_path: Optional[str] = None

@dataclass
class ScannerConfig:
    """Konfigurace Advanced Scanner"""
    screenshot_interval: float = 2.0  # sekundy mezi screenshoty
    change_threshold: float = 0.85  # práh podobnosti pro detekci změny
    min_change_area: int = 50  # minimální plocha změny v pixelech
    max_queue_size: int = 100  # maximální velikost fronty
    enable_gpu: bool = True  # povolit GPU akceleraci
    enable_ocr: bool = True  # povolit OCR pro textové změny
    enable_ml: bool = True  # povolit ML detekci objektů
    memory_limit_mb: int = 2048  # limit paměti pro skener
    similarity_algorithm: str = 'ssim'  # 'ssim', 'mse', 'histogram'
    cluster_eps: float = 10.0  # DBSCAN parametr
    cluster_min_samples: int = 5  # DBSCAN parametr

class ComputerVisionEngine:
    """Počítačové vidění engine pro detekci změn"""
    
    def __init__(self, config: ScannerConfig):
        self.config = config
        self.model = None
        self.ocr_engine = None
        self.device = 'cuda' if config.enable_gpu and torch.cuda.is_available() else 'cpu'
        self.memory_tracker = MemoryTracker()
        
    async def initialize(self):
        """Inicializace CV engine"""
        try:
            if self.config.enable_ml:
                await self._load_ml_models()
            if self.config.enable_ocr:
                await self._initialize_ocr()
            logger.info(f"CV Engine inicializován na {self.device}")
        except Exception as e:
            logger.error(f"Chyba inicializace CV engine: {e}")
            raise
    
    async def _load_ml_models(self):
        """Načtení ML modelů pro detekci objektů"""
        try:
            # Použití YOLOv5 pro detekci UI elementů (open-source)
            self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            self.model.to(self.device)
            self.model.eval()
            logger.info("YOLOv5 model načten úspěšně")
        except Exception as e:
            logger.warning(f"Nepodařilo se načíst YOLO model: {e}")
            self.config.enable_ml = False
    
    async def _initialize_ocr(self):
        """Inicializace OCR engine"""
        try:
            import easyocr
            self.ocr_engine = easyocr.Reader(['en', 'cs'], gpu=self.config.enable_gpu)
            logger.info("OCR engine inicializován")
        except ImportError:
            logger.warning("EasyOCR není nainstalován, OCR vypnuto")
            self.config.enable_ocr = False
        except Exception as e:
            logger.warning(f"Chyba inicializace OCR: {e}")
            self.config.enable_ocr = False
    
    def calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Výpočet podobnosti mezi dvěma obrázky"""
        if self.config.similarity_algorithm == 'ssim':
            return self._calculate_ssim(img1, img2)
        elif self.config.similarity_algorithm == 'mse':
            return self._calculate_mse(img1, img2)
        elif self.config.similarity_algorithm == 'histogram':
            return self._calculate_histogram_similarity(img1, img2)
        else:
            return self._calculate_ssim(img1, img2)
    
    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Strukturální podobnost (SSIM)"""
        try:
            from skimage.metrics import structural_similarity
            if len(img1.shape) == 3:
                # Pro barevné obrázky
                win_size = min(img1.shape[0], img1.shape[1], 7) // 2 * 2 + 1
                if win_size < 3:
                    win_size = 3
                ssim = structural_similarity(img1, img2, win_size=win_size, channel_axis=2)
            else:
                # Pro černobílé obrázky
                win_size = min(img1.shape[0], img1.shape[1], 7) // 2 * 2 + 1
                if win_size < 3:
                    win_size = 3
                ssim = structural_similarity(img1, img2, win_size=win_size)
            return ssim
        except Exception as e:
            logger.error(f"Chyba výpočtu SSIM: {e}")
            return 0.0
    
    def _calculate_mse(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Mean Squared Error"""
        try:
            diff = img1.astype(np.float32) - img2.astype(np.float32)
            mse = np.mean(diff ** 2)
            # Převod MSE na podobnost (0-1)
            max_possible_mse = 255.0 ** 2 * 3 if len(img1.shape) == 3 else 255.0 ** 2
            similarity = 1.0 - (mse / max_possible_mse)
            return max(0.0, similarity)
        except Exception as e:
            logger.error(f"Chyba výpočtu MSE: {e}")
            return 0.0
    
    def _calculate_histogram_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Porovnání histogramů"""
        try:
            hist1 = cv2.calcHist([img1], [0, 1, 2] if len(img1.shape) == 3 else [0], None, [50, 50, 50] if len(img1.shape) == 3 else [50], [0, 256, 0, 256, 0, 256] if len(img1.shape) == 3 else [0, 256])
            hist2 = cv2.calcHist([img2], [0, 1, 2] if len(img2.shape) == 3 else [0], None, [50, 50, 50] if len(img2.shape) == 3 else [50], [0, 256, 0, 256, 0, 256] if len(img2.shape) == 3 else [0, 256])
            
            cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            
            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            return max(0.0, similarity)
        except Exception as e:
            logger.error(f"Chyba výpočtu histogramu: {e}")
            return 0.0
    
    def detect_changes(self, img1: np.ndarray, img2: np.ndarray) -> List[VisualChange]:
        """Detekce vizuálních změn mezi obrázky"""
        changes = []
        
        try:
            # Výpočet rozdílu
            diff = cv2.absdiff(img1, img2)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) if len(diff.shape) == 3 else diff
            
            # Aplikace prahu
            _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
            
            # Morfologické operace pro odstranění šumu
            kernel = np.ones((3, 3), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Nalezení kontur
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            change_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.config.min_change_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    change_regions.append((x, y, x + w, y + h, area))
            
            # Klastrování blízkých změn
            if change_regions:
                clustered_changes = self._cluster_changes(change_regions)
                changes = self._analyze_changes(img1, img2, clustered_changes)
            
        except Exception as e:
            logger.error(f"Chyba detekce změn: {e}")
        
        return changes
    
    def _cluster_changes(self, changes: List[Tuple[int, int, int, int, int]]) -> List[Tuple[int, int, int, int, int]]:
        """Klastrování blízkých změn pomocí DBSCAN"""
        if not changes:
            return []
        
        # Příprava dat pro klastrování (centroidy obdélníků)
        points = []
        for change in changes:
            x1, y1, x2, y2, area = change
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            points.append([cx, cy])
        
        # Aplikace DBSCAN klastrování
        clustering = DBSCAN(eps=self.config.cluster_eps, min_samples=self.config.cluster_min_samples)
        labels = clustering.fit_predict(points)
        
        # Sloučení změn ve stejných clusterech
        clustered_changes = []
        unique_labels = set(labels)
        
        for label in unique_labels:
            if label == -1:  # Hlukové body
                # Zachovat jednotlivé změny
                for i, l in enumerate(labels):
                    if l == -1:
                        clustered_changes.append(changes[i])
            else:
                # Sloučit změny v clusteru
                cluster_changes = [changes[i] for i, l in enumerate(labels) if l == label]
                
                # Najít společný obdélník
                min_x = min(c[0] for c in cluster_changes)
                min_y = min(c[1] for c in cluster_changes)
                max_x = max(c[2] for c in cluster_changes)
                max_y = max(c[3] for c in cluster_changes)
                total_area = sum(c[4] for c in cluster_changes)
                
                clustered_changes.append((min_x, min_y, max_x, max_y, total_area))
        
        return clustered_changes
    
    def _analyze_changes(self, img1: np.ndarray, img2: np.ndarray, changes: List[Tuple[int, int, int, int, int]]) -> List[VisualChange]:
        """Analýza detekovaných změn"""
        visual_changes = []
        
        for i, (x1, y1, x2, y2, area) in enumerate(changes):
            try:
                # Výřez oblasti ze starého a nového obrázku
                old_region = img1[y1:y2, x1:x2]
                new_region = img2[y1:y2, x1:x2]
                
                # Výpočet podobnosti v rámci oblasti
                similarity = self.calculate_similarity(old_region, new_region)
                confidence = 1.0 - similarity
                
                # Určení typu změny
                change_type = self._classify_change(old_region, new_region)
                
                # OCR analýza textu
                text_content = self._extract_text(new_region) if self.config.enable_ocr else None
                
                # Detekce typu elementu pomocí ML
                element_type = self._identify_element(new_region) if self.config.enable_ml else None
                
                # Generování popisu změny
                description = self._generate_change_description(old_region, new_region, change_type, text_content, element_type)
                
                change = VisualChange(
                    change_id=f"change_{int(time.time())}_{i}",
                    timestamp=datetime.now(),
                    change_type=change_type,
                    confidence=confidence,
                    coordinates=(x1, y1, x2, y2),
                    area=area,
                    similarity_score=similarity,
                    description=description,
                    text_content=text_content,
                    element_type=element_type
                )
                
                visual_changes.append(change)
                
            except Exception as e:
                logger.error(f"Chyba analýzy změny {i}: {e}")
        
        return visual_changes

    def _extract_text(self, region: np.ndarray) -> Optional[str]:
        """Extrakce textu z oblasti pomocí OCR"""
        if not self.ocr_engine:
            return None
        
        try:
            # EasyOCR očekává BGR nebo RGB obrázek
            result = self.ocr_engine.readtext(region)
            
            # Spojení nalezeného textu
            text = " ".join([item[1] for item in result])
            return text if text else None
            
        except Exception as e:
            logger.warning(f"Chyba OCR extrakce: {e}")
            return None

    def _identify_element(self, region: np.ndarray) -> Optional[str]:
        """Identifikace typu elementu pomocí ML"""
        if not self.model:
            return None
            
        try:
            # Konverze pro YOLO (očekává RGB)
            img_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
            
            # Detekce
            results = self.model(img_rgb)
            
            # Získání nejpravděpodobnější třídy
            df = results.pandas().xyxy[0]
            if not df.empty:
                # Vrátí název třídy s nejvyšším skóre
                best_match = df.iloc[0]
                return f"{best_match['name']} ({best_match['confidence']:.2f})"
            
            return None
            
        except Exception as e:
            logger.warning(f"Chyba ML identifikace: {e}")
            return None

    
    def _classify_change(self, old_region: np.ndarray, new_region: np.ndarray) -> str:
        """Klasifikace typu změny"""
        try:
            # Jednoduchá klasifikace na základě obsahu
            old_mean = np.mean(old_region)
            new_mean = np.mean(new_region)
            
            if old_mean < 10 and new_mean > 50:  # Tmavý -> Světlý
                return 'added'
            elif old_mean > 50 and new_mean < 10:  # Světlý -> Tmavý
                return 'removed'
            else:
                # Detekce pohybu pomocí optického toku
                if self._detect_movement(old_region, new_region):
                    return 'moved'
                else:
                    return 'modified'
        except Exception:
            return 'modified'
    
    def _detect_movement(self, old_region: np.ndarray, new_region: np.ndarray) -> bool:
        """Detekce pohybu pomocí optického toku"""
        try:
            if len(old_region.shape) == 3:
                old_gray = cv2.cvtColor(old_region, cv2.COLOR_BGR2GRAY)
                new_gray = cv2.cvtColor(new_region, cv2.COLOR_BGR2GRAY)
            else:
                old_gray = old_region
                new_gray = new_region
            
            # Výpočet optického toku
            flow = cv2.calcOpticalFlowFarneback(
                old_gray, new_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            
            # Analýza toku
            magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            mean_magnitude = np.mean(magnitude)
            
            return mean_magnitude > 2.0  # Práh pro detekci pohybu
        except Exception:
            return False
    
    def _generate_change_description(self, old_region: np.ndarray, new_region: np.ndarray, change_type: str, text_content: Optional[str] = None, element_type: Optional[str] = None) -> str:
        """Generování popisu změny"""
        try:
            height, width = old_region.shape[:2]
            desc_parts = []
            
            if change_type == 'added':
                desc_parts.append(f"Přidán nový obsah ({width}x{height}px)")
            elif change_type == 'removed':
                desc_parts.append(f"Odstraněn obsah ({width}x{height}px)")
            elif change_type == 'moved':
                desc_parts.append(f"Přesunut obsah ({width}x{height}px)")
            else:
                desc_parts.append(f"Změněn obsah ({width}x{height}px)")
            
            if element_type:
                desc_parts.append(f"Typ: {element_type}")
                
            if text_content:
                # Zkrácení textu pokud je příliš dlouhý
                preview = text_content[:50] + "..." if len(text_content) > 50 else text_content
                desc_parts.append(f"Text: '{preview}'")
                
            return " | ".join(desc_parts)
        except Exception:
            return f"Detekována změna typu {change_type}"

class MemoryTracker:
    """Sledování využití paměti skenerem"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
    
    def get_current_usage(self) -> int:
        """Získání aktuálního využití paměti"""
        return self.process.memory_info().rss - self.initial_memory
    
    def is_within_limit(self, limit_mb: int) -> bool:
        """Kontrola, zda je využití paměti v limitu"""
        current_mb = self.get_current_usage() / (1024 * 1024)
        return current_mb <= limit_mb

class ScreenshotCapture:
    """Zachytávání screenshotů"""
    
    def __init__(self, config: ScannerConfig):
        self.config = config
        self.last_screenshot = None
        self.capture_count = 0
    
    async def capture_screenshot(self) -> Optional[np.ndarray]:
        """Zachycení screenshotu obrazovky"""
        try:
            # Pro multiplatformní podporu použijeme různé knihovny
            if self._is_windows():
                return await self._capture_windows()
            elif self._is_linux():
                return await self._capture_linux()
            elif self._is_macos():
                return await self._capture_macos()
            else:
                logger.error("Nepodporovaný operační systém")
                return None
        except Exception as e:
            logger.error(f"Chyba zachytávání screenshotu: {e}")
            return None
    
    def _is_windows(self) -> bool:
        """Kontrola Windows systému"""
        import platform
        return platform.system() == 'Windows'
    
    def _is_linux(self) -> bool:
        """Kontrola Linux systému"""
        import platform
        return platform.system() == 'Linux'
    
    def _is_macos(self) -> bool:
        """Kontrola macOS systému"""
        import platform
        return platform.system() == 'Darwin'
    
    async def _capture_windows(self) -> Optional[np.ndarray]:
        """Zachycení screenshotu na Windows"""
        try:
            import win32gui
            import win32ui
            import win32con
            from PIL import ImageGrab
            
            # Použití PIL ImageGrab pro Windows
            screenshot = ImageGrab.grab()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except ImportError:
            logger.warning("Win32 moduly nejsou k dispozici, používám náhradní metodu")
            return await self._capture_fallback()
        except Exception as e:
            logger.error(f"Chyba Windows screenshotu: {e}")
            return None
    
    async def _capture_linux(self) -> Optional[np.ndarray]:
        """Zachycení screenshotu na Linux"""
        try:
            import subprocess
            
            # Použití scrot nebo gnome-screenshot
            result = subprocess.run(['scrot', '-'], capture_output=True, check=True)
            image = Image.open(BytesIO(result.stdout))
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                result = subprocess.run(['gnome-screenshot', '-f', '-'], capture_output=True, check=True)
                image = Image.open(BytesIO(result.stdout))
                return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            except Exception as e:
                logger.error(f"Chyba Linux screenshotu: {e}")
                return await self._capture_fallback()
    
    async def _capture_macos(self) -> Optional[np.ndarray]:
        """Zachycení screenshotu na macOS"""
        try:
            import subprocess
            
            # Použití screencapture
            result = subprocess.run(['screencapture', '-x', '-'], capture_output=True, check=True)
            image = Image.open(BytesIO(result.stdout))
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"Chyba macOS screenshotu: {e}")
            return await self._capture_fallback()
    
    async def _capture_fallback(self) -> Optional[np.ndarray]:
        """Záložní metoda pro zachycení screenshotu"""
        try:
            # Pokus o použití PyAutoGUI
            import pyautogui
            screenshot = pyautogui.screenshot()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except ImportError:
            logger.error("PyAutoGUI není k dispozici")
            return None
        except Exception as e:
            logger.error(f"Chyba fallback screenshotu: {e}")
            return None

class AdvancedScanner:
    """Hlavní třída Advanced Scanner s Computer Vision fallback"""
    
    def __init__(self, config: Optional[ScannerConfig] = None, redis_client: Optional[redis.Redis] = None):
        self.config = config or ScannerConfig()
        self.redis_client = redis_client
        self.cv_engine = ComputerVisionEngine(self.config)
        self.screenshot_capture = ScreenshotCapture(self.config)
        self.memory_tracker = MemoryTracker()
        self.processing_queue = Queue(maxsize=self.config.max_queue_size)
        self.is_running = False
        self.scanner_thread = None
        self.change_history = []
        self.last_screenshot = None
        self.screenshot_count = 0
        
        # Inicializace uložiště
        self.storage_path = Path("scanner_storage")
        self.storage_path.mkdir(exist_ok=True)
        self.screenshots_path = self.storage_path / "screenshots"
        self.diffs_path = self.storage_path / "diffs"
        self.screenshots_path.mkdir(exist_ok=True)
        self.diffs_path.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Inicializace skeneru"""
        try:
            await self.cv_engine.initialize()
            logger.info("Advanced Scanner inicializován úspěšně")
            
            # Inicializace Redis pub/sub pro notifikace
            if self.redis_client:
                await self._setup_redis_pubsub()
            
        except Exception as e:
            logger.error(f"Chyba inicializace skeneru: {e}")
            raise
    
    async def _setup_redis_pubsub(self):
        """Nastavení Redis pub/sub pro notifikace"""
        try:
            # Vytvoření pub/sub kanálů
            self.change_channel = "scanner:changes"
            self.status_channel = "scanner:status"
            
            logger.info("Redis pub/sub nastaven úspěšně")
        except Exception as e:
            logger.warning(f"Chyba nastavení Redis pub/sub: {e}")
    
    async def start_scanning(self, target_url: Optional[str] = None):
        """Spuštění skenování"""
        if self.is_running:
            logger.warning("Skener již běží")
            return
        
        self.is_running = True
        logger.info("Spouštím Advanced Scanner")
        
        # Spuštění hlavní smyčky skenování
        self.scanner_thread = threading.Thread(target=self._scanning_loop, args=(target_url,))
        self.scanner_thread.daemon = True
        self.scanner_thread.start()
        
        # Notifikace o spuštění
        await self._publish_status("started")
    
    async def stop_scanning(self):
        """Zastavení skenování"""
        if not self.is_running:
            logger.warning("Skener již není spuštěn")
            return
        
        self.is_running = False
        logger.info("Zastavuji Advanced Scanner")
        
        if self.scanner_thread:
            self.scanner_thread.join(timeout=10)
        
        # Notifikace o zastavení
        await self._publish_status("stopped")
    
    def _scanning_loop(self, target_url: Optional[str] = None):
        """Hlavní smyčka skenování"""
        logger.info("Skenovací smyčka spuštěna")
        
        while self.is_running:
            try:
                start_time = time.time()
                
                # Kontrola limitu paměti
                if not self.memory_tracker.is_within_limit(self.config.memory_limit_mb):
                    logger.warning(f"Překročen limit paměti ({self.config.memory_limit_mb}MB)")
                    self._cleanup_memory()
                
                # Zachycení screenshotu
                screenshot = asyncio.run(self.screenshot_capture.capture_screenshot())
                if screenshot is None:
                    logger.error("Nepodařilo se zachytit screenshot")
                    time.sleep(self.config.screenshot_interval)
                    continue
                
                # Zpracování screenshotu
                changes = self._process_screenshot(screenshot)
                
                # Uložení změn
                if changes:
                    asyncio.run(self._save_changes(changes))
                    asyncio.run(self._notify_changes(changes))
                
                # Aktualizace metrik
                SCANNER_OPERATIONS.labels(type='screenshot', status='success').inc()
                SCANNER_LATENCY.labels(type='screenshot').observe(time.time() - start_time)
                SCANNER_MEMORY_USAGE.set(self.memory_tracker.get_current_usage())
                SCANNER_QUEUE_SIZE.set(self.processing_queue.qsize())
                
                # Čekání na další cyklus
                time.sleep(self.config.screenshot_interval)
                
            except Exception as e:
                logger.error(f"Chyba ve skenovací smyčce: {e}")
                SCANNER_OPERATIONS.labels(type='screenshot', status='error').inc()
                time.sleep(self.config.screenshot_interval)
        
        logger.info("Skenovací smyčka ukončena")
    
    def _process_screenshot(self, screenshot: np.ndarray) -> List[VisualChange]:
        """Zpracování screenshotu a detekce změn"""
        try:
            # Porovnání s předchozím screenshotem
            if self.last_screenshot is not None:
                changes = self.cv_engine.detect_changes(self.last_screenshot, screenshot)
                
                # Filtrování změn podle prahu
                significant_changes = [
                    change for change in changes 
                    if change.confidence > (1.0 - self.config.change_threshold)
                ]
                
                # Uložení aktuálního screenshotu
                self.last_screenshot = screenshot.copy()
                self.screenshot_count += 1
                
                return significant_changes
            else:
                # První screenshot
                self.last_screenshot = screenshot.copy()
                self.screenshot_count += 1
                return []
                
        except Exception as e:
            logger.error(f"Chyba zpracování screenshotu: {e}")
            return []
    
    def _cleanup_memory(self):
        """Vyčištění paměti"""
        try:
            # Odstranění starých screenshotů z paměti
            if len(self.change_history) > 100:
                self.change_history = self.change_history[-50:]
            
            # Garbage collection
            import gc
            gc.collect()
            
            logger.info("Paměť vyčištěna")
        except Exception as e:
            logger.error(f"Chyba čištění paměti: {e}")
    
    async def _save_changes(self, changes: List[VisualChange]):
        """Uložení detekovaných změn"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i, change in enumerate(changes):
                # Uložení screenshotu s vyznačenou změnou
                screenshot_path = self.screenshots_path / f"screenshot_{timestamp}_{i}.png"
                diff_path = self.diffs_path / f"diff_{timestamp}_{i}.png"
                
                # Vytvoření obrázku s vyznačenou změnou
                if self.last_screenshot is not None:
                    annotated_screenshot = self._annotate_screenshot(self.last_screenshot, change)
                    cv2.imwrite(str(screenshot_path), annotated_screenshot)
                    
                    # Uložení diff obrázku
                    diff_image = self._create_diff_image(change)
                    if diff_image is not None:
                        cv2.imwrite(str(diff_path), diff_image)
                
                # Aktualizace cest v objektu změny
                change.screenshot_path = str(screenshot_path)
                change.diff_image_path = str(diff_path)
                
                # Přidání do historie
                self.change_history.append(change)
            
            logger.info(f"Uloženo {len(changes)} změn")
            
        except Exception as e:
            logger.error(f"Chyba ukládání změn: {e}")
    
    def _annotate_screenshot(self, screenshot: np.ndarray, change: VisualChange) -> np.ndarray:
        """Anotace screenshotu s vyznačenou změnou"""
        try:
            annotated = screenshot.copy()
            x1, y1, x2, y2 = change.coordinates
            
            # Vykreslení obdélníku kolem změny
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Přidání popisku
            label = f"{change.change_type} ({change.confidence:.2f})"
            cv2.putText(annotated, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            return annotated
        except Exception as e:
            logger.error(f"Chyba anotace screenshotu: {e}")
            return screenshot
    
    def _create_diff_image(self, change: VisualChange) -> Optional[np.ndarray]:
        """Vytvoření diff obrázku"""
        try:
            # Tato metoda by měla být rozšířena podle konkrétních potřeb
            # Nyní vracíme prázdný obrázek pro demonstraci
            return np.zeros((100, 100, 3), dtype=np.uint8)
        except Exception as e:
            logger.error(f"Chyba vytvoření diff obrázku: {e}")
            return None
    
    async def _notify_changes(self, changes: List[VisualChange]):
        """Notifikace o detekovaných změnách"""
        try:
            if self.redis_client:
                for change in changes:
                    change_data = {
                        'change_id': change.change_id,
                        'timestamp': change.timestamp.isoformat(),
                        'change_type': change.change_type,
                        'confidence': change.confidence,
                        'coordinates': change.coordinates,
                        'area': change.area,
                        'description': change.description,
                        'screenshot_path': change.screenshot_path,
                        'diff_image_path': change.diff_image_path
                    }
                    
                    await self.redis_client.publish(self.change_channel, json.dumps(change_data))
            
            logger.info(f"Notifikováno {len(changes)} změn")
            
        except Exception as e:
            logger.error(f"Chyba notifikace změn: {e}")
    
    async def _publish_status(self, status: str):
        """Publikace statusu skeneru"""
        try:
            if self.redis_client:
                status_data = {
                    'scanner_id': 'advanced_scanner',
                    'status': status,
                    'timestamp': datetime.now().isoformat(),
                    'screenshot_count': self.screenshot_count,
                    'changes_detected': len(self.change_history),
                    'memory_usage': self.memory_tracker.get_current_usage()
                }
                
                await self.redis_client.publish(self.status_channel, json.dumps(status_data))
            
        except Exception as e:
            logger.error(f"Chyba publikace statusu: {e}")
    
    async def get_change_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Získání historie změn"""
        try:
            recent_changes = self.change_history[-limit:]
            
            history = []
            for change in recent_changes:
                history.append({
                    'change_id': change.change_id,
                    'timestamp': change.timestamp.isoformat(),
                    'change_type': change.change_type,
                    'confidence': change.confidence,
                    'coordinates': change.coordinates,
                    'area': change.area,
                    'description': change.description,
                    'text_content': change.text_content,
                    'element_type': change.element_type,
                    'screenshot_path': change.screenshot_path,
                    'diff_image_path': change.diff_image_path
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Chyba získání historie: {e}")
            return []
    
    async def get_scanner_status(self) -> Dict[str, Any]:
        """Získání statusu skeneru"""
        try:
            return {
                'is_running': self.is_running,
                'screenshot_count': self.screenshot_count,
                'changes_detected': len(self.change_history),
                'memory_usage': self.memory_tracker.get_current_usage(),
                'queue_size': self.processing_queue.qsize(),
                'config': {
                    'screenshot_interval': self.config.screenshot_interval,
                    'change_threshold': self.config.change_threshold,
                    'enable_gpu': self.config.enable_gpu,
                    'enable_ocr': self.config.enable_ocr,
                    'enable_ml': self.config.enable_ml,
                    'memory_limit_mb': self.config.memory_limit_mb
                }
            }
        except Exception as e:
            logger.error(f"Chyba získání statusu: {e}")
            return {}
    
    def find_element_by_template(self, template: np.ndarray, threshold: float = 0.8) -> List[Tuple[int, int, int, int, float]]:
        """
        Nalezení elementu na aktuální obrazovce pomocí template matching
        Vrací seznam (x1, y1, x2, y2, score)
        """
        try:
            if self.last_screenshot is None:
                # Pokud nemáme screenshot, zkusíme ho pořídit
                screenshot = asyncio.run(self.screenshot_capture.capture_screenshot())
                if screenshot is None:
                    return []
                self.last_screenshot = screenshot

            screenshot = self.last_screenshot
            
            # Konverze na šedotón pro template matching
            if len(screenshot.shape) == 3:
                img_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            else:
                img_gray = screenshot
                
            if len(template.shape) == 3:
                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            else:
                template_gray = template
                
            w, h = template_gray.shape[::-1]
            
            # Template matching
            res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            
            matches = []
            for pt in zip(*loc[::-1]):
                matches.append((int(pt[0]), int(pt[1]), int(pt[0] + w), int(pt[1] + h), float(res[pt[1], pt[0]])))
                
            # Non-maximum suppression (odstranění překrývajících se detekcí)
            # Pro jednoduchost vrátíme všechny nad prahem, seřazené podle skóre
            matches.sort(key=lambda x: x[4], reverse=True)
            
            return matches
            
        except Exception as e:
            logger.error(f"Chyba při hledání templatu: {e}")
            return []

    async def cleanup(self):
        """Vyčištění zdrojů"""
        try:
            await self.stop_scanning()
            
            # Vyčištění souborů
            if self.storage_path.exists():
                import shutil
                shutil.rmtree(self.storage_path)
            
            logger.info("Advanced Scanner vyčištěn")
            
        except Exception as e:
            logger.error(f"Chyba čištění skeneru: {e}")

# Pomocné funkce
def create_default_scanner(redis_client: Optional[redis.Redis] = None) -> AdvancedScanner:
    """Vytvoření výchozí instance Advanced Scanner"""
    config = ScannerConfig()
    return AdvancedScanner(config, redis_client)

async def demo_scanner():
    """Demo funkce pro testování skeneru"""
    try:
        # Vytvoření skeneru
        scanner = create_default_scanner()
        await scanner.initialize()
        
        # Spuštění skenování
        await scanner.start_scanning()
        
        print("Advanced Scanner běží - stiskněte Ctrl+C pro zastavení")
        
        # Čekání na uživatelské přerušení
        try:
            while True:
                await asyncio.sleep(1)
                status = await scanner.get_scanner_status()
                print(f"Status: {status}")
        except KeyboardInterrupt:
            print("\nZastavuji skener...")
        
        # Zastavení skeneru
        await scanner.stop_scanning()
        await scanner.cleanup()
        
        print("Demo ukončeno")
        
    except Exception as e:
        logger.error(f"Chyba demo skeneru: {e}")

if __name__ == "__main__":
    # Spuštění demo
    asyncio.run(demo_scanner())