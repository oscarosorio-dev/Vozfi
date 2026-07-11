import { useMemo } from 'react';
import { StyleSheet, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';
import type { CategorySummary } from '@/lib/api';

export function CategoryBreakdown({ data }: { data: CategorySummary[] }) {
  const cardColor = useThemeColor({}, 'card');
  const borderColor = useThemeColor({}, 'border');
  const mutedColor = useThemeColor({}, 'muted');
  const incomeColor = useThemeColor({}, 'income');
  const expenseColor = useThemeColor({}, 'expense');

  const maxTotal = useMemo(() => Math.max(...data.map((item) => item.total), 1), [data]);

  if (data.length === 0) {
    return (
      <View style={[styles.container, { backgroundColor: cardColor }]}>
        <ThemedText style={{ color: mutedColor }}>Sin categorías registradas aún.</ThemedText>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: cardColor }]}>
      <ThemedText type="defaultSemiBold" style={styles.title}>
        Por categoría
      </ThemedText>
      {data.map((item) => {
        const color = item.type === 'income' ? incomeColor : expenseColor;
        const widthPercent = (item.total / maxTotal) * 100;

        return (
          <View key={`${item.category}-${item.type}`} style={styles.row}>
            <View style={styles.rowHeader}>
              <ThemedText style={{ fontSize: 13 }}>{item.category}</ThemedText>
              <ThemedText style={{ fontSize: 13, color }}>{item.total.toFixed(2)}</ThemedText>
            </View>
            <View style={[styles.barTrack, { backgroundColor: borderColor }]}>
              <View style={[styles.barFill, { width: `${widthPercent}%`, backgroundColor: color }]} />
            </View>
          </View>
        );
      })}
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
  row: {
    gap: 4,
  },
  rowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  barTrack: {
    height: 6,
    borderRadius: 3,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 3,
  },
});