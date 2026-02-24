# Vývojářský deník – Page-20

## ESLint konfigurace pro Cortex UI

### Zadání
- Úkol: Doplnit ESLint konfiguraci a rozběhnout Next lint

### Změny
- cortex/package.json: L12-L24 – Přidány devDependencies eslint a eslint-config-next.
- cortex/.eslintrc.json: L1-L3 – Základní konfigurace Next core web vitals.
- cortex/app/layout.jsx: L1-L21 – Přechod na next/font pro fonty.
- cortex/app/globals.css: L18-L55 – Fonty přes CSS proměnné.

### Ověření
- npm run lint
- pytest
- ruff
- mypy
