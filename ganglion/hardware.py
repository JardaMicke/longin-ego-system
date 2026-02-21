from __future__ import annotations

import socket
from typing import Dict, Optional
import importlib


def read_hardware_profile() -> Dict[str, object]:
    hostname = socket.gethostname()
    gpu_model, vram_free_mb = _read_gpu_info()
    return {
        "hostname": hostname,
        "gpu_model": gpu_model,
        "vram_free": vram_free_mb,
        "local_llm_ready": bool(gpu_model and vram_free_mb > 0),
    }


def _read_gpu_info() -> tuple[Optional[str], int]:
    try:
        pynvml = importlib.import_module("pynvml")
    except Exception:
        return None, 0
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        name = pynvml.nvmlDeviceGetName(handle)
        memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
        vram_free_mb = int(memory.free / 1024 / 1024)
        if isinstance(name, bytes):
            name = name.decode(errors="ignore")
        return str(name), vram_free_mb
    except Exception:
        return None, 0
    finally:
        try:
            pynvml.nvmlShutdown()
        except Exception:
            pass
