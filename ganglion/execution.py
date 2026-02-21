from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from typing import Dict, Optional

from kernel.security.container_manager import ContainerLimits, ContainerManager


@dataclass
class ExecutionResult:
    """Účel: Nese výsledek provedení příkazu.

    Vstupy/Výstupy: exit_code a output jako výstupní atributy.
    Vedlejší efekty: Žádné.
    """
    exit_code: int
    output: str


class SandboxExecutor:
    """Účel: Spouští příkazy v izolovaném Docker kontejneru.

    Vstupy/Výstupy: Přijímá command a env_vars, vrací ExecutionResult.
    Vedlejší efekty: Spouští a ukončuje kontejnery.
    """
    def __init__(
        self,
        image: str = "python:3.11-alpine",
        timeout_seconds: int = 120,
        limits: Optional[ContainerLimits] = None,
        manager: Optional[ContainerManager] = None,
    ) -> None:
        self._image = image
        self._timeout_seconds = timeout_seconds
        self._limits = limits or ContainerLimits()
        self._manager = manager or ContainerManager()

    def execute(self, command: str, env_vars: Optional[Dict[str, str]] = None) -> ExecutionResult:
        try:
            entry = f"sh -c {shlex.quote(command)}"
            container_id = self._manager.run_container(
                image=self._image,
                command=entry,
                limits=self._limits,
                env=env_vars,
            )
            try:
                status = self._manager.wait_container(container_id, timeout=self._timeout_seconds)
                output = self._manager.get_logs(container_id)
            finally:
                self._manager.stop_container(container_id)
            return ExecutionResult(exit_code=status, output=output)
        except Exception as exc:
            raise RuntimeError(f"Sandbox execution failed: {exc}") from exc


class LocalExecutor:
    """Účel: Spouští příkazy lokálně přes subprocess.

    Vstupy/Výstupy: Přijímá command a env_vars, vrací ExecutionResult.
    Vedlejší efekty: Spouští lokální procesy.
    """
    def __init__(self, timeout_seconds: int = 120) -> None:
        self._timeout_seconds = timeout_seconds

    def execute(self, command: str, env_vars: Optional[Dict[str, str]] = None) -> ExecutionResult:
        try:
            completed = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                env=env_vars,
            )
            output = (completed.stdout or "") + (completed.stderr or "")
            return ExecutionResult(exit_code=completed.returncode, output=output)
        except Exception as exc:
            raise RuntimeError(f"Local execution failed: {exc}") from exc
