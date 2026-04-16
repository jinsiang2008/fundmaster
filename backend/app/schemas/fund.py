"""Fund-related Pydantic models."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class FundSearchResult(BaseModel):
    """Fund search result item."""

    code: str = Field(..., description="基金代码")
    name: str = Field(..., description="基金名称")
    type: str = Field(default="", description="基金类型")

    class Config:
        json_schema_extra = {"example": {"code": "110011", "name": "易方达中小盘混合", "type": "混合型-偏股"}}


class FundBasicInfo(BaseModel):
    """Fund basic information."""

    code: str = Field(..., description="基金代码")
    name: str = Field(..., description="基金名称")
    type: str = Field(default="", description="基金类型")
    company: str = Field(default="", description="基金公司")
    inception_date: date | None = Field(default=None, description="成立日期")
    manager: str = Field(default="", description="基金经理")
    manager_tenure: str = Field(default="", description="基金经理任职时长")
    aum: float | None = Field(default=None, description="基金规模(亿元)")
    nav: float | None = Field(default=None, description="最新单位净值")
    nav_date: date | None = Field(default=None, description="净值日期")
    acc_nav: float | None = Field(default=None, description="累计净值")

    # Fee structure（运作费率来自 F10；认/申购参考 pingzhongdata）
    management_fee: float | None = Field(default=None, description="管理费率(%)，年")
    custody_fee: float | None = Field(default=None, description="托管费率(%)，年")
    sales_service_fee: float | None = Field(default=None, description="销售服务费率(%)，年")
    purchase_fee: float | None = Field(default=None, description="申购费率参考(%)")
    max_subscription_fee_pct: float | None = Field(
        default=None,
        description="认购费率上限参考(%)（募集期）",
    )
    redemption_fee: float | None = Field(
        default=None,
        description="赎回费率（若无法分档则为示意，优先看 redemption_fee_detail）",
    )
    annual_operating_fee_pct: float | None = Field(
        default=None,
        description="年度运作费率合计约值(%)=管理+托管+销售服务",
    )
    redemption_fee_detail: str | None = Field(
        default=None,
        description="赎回费分档文字摘要",
    )
    lockup_note: str | None = Field(
        default=None,
        description="封闭期/持有期/定开等相关说明",
    )
    holding_cost_summary: str | None = Field(
        default=None,
        description="持有成本综合说明（面向用户）",
    )


class NAVDataPoint(BaseModel):
    """Single NAV data point."""

    date: date
    nav: float = Field(..., description="单位净值")
    acc_nav: float | None = Field(default=None, description="累计净值")
    change_pct: float | None = Field(default=None, description="日涨跌幅(%)")


class FundNAVHistory(BaseModel):
    """Fund NAV history data."""

    code: str
    name: str
    data: list[NAVDataPoint]


class FundHolding(BaseModel):
    """Fund holding item."""

    name: str = Field(..., description="持仓名称")
    code: str | None = Field(default=None, description="证券代码")
    ratio: float = Field(..., description="持仓占比(%)")
    shares: float | None = Field(default=None, description="持仓数量(万股)")
    market_value: float | None = Field(default=None, description="市值(万元)")


class FundHoldings(BaseModel):
    """Fund holdings data."""

    code: str
    name: str
    report_date: date | None = Field(default=None, description="报告期")
    stock_holdings: list[FundHolding] = Field(default_factory=list, description="股票持仓")
    bond_holdings: list[FundHolding] = Field(default_factory=list, description="债券持仓")
    industry_allocation: list[FundHolding] = Field(default_factory=list, description="行业分布")


class FundMetrics(BaseModel):
    """Fund performance metrics."""

    code: str
    name: str

    # Return metrics
    return_1m: float | None = Field(default=None, description="近1月收益率(%)")
    return_3m: float | None = Field(default=None, description="近3月收益率(%)")
    return_6m: float | None = Field(default=None, description="近6月收益率(%)")
    return_1y: float | None = Field(default=None, description="近1年收益率(%)")
    return_3y: float | None = Field(default=None, description="近3年收益率(%)")
    return_5y: float | None = Field(default=None, description="近5年收益率(%)")
    return_ytd: float | None = Field(default=None, description="今年以来收益率(%)")
    return_inception: float | None = Field(default=None, description="成立以来收益率(%)")

    # Risk metrics
    max_drawdown: float | None = Field(default=None, description="最大回撤(%)")
    volatility: float | None = Field(default=None, description="年化波动率(%)")
    sharpe_ratio: float | None = Field(default=None, description="夏普比率")

    # Annualized returns
    return_1y_annualized: float | None = Field(default=None, description="近1年年化收益(%)")
    return_3y_annualized: float | None = Field(default=None, description="近3年年化收益(%)")

    risk_labels: list[str] = Field(
        default_factory=list,
        description="基于类型与风险指标的标签（仅供参考）",
    )


class DCASimulateRequest(BaseModel):
    """定投模拟请求。"""

    fund_code: str = Field(..., min_length=6, max_length=10, description="基金代码")
    monthly_amount: float = Field(..., gt=0, le=1_000_000_000, description="每期投入金额（元）")
    start_date: date = Field(..., description="开始日期（含）")
    end_date: date = Field(..., description="结束日期（含）")


class DCAPeriodRow(BaseModel):
    invest_date: date
    nav: float
    amount: float
    shares: float


class DCASummary(BaseModel):
    total_invested: float
    total_shares: float
    periods_count: int
    latest_nav: float
    latest_nav_date: str
    market_value: float
    profit_loss: float
    profit_loss_pct: float


class DCASimulateResponse(BaseModel):
    fund_code: str
    fund_name: str
    periods: list[DCAPeriodRow]
    summary: DCASummary
    disclaimer: str = Field(
        default="模拟未计入申购/赎回费与分红再投，结果仅供参考，不构成投资建议。",
    )


class FundRecommendRequest(BaseModel):
    """规则化选基请求（与前端画像字段对齐）。"""

    risk_level: Literal["conservative", "stable", "balanced", "aggressive", "radical"] = Field(
        ...,
        description="风险偏好",
    )
    horizon: Literal["short", "medium", "long"] = Field(
        ...,
        description="投资期限：短/中/长",
    )
    liquidity: Literal["high", "medium", "low"] = Field(
        ...,
        description="流动性偏好：高/中/低",
    )
    themes: list[str] = Field(
        default_factory=list,
        description="主题 id 列表，如 broad_index、tech；空表示不限主题",
    )
    limit: int = Field(10, ge=3, le=30, description="返回数量")


class RecommendedFund(BaseModel):
    code: str
    name: str
    type: str = ""
    reasons: list[str] = Field(default_factory=list, description="匹配说明")


class FundRecommendResponse(BaseModel):
    funds: list[RecommendedFund]
    profile_summary: str
    disclaimer: str


class FundAnalysisReport(BaseModel):
    """AI-generated fund analysis report."""

    code: str
    name: str
    basic_info: FundBasicInfo
    metrics: FundMetrics
    analysis: str = Field(..., description="AI分析报告内容")
    recommendation: str = Field(default="观望", description="投资建议: 买入/观望/回避")
    generated_at: datetime = Field(default_factory=datetime.now)


class FundCompareRequest(BaseModel):
    """Request model for fund comparison."""

    fund_codes: list[str] = Field(..., min_length=2, max_length=5, description="基金代码列表")
    include_ai: bool = Field(
        default=True,
        description="是否调用 LLM 生成文字对比；为 False 时仅返回指标与雷达图，响应更快",
    )


class FundCompareResult(BaseModel):
    """Fund comparison result."""

    funds: list[FundMetrics]
    radar_data: dict = Field(default_factory=dict, description="雷达图数据")
    analysis: str = Field(default="", description="AI对比分析")
    recommendation: str = Field(default="", description="推荐基金")
