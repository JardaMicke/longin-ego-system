import { useEffect, useMemo, useState } from "react";
import Image from "next/image";
import {
  compressImage,
  createZipBlob,
  dedupeByName,
  uploadWithProgress,
  validateFile
} from "../../../utils/contextUtils";

const extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"];
const sizeOptions = [
  { id: "sm", label: "S", width: 120, height: 90 },
  { id: "md", label: "M", width: 160, height: 120 },
  { id: "lg", label: "L", width: 200, height: 150 },
  { id: "xl", label: "XL", width: 240, height: 180 }
];

export const FolderImageAction = ({ manager, onClose }) => {
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("");
  const [backupUrl, setBackupUrl] = useState("");
  const [summary, setSummary] = useState(null);
  const [sizeId, setSizeId] = useState("md");
  const activeSize = sizeOptions.find((option) => option.id === sizeId) ?? sizeOptions[1];

  useEffect(() => {
    return () => {
      items.forEach((item) => {
        if (item.previewUrl) {
          URL.revokeObjectURL(item.previewUrl);
        }
      });
      if (backupUrl) {
        URL.revokeObjectURL(backupUrl);
      }
    };
  }, [items, backupUrl]);

  const selectedItems = useMemo(() => items.filter((item) => item.selected), [items]);

  const handleFiles = (list) => {
    const files = Array.from(list || []).filter((file) =>
      extensions.includes(file.name.toLowerCase().slice(file.name.lastIndexOf(".")))
    );
    const unique = dedupeByName(files).map((file) => ({
      id: crypto.randomUUID(),
      file,
      selected: true,
      previewUrl: URL.createObjectURL(file)
    }));
    setItems(unique);
    setSummary(null);
    setBackupUrl("");
    if (!unique.length) {
      setStatus("Nenalezeny obrázky ve složce.");
    } else {
      setStatus("");
    }
  };

  const toggleSelect = (id) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, selected: !item.selected } : item))
    );
  };

  const selectAll = () => setItems((prev) => prev.map((item) => ({ ...item, selected: true })));

  const deselectAll = () =>
    setItems((prev) => prev.map((item) => ({ ...item, selected: false })));

  const submit = async () => {
    if (!selectedItems.length) {
      setStatus("Vyberte alespoň jeden obrázek.");
      return;
    }
    const id = manager.createItem({
      type: "Složka obrázků",
      title: "Hromadné obrázky",
      size: selectedItems.reduce((total, item) => total + item.file.size, 0),
      preview: `Vybráno ${selectedItems.length} obrázků`
    });
    const controller = new AbortController();
    manager.registerOperation(id, controller);
    manager.registerRetry(id, submit);
    manager.updateItem(id, { status: "uploading", progress: 0 });
    manager.addLog("info", "Zahájeno nahrávání složky obrázků.", { id });
    try {
      const formData = new FormData();
      let processed = 0;
      for (const item of selectedItems) {
        const validation = validateFile(item.file, { maxSize: 15 * 1024 * 1024, extensions });
        if (!validation.ok) {
          continue;
        }
        const compressed = await compressImage(item.file, { maxWidth: 1600, maxHeight: 1600 });
        const renamed = new File([compressed], item.file.name, { type: compressed.type });
        formData.append("files", renamed, item.file.webkitRelativePath || item.file.name);
        processed += 1;
        manager.updateItem(id, {
          progress: Math.round((processed / selectedItems.length) * 70)
        });
      }
      const zipEntries = selectedItems.map((item) => ({
        name: item.file.webkitRelativePath || item.file.name,
        blob: item.file
      }));
      const zipBlob = await createZipBlob(zipEntries);
      if (backupUrl) {
        URL.revokeObjectURL(backupUrl);
      }
      setBackupUrl(URL.createObjectURL(zipBlob));
      const response = await uploadWithProgress({
        url: "/api/context/image-folder",
        formData,
        signal: controller.signal,
        onProgress: (progress) =>
          manager.updateItem(id, { progress: 70 + Math.round(progress * 0.3) })
      });
      manager.updateItem(id, {
        status: "ready",
        progress: 100,
        preview: `Nahráno ${response.ok} z ${selectedItems.length}`
      });
      manager.recordMetric("image-folder", "success");
      manager.addLog("info", "Složka obrázků nahrána.", { id });
      setSummary(response);
      onClose();
    } catch (error) {
      const message = error.message || "Složka obrázků se nepodařila nahrát.";
      manager.updateItem(id, { status: "failed", error: message });
      manager.recordMetric("image-folder", message.includes("zrušena") ? "cancelled" : "failure");
      manager.addLog("error", message, { id });
      setStatus(message);
    }
  };

  return (
    <div className="context-action">
      <div className="context-action-row">
        <label className="ghost-button">
          Vybrat složku obrázků
          <input
            type="file"
            webkitdirectory="true"
            directory="true"
            className="file-input"
            onChange={(event) => handleFiles(event.target.files)}
          />
        </label>
        <button type="button" className="ghost-button" onClick={selectAll}>
          Vybrat vše
        </button>
        <button type="button" className="ghost-button" onClick={deselectAll}>
          Zrušit výběr
        </button>
        <label className="context-label">
          Velikost náhledu
          <select
            className="context-input"
            value={sizeId}
            onChange={(event) => setSizeId(event.target.value)}
          >
            {sizeOptions.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="image-grid">
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`image-card ${item.selected ? "selected" : ""}`}
            onClick={() => toggleSelect(item.id)}
            style={{ "--image-card-height": `${activeSize.height}px` }}
          >
            <Image
              src={item.previewUrl}
              alt={item.file.name}
              width={activeSize.width}
              height={activeSize.height}
              className="image-card-image"
              unoptimized
            />
            <div className="image-card-title">{item.file.name}</div>
          </button>
        ))}
      </div>
      {backupUrl ? (
        <a className="ghost-button" href={backupUrl} download="obrazky-backup.zip">
          Stáhnout ZIP zálohu
        </a>
      ) : null}
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
