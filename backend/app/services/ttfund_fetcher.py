"""Tiantian Fund (天天基金) data fetcher for real-time estimates."""

import contextlib
import json
import re
import time
from datetime import date
from typing import Any

import httpx


class TTFundFetcher:
    """Fetcher for real-time fund data from Tiantian Fund."""

    BASE_URL = "http://fundgz.1234567.com.cn/js"
    DETAIL_URL = "http://fund.eastmoney.com/pingzhongdata"
    FUND_LIST_URL = "http://fund.eastmoney.com/js/fundcode_search.js"
    # 基金持仓明细（含股票名称、占净值比）；需带 topline 等参数，否则 tbody 为空
    JJCC_DATAS_URL = "https://fundf10.eastmoney.com/FundArchivesDatas.aspx"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "http://fund.eastmoney.com/",
    }

    # 全量基金列表缓存（与 search 同源），避免 featured 每次拉整包过于频繁
    _fund_list_raw: list[Any] | None = None
    _fund_list_loaded_at: float = 0.0
    FUND_LIST_CACHE_TTL_SEC = 3600.0

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            # 忽略系统/终端里的 HTTP(S)/SOCKS 代理，避免未安装 socksio 时
            # AsyncClient 初始化失败，或代理无法访问天天基金接口导致全站「加载失败」
            self._client = httpx.AsyncClient(
                headers=self.HEADERS,
                timeout=10.0,
                trust_env=False,
            )
        return self._client

    async def get_realtime_estimate(self, fund_code: str) -> dict | None:
        """
        Get real-time fund estimate during trading hours.

        Returns:
            dict with keys: code, name, nav, estimate_nav, estimate_change, update_time
        """
        try:
            client = await self._get_client()
            url = f"{self.BASE_URL}/{fund_code}.js"
            response = await client.get(url)

            if response.status_code != 200:
                return None

            # Parse jsonpgz callback response
            # Format: jsonpgz({"fundcode":"000001","name":"...","dwjz":"1.0",...});
            text = response.text
            match = re.search(r"jsonpgz\((.*)\)", text)
            if not match:
                return None

            data = json.loads(match.group(1))

            return {
                "code": data.get("fundcode"),
                "name": data.get("name"),
                "nav": float(data.get("dwjz", 0)),  # 单位净值
                "estimate_nav": float(data.get("gsz", 0)),  # 估算净值
                "estimate_change": float(data.get("gszzl", 0)),  # 估算涨跌幅
                "update_time": data.get("gztime"),  # 更新时间
                "nav_date": data.get("jzrq"),  # 净值日期
            }
        except Exception as e:
            print(f"Error getting realtime estimate: {e}")
            return None

    async def get_jjcc_datas_page(self, fund_code: str) -> str | None:
        """
        获取基金持仓页（FundArchivesDatas jjcc）原始文本。
        用于解析前十大股票持仓；与 pingzhongdata 中已变更的 stockCodesNew 格式互补。
        """
        try:
            client = await self._get_client()
            url = f"{self.JJCC_DATAS_URL}?type=jjcc&code={fund_code}&topline=50&year=&month=&typename=&rt=0.5"
            headers = {
                **self.HEADERS,
                "Referer": "https://fundf10.eastmoney.com/",
            }
            response = await client.get(url, headers=headers, timeout=20.0)
            if response.status_code != 200:
                return None
            return response.text
        except Exception as e:
            print(f"Error fetching jjcc page: {e}")
            return None

    async def get_fund_detail(self, fund_code: str) -> dict | None:
        """
        Get detailed fund data including history and performance.

        Parses JavaScript response from Eastmoney.
        """
        try:
            client = await self._get_client()
            url = f"{self.DETAIL_URL}/{fund_code}.js"
            response = await client.get(url)

            if response.status_code != 200:
                return None

            text = response.text
            result = {"code": fund_code}

            # Parse various data points from JS
            # Fund name
            name_match = re.search(r'fS_name\s*=\s*"([^"]+)"', text)
            if name_match:
                result["name"] = name_match.group(1)

            # Fund code
            code_match = re.search(r'fS_code\s*=\s*"([^"]+)"', text)
            if code_match:
                result["code"] = code_match.group(1)

            # Fund type
            type_match = re.search(r'Data_fundType\s*=\s*"([^"]+)"', text)
            if type_match:
                result["type"] = type_match.group(1)

            # Fund company
            company_match = re.search(r'fS_company\s*=\s*"([^"]+)"', text)
            if company_match:
                result["company"] = company_match.group(1)

            # Manager
            manager_match = re.search(r"Data_currentFundManager\s*=\s*(\[.*?\]);", text, re.DOTALL)
            if manager_match:
                try:
                    managers = json.loads(manager_match.group(1))
                    if managers:
                        result["manager"] = managers[0].get("name", "")
                        result["manager_id"] = managers[0].get("id", "")
                        result["manager_start_date"] = managers[0].get("startDate", "")
                except Exception:
                    pass

            # AUM (fund scale)
            aum_match = re.search(r'Data_fundScale\s*=\s*"([^"]+)"', text)
            if aum_match:
                with contextlib.suppress(Exception):
                    result["aum"] = float(aum_match.group(1))

            # NAV data array: Data_netWorthTrend
            nav_match = re.search(r"Data_netWorthTrend\s*=\s*(\[.*?\]);", text, re.DOTALL)
            if nav_match:
                try:
                    nav_data = json.loads(nav_match.group(1))
                    result["nav_history"] = nav_data  # Array of {x: timestamp, y: nav}
                except Exception as e:
                    print(f"Error parsing NAV history: {e}")

            # Accumulated NAV data: Data_ACWorthTrend
            acc_nav_match = re.search(r"Data_ACWorthTrend\s*=\s*(\[.*?\]);", text, re.DOTALL)
            if acc_nav_match:
                try:
                    acc_nav_data = json.loads(acc_nav_match.group(1))
                    result["acc_nav_history"] = acc_nav_data
                except Exception:
                    pass

            # Performance data
            perf_match = re.search(r'syl_1n\s*=\s*"([^"]+)"', text)
            if perf_match:
                result["return_1y"] = perf_match.group(1)

            perf_6m_match = re.search(r'syl_6y\s*=\s*"([^"]+)"', text)
            if perf_6m_match:
                result["return_6m"] = perf_6m_match.group(1)

            perf_3m_match = re.search(r'syl_3y\s*=\s*"([^"]+)"', text)
            if perf_3m_match:
                result["return_3m"] = perf_3m_match.group(1)

            perf_1m_match = re.search(r'syl_1y\s*=\s*"([^"]+)"', text)
            if perf_1m_match:
                result["return_1m"] = perf_1m_match.group(1)

            # 认/申购费率（页面展示用，实际以销售机构为准）
            fr_match = re.search(r'fund_Rate\s*=\s*"([^"]+)"', text)
            if fr_match:
                with contextlib.suppress(ValueError):
                    result["fund_Rate"] = float(fr_match.group(1))
            fsr_match = re.search(r'fund_sourceRate\s*=\s*"([^"]+)"', text)
            if fsr_match:
                with contextlib.suppress(ValueError):
                    result["fund_sourceRate"] = float(fsr_match.group(1))

            # Stock holdings: stockCodesNew
            holdings_match = re.search(r"stockCodesNew\s*=\s*(\[.*?\]);", text, re.DOTALL)
            if holdings_match:
                try:
                    holdings_data = json.loads(holdings_match.group(1))
                    result["stock_holdings"] = holdings_data
                except Exception:
                    pass

            return result if result.get("name") else None

        except Exception as e:
            print(f"Error getting fund detail from TTFund: {e}")
            return None

    async def _fetch_fund_list_raw(self) -> list[Any]:
        """拉取并解析东方财富基金代码表（与 search 同源）。"""
        client = await self._get_client()
        response = await client.get(self.FUND_LIST_URL)
        if response.status_code != 200:
            return []
        text = response.text
        match = re.search(r"var r = (\[.*?\]);", text, re.DOTALL)
        if not match:
            return []
        return json.loads(match.group(1))

    async def get_fund_list_raw_cached(self) -> list[Any]:
        """带内存缓存的全量列表，供搜索与首页推荐共用。"""
        now = time.monotonic()
        if self._fund_list_raw is not None and (now - self._fund_list_loaded_at) < self.FUND_LIST_CACHE_TTL_SEC:
            return self._fund_list_raw
        data = await self._fetch_fund_list_raw()
        self._fund_list_raw = data
        self._fund_list_loaded_at = now
        return data

    async def search_funds(self, query: str, limit: int = 20) -> list:
        """
        Search funds from Tiantian Fund list.

        Returns list of dicts with keys: code, name, type
        """
        try:
            funds_data = await self.get_fund_list_raw_cached()
            if not funds_data:
                return []

            # Filter by query
            results = []
            query_lower = query.lower()
            for fund in funds_data:
                if len(fund) < 4:
                    continue
                code, _, name, fund_type = fund[0], fund[1], fund[2], fund[3]

                # Match by code or name
                if query_lower in code.lower() or query_lower in name.lower():
                    results.append(
                        {
                            "code": code,
                            "name": name,
                            "type": fund_type,
                        }
                    )

                    if len(results) >= limit:
                        break

            return results

        except Exception as e:
            print(f"Error searching funds from TTFund: {e}")
            return []

    async def get_featured_funds(self, count: int = 8) -> list[dict]:
        """
        首页「推荐/热门」展示用：从全市场列表中按日期做确定性抽样，每日变化。

        说明：这不是官方销量/涨幅排名，仅为均匀抽样轮换，避免长期固定几只。
        """
        try:
            funds_data = await self.get_fund_list_raw_cached()
            n = len(funds_data)
            if n == 0:
                return []

            today = date.today()
            seed = today.toordinal()
            # 起点与步长随日期变化，使列表在时间与空间上更分散
            stride = 73 + (seed % 61)
            start = (seed * 1103515245 + 12345) % n
            out: list[dict] = []
            seen: set[str] = set()
            step_i = 0
            max_steps = min(n * 3, 50000)
            while len(out) < count and step_i < max_steps:
                idx = (start + step_i * stride) % n
                step_i += 1
                fund = funds_data[idx]
                if len(fund) < 4:
                    continue
                code, name, fund_type = fund[0], fund[2], fund[3]
                if code in seen:
                    continue
                seen.add(code)
                out.append({"code": code, "name": name, "type": fund_type})
            return out
        except Exception as e:
            print(f"Error get_featured_funds: {e}")
            return []

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Singleton instance
_ttfund_fetcher: TTFundFetcher | None = None


def get_ttfund_fetcher() -> TTFundFetcher:
    """Get singleton TTFund fetcher instance."""
    global _ttfund_fetcher
    if _ttfund_fetcher is None:
        _ttfund_fetcher = TTFundFetcher()
    return _ttfund_fetcher
