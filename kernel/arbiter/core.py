from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import importlib


@dataclass(frozen=True)
class ResourceSnapshot:
    """Účel: Reprezentuje aktuální stav systémových zdrojů.

    Vstupy/Výstupy: available_gb, total_gb, gpu_temp_c uložené jako atributy instance.
    Vedlejší efekty: Žádné.
    """
    available_gb: float
    total_gb: float
    gpu_temp_c: Optional[float]


@dataclass(frozen=True)
class ArbiterPolicy:
    """Účel: Konfigurace minimálních bezpečnostních limitů zdrojů.

    Vstupy/Výstupy: min_free_gb a max_gpu_temp_c jako konfigurační hodnoty.
    Vedlejší efekty: Žádné.
    """
    min_free_gb: float = 4.0
    max_gpu_temp_c: float = 80.0


class Arbiter:
    """Účel: Ověřuje, zda systémové zdroje splňují bezpečnostní limity.

    Vstupy/Výstupy: Vstupem je ArbiterPolicy, výstupem snapshoty a boolean kontrola zdrojů.
    Vedlejší efekty: Čte systémové metriky přes psutil a volitelně NVML.
    """
    def __init__(self, policy: ArbiterPolicy) -> None:
        self._policy = policy

    def snapshot(self) -> ResourceSnapshot:
        try:
            import psutil
        except Exception as exc:
            raise RuntimeError(f"psutil import failed: {exc}") from exc
        try:
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024**3)
            total_gb = mem.total / (1024**3)
            gpu_temp = self._read_gpu_temp()
            return ResourceSnapshot(available_gb=available_gb, total_gb=total_gb, gpu_temp_c=gpu_temp)
        except Exception as exc:
            raise RuntimeError(f"Resource snapshot failed: {exc}") from exc

    def check_resources(self) -> bool:
        snapshot = self.snapshot()
        if snapshot.available_gb < self._policy.min_free_gb:
            return False
        if snapshot.gpu_temp_c is not None and snapshot.gpu_temp_c > self._policy.max_gpu_temp_c:
            return False
        return True

    def _read_gpu_temp(self) -> Optional[float]:
        try:
            pynvml = importlib.import_module("pynvml")
        except Exception:
            return None
        try:
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            temp = float(pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU))
            pynvml.nvmlShutdown()
            return temp
        except Exception:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass
            return None
