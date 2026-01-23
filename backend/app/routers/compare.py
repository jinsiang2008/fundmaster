"""Fund comparison API endpoints."""

from fastapi import APIRouter, HTTPException

from app.schemas.fund import FundCompareRequest, FundCompareResult, FundMetrics
from app.services.data_fetcher import get_data_fetcher
from app.services.metrics import get_metrics_calculator
from app.services.llm_service import get_llm_service
from app.services.llm_prompts import FUND_COMPARE_PROMPT, format_fund_for_compare

router = APIRouter()


@router.post("/compare", response_model=FundCompareResult)
async def compare_funds(request: FundCompareRequest):
    """
    多基金对比分析。
    
    支持2-5只基金同时对比，返回对比数据和AI分析。
    """
    fetcher = get_data_fetcher()
    calculator = get_metrics_calculator()
    llm = get_llm_service()
    
    funds_data = []
    metrics_list = []
    
    # Fetch data for all funds
    for code in request.fund_codes:
        info = await fetcher.get_fund_info(code)
        if not info:
            raise HTTPException(status_code=404, detail=f"基金不存在: {code}")
        
        history = await fetcher.get_nav_history(code, "3y")
        metrics = calculator.calculate_metrics(history, info.name) if history else FundMetrics(
            code=code, name=info.name
        )
        
        metrics_list.append(metrics)
        funds_data.append({
            "code": code,
            "name": info.name,
            "type": info.type,
            "aum": info.aum,
            "manager": info.manager,
            "metrics": metrics.model_dump(),
        })
    
    # Build radar chart data
    radar_data = _build_radar_data(metrics_list)
    
    # Generate AI comparison if LLM available
    analysis = ""
    recommendation = ""
    
    if llm:
        # Format funds for prompt
        funds_text = "\n\n".join([
            format_fund_for_compare(f, i + 1)
            for i, f in enumerate(funds_data)
        ])
        
        prompt = FUND_COMPARE_PROMPT.format(
            num_funds=len(funds_data),
            funds_data=funds_text,
        )
        
        response = await llm.generate(
            task_type="compare_funds",
            messages=[
                {"role": "system", "content": "你是专业的基金投资顾问，请提供客观的对比分析。"},
                {"role": "user", "content": prompt},
            ],
        )
        
        analysis = response.choices[0].message.content
        
        # Try to extract recommendation
        for fund in funds_data:
            if fund["name"] in analysis and "推荐" in analysis:
                recommendation = fund["code"]
                break
    
    return FundCompareResult(
        funds=metrics_list,
        radar_data=radar_data,
        analysis=analysis,
        recommendation=recommendation,
    )


def _build_radar_data(metrics_list: list[FundMetrics]) -> dict:
    """
    Build radar chart data for fund comparison.
    
    Normalizes metrics to 0-100 scale for visualization.
    """
    if not metrics_list:
        return {}
    
    # Define radar dimensions
    dimensions = [
        {"name": "收益能力", "key": "return_score"},
        {"name": "稳定性", "key": "stability_score"},
        {"name": "风险控制", "key": "risk_score"},
        {"name": "夏普比率", "key": "sharpe_score"},
        {"name": "性价比", "key": "value_score"},
    ]
    
    radar_series = []
    
    for metrics in metrics_list:
        # Calculate scores (0-100)
        return_score = _normalize_return(metrics.return_1y)
        stability_score = _normalize_stability(metrics.volatility)
        risk_score = _normalize_drawdown(metrics.max_drawdown)
        sharpe_score = _normalize_sharpe(metrics.sharpe_ratio)
        value_score = (return_score + risk_score) / 2  # Simple value metric
        
        radar_series.append({
            "name": metrics.name,
            "code": metrics.code,
            "values": [
                return_score,
                stability_score,
                risk_score,
                sharpe_score,
                value_score,
            ],
        })
    
    return {
        "dimensions": [d["name"] for d in dimensions],
        "series": radar_series,
    }


def _normalize_return(value: float | None) -> float:
    """Normalize return to 0-100 score."""
    if value is None:
        return 50
    # Assume -30% to +50% range
    normalized = (value + 30) / 80 * 100
    return max(0, min(100, normalized))


def _normalize_stability(volatility: float | None) -> float:
    """Normalize volatility to stability score (lower is better)."""
    if volatility is None:
        return 50
    # Assume 0% to 40% volatility range
    stability = (40 - volatility) / 40 * 100
    return max(0, min(100, stability))


def _normalize_drawdown(drawdown: float | None) -> float:
    """Normalize max drawdown to risk score (lower absolute is better)."""
    if drawdown is None:
        return 50
    # Drawdown is negative, so we invert
    # Assume -50% to 0% range
    score = (50 + drawdown) / 50 * 100
    return max(0, min(100, score))


def _normalize_sharpe(sharpe: float | None) -> float:
    """Normalize Sharpe ratio to 0-100 score."""
    if sharpe is None:
        return 50
    # Assume -1 to 3 range
    normalized = (sharpe + 1) / 4 * 100
    return max(0, min(100, normalized))
