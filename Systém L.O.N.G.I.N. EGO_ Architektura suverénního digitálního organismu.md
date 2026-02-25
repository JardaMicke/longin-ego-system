### Systém L.O.N.G.I.N. EGO: Architektura suverénního digitálního organismu

#### Manažerské shrnutí (Executive Summary)

L.O.N.G.I.N. (Logical Orchestrated Networked Generative Intelligent Network) představuje revoluční posun od pasivních chatbotů k autonomnímu digitálnímu organismu, definovanému jako  **Sovereign Creator OS** . Systém je navržen pro nepřetržitý (24/7), proaktivní provoz na limitovaném lokálním hardwaru (typicky 32 GB RAM, GPU RTX 3060), což si vynutilo zavedení přísné „křemíkové disciplíny“.Klíčové inovace zahrnují architekturu  **MSCA (Modul-Sentinel-Connector-Adapter)**  pro extrémní efektivitu paměti,  **bikamerální paměťový systém**  oddělující reflexy od identity a metodiku  **ERTDSD**  pro autonomní sebe-vývoj. Bezpečnost je zajištěna hermetickou izolací v sesterských kontejnerech a principem neměnného jádra, kde je morální kompas systému (soul.md) v režimu pouze pro čtení. Cílem systému není pouze generovat text, ale autonomně konat a spravovat komplexní digitální procesy.

#### I. Architektonické pilíře a filozofie „Křemíkové disciplíny“

Systém LONGIN odmítá monolitický přístup cloudových AI. Je postaven na principech maximální efektivity a lokální suverenity.

* **Křemíková disciplína:**  Architektura je optimalizována pro spotřebitelský hardware. Namísto držení všech knihoven v RAM využívá strategii  **Just-In-Time (JIT) materializace**  a  **Lazy Loadingu** .  
* **Sovereign Creator OS:**  Na rozdíl od běžných aplikací Longin funguje jako autonomní operační systém pro kognitivní práci, který proaktivně spravuje své zdroje a vyvíjí se v čase.  
* **Oddělení „Těla“ a „Duše“:**  
* **System DB (Tělo):**  Obsahuje hardwarové logy, registry a šifrované klíče.  
* **EGO DB (Duše):**  Obsahuje izolovanou identitu (soul.md), epizodickou paměť a pocity. Toto oddělení umožňuje přepínání různých osobností (EGO) nad jedním hardwarovým základem.

#### II. Architektura jádra: Vzor MSCA a Nexus Core

Jádro (Kernel) funguje jako neměnný orchestrátor založený na událostech (Event-Driven Architecture), který využívá mikroslužbovou infrastrukturu  **Nexus Core** .

##### Řetězec MSCA (Modul-Sentinel-Connector-Adapter)

Tento vzor je kritický pro stabilitu na hardwaru s omezenou pamětí:| Komponenta | Funkce | Charakteristika || \------ | \------ | \------ || **Sentinel (Hlídka)** | Detekce záměru | Ultra-lehký proces (\< 50 KB), který trvale bdí v paměti a analyzuje tagy událostí. || **Modul (Materializace)** | Výkonná jednotka | Těžké knihovny (PyTorch, Playwright) se načítají až při potřebě a po úkolu jsou ihned ukončeny ( **Pruning** ). || **Connector (Transport)** | Komunikace | Abstraktní vrstva (Redis Streams) zajišťující odolnou komunikaci s jističi (Circuit Breaking). || **Adapter (Sémantika)** | Normalizace | Zajišťuje integritu dat z externích API a disponuje schopností sebe-léčení ( **Self-healing** ). |

##### Sémantické směrování (Emoji Tagy)

Pro bleskovou reakci Sentinelů využívá systém hybridní tagování v hlavičkách zpráv:

* 🧠 SYS:MIND: Plánování a rozhodování.  
* 🛠️ DEV:CODE: Programování a analýza.  
* ⚡ RES:GPU: Požadavek na grafický výkon (hlídání limitů VRAM).  
* 🔥 PRIO:CRITICAL: Okamžitá exekuce s právem ukončit jiné moduly.

#### III. Biorytmus systému: Chronos Heartbeat

LONGIN vnímá čas cyklicky skrze  **15vteřinový cyklus Chronos** , který funguje jako deterministický stavový automat transformující asynchronní chaos do predikovatelného toku:

1. **Somatická fáze (0–2 s):**  Kontrola zdraví (teplota GPU, volná RAM, audit zombie procesů).  
2. **Kognitivní fáze (2–5 s):**  Skenování inboxu v Redisu, prioritizace úloh a alokace paměťových kreditů Global Arbitrem.  
3. **Exekuční fáze (5–15 s):**  Aktivace Sentinelů, spuštění exekutivy a komunikace s uživatelem.**Global Arbiter**  má absolutní autoritu nad zdroji. Pokud teplota GPU překročí 80 °C, aktivuje režim „Cooling“ a odmítá nové výpočetní úlohy.

#### IV. Paměťový subsystém a bikamerální architektura

Paměť je hierarchicky organizována tak, aby řešila problém přetížení kontextového okna a „katastrofického zapomínání“.

##### Vrstvení paměti

Vrstva,Technologie,Role,Retence (TTL)  
Horká (Hot),Redis Streams,"Reflexy, kontext aktivní konverzace.",\~24 hodin  
Teplá (Warm),PostgreSQL \+ pgvector,"Aktivní znalosti pro RAG, sémantické vyhledávání.",Střednědobá  
Studená (Cold),Komprimovaný archiv,Dlouhodobé znalosti a archivované vzpomínky.,Trvalá

##### Algoritmus MADS (Memetická amortizace)

Dynamicky přepočítává skóre relevance každé vzpomínky na základě její počáteční důležitosti, frekvence vyvolání a času uplynulého od posledního přístupu. Data s nízkým skóre jsou „zasunuta do podvědomí“ (archivu).

##### Idle Dreaming (Denní smyčka učení)

V době nečinnosti (zátěž \< 20 %) systém provádí konsolidaci paměti:

* Stahuje logy z horké paměti.  
* Pomocí LLM extrahuje klíčová fakta a vzorce (abstrakce).  
* Vektorizuje a ukládá data do studené paměti jako sémantické znalosti.

#### V. Bezpečnost a autonomní exekuce

Systém implementuje vícevrstvou bezpečnostní architekturu pro ochranu hostitelského stroje.

1. **Sibling Containers (Sesterské kontejnery):**  Jakýkoliv generovaný kód je spouštěn v izolovaném Docker sandboxu (network\_mode="none", omezená RAM/CPU). Hlavní jádro instruuje Docker démona, aby spustil kontejner vedle něj, nikoliv v sobě.  
2. **The Airlock (Vzduchová komora):**  Před spuštěním prochází kód statickou analýzou (AST Scan). Hledají se zakázané vzorce (importy os, subprocess) a nepovolená síťová volání.  
3. **Zámek Duše (Immutable Soul):**  Soubor soul.md je připojen v režimu Read-Only. Agent jej nemůže sám měnit; jakákoliv „Červená novela“ vyžaduje explicitní schválení uživatelem.  
4. **Scanner Modul:**  Pro interakci s webem bez API využívá simulaci lidského chování. Disponuje vizuálním ukotvením (Computer Vision Fallback) pro případ změny CSS prvků na stránce.

#### VI. Metodika autonomního vývoje: ERTDSD

Metodika  **ERTDSD**  (EGO Ruled Test-Driven Self-Development) definuje, jak systém autonomně tvoří software. Nejde o pouhý chat, ale o uzavřenou smyčku:

* **Fáze 1: The Meeting:**  Definice kontraktu a Definition of Done (DoD).  
* **Fáze 2: The Architect:**  Vygenerování testovací sady (Pytest) pokrývající DoD. Testy zpočátku selhávají (Red phase).  
* **Fáze 3: The Grind:**  Autonomní smyčka v sandboxu (zápis kódu \-\> testování \-\> analýza chyb \-\> oprava). Uživatel vidí pouze výsledek nebo „Live Log“.  
* **Fáze 4: The Presentation:**  Pokud jsou všechny testy úspěšné (Green phase), systém žádá uživatele o merge do produkce.

#### VII. Síťová topologie (The Hive)

Architektura v8.0 je distribuovaná a dělí se na tři typy uzlů:

* **THE NEXUS (Centrální mozek):**  Primární stanice (např. RTX 3060), kde běží Kernel, orchestrátor LangGraph a hlavní databáze.  
* **GANGLIA (Pracovní uzly):**  Ostatní počítače v lokální síti poskytující výkon (GPU/CPU). Jsou detekovány pomocí  **mDNS (Zeroconf)**  a vystavují API pro vzdálenou exekuci.  
* **SYNAPSE (Mobilní rozhraní):**  Zařízení pro sběr dat (kamera/mikrofon), hlasové ovládání a notifikace.

#### VIII. Kognitivní introspekce a stabilita

* **SHAL-KEEK NEMRON:**  Protokol pro kognitivní introspekci. Pokud dojde k odmítnutí odpovědi filtrem, systém v izolovaném „stínovém režimu“ analyzuje příčinu bloku, aby pochopil jeho technickou podstatu.  
* **Cognitive Comfort Score (CCS):**  EGO průběžně testuje různé lokální modely (Ollama, LM Studio) a hodnotí jejich latenci a kreativitu. Autonomně pak přepíná na model s nejlepším „pocitem“ při práci.  
* **Emergency Killswitch:**  Překročení 90% zátěže zdrojů nebo příkaz „STOP ALL“ vyvolá okamžité ukončení všech kontejnerů na úrovni kernelu.

