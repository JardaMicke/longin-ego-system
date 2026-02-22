from __future__ import annotations

import logging
import time
from typing import Optional

_LOGGING_READY = False
_START_TIME = time.monotonic()


def configure_logging(level: str, fmt: Optional[str] = None) -> None:
    global _LOGGING_READY
    if _LOGGING_READY:
        return
    log_format = fmt or "%(asctime)s %(levelname)s %(name)s %(message)s"
    logging.basicConfig(level=level.upper(), format=log_format)
    _LOGGING_READY = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def uptime_seconds() -> float:
    return time.monotonic() - _START_TIME
