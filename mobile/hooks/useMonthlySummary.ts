import { useQuery } from '@tanstack/react-query';

import { getMonthlySummary } from '@/lib/api';
import { queryKeys } from '@/lib/queryClient';

export function useMonthlySummary() {
  return useQuery({
    queryKey: queryKeys.monthlySummary,
    queryFn: getMonthlySummary,
  });
}