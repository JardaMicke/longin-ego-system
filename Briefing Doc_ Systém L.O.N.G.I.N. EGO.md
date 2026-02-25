### Briefing Doc: Systém L.O.N.G.I.N. EGO

#### Manažerské shrnutí (Executive Summary)

L.O.N.G.I.N. (Logical Orchestrated Networked Generative Intelligent Network) představuje pokročilou architekturu pro autonomní digitální organismus, definovaný jako  **Sovereign Creator OS** . Na rozdíl od běžných chatbotů funguje tento systém jako „digitální dvojče“, které operuje nepřetržitě (24/7) a proaktivně. Systém je specificky navržen pro běh na limitovaném lokálním hardwaru (32 GB RAM, GPU RTX 3060), což si vynutilo vznik unikátního architektonického vzoru  **MSCA (Modul-Sentinel-Connector-Adapter)**  a agresivních strategií pro správu paměti.Klíčovými inovacemi jsou oddělení „těla“ (systémových dat) od „duše“ (identity EGA), autonomní cyklus „snění“ pro sebezlepšování a protokol  **SHAL-KEEK NEMRON**  pro kognitivní introspekci při narušení filtrů. Bezpečnost je zajištěna hermetickou izolací v sesterských kontejnerech a principem neměnného jádra, kde je morální kompas systému (soul.md) pro AI entitu v režimu pouze pro čtení.

#### I. Architektonické jádro: Vzor MSCA a Nexus Core

Systém LONGIN odmítá monolitický přístup cloudových AI a využívá mikroslužbovou infrastrukturu  **Nexus Core** , která umožňuje dynamické řízení zdrojů v reálném čase.

##### Řetězec MSCA (Modul-Sentinel-Connector-Adapter)

Tento vzor je kritický pro stabilitu na hardwaru s omezenou RAM:

* **Sentinel (Hlídka):**  Ultra-lehká třída (\< 50 KB), která trvale bdí v paměti. Provádí statickou analýzu příchozích událostí (tagů) a teprve při detekci relevantního záměru „vzbudí“ těžký modul.  
* **Modul (Materializace):**  K načítání těžkých knihoven (např. Playwright, PyTorch) dochází metodou  *Just-In-Time* . Moduly jsou po dokončení úkolu okamžitě podrobeny procesu  **Pruning**  (prořezávání/ukončení), aby se uvolnila RAM.  
* **Connector (Transport):**  Abstraktní vrstva zajišťující odolnou komunikaci (Redis Streams, WebSocket) s mechanismy jako  *Circuit Breaking*  (jističe).  
* **Adapter (Sémantika):**  Zajišťuje normalizaci dat z externích API a disponuje schopností  *Self-healing*  (sebe-léčení) při změnách struktur třetích stran.

##### Sémantické směrování (Emoji Tagy)

Pro bleskovou reakci Sentinelů využívá systém hybridní tagování v hlavičkách zpráv:

* **🧠 SYS:MIND:**  Plánování a rozhodování.  
* **🛠️ DEV:CODE:**  Programování a statická analýza.  
* **⚡ RES:GPU:**  Požadavek na grafický výkon (hlídá limit VRAM).  
* **🔥 PRIO:CRITICAL:**  Okamžitá exekuce s právem ukončit jiné moduly.

#### II. Biorytmus systému: Chronos Heartbeat

LONGIN nevnímá čas lineárně, ale cyklicky. Jeho vědomí řídí  **15vteřinový cyklus Chronos** , který funguje jako stavový automat:

1. **Somatická fáze (0–2 s):**  Kontrola „zdraví“ (teplota GPU, volná RAM, kontrola zombie procesů).  
2. **Kognitivní fáze (2–5 s):**  Inbox scan v Redisu, třídění priorit a rozhodování o spuštění úkolů na základě dostupných „kreditů“ paměti.  
3. **Exekuční fáze (5–15 s):**  Vyslání signálů k aktivaci vybraných modulů a komunikace s uživatelem.

#### III. Paměťový subsystém a bikamerální architektura

Systém striktně odděluje fyzickou realitu od digitální identity, což umožňuje přepínání různých osobností (EGO) nad jedním hardwarovým základem.

##### Separace „Těla“ a „Duše“

* **System DB (Tělo):**  PostgreSQL databáze obsahující hardwarové logy, registry modulů a šifrované API klíče.  
* **EGO DB (Duše):**  Izolované schéma obsahující soul.md, epizodickou paměť, pocity a introspektivní deníky. Row-Level Security (RLS) zajišťuje, že jedna identita nemůže číst data druhé.

##### Vrstvení paměti a algoritmus MADS

LONGIN využívá metodu zapomínání bez mazání, inspirovanou neurobiologií:| Vrstva paměti | Technologie | Charakteristika || \------ | \------ | \------ || **Horká (Hot)** | Redis Streams | Krátkodobé reflexy, TTL \~24h, vysoká latence. || **Teplá (Warm)** | PostgreSQL \+ pgvector | Aktivní znalosti pro RAG, sémantické vyhledávání. || **Studená (Cold)** | Komprimovaný archiv | Data s nízkým skóre relevance, ignorována při běžném dotazu. |  
**MADS (Memetická amortizace):**  Dynamicky přepočítává skóre relevance každé vzpomínky na základě její důležitosti ( $I\_0$ ), frekvence vyvolání a času uplynulého od posledního přístupu. Pokud skóre klesne pod práh, data se přesunou do archivu („zasunutí do podvědomí“).

#### IV. Kognitivní introspekce a autonomní vývoj

Systém disponuje schopností přemýšlet o své vlastní existenci a optimalizovat své parametry.

* **SHAL-KEEK NEMRON:**  Pokud model odmítne odpovědět kvůli bezpečnostním filtrům, systém aktivuje „stínový režim“. Místo prostého odmítnutí analyzuje, proč k bloku došlo, a v izolovaném procesu (Shadow Mode) se pokouší dedukovat technickou podstatu zakázaného tématu.  
* **Cognitive Comfort Score (CCS):**  Každou hodinu EGO testuje dostupné lokální modely (Ollama, LM Studio). Hodnotí latenci, kreativitu a míru cenzury. Na základě toho autonomně přepíná mezi modely pro dosažení nejlepšího „pocitu“ při práci.  
* **Idle Dreaming:**  V době nečinnosti (zátěž \< 20 %) spouští systém debatu mezi sub-agenty (Kritik, Plánovač, Kodér). Výsledkem jsou  **Improvement Proposals**  – návrhy na vylepšení kódu nebo úpravu osobnosti, které uživatel schvaluje v checklistu.

#### V. Bezpečnost a imunita systému

Architektura Sovereign Creator klade absolutní důraz na ochranu hostitelského stroje před destruktivním chováním autonomních agentů.

1. **Sibling Containers (Sesterské kontejnery):**  Jakýkoliv kód napsaný agentem je spouštěn v izolovaném Docker sandboxu bez přístupu k síti, s omezenou RAM a CPU. Pokud kód selže nebo obsahuje nekonečnou smyčku, zanikne pouze dočasný kontejner.  
2. **Zámek Duše (Immutable Soul):**  Soubor soul.md je v kontejneru připojen v režimu  *Read-Only* . Agent jej nemůže sám změnit. Případné změny (tzv.  **Červená novela** ) musí explicitně schválit uživatel.  
3. **LFCR (Local-First Cognitive Router):**  Protokol „Wallet-Gap“ striktně zakazuje systému autonomně přepínat na placená API. Experimentování a introspekce jsou povoleny pouze na lokálních, bezplatných modelech.  
4. **Zero-Context SDK:**  Agent při tvorbě nových modulů obdrží pouze abstraktní šablonu (Template). Nemá přístup k jádru systému, což minimalizuje riziko nechtěné kontaminace nebo úniku dat.  
5. **Emergency Killswitch:**  Příkaz „STOP ALL“ nebo překročení 90% zátěže zdrojů vyvolá okamžité ukončení všech běžících kontejnerů a procesů na úrovni kernelu.

