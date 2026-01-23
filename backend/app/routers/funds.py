"""Fund data API endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.fund import (
    FundBasicInfo,
    FundSearchResult,
    FundNAVHistory,
    FundHoldings,
    FundMetrics,
)
from app.services.data_fetcher import get_data_fetcher
from app.services.metrics import get_metrics_calculator

router = APIRouter()


@router.get("/search", response_model=list[FundSearchResult])
async def search_funds(
    q: str = Query(..., min_length=1, description="搜索关键词（基金名称或代码）"),
    limit: int = Query(20, ge=1, le=50, description="返回数量限制"),
):
    """
    搜索基金。
    
    支持按基金名称或代码模糊搜索。
    """
    fetcher = get_data_fetcher()
    results = await fetcher.search_funds(q, limit)
    return results


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
    
    return metrics


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
