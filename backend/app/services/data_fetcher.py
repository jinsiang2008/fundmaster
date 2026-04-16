"""Unified data fetcher combining multiple data sources."""

from app.schemas.fund import (
    FundBasicInfo,
    FundHoldings,
    FundNAVHistory,
    FundRecommendRequest,
    FundRecommendResponse,
    FundSearchResult,
)
from app.services.akshare_fetcher import AKShareFetcher, get_akshare_fetcher
from app.services.fund_recommender import recommend_from_list
from app.services.ttfund_enhanced import (
    get_fund_info_from_ttfund,
    get_holdings_from_ttfund,
    get_nav_history_from_ttfund,
)
from app.services.ttfund_fetcher import TTFundFetcher, get_ttfund_fetcher

# 接口失败时的静态兜底（与旧版首页一致）
_FEATURED_FALLBACK: list[FundSearchResult] = [
    FundSearchResult(code="110011", name="易方达优质精选混合", type="混合型"),
    FundSearchResult(code="000961", name="天弘沪深300ETF联接A", type="指数型"),
    FundSearchResult(code="005827", name="易方达蓝筹精选混合", type="混合型"),
    FundSearchResult(code="161725", name="招商中证白酒指数", type="指数型"),
    FundSearchResult(code="007119", name="景顺长城绩优成长混合", type="混合型"),
]


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

    async def get_featured_funds(self, limit: int = 8) -> list[FundSearchResult]:
        """
        首页推荐位：优先从全市场基金表按日轮换抽样；失败则用静态列表。
        """
        try:
            raw = await self._ttfund.get_featured_funds(limit)
            if raw:
                return [
                    FundSearchResult(
                        code=r["code"],
                        name=r["name"],
                        type=r.get("type", ""),
                    )
                    for r in raw
                ]
        except Exception as e:
            print(f"get_featured_funds failed: {e}")
        return _FEATURED_FALLBACK[: min(limit, len(_FEATURED_FALLBACK))]

    async def recommend_funds(self, body: FundRecommendRequest) -> FundRecommendResponse:
        """规则化选基：全市场列表 + 类型/主题过滤。"""
        raw = await self._ttfund.get_fund_list_raw_cached()
        if not raw:
            return FundRecommendResponse(
                funds=[],
                profile_summary="暂时无法加载基金列表，请稍后重试。",
                disclaimer=(
                    "本推荐基于基金类型与名称关键词的规则筛选，非业绩排名或持牌投顾建议；"
                    "投资有风险，请结合招募说明书与个人情况决策。"
                ),
            )
        return recommend_from_list(raw, body)

    async def get_fund_info(self, fund_code: str) -> FundBasicInfo | None:
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
                    holding_cost_summary=(
                        "当前仅获取到行情简称，未能拉取完整档案与费率页。"
                        "请稍后再试，或至基金公司官网、代销机构 APP 的「基金详情-费率」查看。"
                    ),
                )
        except Exception:
            pass

        return None

    async def get_nav_history(self, fund_code: str, period: str = "1y") -> FundNAVHistory | None:
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

    async def get_holdings(self, fund_code: str) -> FundHoldings | None:
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

    async def get_realtime_estimate(self, fund_code: str) -> dict | None:
        """Get real-time estimate (only available from TTFund)."""
        return await self._ttfund.get_realtime_estimate(fund_code)

    async def get_fund_with_estimate(self, fund_code: str) -> dict | None:
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
_data_fetcher: DataFetcher | None = None


def get_data_fetcher() -> DataFetcher:
    """Get singleton data fetcher instance."""
    global _data_fetcher
    if _data_fetcher is None:
        _data_fetcher = DataFetcher()
    return _data_fetcher
