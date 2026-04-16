"""Fund data API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.fund import (
    DCAPeriodRow,
    DCASimulateRequest,
    DCASimulateResponse,
    DCASummary,
    FundBasicInfo,
    FundHoldings,
    FundMetrics,
    FundNAVHistory,
    FundRecommendRequest,
    FundRecommendResponse,
    FundSearchResult,
)
from app.services.data_fetcher import get_data_fetcher
from app.services.dca_simulator import simulate_monthly_dca
from app.services.metrics import get_metrics_calculator
from app.services.risk_labels import enrich_metrics_with_risk_labels

router = APIRouter()


def _filter_by_category(results: list[FundSearchResult], category: str | None) -> list[FundSearchResult]:
    if not category or category.strip().lower() in ("", "all"):
        return results
    cat = category.strip().lower()
    keywords_map: dict[str, tuple[str, ...]] = {
        "stock": ("股票", "偏股"),
        "bond": ("债券", "转债", "纯债"),
        "mixed": ("混合",),
        "index": ("指数", "ETF", "联接", "etf"),
        "money": ("货币",),
        "qdii": ("QDII", "qdii", "境外"),
    }
    keys = keywords_map.get(cat)
    if not keys:
        return results
    out: list[FundSearchResult] = []
    for r in results:
        t = r.type or ""
        if any(k in t for k in keys):
            out.append(r)
    return out


@router.get("/search", response_model=list[FundSearchResult])
async def search_funds(
    q: str = Query(..., min_length=1, description="搜索关键词（基金名称或代码）"),
    limit: int = Query(20, ge=1, le=50, description="返回数量限制"),
    category: str | None = Query(
        None,
        description="类型筛选: all/stock/bond/mixed/index/money/qdii（在搜索结果上过滤）",
    ),
):
    """
    搜索基金。

    支持按基金名称或代码模糊搜索；可选按基金类型关键词进一步筛选。
    """
    fetcher = get_data_fetcher()
    fetch_limit = min(80, limit * 4) if category and category.strip().lower() not in ("", "all") else limit
    results = await fetcher.search_funds(q, fetch_limit)
    results = _filter_by_category(results, category)
    return results[:limit]


@router.get("/featured", response_model=list[FundSearchResult])
async def get_featured_funds(
    limit: int = Query(8, ge=3, le=20, description="返回数量"),
):
    """
    首页「今日推荐」：从东方财富全量基金代码表中按日期做确定性抽样，每日轮换。

    非官方销量/涨幅排名；仅用于丰富入口。接口失败时返回内置兜底列表。
    """
    fetcher = get_data_fetcher()
    return await fetcher.get_featured_funds(limit)


@router.post("/recommend", response_model=FundRecommendResponse)
async def recommend_funds(body: FundRecommendRequest):
    """
    智能选基（规则引擎）：按风险偏好、投资期限、流动性与可选主题从全市场基金中筛选，
    并给出简要匹配理由。非业绩排名，不构成投资建议。
    """
    fetcher = get_data_fetcher()
    return await fetcher.recommend_funds(body)


@router.post("/tools/dca-simulate", response_model=DCASimulateResponse)
async def simulate_dca(req: DCASimulateRequest):
    """
    基于历史净值按月定投模拟（每月在当月中取第一个可用净值日扣款）。
    """
    fetcher = get_data_fetcher()
    info = await fetcher.get_fund_info(req.fund_code)
    if not info:
        raise HTTPException(status_code=404, detail=f"基金不存在: {req.fund_code}")

    history = await fetcher.get_nav_history(req.fund_code, "max")
    if not history or not history.data:
        raise HTTPException(status_code=404, detail=f"未找到净值数据: {req.fund_code}")

    try:
        periods, summary = simulate_monthly_dca(
            history,
            req.monthly_amount,
            req.start_date,
            req.end_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return DCASimulateResponse(
        fund_code=req.fund_code,
        fund_name=info.name,
        periods=[
            DCAPeriodRow(
                invest_date=p.invest_date,
                nav=round(p.nav, 4),
                amount=round(p.amount, 2),
                shares=round(p.shares, 6),
            )
            for p in periods
        ],
        summary=DCASummary(**summary),
    )


@router.get("/{fund_code}", response_model=FundBasicInfo)
async def get_fund_info(fund_code: str):
    """
    获取基金基本信息。

    返回基金名称、类型、规模、基金经理、费率等信息。
    """
    fetcher = get_data_fetcher()
    info = await fetcher.get_fund_info(fund_code)

    if not info:
        raise HTTPException(status_code=404, detail=f"基金不存在: {fund_code}")

    return info


@router.get("/{fund_code}/nav", response_model=FundNAVHistory)
async def get_fund_nav_history(
    fund_code: str,
    period: str = Query("1y", regex="^(1m|3m|6m|1y|3y|5y|max)$", description="时间周期"),
):
    """
    获取基金历史净值数据。

    - period: 1m(1月), 3m(3月), 6m(6月), 1y(1年), 3y(3年), 5y(5年), max(全部)
    """
    fetcher = get_data_fetcher()
    history = await fetcher.get_nav_history(fund_code, period)

    if not history:
        raise HTTPException(status_code=404, detail=f"未找到净值数据: {fund_code}")

    return history


@router.get("/{fund_code}/holdings", response_model=FundHoldings)
async def get_fund_holdings(fund_code: str):
    """
    获取基金持仓数据。

    返回前十大股票/债券持仓。
    """
    fetcher = get_data_fetcher()
    holdings = await fetcher.get_holdings(fund_code)

    if not holdings:
        raise HTTPException(status_code=404, detail=f"未找到持仓数据: {fund_code}")

    return holdings


@router.get("/{fund_code}/metrics", response_model=FundMetrics)
async def get_fund_metrics(
    fund_code: str,
    period: str = Query("3y", regex="^(1y|3y|5y|max)$", description="计算周期"),
):
    """
    获取基金业绩指标。

    返回收益率、最大回撤、夏普比率等指标。
    """
    fetcher = get_data_fetcher()

    # Get NAV history
    history = await fetcher.get_nav_history(fund_code, period)
    if not history:
        raise HTTPException(status_code=404, detail=f"未找到数据: {fund_code}")

    # Get fund name
    info = await fetcher.get_fund_info(fund_code)
    fund_name = info.name if info else fund_code

    # Calculate metrics
    calculator = get_metrics_calculator()
    metrics = calculator.calculate_metrics(history, fund_name)
    fund_type = info.type if info else ""
    return enrich_metrics_with_risk_labels(metrics, fund_type)


@router.get("/{fund_code}/realtime")
async def get_realtime_estimate(fund_code: str):
    """
    获取基金实时估值（仅交易时段）。

    返回当前估算净值和涨跌幅。
    """
    fetcher = get_data_fetcher()
    estimate = await fetcher.get_realtime_estimate(fund_code)

    if not estimate:
        raise HTTPException(status_code=404, detail=f"未找到实时估值: {fund_code}")

    return estimate
