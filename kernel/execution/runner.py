from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from kernel.security.airlock import Airlock
from kernel.security.container_manager import ContainerLimits, ContainerManager


@dataclass(frozen=True)
class RunnerConfig:
    image: str = "python:3.11-alpine"
    command: str = "python /tmp/runner.py"
    soft_timeout_seconds: int = 60
    hard_timeout_seconds: int = 120


class SiblingRunner:
    def __init__(
        self,
        airlock: Airlock,
        container_manager: ContainerManager,
        config: RunnerConfig,
    ) -> None:
        self._airlock = airlock
        self._container_manager = container_manager
        self._config = config

    def run(self, code: str, limits: Optional[ContainerLimits] = None) -> Tuple[int, str]:
        validation = self._airlock.validate_code(code)
        if not validation.ok:
            raise RuntimeError(f"Airlock rejected code: {validation.errors}")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                script_path = Path(temp_dir) / "runner.py"
                script_path.write_text(code, encoding="utf-8")
                volumes = {str(script_path): {"bind": "/tmp/runner.py", "mode": "ro"}}
                container_id = self._container_manager.run_container(
                    image=self._config.image,
                    command=self._config.command,
                    limits=limits,
                    volumes=volumes,
                )
                try:
                    status_code = self._container_manager.wait_container(
                        container_id, timeout=self._config.soft_timeout_seconds
                    )
                except Exception as exc:
                    self._container_manager.stop_container(container_id)
                    raise RuntimeError(f"Container timeout: {exc}") from exc
                output = self._container_manager.get_logs(container_id)
                self._container_manager.stop_container(container_id)
                return status_code, output
        except Exception as exc:
            raise RuntimeError(f"Sibling run failed: {exc}") from exc
