import { StyleSheet, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';
import { useBalance } from '@/hooks/useBalance';

export function BalanceCard() {
  const { data, isLoading, isError } = useBalance();
  const cardColor = useThemeColor({}, 'card');
  const incomeColor = useThemeColor({}, 'income');
  const expenseColor = useThemeColor({}, 'expense');
  const mutedColor = useThemeColor({}, 'muted');

  if (isLoading) {
    return (
      <View style={[styles.container, { backgroundColor: cardColor }]}>
        <ThemedText style={{ color: mutedColor }}>Cargando balance...</ThemedText>
      </View>
    );
  }

  if (isError || !data) {
    return (
      <View style={[styles.container, { backgroundColor: cardColor }]}>
        <ThemedText style={{ color: expenseColor }}>No se pudo cargar el balance</ThemedText>
      </View>
    );
  }

  const balanceColor = data.balance >= 0 ? incomeColor : expenseColor;

  return (
    <View style={[styles.container, { backgroundColor: cardColor }]}>
      <View style={styles.row}>
        <View style={styles.column}>
          <ThemedText style={[styles.label, { color: mutedColor }]}>Ingresos</ThemedText>
          <ThemedText type="defaultSemiBold" style={{ color: incomeColor }}>
            {data.income.toFixed(2)}
          </ThemedText>
        </View>
        <View style={styles.column}>
          <ThemedText style={[styles.label, { color: mutedColor }]}>Gastos</ThemedText>
          <ThemedText type="defaultSemiBold" style={{ color: expenseColor }}>
            {data.expense.toFixed(2)}
          </ThemedText>
        </View>
        <View style={styles.column}>
          <ThemedText style={[styles.label, { color: mutedColor }]}>Balance</ThemedText>
          <ThemedText type="defaultSemiBold" style={{ color: balanceColor }}>
            {data.balance.toFixed(2)}
          </ThemedText>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 16,
    padding: 16,
    width: '100%',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  column: {
    alignItems: 'center',
    gap: 4,
  },
  label: {
    fontSize: 12,
  },
});