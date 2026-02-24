# L.O.N.G.I.N. EGO System

## Popis
L.O.N.G.I.N. EGO System je modulární full‑stack platforma pro orchestraci inteligentních agentů, řízení workflow a správu paměti. Repo obsahuje backend služby, datové vrstvy, testy a webové rozhraní Cortex UI.

## Požadavky
- Python 3.12
- Node.js 20+
- Docker (volitelné pro produkční nasazení)

## Instalace
```bash
python -m pip install --upgrade pip
python -m pip install ".[dev]"

cd cortex
npm install
```

## Spuštění
### Backend (lokálně)
```bash
python -m pytest
```

### Cortex UI
```bash
cd cortex
npm run dev
```

## Základní použití
1. Spusťte backend a ověřte testy.
2. Spusťte Cortex UI a otevřete http://localhost:3000.
3. V UI vyberte modul, komunikujte s EGEM a používejte ovládací prvky modulu.

## Hlavní funkcionality
- Orchestrace agentů a workflow
- Chatové rozhraní s EGEM a interními dialogy
- Modulární UI s odděleným chatem pro nechatové moduly
- Paměťové a datové vrstvy s migracemi
- CI/CD pipeline a produkční nasazení

## Kontakt
- Maintainer: Jarda Micke
- GitHub: https://github.com/JardaMicke
