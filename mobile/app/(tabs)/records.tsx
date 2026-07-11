import React, { useMemo, useState } from 'react';
import { FlatList, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { TransactionFilters, TransactionTypeFilter } from '@/components/finance/TransactionFilters';
import { TransactionRow } from '@/components/finance/TransactionRow';
import { ThemedText } from '@/components/themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';
import { useTransactions } from '@/hooks/useTransactions';
import { useDeleteTransaction } from '@/hooks/useDeleteTransaction';

/**
 * Pantalla de historial de transacciones con filtros de búsqueda y tipo de movimiento.
 */
export default function RecordsScreen() {
  const { data: transactions, isLoading, isError } = useTransactions();
  const deleteTransaction = useDeleteTransaction();

  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<TransactionTypeFilter>('all');

  const cardColor = useThemeColor({}, 'card');
  const mutedColor = useThemeColor({}, 'muted');
  const expenseColor = useThemeColor({}, 'expense');
  const borderColor = useThemeColor({}, 'border');

  const filteredTransactions = useMemo(() => {
    if (!transactions) return [];
    return transactions.filter((tx) => {
      const cleanSearch = search.trim().toLowerCase();
      const matchesSearch =
        !cleanSearch ||
        tx.category.toLowerCase().includes(cleanSearch) ||
        (tx.description && tx.description.toLowerCase().includes(cleanSearch));

      const matchesType = typeFilter === 'all' || tx.type === typeFilter;

      return matchesSearch && matchesType;
    });
  }, [transactions, search, typeFilter]);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <View style={styles.header}>
        <ThemedText type="title">Movimientos</ThemedText>
        <ThemedText style={{ color: mutedColor, fontSize: 13 }}>Historial de transacciones</ThemedText>
      </View>

      <TransactionFilters
        search={search}
        onSearchChange={setSearch}
        typeFilter={typeFilter}
        onTypeFilterChange={setTypeFilter}
      />

      <FlatList
        data={filteredTransactions}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        renderItem={({ item }) => (
          <TransactionRow
            transaction={item}
            onDelete={(id) => deleteTransaction.mutate(id)}
          />
        )}
        ListEmptyComponent={() => (
          <View style={styles.centerContainer}>
            {isLoading ? (
              <ThemedText style={{ color: mutedColor }}>Cargando transacciones...</ThemedText>
            ) : isError ? (
              <ThemedText style={{ color: expenseColor }}>Error al cargar las transacciones</ThemedText>
            ) : (
              <ThemedText style={{ color: mutedColor }}>No se encontraron movimientos</ThemedText>
            )}
          </View>
        )}
        style={[styles.list, { backgroundColor: cardColor, borderColor }]}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    gap: 16,
  },
  header: {
    paddingHorizontal: 16,
    paddingTop: 12,
  },
  list: {
    flex: 1,
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 16,
    borderWidth: StyleSheet.hairlineWidth,
  },
  listContainer: {
    flexGrow: 1,
  },
  centerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
  },
});