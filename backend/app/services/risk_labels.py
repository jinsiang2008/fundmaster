"""Derive human-readable risk / style labels from metrics and fund type."""

from __future__ import annotations

from app.schemas.fund import FundMetrics


def build_risk_labels(
    metrics: FundMetrics,
    fund_type: str = "",
) -> list[str]:
    """
    Build 3–6 short labels for UI chips. Rules are heuristic, not investment advice.
    """
    labels: list[str] = []
    ft = (fund_type or "").strip()

    if ft:
        if "货币" in ft:
            labels.append("货币理财")
        elif "债券" in ft or "纯债" in ft:
            labels.append("债类为主")
        elif "指数" in ft or "ETF" in ft or "联接" in ft:
            labels.append("被动指数")
        elif "QDII" in ft or "qdii" in ft.lower():
            labels.append("QDII/境外")
        elif "混合" in ft:
            labels.append("混合配置")
        elif "股票" in ft:
            labels.append("股票仓位为主")

    vol = metrics.volatility
    if vol is not None:
        if vol >= 28:
            labels.append("波动较高")
        elif vol >= 18:
            labels.append("波动中等")
        else:
            labels.append("波动相对较低")

    mdd = metrics.max_drawdown
    if mdd is not None:
        if mdd <= -40:
            labels.append("历史回撤大")
        elif mdd <= -25:
            labels.append("回撤中等")
        else:
            labels.append("回撤相对温和")

    sharpe = metrics.sharpe_ratio
    if sharpe is not None:
        if sharpe >= 1.0:
            labels.append("夏普较优")
        elif sharpe < 0.3:
            labels.append("风险收益比一般")

    # Dedupe while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for x in labels:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out[:6]


def enrich_metrics_with_risk_labels(metrics: FundMetrics, fund_type: str = "") -> FundMetrics:
    """Return a copy of metrics with ``risk_labels`` filled."""
    return metrics.model_copy(update={"risk_labels": build_risk_labels(metrics, fund_type)})
