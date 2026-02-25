import { useEffect, useState } from "react";
import { parseId3v2, uploadWithProgress, validateFile } from "../../../utils/contextUtils";

export const MP3Action = ({ manager, onClose }) => {
  const [file, setFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState("");
  const [tags, setTags] = useState({});
  const [note, setNote] = useState("");
  const [status, setStatus] = useState("");

  const handleFile = async (nextFile) => {
    if (!nextFile) {
      return;
    }
    const validation = validateFile(nextFile, { maxSize: 20 * 1024 * 1024, extensions: [".mp3"] });
    if (!validation.ok) {
      setStatus(validation.error);
      setFile(null);
      setTags({});
      return;
    }
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioUrl(URL.createObjectURL(nextFile));
    setFile(nextFile);
    setStatus("");
    try {
      const buffer = await nextFile.arrayBuffer();
      setTags(parseId3v2(buffer));
    } catch (error) {
      setTags({});
    }
  };

  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const submit = async () => {
    if (!file) {
      setStatus("Vyberte MP3 soubor.");
      return;
    }
    const id = manager.createItem({
      type: "MP3",
      title: file.name,
      size: file.size,
      preview: tags.title ? `Název: ${tags.title}` : "Bez ID3 tagů"
    });
    const controller = new AbortController();
    manager.registerOperation(id, controller);
    manager.registerRetry(id, submit);
    manager.updateItem(id, { status: "uploading", progress: 0 });
    manager.addLog("info", "Zahájeno nahrávání MP3.", { id });
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("note", note);
      await uploadWithProgress({
        url: "/api/context/mp3",
        formData,
        signal: controller.signal,
        onProgress: (progress) => manager.updateItem(id, { progress })
      });
      manager.updateItem(id, { status: "ready", progress: 100 });
      manager.recordMetric("mp3", "success");
      manager.addLog("info", "MP3 nahrána.", { id });
      onClose();
    } catch (error) {
      const message = error.message || "MP3 se nepodařilo nahrát.";
      manager.updateItem(id, { status: "failed", error: message });
      manager.recordMetric("mp3", message.includes("zrušena") ? "cancelled" : "failure");
      manager.addLog("error", message, { id });
      setStatus(message);
    }
  };

  return (
    <div className="context-action">
      <div className="context-action-row">
        <label className="ghost-button">
          Vybrat MP3
          <input
            type="file"
            accept=".mp3"
            className="file-input"
            onChange={(event) => handleFile(event.target.files?.[0])}
          />
        </label>
      </div>
      {file ? (
        <div className="context-preview">
          <div className="context-preview-title">{file.name}</div>
          <div>{tags.title ? `Název: ${tags.title}` : "Bez názvu"}</div>
          <div>{tags.artist ? `Interpret: ${tags.artist}` : "Bez interpreta"}</div>
          <div>{tags.album ? `Album: ${tags.album}` : "Bez alba"}</div>
          <audio controls src={audioUrl} />
        </div>
      ) : null}
      <label className="context-label">
        Poznámka
        <input className="context-input" value={note} onChange={(event) => setNote(event.target.value)} />
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
