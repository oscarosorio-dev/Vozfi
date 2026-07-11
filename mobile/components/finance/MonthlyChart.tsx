import { useMemo } from 'react';
import { Dimensions, StyleSheet, View } from 'react-native';
import { BarChart } from 'react-native-gifted-charts';

import { ThemedText } from '@/components/themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';
import type { MonthlySummary } from '@/lib/api';

const screenWidth = Dimensions.get('window').width;

function formatMonthLabel(month: string): string {
  const [year, monthNumber] = month.split('-');
  const date = new Date(Number(year), Number(monthNumber) - 1);
  return date.toLocaleDateString('es', { month: 'short' });
}

export function MonthlyChart({ data }: { data: MonthlySummary[] }) {
  const cardColor = useThemeColor({}, 'card');
  const mutedColor = useThemeColor({}, 'muted');
  const incomeColor = useThemeColor({}, 'income');
  const expenseColor = useThemeColor({}, 'expense');
  const textColor = useThemeColor({}, 'text');

  const chartData = useMemo(() => {
    return data.flatMap((item) => [
      { value: item.income, frontColor: incomeColor, label: formatMonthLabel(item.month) },
      { value: item.expense, frontColor: expenseColor, spacing: 20 },
    ]);
  }, [data, incomeColor, expenseColor]);

  if (data.length === 0) {
    return (
      <View style={[styles.container, { backgroundColor: cardColor }]}>
        <ThemedText style={{ color: mutedColor }}>Sin datos suficientes para graficar aún.</ThemedText>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: cardColor }]}>
      <ThemedText type="defaultSemiBold" style={styles.title}>
        Ingresos vs. gastos por mes
      </ThemedText>
      <BarChart
        data={chartData}
        barWidth={18}
        spacing={10}
        roundedTop
        noOfSections={4}
        yAxisThickness={0}
        xAxisThickness={0}
        yAxisTextStyle={{ color: mutedColor, fontSize: 10 }}
        xAxisLabelTextStyle={{ color: textColor, fontSize: 11 }}
        width={screenWidth - 96}
        height={180}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 16,
    padding: 16,
    gap: 12,
  },
  title: {
    fontSize: 14,
  },
});