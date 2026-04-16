/**
 * API client for FundMaster backend
 */

import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type {
  FundSearchResult,
  FundBasicInfo,
  FundNAVHistory,
  FundHoldings,
  FundMetrics,
  FundAnalysisReport,
  RealtimeEstimate,
  FundCompareRequest,
  FundCompareResult,
  DCASimulateRequest,
  DCASimulateResponse,
  FundRecommendRequest,
  FundRecommendResponse,
} from '../types/fund';
import type {
  ChatRequest,
  ChatResponse,
  CreateSessionRequest,
  CreateSessionResponse,
  ChatMessage,
  UserProfile,
} from '../types/chat';

// In development, use relative URL (proxied by Vite)
// In production, use the environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/** 普通接口（与后端默认 30s 以内一致） */
const DEFAULT_TIMEOUT_MS = 30_000;
/**
 * 含 LLM 或多基金串行拉数的请求；需与后端 httpx 超时（如 120s）对齐，避免「后端仍在算、前端已超时」。
 */
const LONG_REQUEST_TIMEOUT_MS = 120_000;

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: DEFAULT_TIMEOUT_MS,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // ==================== Fund APIs ====================

  async getFeaturedFunds(limit = 8): Promise<FundSearchResult[]> {
    const { data } = await this.client.get<FundSearchResult[]>('/api/funds/featured', {
      params: { limit },
    });
    return data;
  }

  async searchFunds(
    query: string,
    limit = 20,
    category?: string
  ): Promise<FundSearchResult[]> {
    const { data } = await this.client.get<FundSearchResult[]>('/api/funds/search', {
      params: {
        q: query,
        limit,
        ...(category && category !== 'all' ? { category } : {}),
      },
    });
    return data;
  }

  async simulateDCA(body: DCASimulateRequest): Promise<DCASimulateResponse> {
    const { data } = await this.client.post<DCASimulateResponse>(
      '/api/funds/tools/dca-simulate',
      body
    );
    return data;
  }

  async recommendFunds(body: FundRecommendRequest): Promise<FundRecommendResponse> {
    const { data } = await this.client.post<FundRecommendResponse>('/api/funds/recommend', body);
    return data;
  }

  async getFundInfo(fundCode: string): Promise<FundBasicInfo> {
    const { data } = await this.client.get<FundBasicInfo>(`/api/funds/${fundCode}`);
    return data;
  }

  async getFundNAVHistory(fundCode: string, period = '1y'): Promise<FundNAVHistory> {
    const { data } = await this.client.get<FundNAVHistory>(`/api/funds/${fundCode}/nav`, {
      params: { period },
    });
    return data;
  }

  async getFundHoldings(fundCode: string): Promise<FundHoldings> {
    const { data } = await this.client.get<FundHoldings>(`/api/funds/${fundCode}/holdings`);
    return data;
  }

  async getFundMetrics(fundCode: string, period = '3y'): Promise<FundMetrics> {
    const { data } = await this.client.get<FundMetrics>(`/api/funds/${fundCode}/metrics`, {
      params: { period },
    });
    return data;
  }

  async getRealtimeEstimate(fundCode: string): Promise<RealtimeEstimate> {
    const { data } = await this.client.get<RealtimeEstimate>(`/api/funds/${fundCode}/realtime`);
    return data;
  }

  // ==================== Analysis APIs ====================

  async getFundAnalysis(fundCode: string): Promise<FundAnalysisReport> {
    const { data } = await this.client.get<FundAnalysisReport>(
      `/api/funds/${fundCode}/analysis`,
      { timeout: LONG_REQUEST_TIMEOUT_MS }
    );
    return data;
  }

  async getFundAnalysisStream(
    fundCode: string,
    onChunk: (chunk: string) => void
  ): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/funds/${fundCode}/analysis/stream`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data !== '[DONE]') {
            onChunk(data);
          }
        }
      }
    }
  }

  // ==================== Compare APIs ====================

  async compareFunds(request: FundCompareRequest): Promise<FundCompareResult> {
    const timeout =
      request.include_ai === false ? DEFAULT_TIMEOUT_MS : LONG_REQUEST_TIMEOUT_MS;
    const { data } = await this.client.post<FundCompareResult>(
      '/api/compare',
      request,
      { timeout }
    );
    return data;
  }

  // ==================== Chat APIs ====================

  async createChatSession(request: CreateSessionRequest): Promise<CreateSessionResponse> {
    const { data } = await this.client.post<CreateSessionResponse>(
      '/api/chat/sessions',
      request
    );
    return data;
  }

  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    const { data } = await this.client.post<ChatResponse>('/api/chat/messages', request);
    return data;
  }

  async sendChatMessageStream(
    request: ChatRequest,
    onChunk: (chunk: string) => void
  ): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/api/chat/messages/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      // 只能读一次 body：先 text，再 JSON.parse，避免 json() 失败后再 text() 报错
      const raw = await response.text();
      let detail = raw;
      try {
        const errBody = JSON.parse(raw) as { detail?: unknown };
        if (typeof errBody.detail === 'string') {
          detail = errBody.detail;
        } else if (Array.isArray(errBody.detail)) {
          detail = errBody.detail.map((x) => JSON.stringify(x)).join('; ');
        } else if (errBody.detail != null) {
          detail = JSON.stringify(errBody.detail);
        }
      } catch {
        /* 非 JSON 时用原始文本 */
      }
      throw new Error(
        detail ? `请求失败 (${response.status}): ${detail}` : `请求失败: HTTP ${response.status}`
      );
    }

    // Get session ID from header
    const sessionId = response.headers.get('X-Session-ID') || '';

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available');
    }

    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data.startsWith('[ERROR]')) {
            const msg = data.slice('[ERROR]'.length).trim();
            throw new Error(msg || '对话服务返回错误');
          }
          if (data !== '[DONE]') {
            onChunk(data);
          }
        }
      }
    }

    return sessionId;
  }

  async getChatMessages(sessionId: string): Promise<ChatMessage[]> {
    const { data } = await this.client.get<ChatMessage[]>(
      `/api/chat/sessions/${sessionId}/messages`
    );
    return data;
  }

  async updateUserProfile(sessionId: string, profile: UserProfile): Promise<void> {
    await this.client.put(`/api/chat/sessions/${sessionId}/profile`, profile);
  }

  async deleteChatSession(sessionId: string): Promise<void> {
    await this.client.delete(`/api/chat/sessions/${sessionId}`);
  }
}

export const apiClient = new ApiClient();
export default apiClient;
