# Vývojářský deník – Page-18

## CI/CD – produkční doména www.longinegosystem.eu

### Zadání
- Úkol: Upravit CI/CD konfiguraci tak, aby se homepage zobrazovala na www.longinegosystem.eu

### Změny
- .github/workflows/ci.yml: L44-L74 – Přidán deploy job s SSH nasazením.
- docker-compose.release.yml: L39-L74 – Přidán Caddy reverse proxy.
- caddy/Caddyfile: L1-L9 – Doména www.longinegosystem.eu a přesměrování.
- release/manifest.json: L8-L18 – Přidán Caddyfile.
- release/RELEASE.md: L23-L32 – Přidán Caddyfile do artefaktů.
- release/PRODUCTION.md: L9-L31 – DNS a CI/CD secrets.
