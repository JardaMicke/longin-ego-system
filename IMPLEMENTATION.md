# Implementační dokumentace Longin EGO

## 1. Účel dokumentu

Tento dokument mapuje klíčové architektonické prvky popsané v návrhu Longin EGO na konkrétní implementace v kódu. Slouží jako navigační přehled mezi specifikací a reálným systémem.

## 2. Mapování architektury na kód

### 2.1 Orchestrátor jádra (Kernel Runtime)

- Centrální kompozice subsystémů, konfigurace Redis/Postgres a registrace sentinelů běží v [runtime.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/runtime.py#L1-L156).
- Propojení Chronos Heartbeat, Inbox Routeru a Memory Routeru je zde inicializováno, včetně identity firewallu a discovery služby.

### 2.2 Event Bus (Redis Streams)

- Základní komunikace přes Redis Streams je implementována v [redis_bus.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/bus/redis_bus.py#L1-L55).
- Inbox zprávy směruje [inbox_router.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/bus/inbox_router.py#L1-L140), který dekóduje payloady a deleguje na Sentinel Registry.
- Paměťové streamy konsolidace obsluhuje [memory_router.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/bus/memory_router.py#L1-L52).

### 2.3 Sentinel Pattern (MSCA)

- Registry sentinelů je v [registry.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/workers/_sentinels/registry.py#L1-L41).
- Chronos sentinel hlídá systémové zdroje a publikuje alerty v [chronos_sentinel.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/workers/_sentinels/chronos_sentinel.py#L1-L36).
- Konsolidace paměti iniciuje přesměrování do konsolidačního streamu v [memory_consolidate_sentinel.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/workers/_sentinels/memory_consolidate_sentinel.py#L1-L36).
- Vlastní pipeline pro čtení hot memory a ukládání do cold memory je v [memory_pipeline_sentinel.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/workers/_sentinels/memory_pipeline_sentinel.py#L1-L66).

### 2.4 Chronos Heartbeat

- Periodická 15s smyčka s fázemi somatic/cognitive/execute je v [heartbeat.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/chronos/heartbeat.py#L1-L65).
- Puls zapisuje heartbeat do Redis a volitelně do streamu.

### 2.5 Global Arbiter (Resource Management)

- Snímání RAM a GPU teploty je v [core.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/arbiter/core.py#L1-L63).
- Chronos sentinel využívá Arbiter pro blokaci akcí při nedostatku zdrojů.

### 2.6 Bikamerální paměť (Redis + Postgres)

- Schéma dlouhodobé paměti v Postgresu je v [schema.sql](file:///f:/L.O.N.G.I.N.%20EGO%20System/memory/postgres/schema.sql#L1-L50).
- API pro vektorové vyhledávání a zápis do Postgresu je v [client.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/memory/postgres/client.py#L1-L203).
- Hot memory (Redis) přístup je v [client.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/memory/redis/client.py#L1-L63).
- Jednoduchý embedder (deterministický) je v [simple_embedder.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/embeddings/simple_embedder.py#L1-L25).

### 2.7 Identita a Soul.md

- Identity firewall sleduje změnu soul souboru a ukládá hash do Redis v [identity_firewall.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/security/identity_firewall.py#L1-L58).
- Soul soubor je v [soul.md](file:///f:/L.O.N.G.I.N.%20EGO%20System/ego/soul.md).
- Boot loader identity parsuje direktivy a ukládá je do Redis/Postgres v [identity_boot.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/security/identity_boot.py#L1-L92).
- Kernel runtime spouští boot identity při startu v [runtime.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/runtime.py#L42-L164).
- Deník: [Page-1](file:///f:/L.O.N.G.I.N.%20EGO%20System/Diary/Page-1.md).

### 2.8 Bezpečnostní vrstva (Airlock + Sibling Containers)

- AST validace zakázaných importů a whitelistu modulů je v [airlock.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/security/airlock.py#L1-L55).
- Spouštění izolovaných kontejnerů je v [container_manager.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/security/container_manager.py).
- Sibling runner pro spouštění skriptů v kontejnerech je v [runner.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/execution/runner.py).
- Lokální Ganglion exekuce příkazů (sandbox i raw) je v [execution.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/ganglion/execution.py).

### 2.9 Síťová topologie (Nexus + Ganglia)

- mDNS discovery a registrace uzlů je v [discovery.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/network/discovery.py).
- Registry uzlů a TTL purge logika je v [registry.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/network/registry.py#L1-L57).
- Ganglion REST API a hardware profil jsou v [api.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/ganglion/api.py) a [hardware.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/ganglion/hardware.py#L1-L39).
- HTTP klient pro připojení na Ganglion uzly je v [ganglion_client.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/network/ganglion_client.py).

### 2.10 MCP nástroje a SDK

- MCP server registry a tool API jsou v [server.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/sdk/longin_sdk/mcp/server.py) a [adapters.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/sdk/longin_sdk/mcp/adapters.py).
- Nexus MCP nástroje pro sken sítě a delegaci výpočtu jsou v [nexus_control.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/mcp/nexus_control.py#L1-L62).
- SDK základní datové typy a zadání úloh jsou v [base.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/sdk/longin_sdk/core/base.py).
- Bezpečný filesystem a paměťový klient SDK jsou v [fs.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/sdk/longin_sdk/tools/fs.py#L1-L31) a [memory.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/sdk/longin_sdk/tools/memory.py#L1-L66).

### 2.11 Orchestrace ERTDSD (LangGraph)

- LangGraph workflow a ERTDSD orchestrátor jsou v [ertdsd_graph.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/orchestration/ertdsd_graph.py#L1-L157).
- Registrace ERTDSD sentinelů probíhá v [runtime.py](file:///f:/L.O.N.G.I.N.%20EGO%20System/kernel/runtime.py#L151-L169).

### 2.12 Cortex UI (Next.js + Puck)

- UI aplikace a Puck editor jsou v [page.jsx](file:///f:/L.O.N.G.I.N.%20EGO%20System/cortex/app/page.jsx#L1-L63).
- REST API pro layout persistence je v [route.js](file:///f:/L.O.N.G.I.N.%20EGO%20System/cortex/app/api/puck/route.js#L1-L38).
- Datový layer pro verzované layouty je v [db.js](file:///f:/L.O.N.G.I.N.%20EGO%20System/cortex/lib/db.js#L1-L76).

## 3. Stav implementace vůči návrhu

### 3.1 Implementováno

- Event-driven Kernel (Redis Streams), Chronos Heartbeat a Arbiter.
- Sentinely a routing inbox/paměťových streamů.
- Bipolární paměťové schéma a základní persistence.
- Identity Firewall, boot identity a Airlock validace.
- Ganglion uzly, discovery, MCP nástroje a klient.
- Docker Compose infrastruktura včetně kernel/cortex služeb.
- LangGraph orchestrátor ERTDSD a sentinel registrace.
- Cortex UI (Next.js + Puck) s perzistencí layoutů.
- Integrační a safety testy pro boot identity a SiblingRunner.
- Docstringy tříd dle standardu.
- Deník: [Page-1](file:///f:/L.O.N.G.I.N.%20EGO%20System/Diary/Page-1.md).
- Deník: [Page-2](file:///f:/L.O.N.G.I.N.%20EGO%20System/Diary/Page-2.md).
- Deník: [Page-3](file:///f:/L.O.N.G.I.N.%20EGO%20System/Diary/Page-3.md).
- Deník: [Page-4](file:///f:/L.O.N.G.I.N.%20EGO%20System/Diary/Page-4.md).
- Deník: [Page-5](file:///f:/L.O.N.G.I.N.%20EGO%20System/Diary/Page-5.md).
- Deník: [Page-6](file:///f:/L.O.N.G.I.N.%20EGO%20System/Diary/Page-6.md).

### 3.2 Chybějící části dle specifikace

- Mobilní Synapse klient a vzdálené ovládací rozhraní nejsou součástí tohoto repo.

## 4. Doporučené navázání

- Rozšířit identity boot o validační pravidla a auditní log.
- Zvážit mobilní Synapse klient a vzdálené ovládací rozhraní.
