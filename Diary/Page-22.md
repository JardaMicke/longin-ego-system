# Vývojářský deník – Page-22

## Oprava balení a mypy

### Zadání
- Úkol: Opravit pip install .[dev] a navazující mypy chybu

### Změny
- pyproject.toml: L33-L45 – Explicitní balíčky pro setuptools a exclude build pro mypy.
- IMPLEMENTATION.md: L108-L129 – Přidán odkaz na Page-22.

### Ověření
- python -m pip install .[dev]
- pytest
- ruff
- mypy
