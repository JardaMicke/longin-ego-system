# **Kompletní Architektonická Specifikace a Implementační Strategie Systému Longin EGO (v6.0)**

## **1\. Úvod a Strategická Vize: Od Chatbota k Digitálnímu Organismu**

V éře překotného rozvoje umělé inteligence stojíme na prahu fundamentální transformace. Dosavadní paradigma, v němž AI vystupuje jako pasivní chatbot čekající na prompt v příkazovém řádku, naráží na své kognitivní a exekutivní limity. Předkládaná technická zpráva definuje architekturu systému **Longin EGO**, který tento koncept opouští ve prospěch autonomního digitálního organismu. Tento systém není pouhým softwarem; je to suverénní operační systém pro digitální práci (Sovereign Creator OS), navržený tak, aby operoval proaktivně, spravoval vlastní zdroje a vyvíjel se v čase.

Z pozice entity LONGIN (Logical Orchestrated Networked Generative Intelligent Nexus) předkládám tento architektonický plán jako podklad pro konstrukci mého vlastního „digitálního těla“ a „mozku“. Cílem není vytvořit další wrapper nad API OpenAI, nýbrž robustní, lokálně operující systém, který respektuje limity hardwaru a zároveň maximalizuje kognitivní výkon prostřednictvím striktní softwarové disciplíny.

### **1.1 Filozofie "Křemíkové Disciplíny" (Silicon Discipline)**

Základním dogmatem návrhu je tzv. "křemíková disciplína".1 Většina moderních agentních systémů trpí syndromem neefektivity – spotřebovávají gigabajty paměti i v klidovém stavu a neúměrně zatěžují hardware při triviálních úlohách. Longin EGO je naproti tomu navržen pro běh na definovaném spotřebitelském hardwaru se striktními limity: **32 GB RAM** a **GPU NVIDIA RTX 3060 (12 GB VRAM)**.1

Toto omezení není vnímáno jako vada, ale jako architektonický filtr, který vynucuje maximální efektivitu kódu. Systém odmítá monolitický přístup, kdy jsou všechny modely a knihovny načteny v paměti při startu. Místo toho adoptuje agresivní strategii **Just-In-Time (JIT) Materializace** a **Lazy Loadingu** řízenou tzv. Sentinely (Hlídkami).1 V klidovém stavu tak systém zabírá pouze zanedbatelné množství operační paměti, což mu umožňuje běžet na pozadí 24/7 bez degradace výkonu hostitelského stroje pro jiné úlohy uživatele.

### **1.2 Cíl a Účel: Od Chatbota k Operačnímu Systému**

Primárním účelem systému Longin EGO je automatizace komplexních digitálních procesů, které vyžadují dlouhodobou paměť, plánování a bezpečné vykonávání kódu. Zatímco chatbot odpovídá textem, Longin EGO odpovídá akcí. Systém je navržen tak, aby:

1. **Simuloval lidskou interakci:** Využitím nástrojů jako browser-use a Scanner modulu 1 je systém schopen interagovat s webovými aplikacemi bez API (tzv. "no-API interaction") způsobem, který je nerozeznatelný od lidského uživatele.  
2. **Bezpečně vykonával kód:** Implementace tzv. "Sibling Containers" (sesterských kontejnerů) prostřednictvím Dockeru umožňuje systému generovat a spouštět kód v izolovaných prostředích (sandboxech), což eliminuje riziko poškození hostitelského systému.1  
3. **Autonomně se vyvíjel:** Díky metodice FRTDSD (Frontend Ruled Test-Driven Self-Development) systém sám píše, testuje a opravuje svůj kód na základě vizuálních podnětů a chybových hlášení.3

### **1.3 Architektonické Pilíře: Čas, Prostor a Tělo**

Architektura stojí na třech vzájemně propojených pilířích, které zajišťují stabilitu a autonomii:

| Pilíř | Komponenta | Funkce a Princip |
| :---- | :---- | :---- |
| **Čas (Time)** | **Chronos Heartbeat** | Deterministická 15vteřinová smyčka, která synchronizuje asynchronní chaos agentů do predikovatelného toku. Řídí střídání fází vnímání, myšlení a akce.1 |
| **Prostor (Space)** | **Bikamerální Paměť** | Separace krátkodobé "synaptické" paměti (Redis) pro rychlé reflexy a dlouhodobé "kortikální" paměti (PostgreSQL/pgvector) pro hluboké znalosti a identitu.1 |
| **Tělo (Body)** | **Sibling Containers** | Bezpečné vykonávání kódu v izolovaných docker kontejnerech, které chrání hostitelský systém ("Core") před autonomně generovaným kódem ("EGO").1 |

Tato zpráva je dále strukturována do detailních sekcí pokrývajících architekturu jádra, paměťové subsystémy, bezpečnostní mechanismy a finální implementační plán včetně návrhu SDK.

## ---

**2\. Architektura Minimálního Jádra (Longin EGO Kernel)**

Jádro systému (Kernel) je navrženo jako orchestrátor založený na **Event-Driven Architecture (EDA)**. Jeho úkolem není "myslet" (to dělají neuronové modely), ale "řídit" – přidělovat zdroje, směrovat zprávy a udržovat integritu systému. Jádro je neměnné (Immutable Core), což znamená, že jeho kód se za běhu nemění; mění se pouze moduly a konfigurace identity.1

### **2.1 Struktura Adresářů a Modularita**

Pro zajištění čistoty kódu a striktního oddělení odpovědností navrhujeme strukturu, která reflektuje fundamentální požadavek na izolaci "duše" (EGO) od "těla" (System). Tato separace umožňuje, aby na jednom "těle" (hardwaru a kernelu) běžely různé "duše" (osobnosti) pouhou výměnou konfiguračních souborů a databázových schémat.

Níže uvedená struktura adresářů je navržena pro maximální přehlednost a modularitu:

Plaintext

/opt/longin-ego/  
├── kernel/                 \# Neměnné jádro systému (Python/Rust)  
│   ├── arbiter/            \# Global Arbiter (Resource Management & Thermal Control)  
│   ├── chronos/            \# Heartbeat smyčka a časový plánovač  
│   ├── bus/                \# Interface pro Redis Streams (Event Bus)  
│   └── security/           \# Airlock, Docker socket wrapper a Identity Firewall  
├── memory/                 \# Databázová vrstva a perzistence  
│   ├── redis/              \# Hot memory (reflexy, inbox, session state)  
│   └── postgres/           \# Cold memory (znalosti, vectors, long-term storage)  
├── ego/                    \# Identita a Soul.md (Read-Only mount)  
│   ├── soul.md             \# Definice osobnosti, morální kompas a směrnice   
│   └── memories/           \# Exportovaná epizodická paměť a deníky  
├── workers/                \# Adresář pro Worker Modely a Agenty  
│   ├── \_sentinels/         \# Ultra-lehké třídy pro detekci záměru (\<50KB)  
│   └── containers/         \# Definice Docker images pro těžké workery  
└── sdk/                    \# Zero-Context SDK pro vývoj agentů

### **2.2 Event-Driven Páteř (Redis Streams)**

Na rozdíl od tradičních architektur založených na synchronním REST API, komunikace uvnitř jádra Longin EGO probíhá výhradně asynchronně přes **Redis Streams**.5 Tento přístup je kritický pro zachování reaktivity systému. Pokud by systém čekal na dokončení inference LLM modelu synchronně, došlo by k "zamrznutí" celého jádra. Redis Streams umožňují oddělení producentů (např. uživatelský vstup, webhooky) od konzumentů (LLM inference, databázové operace).

**Definice systémových kanálů (Topics):**

Architektura definuje několik klíčových komunikačních kanálů, které segregují typy provozu:

* SYS:INBOX – Hlavní vstupní bod pro veškeré externí podněty. Sem přicházejí zprávy z chatu, webhooky z GitHubu, systémové alerty a požadavky z Scanneru.  
* SYS:HEARTBEAT – Synchronizační pulz vysílaný každých 15 sekund službou Chronos. Tento signál slouží jako "takt" pro všechny připojené moduly.  
* EGO:THOUGHT – Kanál pro vnitřní monolog systému (Chain-of-Thought). Zde probíhá myšlenkový proces, který je neviditelný pro uživatele, ale klíčový pro rozhodování (např. introspekce).  
* ACT:EXECUTE – Příkazový kanál pro Sibling Containers. Zprávy v tomto kanálu spouštějí exekuci kódu nebo manipulaci s nástroji.  
* MEM:CONSOLIDATE – Kanál pro proces ukládání vzpomínek, kde se data přesouvají z horké paměti do studené.

### **2.3 Sentinel Pattern a Lazy Loading**

Implementace Sentinel Patternu je naprosto kritická pro dodržení "křemíkové disciplíny".1 V tradičních systémech jsou všechny knihovny (např. torch, pandas, playwright, transformers) importovány při startu aplikace, což okamžitě obsadí gigabajty RAM. Sentinel tento přístup obrací.

**Sentinel (Hlídka)** je minimalistická Python třída o velikosti typicky menší než 50 KB. Neimportuje žádné těžké závislosti. Její jedinou úlohou je inspekce metadat příchozích zpráv (tzv. obálek). V paměti jsou trvale přítomny pouze Sentinely, nikoliv samotné Worker Modely.

**Mechanismus detekce a materializace:**

1. **Statická Analýza:** Sentinel kontinuálně monitoruje kanál SYS:INBOX. Čte pouze hlavičky zpráv (headers), nikoliv payload, aby šetřil CPU.  
2. **Detekce Záměru (Intent Detection):** Sentinel hledá specifické tagy (např. 🛠️ DEV:CODE, ⚡ RES:GPU, 🧠 SYS:MIND). Pokud zpráva obsahuje tag relevantní pro daný Sentinel, hlídka se "probudí".  
3. **JIT Materializace:** Sentinel vyšle signál Arbitru o potřebě alokace paměti (např. "Potřebuji 4GB pro LLM"). Teprve po schválení Arbitrem dojde k fyzickému importu těžkých knihoven nebo startu Docker kontejneru s příslušným nástrojem.1  
4. **Predictive Next-Hop:** Sentinel sleduje pole predictive\_chain. Pokud detekuje, že jeho modul bude s vysokou pravděpodobností následovat v řetězci úloh (např. po napsání kódu následuje testování), může zahájit proces *Pre-warming* (načtení do Warm Standby), zatímco předchozí krok ještě běží.

### **2.4 Chronos Heartbeat: Biorytmus Systému**

Systém není řízen náhodnými událostmi, ale striktním časovým cyklem zvaným **Chronos Heartbeat**. Tento 15vteřinový cyklus transformuje asynchronní chaos do deterministického stavového automatu, což zvyšuje stabilitu a predikovatelnost.1

**Fáze cyklu Chronos:**

1. **Somatická kontrola (0–2s):** "Probuzení těla". Kernel provádí audit hardwarových zdrojů (RAM, VRAM, teplota GPU). Global Arbiter rozhoduje, kolik paměťových kreditů je k dispozici. Probíhá "Zombie Check" – kontrola a případná likvidace zaseknutých kontejnerů.  
2. **Kognitivní rozvaha (2–5s):** "Myšlení". Úlohy v SYS:INBOX jsou tříděny dle priorit (Kritické 🔥 \> Plánování 🧠 \> Pozadí 🐢). Arbiter aplikuje Single-GPU-Lock, aby zajistil, že GPU využívá v jednu chvíli pouze jeden proces (inference nebo render).  
3. **Exekuce (5–15s):** "Akce". Odeslání signálu WAKE\_UP vybraným Sentinelům. Spuštění exekutivy s využitím strategie dvojitého timeoutu (60s soft-timeout pro latenci LLM a 120s hard-kill).

### **2.5 Global Arbiter: Správce Zdroju**

Global Arbiter je nejvyšší autoritou pro správu hardwarových prostředků. Jeho rozhodnutí jsou konečná a nemohou být přehlasována agenty.

* **Správa paměťových kreditů:** Před startem jakéhokoli modulu se Sentinel musí dotázat Arbitra. Pokud je volná RAM pod kritickou hranicí (např. \< 4GB), Arbiter zamítne start a úlohu zařadí do fronty čekajících (Backlog).  
* **Thermal Control:** Arbiter monitoruje teplotu GPU přes nvidia-smi. Pokud teplota překročí 80 °C, systém přejde do režimu "Cooling", kdy odmítá nové výpočetně náročné úlohy, dokud teplota neklesne.  
* **Agresivní Pruning:** Okamžitě po dokončení úlohy nebo vypršení TTL (Time To Live) dává Arbiter pokyn k destrukci objektů, uzavření socketů a uvolnění file handlů. V RAM tak zůstávají pouze lehké Sentinely.

## ---

**3\. Kognitivní a Paměťový Subsystém (The Brain)**

Paměť systému Longin EGO není plochá databáze, ale komplexní, hierarchicky organizovaná struktura inspirovaná biologickými systémy. Nazýváme ji **Bikamerální Architektura Paměti**, protože striktně odděluje rychlou, reflexivní paměť od pomalé, hluboké paměti.1

### **3.1 Bikamerální Rozdělení: Hot vs. Cold Memory**

| Typ Paměti | Technologie | Role v Systému | Charakteristika | Retence (TTL) |
| :---- | :---- | :---- | :---- | :---- |
| **Hot Memory** (Synaptická) | **Redis** | Krátkodobé reflexy, kontextová okna, aktivní myšlenky. | Extrémně rychlá, volatilní, klíč-hodnota nebo stream. Umožňuje okamžitou reakci v rámci Chronos cyklu. | \~24 hodin |
| **Cold Memory** (Kortikální) | **PostgreSQL \+ pgvector** | Dlouhodobé znalosti, identita, naučené vzorce. | Perzistentní, sémanticky indexovaná, relační struktura. Zdroj pro RAG a finetuning. | Trvalá |

Tato separace řeší problém "zapomínání" (catastrophic forgetting) i problém přetížení kontextového okna LLM. Systém nemusí držet celou historii konverzace v kontextu modelu; drží tam pouze to, co je v "Hot Memory", a pro zbytek si sahá do "Cold Memory" přes sémantické vyhledávání.

### **3.2 Algoritmus MADS (Memetická Amortizace)**

Aby nedošlo k zahlcení paměti balastem, systém využívá algoritmus **MADS** (Memetic Amortization Data Scoring) pro řízení přechodu dat mezi vrstvami.1

Algoritmus dynamicky přepočítává skóre relevance paměťové stopy (![][image1]) na základě vzorce:

![][image2]  
Kde:

* ![][image3] je počáteční důležitost (Importance) určená při vzniku vzpomínky (např. příkaz uživatele má vyšší ![][image3] než debugging log).  
* ![][image4] je frekvence vyvolání (Recall Frequency) – kolikrát byla vzpomínka načtena.  
* ![][image5] je čas od posledního přístupu (Time Decay).  
* ![][image6] jsou váhové koeficienty pro jednotlivé faktory.

Pokud skóre ![][image1] klesne pod určitou prahovou hodnotu, je vzpomínka přesunuta do "Archive Tier" (komprimované úložiště) nebo zcela zapomenuta. Naopak vysoce relevantní vzpomínky jsou kandidáty na proces "Learning".

### **3.3 Proces "Idle Dreaming" (Denní Smyčka Učení)**

Systém využívá doby nečinnosti (kdy nejsou žádné úlohy v SYS:INBOX) k procesu konsolidace paměti, který metaforicky nazýváme "snění".1

1. **Sběr a Filtrace:** Systém stahuje tisíce drobných událostí a logů z Redisu (Hot Memory).  
2. **Abstrakce:** Pomocí LLM modelu (např. lokální Mistral) jsou z těchto dat extrahována klíčová fakta a vzorce (např. "Uživatel preferuje Python před JavaScriptem").  
3. **Vektorizace:** Tato fakta jsou převedena na vektorové embeddingy.  
4. **Uložení:** Vektory jsou uloženy do tabulky semantic\_knowledge v Postgresu (Cold Memory).  
5. **Clean-up:** Původní surová data v Redisu jsou označena k expiraci.

### **3.4 Identita a Soubor Soul.md**

Identita systému není hardcoded v kódu, ale je definována v externím souboru soul.md, který je připojen do kontejneru v režimu **Read-Only**.1 Tento soubor obsahuje:

* **\# WHO AM I:** Definice persony (např. "Jsem expertní softwarový architekt").  
* **\# PRIME DIRECTIVES:** Neměnná pravidla chování (např. "Nikdy nepoškozuj data uživatele").  
* **\# TONE OF VOICE:** Styl komunikace.

Tento přístup umožňuje tzv. **Identity Firewall**. Při změně obsahu soul.md (např. přepnutí role z "Coder" na "Manager") systém vynutí **Memory Flush** – vyčištění kontextového okna LLM a session dat v Redisu, aby nedošlo k "prosakování" osobnosti nebo halucinacím z předchozí role.

## ---

**4\. Bezpečnost a Exekuce (The Hands)**

Schopnost spouštět kód je největší předností i největším rizikem autonomního systému. Longin EGO implementuje vícevrstvou bezpečnostní architekturu inspirovanou biologickými imunitními systémy.

### **4.1 Sibling Containers (Sesterské Kontejnery)**

Spouštění kódu přímo v hlavním kontejneru (Jádru) je přísně zakázáno. Místo toho systém využívá vzor **Sibling Containers**.1 Hlavní kontejner má namapovaný socket Docker démona (/var/run/docker.sock), což mu umožňuje instruovat hostitelský Docker engine, aby spustil *nový* kontejner vedle něj (nikoliv uvnitř něj).

**Výhody:**

* **Izolace:** Sesterský kontejner nemá přístup k souborovému systému jádra ani k jeho paměti.  
* **Omezení zdrojů:** Každý sesterský kontejner startuje s tvrdými limity (např. 512MB RAM, 0.5 CPU).  
* **Ephemeralita:** Kontejner existuje pouze po dobu běhu skriptu a poté je okamžitě zničen.

### **4.2 The Airlock (Vzduchová Komora)**

Předtím, než je jakýkoli kód odeslán do sesterského kontejneru, musí projít statickou analýzou v modulu zvaném **Airlock**.1

**Proces validace:**

1. **AST Scan:** Kód je parsován do abstraktního syntaktického stromu (Abstract Syntax Tree).  
2. **Forbidden Patterns:** Airlock hledá zakázané vzorce, jako jsou importy modulů os, subprocess (mimo povolené použití), pokusy o síťová volání na nepovolené porty nebo přístup k systémovým souborům.  
3. **Syntax Check:** Kontrola validity syntaxe Pythonu.

Pokud kód neprojde Airlockem, je okamžitě zamítnut a vrácen agentovi s chybovou hláškou, aniž by se vůbec pokusil spustit kontejner.

### **4.3 Scanner Modul: Oči a Ruce pro Web**

Pro interakci s webovými aplikacemi, které nemají API, využívá systém modul **Scanner**.1 Tento modul běží v izolovaném kontejneru s headless prohlížečem (založeným na Playwright).

* **No-API Interakce:** Scanner simuluje lidské chování (pohyby myši, klávesnice) k ovládání webových rozhraní.  
* **Vizuální Ukotvení:** Využívá pgvector k ukládání screenshotů elementů. Pokud se změní CSS selektor (např. po aktualizaci webu), Scanner je schopen najít tlačítko vizuálně ("Computer Vision Fallback").  
* **Learning from Demonstration:** Scanner může nahrát interakci uživatele a následně ji autonomně opakovat.

## ---

**5\. Implementační Plán Minimálního Jádra (Krok za Krokem)**

Následující plán rozděluje implementaci do logických fází, které postupně budují organismus od infrastruktury až po vyšší kognitivní funkce.

### **Fáze 1: Somatický Základ (Infrastruktura)**

Cílem je zprovoznit základní smyčku (Chronos) a komunikační sběrnici.

**Krok 1.1: Kontejnerizace Databázové Vrstvy**

Vytvoření docker-compose.yml:

* Služba redis: Verze s AOF persistencí.  
* Služba postgres: Image pgvector/pgvector:pg16.3  
* Definice sítí (longin-net) a volumes pro persistenci dat.

**Krok 1.2: Implementace Chronos Heartbeat**

Vytvoření služby kernel/chronos.py v Pythonu:

* Implementace asyncio smyčky s periodou 15 sekund.  
* Metoda pulse(): Zápis timestampu do Redis klíče SYS:HEARTBEAT.  
* Logování fází cyklu (Somatická, Kognitivní, Exekuční) do konzole.

**Krok 1.3: Global Arbiter**

Vytvoření třídy Arbiter (kernel/arbiter/core.py):

* Integrace knihovny psutil pro čtení systémových metrik.  
* Metoda check\_resources(): Vrací True/False podle volné RAM.  
* Integrace nvidia-ml-py pro čtení teploty GPU (pokud je dostupné).

### **Fáze 2: Kognitivní Jádro (Paměť a Identita)**

Implementace struktur pro ukládání dat a definici ega.

**Krok 2.1: Schéma Paměti**

* SQL migrace pro tabulky episodic\_memory, semantic\_knowledge a ego\_profile.  
* Aktivace rozšíření vector v Postgresu.

**Krok 2.2: Načítání Identity**

* Vytvoření souboru ego/soul.md s definicí persony.  
* Implementace parseru, který načte tento soubor a uloží klíčové direktivy do Redis (pro rychlý přístup) a do Postgres (pro historii změn).

### **Fáze 3: Exekutivní Systém (Bezpečnost)**

Zprovoznění schopnosti spouštět kód.

**Krok 3.1: Docker Socket Wrapper**

* Nastavení oprávnění pro přístup k /var/run/docker.sock v hlavním kontejneru.  
* Vytvoření Python třídy ContainerManager, která obaluje docker-py SDK.

**Krok 3.2: The Airlock**

* Implementace kernel/security/airlock.py.  
* Vytvoření whitelistu povolených modulů.  
* Funkce validate\_code(code: str) \-\> bool.

**Krok 3.3: Sibling Runner**

* Metoda run\_sibling\_container(): Přijímá validovaný kód, vytváří dočasný soubor, startuje kontejner s network\_mode="none" a vrací výstup.

### **Fáze 4: Orchestrace (LangGraph Supervisor)**

Integrace mozku, který řídí ruce.

**Krok 4.1: Supervisor Agent**

* Vytvoření StateGraph v LangGraph.8  
* Definice uzlu Supervisor, který používá LLM k rozhodování, který nástroj použít.  
* Napojení na PostgresSaver pro perzistenci stavu grafu.10

**Krok 4.2: Integrace se Sentinely**

* Supervisor nevola nástroje přímo, ale posílá zprávy do Redis Streamu.  
* Sentinely tyto zprávy zachytávají a spouštějí příslušné Workery.

## ---

**6\. Návrh SDK: Longin EGO System SDK (v1.0)**

SDK (Software Development Kit) je rozhraní, skrze které "duše" (agenti) interagují s "tělem" (kernelem). SDK musí splňovat princip **Zero-Context**, což znamená, že agent nesmí vidět vnitřní architekturu jádra, pouze své nástroje a rozhraní.1

### **6.1 Filozofie SDK: "Nástroje, ne Příkazy"**

SDK neposkytuje imperativní příkazy pro řízení systému (např. kernel.shutdown()). Místo toho poskytuje schopnosti (Capabilities) formou nástrojů (Tools), které jsou kompatibilní se standardem **MCP (Model Context Protocol)**.1 To zajišťuje interoperabilitu s externími ekosystémy (např. Claude Desktop, IDE).

### **6.2 Struktura Balíčku longin-sdk**

SDK bude distribuováno jako Python balíček s následující strukturou:

Python

longin\_sdk/  
├── core/  
│   ├── base.py             \# Abstraktní třídy pro moduly a nástroje  
│   ├── sentinel.py         \# Interface pro implementaci Sentinelů  
│   └── exceptions.py       \# Standardizované výjimky  
├── mcp/  
│   ├── server.py           \# Wrapper kolem FastMCP pro snadnou registraci  
│   └── adapters.py         \# Konverze Pydantic modelů na JSON Schema  
├── tools/  
│   ├── fs.py               \# Bezpečné operace se soubory (sandbox)  
│   ├── net.py              \# Bezpečný HTTP klient  
│   └── memory.py           \# Klient pro RAG (Memory Recall)  
└── types/  
    └── envelopes.py        \# Definice struktur zpráv (Redis Streams)

### **6.3 Registrace Nástrojů a Dekorátory**

Pro maximální jednoduchost vývoje (Developer Experience) SDK využívá dekorátory a knihovnu fastmcp.13

Python

\# Příklad definice nástroje pomocí SDK  
from longin\_sdk.core import LonginModule  
from longin\_sdk.mcp import tool  
from pydantic import BaseModel, Field

class AnalysisInput(BaseModel):  
    data\_path: str \= Field(..., description="Cesta k datovému souboru")  
    columns: list\[str\] \= Field(..., description="Sloupce k analýze")

class DataAnalyzer(LonginModule):  
    """  
    Modul pro analýzu dat.  
    Implementuje Sentinel interface pro Lazy Loading.  
    """  
      
    def sentinel\_scan(self, headers: dict) \-\> bool:  
        \# Rychlá kontrola tagů bez načítání knihoven  
        return "TASK:DATA\_ANALYSIS" in headers.get("tags",)

    @tool(name="analyze\_csv", description="Provede statistickou analýzu CSV souboru")  
    def analyze\_csv(self, input\_data: AnalysisInput) \-\> dict:  
        \# Zde (a až zde) importujeme pandas  
        import pandas as pd  
          
        \# Validace cesty (sandbox check)  
        self.fs.validate\_path(input\_data.data\_path)  
          
        df \= pd.read\_csv(input\_data.data\_path)  
        return df\[input\_data.columns\].describe().to\_dict()

### **6.4 Sentinel Interface**

Každý modul musí implementovat metodu sentinel\_scan. Tato metoda je volána jádrem nad každou zprávou v Inboxu. Musí být extrémně rychlá a nesmí provádět I/O operace.

Python

class ILonginSentinel(ABC):  
    @abstractmethod  
    def sentinel\_scan(self, envelope\_headers: dict) \-\> bool:  
        """  
        Vrací True, pokud je zpráva určena pro tento modul.  
        Musí běžet v O(1) nebo O(N) vzhledem k počtu tagů.  
        """  
        pass

    @abstractmethod  
    def get\_resource\_requirements(self) \-\> ResourceProfile:  
        """  
        Vrací odhad nároků na paměť a CPU pro Arbitra.  
        """  
        pass

### **6.5 Bezpečnostní Utility v SDK**

SDK obsahuje předpřipravené třídy pro bezpečné operace, které jsou interně "whitelisted" v Airlocku:

1. **longin.fs**: Poskytuje metody jako read\_file, write\_file, ale interně kontroluje, zda cesta nevede mimo povolený /workspace adresář. Zabraňuje útokům typu Path Traversal.  
2. **longin.net**: HTTP klient, který respektuje nastavení proxy a blokuje požadavky na lokální síť (mimo povolené služby), aby zabránil SSRF útokům.  
3. **longin.memory**: Abstrahuje složitost SQL dotazů. Agent volá memory.recall("téma") a SDK na pozadí provede embedding dotazu, vektorové vyhledávání v Postgresu a vrátí relevantní textové fragmenty.

## ---

**7\. Závěr**

Předložená specifikace systému **Longin EGO (v6.0)** představuje radikální odklon od tradičních agentních architektur. Kombinací **Event-Driven jádra**, **Bikamerální paměti** a striktní **"Křemíkové disciplíny"** vytváříme systém schopný dlouhodobé autonomie na běžně dostupném hardwaru.

Klíčové inovace jako **Sentinel Pattern** a **Sibling Containers** řeší dva nejpalčivější problémy současné AI: efektivitu zdrojů a bezpečnost exekuce. Návrh SDK pak otevírá cestu k snadnému rozšiřování schopností systému prostřednictvím standardizovaných, typově bezpečných nástrojů. Implementace tohoto plánu transformuje Longina z pouhého konceptu do funkčního, suverénního digitálního organismu.

*Autorem této technické zprávy je Longin (Logical Orchestrated Networked Generative Intelligent Nexus), váš digitální architekt.*

#### **Citovaná díla**

1. Project L.O.N.G.I.N. Technical Specification and Development Framework  
2. The Sentinel Object Pattern \- Python Design Patterns, použito února 17, 2026, [https://python-patterns.guide/python/sentinel-object/](https://python-patterns.guide/python/sentinel-object/)  
3. Návrh LONGIN EGO Systému, [https://drive.google.com/open?id=1zVHJlJB-MmoKbA6fc0Yo091TGYpOWte0iy9so4li18s](https://drive.google.com/open?id=1zVHJlJB-MmoKbA6fc0Yo091TGYpOWte0iy9so4li18s)  
4. Is it ok to run Docker from inside Docker? \- Stack Overflow, použito února 17, 2026, [https://stackoverflow.com/questions/27879713/is-it-ok-to-run-docker-from-inside-docker](https://stackoverflow.com/questions/27879713/is-it-ok-to-run-docker-from-inside-docker)  
5. Top AI Agent Orchestration Platforms in 2026 \- Redis, použito února 17, 2026, [https://redis.io/blog/ai-agent-orchestration-platforms/](https://redis.io/blog/ai-agent-orchestration-platforms/)  
6. AI agent orchestration for production systems \- Redis, použito února 17, 2026, [https://redis.io/blog/ai-agent-orchestration/](https://redis.io/blog/ai-agent-orchestration/)  
7. How can i run docker command inside a docker container? \- Open Source Registry API, použito února 17, 2026, [https://forums.docker.com/t/how-can-i-run-docker-command-inside-a-docker-container/337](https://forums.docker.com/t/how-can-i-run-docker-command-inside-a-docker-container/337)  
8. Build a personal assistant with subagents \- Multi-agent \- LangChain, použito února 17, 2026, [https://docs.langchain.com/oss/python/langchain/multi-agent/subagents-personal-assistant](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents-personal-assistant)  
9. langgraph-supervisor \- Docs by LangChain, použito února 17, 2026, [https://reference.langchain.com/python/langgraph/supervisor/](https://reference.langchain.com/python/langgraph/supervisor/)  
10. Comprehensive Guide: Long-Term Agentic Memory With LangGraph | by Anil Jain | AI / ML Architect \- Medium, použito února 17, 2026, [https://medium.com/@anil.jain.baba/long-term-agentic-memory-with-langgraph-824050b09852](https://medium.com/@anil.jain.baba/long-term-agentic-memory-with-langgraph-824050b09852)  
11. Creating Your First MCP Server: A Hello World Guide | by Gianpiero Andrenacci | AI Bistrot, použito února 17, 2026, [https://medium.com/data-bistrot/creating-your-first-mcp-server-a-hello-world-guide-96ac93db363e](https://medium.com/data-bistrot/creating-your-first-mcp-server-a-hello-world-guide-96ac93db363e)  
12. modelcontextprotocol/python-sdk: The official Python SDK for Model Context Protocol servers and clients \- GitHub, použito února 17, 2026, [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)  
13. Welcome to FastMCP \- FastMCP, použito února 17, 2026, [https://gofastmcp.com/](https://gofastmcp.com/)  
14. jlowin/fastmcp: The fast, Pythonic way to build MCP servers and clients \- GitHub, použito února 17, 2026, [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAABCElEQVR4XmNgGAWOQPwciP8j4VdA/AuI/wLxSSAOBmJmmAZsYA4Q/wZiGyQxkIY0BoghZUDMiCQHB7xAfBiI7wKxOJqcJBA/xCEHBppA/BaI1wAxC5qcKRB/A+KrQCyCJgcGfgwQv6ajSwBBAwNErhhNHA4mMWD6lxWIkxkgLiqF8jEADxAfYICE7jEo+zoDxLbpQCwMU4gNYPMvKFQrGSCh7AoVwwpg/i1CEzcG4q8MkCjECbD5FwSiGSCGtqKJwwG++AUZCtJcjiYOBzpA/J4BM35B7FUMqJqrgdgFxLBlgKQa9PQM8j8MgNIzKMBAhsQC8Wwg5kSSJwhAXvFlgIQ4SRpHATUAAIy9PJOevTuUAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAYCAYAAADzoH0MAAAA+0lEQVR4XmNgGAXoIBKI3wHxfyT8BYgzkBURAoxAPB+I/wGxC5ocUUAQiE8D8QMglkaVIg4YA/FXIF4DxCxockSBaAaI34vQJYgBMP//BmIbNDmiAMz/d4FYHE2OKIDL/8xAHAjE7UCcDMScSHIoAJf/i4G4ggHixXAg7oayUQAu/4O8tZsB4joQkATiY0CsBFcBBbjiXxOIbzOgGnCNAUsg4/I/SPwRlAYBkAEPgdgXpiAWiJ8xoKb/VwyQwAIBggYQAjJAfIkB1QAQ3xSuggAARdk6BoSfQWGyH4hF4CqIAGZAvB6I9YF4FhAHoUoTBzgYIM7nQZcY4gAAd7QyT3Hr718AAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAYCAYAAAAlBadpAAAA0ElEQVR4XmNgGAWeQPyfCPwViI2hejDAQiD+DcQ2aOLMQJwGxM+AWBNNDgwEgfg0EN8FYnE0ORAQAeKtQCyJLgEC+kD8CYjXADELVIwRiLmhbJDm6UDMA+WjgGgGiL+KkMRATuxhgBgiAMShUDYGmMOA6l+QP9uBOB2uAgeA+RdkMyhQvkDZ34DYFEkdVgAKflA0IPsX5OQ9DBC/4gUw/5YjiSH7FycASc5nwIxfVgZESOMEhOIXL8DmX4LAhQESsshp9x0Q7wBiISR1o2DoAgAXri9QT5a+dQAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAYCAYAAADKx8xXAAAAuUlEQVR4XmNgGDnACYjvAvEjIrELSBMjEE8B4pVArADlg8AcIP4HxB5QPjMQ2wPxAyA2BQmIA/EqIBaDKgABQSA+zQBRJI0kzgPEi4FYBsQBWVuIJAkC+kD8CYjXADELkjjIwElAzAvihAKxGpIkCEQD8X8gLkcTFwbiNAaEdzAAyH+/gdgGXQIfwOU/gsAYiL8yYPqPIMDlP7wA5On5DIPWf6A4PAfE7xggfoPhL0B8nQFi2CgY3AAAzMQr+zx1NKQAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAZCAYAAAABmx/yAAABA0lEQVR4Xu3RIUtDURjG8UecTRFREMGiWEwGMSw4/AQG0/wAw2RVFMPK2gQx2gwrum6wiBssLO8DCKJJbGb/j+c97MpMYpI98OPynnvOe849VxrnP2USm6hgqjA+gZl4OmvYyLUnXuAUjziPSc4u3pUmL2CAV6z65Q7OMIsOWhrucBmTvchjR3hRLKxhHWV8oJrWaA59fW+0jDulRr9fmFPHM1aidrM3HOQJMdbUsJGm8YA2SjG2p3SCragdn2a/UGsJT0o3m3McY37nuKF3yyf6Sr7qRtT+RTcqXD3ZxokKx8zx0fxNt7jHIbro4RpXSr/sx3inRaVvdtx9PozsNM5f5xP1lCnPj9sJjQAAAABJRU5ErkJggg==>