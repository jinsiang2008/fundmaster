/**
 * Chat-related type definitions
 */

export type RiskLevel = 'conservative' | 'stable' | 'balanced' | 'aggressive' | 'radical';
export type InvestmentPurpose = 'savings' | 'retirement' | 'growth' | 'education' | 'other';
export type InvestmentHorizon = 'short' | 'medium' | 'long';

export interface UserProfile {
  risk_level: RiskLevel;
  purpose: InvestmentPurpose;
  horizon: InvestmentHorizon;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ChatSession {
  session_id: string;
  fund_code: string;
  fund_context: Record<string, unknown>;
  user_profile: UserProfile | null;
  messages: ChatMessage[];
  created_at: string;
}

export interface ChatRequest {
  session_id?: string;
  fund_code?: string;
  message: string;
  user_profile?: UserProfile;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  timestamp: string;
}

export interface CreateSessionRequest {
  fund_code: string;
}

export interface CreateSessionResponse {
  session_id: string;
  fund_code: string;
  fund_name: string;
  created_at: string;
}

// Risk level display mapping
export const RISK_LEVEL_MAP: Record<RiskLevel, string> = {
  conservative: '保守型',
  stable: '稳健型',
  balanced: '平衡型',
  aggressive: '进取型',
  radical: '激进型',
};

export const PURPOSE_MAP: Record<InvestmentPurpose, string> = {
  savings: '闲钱理财',
  retirement: '养老储备',
  growth: '资产增值',
  education: '教育金',
  other: '其他',
};

export const HORIZON_MAP: Record<InvestmentHorizon, string> = {
  short: '短期(<1年)',
  medium: '中期(1-3年)',
  long: '长期(>3年)',
};
