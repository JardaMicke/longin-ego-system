"use client";

import { useMemo, useState } from "react";

export default function Home() {
  const modules = useMemo(
    () => [
      {
        id: "core",
        name: "Core Chat",
        hasChat: true,
        controls: ["Session", "Memory", "Mode", "Safety"]
      },
      {
        id: "planner",
        name: "Planner",
        hasChat: true,
        controls: ["Tasks", "Priority", "Timeline", "Autonomy"]
      },
      {
        id: "ops",
        name: "Ops Console",
        hasChat: false,
        controls: ["Deploy", "Health", "Logs", "Rollback"]
      },
      {
        id: "memory",
        name: "Memory Vault",
        hasChat: false,
        controls: ["Recall", "Index", "Snapshot", "Purge"]
      }
    ],
    []
  );
  const [activeModuleId, setActiveModuleId] = useState(modules[0].id);
  const activeModule = modules.find((module) => module.id === activeModuleId) ?? modules[0];
  const chatDetached = !activeModule.hasChat;
  const messages = useMemo(
    () => [
      {
        id: "m1",
        role: "user",
        title: "User",
        text: "Potřebuju stav systémových modulů a návrh dalšího kroku."
      },
      {
        id: "m2",
        role: "ego",
        title: "EGO",
        text: "Skenuji registry, dávám dohromady plán a validuji dostupnost."
      },
      {
        id: "m3",
        role: "internal",
        title: "Internal",
        text: "ERTDSD: stabilizovat runtime, vyčistit fronty, připravit deploy."
      }
    ],
    []
  );
  const actionButtons = useMemo(
    () => [
      "Hlas",
      "Soubor",
      "Složka",
      "Obrázek",
      "Složka obrázků",
      "MP3",
      "NotebookLM",
      "URL repozitáře",
      "URL webu"
    ],
    []
  );

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="title-block">
          <h1 className="app-title">L.O.N.G.I.N. EGO System</h1>
          <p className="app-subtitle">
            Logical Orchestrated Networked Generative Intelligent Nexus
          </p>
        </div>
      </header>

      <div className="app-body">
        <aside className="sidebar left">
          <div className="panel-title">Moduly</div>
          <div className="module-list">
            {modules.map((module) => (
              <button
                key={module.id}
                type="button"
                className={`module-button ${
                  module.id === activeModuleId ? "active" : ""
                }`}
                onClick={() => setActiveModuleId(module.id)}
              >
                <span className="module-name">{module.name}</span>
                <span className="module-meta">{module.hasChat ? "Chat" : "No Chat"}</span>
              </button>
            ))}
          </div>
        </aside>

        <main className="center-area">
          {chatDetached ? (
            <section className="chat-panel detached">
              <div className="panel-title">Chat</div>
              <div className="chat-messages">
                {messages.map((message) => (
                  <div key={message.id} className={`chat-message ${message.role}`}>
                    <div className="chat-role">{message.title}</div>
                    <div className="chat-text">{message.text}</div>
                  </div>
                ))}
              </div>
              <div className="chat-input">
                <div className="input-row">
                  <input
                    type="text"
                    placeholder="Napiš zprávu nebo příkaz..."
                    className="chat-field"
                  />
                  <button type="button" className="primary-button">
                    Odeslat
                  </button>
                </div>
                <div className="action-row">
                  {actionButtons.map((label) => (
                    <button key={label} type="button" className="ghost-button">
                      {label}
                    </button>
                  ))}
                </div>
                <div className="action-row">
                  <button type="button" className="danger-button">
                    Smazat poslední
                  </button>
                  <button type="button" className="danger-button">
                    Zastavit práci
                  </button>
                </div>
              </div>
            </section>
          ) : null}

          <section className="module-panel">
            <div className="panel-title">{activeModule.name}</div>
            <div className="module-body">
              <div className="module-card">
                <div className="module-card-title">Aktivní režim</div>
                <div className="module-card-value">
                  {activeModule.hasChat ? "Chat s EGEM" : "Samostatný modul"}
                </div>
              </div>
              <div className="module-card">
                <div className="module-card-title">Stav</div>
                <div className="module-card-value">Online</div>
              </div>
              <div className="module-card">
                <div className="module-card-title">Fronta úkolů</div>
                <div className="module-card-value">3 aktivní</div>
              </div>
            </div>
          </section>

          {!chatDetached ? (
            <section className="chat-panel">
              <div className="panel-title">Chat</div>
              <div className="chat-messages">
                {messages.map((message) => (
                  <div key={message.id} className={`chat-message ${message.role}`}>
                    <div className="chat-role">{message.title}</div>
                    <div className="chat-text">{message.text}</div>
                  </div>
                ))}
              </div>
              <div className="chat-input">
                <div className="input-row">
                  <input
                    type="text"
                    placeholder="Napiš zprávu nebo příkaz..."
                    className="chat-field"
                  />
                  <button type="button" className="primary-button">
                    Odeslat
                  </button>
                </div>
                <div className="action-row">
                  {actionButtons.map((label) => (
                    <button key={label} type="button" className="ghost-button">
                      {label}
                    </button>
                  ))}
                </div>
                <div className="action-row">
                  <button type="button" className="danger-button">
                    Smazat poslední
                  </button>
                  <button type="button" className="danger-button">
                    Zastavit práci
                  </button>
                </div>
              </div>
            </section>
          ) : null}
        </main>

        <aside className="sidebar right">
          <div className="panel-title">Ovládání modulu</div>
          <div className="control-list">
            {activeModule.controls.map((control) => (
              <button key={control} type="button" className="control-button">
                {control}
              </button>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
