/**
 * Custom hooks for fund data fetching
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { FundCompareRequest } from '../types/fund';

// Query keys
export const fundKeys = {
  all: ['funds'] as const,
  search: (query: string) => [...fundKeys.all, 'search', query] as const,
  info: (code: string) => [...fundKeys.all, 'info', code] as const,
  nav: (code: string, period: string) => [...fundKeys.all, 'nav', code, period] as const,
  holdings: (code: string) => [...fundKeys.all, 'holdings', code] as const,
  metrics: (code: string, period: string) => [...fundKeys.all, 'metrics', code, period] as const,
  realtime: (code: string) => [...fundKeys.all, 'realtime', code] as const,
  analysis: (code: string) => [...fundKeys.all, 'analysis', code] as const,
};

/**
 * Search funds by name or code
 */
export function useSearchFunds(query: string, enabled = true) {
  return useQuery({
    queryKey: fundKeys.search(query),
    queryFn: () => apiClient.searchFunds(query),
    enabled: enabled && query.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Get fund basic information
 */
export function useFundInfo(fundCode: string, enabled = true) {
  return useQuery({
    queryKey: fundKeys.info(fundCode),
    queryFn: () => apiClient.getFundInfo(fundCode),
    enabled: enabled && !!fundCode,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Get fund NAV history
 */
export function useFundNAVHistory(fundCode: string, period = '1y', enabled = true) {
  return useQuery({
    queryKey: fundKeys.nav(fundCode, period),
    queryFn: () => apiClient.getFundNAVHistory(fundCode, period),
    enabled: enabled && !!fundCode,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Get fund holdings
 */
export function useFundHoldings(fundCode: string, enabled = true) {
  return useQuery({
    queryKey: fundKeys.holdings(fundCode),
    queryFn: () => apiClient.getFundHoldings(fundCode),
    enabled: enabled && !!fundCode,
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}

/**
 * Get fund metrics
 */
export function useFundMetrics(fundCode: string, period = '3y', enabled = true) {
  return useQuery({
    queryKey: fundKeys.metrics(fundCode, period),
    queryFn: () => apiClient.getFundMetrics(fundCode, period),
    enabled: enabled && !!fundCode,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Get realtime estimate
 */
export function useRealtimeEstimate(fundCode: string, enabled = true) {
  return useQuery({
    queryKey: fundKeys.realtime(fundCode),
    queryFn: () => apiClient.getRealtimeEstimate(fundCode),
    enabled: enabled && !!fundCode,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 60 * 1000, // Refresh every minute
  });
}

/**
 * Get fund analysis report
 */
export function useFundAnalysis(fundCode: string, enabled = true) {
  return useQuery({
    queryKey: fundKeys.analysis(fundCode),
    queryFn: () => apiClient.getFundAnalysis(fundCode),
    enabled: enabled && !!fundCode,
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}

/**
 * Compare multiple funds
 */
export function useCompareFunds() {
  return useMutation({
    mutationFn: (request: FundCompareRequest) => apiClient.compareFunds(request),
  });
}
