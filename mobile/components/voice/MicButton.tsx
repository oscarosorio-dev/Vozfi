import { useEffect } from 'react';
import { Pressable, StyleSheet } from 'react-native';
import Animated, {
  cancelAnimation,
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
} from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';

import { IconSymbol } from '@/components/ui/icon-symbol';
import { useThemeColor } from '@/hooks/use-theme-color';
import type { VoicePipelineStatus } from '@/hooks/useVoicePipeline';

type Props = {
  status: VoicePipelineStatus;
  onPressIn: () => void;
  onPressOut: () => void;
};

const SIZE = 96;

export function MicButton({ status, onPressIn, onPressOut }: Props) {
  const pulse = useSharedValue(1);
  const tint = useThemeColor({}, 'tint');
  const expenseColor = useThemeColor({}, 'expense');
  const disabled = status === 'processing' || status === 'speaking';

  useEffect(() => {
    if (status === 'recording') {
      pulse.value = withRepeat(withTiming(1.15, { duration: 700 }), -1, true);
    } else {
      cancelAnimation(pulse);
      pulse.value = withTiming(1, { duration: 200 });
    }
  }, [status, pulse]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulse.value }],
  }));

  function handlePressIn() {
    if (disabled) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    onPressIn();
  }

  function handlePressOut() {
    if (disabled) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    onPressOut();
  }

  const backgroundColor = status === 'recording' ? expenseColor : tint;
  const iconName = 'mic.fill';

  return (
    <Animated.View style={animatedStyle}>
      <Pressable
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        disabled={disabled}
        style={[styles.button, { backgroundColor, opacity: disabled ? 0.6 : 1 }]}
        accessibilityRole="button"
        accessibilityLabel={status === 'recording' ? 'Soltar para enviar' : 'Mantener presionado para grabar'}>
        <IconSymbol name={iconName} size={40} color="" />
      </Pressable>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  button: {
    width: SIZE,
    height: SIZE,
    borderRadius: SIZE / 2,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
  },
});