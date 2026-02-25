"""
GPU Scheduler pro LONGIN EGO
Implementuje Single-GPU-Lock pro efektivní využití RTX 3060 12GB
"""

import threading
import asyncio
import logging
import time
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
from enum import Enum
import queue

logger = logging.getLogger(__name__)

class GPUPriority(Enum):
    CRITICAL = 0  # System critical tasks (e.g. security scan)
    HIGH = 1      # User interaction (e.g. chat response)
    MEDIUM = 2    # Standard background tasks (e.g. memory consolidation)
    LOW = 3       # Idle tasks (e.g. dreaming)

@dataclass
class GPUTask:
    """Reprezentace GPU úlohy"""
    id: str
    priority: GPUPriority
    func: Callable
    args: tuple
    kwargs: Dict[str, Any]
    created_at: float
    future: asyncio.Future

class GPUScheduler:
    """
    Plánovač GPU úloh zajišťující exkluzivní přístup ke GPU.
    Zabraňuje OOM chybám a přehřívání.
    """
    
    def __init__(self, max_temp_c: float = 80.0):
        self.max_temp_c = max_temp_c
        self.task_queue = queue.PriorityQueue()
        self.lock = asyncio.Lock()
        self.is_running = False
        self.worker_thread = None
        self.current_task: Optional[GPUTask] = None
        self.gpu_temp = 0.0
        
        # Pynvml pro monitoring teploty
        try:
            import pynvml
            self.pynvml = pynvml
            self.pynvml.nvmlInit()
            self.gpu_handle = self.pynvml.nvmlDeviceGetHandleByIndex(0)
            self.monitoring_enabled = True
        except ImportError:
            logger.warning("pynvml not found, GPU thermal monitoring disabled")
            self.monitoring_enabled = False
        except Exception as e:
            logger.error(f"Failed to init NVML: {e}")
            self.monitoring_enabled = False
            
    def start(self):
        """Spuštění worker threadu"""
        if self.is_running:
            return
            
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("GPU Scheduler started")
        
    def stop(self):
        """Zastavení scheduleru"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
            
        if self.monitoring_enabled:
            try:
                self.pynvml.nvmlShutdown()
            except:
                pass
                
    async def submit_task(self, func: Callable, *args, priority: GPUPriority = GPUPriority.MEDIUM, **kwargs) -> Any:
        """Odeslání úlohy ke zpracování na GPU"""
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        task = GPUTask(
            id=f"gpu_task_{time.time()}",
            priority=priority,
            func=func,
            args=args,
            kwargs=kwargs,
            created_at=time.time(),
            future=future
        )
        
        # PriorityQueue řadí podle prvního prvku tuple (priority.value)
        self.task_queue.put((priority.value, task))
        logger.debug(f"GPU Task submitted: {task.id} (Priority: {priority.name})")
        
        return await future
        
    def _worker_loop(self):
        """Hlavní smyčka zpracování úloh"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.is_running:
            try:
                # Kontrola teploty před spuštěním další úlohy
                if self.monitoring_enabled:
                    self._check_thermal_status()
                    
                # Získání úlohy (blokující s timeoutem pro kontrolu is_running)
                try:
                    _, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                    
                self.current_task = task
                logger.debug(f"Processing GPU Task: {task.id}")
                
                try:
                    # Spuštění úlohy
                    if asyncio.iscoroutinefunction(task.func):
                        result = loop.run_until_complete(task.func(*task.args, **task.kwargs))
                    else:
                        result = task.func(*task.args, **task.kwargs)
                        
                    # Nastavení výsledku do future (musí být thread-safe)
                    loop.call_soon_threadsafe(task.future.set_result, result)
                    
                except Exception as e:
                    logger.error(f"Error in GPU task {task.id}: {e}")
                    loop.call_soon_threadsafe(task.future.set_exception, e)
                finally:
                    self.current_task = None
                    self.task_queue.task_done()
                    
                    # Agresivní uvolnění paměti po každé úloze
                    self._cleanup_vram()
                    
            except Exception as e:
                logger.error(f"Error in GPU worker loop: {e}")
                
    def _check_thermal_status(self):
        """Kontrola teploty a případné chlazení"""
        try:
            temp = self.pynvml.nvmlDeviceGetTemperature(self.gpu_handle, self.pynvml.NVML_TEMPERATURE_GPU)
            self.gpu_temp = float(temp)
            
            if self.gpu_temp > self.max_temp_c:
                logger.warning(f"GPU Overheating ({self.gpu_temp}°C). Throttling...")
                # Čekáme, dokud teplota neklesne
                while self.gpu_temp > (self.max_temp_c - 5.0) and self.is_running:
                    time.sleep(2.0)
                    temp = self.pynvml.nvmlDeviceGetTemperature(self.gpu_handle, self.pynvml.NVML_TEMPERATURE_GPU)
                    self.gpu_temp = float(temp)
                logger.info("GPU Cooled down. Resuming...")
        except Exception as e:
            logger.warning(f"Thermal check failed: {e}")
            
    def _cleanup_vram(self):
        """Vyčištění VRAM po úloze"""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

# Singleton instance
_scheduler: Optional[GPUScheduler] = None

def get_gpu_scheduler() -> GPUScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = GPUScheduler()
        _scheduler.start()
    return _scheduler
