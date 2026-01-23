"""AKShare data fetcher for Chinese mutual funds."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from functools import lru_cache
from typing import Optional

import akshare as ak
import pandas as pd

from app.schemas.fund import (
    FundBasicInfo,
    FundSearchResult,
    FundNAVHistory,
    NAVDataPoint,
    FundHolding,
    FundHoldings,
)


class AKShareFetcher:
    """Fetcher for fund data using AKShare library."""
    
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._fund_list_cache: Optional[pd.DataFrame] = None
        self._fund_list_cache_time: Optional[datetime] = None
    
    async def _run_sync(self, func, *args, **kwargs):
        """Run synchronous function in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor, 
            lambda: func(*args, **kwargs)
        )
    
    def _get_fund_list_sync(self) -> pd.DataFrame:
        """
        Get fund list (DISABLED due to libmini_racer crashes).
        
        AKShare has dependency issues with libmini_racer on macOS.
        Use TTFund instead for fund search.
        """
        print("⚠️  AKShare fund list disabled (libmini_racer crashes)")
        print("    Using TTFund as primary data source")
        
        # Return cached data if available, otherwise empty
        if self._fund_list_cache is not None:
            return self._fund_list_cache
        
        return pd.DataFrame()
    
    async def search_funds(self, query: str, limit: int = 20) -> list[FundSearchResult]:
        """Search funds by name or code."""
        def _search() -> list[FundSearchResult]:
            df = self._get_fund_list_sync()
            if df.empty:
                print("Fund list DataFrame is empty")
                return []
            
            print(f"Searching in DataFrame with columns: {list(df.columns)[:10]}")
            
            # Try to find column names (different versions may have different column names)
            code_col = None
            name_col = None
            type_col = None
            
            # Possible column name variations
            for col in df.columns:
                col_lower = str(col).lower()
                if code_col is None and ('代码' in col or 'code' in col_lower):
                    code_col = col
                if name_col is None and ('名称' in col or '简称' in col or 'name' in col_lower):
                    name_col = col
                if type_col is None and ('类型' in col or 'type' in col_lower):
                    type_col = col
            
            if not code_col or not name_col:
                print(f"Could not find required columns. Available: {list(df.columns)}")
                return []
            
            print(f"Using columns - code: {code_col}, name: {name_col}, type: {type_col}")
            
            # Fuzzy match on code or name
            try:
                mask = (
                    df[code_col].astype(str).str.contains(query, case=False, na=False) |
                    df[name_col].astype(str).str.contains(query, case=False, na=False)
                )
                results = df[mask].head(limit)
                
                return [
                    FundSearchResult(
                        code=str(row[code_col]),
                        name=str(row[name_col]),
                        type=str(row[type_col]) if type_col and pd.notna(row.get(type_col)) else '',
                    )
                    for _, row in results.iterrows()
                ]
            except Exception as e:
                print(f"Error during search: {e}")
                return []
        
        return await self._run_sync(_search)
    
    async def get_fund_info(self, fund_code: str) -> Optional[FundBasicInfo]:
        """Get basic fund information."""
        def _get_info() -> Optional[FundBasicInfo]:
            try:
                # Get fund info from multiple sources
                info = {}
                
                # Try to get from fund list first
                df = self._get_fund_list_sync()
                if not df.empty:
                    fund_row = df[df['基金代码'] == fund_code]
                    if not fund_row.empty:
                        row = fund_row.iloc[0]
                        info['name'] = row.get('基金简称', '')
                        info['type'] = row.get('基金类型', '')
                
                # Get detailed info
                try:
                    detail_df = ak.fund_individual_basic_info_xq(symbol=fund_code)
                    if detail_df is not None and not detail_df.empty:
                        for _, row in detail_df.iterrows():
                            item = row.get('item', '')
                            value = row.get('value', '')
                            if '基金经理' in item:
                                info['manager'] = value
                            elif '基金公司' in item or '管理人' in item:
                                info['company'] = value
                            elif '成立日期' in item:
                                try:
                                    info['inception_date'] = datetime.strptime(value, '%Y-%m-%d').date()
                                except:
                                    pass
                            elif '管理费' in item:
                                try:
                                    info['management_fee'] = float(value.replace('%', ''))
                                except:
                                    pass
                            elif '托管费' in item:
                                try:
                                    info['custody_fee'] = float(value.replace('%', ''))
                                except:
                                    pass
                except Exception as e:
                    print(f"Error getting fund detail: {e}")
                
                # Get latest NAV - try different methods
                nav_functions = [
                    ('fund_open_fund_info_em', {'symbol': fund_code, 'indicator': '单位净值走势'}),
                    ('fund_em_open_fund_info', {'fund': fund_code, 'indicator': '单位净值走势'}),
                ]
                
                for func_name, kwargs in nav_functions:
                    try:
                        if hasattr(ak, func_name):
                            func = getattr(ak, func_name)
                            nav_df = func(**kwargs)
                            if nav_df is not None and not nav_df.empty:
                                latest = nav_df.iloc[-1]
                                # Find NAV column
                                nav_col = None
                                date_col = None
                                for col in nav_df.columns:
                                    if '净值' in str(col) and '累计' not in str(col):
                                        nav_col = col
                                    if '日期' in str(col):
                                        date_col = col
                                
                                if nav_col:
                                    info['nav'] = float(latest[nav_col])
                                if date_col:
                                    info['nav_date'] = pd.to_datetime(latest[date_col]).date()
                                break
                    except Exception as e:
                        print(f"Error getting NAV with {func_name}: {e}")
                
                # Get fund scale - try different methods
                scale_functions = [
                    ('fund_open_fund_info_em', {'symbol': fund_code, 'indicator': '规模变动'}),
                    ('fund_em_open_fund_info', {'fund': fund_code, 'indicator': '规模变动'}),
                ]
                
                for func_name, kwargs in scale_functions:
                    try:
                        if hasattr(ak, func_name):
                            func = getattr(ak, func_name)
                            scale_df = func(**kwargs)
                            if scale_df is not None and not scale_df.empty:
                                latest = scale_df.iloc[-1]
                                for col in scale_df.columns:
                                    if '净资产' in str(col) or 'aum' in str(col).lower():
                                        info['aum'] = float(latest[col]) / 100000000  # Convert to 亿
                                        break
                                break
                    except Exception as e:
                        print(f"Error getting scale with {func_name}: {e}")
                
                if not info.get('name'):
                    return None
                
                return FundBasicInfo(
                    code=fund_code,
                    name=info.get('name', ''),
                    type=info.get('type', ''),
                    company=info.get('company', ''),
                    inception_date=info.get('inception_date'),
                    manager=info.get('manager', ''),
                    aum=info.get('aum'),
                    nav=info.get('nav'),
                    nav_date=info.get('nav_date'),
                    management_fee=info.get('management_fee'),
                    custody_fee=info.get('custody_fee'),
                )
            except Exception as e:
                print(f"Error in get_fund_info: {e}")
                return None
        
        return await self._run_sync(_get_info)
    
    async def get_nav_history(
        self, 
        fund_code: str, 
        period: str = "1y"
    ) -> Optional[FundNAVHistory]:
        """
        Get fund NAV history (DISABLED due to libmini_racer crashes).
        
        Returns None to trigger failover to TTFund.
        """
        print(f"⚠️  AKShare NAV history disabled for {fund_code} (using TTFund instead)")
        return None
        
        # ORIGINAL CODE DISABLED TO AVOID CRASHES
        def _get_nav_disabled() -> Optional[FundNAVHistory]:
            # This code is disabled because AKShare functions crash with libmini_racer
            try:
                
                # Filter by period
                end_date = datetime.now()
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
                start_date = end_date - pd.Timedelta(days=days)
                
                df['净值日期'] = pd.to_datetime(df['净值日期'])
                df = df[df['净值日期'] >= start_date]
                
                # Get fund name
                fund_list = self._get_fund_list_sync()
                fund_row = fund_list[fund_list['基金代码'] == fund_code]
                fund_name = fund_row.iloc[0]['基金简称'] if not fund_row.empty else fund_code
                
                data_points = []
                for _, row in df.iterrows():
                    try:
                        data_points.append(NAVDataPoint(
                            date=row['净值日期'].date(),
                            nav=float(row['单位净值']),
                            acc_nav=float(row.get('累计净值', row['单位净值'])),
                            change_pct=float(row.get('日增长率', 0)) if pd.notna(row.get('日增长率')) else None,
                        ))
                    except:
                        continue
                
                return FundNAVHistory(
                    code=fund_code,
                    name=fund_name,
                    data=data_points,
                )
            except Exception as e:
                print(f"Error getting NAV history: {e}")
                return None
        
        return await self._run_sync(_get_nav)
    
    async def get_fund_info(self, fund_code: str) -> Optional[FundBasicInfo]:
        """
        Get fund basic information (DISABLED due to libmini_racer crashes).
        
        Returns None to trigger failover to TTFund.
        """
        print(f"⚠️  AKShare fund info disabled for {fund_code} (using TTFund instead)")
        return None
    
    async def get_holdings(self, fund_code: str) -> Optional[FundHoldings]:
        """
        Get fund holdings (DISABLED due to libmini_racer crashes).
        
        Returns None - holdings data not available from AKShare.
        """
        print(f"⚠️  AKShare holdings disabled for {fund_code}")
        return None
    
    async def get_holdings_disabled(self, fund_code: str) -> Optional[FundHoldings]:
        """ORIGINAL CODE - DISABLED."""
        def _get_holdings() -> Optional[FundHoldings]:
            try:
                # Get fund name
                fund_list = self._get_fund_list_sync()
                fund_name = fund_code
                
                if not fund_list.empty:
                    # Find code column
                    code_col = None
                    name_col = None
                    for col in fund_list.columns:
                        if '代码' in str(col) or 'code' in str(col).lower():
                            code_col = col
                        if '名称' in str(col) or '简称' in str(col) or 'name' in str(col).lower():
                            name_col = col
                    
                    if code_col and name_col:
                        fund_row = fund_list[fund_list[code_col].astype(str) == fund_code]
                        if not fund_row.empty:
                            fund_name = fund_row.iloc[0][name_col]
                
                stock_holdings = []
                
                # Try different holding functions
                holding_functions = [
                    ('fund_portfolio_hold_em', {'symbol': fund_code, 'date': '2024'}),
                    ('fund_em_portfolio_hold', {'symbol': fund_code}),
                ]
                
                for func_name, kwargs in holding_functions:
                    try:
                        if hasattr(ak, func_name):
                            func = getattr(ak, func_name)
                            df = func(**kwargs)
                            if df is not None and not df.empty:
                                print(f"Holdings success with {func_name}, columns: {list(df.columns)[:5]}")
                                # Try to map columns
                                for _, row in df.head(10).iterrows():
                                    # Find columns dynamically
                                    name_val = ''
                                    code_val = ''
                                    ratio_val = 0.0
                                    
                                    for col in df.columns:
                                        col_str = str(col)
                                        if '名称' in col_str and not name_val:
                                            name_val = str(row[col])
                                        elif '代码' in col_str and not code_val:
                                            code_val = str(row[col])
                                        elif ('比例' in col_str or 'ratio' in col_str.lower()) and ratio_val == 0:
                                            try:
                                                ratio_val = float(row[col])
                                            except:
                                                pass
                                    
                                    if name_val:  # Only add if we have at least a name
                                        stock_holdings.append(FundHolding(
                                            name=name_val,
                                            code=code_val if code_val else None,
                                            ratio=ratio_val,
                                            shares=None,
                                            market_value=None,
                                        ))
                                break
                    except Exception as e:
                        print(f"Error getting holdings with {func_name}: {e}")
                
                return FundHoldings(
                    code=fund_code,
                    name=fund_name,
                    stock_holdings=stock_holdings,
                )
            except Exception as e:
                print(f"Error in get_holdings: {e}")
                return None
        
        return await self._run_sync(_get_holdings)


# Singleton instance
_akshare_fetcher: Optional[AKShareFetcher] = None


def get_akshare_fetcher() -> AKShareFetcher:
    """Get singleton AKShare fetcher instance."""
    global _akshare_fetcher
    if _akshare_fetcher is None:
        _akshare_fetcher = AKShareFetcher()
    return _akshare_fetcher
