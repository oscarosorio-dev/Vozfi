import { StyleSheet, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';
import type { VoiceInputResponse } from '@/lib/api';

export function ConversationFeedback({ result }: { result: VoiceInputResponse | null }) {
  const cardColor = useThemeColor({}, 'card');
  const mutedColor = useThemeColor({}, 'muted');

  if (!result) return null;

  return (
    <View style={[styles.container, { backgroundColor: cardColor }]}>
      <ThemedText style={{ color: mutedColor }} numberOfLines={2}>
        “{result.transcript}”
      </ThemedText>
      <ThemedText type="defaultSemiBold" style={styles.reply}>
        {result.reply}
      </ThemedText>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 16,
    padding: 16,
    gap: 8,
    width: '100%',
  },
  reply: {
    lineHeight: 22,
  },
});