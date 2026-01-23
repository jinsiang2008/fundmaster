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
  management_fee: number | null;
  custody_fee: number | null;
  purchase_fee: number | null;
  redemption_fee: number | null;
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
