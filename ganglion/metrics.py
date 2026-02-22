from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Dict, Optional


@dataclass
class MetricsState:
    start_time: float = field(default_factory=time.monotonic)
    request_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    per_route: Dict[str, int] = field(default_factory=dict)
    status_codes: Dict[int, int] = field(default_factory=dict)

    def record_request(self, route: str, status_code: int, error: Optional[str]) -> None:
        self.request_count += 1
        self.per_route[route] = self.per_route.get(route, 0) + 1
        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
        if status_code >= 500 or error:
            self.error_count += 1
            self.last_error = error or f"status={status_code}"

    def snapshot(self) -> Dict[str, object]:
        return {
            "uptime_seconds": time.monotonic() - self.start_time,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "per_route": dict(self.per_route),
            "status_codes": dict(self.status_codes),
        }
