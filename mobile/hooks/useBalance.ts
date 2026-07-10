import { useQuery } from '@tanstack/react-query';

import { getBalance } from '@/lib/api';
import { queryKeys } from '@/lib/queryClient';

export function useBalance() {
  return useQuery({
    queryKey: queryKeys.balance,
    queryFn: getBalance,
  });
}