from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ResourceProfile:
    """Účel: Deklaruje nároky sentinelu na zdroje.

    Vstupy/Výstupy: memory_gb, cpu_cores a tags jako profil.
    Vedlejší efekty: Žádné.
    """
    memory_gb: float
    cpu_cores: float
    tags: List[str]


class ILonginSentinel(ABC):
    """Účel: Rozhraní pro sentinel moduly v SDK.

    Vstupy/Výstupy: Definuje sentinel_scan a get_resource_requirements.
    Vedlejší efekty: Závisí na implementaci.
    """
    @abstractmethod
    def sentinel_scan(self, envelope_headers: Dict[str, str]) -> bool:
        raise NotImplementedError("sentinel_scan must be implemented")

    @abstractmethod
    def get_resource_requirements(self) -> ResourceProfile:
        raise NotImplementedError("get_resource_requirements must be implemented")
