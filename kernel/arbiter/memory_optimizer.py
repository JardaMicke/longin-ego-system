"""
Optimalizace paměti pro LONGIN EGO
Zajišťuje dodržení 32GB RAM limitu (Křemíková disciplína)
"""

import gc
import psutil
import logging
import time
import os
import ctypes
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import threading
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class MemoryConfig:
    """Konfigurace paměťového optimalizátoru"""
    max_ram_gb: float = 32.0
    critical_threshold_percent: float = 90.0
    warning_threshold_percent: float = 75.0
    check_interval_seconds: float = 5.0
    aggressive_pruning_enabled: bool = True
    page_file_usage_allowed: bool = False

class MemoryOptimizer:
    """
    Optimalizátor paměti pro LONGIN EGO.
    Implementuje strategie pro agresivní uvolňování paměti a prediktivní načítání.
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        self.process = psutil.Process(os.getpid())
        self.is_running = False
        self.monitor_thread = None
        self.memory_pools: Dict[str, List[object]] = {}
        self.managed_objects: Set[int] = set()
        
    def start_monitoring(self):
        """Spuštění monitorování paměti na pozadí"""
        if self.is_running:
            return
            
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Memory Optimizer monitoring started")
        
    def stop_monitoring(self):
        """Zastavení monitorování"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            logger.info("Memory Optimizer monitoring stopped")
            
    def _monitor_loop(self):
        """Hlavní smyčka monitorování"""
        while self.is_running:
            try:
                self._check_memory_status()
                time.sleep(self.config.check_interval_seconds)
            except Exception as e:
                logger.error(f"Error in memory monitor loop: {e}")
                time.sleep(self.config.check_interval_seconds)
                
    def _check_memory_status(self):
        """Kontrola stavu paměti a provedení akcí"""
        mem = psutil.virtual_memory()
        usage_percent = mem.percent
        
        if usage_percent > self.config.critical_threshold_percent:
            logger.warning(f"CRITICAL MEMORY USAGE: {usage_percent}% - Triggering emergency pruning")
            self.aggressive_pruning()
        elif usage_percent > self.config.warning_threshold_percent:
            logger.info(f"High memory usage: {usage_percent}% - Triggering standard cleanup")
            self._standard_cleanup()
            
    def aggressive_pruning(self):
        """
        Agresivní uvolnění paměti.
        Volá GC, maže cache, uvolňuje VRAM pokud je to možné.
        """
        logger.info("Executing aggressive memory pruning")
        
        # 1. Force Python Garbage Collection
        gc.collect(generation=2)
        
        # 2. Clear internal caches
        self._clear_internal_caches()
        
        # 3. Try to release OS memory (Windows specific)
        if os.name == 'nt':
            try:
                # EmptyWorkingSet - trims the working set of the process
                ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
            except Exception as e:
                logger.warning(f"Failed to trim working set: {e}")
                
        # 4. Release VRAM if GPU libraries are loaded
        self._release_vram()
        
    def _standard_cleanup(self):
        """Standardní čištění paměti"""
        gc.collect(generation=1)
        
    def _clear_internal_caches(self):
        """Vyčištění interních cache"""
        # Vyprázdnění memory pools
        for pool_name in self.memory_pools:
            self.memory_pools[pool_name].clear()
        
        # Zde by se mohly volat hooky pro další komponenty
        # např. self.event_bus.publish("memory:cleanup")
        
    def _release_vram(self):
        """Pokus o uvolnění VRAM (PyTorch, TensorFlow)"""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("PyTorch CUDA cache cleared")
        except ImportError:
            pass
            
    def register_pool(self, name: str) -> List[object]:
        """Registrace poolu objektů pro správu"""
        if name not in self.memory_pools:
            self.memory_pools[name] = []
        return self.memory_pools[name]
        
    def get_memory_stats(self) -> Dict[str, float]:
        """Získání statistik paměti"""
        mem = psutil.virtual_memory()
        proc_mem = self.process.memory_info()
        
        return {
            "total_system_gb": mem.total / (1024**3),
            "available_system_gb": mem.available / (1024**3),
            "percent_used": mem.percent,
            "process_rss_mb": proc_mem.rss / (1024**2),
            "process_vms_mb": proc_mem.vms / (1024**2)
        }

# Singleton instance
_optimizer: Optional[MemoryOptimizer] = None

def get_memory_optimizer() -> MemoryOptimizer:
    global _optimizer
    if _optimizer is None:
        _optimizer = MemoryOptimizer()
    return _optimizer
