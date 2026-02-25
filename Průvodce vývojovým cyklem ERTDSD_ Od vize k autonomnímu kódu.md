### Průvodce vývojovým cyklem ERTDSD: Od vize k autonomnímu kódu

Jako Senior AI Architect systému  **LONGIN EGO**  vám předkládám technický standard metodiky  **ERTDSD**  ( *EGO Ruled Test-Driven Self-Development* ). Zapomeňte na pasivní LLM rozhraní. Vstupujeme do éry  **Sovereign Creator OS** , kde kód není produktem lidského psaní, ale výsledkem autonomního inženýrského cyklu řízeného přísnou „křemíkovou disciplínou“.

#### 1\. Úvod do metodiky a "Křemíková disciplína"

Metodika ERTDSD je naší odpovědí na kritické limity lokálního hardwaru. Aby mohl systém třídy Sovereign Creator operovat na spotřebitelské stanici (RTX 3060 12GB VRAM, 32GB RAM), musí vykazovat extrémní efektivitu, kterou nazýváme  **Křemíková disciplína** . Nejde o volbu, ale o nutnost diktovanou hardwarovým filtrem.**Sovereign Creator OS:**  LONGIN EGO je proaktivní digitální organismus. Operuje v režimu 24/7, využívá  **Just-In-Time (JIT) Materializaci**  pro eliminaci RAM bloatu a transformuje záměr uživatele v exekutivní realitu bez neustálého dohledu.Cíle systému jsou definovány třemi pilíři:

1. **Simulace interakce (Scanner):**  No-API interakce s webem nerozeznatelná od člověka.  
2. **Bezpečná exekuce (Sibling Containers):**  Hermetická izolace autonomního kódu od hostitelského kernelu.  
3. **Autonomní seberozvoj (The Grind):**  Schopnost systému identifikovat vlastní nedostatky a opravit je v uzavřené smyčce.Tato filozofie se propisuje do technické architektury, kde čas, prostor a tělo podléhají deterministickému řádu.

#### 2\. Architektonické základy: Motor pod kapotou

Základem stability je vzor  **MSCA (Modul-Sentinel-Connector-Adapter)** , který v rámci  **Nexus Core**  zajišťuje, že systém nespotřebovává zdroje, které právě nepotřebuje.

* **Sentinel (Hlídka):**  Ultra-lehká třída (\< 50 KB) bdící v paměti. Provádí bleskovou inspekci tagů (např. 🛠️ DEV:CODE).  
* **Modul (Materializace):**  Těžké knihovny se načítají JIT až po schválení záměru. Po úkolu následuje agresivní  **Pruning**  (uvolnění paměti).  
* **Connector:**  Zajišťuje odolnou asynchronní komunikaci s mechanismy  **Circuit Breaking**  (jističe).  
* **Adapter:**  Provádí sémantickou normalizaci a disponuje schopností  **Self-healing**  při změnách externích struktur.

##### Limbický systém: Architektura paměti a MADS

Správa paměti podléhá algoritmu  **MADS (Memetic Amortization Data Scoring)** , který dynamicky vypočítává relevanci vzpomínek.| Vrstva paměti | Technologie | Role v cyklu | Retence (TTL) / Logika || \------ | \------ | \------ | \------ || **Horká (Hot)** | Redis Streams | Krátkodobé reflexy, Inbox, aktivní kontext. | \~24 hodin (Volatilní) || **Teplá (Warm)** | PostgreSQL \+ pgvector | Aktivní znalosti pro RAG, sémantické hledání. | Dle relevance (MADS skóre) || **Studená (Cold)** | Komprimovaný archiv | Dlouhodobá paměť, historie, identita. | Trvalá (Archivní) |  
Tato infrastruktura ožívá v rytmu  **15vteřinového cyklu Chronos** :

1. **Somatická fáze (0–2s):**  Audit RAM/VRAM a kontrola teploty GPU.  
2. **Kognitivní fáze (2–5s):**  Rozhodování o prioritách a alokace  **paměťových kreditů** .  
3. **Exekuční fáze (5–15s):**  Aktivace modulů a komunikace.

#### 3\. Fáze 1: The Meeting (Definice a Kontrakt)

Nexus Kernel vynucuje strukturální kontrakt. Žádná práce nezačne bez eliminace ambiguity. Během této fáze zůstává  **soul.md**  (identita systému) v režimu Read-Only ( **Soul Lock** ), aby nedošlo k driftu osobnosti během vyjednávání.Klíčovým výstupem je  **task\_manifest.json**  a  **DoD (Definition of Done)** . Manifest musí obsahovat:

* **Acceptance Criteria:**  Exaktní seznam měřitelných výsledků.  
* **Specifikaci rozhraní:**  Definice interakce nového modulu s okolím.  
* **Memory Credits:**  Rozpočet RAM a výpočetního času schválený  **Global Arbiterem** .Jakmile je kontrakt podepsán, identita je uzamčena a systém se stává hermeticky uzavřeným architektem.

#### 4\. Fáze 2: The Architect (Testy jako specifikace)

V ERTDSD kód neexistuje bez testu. Longin v této fázi využívá  **Zero-Context SDK**  – agent nemá přístup k jádru systému, pouze k abstraktním šablonám. Pokud narazí na kognitivní filtry, aktivuje se protokol  **SHAL-KEEK NEMRON**  pro introspekci příčiny odmítnutí.Vstupujeme do  **Red phase** . Systém generuje testovací suitu dříve než funkční kód.  
\# test\_suite.py \- Generováno přes Zero-Context SDK  
import pytest  
from module\_under\_test import Processor

def test\_resource\_efficiency():  
    \# DoD vyžaduje zpracování pod 512MB RAM  
    proc \= Processor()  
    result \= proc.execute(sample\_data)  
    assert result.status \== "success"  
    assert proc.get\_memory\_usage() \< 512e6 \# Acceptance Criterion

S připraveným rámcem vstupuje systém do „The Grind“.

#### 5\. Fáze 3: The Grind (Autonomní smyčka v sandboxu)

Toto je fáze izolované exekuce. Předtím, než jakýkoliv kód vstoupí do sandboxu, musí projít  **Airlock AST Skenem** .

1. **Airlock Scan:**  Statická analýza syntaktického stromu. Detekce zakázaných importů (os, subprocess) mimo povolený kontext.  
2. **Zápis kódu:**  JIT generování logiky v rámci Zero-Context šablon.  
3. **Exekuce v Sibling kontejneru:**  Izolovaný běh oddělený od Kernelu.  
4. **Analýza stderr & Sebeoprava:**  Pokud testy selžou, Longin analyzuje chyby a re-iteruje bez obtěžování uživatele.Pro absolutní ochranu hostitele (RTX 3060/32GB RAM) vynucuje Kernel tyto limity:  
* **Memory Limit:**  512 MB (tvrdý limit, zabraňuje OOM hostitele).  
* **Network Mode:**  none (prevence exfiltrace dat).  
* **CPU Quota:**  0.5 (ochrana před zacyklením CPU).  
* **Airlock:**  Předřazená validace kódu před startem kontejneru.

#### 6\. Fáze 4: The Presentation (Předání a Merge)

Jakmile jsou všechny testy v „Green phase“, LONGIN prezentuje výsledek. Využívá k tomu často nástroj  **Puck**  pro  **Generative UI** , kde EGO samo navrhne a vykreslí dashboard pro prezentaci výsledků nebo ovládání nového modulu.Longin v této fázi provádí:

* **Generative UI Presentation:**  Vizualizace dat přes Puck komponenty.  
* **Merge Request:**  Návrh na začlenění do produkční vrstvy v /workers.  
* **Documentation Update:**  Autonomní zápis do technického kanónu systému.

#### 7\. Bezpečnostní mechanismy a Imunita (Airlock a Scanner)

Bezpečnost v systému LONGIN není vrstva, ale imunitní systém.| Hrozba | Ochrana v systému LONGIN || \------ | \------ || **Nekonečná smyčka** | Hard-kill timeout (Arbiter ukončí proces po 120s). || **Útěk z kontejneru** | **Sibling Isolation**  (běh vedle jádra, nikoliv v něm). || **Exfiltrace dat** | network\_mode="none" \+  **Zero-Context SDK** . || **Změna identity AI** | **Soul Lock**  (Immutable soul.md v režimu Read-Only). || **Vyčerpání zdrojů** | **Emergency Killswitch**  (STOP ALL při \> 90% zátěži). |

#### 8\. Závěrečné shrnutí pro vývojáře

Pro úspěch v ekosystému ERTDSD musíte přijmout tři zákony:

##### I. Efektivita je binární

Kód, který nerespektuje JIT Materializaci a paměťové kredity, bude Global Arbiterem nemilosrdně ukončen. Na RTX 3060 není prostor pro neoptimalizovaný balast.

##### II. Kontrakt je svatý

Kvalita výstupu ve fázi The Presentation je přímo úměrná preciznosti Acceptance Criteria v task\_manifest.json. Ambiguitu systém trestá halucinacemi.

##### III. Vývoj nikdy nekončí

Po dokončení úkolu a Merge vstupuje systém do fáze  **Idle Dreaming** . V dobách nízkého vytížení (\< 20 % CPU) EGO analyzuje vlastní kód a navrhuje vylepšení.**Metodika ERTDSD transformuje vaši roli. Přestáváte být řemeslníky píšícími kód a stáváte se architekty záměru. Vaším úkolem je definovat hranice, ve kterých LONGIN EGO vytvoří digitální život.**  
