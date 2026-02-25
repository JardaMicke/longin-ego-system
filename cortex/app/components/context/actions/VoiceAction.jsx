import { useEffect, useMemo, useRef, useState } from "react";
import { uploadWithProgress, validateFile } from "../../../utils/contextUtils";

const mimeTypes = ["audio/wav", "audio/mpeg", "audio/mp4", "audio/webm"];

export const VoiceAction = ({ manager, onClose }) => {
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState("");
  const [transcript, setTranscript] = useState("");
  const [status, setStatus] = useState("");
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const supportedType = useMemo(
    () => mimeTypes.find((type) => MediaRecorder.isTypeSupported(type)) ?? "",
    []
  );

  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, supportedType ? { mimeType: supportedType } : {});
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm"
        });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach((track) => track.stop());
      };
      recorder.start();
      setRecording(true);
      setStatus("Nahrávání...");
    } catch (error) {
      setStatus("Nahrávání se nepodařilo spustit.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      setStatus("Nahrávání zastaveno.");
    }
  };

  const clearRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
    }
    setRecording(false);
    setAudioBlob(null);
    setAudioUrl("");
    setTranscript("");
    setStatus("");
  };

  const transcribeAudio = async () => {
    if (!audioBlob) {
      setStatus("Nejprve nahrajte zvuk.");
      return;
    }
    try {
      setStatus("Probíhá přepis...");
      const formData = new FormData();
      formData.append("file", new File([audioBlob], "voice.webm", { type: audioBlob.type }));
      const response = await fetch("/api/context/stt", { method: "POST", body: formData });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.error ?? "Přepis selhal.");
      }
      setTranscript(data.text ?? "");
      setStatus("Přepis hotov.");
    } catch (error) {
      setStatus(error.message);
    }
  };

  const submit = async () => {
    if (!audioBlob) {
      setStatus("Chybí nahrávka.");
      return;
    }
    const file = new File([audioBlob], "voice.webm", { type: audioBlob.type });
    const validation = validateFile(file, {
      maxSize: 10 * 1024 * 1024,
      extensions: [".wav", ".mp3", ".m4a", ".webm"]
    });
    if (!validation.ok) {
      setStatus(validation.error);
      return;
    }
    const id = manager.createItem({
      type: "Hlas",
      title: "Hlasová zpráva",
      size: file.size,
      preview: transcript ? `Přepis: ${transcript.slice(0, 140)}` : "Bez přepisu"
    });
    const controller = new AbortController();
    manager.registerOperation(id, controller);
    manager.registerRetry(id, submit);
    manager.updateItem(id, { status: "uploading", progress: 0 });
    manager.addLog("info", "Zahájeno nahrávání hlasu.", { id });
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("transcript", transcript);
      await uploadWithProgress({
        url: "/api/context/voice",
        formData,
        signal: controller.signal,
        onProgress: (progress) => manager.updateItem(id, { progress })
      });
      manager.updateItem(id, { status: "ready", progress: 100 });
      manager.recordMetric("voice", "success");
      manager.addLog("info", "Hlasová zpráva odeslána.", { id });
      onClose();
    } catch (error) {
      const message = error.message || "Hlasová zpráva selhala.";
      manager.updateItem(id, { status: "failed", error: message });
      manager.recordMetric("voice", message.includes("zrušena") ? "cancelled" : "failure");
      manager.addLog("error", message, { id });
      setStatus(message);
    }
  };

  return (
    <div className="context-action">
      <div className="context-action-row">
        <button type="button" className="primary-button" onClick={startRecording} disabled={recording}>
          Spustit nahrávání
        </button>
        <button type="button" className="ghost-button" onClick={stopRecording} disabled={!recording}>
          Zastavit
        </button>
        <button type="button" className="ghost-button" onClick={clearRecording}>
          Reset
        </button>
      </div>
      {status ? <div className="context-status">{status}</div> : null}
      {audioUrl ? (
        <div className="context-preview">
          <audio controls src={audioUrl} />
        </div>
      ) : null}
      <div className="context-action-row">
        <button type="button" className="ghost-button" onClick={transcribeAudio} disabled={!audioBlob}>
          Přepsat
        </button>
      </div>
      <textarea
        className="context-textarea"
        rows={4}
        value={transcript}
        onChange={(event) => setTranscript(event.target.value)}
        placeholder="Přepis zprávy..."
      />
      <div className="context-action-row">
        <button type="button" className="primary-button" onClick={submit}>
          Přidat do kontextu
        </button>
      </div>
    </div>
  );
};
