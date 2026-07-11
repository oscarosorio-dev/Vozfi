"use client";

import { useRef, useState } from "react";
import { sendVoiceInput, type VoiceInputResponse } from "@/lib/api";

type Props = {
  onResult?: (result: VoiceInputResponse) => void;
};

export default function VoiceRecorder({ onResult }: Props) {
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VoiceInputResponse | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  async function startRecording() {
    setError(null);
    setResult(null);

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mimeType = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "audio/ogg";
    const recorder = new MediaRecorder(stream, { mimeType });

    chunksRef.current = [];
    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };
    recorder.onstop = () => {
      stream.getTracks().forEach((track) => track.stop());
      void submitAudio(new Blob(chunksRef.current, { type: mimeType }));
    };

    mediaRecorderRef.current = recorder;
    recorder.start();
    setRecording(true);
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  }

  async function submitAudio(blob: Blob) {
    setLoading(true);
    setError(null);

    try {
      const response = await sendVoiceInput(blob);
      setResult(response);
      onResult?.(response);

      if (response.audio_base64 && response.audio_content_type) {
        const audio = new Audio(`data:${response.audio_content_type};base64,${response.audio_base64}`);
        void audio.play();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al procesar el audio");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center gap-4 p-6 border rounded-lg">
      <button
        onClick={recording ? stopRecording : startRecording}
        disabled={loading}
        className={`px-6 py-3 rounded-full font-medium text-white transition-colors ${
          recording ? "bg-red-600 hover:bg-red-700" : "bg-blue-600 hover:bg-blue-700"
        } disabled:opacity-50`}
      >
        {loading ? "Procesando..." : recording ? "Detener" : "Hablar"}
      </button>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      {result && (
        <div className="w-full text-sm space-y-1">
          <p className="text-gray-500">
            <span className="font-medium">Escuché:</span> {result.transcript}
          </p>
          <p className="text-gray-900">
            <span className="font-medium">Respuesta:</span> {result.reply}
          </p>
        </div>
      )}
    </div>
  );
}