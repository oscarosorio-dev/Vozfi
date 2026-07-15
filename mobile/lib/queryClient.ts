import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

export const queryKeys = {
  balance: ['balance'] as const,
  transactions: ['transactions'] as const,
  categorySummary: ['summary', 'by-category'] as const,
  monthlySummary: ['summary', 'by-month'] as const,
};