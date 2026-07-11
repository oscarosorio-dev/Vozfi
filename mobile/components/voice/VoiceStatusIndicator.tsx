import { ThemedText } from '@/components/themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';
import type { VoicePipelineStatus } from '@/hooks/useVoicePipeline';

const LABELS: Record<VoicePipelineStatus, string> = {
  idle: 'Toca para hablar',
  recording: 'Escuchando... toca para detener',
  processing: 'Procesando...',
  speaking: 'Respondiendo...',
  error: 'Ocurrió un error',
};

export function VoiceStatusIndicator({ status, errorMessage }: { status: VoicePipelineStatus; errorMessage?: string | null }) {
  const expenseColor = useThemeColor({}, 'expense');
  const mutedColor = useThemeColor({}, 'muted');

  const label = status === 'error' && errorMessage ? errorMessage : LABELS[status];
  const color = status === 'error' ? expenseColor : mutedColor;

  return (
    <ThemedText style={{ color, textAlign: 'center' }}>
      {label}
    </ThemedText>
  );
}