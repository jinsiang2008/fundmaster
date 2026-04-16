"""Monthly DCA (定投) simulation using historical NAV series."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime

from app.schemas.fund import FundNAVHistory, NAVDataPoint


@dataclass
class DCAPeriod:
    invest_date: date
    nav: float
    amount: float
    shares: float


def _parse_nav_date(p: NAVDataPoint) -> date | None:
    if isinstance(p.date, date):
        return p.date
    if isinstance(p.date, datetime):
        return p.date.date()
    try:
        return datetime.strptime(str(p.date)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _nav_series_sorted(history: FundNAVHistory) -> list[tuple[date, float]]:
    rows: list[tuple[date, float]] = []
    for p in history.data:
        d = _parse_nav_date(p)
        if d is None or p.nav is None or p.nav <= 0:
            continue
        rows.append((d, float(p.nav)))
    rows.sort(key=lambda x: x[0])
    return rows


def _month_end(y: int, m: int) -> date:
    last = calendar.monthrange(y, m)[1]
    return date(y, m, last)


def _first_nav_in_range(
    series: list[tuple[date, float]],
    low: date,
    high: date,
) -> tuple[date, float] | None:
    """First NAV point with date in [low, high] inclusive."""
    for d, nav in series:
        if d < low:
            continue
        if d > high:
            break
        return d, nav
    return None


def simulate_monthly_dca(
    history: FundNAVHistory,
    monthly_amount: float,
    start: date,
    end: date,
) -> tuple[list[DCAPeriod], dict]:
    """
    Fixed monthly investment: each calendar month, buy on the first available NAV
    date within that month (and within [start, end], and on/after data start).

    Does not model fees or dividend reinvestment.
    """
    if monthly_amount <= 0:
        raise ValueError("每期投入金额必须大于 0")
    if start > end:
        raise ValueError("开始日期不能晚于结束日期")

    series = _nav_series_sorted(history)
    if len(series) < 2:
        raise ValueError("净值数据不足，无法模拟")

    data_start = series[0][0]
    data_end = series[-1][0]
    if end < data_start or start > data_end:
        raise ValueError("所选区间与基金净值日期无交集，请缩短时间范围")

    periods: list[DCAPeriod] = []
    total_invested = 0.0
    total_shares = 0.0

    y, m = start.year, start.month
    end_ym = (end.year, end.month)

    while (y, m) <= end_ym:
        ms = date(y, m, 1)
        me = _month_end(y, m)
        low = max(ms, start, data_start)
        hi = min(me, end)
        if low <= hi:
            hit = _first_nav_in_range(series, low, hi)
            if hit:
                d, nav = hit
                shares = monthly_amount / nav
                periods.append(DCAPeriod(invest_date=d, nav=nav, amount=monthly_amount, shares=shares))
                total_invested += monthly_amount
                total_shares += shares

        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1

    if not periods:
        raise ValueError("在选定区间内没有可执行的定投期")

    last_nav = series[-1][1]
    last_nav_date = series[-1][0]
    market_value = total_shares * last_nav
    profit = market_value - total_invested
    profit_pct = (profit / total_invested * 100) if total_invested > 0 else 0.0

    summary = {
        "total_invested": round(total_invested, 2),
        "total_shares": round(total_shares, 6),
        "periods_count": len(periods),
        "latest_nav": last_nav,
        "latest_nav_date": last_nav_date.isoformat(),
        "market_value": round(market_value, 2),
        "profit_loss": round(profit, 2),
        "profit_loss_pct": round(profit_pct, 2),
    }
    return periods, summary
