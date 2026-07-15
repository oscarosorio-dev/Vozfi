import { useQuery } from '@tanstack/react-query';

import { listTransactions } from '@/lib/api';
import { queryKeys } from '@/lib/queryClient';

export function useTransactions() {
  return useQuery({
    queryKey: queryKeys.transactions,
    queryFn: listTransactions,
  });
}