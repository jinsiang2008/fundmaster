"""Enhanced TTFund fetcher with full data extraction."""

import contextlib
import re
from datetime import date, datetime

import pandas as pd

from app.schemas.fund import (
    FundBasicInfo,
    FundHolding,
    FundHoldings,
    FundNAVHistory,
    NAVDataPoint,
)
from app.services.eastmoney_fees import (
    build_holding_cost_summary,
    compute_annual_operating_pct,
    fetch_jjfl_fees_async,
)
from app.services.ttfund_fetcher import get_ttfund_fetcher


async def get_fund_info_from_ttfund(fund_code: str) -> FundBasicInfo | None:
    """Get fund basic info from TTFund detail endpoint + Eastmoney F10 fee page."""
    fetcher = get_ttfund_fetcher()
    detail = await fetcher.get_fund_detail(fund_code)

    if not detail:
        return None

    # Parse inception date
    inception_date = None
    if detail.get("inception_date"):
        with contextlib.suppress(Exception):
            inception_date = datetime.strptime(detail["inception_date"], "%Y-%m-%d").date()

    fee_html: dict = {}
    try:
        fee_html = await fetch_jjfl_fees_async(fund_code)
    except Exception as e:
        print(f"get_fund_info_from_ttfund: jjfl fee fetch failed {fund_code}: {e}")

    mg = fee_html.get("management_fee")
    cg = fee_html.get("custody_fee")
    sg = fee_html.get("sales_service_fee")
    if mg is None and detail.get("management_fee") is not None:
        mg = detail.get("management_fee")
    if cg is None and detail.get("custody_fee") is not None:
        cg = detail.get("custody_fee")

    annual = compute_annual_operating_pct(mg, cg, sg)

    sub_note = None
    if detail.get("fund_sourceRate") is not None:
        sub_note = f"认购费率上限参考约 {detail['fund_sourceRate']}%（募集期，以基金合同为准）。"
    pur_note = None
    if detail.get("fund_Rate") is not None:
        pur_note = f"申购费率参考约 {detail['fund_Rate']}%（以各销售机构实际折扣为准）。"

    lock_note = fee_html.get("lockup_note")
    ftype = detail.get("type") or ""
    if not lock_note and ("定开" in ftype or "定期开放" in ftype):
        lock_note = "该基金可能含定期开放等特殊申赎安排，请关注开放期与封闭期公告。"

    redemption_detail = fee_html.get("redemption_fee_detail")
    holding_summary = build_holding_cost_summary(
        annual,
        redemption_detail,
        sub_note,
        pur_note,
    )

    # 赎回费率：取分档中最低一档的百分比（常为长期持有免赎回费）
    redemption_min = None
    for t in fee_html.get("redemption_tiers") or []:
        rate = t.get("rate", "")
        m = re.search(r"([\d.]+)\s*%", rate)
        if m:
            try:
                v = float(m.group(1))
                redemption_min = v if redemption_min is None else min(redemption_min, v)
            except ValueError:
                pass

    return FundBasicInfo(
        code=fund_code,
        name=detail.get("name", ""),
        type=ftype,
        company=detail.get("company", ""),
        manager=detail.get("manager", ""),
        aum=detail.get("aum"),
        inception_date=inception_date,
        management_fee=mg,
        custody_fee=cg,
        sales_service_fee=sg,
        purchase_fee=detail.get("fund_Rate"),
        max_subscription_fee_pct=detail.get("fund_sourceRate"),
        redemption_fee=redemption_min,
        annual_operating_fee_pct=annual,
        redemption_fee_detail=redemption_detail,
        lockup_note=lock_note,
        holding_cost_summary=holding_summary,
    )


async def get_nav_history_from_ttfund(
    fund_code: str,
    period: str = "1y",
) -> FundNAVHistory | None:
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
        except Exception:
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

            data_points.append(
                NAVDataPoint(
                    date=nav_date,
                    nav=float(nav),
                    acc_nav=float(acc_nav) if acc_nav else None,
                )
            )
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


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def _parse_jjcc_row_qdii_toc(row: str) -> FundHolding | None:
    """
    QDII 等基金持仓行：列使用 class=toc（非 tol/tor），含港股 5 位代码如 00700。
    """
    # 前两列：证券代码、名称（带 quote 行情链接）
    code_name = re.findall(
        r"<td class='toc'[^>]*>\s*<a href='//quote\.eastmoney\.com/unify/r/[^']+'[^>]*>([^<]+)</a>",
        row,
    )
    if len(code_name) < 2:
        return None
    code = code_name[0].strip()
    name = code_name[1].strip().replace("&nbsp;", " ")
    if not code or not name:
        return None

    toc_cells = [_strip_tags(m.group(1)) for m in re.finditer(r"<td class='toc'[^>]*>(.*?)</td>", row, re.DOTALL)]
    ratio: float | None = None
    ratio_i: int | None = None
    for i, cell in enumerate(toc_cells):
        if cell.endswith("%"):
            core = cell[:-1].strip()
            if core and re.match(r"^[\d.]+$", core):
                try:
                    v = float(core)
                    if 0 < v <= 100:
                        ratio = v
                        ratio_i = i
                        break
                except ValueError:
                    continue
    if ratio is None or ratio_i is None:
        return None

    shares_val: float | None = None
    mv_val: float | None = None
    if ratio_i + 1 < len(toc_cells):
        s = toc_cells[ratio_i + 1].replace(",", "")
        if s and re.match(r"^[\d.]+$", s):
            with contextlib.suppress(ValueError):
                shares_val = float(s)
    if ratio_i + 2 < len(toc_cells):
        m = toc_cells[ratio_i + 2].replace(",", "")
        if m and re.match(r"^[\d.]+$", m):
            with contextlib.suppress(ValueError):
                mv_val = float(m)

    return FundHolding(
        code=code,
        name=name,
        ratio=ratio,
        shares=shares_val,
        market_value=mv_val,
    )


def _parse_jjcc_row_a_share(row: str) -> FundHolding | None:
    """普通开放式基金：tol + tor 列。"""
    code_m = re.search(r"'>(\d{6})</a></td><td class='tol'", row)
    if not code_m:
        code_m = re.search(r"unify/r/[01]\.\d+'>(\d{6})</a>", row)
    name_m = re.search(r"class='tol'><a[^>]*>([^<]+)</a>", row)
    if not (code_m and name_m):
        return None

    tor_cells = [_strip_tags(m.group(1)) for m in re.finditer(r"<td class='tor'>(.*?)</td>", row, re.DOTALL)]
    ratio: float | None = None
    ratio_i: int | None = None
    for i, cell in enumerate(tor_cells):
        if cell.endswith("%"):
            core = cell[:-1].strip()
            if core and re.match(r"^[\d.]+$", core):
                try:
                    v = float(core)
                    if 0 < v <= 100:
                        ratio = v
                        ratio_i = i
                        break
                except ValueError:
                    continue
    if ratio is None or ratio_i is None:
        return None

    shares_val: float | None = None
    mv_val: float | None = None
    if ratio_i + 1 < len(tor_cells):
        s = tor_cells[ratio_i + 1].replace(",", "")
        if s and re.match(r"^[\d.]+$", s):
            with contextlib.suppress(ValueError):
                shares_val = float(s)
    if ratio_i + 2 < len(tor_cells):
        m = tor_cells[ratio_i + 2].replace(",", "")
        if m and re.match(r"^[\d.]+$", m):
            with contextlib.suppress(ValueError):
                mv_val = float(m)

    return FundHolding(
        code=code_m.group(1),
        name=name_m.group(1).strip().replace("&nbsp;", " "),
        ratio=ratio,
        shares=shares_val,
        market_value=mv_val,
    )


def parse_jjcc_stock_table(html: str) -> tuple[list[FundHolding], date | None]:
    """
    解析基金 F10「基金持仓」接口返回的 HTML（FundArchivesDatas.aspx?type=jjcc&...&topline=50）。
    取第一个 tbody（最新一期季报）的前十大股票。
    """
    report_date: date | None = None
    dm = re.search(r"截止至[^<]*<font[^>]*>(\d{4}-\d{2}-\d{2})</font>", html)
    if dm:
        with contextlib.suppress(ValueError):
            report_date = datetime.strptime(dm.group(1), "%Y-%m-%d").date()

    tbodies = re.findall(r"<tbody>(.*?)</tbody>", html, re.DOTALL)
    if not tbodies or not tbodies[0].strip():
        return [], report_date

    rows = re.findall(r"<tr>(.*?)</tr>", tbodies[0], re.DOTALL)
    out: list[FundHolding] = []

    for row in rows:
        fh: FundHolding | None = None
        # QDII/港股：表格用 class=toc，无 tol
        if "class='tol'" not in row and "class='toc'" in row and "unify/r" in row:
            fh = _parse_jjcc_row_qdii_toc(row)
        if fh is None:
            fh = _parse_jjcc_row_a_share(row)
        if fh:
            out.append(fh)
        if len(out) >= 10:
            break

    return out, report_date


async def get_holdings_from_ttfund(fund_code: str) -> FundHoldings | None:
    """
    基金持仓：优先东方财富 F10 季报明细（名称、占比、持股数、市值）；
    其次兼容 pingzhongdata 中旧版 stockCodesNew（嵌套数组）。
    说明：新版 JS 里 stockCodesNew 仅为「市场.代码」字符串数组，无法还原名称与占比，故不再依赖。
    """
    fetcher = get_ttfund_fetcher()
    detail = await fetcher.get_fund_detail(fund_code)
    fund_name = detail.get("name", fund_code) if detail else fund_code

    jjcc_html = await fetcher.get_jjcc_datas_page(fund_code)
    if jjcc_html:
        stock_holdings, rdate = parse_jjcc_stock_table(jjcc_html)
        if stock_holdings:
            print(f"✓ Holdings from jjcc F10: {len(stock_holdings)} stocks")
            return FundHoldings(
                code=fund_code,
                name=fund_name,
                report_date=rdate,
                stock_holdings=stock_holdings[:10],
            )

    if not detail or not detail.get("stock_holdings"):
        return None

    holdings_data = detail["stock_holdings"]
    stock_holdings: list[FundHolding] = []

    for item in holdings_data:
        try:
            if isinstance(item, list) and len(item) >= 3:
                stock_holdings.append(
                    FundHolding(
                        code=str(item[0]),
                        name=str(item[1]),
                        ratio=float(item[2]),
                    )
                )
        except Exception:
            continue

    if not stock_holdings:
        return None

    return FundHoldings(
        code=fund_code,
        name=fund_name,
        stock_holdings=stock_holdings[:10],
    )
