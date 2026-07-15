import { router } from 'expo-router';
import { Pressable, StyleSheet, View } from 'react-native';
import ReanimatedSwipeable from 'react-native-gesture-handler/ReanimatedSwipeable';
import Animated, { type SharedValue, useAnimatedStyle } from 'react-native-reanimated';
import * as Haptics from 'expo-haptics';

import { ThemedText } from '@/components/themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';
import type { Transaction } from '@/lib/api';

type Props = {
  transaction: Transaction;
  onDelete: (id: string) => void;
};

function DeleteAction({ progress, onPress }: { progress: SharedValue<number>; onPress: () => void }) {
  const style = useAnimatedStyle(() => ({
    transform: [{ scale: progress.value }],
  }));

  return (
    <Pressable onPress={onPress} style={styles.deleteAction}>
      <Animated.View style={style}>
        <ThemedText style={styles.deleteText}>Eliminar</ThemedText>
      </Animated.View>
    </Pressable>
  );
}

export function TransactionRow({ transaction, onDelete }: Props) {
  const cardColor = useThemeColor({}, 'card');
  const borderColor = useThemeColor({}, 'border');
  const mutedColor = useThemeColor({}, 'muted');
  const incomeColor = useThemeColor({}, 'income');
  const expenseColor = useThemeColor({}, 'expense');

  const amountColor = transaction.type === 'income' ? incomeColor : expenseColor;
  const sign = transaction.type === 'income' ? '+' : '-';

  function handleDelete() {
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    onDelete(transaction.id);
  }

  return (
    <ReanimatedSwipeable
      renderRightActions={(progress) => <DeleteAction progress={progress} onPress={handleDelete} />}
      overshootRight={false}>
      <Pressable
        onPress={() => router.push(`/transaction/${transaction.id}`)}
        style={[styles.row, { backgroundColor: cardColor, borderBottomColor: borderColor }]}>
        <View style={styles.info}>
          <ThemedText type="defaultSemiBold">{transaction.category}</ThemedText>
          {transaction.description ? (
            <ThemedText style={{ color: mutedColor, fontSize: 13 }} numberOfLines={1}>
              {transaction.description}
            </ThemedText>
          ) : null}
        </View>
        <ThemedText type="defaultSemiBold" style={{ color: amountColor }}>
          {sign}
          {transaction.amount.toFixed(2)}
        </ThemedText>
      </Pressable>
    </ReanimatedSwipeable>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  info: {
    flex: 1,
    gap: 2,
    paddingRight: 12,
  },
  deleteAction: {
    backgroundColor: '#dc2626',
    justifyContent: 'center',
    alignItems: 'center',
    width: 88,
  },
  deleteText: {
    color: '#fff',
    fontWeight: '600',
  },
});