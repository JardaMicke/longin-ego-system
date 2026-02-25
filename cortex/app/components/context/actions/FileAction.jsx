import { useState } from "react";
import {
  isTextFile,
  readFileAsText,
  uploadWithProgress,
  validateFile
} from "../../../utils/contextUtils";

export const FileAction = ({ manager, onClose }) => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [status, setStatus] = useState("");

  const handleFile = async (nextFile) => {
    const validation = validateFile(nextFile, { maxSize: 10 * 1024 * 1024 });
    if (!validation.ok) {
      setStatus(validation.error);
      setFile(null);
      setPreview("");
      return;
    }
    setFile(nextFile);
    setStatus("");
    if (isTextFile(nextFile)) {
      try {
        const content = await readFileAsText(nextFile);
        setPreview(content.slice(0, 500));
      } catch (error) {
        setPreview("");
      }
    } else {
      setPreview("");
    }
  };

  const onDrop = async (event) => {
    event.preventDefault();
    const dropped = event.dataTransfer.files?.[0];
    if (dropped) {
      await handleFile(dropped);
    }
  };

  const submit = async () => {
    if (!file) {
      setStatus("Vyberte soubor.");
      return;
    }
    const id = manager.createItem({
      type: "Soubor",
      title: file.name,
      size: file.size,
      preview
    });
    const controller = new AbortController();
    manager.registerOperation(id, controller);
    manager.registerRetry(id, submit);
    manager.updateItem(id, { status: "uploading", progress: 0 });
    manager.addLog("info", "Zahájeno nahrávání souboru.", { id });
    try {
      const formData = new FormData();
      formData.append("file", file);
      await uploadWithProgress({
        url: "/api/context/file",
        formData,
        signal: controller.signal,
        onProgress: (progress) => manager.updateItem(id, { progress })
      });
      manager.updateItem(id, { status: "ready", progress: 100 });
      manager.recordMetric("file", "success");
      manager.addLog("info", "Soubor nahrán.", { id });
      onClose();
    } catch (error) {
      const message = error.message || "Soubor se nepodařilo nahrát.";
      manager.updateItem(id, { status: "failed", error: message });
      manager.recordMetric("file", message.includes("zrušena") ? "cancelled" : "failure");
      manager.addLog("error", message, { id });
      setStatus(message);
    }
  };

  return (
    <div className="context-action">
      <div
        className="drop-zone"
        onDragOver={(event) => event.preventDefault()}
        onDrop={onDrop}
        role="button"
        tabIndex={0}
        aria-label="Přetáhněte soubor"
      >
        Přetáhněte soubor nebo klikněte pro výběr.
        <input
          type="file"
          className="file-input"
          onChange={(event) => handleFile(event.target.files?.[0])}
        />
      </div>
      {file ? (
        <div className="context-preview">
          <div className="context-preview-title">{file.name}</div>
          {preview ? <pre>{preview}</pre> : <span>Bez náhledu.</span>}
          <button type="button" className="ghost-button" onClick={() => setFile(null)}>
            Odebrat
          </button>
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
