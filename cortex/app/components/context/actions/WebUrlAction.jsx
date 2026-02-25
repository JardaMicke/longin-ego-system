import { useState } from "react";

export const WebUrlAction = ({ manager, onClose }) => {
  const [url, setUrl] = useState("");
  const [preview, setPreview] = useState("");
  const [status, setStatus] = useState("");

  const submit = async () => {
    let parsed;
    try {
      parsed = new URL(url);
    } catch (error) {
      setStatus("Zadejte platnou URL.");
      return;
    }
    const id = manager.createItem({
      type: "Web",
      title: parsed.hostname,
      preview: "Načítání obsahu"
    });
    const controller = new AbortController();
    manager.registerOperation(id, controller);
    manager.registerRetry(id, submit);
    manager.updateItem(id, { status: "uploading", progress: 0 });
    manager.addLog("info", "Zahájeno načtení webu.", { id });
    try {
      const response = await fetch("/api/context/web", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: parsed.toString() }),
        signal: controller.signal
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.error ?? "Web se nepodařilo načíst.");
      }
      setPreview(data.preview ?? "");
      manager.updateItem(id, { status: "ready", progress: 100, preview: data.preview });
      manager.recordMetric("web", "success");
      manager.addLog("info", "Web přidán.", { id });
      onClose();
    } catch (error) {
      const message = error.message || "Web se nepodařilo přidat.";
      manager.updateItem(id, { status: "failed", error: message });
      manager.recordMetric("web", message.includes("zrušena") ? "cancelled" : "failure");
      manager.addLog("error", message, { id });
      setStatus(message);
    }
  };

  return (
    <div className="context-action">
      <label className="context-label">
        URL webu
        <input className="context-input" value={url} onChange={(event) => setUrl(event.target.value)} />
      </label>
      {preview ? <div className="context-preview">{preview}</div> : null}
      {status ? <div className="context-status">{status}</div> : null}
      <div className="context-action-row">
        <button type="button" className="primary-button" onClick={submit}>
          Přidat do kontextu
        </button>
      </div>
    </div>
  );
};
