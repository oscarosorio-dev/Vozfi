import { ScrollView, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { BalanceCard } from '@/components/finance/BalanceCard';
import { CategoryBreakdown } from '@/components/finance/CategoryBreakdown';
import { MonthlyChart } from '@/components/finance/MonthlyChart';
import { ThemedText } from '@/components/themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';
import { useCategorySummary } from '@/hooks/useCategorySummary';
import { useMonthlySummary } from '@/hooks/useMonthlySummary';

export default function SummaryScreen() {
  const monthly = useMonthlySummary();
  const categories = useCategorySummary();
  const mutedColor = useThemeColor({}, 'muted');
  const expenseColor = useThemeColor({}, 'expense');

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <ScrollView contentContainerStyle={styles.container}>
        <ThemedText type="title" style={styles.title}>
          Resumen
        </ThemedText>

        <BalanceCard />

        {monthly.isLoading ? (
          <ThemedText style={{ color: mutedColor }}>Cargando resumen mensual...</ThemedText>
        ) : monthly.isError ? (
          <ThemedText style={{ color: expenseColor }}>No se pudo cargar el resumen mensual</ThemedText>
        ) : (
          <MonthlyChart data={monthly.data ?? []} />
        )}

        {categories.isLoading ? (
          <ThemedText style={{ color: mutedColor }}>Cargando categorías...</ThemedText>
        ) : categories.isError ? (
          <ThemedText style={{ color: expenseColor }}>No se pudieron cargar las categorías</ThemedText>
        ) : (
          <CategoryBreakdown data={categories.data ?? []} />
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  container: {
    padding: 16,
    gap: 16,
  },
  title: {
    marginBottom: 4,
  },
});