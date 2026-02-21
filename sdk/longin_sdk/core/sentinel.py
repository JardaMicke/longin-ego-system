from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ResourceProfile:
    memory_gb: float
    cpu_cores: float
    tags: List[str]


class ILonginSentinel(ABC):
    @abstractmethod
    def sentinel_scan(self, envelope_headers: Dict[str, str]) -> bool:
        raise NotImplementedError("sentinel_scan must be implemented")

    @abstractmethod
    def get_resource_requirements(self) -> ResourceProfile:
        raise NotImplementedError("get_resource_requirements must be implemented")
