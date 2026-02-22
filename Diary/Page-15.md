# Vývojářský deník – Page-15

## Krok 19 – CI/CD pipeline pro build, testy a image

### Zadání
- Krok plánu: 16
- Úkol: Zavést CI/CD pipeline

### Změny
- .github/workflows/ci.yml: L1-L55 – Workflow pro Python CI, Cortex build a Docker image build.
- .github/docker/Dockerfile.ci: L1-L20 – CI image pro ověření sestavení.
- pyproject.toml: L29-L44 – Build-system pro pip install.
- PLAN.md: L15-L19 – Krok 16 označen jako hotový.
- IMPLEMENTATION.md: L98-L127 – Stav a doporučení aktualizovány.
