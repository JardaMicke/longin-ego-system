# Vývojářský deník – Page-3

## Krok 2 – Implementovat LangGraph orchestrace ERTDSD smyčky

### Zadání

- Krok plánu: 2
- Úkol: Implementovat LangGraph orchestrace ERTDSD smyčky

### Změny

- kernel/orchestration/ertdsd_graph.py: L135-L157 – Přidán ERTDSD sentinel a konfigurace pro spouštění workflow.
- kernel/runtime.py: L16-L21, L52-L54, L151-L165 – Doplněna konfigurace a registrace ERTDSD sentinelů v runtime.
- tests/test_ertdsd_orchestrator.py: L115-L136 – Přidán test sentinel invokace orchestrátoru.

## Krok 3 – Vytvořit Cortex UI (Next.js + Puck) včetně persistence

### Zadání (krok 3)

- Krok plánu: 3
- Úkol: Vytvořit Cortex UI (Next.js + Puck) včetně persistence

### Změny (krok 3)

- cortex/lib/db.js: L1-L67 – Upravena persistence na verzované layouty s aktivní verzí.
- cortex/app/api/puck/route.js: L1-L38 – API upraveno na projektové layouty a verze.
- cortex/app/page.jsx: L10-L53 – UI načítá/ukládá layout podle projectId.

## Krok 7 – Aktualizace dokumentace a plánu

### Úkol

- Krok plánu: 7
- Úkol: Aktualizace implementační dokumentace a stavu plánu

#### Změny (krok 7)

- IMPLEMENTATION.md: L66-L109 – Doplněny sekce ERTDSD a Cortex UI, aktualizován stav implementace.
- PLAN.md: L3-L5 – Krok 1–3 označeny jako dokončené.
