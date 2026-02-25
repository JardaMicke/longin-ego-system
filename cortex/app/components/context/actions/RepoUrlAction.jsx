import { useEffect, useState } from "react";
import { parseRepoUrl } from "../../../utils/contextUtils";

export const RepoUrlAction = ({ manager, onClose }) => {
  const [url, setUrl] = useState("");
  const [branch, setBranch] = useState("");
  const [status, setStatus] = useState("");
  const [parsed, setParsed] = useState(null);

  useEffect(() => {
    setParsed(parseRepoUrl(url));
  }, [url]);

  const submit = async () => {
    if (!parsed) {
      setStatus("Zadejte platnou URL repozitáře.");
      return;
    }
    const id = manager.createItem({
      type: "Repozitář",
      title: `${parsed.owner}/${parsed.repo}`,
      preview: branch ? `Branch: ${branch}` : `Provider: ${parsed.provider}`
    });
    const controller = new AbortController();
    manager.registerOperation(id, controller);
    manager.registerRetry(id, submit);
    manager.updateItem(id, { status: "uploading", progress: 0 });
    manager.addLog("info", "Zahájeno načtení repozitáře.", { id });
    try {
      const response = await fetch("/api/context/repo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, branch, ...parsed }),
        signal: controller.signal
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.error ?? "Repozitář se nepodařilo načíst.");
      }
      manager.updateItem(id, { status: "ready", progress: 100 });
      manager.recordMetric("repo", "success");
      manager.addLog("info", "Repozitář přidán.", { id });
      onClose();
    } catch (error) {
      const message = error.message || "Repozitář se nepodařilo přidat.";
      manager.updateItem(id, { status: "failed", error: message });
      manager.recordMetric("repo", message.includes("zrušena") ? "cancelled" : "failure");
      manager.addLog("error", message, { id });
      setStatus(message);
    }
  };

  return (
    <div className="context-action">
      <label className="context-label">
        URL repozitáře
        <input className="context-input" value={url} onChange={(event) => setUrl(event.target.value)} />
      </label>
      <label className="context-label">
        Branch
        <input className="context-input" value={branch} onChange={(event) => setBranch(event.target.value)} />
      </label>
      {parsed ? (
        <div className="context-preview">
          <div>Provider: {parsed.provider}</div>
          <div>Owner: {parsed.owner}</div>
          <div>Repo: {parsed.repo}</div>
        </div>
      ) : null}
      {status ? <div className="context-status">{status}</div> : null}
      <div className="context-action-row">
        <button type="button" className="primary-button" onClick={submit}>
          Přidat do kontextu
        </button>
      </div>
    </div>
  );
};
