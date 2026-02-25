export const formatBytes = (bytes) => {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return "0 B";
  }
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** index;
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[index]}`;
};

export const normalizeExtension = (name) => {
  if (!name) {
    return "";
  }
  const parts = name.toLowerCase().split(".");
  return parts.length > 1 ? `.${parts.pop()}` : "";
};

export const validateFile = (file, rules) => {
  if (!file) {
    return { ok: false, error: "Soubor není k dispozici." };
  }
  const maxSize = rules?.maxSize ?? 10 * 1024 * 1024;
  if (file.size > maxSize) {
    return { ok: false, error: `Soubor je větší než ${formatBytes(maxSize)}.` };
  }
  const ext = normalizeExtension(file.name);
  if (rules?.extensions?.length && !rules.extensions.includes(ext)) {
    return { ok: false, error: `Nepodporovaný formát ${ext || "souboru"}.` };
  }
  if (rules?.mimeTypes?.length && file.type && !rules.mimeTypes.includes(file.type)) {
    return { ok: false, error: `Nepodporovaný typ ${file.type}.` };
  }
  return { ok: true };
};

export const readFileAsText = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result ?? "");
    reader.onerror = () => reject(new Error("Soubor se nepodařilo načíst."));
    reader.readAsText(file);
  });

export const isTextFile = (file) => {
  if (!file) {
    return false;
  }
  if (file.type.startsWith("text/")) {
    return true;
  }
  const ext = normalizeExtension(file.name);
  return [".md", ".txt", ".json", ".csv", ".log", ".yaml", ".yml"].includes(ext);
};

export const stripHtml = (html) => {
  if (!html) {
    return "";
  }
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<\/(nav|header|footer|aside)>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
};

export const parseRepoUrl = (input) => {
  if (!input) {
    return null;
  }
  const value = input.trim();
  const github = value.match(/github\.com[:/](?<owner>[^/]+)\/(?<repo>[^/#.]+)/i);
  if (github?.groups) {
    return { provider: "github", ...github.groups };
  }
  const gitlab = value.match(/gitlab\.com[:/](?<owner>[^/]+)\/(?<repo>[^/#.]+)/i);
  if (gitlab?.groups) {
    return { provider: "gitlab", ...gitlab.groups };
  }
  const bitbucket = value.match(/bitbucket\.org[:/](?<owner>[^/]+)\/(?<repo>[^/#.]+)/i);
  if (bitbucket?.groups) {
    return { provider: "bitbucket", ...bitbucket.groups };
  }
  return null;
};

export const dedupeByName = (items) => {
  const seen = new Set();
  return items.filter((item) => {
    if (!item?.name) {
      return false;
    }
    if (seen.has(item.name)) {
      return false;
    }
    seen.add(item.name);
    return true;
  });
};

export const parseId3v2 = (buffer) => {
  try {
    const data = new Uint8Array(buffer);
    const header = String.fromCharCode(data[0], data[1], data[2]);
    if (header !== "ID3") {
      return {};
    }
    const size =
      ((data[6] & 0x7f) << 21) |
      ((data[7] & 0x7f) << 14) |
      ((data[8] & 0x7f) << 7) |
      (data[9] & 0x7f);
    let offset = 10;
    const tags = {};
    while (offset + 10 < size) {
      const frameId = String.fromCharCode(
        data[offset],
        data[offset + 1],
        data[offset + 2],
        data[offset + 3]
      );
      const frameSize =
        (data[offset + 4] << 24) |
        (data[offset + 5] << 16) |
        (data[offset + 6] << 8) |
        data[offset + 7];
      if (!frameId.trim()) {
        break;
      }
      const frameData = data.slice(offset + 10, offset + 10 + frameSize);
      if (frameData.length > 1) {
        const text = new TextDecoder().decode(frameData.slice(1)).trim();
        if (frameId === "TIT2") {
          tags.title = text;
        }
        if (frameId === "TPE1") {
          tags.artist = text;
        }
        if (frameId === "TALB") {
          tags.album = text;
        }
      }
      offset += 10 + frameSize;
    }
    return tags;
  } catch (error) {
    return {};
  }
};

export const buildTree = (paths) => {
  const root = { name: "root", children: [] };
  paths.forEach((path) => {
    const parts = path.split("/");
    let current = root;
    parts.forEach((part, index) => {
      let node = current.children.find((child) => child.name === part);
      if (!node) {
        node = { name: part, children: [] };
        current.children.push(node);
      }
      if (index === parts.length - 1) {
        node.isLeaf = true;
      }
      current = node;
    });
  });
  return root;
};

export const uploadWithProgress = ({ url, formData, signal, onProgress }) =>
  new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.responseType = "json";
    xhr.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable) {
        onProgress?.(Math.round((event.loaded / event.total) * 100));
      }
    });
    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(xhr.response);
      } else {
        reject(new Error(xhr.response?.error ?? "Nahrávání selhalo."));
      }
    });
    xhr.addEventListener("error", () => reject(new Error("Nahrávání selhalo.")));
    if (signal) {
      signal.addEventListener("abort", () => {
        xhr.abort();
        reject(new Error("Operace byla zrušena."));
      });
    }
    xhr.send(formData);
  });

export const compressImage = async (file, options) => {
  const maxWidth = options?.maxWidth ?? 1600;
  const maxHeight = options?.maxHeight ?? 1600;
  const quality = options?.quality ?? 0.8;
  const bitmap = await createImageBitmap(file);
  const ratio = Math.min(maxWidth / bitmap.width, maxHeight / bitmap.height, 1);
  const targetWidth = Math.round(bitmap.width * ratio);
  const targetHeight = Math.round(bitmap.height * ratio);
  const canvas = document.createElement("canvas");
  canvas.width = targetWidth;
  canvas.height = targetHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(bitmap, 0, 0, targetWidth, targetHeight);
  const blob = await new Promise((resolve) =>
    canvas.toBlob(resolve, "image/jpeg", quality)
  );
  return new File([blob], file.name.replace(/\.\w+$/, ".jpg"), { type: "image/jpeg" });
};

const crcTable = (() => {
  const table = new Uint32Array(256);
  for (let i = 0; i < 256; i += 1) {
    let c = i;
    for (let k = 0; k < 8; k += 1) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[i] = c >>> 0;
  }
  return table;
})();

const crc32 = (data) => {
  let crc = 0xffffffff;
  for (let i = 0; i < data.length; i += 1) {
    crc = crcTable[(crc ^ data[i]) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
};

const createHeader = (length) => {
  const buffer = new ArrayBuffer(length);
  return { view: new DataView(buffer), bytes: new Uint8Array(buffer) };
};

export const createZipBlob = async (entries) => {
  const encoder = new TextEncoder();
  const localParts = [];
  const centralParts = [];
  let offset = 0;
  for (const entry of entries) {
    const nameBytes = encoder.encode(entry.name);
    const data = new Uint8Array(await entry.blob.arrayBuffer());
    const checksum = crc32(data);
    const localHeader = createHeader(30);
    localHeader.view.setUint32(0, 0x04034b50, true);
    localHeader.view.setUint16(4, 20, true);
    localHeader.view.setUint16(6, 0, true);
    localHeader.view.setUint16(8, 0, true);
    localHeader.view.setUint16(10, 0, true);
    localHeader.view.setUint16(12, 0, true);
    localHeader.view.setUint32(14, checksum, true);
    localHeader.view.setUint32(18, data.length, true);
    localHeader.view.setUint32(22, data.length, true);
    localHeader.view.setUint16(26, nameBytes.length, true);
    localHeader.view.setUint16(28, 0, true);
    localParts.push(localHeader.bytes, nameBytes, data);

    const centralHeader = createHeader(46);
    centralHeader.view.setUint32(0, 0x02014b50, true);
    centralHeader.view.setUint16(4, 20, true);
    centralHeader.view.setUint16(6, 20, true);
    centralHeader.view.setUint16(8, 0, true);
    centralHeader.view.setUint16(10, 0, true);
    centralHeader.view.setUint16(12, 0, true);
    centralHeader.view.setUint16(14, 0, true);
    centralHeader.view.setUint32(16, checksum, true);
    centralHeader.view.setUint32(20, data.length, true);
    centralHeader.view.setUint32(24, data.length, true);
    centralHeader.view.setUint16(28, nameBytes.length, true);
    centralHeader.view.setUint16(30, 0, true);
    centralHeader.view.setUint16(32, 0, true);
    centralHeader.view.setUint16(34, 0, true);
    centralHeader.view.setUint16(36, 0, true);
    centralHeader.view.setUint32(38, 0, true);
    centralHeader.view.setUint32(42, offset, true);
    centralParts.push(centralHeader.bytes, nameBytes);

    offset += 30 + nameBytes.length + data.length;
  }

  const centralSize = centralParts.reduce((total, part) => total + part.length, 0);
  const endRecord = createHeader(22);
  endRecord.view.setUint32(0, 0x06054b50, true);
  endRecord.view.setUint16(4, 0, true);
  endRecord.view.setUint16(6, 0, true);
  endRecord.view.setUint16(8, entries.length, true);
  endRecord.view.setUint16(10, entries.length, true);
  endRecord.view.setUint32(12, centralSize, true);
  endRecord.view.setUint32(16, offset, true);
  endRecord.view.setUint16(20, 0, true);

  return new Blob([...localParts, ...centralParts, endRecord.bytes], {
    type: "application/zip"
  });
};
