# Vývojářský deník – Page-16

## Krok 20 – Docker image a release artefakty

### Zadání
- Krok plánu: 17
- Úkol: Připravit Docker image a release artefakty

### Změny
- .dockerignore: L1-L14 – Výjimky pro build kontext.
- docker/Dockerfile.ganglion: L1-L21 – Produkční image pro Ganglion API.
- docker/Dockerfile.cortex: L1-L22 – Produkční image pro Cortex UI.
- docker-compose.release.yml: L1-L61 – Release stack s image buildy.
- release/RELEASE.md: L1-L28 – Návod na build a release compose.
- release/manifest.json: L1-L15 – Seznam artefaktů a image.
- PLAN.md: L17-L20 – Krok 17 označen jako hotový.
- IMPLEMENTATION.md: L98-L129 – Stav a doporučení aktualizovány.
