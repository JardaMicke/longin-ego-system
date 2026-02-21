from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, cast


@dataclass(frozen=True)
class ContainerLimits:
    """Účel: Konfiguruje limity pro kontejnery v sandboxu.

    Vstupy/Výstupy: Limity paměti a CPU pro docker run.
    Vedlejší efekty: Žádné.
    """
    mem_limit: str = "512m"
    cpu_quota: int = 50000
    cpu_period: int = 100000


class ContainerManager:
    """Účel: Spravuje Docker kontejnery pro izolovaný běh kódu.

    Vstupy/Výstupy: Přijímá parametry pro kontejnery, vrací ID a výstupy/logy.
    Vedlejší efekty: Spouští a zastavuje Docker kontejnery přes Docker SDK.
    """
    def __init__(self) -> None:
        self._client: Any | None = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            import docker
        except Exception as exc:
            raise RuntimeError(f"Docker SDK import failed: {exc}") from exc
        try:
            self._client = docker.from_env()
            return cast(Any, self._client)
        except Exception as exc:
            raise RuntimeError(f"Docker client init failed: {exc}") from exc

    def run_container(
        self,
        image: str,
        command: str,
        limits: Optional[ContainerLimits] = None,
        env: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> str:
        limits = limits or ContainerLimits()
        try:
            client = self._get_client()
            container = client.containers.run(
                image=image,
                command=command,
                detach=True,
                mem_limit=limits.mem_limit,
                cpu_quota=limits.cpu_quota,
                cpu_period=limits.cpu_period,
                network_mode="none",
                environment=env or {},
                volumes=volumes or {},
            )
            return cast(str, container.id)
        except Exception as exc:
            raise RuntimeError(f"Container run failed for image {image}: {exc}") from exc

    def stop_container(self, container_id: str) -> None:
        try:
            client = self._get_client()
            container = client.containers.get(container_id)
            container.stop(timeout=5)
            container.remove(force=True)
        except Exception as exc:
            raise RuntimeError(f"Container stop failed for {container_id}: {exc}") from exc

    def get_logs(self, container_id: str) -> str:
        try:
            client = self._get_client()
            container = client.containers.get(container_id)
            logs = cast(bytes, container.logs(stdout=True, stderr=True))
            return logs.decode("utf-8", errors="replace")
        except Exception as exc:
            raise RuntimeError(f"Container logs failed for {container_id}: {exc}") from exc

    def wait_container(self, container_id: str, timeout: int = 60) -> int:
        try:
            client = self._get_client()
            container = client.containers.get(container_id)
            result = container.wait(timeout=timeout)
            status_code = int(result.get("StatusCode", 1))
            return status_code
        except Exception as exc:
            raise RuntimeError(f"Container wait failed for {container_id}: {exc}") from exc
