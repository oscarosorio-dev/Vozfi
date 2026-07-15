import { useQuery } from '@tanstack/react-query';

import { getTransaction } from '@/lib/api';

export function useTransaction(id: string) {
  return useQuery({
    queryKey: ['transaction', id],
    queryFn: () => getTransaction(id),
    enabled: !!id,
  });
}