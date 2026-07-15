import { useCallback, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { createAudioPlayer, setAudioModeAsync } from 'expo-audio';
import { File, Paths } from 'expo-file-system';

import { sendVoiceInput, type VoiceInputResponse } from '@/lib/api';
import { queryKeys } from '@/lib/queryClient';
import { useVoiceRecorder } from '@/hooks/useVoiceRecorder';

export type VoicePipelineStatus = 'idle' | 'recording' | 'processing' | 'speaking' | 'error';

/**
 * Escribe el audio TTS (base64) a un archivo temporal y lo reproduce.
 * Resuelve la promesa cuando la reproducción termina (evento `didJustFinish`),
 * para poder reflejar el estado "speaking" con precisión en la UI.
 */
async function playResponseAudio(audioBase64: string, contentType: string): Promise<void> {
  const extension = contentType.split('/')[1]?.split(';')[0] ?? 'mp3';
  const file = new File(Paths.cache, `vozfi-reply-${Date.now()}.${extension}`);
  file.create();
  file.write(audioBase64, { encoding: 'base64' });

  await setAudioModeAsync({ playsInSilentMode: true, allowsRecording: false });
  const player = createAudioPlayer({ uri: file.uri });

  await new Promise<void>((resolve) => {
    const subscription = player.addListener('playbackStatusUpdate', (status) => {
      if (status.didJustFinish) {
        subscription.remove();
        resolve();
      }
    });
    player.play();
  });
}

export function useVoicePipeline() {
  const { isRecording, startRecording, stopRecording } = useVoiceRecorder();
  const [status, setStatus] = useState<VoicePipelineStatus>('idle');
  const [result, setResult] = useState<VoiceInputResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const start = useCallback(async () => {
    setError(null);
    setResult(null);
    try {
      await startRecording();
      setStatus('recording');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo iniciar la grabación');
      setStatus('error');
    }
  }, [startRecording]);

const stop = useCallback(async () => {
    // Si el grabador no está activo (ej. toque ultra rápido o error al iniciar),
    // cancelamos de forma segura sin intentar subir un audio inexistente.
    if (!isRecording) {
      try {
        await stopRecording();
      } catch {}
      setStatus('idle');
      return;
    }

    setStatus('processing');
    try {
      const recording = await stopRecording();
      if (!recording) {
        throw new Error('No se detectó audio grabado');
      }

      const response = await sendVoiceInput(recording.uri, recording.mimeType);
      setResult(response);

      queryClient.invalidateQueries({ queryKey: queryKeys.balance });
      queryClient.invalidateQueries({ queryKey: queryKeys.transactions });
      queryClient.invalidateQueries({ queryKey: queryKeys.categorySummary });
      queryClient.invalidateQueries({ queryKey: queryKeys.monthlySummary });

      if (response.audio_base64 && response.audio_content_type) {
        setStatus('speaking');
        await playResponseAudio(response.audio_base64, response.audio_content_type);
      }

      setStatus('idle');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo procesar el audio');
      setStatus('error');
    }
  }, [stopRecording, queryClient, isRecording]); // Agregamos isRecording como dependencia

  return { status, isRecording, result, error, start, stop };
}