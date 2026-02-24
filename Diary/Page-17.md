# Vývojářský deník – Page-17

## Krok 18 – Produkční nasazení a ověření dostupnosti

### Zadání
- Krok plánu: 18
- Úkol: Nasadit na produkci a ověřit dostupnost

### Změny
- docker-compose.yml: L11-L22 – Oprava tagu pgvector image.
- docker-compose.release.yml: L11-L22 – Oprava tagu pgvector image.
- docker/Dockerfile.ganglion: L1-L22 – Instalace závislostí z requirements.txt.
- requirements.txt: L1-L13 – Seznam produkčních závislostí.
- scripts/deploy_prod.ps1: L1-L16 – Produkční deployment skript.
- scripts/check_prod.ps1: L1-L56 – Ověření dostupnosti s retry politikou.
- release/PRODUCTION.md: L1-L21 – Produkční postupy.
- release/RELEASE.md: L1-L31 – Rozšíření seznamu artefaktů.
- release/manifest.json: L1-L18 – Rozšíření artefaktů.
- PLAN.md: L12-L20 – Krok 18 označen jako hotový.
- IMPLEMENTATION.md: L90-L131 – Stav implementace aktualizován.

### Ověření
- docker compose release build + up -d
- scripts/check_prod.ps1
