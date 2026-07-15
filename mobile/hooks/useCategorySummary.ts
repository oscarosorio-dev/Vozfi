import { useQuery } from '@tanstack/react-query';

import { getCategorySummary } from '@/lib/api';
import { queryKeys } from '@/lib/queryClient';

export function useCategorySummary() {
  return useQuery({
    queryKey: queryKeys.categorySummary,
    queryFn: getCategorySummary,
  });
}