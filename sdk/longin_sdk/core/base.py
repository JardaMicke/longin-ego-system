from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from longin_sdk.core.sentinel import ILonginSentinel, ResourceProfile
from longin_sdk.tools.fs import SafeFileSystem
from longin_sdk.tools.memory import MemoryClient
from longin_sdk.tools.net import SafeHttpClient


@dataclass(frozen=True)
class ModuleConfig:
    """Účel: Konfigurace pro LonginModule.

    Vstupy/Výstupy: workspace_root jako základ pro SafeFileSystem.
    Vedlejší efekty: Žádné.
    """
    workspace_root: str


class LonginModule(ILonginSentinel):
    """Účel: Základní modul poskytující SDK nástroje a sentinel rozhraní.

    Vstupy/Výstupy: Přijímá konfiguraci a poskytuje fs/net/memory utility.
    Vedlejší efekty: Inicializuje klienty SDK.
    """
    def __init__(self, config: ModuleConfig) -> None:
        self._config = config
        self.fs = SafeFileSystem(config.workspace_root)
        self.net = SafeHttpClient()
        self.memory = MemoryClient()

    def sentinel_scan(self, envelope_headers: Mapping[str, object]) -> bool:
        return False

    def get_resource_requirements(self) -> ResourceProfile:
        return ResourceProfile(memory_gb=0.1, cpu_cores=0.1, tags=[])
