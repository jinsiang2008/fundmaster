"""Fund-related Pydantic models."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class FundSearchResult(BaseModel):
    """Fund search result item."""
    code: str = Field(..., description="基金代码")
    name: str = Field(..., description="基金名称")
    type: str = Field(default="", description="基金类型")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "110011",
                "name": "易方达中小盘混合",
                "type": "混合型-偏股"
            }
        }


class FundBasicInfo(BaseModel):
    """Fund basic information."""
    code: str = Field(..., description="基金代码")
    name: str = Field(..., description="基金名称")
    type: str = Field(default="", description="基金类型")
    company: str = Field(default="", description="基金公司")
    inception_date: Optional[date] = Field(default=None, description="成立日期")
    manager: str = Field(default="", description="基金经理")
    manager_tenure: str = Field(default="", description="基金经理任职时长")
    aum: Optional[float] = Field(default=None, description="基金规模(亿元)")
    nav: Optional[float] = Field(default=None, description="最新单位净值")
    nav_date: Optional[date] = Field(default=None, description="净值日期")
    acc_nav: Optional[float] = Field(default=None, description="累计净值")
    
    # Fee structure
    management_fee: Optional[float] = Field(default=None, description="管理费率(%)")
    custody_fee: Optional[float] = Field(default=None, description="托管费率(%)")
    purchase_fee: Optional[float] = Field(default=None, description="申购费率(%)")
    redemption_fee: Optional[float] = Field(default=None, description="赎回费率(%)")


class NAVDataPoint(BaseModel):
    """Single NAV data point."""
    date: date
    nav: float = Field(..., description="单位净值")
    acc_nav: Optional[float] = Field(default=None, description="累计净值")
    change_pct: Optional[float] = Field(default=None, description="日涨跌幅(%)")


class FundNAVHistory(BaseModel):
    """Fund NAV history data."""
    code: str
    name: str
    data: list[NAVDataPoint]


class FundHolding(BaseModel):
    """Fund holding item."""
    name: str = Field(..., description="持仓名称")
    code: Optional[str] = Field(default=None, description="证券代码")
    ratio: float = Field(..., description="持仓占比(%)")
    shares: Optional[float] = Field(default=None, description="持仓数量(万股)")
    market_value: Optional[float] = Field(default=None, description="市值(万元)")


class FundHoldings(BaseModel):
    """Fund holdings data."""
    code: str
    name: str
    report_date: Optional[date] = Field(default=None, description="报告期")
    stock_holdings: list[FundHolding] = Field(default_factory=list, description="股票持仓")
    bond_holdings: list[FundHolding] = Field(default_factory=list, description="债券持仓")
    industry_allocation: list[FundHolding] = Field(default_factory=list, description="行业分布")


class FundMetrics(BaseModel):
    """Fund performance metrics."""
    code: str
    name: str
    
    # Return metrics
    return_1m: Optional[float] = Field(default=None, description="近1月收益率(%)")
    return_3m: Optional[float] = Field(default=None, description="近3月收益率(%)")
    return_6m: Optional[float] = Field(default=None, description="近6月收益率(%)")
    return_1y: Optional[float] = Field(default=None, description="近1年收益率(%)")
    return_3y: Optional[float] = Field(default=None, description="近3年收益率(%)")
    return_5y: Optional[float] = Field(default=None, description="近5年收益率(%)")
    return_ytd: Optional[float] = Field(default=None, description="今年以来收益率(%)")
    return_inception: Optional[float] = Field(default=None, description="成立以来收益率(%)")
    
    # Risk metrics
    max_drawdown: Optional[float] = Field(default=None, description="最大回撤(%)")
    volatility: Optional[float] = Field(default=None, description="年化波动率(%)")
    sharpe_ratio: Optional[float] = Field(default=None, description="夏普比率")
    
    # Annualized returns
    return_1y_annualized: Optional[float] = Field(default=None, description="近1年年化收益(%)")
    return_3y_annualized: Optional[float] = Field(default=None, description="近3年年化收益(%)")


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


class FundCompareResult(BaseModel):
    """Fund comparison result."""
    funds: list[FundMetrics]
    radar_data: dict = Field(default_factory=dict, description="雷达图数据")
    analysis: str = Field(default="", description="AI对比分析")
    recommendation: str = Field(default="", description="推荐基金")
