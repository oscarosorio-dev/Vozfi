import { Pressable, StyleSheet, TextInput, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';

export type TransactionTypeFilter = 'all' | 'income' | 'expense';

type Props = {
  search: string;
  onSearchChange: (value: string) => void;
  typeFilter: TransactionTypeFilter;
  onTypeFilterChange: (value: TransactionTypeFilter) => void;
};

const OPTIONS: { value: TransactionTypeFilter; label: string }[] = [
  { value: 'all', label: 'Todos' },
  { value: 'income', label: 'Ingresos' },
  { value: 'expense', label: 'Gastos' },
];

export function TransactionFilters({ search, onSearchChange, typeFilter, onTypeFilterChange }: Props) {
  const cardColor = useThemeColor({}, 'card');
  const textColor = useThemeColor({}, 'text');
  const mutedColor = useThemeColor({}, 'muted');
  const tintColor = useThemeColor({}, 'tint');

  return (
    <View style={styles.container}>
      <TextInput
        value={search}
        onChangeText={onSearchChange}
        placeholder="Buscar por categoría o descripción"
        placeholderTextColor={mutedColor}
        style={[styles.input, { backgroundColor: cardColor, color: textColor }]}
      />

      <View style={styles.chips}>
        {OPTIONS.map((option) => {
          const active = typeFilter === option.value;
          return (
            <Pressable
              key={option.value}
              onPress={() => onTypeFilterChange(option.value)}
              style={[
                styles.chip,
                { backgroundColor: active ? tintColor : cardColor },
              ]}>
              <ThemedText style={{ color: active ? '#fff' : textColor, fontSize: 13 }}>{option.label}</ThemedText>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: 10,
    paddingHorizontal: 16,
  },
  input: {
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 15,
  },
  chips: {
    flexDirection: 'row',
    gap: 8,
  },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
  },
});