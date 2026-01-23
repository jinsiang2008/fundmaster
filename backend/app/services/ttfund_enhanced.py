"""Enhanced TTFund fetcher with full data extraction."""

from datetime import datetime, date
from typing import Optional
import pandas as pd

from app.schemas.fund import (
    FundBasicInfo,
    FundNAVHistory,
    NAVDataPoint,
    FundHoldings,
    FundHolding,
)
from app.services.ttfund_fetcher import get_ttfund_fetcher


async def get_fund_info_from_ttfund(fund_code: str) -> Optional[FundBasicInfo]:
    """Get fund basic info from TTFund detail endpoint."""
    fetcher = get_ttfund_fetcher()
    detail = await fetcher.get_fund_detail(fund_code)
    
    if not detail:
        return None
    
    # Parse inception date
    inception_date = None
    if detail.get("inception_date"):
        try:
            inception_date = datetime.strptime(detail["inception_date"], "%Y-%m-%d").date()
        except:
            pass
    
    return FundBasicInfo(
        code=fund_code,
        name=detail.get("name", ""),
        type=detail.get("type", ""),
        company=detail.get("company", ""),
        manager=detail.get("manager", ""),
        aum=detail.get("aum"),
        inception_date=inception_date,
    )


async def get_nav_history_from_ttfund(
    fund_code: str,
    period: str = "1y",
) -> Optional[FundNAVHistory]:
    """Extract NAV history from TTFund detail endpoint."""
    fetcher = get_ttfund_fetcher()
    detail = await fetcher.get_fund_detail(fund_code)
    
    if not detail or not detail.get("nav_history"):
        print(f"No NAV history found in TTFund for {fund_code}")
        return None
    
    nav_data = detail["nav_history"]
    acc_nav_data = detail.get("acc_nav_history", [])
    
    # Convert timestamps to dates and build NAV points
    data_points = []
    
    # Create a dict for accumulated NAV lookup
    acc_nav_dict = {}
    for item in acc_nav_data:
        try:
            timestamp = item.get("x")
            acc_nav = item.get("y")
            if timestamp and acc_nav:
                acc_nav_dict[timestamp] = float(acc_nav)
        except:
            continue
    
    # Filter by period
    end_time = datetime.now()
    period_days = {
        "1m": 30,
        "3m": 90,
        "6m": 180,
        "1y": 365,
        "3y": 365 * 3,
        "5y": 365 * 5,
        "max": 365 * 50,
    }
    days = period_days.get(period, 365)
    start_time = end_time - pd.Timedelta(days=days)
    start_timestamp = int(start_time.timestamp() * 1000)
    
    for item in nav_data:
        try:
            timestamp = item.get("x")
            nav = item.get("y")
            
            if not timestamp or not nav:
                continue
            
            # Filter by period
            if timestamp < start_timestamp:
                continue
            
            # Convert timestamp to date
            dt = datetime.fromtimestamp(timestamp / 1000)
            nav_date = dt.date()
            
            # Get accumulated NAV
            acc_nav = acc_nav_dict.get(timestamp)
            
            data_points.append(NAVDataPoint(
                date=nav_date,
                nav=float(nav),
                acc_nav=float(acc_nav) if acc_nav else None,
            ))
        except Exception as e:
            print(f"Error parsing NAV point: {e}")
            continue
    
    if not data_points:
        return None
    
    return FundNAVHistory(
        code=fund_code,
        name=detail.get("name", fund_code),
        data=data_points,
    )


async def get_holdings_from_ttfund(fund_code: str) -> Optional[FundHoldings]:
    """Extract holdings from TTFund detail endpoint."""
    fetcher = get_ttfund_fetcher()
    detail = await fetcher.get_fund_detail(fund_code)
    
    if not detail or not detail.get("stock_holdings"):
        return None
    
    holdings_data = detail["stock_holdings"]
    stock_holdings = []
    
    for item in holdings_data:
        try:
            # stockCodesNew format: [code, name, ratio, ...]
            if isinstance(item, list) and len(item) >= 3:
                stock_holdings.append(FundHolding(
                    code=str(item[0]),
                    name=str(item[1]),
                    ratio=float(item[2]),
                ))
        except:
            continue
    
    return FundHoldings(
        code=fund_code,
        name=detail.get("name", fund_code),
        stock_holdings=stock_holdings[:10],  # Top 10
    )
