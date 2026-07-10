import { useMutation, useQueryClient } from '@tanstack/react-query';

import { deleteTransaction } from '@/lib/api';
import { queryKeys } from '@/lib/queryClient';

export function useDeleteTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.transactions });
      queryClient.invalidateQueries({ queryKey: queryKeys.balance });
      queryClient.invalidateQueries({ queryKey: queryKeys.categorySummary });
      queryClient.invalidateQueries({ queryKey: queryKeys.monthlySummary });
    },
  });
}