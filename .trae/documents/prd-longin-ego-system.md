## 1. Product Overview
LONGIN EGO je lokálně běžící „Sovereign Creator OS“ – autonomní digitální organismus pro bezpečnou exekuci kódu, plánování a dlouhodobou paměť.
- Cíl: Zajistit suverénní AI bez cloudu, s přísnou křemíkovou disciplínou (32GB RAM, RTX 3060 12GB VRAM) a bezpečnou orchestrací MSCA.

## 2. Core Features

### 2.1 User Roles
| Role | Registration Method | Core Permissions |
|------|---------------------|------------------|
| Architekt (uživatel) | Lokální účet / přihlášení | Ovládá moduly, spouští ERTDSD, schvaluje změny (Červená novela), správa systému |

### 2.2 Feature Module
Na minimální počet stránek s vysokou funkční hustotou:
1. **Dashboard (Cortex UI)**: levý panel modulů, centrální chat + vnitřní dialogy, pravá lišta ovladačů modulu; odpojitelný chat při UI bez chatu.
2. **Detail modulu**: stav, telemetrie, akce (start/stop), parametry, logy a výsledky.
3. **Přihlášení**: bezpečný vstup do systému (JWT), volby profilu/identity.

### 2.3 Page Details
| Page Name | Module Name | Feature description |
|-----------|-------------|---------------------|
| Dashboard (Cortex UI) | Levý panel modulů | Zobrazit seznam modulů (Sentinel/Worker); přepínat aktivní UI modulu; indikovat stav (online/offline). |
| Dashboard (Cortex UI) | Chat panel | Zobrazit konverzaci uživatel ↔ EGO a vnitřní dialogy; pole vstupu; akce: hlasové zadání, vložení souboru/složky/obrázku/složky obrázků/mp3/notebookLM/URL repo/URL webu; odeslat, smazat poslední, zastavit práci. |
| Dashboard (Cortex UI) | Pravý ovládací panel | Zobrazit ovladače aktuálního modulu: parametry, start/stop, priority; zobrazit metriky (RAM/VRAM/teplota GPU) a Kill Switch. |
| Dashboard (Cortex UI) | Odpojitelný chat | Při UI modulu bez chatu odpojit chat do samostatného okna a pozicionovat navrch. |
| Detail modulu | Stav & Telemetrie | Zobrazit stav modulu (běží/stojí), poslední heartbeat, využití zdrojů; zobrazit logy a události z Redis Streams. |
| Detail modulu | Akce & Parametry | Upravit parametry (limity RAM/VRAM, timeouty); spustit/zastavit; vyvolat ERTDSD workflow; zobrazit výsledky. |
| Přihlášení | Auth | Přihlásit uživatele (lokálně); spravovat token; volba identity (soul.md profil). |

## 3. Core Process
- Architekt se přihlásí, otevře Dashboard.
- Vybere modul; v chat panelu zadá úkol (tagy: 🛠️ DEV:CODE, 🧠 SYS:MIND, ⚡ RES:GPU).
- Kernel přes Chronos (15s) provede somatickou kontrolu → kognitivní rozvahu → exekuci.
- Sentinely skenují SYS:INBOX; Arbiter přidělí kredity; modul se materializuje JIT a běží v Sibling kontejneru; výsledky se zobrazí v UI.
- Idle Dreaming konsoliduje paměť pod zátěží < 20 %; změny identity vyžadují Červenou novelu.

```mermaid
graph TD
  "Login" --> "Dashboard"
  "Dashboard" --> "Detail modulu"
  "Dashboard" --> "ERTDSD Workflow"
  "ERTDSD Workflow" --> "Exekuce v Sibling kontejneru"
  "Exekuce v Sibling kontejneru" --> "Logy & Výsledky"
  "Dashboard" --> "Idle Dreaming"
  "Idle Dreaming" --> "Paměťová konsolidace"
```

## 4. User Interface Design
### 4.1 Design Style
- Barvy: primární #00FF66 (zelená), sekundární #0A2342 (tmavě modrá), pozadí #000000 (černé).
- Tlačítka: hranatá s jemným glow efektem; ghost-button pro sekundární akce.
- Font: Inter (UI), JetBrains Mono (logy/kód); velikosti 14–16px, nadpisy 20–24px.
- Layout: top nav minimal; hlavní rozvržení 3 panely (levý modul selector, střed chat, pravý controls); card-based sekce pro logy/telemetrii.
- Ikony/emoji: lucide + systémové emoji tagy (🧠, 🛠️, ⚡, 🔥).

### 4.2 Page Design Overview
| Page Name | Module Name | UI Elements |
|-----------|-------------|-------------|
| Dashboard | Levý panel modulů | Sidebar; seznam s indikátory stavu; barvy stavu (zelená/žlutá/červená); hover detaily. |
| Dashboard | Chat panel | Scrolovací feed; role badge; input lišta s akcemi; tlačítka pro odeslání/zastavení/smazání; status tx/rx. |
| Dashboard | Pravý ovládací panel | Form controls (slidery, přepínače); metriky (RAM/VRAM/GPU temp); Kill Switch; telemetry mini-chart. |
| Detail modulu | Stav & Telemetrie | Cards s heartbeat, CPU/GPU; log viewer; filtr událostí; start/stop; parametry. |
| Přihlášení | Auth | Form s email/heslo nebo lokální uživatel; volba identity (select soul.md profil). |

### 4.3 Responsiveness
- Desktop-first, mobilní adaptace: ano (breakpointy ≥ 1024px primárně; mobil ořezává pravý panel pod chat); optimalizace pro touch: základní.

### 4.4 3D Scene Guidance
- Prostředí: studio/technologické; tmavé HDRI; mood: „neon tech“.
- Světla: key (bílé, střední intenzita), fill (modrá nízká), rim (zelená jemná); softShadows.
- Kamera: FOV 50°, orbit kolem „Nexus“ uzlu; počáteční pozice (0,2,6), target (0,0,0); pomalý orbit; ovládání myší.
- Kompozice: foreground „Nexus“, mid „Ganglia“, background „Synapse“; datové linky jako animované partikl linie.
- Interakce/animace: hover zvýrazní uzel; klik zobrazí telemetrii; idle loop pomalý puls.
- Postprocessing: bloom nízký, SSAO střední, tone mapping filmic.
- Assety: GLTF/GLB jednoduché tvary; textury 1k; performance budget: 60 FPS na RTX 3060.