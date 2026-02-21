from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Iterable, List, Set


@dataclass(frozen=True)
class ValidationResult:
    """Účel: Výsledek validace kódu v Airlocku.

    Vstupy/Výstupy: ok a seznam chyb z validace.
    Vedlejší efekty: Žádné.
    """
    ok: bool
    errors: List[str]


@dataclass(frozen=True)
class AirlockPolicy:
    """Účel: Definuje povolené a blokované moduly.

    Vstupy/Výstupy: allowed_modules a blocked_modules jako pravidla.
    Vedlejší efekty: Žádné.
    """
    allowed_modules: Set[str]
    blocked_modules: Set[str]


class Airlock:
    """Účel: Provádí AST validaci kódu proti bezpečnostní politice.

    Vstupy/Výstupy: Přijímá kód, vrací ValidationResult.
    Vedlejší efekty: Žádné.
    """
    def __init__(self, policy: AirlockPolicy) -> None:
        self._policy = policy

    def validate_code(self, code: str) -> ValidationResult:
        errors: List[str] = []
        try:
            tree = ast.parse(code)
        except Exception as exc:
            return ValidationResult(ok=False, errors=[f"Syntax error: {exc}"])
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                errors.extend(self._validate_imports(node.names))
            if isinstance(node, ast.ImportFrom):
                errors.extend(self._validate_from_import(node))
        ok = len(errors) == 0
        return ValidationResult(ok=ok, errors=errors)

    def _validate_imports(self, names: Iterable[ast.alias]) -> List[str]:
        errors: List[str] = []
        for name in names:
            module_name = name.name.split(".")[0]
            if module_name in self._policy.blocked_modules:
                errors.append(f"Blocked import: {module_name}")
            if self._policy.allowed_modules and module_name not in self._policy.allowed_modules:
                errors.append(f"Import not allowed: {module_name}")
        return errors

    def _validate_from_import(self, node: ast.ImportFrom) -> List[str]:
        errors: List[str] = []
        module_name = (node.module or "").split(".")[0]
        if module_name in self._policy.blocked_modules:
            errors.append(f"Blocked import: {module_name}")
        if self._policy.allowed_modules and module_name not in self._policy.allowed_modules:
            errors.append(f"Import not allowed: {module_name}")
        return errors
