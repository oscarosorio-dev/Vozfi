import { useMutation, useQueryClient } from '@tanstack/react-query';

import { updateTransaction, type TransactionUpdate } from '@/lib/api';
import { queryKeys } from '@/lib/queryClient';

export function useUpdateTransaction(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TransactionUpdate) => updateTransaction(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transaction', id] });
      queryClient.invalidateQueries({ queryKey: queryKeys.transactions });
      queryClient.invalidateQueries({ queryKey: queryKeys.balance });
      queryClient.invalidateQueries({ queryKey: queryKeys.categorySummary });
      queryClient.invalidateQueries({ queryKey: queryKeys.monthlySummary });
    },
  });
}