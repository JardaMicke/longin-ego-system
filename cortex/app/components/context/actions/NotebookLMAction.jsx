import { useState } from "react";

export const NotebookLMAction = ({ manager, onClose }) => {
  const [url, setUrl] = useState("");
  const [note, setNote] = useState("");
  const [status, setStatus] = useState("");

  const submit = async () => {
    let parsed;
    try {
      parsed = new URL(url);
    } catch (error) {
      setStatus("Zadejte platnou URL NotebookLM.");
      return;
    }
    const id = manager.createItem({
      type: "NotebookLM",
      title: parsed.hostname,
      preview: note ? note.slice(0, 140) : "Bez poznámky"
    });
    const controller = new AbortController();
    manager.registerOperation(id, controller);
    manager.registerRetry(id, submit);
    manager.updateItem(id, { status: "uploading", progress: 0 });
    manager.addLog("info", "Zahájeno přidání NotebookLM.", { id });
    try {
      const response = await fetch("/api/context/notebooklm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: parsed.toString(), note }),
        signal: controller.signal
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.error ?? "NotebookLM se nepodařilo načíst.");
      }
      manager.updateItem(id, { status: "ready", progress: 100 });
      manager.recordMetric("notebooklm", "success");
      manager.addLog("info", "NotebookLM přidáno.", { id });
      onClose();
    } catch (error) {
      const message = error.message || "NotebookLM se nepodařilo přidat.";
      manager.updateItem(id, { status: "failed", error: message });
      manager.recordMetric("notebooklm", message.includes("zrušena") ? "cancelled" : "failure");
      manager.addLog("error", message, { id });
      setStatus(message);
    }
  };

  return (
    <div className="context-action">
      <label className="context-label">
        URL NotebookLM
        <input className="context-input" value={url} onChange={(event) => setUrl(event.target.value)} />
      </label>
      <label className="context-label">
        Poznámka
        <textarea className="context-textarea" rows={4} value={note} onChange={(event) => setNote(event.target.value)} />
      </label>
      {status ? <div className="context-status">{status}</div> : null}
      <div className="context-action-row">
        <button type="button" className="primary-button" onClick={submit}>
          Přidat do kontextu
        </button>
      </div>
    </div>
  );
};
