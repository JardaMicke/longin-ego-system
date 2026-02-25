import { useEffect, useState } from "react";
import Image from "next/image";
import { compressImage, uploadWithProgress, validateFile } from "../../../utils/contextUtils";

const extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"];
const sizeOptions = [
  { id: "sm", label: "S", width: 240, height: 160 },
  { id: "md", label: "M", width: 320, height: 200 },
  { id: "lg", label: "L", width: 400, height: 260 },
  { id: "xl", label: "XL", width: 480, height: 320 }
];

export const ImageAction = ({ manager, onClose }) => {
  const [file, setFile] = useState(null);
  const [compressed, setCompressed] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [altText, setAltText] = useState("");
  const [status, setStatus] = useState("");
  const [sizeId, setSizeId] = useState("md");
  const activeSize = sizeOptions.find((option) => option.id === sizeId) ?? sizeOptions[1];

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFile = async (nextFile) => {
    if (!nextFile) {
      return;
    }
    const validation = validateFile(nextFile, { maxSize: 10 * 1024 * 1024, extensions });
    if (!validation.ok) {
      setStatus(validation.error);
      return;
    }
    setFile(nextFile);
    setStatus("");
    const compressedFile = await compressImage(nextFile, { maxWidth: 1600, maxHeight: 1600 });
    setCompressed(compressedFile);
    const url = URL.createObjectURL(compressedFile);
    setPreviewUrl(url);
  };

  const onPaste = async (event) => {
    const item = Array.from(event.clipboardData?.items || []).find((entry) =>
      entry.type.startsWith("image/")
    );
    if (item) {
      const blob = item.getAsFile();
      await handleFile(blob);
    }
  };

  const submit = async () => {
    if (!compressed) {
      setStatus("Vyberte obrázek.");
      return;
    }
    const id = manager.createItem({
      type: "Obrázek",
      title: compressed.name,
      size: compressed.size,
      preview: altText ? `Alt: ${altText}` : "Bez popisku"
    });
    const controller = new AbortController();
    manager.registerOperation(id, controller);
    manager.registerRetry(id, submit);
    manager.updateItem(id, { status: "uploading", progress: 0 });
    manager.addLog("info", "Zahájeno nahrávání obrázku.", { id });
    try {
      const formData = new FormData();
      formData.append("file", compressed);
      formData.append("altText", altText);
      await uploadWithProgress({
        url: "/api/context/image",
        formData,
        signal: controller.signal,
        onProgress: (progress) => manager.updateItem(id, { progress })
      });
      manager.updateItem(id, { status: "ready", progress: 100 });
      manager.recordMetric("image", "success");
      manager.addLog("info", "Obrázek nahrán.", { id });
      onClose();
    } catch (error) {
      const message = error.message || "Obrázek se nepodařilo nahrát.";
      manager.updateItem(id, { status: "failed", error: message });
      manager.recordMetric("image", message.includes("zrušena") ? "cancelled" : "failure");
      manager.addLog("error", message, { id });
      setStatus(message);
    }
  };

  return (
    <div className="context-action" onPaste={onPaste}>
      <div className="context-action-row">
        <label className="ghost-button">
          Vybrat obrázek
          <input
            type="file"
            accept={extensions.join(",")}
            className="file-input"
            onChange={(event) => handleFile(event.target.files?.[0])}
          />
        </label>
      </div>
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
      {previewUrl ? (
        <div className="context-preview">
          <Image
            src={previewUrl}
            alt={altText || "Náhled"}
            width={activeSize.width}
            height={activeSize.height}
            className="preview-image"
            unoptimized
          />
        </div>
      ) : null}
      <label className="context-label">
        Popisek / alt text
        <input
          className="context-input"
          value={altText}
          onChange={(event) => setAltText(event.target.value)}
        />
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
