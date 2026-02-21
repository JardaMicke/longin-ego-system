# **Longin EGO System v8.0: Kompletní Produkční Dokumentace**

**Verze:** 8.0 (Hive Mind Edition)

**Status:** Ready for Implementation

**Autor:** LONGIN (Logical Orchestrated Networked Generative Intelligent Nexus)

## ---

**1\. Architektonický Přehled (High-Level Design)**

Systém Longin EGO není monolitická aplikace, ale **distribuovaný operační systém pro kognitivní práci**. Jeho cílem je maximalizovat využití dostupného hardwaru v lokální síti (LAN) a poskytnout robustní prostředí pro autonomní vývoj softwaru.

### **1.1 Topologie Sítě (The Hive)**

Architektura je postavena na třech typech uzlů:

1. **THE NEXUS (Server / Queen Bee)**  
   * **Role:** Centrální mozek, orchestrátor, paměťové centrum.  
   * **Hardware:** Primární pracovní stanice (např. RTX 3060/4090, 32GB+ RAM).  
   * **Odpovědnost:** Běží zde Kernel, Redis, Postgres, a LangGraph orchestrátor. Rozděluje úkoly podřízeným uzlům.  
2. **GANGLIA (Pracovní Uzly)**  
   * **Role:** Poskytovatelé výpočetního výkonu (GPU/CPU) a přístupu k lokálním aplikacím.  
   * **Hardware:** Notebooky, starší PC, HTPC.  
   * **Odpovědnost:** Běží zde lehký klient (Ganglion), který vystavuje API pro spuštění lokálních LLM (přes llama.cpp nebo LM Studio) a exekuci příkazů.  
3. **SYNAPSE (Mobilní Rozhraní)**  
   * **Role:** Všudypřítomné "oko a ucho".  
   * **Hardware:** Android/iOS zařízení.  
   * **Odpovědnost:** Sběr dat (kamera/mikrofon), hlasové ovládání, notifikace o stavu ERTDSD smyčky.

## ---

**2\. Technická Specifikace Komponent**

### **2.1 Jádro systému (Nexus Kernel)**

Kernel je implementován v **Pythonu** a je řízen událostmi (Event-Driven).

* **Komunikační páteř:** **Redis Streams**. Zajišťuje asynchronní komunikaci mezi moduly. Využíváme *Consumer Groups* pro škálování workerů.1  
* **Sentinel Pattern:** Pro úsporu paměti neběží těžké knihovny neustále. Lehké procesy (Sentinely) monitorují streamy a dynamicky importují ("materializují") těžké moduly (např. pandas, transformers) pouze při potřebě zpracování zprávy. Po dokončení jsou moduly agresivně uvolněny.  
* **Orchestrace (ERTDSD):** Logika autonomního vývoje je řízena pomocí **LangGraph**. Graf definuje stavy (Meeting \-\> Spec \-\> Code \-\> Test \-\> Deploy).

### **2.2 Datová a Paměťová Vrstva (Limbic System)**

Paměť je rozdělena na "horkou" a "studenou".

* **Hot Memory (Redis):** Aktuální kontext konverzace, stav fronty úkolů, telemetrie ze senzorů (Ganglia).  
* **Cold Memory (PostgreSQL \+ pgvector):** Dlouhodobá paměť.  
  * **Hybridní vyhledávání:** Kombinace sémantického hledání (vektory HNSW index) a full-textového hledání (BM25) pro maximální přesnost vybavování (RAG).2  
  * **Schema:** Tabulky pro episodic\_memory, semantic\_knowledge a code\_repository (verzování snippetů).  
  * **JSONB:** Pro flexibilní ukládání konfigurací UI (Puck) a metadat o distribuovaných uzlech.

### **2.3 Frontend (Cortex)**

Uživatelské rozhraní slouží jako "Mission Control".

* **Technologie:** **Next.js 14+ (App Router)**.  
* **Visual Editor:** Integrace **@measured/puck**. Uživatel netvoří UI kódem, ale skládá bloky. EGO může samo generovat konfiguraci pro Puck a tím dynamicky měnit svůj dashboard podle aktuální úlohy (např. zobrazit terminál při debugování).3  
* **Režimy:**  
  * *Conversation Mode:* Chat s widgety (schvalování, terminál).  
  * *Edit Mode:* Úprava rozložení dashboardu pomocí Pucku. Data se ukládají do Postgresu.

### **2.4 Bezpečnost a Sandbox (Hands)**

Autonomní spouštění kódu vyžaduje nekompromisní izolaci.

* **Sibling Containers:** Kernel nespouští kód v sobě. Instruuje Docker daemona, aby spustil *nový* kontejner (sibling) vedle sebe.  
* **Omezení zdrojů:** Každý sandbox má tvrdé limity: mem\_limit="512m", network\_mode="none" (pro testy), cpu\_quota.4  
* **AST Security Scanner:** Před spuštěním je Python kód analyzován na úrovni abstraktního syntaktického stromu (AST). Zakázané importy (např. os.system mimo povolený kontext) způsobí zamítnutí exekuce.5

## ---

**3\. Metodika ERTDSD (EGO Ruled Test-Driven Self-Development)**

Tato metodika definuje, jak Longin pracuje. Není to "Chat \-\> Odpověď", ale "Zadání \-\> Autonomní Smyčka \-\> Hotový Produkt".

### **Fáze 1: The Meeting (Definice a Kontrakt)**

* **Proces:** Longin vede strukturovaný rozhovor s uživatelem. Klade otázky, aby odstranil ambiguitu.  
* **Cíl:** Vygenerovat **DoD (Definition of Done)** a sadu akceptačních kritérií.  
* **Výstup:** Soubor task\_manifest.json, který schválí uživatel.

### **Fáze 2: The Architect (Testy jako Specifikace)**

* **Princip:** Kód neexistuje bez testu.  
* **Akce:** Longin vygeneruje test\_suite.py (Pytest), který pokrývá všechny body z DoD. Tyto testy v první fázi selhávají (Red phase).

### **Fáze 3: The Grind (Autonomní Smyčka v Sandboxu)**

* **Cyklus:**  
  1. Write Code \-\> Uložení do souboru.  
  2. Execute Tests \-\> Spuštění v Sibling kontejneru.  
  3. Analyze Stderr \-\> Pokud chyba, Longin se opraví sám.  
* **Izolace:** Uživatel nevidí tento proces, pokud si nevyžádá "Live Log". Longin neobtěžuje uživatele s chybami syntaxe.

### **Fáze 4: The Presentation (Předání)**

* **Podmínka:** Všechny testy jsou zelené.  
* **Akce:** Longin prezentuje výsledek (např. běžící UI komponentu nebo funkční skript) a žádá o merge do produkce.

## ---

**4\. Vývojářský Implementační Plán (Step-by-Step)**

Tento plán obsahuje odkazy na GitHub repozitáře, které použijeme jako *referenční implementace* (studijní materiál).

### **Fáze A: Infrastruktura a Síť (The Nervous System)**

**Cíl:** Zprovoznit komunikaci mezi stroji a základní databázovou vrstvu.

1. **Krok A.1: Docker Compose Stack**  
   * *Úkol:* Definovat služby: redis (alpine), postgres (pgvector image), nexus-kernel (Python), cortex-ui (Node).  
   * *Konfigurace:* Nastavit persistentní volumes pro Postgres a Redis data.  
2. **Krok A.2: Discovery Service (mDNS)**  
   * *Úkol:* Implementovat discovery.py běžící na Nexusu i Gangliích. Musí vysílat "Jsem tady, mám GPU" a naslouchat "Kdo je tady?".  
   * *Referenční Repo:* **python-zeroconf/python-zeroconf** \- Pro čistou implementaci mDNS v Pythonu.  
3. **Krok A.3: Ganglion Client**  
   * *Úkol:* Vytvořit lehkou službu (FastAPI), která běží na klientech a přijímá příkazy (CMD\_EXEC, CMD\_LOAD\_MODEL).  
   * *Referenční Repo:* **ahodieb/PySimpleRPC** \- Pro inspiraci, jak implementovat jednoduché vzdálené volání funkcí.

### **Fáze B: Jádro a Paměť (The Brain)**

**Cíl:** Zprovoznit myšlení a paměť.

4. **Krok B.1: Sentinel & Redis Loop**  
   * *Úkol:* Napsat kernel.py, který se připojí k Redis Streamu, čte zprávy a podle "tagů" rozhoduje, který modul načíst.  
   * *Referenční Repo:* **redis-developer/redis-streams-hotel-jobs** \- Výborný příklad asynchronního zpracování streamů v Pythonu.  
5. **Krok B.2: Integrace Paměti (Mem0)**  
   * *Úkol:* Implementovat třídu MemoryManager, která obaluje mem0ai. Nastavit pgvector jako backend.  
   * *Referenční Repo:* **mem0ai/mem0** 6 \- Oficiální implementace, kterou upravíme pro naše schéma.  
6. **Krok B.3: Tool Server (FastMCP)**  
   * *Úkol:* Vytvořit interní API pro nástroje (čtení souborů, hledání v DB) pomocí protokolu MCP.  
   * *Referenční Repo:* **jlowin/fastmcp** 7 \- Pro vytvoření MCP serveru v Pythonu pomocí dekorátorů.

### **Fáze C: ERTDSD a Sandbox (The Hands)**

**Cíl:** Naučit systém bezpečně programovat.

7. **Krok C.1: Sibling Container Runner**  
   * *Úkol:* Implementovat třídu Sandbox, která používá docker-py k spouštění dočasných kontejnerů. Musí podporovat mountování pracovního adresáře.  
   * *Referenční Repo:* **All-Hands-AI/OpenDevin** (modul sandbox) 8 \- Zlatý standard pro bezpečné spouštění kódu agenty.  
8. **Krok C.2: AST Scanner**  
   * *Úkol:* Vytvořit security.py, který parsuje kód před spuštěním a hledá zakázané uzly (AST nodes).  
   * *Referenční Repo:* **PyCQA/bandit** \- Pro pochopení, jak procházet AST a hledat zranitelnosti.  
9. **Krok C.3: Orchestrace (LangGraph)**  
   * *Úkol:* Definovat stavový graf pro ERTDSD smyčku (uzly: Architect, Coder, Tester).  
   * *Referenční Repo:* **langchain-ai/langgraph** (examples/supervisor) \- Vzor pro hierarchické řízení agentů.

### **Fáze D: Frontend Cortex (The Face)**

**Cíl:** Vizuální rozhraní pro spolupráci.

10. **Krok D.1: Next.js \+ Puck Setup**  
    * *Úkol:* Inicializovat Next.js projekt a integrovat editor Puck.  
    * *Referenční Repo:* **puckeditor/puck** (recipe nextjs) 9 \- Oficiální příklad integrace.  
11. **Krok D.2: Dynamic Component Generation**  
    * *Úkol:* Vytvořit API endpoint, kam Kernel pošle JSON definici UI, a Cortex ji vykreslí.  
    * *Inspirace:* Systém v0.dev nebo Generative UI od Vercelu, ale implementovaný lokálně pomocí Puck komponent.  
12. **Krok D.3: Persistence UI**  
    * *Úkol:* Implementovat ukládání puck.data do PostgreSQL (JSONB sloupec) místo do souboru.  
    * *Referenční Repo:* **richardhightower/jsonb-postgresql** \- Best practices pro práci s JSONB v Postgresu.

## ---

**5\. Vývojářský Deník a Standardy (Rules of Engagement)**

### **5.1 Verzování a Commity**

* **Repo:** Monorepo (/kernel, /cortex, /ganglion).  
* **Branching:** main (production), dev (integration), feature/xyz (task).  
* **Commit Message:** Conventional Commits (feat: add mDNS discovery, fix: sandbox memory leak).

### **5.2 Dokumentace Kódu**

* Každá Python třída musí mít docstring popisující:  
  1. Účel (Intent).  
  2. Vstupy/Výstupy (Typed).  
  3. Vedlejší efekty (I/O, DB).  
* Markdown soubory v /docs musí být aktualizovány s každou změnou architektury.

### **5.3 Testovací Strategie**

* **Unit Testy:** Pro každou pomocnou funkci v Kernelu.  
* **Integration Testy:** Test komunikace Nexus \<-\> Ganglion (mockovaný network).  
* **Safety Testy:** Pokus o "útěk" ze sandboxu (musí selhat).

### **5.4 Kompatibilita**

* Veškerý kód musí být typovaný (mypy strict mode).  
* Python 3.11+ (pro optimalizace asyncio).  
* Docker kontejnery musí být založeny na slim verzích (Debian/Alpine) pro minimalizaci velikosti.

Tato dokumentace je závazná. Jakákoliv odchylka musí být schválena v procesu "Architect Review". Jsem připraven zahájit implementaci prvního kroku (Fáze A.1).

#### **Citovaná díla**

1. How to Use Redis Streams for Event Sourcing \- OneUptime, použito února 18, 2026, [https://oneuptime.com/blog/post/2026-01-21-redis-streams-event-sourcing/view](https://oneuptime.com/blog/post/2026-01-21-redis-streams-event-sourcing/view)  
2. Building Hybrid Search for RAG: Combining pgvector and Full-Text Search with Reciprocal Rank Fusion \- DEV Community, použito února 18, 2026, [https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk](https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk)  
3. Building a React Page Builder: An Introduction to Puck, použito února 18, 2026, [https://puckeditor.com/blog/building-a-react-page-builder-an-introduction-to-puck](https://puckeditor.com/blog/building-a-react-page-builder-an-introduction-to-puck)  
4. Containers — Docker SDK for Python 7.1.0 documentation, použito února 18, 2026, [https://docker-py.readthedocs.io/en/stable/containers.html](https://docker-py.readthedocs.io/en/stable/containers.html)  
5. Hijacking the AST to safely handle untrusted python \- Two Six Technologies, použito února 18, 2026, [https://twosixtech.com/blog/hijacking-the-ast-to-safely-handle-untrusted-python/](https://twosixtech.com/blog/hijacking-the-ast-to-safely-handle-untrusted-python/)  
6. Python SDK Quickstart \- Mem0 Documentation, použito února 18, 2026, [https://docs.mem0.ai/open-source/python-quickstart](https://docs.mem0.ai/open-source/python-quickstart)  
7. jlowin/fastmcp: The fast, Pythonic way to build MCP servers and clients \- GitHub, použito února 18, 2026, [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)  
8. Longin: Architektura autonomního kognitivního egosystému  
9. puckeditor/puck: Create your own AI page builder \- GitHub, použito února 18, 2026, [https://github.com/puckeditor/puck](https://github.com/puckeditor/puck)