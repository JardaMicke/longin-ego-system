from __future__ import annotations

from pathlib import Path

from longin_sdk.core.exceptions import PermissionError


class SafeFileSystem:
    """Účel: Bezpečné čtení a zápis souborů v rámci workspace.

    Vstupy/Výstupy: Přijímá root workspace, čte a zapisuje obsah souborů.
    Vedlejší efekty: Operace se souborovým systémem.
    """
    def __init__(self, workspace_root: str) -> None:
        self._root = Path(workspace_root).resolve()

    def _resolve(self, path: str) -> Path:
        target = (self._root / path).resolve()
        if not str(target).startswith(str(self._root)):
            raise PermissionError("Path is outside workspace root")
        return target

    def read_file(self, path: str) -> str:
        target = self._resolve(path)
        try:
            return target.read_text(encoding="utf-8")
        except Exception as exc:
            raise RuntimeError(f"Read file failed: {exc}") from exc

    def write_file(self, path: str, content: str) -> None:
        target = self._resolve(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        except Exception as exc:
            raise RuntimeError(f"Write file failed: {exc}") from exc
