/**
 * Fund-related type definitions
 */

export interface FundSearchResult {
  code: string;
  name: string;
  type: string;
}

export interface FundBasicInfo {
  code: string;
  name: string;
  type: string;
  company: string;
  inception_date: string | null;
  manager: string;
  manager_tenure: string;
  aum: number | null;
  nav: number | null;
  nav_date: string | null;
  acc_nav: number | null;
  /** 年费率，从基金资产计提 */
  management_fee: number | null;
  custody_fee: number | null;
  sales_service_fee: number | null;
  /** 管理+托管+销售服务，年费率合计约值 */
  annual_operating_fee_pct: number | null;
  /** 申购费率参考 */
  purchase_fee: number | null;
  /** 认购费率上限参考（募集期） */
  max_subscription_fee_pct: number | null;
  /** 赎回分档中的最低费率（示意） */
  redemption_fee: number | null;
  /** 赎回分档文字 */
  redemption_fee_detail: string | null;
  /** 封闭/定开/持有期说明 */
  lockup_note: string | null;
  /** 持有成本综合说明 */
  holding_cost_summary: string | null;
}

export interface NAVDataPoint {
  date: string;
  nav: number;
  acc_nav: number | null;
  change_pct: number | null;
}

export interface FundNAVHistory {
  code: string;
  name: string;
  data: NAVDataPoint[];
}

export interface FundHolding {
  name: string;
  code: string | null;
  ratio: number;
  shares: number | null;
  market_value: number | null;
}

export interface FundHoldings {
  code: string;
  name: string;
  report_date: string | null;
  stock_holdings: FundHolding[];
  bond_holdings: FundHolding[];
  industry_allocation: FundHolding[];
}

export interface FundMetrics {
  code: string;
  name: string;
  return_1m: number | null;
  return_3m: number | null;
  return_6m: number | null;
  return_1y: number | null;
  return_3y: number | null;
  return_5y: number | null;
  return_ytd: number | null;
  return_inception: number | null;
  max_drawdown: number | null;
  volatility: number | null;
  sharpe_ratio: number | null;
  return_1y_annualized: number | null;
  return_3y_annualized: number | null;
  /** 后端生成的风险/风格标签 */
  risk_labels?: string[];
}

export interface DCASimulateRequest {
  fund_code: string;
  monthly_amount: number;
  start_date: string;
  end_date: string;
}

export interface DCAPeriodRow {
  invest_date: string;
  nav: number;
  amount: number;
  shares: number;
}

export interface DCASummary {
  total_invested: number;
  total_shares: number;
  periods_count: number;
  latest_nav: number;
  latest_nav_date: string;
  market_value: number;
  profit_loss: number;
  profit_loss_pct: number;
}

export interface DCASimulateResponse {
  fund_code: string;
  fund_name: string;
  periods: DCAPeriodRow[];
  summary: DCASummary;
  disclaimer: string;
}

/** 与后端 FundRecommendRequest 一致 */
export type RecommendRiskLevel = 'conservative' | 'stable' | 'balanced' | 'aggressive' | 'radical';
export type RecommendHorizon = 'short' | 'medium' | 'long';
export type RecommendLiquidity = 'high' | 'medium' | 'low';

export interface FundRecommendRequest {
  risk_level: RecommendRiskLevel;
  horizon: RecommendHorizon;
  liquidity: RecommendLiquidity;
  themes: string[];
  limit: number;
}

export interface RecommendedFund {
  code: string;
  name: string;
  type: string;
  reasons: string[];
}

export interface FundRecommendResponse {
  funds: RecommendedFund[];
  profile_summary: string;
  disclaimer: string;
}

export interface FundAnalysisReport {
  code: string;
  name: string;
  basic_info: FundBasicInfo;
  metrics: FundMetrics;
  analysis: string;
  recommendation: '买入' | '观望' | '回避';
  generated_at: string;
}

export interface RealtimeEstimate {
  code: string;
  name: string;
  nav: number;
  estimate_nav: number;
  estimate_change: number;
  update_time: string;
  nav_date: string;
}

export interface FundCompareRequest {
  fund_codes: string[];
  /** 默认 true；设为 false 仅拉取指标与雷达图，不调用 LLM，速度更快 */
  include_ai?: boolean;
}

export interface RadarSeriesItem {
  name: string;
  code: string;
  values: number[];
}

export interface FundCompareResult {
  funds: FundMetrics[];
  radar_data: {
    dimensions: string[];
    series: RadarSeriesItem[];
  };
  analysis: string;
  recommendation: string;
}
