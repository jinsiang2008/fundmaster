"""AI analysis API endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.fund import FundAnalysisReport
from app.services.data_fetcher import get_data_fetcher
from app.services.llm_prompts import FUND_ANALYSIS_PROMPT, format_holdings_for_prompt
from app.services.llm_service import get_llm_service
from app.services.metrics import get_metrics_calculator
from app.services.risk_labels import enrich_metrics_with_risk_labels

router = APIRouter()


@router.get("/{fund_code}/analysis", response_model=FundAnalysisReport)
async def get_fund_analysis(fund_code: str):
    """
    获取基金AI分析报告。

    使用 deepseek-reasoner 进行深度分析，返回专业分析报告和投资建议。
    """
    llm = get_llm_service()
    if not llm:
        raise HTTPException(status_code=503, detail="AI服务不可用，请检查API Key配置")

    fetcher = get_data_fetcher()

    # Get fund data
    info = await fetcher.get_fund_info(fund_code)
    if not info:
        raise HTTPException(status_code=404, detail=f"基金不存在: {fund_code}")

    # Get NAV history and calculate metrics
    history = await fetcher.get_nav_history(fund_code, "3y")
    calculator = get_metrics_calculator()
    metrics = calculator.calculate_metrics(history, info.name) if history else None
    if metrics:
        metrics = enrich_metrics_with_risk_labels(metrics, info.type or "")

    # Get holdings
    holdings = await fetcher.get_holdings(fund_code)
    holdings_text = ""
    if holdings and holdings.stock_holdings:
        holdings_text = format_holdings_for_prompt(
            [{"name": h.name, "ratio": h.ratio} for h in holdings.stock_holdings]
        )

    # Build prompt
    prompt = FUND_ANALYSIS_PROMPT.format(
        name=info.name,
        code=info.code,
        fund_type=info.type or "未知",
        inception_date=info.inception_date or "未知",
        aum=info.aum or "未知",
        manager=info.manager or "未知",
        return_1m=metrics.return_1m if metrics else "N/A",
        return_3m=metrics.return_3m if metrics else "N/A",
        return_6m=metrics.return_6m if metrics else "N/A",
        return_1y=metrics.return_1y if metrics else "N/A",
        return_3y=metrics.return_3y if metrics else "N/A",
        return_ytd=metrics.return_ytd if metrics else "N/A",
        return_inception=metrics.return_inception if metrics else "N/A",
        max_drawdown=metrics.max_drawdown if metrics else "N/A",
        volatility=metrics.volatility if metrics else "N/A",
        sharpe_ratio=metrics.sharpe_ratio if metrics else "N/A",
        management_fee=info.management_fee or "N/A",
        custody_fee=info.custody_fee or "N/A",
        top_holdings=holdings_text or "暂无数据",
    )

    # Generate analysis using reasoning model
    response = await llm.generate(
        task_type="deep_analysis",
        messages=[
            {"role": "system", "content": "你是一位专业的基金分析师，请提供详细、客观的分析报告。"},
            {"role": "user", "content": prompt},
        ],
    )

    analysis_text = response.choices[0].message.content

    # Extract recommendation from analysis
    recommendation = "观望"
    if "【买入】" in analysis_text or "买入" in analysis_text[:100]:
        recommendation = "买入"
    elif "【回避】" in analysis_text or "回避" in analysis_text[:100]:
        recommendation = "回避"

    return FundAnalysisReport(
        code=info.code,
        name=info.name,
        basic_info=info,
        metrics=metrics,
        analysis=analysis_text,
        recommendation=recommendation,
        generated_at=datetime.now(),
    )


@router.get("/{fund_code}/analysis/stream")
async def get_fund_analysis_stream(fund_code: str):
    """
    获取基金AI分析报告（流式输出）。

    返回 Server-Sent Events 流，支持打字机效果展示。
    """
    llm = get_llm_service()
    if not llm:
        raise HTTPException(status_code=503, detail="AI服务不可用，请检查API Key配置")

    fetcher = get_data_fetcher()

    # Get fund data
    info = await fetcher.get_fund_info(fund_code)
    if not info:
        raise HTTPException(status_code=404, detail=f"基金不存在: {fund_code}")

    # Get NAV history and calculate metrics
    history = await fetcher.get_nav_history(fund_code, "3y")
    calculator = get_metrics_calculator()
    metrics = calculator.calculate_metrics(history, info.name) if history else None
    if metrics:
        metrics = enrich_metrics_with_risk_labels(metrics, info.type or "")

    # Get holdings
    holdings = await fetcher.get_holdings(fund_code)
    holdings_text = ""
    if holdings and holdings.stock_holdings:
        holdings_text = format_holdings_for_prompt(
            [{"name": h.name, "ratio": h.ratio} for h in holdings.stock_holdings]
        )

    # Build prompt
    prompt = FUND_ANALYSIS_PROMPT.format(
        name=info.name,
        code=info.code,
        fund_type=info.type or "未知",
        inception_date=info.inception_date or "未知",
        aum=info.aum or "未知",
        manager=info.manager or "未知",
        return_1m=metrics.return_1m if metrics else "N/A",
        return_3m=metrics.return_3m if metrics else "N/A",
        return_6m=metrics.return_6m if metrics else "N/A",
        return_1y=metrics.return_1y if metrics else "N/A",
        return_3y=metrics.return_3y if metrics else "N/A",
        return_ytd=metrics.return_ytd if metrics else "N/A",
        return_inception=metrics.return_inception if metrics else "N/A",
        max_drawdown=metrics.max_drawdown if metrics else "N/A",
        volatility=metrics.volatility if metrics else "N/A",
        sharpe_ratio=metrics.sharpe_ratio if metrics else "N/A",
        management_fee=info.management_fee or "N/A",
        custody_fee=info.custody_fee or "N/A",
        top_holdings=holdings_text or "暂无数据",
    )

    async def generate_stream():
        """Generate SSE stream."""
        async for chunk in llm.generate_stream(
            task_type="deep_analysis",
            messages=[
                {"role": "system", "content": "你是一位专业的基金分析师，请提供详细、客观的分析报告。"},
                {"role": "user", "content": prompt},
            ],
        ):
            # SSE format
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
