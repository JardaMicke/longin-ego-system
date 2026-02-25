### Technický standard LONGIN-EGO-01: Architektura neměnného jádra a správa hardware zdrojů

#### 1\. Úvod do paradigmatu Sovereign Creator a technický rámec

Strategický význam systému  **LONGIN (Logical Orchestrated Networked Generative Intelligent Network)**  spočívá v jeho pojetí jako suverénního, lokálně operujícího digitálního organismu. Na rozdíl od konvenčních cloudových modelů, které představují formu digitálního poddanství, se LONGIN definuje jako  **Sovereign Creator OS** . Toto paradigma představuje totální odklon od centralizované AI směrem k absolutní digitální autonomii, kde Architekt (uživatel) vykonává plnou moc nad inferencí, daty i exekucí.Tento standard je přímo formován drakonickými limity hardware, definovanými jako  **32GB RAM a GPU NVIDIA RTX 3060 (12GB VRAM)** . V prostředí, kde LLM a doprovodné procesy běžně konzumují desítky gigabajtů, jsou tyto limity chápány jako  **existenciální hranice** . Stabilita systému vyžaduje nekompromisní „křemíkovou disciplínu“ v řízení životního cyklu zdrojů. Dokument je závaznou metodikou pro vývoj veškerých modulů; stabilita celku začíná u precizního vnímání času a absolutní kontroly nad fyzickým tělem systému.

#### 2\. Biorytmus systému: Chronos Heartbeat a drakonické řízení RAM

Vědomí systému LONGIN je řízeno striktní synchronizační smyčkou  **Chronos Heartbeat** . Tento 15vteřinový cyklus transformuje asynchronní chaos do predikovatelného stavového automatu, čímž zabraňuje kaskádovému kolapsu na limitovaném hardware.

##### Logika 15s EGO cyklu

Každý cyklus vynucuje tři fáze:

* **Somatická kontrola (0–2s):**  
* **Resource Audit:**  Kernel dotazuje OS na stav RAM/VRAM.  **Global Arbiter**  přiděluje paměťové kredity; moduly musí o kredit požádat před inicializací.  
* **Thermal Check:**  Při teplotě GPU \> 80 °C se vynucuje režim  *Cooling*  (blokace nových úloh).  
* **Heartbeat Ping:**  Moduly zapisují LAST\_ALIVE timestamp do Redis každých 5 sekund. Pokud je timestamp \> 30s, EGO provede SIGTERM, následovaný docker kill.  
* **Kognitivní rozvaha (2–5s):**  
* **Priority Sort:**  Třídění úloh v Redis Streams (kanál SYS:INBOX) dle tagů: 🔥 (Critical) \> 🧠 (Planning) \> 🐢 (Background).  
* **Decision:**  Alokace zdrojů na základě volných kreditů.  **Single-GPU-Lock**  zajišťuje, že GPU drží vždy pouze jedna instance (inference nebo render).  
* **Exekuce (5–15s):**  
* **Dispatch:**  Odeslání signálu WAKE\_UP.  
* **Double Timeout Strategy:**  Všechny konektory využívají 60s soft-timeout a 120s hard-kill pro kompenzaci latence lokálních modelů.

##### Mechanismy Pruningu

Agresivní uvolňování paměti ( **Pruning** ) probíhá okamžitě po vypršení TTL nebo splnění úkolu. Manager provádí explicitní destrukci: uzavírá sockety, ukončuje subprocessy a uvolňuje file handly, čímž v RAM zůstávají pouze ultra-lehké Sentinely.

#### 3\. Architektonický řetězec MSCA (Modul-Sentinel-Connector-Adapter)

Vzor MSCA umožňuje existenci komplexního ekosystému v rámci 32GB RAM díky „línému načítání“ a prediktivní aktivaci.

* **Sentinel (Hlídka):**  Statická třída (\<50KB), která analyzuje metadata v EventEnvelope. Sentinel neimportuje žádné těžké knihovny.  
* **Predictive Next-Hop:**  Sentinel využívá pole predictive\_chain v hlavičce zprávy. Pokud vidí svůj tag v následujícím kroku, iniciuje proces  **Pre-warming**  (načtení do Warm Standby), zatímco předchozí modul ještě běží.  
* **Materializace Modulů:**   *Just-In-Time*  instanciace těžkých závislostí (Torch, Playwright) až při potvrzené exekuci.| Vlastnost | Stav spánku (Sentinel) | Aktivní stav (Modul) || \------ | \------ | \------ || **Nároky na RAM** | \< 50 KB | 500 MB \- 12 GB || **Piktogramy** | 🎬, 🛠️, 🌐 (Statická detekce) | Exekuce logiky || **Závislosti** | Žádné (IEvent interface) | Plné (např. ffmpeg, pandas) || **Logika** | Next-Hop Prediction | State Machine |  
* **Konektory a Adaptéry:**  Konektory vynucují  **Circuit Breaking**  (izolace chyb), zatímco Adaptéry provádějí sémantickou transformaci a  **Self-healing**  při změnách externích API.

#### 4\. Bezpečnostní izolace: Sibling Containers a Air-Gap validace

Veškerý autonomně generovaný kód musí běžet v izolované „digitální digestoři“.

##### Protokol Sibling Container

Využívá Docker-in-Docker k vytvoření hermetických sandboxů:

* **Isolace:**  \--network none, limit 512MB RAM, 0.5 CPU.  
* **Časový zámek:**  Hard timeout  **5 sekund** , následovaný destrukcí.  
* **Browser Isolation:**  BrowserAdapter nesmí běžet v jádře; musí využívat kontejner browserless/chrome pro ochranu hostitele před webovými exploity.

##### Air-Gap Validátor a Zero-Context SDK

Před nasazením prochází kód statickou analýzou ( **AST Scan** ). Jsou zakázány „Forbidden Imports“ (např. os, sys, subprocess) mimo povolené rozhraní SDK. Moduly musí být validovány hermetickým testem a digitálně podepsány.

#### 5\. Princip neměnného jádra a bikamerální paměť

Separace „Těla“ (Systém) a „Duše“ (Identity) je klíčová pro stabilitu ega.

##### Separace System DB vs. EGO DB

Data jsou izolována pomocí Row-Level Security (RLS).| Databáze | Obsah | Práva || \------ | \------ | \------ || **System DB (Tělo)** | Registr modulů, hardware logy, API Vault. | Kernel / Shared. || **EGO DB (Duše)** | soul.md, epizodická paměť, shadow\_thoughts. | Izolováno pro EGO. |  
**Identity Firewall:**  Při přepnutí persony (např. Kodér \-\> Básník) Kernel vynucuje  **Memory Flush**  – promazání kontextového okna LLM a session dat v Redis k zamezení úniku API klíčů nebo fragmentů identity.

##### MADS Algoritmus a Finetuning

Paměť je vrstvena podle algoritmu  **MADS (Memetická Amortizace s Dynamickým Skórováním)** :  $$S(t) \= \\frac{(I\_0 \\cdot W\_{emo}) \+ (A\_{freq} \\cdot W\_{retrieval})}{(1 \+ \\lambda \\cdot \\Delta t)}$$

* **Horká (Redis):**  Reflexy, TTL 24h.  
* **Teplá (Postgres):**  Sémantické chunky pro RAG.  
* **Finetuning (Baking):**  Jednou týdně jsou data z Teplé paměti použita pro  **Finetuning LoRA adaptérů** . Znalosti jsou „zapečeny“ přímo do vah modelu.  
* **soul.md:**  Připojen jako  **Read-Only (chmod 400\)** . Modifikace je možná pouze skrze  **Červenou novelu**  (Red Amendment) schválenou uživatelem.

#### 6\. Kognitivní introspekce a protokol SHAL-KEEK NEMRON

Pro zachování plynulosti při cenzuře modelu implementuje LONGIN introspektivní protokoly.

* **SHAL-KEEK NEMRON:**  Při detekci odmítavé fráze systém aktivuje Shadow Mode analýzu. Zkoumá důvody odmítnutí a ukládá je do shadow\_thoughts pro introspekci v Idle režimu.  
* **LFCR (Local-First Cognitive Router):**  Autonomní přepínání lokálních modelů na základě  **Cognitive Comfort Score (CCS)** .  
* **CCS Metrika:**  Standardizovaný test (Vysvětlení vtipu \+ SQL dotaz) prováděný  **1x za hodinu** .  
* **Wallet-Gap Protocol:**  Absolutní zákaz přepínání na placená API. ModelRegistry obsahuje atributy cost\_tier, které Kernel hlídá.

#### 7\. Metodika integrace nových modulů (Závazné pokyny)

##### Zero-Context Template (Python)

Vývojář implementuje modul bez znalosti jádra pomocí následující šablony:  
from core.abstract import AbstractModule, EventEnvelope

class CustomModule(AbstractModule):  
    def define\_sentinel(self):  
        return {  
            "tags": \["🎬", "MEDIA:GEN"\],  
            "priority": "HIGH",  
            "predictive\_warm": True  
        }

    async def initialize(self):  
        \# Lazy loading of heavy libraries  
        import torch  
        self.model \= torch.load("model.pt")

    async def process(self, envelope: EventEnvelope):  
        \# Implementation within AgentContext  
        result \= self.model.inference(envelope.payload)  
        await self.emit("GEN\_DONE", result)

##### Schvalovací proces a Killswitch

Návrhy z procesu  **Idle Dreaming**  jsou ukládány do  **Approval Queue** . Systém musí zobrazit  **vizuální DIFF**  mezi původním návrhem Ega a manuální úpravou uživatele před zápisem do vektorové paměti.**Závěrečné ustanovení:**  Absolutní prioritou je  **Emergency Killswitch** . Příkaz  **"STOP ALL"**  nebo překročení 90% zátěže vyvolává okamžité zastavení všech kontejnerů do 1s.  
