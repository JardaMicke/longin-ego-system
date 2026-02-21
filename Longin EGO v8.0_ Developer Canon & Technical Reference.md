# **Longin EGO v8.0: Vývojářská Dokumentace (The Canon)**

**Verze:** 8.0.1 (Hive Mind / ERTDSD Revision)

**Určeno pro:** Senior Architect & Autonomous Builders

**Tech Stack:** Python 3.12+, Next.js 14, PostgreSQL (pgvector), Redis Streams, Docker, MCP

## ---

**1\. MSCA: Základní Abstraktní Vzory**

Architektura jádra stojí na vzoru **MSCA** (Module-Sentinel-Connector-Adapter). Tento vzor řeší problém "bloatu" – jak mít schopnost udělat cokoliv, ale nespotřebovávat paměť na všechno najednou.

### **1.1 The Sentinel (Hlídka)**

Sentinel je lehká třída, která nikdy nespí. Musí být implementována tak, aby její import nezavedl těžké závislosti (žádné import torch na úrovni modulu\!).

Python

from abc import ABC, abstractmethod  
from typing import Dict, Any, List

class ISentinel(ABC):  
    """  
    Ultra-lehký proces pro detekci záměru (Intent Detection).  
    Musí běžet v O(1) nebo O(N) nad hlavičkami zpráv.  
    """  
      
    @property  
    @abstractmethod  
    def trigger\_tags(self) \-\> List\[str\]:  
        """Seznam tagů, na které tento Sentinel reaguje (např.)"""  
        pass

    @abstractmethod  
    async def scan(self, headers: Dict\[str, Any\]) \-\> bool:  
        """  
        Rychlá analýza metadat.  
        Vrací True, pokud má být aktivován těžký Modul.  
        """  
        pass

    @abstractmethod  
    def estimate\_resource\_cost(self) \-\> dict:  
        """Vrací odhad pro Arbitra: {'ram\_mb': 4000, 'gpu\_vram\_mb': 2000}"""  
        pass

### **1.2 The Module (Těžký Dělník)**

Modul se materializuje (instanciuje) až v momentě, kdy Sentinel řekne True.

Python

class IModule(ABC):  
    """  
    Výkonná jednotka. Její \_\_init\_\_ může trvat sekundy (loading modelů).  
    """  
      
    @abstractmethod  
    async def initialize(self):  
        """Lazy loading těžkých knihoven (torch, transformers)"""  
        pass

    @abstractmethod  
    async def execute(self, payload: Any, context: 'EgoContext') \-\> Any:  
        """Vlastní logika"""  
        pass

    @abstractmethod  
    async def shutdown(self):  
        """Cleanup. Explicitní uvolnění VRAM/RAM."""  
        pass

## ---

**2\. API Definice: Protokoly a Rozhraní**

Komunikace v Longin v8.0 je hybridní: **MCP** pro nástroje (Tools) a **Redis Streams** pro asynchronní události.

### **2.1 Ganglion Protocol (gRPC/HTTP)**

Definice rozhraní mezi Nexusem (Server) a Gangliemi (Klienti na síti).

**OpenAPI Spec (zkrácená):**

YAML

openapi: 3.0.0  
info:  
  title: Longin Ganglion API  
  version: 1.0.0  
paths:  
  /v1/capabilities:  
    get:  
      summary: "Discovery: Co tento počítač umí?"  
      responses:  
        200:  
          description: "Vrací hardware profil"  
          content:  
            application/json:  
              schema:  
                type: object  
                properties:  
                  hostname: {type: string}  
                  gpu\_model: {type: string, example: "RTX 3060"}  
                  vram\_free: {type: integer, description: "MB"}  
                  local\_llm\_ready: {type: boolean}  
  /v1/spawn:  
    post:  
      summary: "Remote Process Execution"  
      requestBody:  
        content:  
          application/json:  
            schema:  
              type: object  
              properties:  
                command: {type: string}  
                sandbox\_mode: {type: boolean, default: true}  
                env\_vars: {type: object}

### **2.2 Model Context Protocol (MCP) Tool Definition**

Longin vystavuje své schopnosti LLM modelům přes standardizované MCP rozhraní.

Python

\# Definice nástroje pro správu síťových zdrojů (Network Resources)  
from mcp.server.fastmcp import FastMCP, Context

mcp \= FastMCP("NexusControl")

@mcp.tool()  
async def scan\_network\_resources(ctx: Context) \-\> str:  
    """  
    Prohledá lokální síť (LAN) a najde dostupné Ganglia uzly.  
    Vrací seznam dostupných GPU a sdílených složek.  
    """  
    \# Implementace mDNS discovery  
    return json.dumps(active\_ganglia\_registry)

@mcp.tool()  
async def delegate\_computation(node\_id: str, task\_script: str) \-\> str:  
    """  
    Odešle Python skript na vzdálený uzel (Ganglion) k exekuci.  
    """  
    \# RPC volání na Ganglion  
    return job\_id

## ---

**3\. Datové Toky a Diagramy (Mermaid)**

### **3.1 ERTDSD Development Loop Flow**

Tok dat při autonomním vývoji. Žádný krok není přeskočen.

Fragment kódu

sequenceDiagram  
    participant U as User  
    participant E as EGO (Architect)  
    participant S as Sandbox (Sibling)  
    participant M as Memory (PgVector)  
      
    U-\>\>E: "Potřebuji analyzátor faktur (PDF)"  
    E-\>\>E: Introspection (Soul.md check)  
    E-\>\>U: The Meeting (Křížový výslech požadavků)  
    U-\>\>E: Upřesnění (DoD)  
      
    rect rgb(30, 0, 0\)  
    note right of E: Red Phase  
    E-\>\>E: Generate Tests (test\_invoice.py)  
    E-\>\>S: Run Tests (FAIL očekáván)  
    end  
      
    rect rgb(0, 30, 0\)  
    note right of E: Green Phase Loop  
    loop Until Tests Pass  
        E-\>\>M: Retrieve Coding Patterns  
        E-\>\>E: Write Implementation  
        E-\>\>S: Run Tests in Sandbox  
        S--\>\>E: Stderr / Logs  
    end  
    end  
      
    E-\>\>U: "Hotovo. Zde je demo. Nasadit?"

### **3.2 Ganglion Discovery Flow**

Jak se "Hive Mind" dozví o novém zdroji (např. zapnutý notebook).

Fragment kódu

sequenceDiagram  
    participant N as Nexus (Server)  
    participant G as Ganglion (Laptop)  
      
    G-\>\>N: mDNS Broadcast ("I am Ganglion-02, RTX 3050")  
    N-\>\>G: Handshake (Verify Cert)  
    G-\>\>N: Capabilities Payload (RAM, Apps, Local LLM)  
    N-\>\>N: Update Resource Registry  
    N-\>\>U: Notification ("New resource added: Laptop GPU")

## ---

**4\. Databázové Schéma (PostgreSQL)**

Pro persistenci využíváme relační strukturu obohacenou o vektorová data.

**Table: memories (Hybrid Search)**

SQL

CREATE TABLE memories (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    content TEXT NOT NULL,  
    embedding VECTOR(1536),  \-- OpenAI / Nomic embedding  
    metadata JSONB,          \-- { "source": "chat", "timestamp":... }  
    user\_id VARCHAR(255),  
    created\_at TIMESTAMPTZ DEFAULT NOW()  
);  
CREATE INDEX ON memories USING hnsw (embedding vector\_cosine\_ops);  
CREATE INDEX ON memories USING GIN (to\_tsvector('english', content)); \-- Fulltext

**Table: ui\_layouts (Puck Config Persistence)**

Ukládá JSON konfiguraci dashboardu. Umožňuje verzování UI.

SQL

CREATE TABLE ui\_layouts (  
    id UUID PRIMARY KEY,  
    project\_id VARCHAR(50),  
    layout\_data JSONB NOT NULL, \-- Puck Data Object  
    version INT,  
    is\_active BOOLEAN  
);

## ---

**5\. Implementační Vzory (Code Snippets)**

### **5.1 Sibling Container Runner (Secure Sandbox)**

Toto je kritická bezpečnostní komponenta. Kód *nesmí* běžet v hlavním procesu.

Python

import docker  
from docker.errors import ContainerError

class SiblingSandbox:  
    def \_\_init\_\_(self):  
        self.client \= docker.from\_env()

    def run\_isolated(self, code: str, env\_vars: dict \= None):  
        try:  
            \# Tvrdé limity pro ochranu hostitele  
            container \= self.client.containers.run(  
                image="python:3.12-slim",  
                command=\["python", "-c", code\],  
                mem\_limit="512m",           \# Max 512MB RAM  
                cpu\_quota=50000,            \# 50% jednoho CPU jádra  
                network\_mode="none",        \# Žádný internet (pokud není potřeba)  
                security\_opt=\["no-new-privileges"\],  
                remove=True,                \# Ephemeralita  
                stdout=True,  
                stderr=True  
            )  
            return {"status": "success", "output": container.decode('utf-8')}  
        except ContainerError as e:  
            return {"status": "error", "output": e.stderr.decode('utf-8')}

### **5.2 Puck Editor Persistence (Next.js App Router)**

Jak uložit změny z vizuálního editoru do naší DB.

TypeScript

// app/api/puck/route.ts  
import { NextResponse } from 'next/server';  
import { db } from '@/lib/db'; // Drizzle/Prisma client

export async function POST(request: Request) {  
  const payload \= await request.json();  
  const { data, path } \= payload;

  // Uložení Puck JSONu do JSONB sloupce  
  await db.ui\_layouts.upsert({  
    where: { path: path },  
    update: { layout\_data: data },  
    create: { path: path, layout\_data: data }  
  });

  return NextResponse.json({ status: 'saved' });  
}

## ---

**6\. Seznam Zdrojů a Repozitářů (Tech Stack)**

Tyto knihovny a repozitáře tvoří DNA systému Longin v8.0.

### **Core & Orchestration**

* **LangGraph** (langchain-ai/langgraph): Pro stavový automat ERTDSD smyčky.  
* **FastMCP** (jlowin/fastmcp): Pro definici nástrojů (Tools API).  
* **Redis Streams** (redis-py): Pro asynchronní event bus.

### **Memory & Knowledge**

* **Mem0** (mem0ai/mem0): Abstraktní vrstva nad pamětí.  
* **Pgvector**: PostgreSQL extenze pro vektory.

### **Network & Distributed Compute**

* **Zeroconf** (python-zeroconf): Pro mDNS discovery (náhrada za komplexní service discovery).  
* **Exo** (exo-explore/exo): Inspirace pro distribuovanou inferenci LLM.

### **Frontend & UI**

* **Puck** (measured/puck): Vizuální editor pro React.  
* **Xterm.js**: Pro terminálová okna v prohlížeči.

## ---

**7\. Bezpečnostní Manifest**

1. **Code Execution:** Nikdy nespouštět generovaný kód přes exec(). Vždy použít Sibling Container.  
2. **Network Policy:** Defaultně DENY ALL. Kontejnery mají zakázaný přístup k LAN, pokud není explicitně povolen (např. pro stažení knihovny).  
3. **Human Override:** Uživatel má vždy "Kill Switch" v UI, který okamžitě zastaví Docker kontejnery a vyprázdní Redis frontu.

Tato dokumentace je připravena k nahrání do paměti LONGIN EGO jako SYSTEM\_CANON.md.