import { useEffect, useState } from 'react';
import { router, useLocalSearchParams } from 'expo-router';
import { Alert, Pressable, ScrollView, StyleSheet, TextInput, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { useThemeColor } from '@/hooks/use-theme-color';
import { useDeleteTransaction } from '@/hooks/useDeleteTransaction';
import { useTransaction } from '@/hooks/useTransaction';
import { useUpdateTransaction } from '@/hooks/useUpdateTransaction';

export default function TransactionDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { data, isLoading, isError } = useTransaction(id);
  const updateTransaction = useUpdateTransaction(id);
  const deleteTransaction = useDeleteTransaction();

  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');

  const cardColor = useThemeColor({}, 'card');
  const textColor = useThemeColor({}, 'text');
  const mutedColor = useThemeColor({}, 'muted');
  const borderColor = useThemeColor({}, 'border');
  const tintColor = useThemeColor({}, 'tint');
  const expenseColor = useThemeColor({}, 'expense');
  const incomeColor = useThemeColor({}, 'income');

  useEffect(() => {
    if (data) {
      setAmount(String(data.amount));
      setCategory(data.category);
      setDescription(data.description ?? '');
    }
  }, [data]);

  if (isLoading) {
    return (
      <ThemedView style={styles.centerContainer}>
        <ThemedText>Cargando...</ThemedText>
      </ThemedView>
    );
  }

  if (isError || !data) {
    return (
      <ThemedView style={styles.centerContainer}>
        <ThemedText style={{ color: expenseColor }}>No se pudo cargar la transacción</ThemedText>
      </ThemedView>
    );
  }

  const parsedAmount = Number(amount.replace(',', '.'));
  const isAmountValid = !Number.isNaN(parsedAmount) && parsedAmount > 0;
  const hasChanges =
    parsedAmount !== data.amount || category !== data.category || description !== (data.description ?? '');
  const transactionId = data.id;

  function handleSave() {
    if (!isAmountValid || category.trim().length === 0) {
      Alert.alert('Datos inválidos', 'Verifica el monto y la categoría.');
      return;
    }

    updateTransaction.mutate(
      {
        amount: parsedAmount,
        category: category.trim(),
        description: description.trim().length > 0 ? description.trim() : null,
      },
      { onSuccess: () => router.back() }
    );
  }

  function handleDelete() {
    Alert.alert('Eliminar transacción', 'Esta acción no se puede deshacer.', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Eliminar',
        style: 'destructive',
        onPress: () => deleteTransaction.mutate(transactionId, { onSuccess: () => router.back() }),
      },
    ]);
  }

  const typeColor = data.type === 'income' ? incomeColor : expenseColor;
  const typeLabel = data.type === 'income' ? 'Ingreso' : 'Gasto';

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={[styles.typeBadge, { backgroundColor: typeColor }]}>
        <ThemedText style={styles.typeBadgeText}>{typeLabel}</ThemedText>
      </View>

      <View style={styles.field}>
        <ThemedText style={{ color: mutedColor, fontSize: 13 }}>Monto</ThemedText>
        <TextInput
          value={amount}
          onChangeText={setAmount}
          keyboardType="decimal-pad"
          style={[styles.input, { backgroundColor: cardColor, color: textColor, borderColor }]}
        />
      </View>

      <View style={styles.field}>
        <ThemedText style={{ color: mutedColor, fontSize: 13 }}>Categoría</ThemedText>
        <TextInput
          value={category}
          onChangeText={setCategory}
          style={[styles.input, { backgroundColor: cardColor, color: textColor, borderColor }]}
        />
      </View>

      <View style={styles.field}>
        <ThemedText style={{ color: mutedColor, fontSize: 13 }}>Descripción (opcional)</ThemedText>
        <TextInput
          value={description}
          onChangeText={setDescription}
          style={[styles.input, { backgroundColor: cardColor, color: textColor, borderColor }]}
        />
      </View>

      <View style={styles.field}>
        <ThemedText style={{ color: mutedColor, fontSize: 13 }}>Fecha</ThemedText>
        <ThemedText>{new Date(data.occurred_at).toLocaleString()}</ThemedText>
      </View>

      <Pressable
        onPress={handleSave}
        disabled={!hasChanges || !isAmountValid || updateTransaction.isPending}
        style={[
          styles.button,
          { backgroundColor: tintColor, opacity: !hasChanges || !isAmountValid ? 0.5 : 1 },
        ]}>
        <ThemedText style={styles.buttonText}>
          {updateTransaction.isPending ? 'Guardando...' : 'Guardar cambios'}
        </ThemedText>
      </Pressable>

      <Pressable onPress={handleDelete} style={[styles.button, styles.deleteButton]}>
        <ThemedText style={[styles.buttonText, { color: expenseColor }]}>Eliminar transacción</ThemedText>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    gap: 16,
  },
  centerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  typeBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  typeBadgeText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 12,
  },
  field: {
    gap: 6,
  },
  input: {
    borderRadius: 10,
    borderWidth: StyleSheet.hairlineWidth,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
  },
  button: {
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 8,
  },
  deleteButton: {
    backgroundColor: 'transparent',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
});