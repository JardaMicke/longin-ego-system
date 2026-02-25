import { useMemo, useState } from "react";
import { buildTree, uploadWithProgress, validateFile } from "../../../utils/contextUtils";

const TreeNode = ({ node, level }) => (
  <div className="tree-node" style={{ paddingLeft: `${level * 12}px` }}>
    <span>{node.name}</span>
    {node.children?.length
      ? node.children.map((child) => <TreeNode key={child.name} node={child} level={level + 1} />)
      : null}
  </div>
);

export const FolderAction = ({ manager, onClose }) => {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState("");
  const [filter, setFilter] = useState(".txt,.md,.json,.csv");
  const [summary, setSummary] = useState(null);

  const allowedExtensions = useMemo(
    () => filter.split(",").map((item) => item.trim()).filter(Boolean),
    [filter]
  );

  const handleFiles = (list) => {
    const filtered = Array.from(list || []).filter((file) =>
      allowedExtensions.length ? allowedExtensions.some((ext) => file.name.endsWith(ext)) : true
    );
    setFiles(filtered);
    setSummary(null);
    if (!filtered.length) {
      setStatus("Nenalezeny soubory dle filtru.");
    } else {
      setStatus("");
    }
  };

  const tree = useMemo(() => buildTree(files.map((file) => file.webkitRelativePath || file.name)), [
    files
  ]);

  const submit = async () => {
    if (!files.length) {
      setStatus("Vyberte složku.");
      return;
    }
    const id = manager.createItem({
      type: "Složka",
      title: "Složka souborů",
      size: files.reduce((total, file) => total + file.size, 0),
      preview: `Souborů: ${files.length}`
    });
    const controller = new AbortController();
    manager.registerOperation(id, controller);
    manager.registerRetry(id, submit);
    manager.updateItem(id, { status: "uploading", progress: 0 });
    manager.addLog("info", "Zahájeno nahrávání složky.", { id });
    try {
      const formData = new FormData();
      files.forEach((file) => {
        const validation = validateFile(file, { maxSize: 10 * 1024 * 1024 });
        if (validation.ok) {
          formData.append("files", file, file.webkitRelativePath || file.name);
        }
      });
      const response = await uploadWithProgress({
        url: "/api/context/folder",
        formData,
        signal: controller.signal,
        onProgress: (progress) => manager.updateItem(id, { progress })
      });
      manager.updateItem(id, { status: "ready", progress: 100, preview: `Nahráno ${response.ok}` });
      manager.recordMetric("folder", "success");
      manager.addLog("info", "Složka nahrána.", { id });
      setSummary(response);
      onClose();
    } catch (error) {
      const message = error.message || "Složka se nepodařila nahrát.";
      manager.updateItem(id, { status: "failed", error: message });
      manager.recordMetric("folder", message.includes("zrušena") ? "cancelled" : "failure");
      manager.addLog("error", message, { id });
      setStatus(message);
    }
  };

  return (
    <div className="context-action">
      <label className="context-label">
        Filtr přípon
        <input
          className="context-input"
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
        />
      </label>
      <div className="context-action-row">
        <label className="ghost-button">
          Vybrat složku
          <input
            type="file"
            webkitdirectory="true"
            directory="true"
            className="file-input"
            onChange={(event) => handleFiles(event.target.files)}
          />
        </label>
      </div>
      <div className="context-tree">{tree.children.map((child) => <TreeNode key={child.name} node={child} level={0} />)}</div>
      {summary ? (
        <div className="context-preview">
          <div>Úspěšně: {summary.ok}</div>
          <div>Neúspěšně: {summary.failed}</div>
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
