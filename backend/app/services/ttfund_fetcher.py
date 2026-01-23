"""Tiantian Fund (天天基金) data fetcher for real-time estimates."""

import re
import json
from datetime import datetime
from typing import Optional

import httpx

from app.schemas.fund import FundBasicInfo


class TTFundFetcher:
    """Fetcher for real-time fund data from Tiantian Fund."""
    
    BASE_URL = "http://fundgz.1234567.com.cn/js"
    DETAIL_URL = "http://fund.eastmoney.com/pingzhongdata"
    FUND_LIST_URL = "http://fund.eastmoney.com/js/fundcode_search.js"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "http://fund.eastmoney.com/",
    }
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=self.HEADERS,
                timeout=10.0,
            )
        return self._client
    
    async def get_realtime_estimate(self, fund_code: str) -> Optional[dict]:
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
            match = re.search(r'jsonpgz\((.*)\)', text)
            if not match:
                return None
            
            data = json.loads(match.group(1))
            
            return {
                "code": data.get("fundcode"),
                "name": data.get("name"),
                "nav": float(data.get("dwjz", 0)),          # 单位净值
                "estimate_nav": float(data.get("gsz", 0)),   # 估算净值
                "estimate_change": float(data.get("gszzl", 0)),  # 估算涨跌幅
                "update_time": data.get("gztime"),           # 更新时间
                "nav_date": data.get("jzrq"),                # 净值日期
            }
        except Exception as e:
            print(f"Error getting realtime estimate: {e}")
            return None
    
    async def get_fund_detail(self, fund_code: str) -> Optional[dict]:
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
            manager_match = re.search(r'Data_currentFundManager\s*=\s*(\[.*?\]);', text, re.DOTALL)
            if manager_match:
                try:
                    managers = json.loads(manager_match.group(1))
                    if managers:
                        result["manager"] = managers[0].get("name", "")
                        result["manager_id"] = managers[0].get("id", "")
                        result["manager_start_date"] = managers[0].get("startDate", "")
                except:
                    pass
            
            # AUM (fund scale)
            aum_match = re.search(r'Data_fundScale\s*=\s*"([^"]+)"', text)
            if aum_match:
                try:
                    result["aum"] = float(aum_match.group(1))
                except:
                    pass
            
            # NAV data array: Data_netWorthTrend
            nav_match = re.search(r'Data_netWorthTrend\s*=\s*(\[.*?\]);', text, re.DOTALL)
            if nav_match:
                try:
                    nav_data = json.loads(nav_match.group(1))
                    result["nav_history"] = nav_data  # Array of {x: timestamp, y: nav}
                except Exception as e:
                    print(f"Error parsing NAV history: {e}")
            
            # Accumulated NAV data: Data_ACWorthTrend
            acc_nav_match = re.search(r'Data_ACWorthTrend\s*=\s*(\[.*?\]);', text, re.DOTALL)
            if acc_nav_match:
                try:
                    acc_nav_data = json.loads(acc_nav_match.group(1))
                    result["acc_nav_history"] = acc_nav_data
                except:
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
            
            # Stock holdings: stockCodesNew
            holdings_match = re.search(r'stockCodesNew\s*=\s*(\[.*?\]);', text, re.DOTALL)
            if holdings_match:
                try:
                    holdings_data = json.loads(holdings_match.group(1))
                    result["stock_holdings"] = holdings_data
                except:
                    pass
            
            return result if result.get("name") else None
            
        except Exception as e:
            print(f"Error getting fund detail from TTFund: {e}")
            return None
    
    async def search_funds(self, query: str, limit: int = 20) -> list:
        """
        Search funds from Tiantian Fund list.
        
        Returns list of dicts with keys: code, name, type
        """
        try:
            client = await self._get_client()
            response = await client.get(self.FUND_LIST_URL)
            
            if response.status_code != 200:
                return []
            
            # Parse: var r = [["000001","HXCZHH","华夏成长混合","混合型-偏股","HUAXIACHENCHANGHUNHE"],...];
            text = response.text
            match = re.search(r'var r = (\[.*?\]);', text, re.DOTALL)
            if not match:
                return []
            
            # Parse JSON array
            data_str = match.group(1)
            funds_data = json.loads(data_str)
            
            # Filter by query
            results = []
            query_lower = query.lower()
            for fund in funds_data:
                if len(fund) < 4:
                    continue
                code, _, name, fund_type = fund[0], fund[1], fund[2], fund[3]
                
                # Match by code or name
                if query_lower in code.lower() or query_lower in name.lower():
                    results.append({
                        "code": code,
                        "name": name,
                        "type": fund_type,
                    })
                    
                    if len(results) >= limit:
                        break
            
            return results
            
        except Exception as e:
            print(f"Error searching funds from TTFund: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Singleton instance
_ttfund_fetcher: Optional[TTFundFetcher] = None


def get_ttfund_fetcher() -> TTFundFetcher:
    """Get singleton TTFund fetcher instance."""
    global _ttfund_fetcher
    if _ttfund_fetcher is None:
        _ttfund_fetcher = TTFundFetcher()
    return _ttfund_fetcher
