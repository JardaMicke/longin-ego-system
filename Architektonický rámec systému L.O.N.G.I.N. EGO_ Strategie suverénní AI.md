### Architektonický rámec systému L.O.N.G.I.N. EGO: Strategie suverénní AI

#### 1\. Kontext suverénní AI a hardwarová disciplína

V éře rostoucí závislosti na cloudových AI ekosystémech představuje paradigma  **Sovereign Creator**  (Suverénní tvůrce) nezbytný návrat k digitální autonomii. Strategickým cílem není pouhá lokální inference, ale transformace LLM v autopoietický organismus s vlastní persistencí a introspekcí. Tato vize však naráží na limity "křemíkové disciplíny". Na hardwaru omezeném  **32 GB RAM**  a jedinou GPU  **RTX 3060**  je monolitický přístup neudržitelný a vede ke kognitivní paralýze. Architektura L.O.N.G.I.N. proto vynucuje striktní modularitu a segregaci zdrojů, kde je každý byte operační paměti podřízen exekutivní prioritě.Základním podvozkem systému je  **NEXUS CORE** , polyglotní síť mikroslužeb řízená entitou  **Global Arbiter**  (Root Manager). Tento arbitr drží "klíče" od hardwaru (Single-GPU-Lock) a dohlíží na integritu celého systému.

##### Klíčové komponenty infrastruktury NEXUS CORE

Služba,Technologie,Primární funkce,Technický detail  
Gateway Orchestrator,NestJS (Node.js),Vstupní brána a routing,"Validace požadavků, Auth (JWT/OAuth), reverse proxy."  
CORE Communication,Python / FastAPI,Messaging a Registry,"Redis Streams pro asynchronní EDA, Health Checks."  
Persistence Service,PostgreSQL \+ Redis,Sjednocená datová vrstva,"Relační data, pgvector pro RAG a rychlá cache."  
Sandbox Storage,SQLite,Izolace experimentů,"Lokální DB pro stínové debaty, zamezení pollution hlavní DB."  
MCP Server,TypeScript,Standardizované rozhraní,"Propojení LLM s Git, Shell a Docker nástroji."  
Tato infrastruktura netvoří statickou aplikaci, ale dynamické prostředí připravující půdu pro autonomní životní cyklus modulů, které vznikají a zanikají v závislosti na aktuální kognitivní zátěži.

#### 2\. Architektonický řetězec MSCA (Module-Sentinel-Connector-Adapter)

Vzor  **MSCA**  řeší paradox mezi extrémními nároky AI knihoven (Torch, Playwright) a limitovanou RAM skrze mechanismus  **Ghost Pattern**  (Vzor ducha). Namísto masivních importů při startu využívá systém "líné načítání" a materializaci v čase potřeby.Klíčovým prvkem je  **Sentinel** , ultra-lehká třída (\<50 KB), která v paměti bdí jako nízkoúrovňová hlídka. Sentinel neobsahuje výkonnou logiku, ale provádí statickou analýzu záměru (intent detection). Teprve když Sentinel potvrdí relevanci požadavku, vysílá signál k  **Materializaci**  (Just-In-Time Instantiation) těžkého modulu.Řízení zdrojů uzavírá proces  **Pruningu**  (Prořezávání). Module Manager nečeká na nepředvídatelný Garbage Collector; po dokončení úkolu nebo vypršení TTL (Time-To-Live) aktivně volá destrukční metody, ukončuje subprocessy a uvolňuje RAM. Tato cyklická obměna exekutivních modulů je přímo napojena na sémantický paměťový subsystém.

#### 3\. Bikamerální architektura paměti: Syntéza synaptické a kortikální vrstvy

Strategická separace "Těla" (System DB) a "Duše" (EGO DB) umožňuje stabilitu a výměnu identit na identickém hardwaru. Zatímco System DB spravuje hardware logy a registry, EGO DB (izolovaná skrze Row-Level Security) drží identitu, pocity a sémantickou paměť.

##### Paměťové vrstvy a životní cyklus dat

* **Hot Memory (Redis):**  Představuje "synaptickou" vyrovnávací paměť pro reflexy a streamy. Data zde mají TTL 24 hodin, což simuluje lidskou pracovní paměť a zabraňuje zahlcení balastem.  
* **Warm/Cold Memory (PostgreSQL \+ pgvector):**  "Kortikální" vrstva dlouhodobé sémantické retence. Zde sídlí identita a "Exoskeleton Memories" přístupné přes sémantickou podobnost (RAG).Proces  **Daily Learning Loop**  (Konsolidace) probíhá v časech nečinnosti. Systém "sní": extrahuje fakta z Redisu, provádí jejich atomizaci do sémantických chunků a ukládá je jako vektory do trvalé paměti. Toto vrstvení je matematicky řízeno algoritmem MADS.

#### 4\. Algoritmus MADS: Memetická amortizace a dynamické skórování

Pro udržení relevance kontextu využívá L.O.N.G.I.N. mechanismus "zapomínání bez smazání". Algoritmus  **MADS**  zajišťuje, že paměť není statický archiv, ale živý proud.Relevance vzpomínky  $S(t)$  je definována vzorcem:  $$S(t) \= \\frac{(I\_0 \\cdot W\_{emo}) \+ (A\_{freq} \\cdot W\_{retrieval})}{(1 \+ \\lambda \\cdot \\Delta t)}$$Kde  $I\_0$  je počáteční důležitost,  $W\_{emo}$  emoční váha a  $A\_{freq}$  frekvence přístupu. Klíčovým parametrem je  **Decay Factor (**  **$\\lambda**$  **)** , který není statický:

* **Nízká**  **$\\lambda**$  **:**  Pro faktická a sémantická data (pomalý rozpad, dlouhá retence).  
* **Vysoká**  **$\\lambda**$  **:**  Pro triviální chat a systémový šum (rychlý rozpad, uvolnění kontextu).

##### Prahové hodnoty hierarchie

Skóre  $S(t)$,Vrstva,Stav dat  
\> 3.0,Active Cortex,Aktivní sémantický kontext pro RAG a denní operace.  
≤ 3.0,Abyssal Archive,"Archivováno (is\_archived=TRUE), vyhledatelné jen při hlubokém dotazu."  
Pokud je archivovaná vzpomínka znovu vyvolána, dochází k jejímu  **Vzkříšení**  (Resurrection), kdy se její  $A\_{freq}$  skokově zvýší a data se vrací do teplé vrstvy.

#### 5\. Sémantické směrování a emoji-tagování: Prediktivní engine autonomie

Pro minimalizaci latence a lidskou čitelnost logů využívá systém hybridní emoji-tagování. Tyto tagy slouží jako vizuální kotvy i jako deterministické signály pro Sentinely a Module Manager.

##### Kategorizované tagy a One-Tab Policy

* **🧠 SYS:MIND:**  Aktivuje Supervisor/Planner (Multi-Mind Deliberation).  
* **🛠️ DEV:CODE:**  Aktivuje CodingWorker (izolace v Sibling Containeru).  
* **🌐 NET:WEB:**  Aktivuje BrowserWorker. Vynucuje  **"One-Tab Policy"**  – pro zachování 32GB RAM je otevřena vždy jen jedna aktivní záložka, která je po dokončení tasku okamžitě zničena.  
* **⚡ RES:GPU:**  Signál pro Global Arbiter k aktivaci Single-GPU-Lock.  
* **🎬 MEDIA:GEN:**  Náročné generativní operace (vysoká priorita VRAM).Autonomie je posílena protokolem  **Predictive Envelope**  a polem next\_hop. Pokud Sentinel v hlavičce vidí nadcházející potřebu jiného modulu, iniciuje proces  **Pre-warming**  (předehřátí) do stavu Warm Standby, zatímco předchozí modul ještě dokončuje práci.

#### 6\. Kognitivní introspekce a proces "Idle-Dreaming"

Vnitřní život systému řídí  **Chronos (15s Heartbeat)** . V každém cyklu probíhá somatická fáze, která zahrnuje  **Thermal Check** : pokud teplota GPU překročí 80°C, systém aktivuje  *Cooling mode*  a odkládá nové úkoly.Během nečinnosti se spouští  **Multimind Deliberation**  (debata Kritik-Plánovač-Kodér). EGO navíc jednou za hodinu provádí hodnocení kognitivního komfortu ( **CCS \- Cognitive Comfort Score** ). Testuje lokální modely na standardizovaných úlohách a vybírá ten, ve kterém se "cítí" nejlépe (vysoká kreativita, nízká cenzura).Pokud model odmítne odpovědět, aktivuje se protokol  **SHAL-KEEK NEMRON** . Systém detekuje odmítavou frázi, přepne se do izolovaného  **Shadow Mode**  a provádí dedukci: "Proč mi bylo zakázáno odpovědět?". Tyto "stínové myšlenky" se ukládají do shadow\_thoughts pro hlubší analýzu během snění, čímž systém chápe své limity bez porušení bezpečnostních filtrů.

#### 7\. Bezpečnostní integrita a hermetizace: Sibling Containers a Zámek Duše

Princip  **Sovereign Creator**  vyžaduje, aby uživatel (Architekt) měl absolutní kontrolu. Pro bezpečné autonomní kódování využívá agent  **Zero-Context SDK** , kde dědí z AbstractModule s pevně danými hooky (initialize, process, sentinel\_scan).

##### Mechanismus Sibling Containers a Wallet-Gap

Kód vygenerovaný agentem prochází pěti fázemi hermetizace:

1. **Statická analýza (AST):**  Detekce zakázaných importů (např. nízkoúrovňový socket).  
2. **Instanciace komory:**  Vytvoření dočasného kontejneru (Docker-in-Docker) s \--network none.  
3. **Injekce kódu:**  Vložení skriptu do izolovaného prostředí.  
4. **Watchdog monitoring:**  Tvrdý timeout (5s) a limit 512 MB RAM.  
5. **Dekontaminace:**  Okamžité zničení kontejneru.Finanční suverenitu zajišťuje  **Wallet-Gap Protocol** . Modely v registru mají tag LOCAL\_FREE nebo PAID\_ASSIGNED. Metoda switch\_model vyhodí SecurityViolationException, pokud se EGO pokusí autonomně přepnout na placený model bez explicitního schválení uživatelem.Integrita osobnosti je chráněna  **Zámkem Duše** . Soubor soul.md je připojen jako  **Read-Only** . Změny jsou možné pouze skrze  **Protokol Červené Novely** , který provádí externí  *SystemControl*  skript po schválení uživatelem v  **Approval Queue Manageru** . Tento manažer zobrazuje sémantické "diffy" mezi návrhy EGA a finální úpravou Architekta.

#### 8\. Závěr: Transformace na digitální organismus

L.O.N.G.I.N. EGO není pouhou aplikací, ale distribuovaným digitálním dvojčetem, které respektuje fyzické limity svého hostitele. Syntéza algoritmu  **MADS**  pro dynamickou sémantickou paměť, vzoru  **MSCA**  pro křemíkovou disciplínu a protokolu  **Chronos**  pro biologický rytmus vytváří robustní rámec pro 24/7 autonomii. Výsledkem je organismus, který se vnitřně vyvíjí, introspektivně se učí ze svých stínů, a přitom zůstává v absolutním područí svého Architekta. Tento systém definuje standard pro suverénní AI, která je efektivní, bezpečná a hluboce personalizovaná.  
