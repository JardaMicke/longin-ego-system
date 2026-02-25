"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from 'next/dynamic';
import { ContextActionModal } from "./components/context/ContextActionModal";
import { ContextItemList } from "./components/context/ContextItemList";
import { ContextLogs } from "./components/context/ContextLogs";
import { FileAction } from "./components/context/actions/FileAction";
import { FolderAction } from "./components/context/actions/FolderAction";
import { FolderImageAction } from "./components/context/actions/FolderImageAction";
import { ImageAction } from "./components/context/actions/ImageAction";
import { MP3Action } from "./components/context/actions/MP3Action";
import { NotebookLMAction } from "./components/context/actions/NotebookLMAction";
import { RepoUrlAction } from "./components/context/actions/RepoUrlAction";
import { VoiceAction } from "./components/context/actions/VoiceAction";
import { WebUrlAction } from "./components/context/actions/WebUrlAction";
import { useContextManager } from "./hooks/useContextManager";
import { TutorialOverlay } from "./components/tutorial/TutorialOverlay";

// Dynamický import pro 3D vizualizaci (pouze client-side)
const SystemVisualization = dynamic(
  () => import('./components/SystemVisualization'),
  { ssr: false }
);

const ChatPanel = ({
  detached,
  messages,
  manager,
  actions,
  onOpenAction
}) => {
  return (
    <section className={`chat-panel ${detached ? "detached" : ""}`}>
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
          <input type="text" placeholder="Napiš zprávu nebo příkaz..." className="chat-field" />
          <button type="button" className="primary-button">
            Odeslat
          </button>
        </div>
        <div className="action-row">
          {actions.map((action) => (
            <button
              key={action.id}
              type="button"
              className="ghost-button"
              onClick={() => onOpenAction(action.id)}
            >
              {action.label}
            </button>
          ))}
        </div>
        <div className="action-row">
          <button type="button" className="danger-button" onClick={manager.removeLastWithUndo}>
            Smazat poslední
          </button>
          <button
            type="button"
            className="danger-button"
            onClick={() => {
              manager.stopAllOperations();
              manager.addLog("info", "Práce byla zastavena uživatelem.");
            }}
          >
            Zastavit práci
          </button>
        </div>
        {manager.undoState ? (
          <div className="context-undo">
            <span>Poslední položka odebrána.</span>
            <button type="button" className="ghost-button" onClick={manager.undoRemove}>
              Vrátit
            </button>
          </div>
        ) : null}
        {manager.cancelSummary ? (
          <div className="context-status">
            Zrušeno operací: {manager.cancelSummary.cancelled.length}
          </div>
        ) : null}
        <ContextItemList
          items={manager.items}
          onRemove={manager.removeItem}
          onRetry={manager.retryItem}
        />
        <ContextLogs logs={manager.logs} />
      </div>
    </section>
  );
};

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
        id: "3d",
        name: "3D Monitor",
        hasChat: false,
        controls: ["Rotate", "Zoom", "Reset", "Filter"]
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
  const manager = useContextManager();
  const contextActions = useMemo(
    () => [
      { id: "voice", label: "Hlas", title: "Hlasová zpráva", component: VoiceAction },
      { id: "file", label: "Soubor", title: "Soubor", component: FileAction },
      { id: "folder", label: "Složka", title: "Složka souborů", component: FolderAction },
      { id: "image", label: "Obrázek", title: "Obrázek", component: ImageAction },
      { id: "image-folder", label: "Složka obrázků", title: "Složka obrázků", component: FolderImageAction },
      { id: "mp3", label: "MP3", title: "MP3", component: MP3Action },
      { id: "notebooklm", label: "NotebookLM", title: "NotebookLM", component: NotebookLMAction },
      { id: "repo", label: "URL repozitáře", title: "Repozitář", component: RepoUrlAction },
      { id: "web", label: "URL webu", title: "Web", component: WebUrlAction }
    ],
    []
  );
  const [activeActionId, setActiveActionId] = useState(null);
  const activeAction = contextActions.find((action) => action.id === activeActionId) || null;
  const ActionComponent = activeAction?.component || null;

  // Stav pro 3D vizualizaci
  const [systemMetrics, setSystemMetrics] = useState({
    system: { cpu_percent: 15.2 },
    msca: { module_count: 6, sentinel_count: 4 }
  });

  // Fetch metrics every 5s
  useEffect(() => {
    if (activeModuleId === '3d') {
      const fetchMetrics = async () => {
        try {
          const res = await fetch('http://localhost:8000/system/status');
          const data = await res.json();
          if (data.status === 'operational' && data.metrics) {
            setSystemMetrics(data.metrics);
          }
        } catch (e) {
          console.error("Failed to fetch metrics", e);
        }
      };
      
      fetchMetrics();
      const interval = setInterval(fetchMetrics, 5000);
      return () => clearInterval(interval);
    }
  }, [activeModuleId]);
  
  // Tutorial State
  const [showTutorial, setShowTutorial] = useState(false);
  
  useEffect(() => {
    // Show tutorial on first visit
    const hasSeenTutorial = localStorage.getItem('hasSeenTutorial');
    if (!hasSeenTutorial) {
      setShowTutorial(true);
      localStorage.setItem('hasSeenTutorial', 'true');
    }
  }, []);

  useEffect(() => {
    if (!manager.undoState?.expiresAt) {
      return;
    }
    const delay = Math.max(manager.undoState.expiresAt - Date.now(), 0);
    const timer = setTimeout(() => manager.clearUndo(), delay);
    return () => clearTimeout(timer);
  }, [manager, manager.undoState]);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-left">
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>ONLINE</span>
          </div>
          <div>
            <h1 className="app-title">L.O.N.G.I.N. EGO</h1>
            <p className="app-subtitle">Sovereign Digital Organism v8.0</p>
          </div>
        </div>
        <div className="header-right">
          <button 
            className="icon-button" 
            onClick={() => setShowTutorial(true)}
            title="Spustit průvodce"
            style={{ marginRight: '10px' }}
          >
            ❓
          </button>
        </div>
      </header>

      <div className="app-body">
        <aside className="sidebar left">
          <div className="panel-title">System Modules</div>
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
                <span className="module-meta">{module.hasChat ? "Interactive Mode" : "Background Process"}</span>
              </button>
            ))}
          </div>
          
          <div className="metrics-panel">
            <div className="panel-title">Live Telemetry</div>
            <div className="metric-item">
              <span className="metric-label">CPU Load</span>
              <span className="metric-value">{systemMetrics.system?.cpu_percent ?? 0}%</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Memory</span>
              <span className="metric-value">{(systemMetrics.system?.memory_used_gb ?? 0).toFixed(1)} GB</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">GPU Temp</span>
              <span className="metric-value">{systemMetrics.system?.gpu_temp ?? 0}°C</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Active Threads</span>
              <span className="metric-value">{systemMetrics.application?.active_threads ?? 0}</span>
            </div>
          </div>
        </aside>

        <main className="center-area">
          <section className="module-panel">
            <div className="module-panel-header">
              <div className="panel-title">{activeModule.name}</div>
              <div className="action-group">
                <button className="icon-button" title="Settings">⚙️</button>
                <button className="icon-button" title="Expand">⛶</button>
              </div>
            </div>
            
            <div className="module-content">
              {activeModuleId === '3d' ? (
                <div style={{ width: '100%', height: '100%', minHeight: '500px' }}>
                  <SystemVisualization data={systemMetrics} />
                </div>
              ) : activeModule.hasChat ? (
                <div className="chat-container">
                  <div className="chat-messages">
                    {messages.map((message) => (
                      <div key={message.id} className={`chat-message ${message.role}`}>
                        <div className="chat-role">{message.title}</div>
                        <div className="chat-text">{message.text}</div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="chat-input-area">
                    <div className="action-bar">
                      <div className="action-group">
                        {contextActions.slice(0, 4).map((action) => (
                          <button
                            key={action.id}
                            className="icon-button"
                            title={action.label}
                            onClick={() => setActiveActionId(action.id)}
                          >
                            {action.id === 'voice' ? '🎤' : 
                             action.id === 'file' ? '📎' : 
                             action.id === 'image' ? '🖼️' : '📁'}
                          </button>
                        ))}
                      </div>
                      <button className="send-button">Execute</button>
                    </div>
                    <textarea 
                      className="chat-field" 
                      placeholder="Enter command or natural language request..."
                      rows={3}
                    />
                  </div>
                </div>
              ) : (
                <div className="module-body" style={{ padding: '20px' }}>
                  <div className="module-card">
                    <div className="module-card-title">Status</div>
                    <div className="module-card-value">Operational</div>
                  </div>
                </div>
              )}
            </div>
          </section>
        </main>

        <aside className="sidebar right">
          <div className="panel-title">Control Plane</div>
          <div className="control-grid">
            {activeModule.controls.map((control) => (
              <button key={control} type="button" className="control-button">
                {control}
              </button>
            ))}
          </div>
          
          <div style={{ marginTop: '20px' }}>
            <div className="panel-title">Context Stack</div>
            {Object.keys(manager.metrics).length === 0 ? (
              <div className="context-empty">No active context items.</div>
            ) : (
              Object.entries(manager.metrics).map(([key, value]) => (
                <div key={key} className="context-metric-row">
                  <span>{key}</span>
                  <span>
                    {value.success ?? 0}/{value.failure ?? 0}
                  </span>
                </div>
              ))
            )}
          </div>
          
          <ContextItemList
            items={manager.items}
            onRemove={manager.removeItem}
            onRetry={manager.retryItem}
          />
        </aside>
      </div>
      
      {activeAction && ActionComponent ? (
        <ContextActionModal title={activeAction.title} onClose={() => setActiveActionId(null)}>
          <ActionComponent manager={manager} onClose={() => setActiveActionId(null)} />
        </ContextActionModal>
      ) : null}
      
      {showTutorial && <TutorialOverlay onClose={() => setShowTutorial(false)} />}
    </div>
  );
}
