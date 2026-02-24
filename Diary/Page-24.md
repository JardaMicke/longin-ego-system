# Vývojářský deník – Page-24

## Docker úpravy a rebuild

### Zadání
- Úkol: Upravit Docker a docker-compose soubory a rebuildovat kontejnery

### Změny
- docker-compose.yml: L23-L50 – Nahrazen nexus-kernel službou ganglion-api, build image a env pro dev.
- docker-compose.staging.yml: L5-L10 – Aktualizace názvu služby na ganglion-api.
- docker/Dockerfile.ganglion: L5-L19 – Instalace balíčku přes pyproject a pip install .
- docker/Dockerfile.cortex: L5-L7 – npm ci s package-lock.
- IMPLEMENTATION.md: L122-L131 – Přidán odkaz na Page-24.

### Ověření
- docker compose up -d --build
- npm run lint
- pytest
- ruff
- mypy
