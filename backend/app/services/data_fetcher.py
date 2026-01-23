"""Unified data fetcher combining multiple data sources."""

from typing import Optional

from app.schemas.fund import (
    FundBasicInfo,
    FundSearchResult,
    FundNAVHistory,
    FundHoldings,
)
from app.services.akshare_fetcher import get_akshare_fetcher, AKShareFetcher
from app.services.ttfund_fetcher import get_ttfund_fetcher, TTFundFetcher
from app.services.ttfund_enhanced import (
    get_fund_info_from_ttfund,
    get_nav_history_from_ttfund,
    get_holdings_from_ttfund,
)


class DataFetcher:
    """
    Unified data fetcher with fallback strategy.
    
    Primary: AKShare (structured, stable)
    Fallback: Tiantian Fund (real-time estimates)
    """
    
    def __init__(self):
        self._akshare: AKShareFetcher = get_akshare_fetcher()
        self._ttfund: TTFundFetcher = get_ttfund_fetcher()
    
    async def search_funds(self, query: str, limit: int = 20) -> list[FundSearchResult]:
        """
        Search funds by name or code with failover.
        
        Strategy:
        1. Use TTFund first (stable, no crashes)
        2. Fallback to AKShare if TTFund fails
        """
        # Try TTFund first (避免 AKShare 的 libmini_racer 崩溃问题)
        try:
            ttfund_results = await self._ttfund.search_funds(query, limit)
            if ttfund_results:
                print(f"✓ TTFund search successful: {len(ttfund_results)} results")
                return [
                    FundSearchResult(
                        code=r["code"],
                        name=r["name"],
                        type=r.get("type", ""),
                    )
                    for r in ttfund_results
                ]
            print("TTFund returned empty results, trying AKShare fallback")
        except Exception as e:
            print(f"TTFund search failed: {e}, trying AKShare fallback")
        
        # Fallback: Try AKShare (may crash with libmini_racer)
        try:
            results = await self._akshare.search_funds(query, limit)
            if results:
                print(f"✓ AKShare fallback successful: {len(results)} results")
                return results
            print("AKShare also returned empty results")
        except Exception as e:
            print(f"✗ AKShare fallback also failed: {e}")
        
        print("No results from either source")
        return []
    
    async def get_fund_info(self, fund_code: str) -> Optional[FundBasicInfo]:
        """
        Get fund basic information with failover.
        
        Primary: TTFund (stable)
        Fallback: AKShare (currently disabled due to crashes)
        """
        # Try TTFund first (primary source now)
        try:
            info = await get_fund_info_from_ttfund(fund_code)
            if info:
                print(f"✓ Fund info from TTFund: {info.name}")
                return info
        except Exception as e:
            print(f"TTFund get_fund_info failed: {e}")
        
        # Fallback to AKShare (currently disabled)
        try:
            info = await self._akshare.get_fund_info(fund_code)
            if info:
                print(f"✓ Fund info from AKShare: {info.name}")
                return info
        except Exception as e:
            print(f"AKShare get_fund_info also failed: {e}")
        
        # Last resort: basic info from realtime API
        try:
            estimate = await self._ttfund.get_realtime_estimate(fund_code)
            if estimate:
                return FundBasicInfo(
                    code=fund_code,
                    name=estimate.get("name", fund_code),
                )
        except:
            pass
        
        return None
    
    async def get_nav_history(
        self, 
        fund_code: str, 
        period: str = "1y"
    ) -> Optional[FundNAVHistory]:
        """
        Get fund NAV history with failover.
        
        Primary: TTFund (stable)
        Fallback: AKShare (currently disabled)
        """
        # Try TTFund first
        try:
            history = await get_nav_history_from_ttfund(fund_code, period)
            if history and history.data:
                print(f"✓ NAV history from TTFund: {len(history.data)} points")
                return history
            print(f"TTFund returned no NAV history for {fund_code}")
        except Exception as e:
            print(f"TTFund NAV fetch failed for {fund_code}: {e}")
        
        # Fallback to AKShare (currently disabled due to crashes)
        try:
            history = await self._akshare.get_nav_history(fund_code, period)
            if history:
                print(f"✓ NAV history from AKShare: {len(history.data)} points")
                return history
        except Exception as e:
            print(f"AKShare NAV fetch also failed: {e}")
        
        print(f"No NAV history available for {fund_code}")
        return None
    
    async def get_holdings(self, fund_code: str) -> Optional[FundHoldings]:
        """
        Get fund holdings with failover.
        
        Primary: TTFund
        Fallback: AKShare (currently disabled)
        """
        # Try TTFund first
        try:
            holdings = await get_holdings_from_ttfund(fund_code)
            if holdings and holdings.stock_holdings:
                print(f"✓ Holdings from TTFund: {len(holdings.stock_holdings)} stocks")
                return holdings
        except Exception as e:
            print(f"TTFund holdings failed: {e}")
        
        # Fallback to AKShare (currently disabled)
        try:
            holdings = await self._akshare.get_holdings(fund_code)
            if holdings:
                return holdings
        except Exception as e:
            print(f"AKShare holdings also failed: {e}")
        
        # Return empty holdings
        return FundHoldings(
            code=fund_code,
            name="",
            stock_holdings=[],
        )
    
    async def get_realtime_estimate(self, fund_code: str) -> Optional[dict]:
        """Get real-time estimate (only available from TTFund)."""
        return await self._ttfund.get_realtime_estimate(fund_code)
    
    async def get_fund_with_estimate(self, fund_code: str) -> Optional[dict]:
        """Get fund info combined with real-time estimate."""
        info = await self.get_fund_info(fund_code)
        if not info:
            return None
        
        result = info.model_dump()
        
        # Add real-time estimate
        estimate = await self.get_realtime_estimate(fund_code)
        if estimate:
            result["realtime_estimate"] = estimate
        
        return result


# Singleton instance
_data_fetcher: Optional[DataFetcher] = None


def get_data_fetcher() -> DataFetcher:
    """Get singleton data fetcher instance."""
    global _data_fetcher
    if _data_fetcher is None:
        _data_fetcher = DataFetcher()
    return _data_fetcher
