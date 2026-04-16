/**
 * Custom hooks for fund data fetching
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { DCASimulateRequest, FundCompareRequest, FundRecommendRequest } from '../types/fund';

// Query keys
export const fundKeys = {
  all: ['funds'] as const,
  featured: (limit: number) => [...fundKeys.all, 'featured', limit] as const,
  search: (query: string, category?: string) =>
    [...fundKeys.all, 'search', query, category ?? 'all'] as const,
  info: (code: string) => [...fundKeys.all, 'info', code] as const,
  nav: (code: string, period: string) => [...fundKeys.all, 'nav', code, period] as const,
  holdings: (code: string) => [...fundKeys.all, 'holdings', code] as const,
  metrics: (code: string, period: string) => [...fundKeys.all, 'metrics', code, period] as const,
  realtime: (code: string) => [...fundKeys.all, 'realtime', code] as const,
  analysis: (code: string) => [...fundKeys.all, 'analysis', code] as const,
};

/**
 * 首页今日推荐（后端按日轮换抽样）
 */
export function useFeaturedFunds(limit = 8) {
  return useQuery({
    queryKey: fundKeys.featured(limit),
    queryFn: () => apiClient.getFeaturedFunds(limit),
    staleTime: 60 * 60 * 1000, // 与后端列表缓存节奏接近，1 小时内不重复打接口
  });
}

/**
 * Search funds by name or code
 */
export function useSearchFunds(query: string, enabled = true, category?: string) {
  return useQuery({
    queryKey: fundKeys.search(query, category),
    queryFn: () => apiClient.searchFunds(query, 20, category),
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

export function useDCASimulate() {
  return useMutation({
    mutationFn: (request: DCASimulateRequest) => apiClient.simulateDCA(request),
  });
}

export function useRecommendFunds() {
  return useMutation({
    mutationFn: (request: FundRecommendRequest) => apiClient.recommendFunds(request),
  });
}
