import { useCallback } from 'react';
import {
  RecordingPresets,
  requestRecordingPermissionsAsync,
  setAudioModeAsync,
  useAudioRecorder,
  useAudioRecorderState,
} from 'expo-audio';

/**
 * `RecordingPresets.HIGH_QUALITY` produce un contenedor `.m4a` (MPEG-4 Audio),
 * cuyo content-type MIME estándar es `audio/mp4` — aceptado por el backend y por Groq.
 */
const RECORDING_MIME_TYPE = 'audio/mp4';

export function useVoiceRecorder() {
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const state = useAudioRecorderState(recorder);

  const startRecording = useCallback(async () => {
    const { granted } = await requestRecordingPermissionsAsync();
    if (!granted) {
      throw new Error('Permiso de micrófono denegado. Actívalo en los ajustes del sistema.');
    }

    await setAudioModeAsync({ allowsRecording: true, playsInSilentMode: true });
    await recorder.prepareToRecordAsync();
    recorder.record();
  }, [recorder]);

  const stopRecording = useCallback(async (): Promise<{ uri: string; mimeType: string } | null> => {
    await recorder.stop();
    if (!recorder.uri) return null;
    return { uri: recorder.uri, mimeType: RECORDING_MIME_TYPE };
  }, [recorder]);

  return {
    isRecording: state.isRecording,
    startRecording,
    stopRecording,
  };
}