"""Parse fund fee tables from Eastmoney F10 (jjfl) HTML."""

from __future__ import annotations

import asyncio
import re
import urllib.request
from typing import Any

import httpx

JJFL_URL = "https://fundf10.eastmoney.com/jjfl_{code}.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://fund.eastmoney.com/",
}


def _parse_pct_cell(raw: str) -> float | None:
    raw = (raw or "").strip()
    if not raw or raw in ("---", "--", "-", "－"):
        return None
    m = re.search(r"([\d.]+)\s*%", raw)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def parse_jjfl_html(html: str) -> dict[str, Any]:
    """
    Extract operation fees + redemption tiers from jjfl page body.

    Returns keys: management_fee, custody_fee, sales_service_fee,
    redemption_tiers (list of {period, rate}), redemption_fee_detail (str)
    """
    out: dict[str, Any] = {}

    # 允许标签间空白/换行
    mg = re.search(r"管理费率</td>\s*<td[^>]*>([^<]+)</td>", html, re.DOTALL)
    tg = re.search(r"托管费率</td>\s*<td[^>]*>([^<]+)</td>", html, re.DOTALL)
    ss = re.search(r"销售服务费率</td>\s*<td[^>]*>([^<]+)</td>", html, re.DOTALL)
    if mg:
        out["management_fee"] = _parse_pct_cell(mg.group(1))
    if tg:
        out["custody_fee"] = _parse_pct_cell(tg.group(1))
    if ss:
        out["sales_service_fee"] = _parse_pct_cell(ss.group(1))

    # 赎回表：锚定「赎回费率」区块，避免匹配到上方认购/申购表
    sec = re.search(
        r'赎回费率<a name="shfl"></a>.*?</thead>\s*<tbody>(.*?)</tbody>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if not sec:
        sec = re.search(
            r"赎回费率.*?</thead>\s*<tbody>(.*?)</tbody>",
            html,
            re.DOTALL | re.IGNORECASE,
        )
    tiers: list[dict[str, str]] = []
    if sec:
        for a, b in re.findall(r"<td>([^<]+)</td>\s*<td>([^<]+)</td>", sec.group(1)):
            tiers.append({"period": a.strip(), "rate": b.strip()})
    out["redemption_tiers"] = tiers
    if tiers:
        lines = [f"{t['period']}：{t['rate']}" for t in tiers[:8]]
        out["redemption_fee_detail"] = "；".join(lines)
        if len(tiers) > 8:
            out["redemption_fee_detail"] += "；…"

    lock_hints: list[str] = []
    if "定开" in html or "定期开放" in html:
        lock_hints.append("基金可能为定期开放运作，请以基金合同与公告为准。")
    if "持有期" in html and "赎回" in html:
        m = re.search(r"持有期[^。<]{0,40}", html)
        if m:
            lock_hints.append(m.group(0).strip())
    if lock_hints:
        out["lockup_note"] = " ".join(dict.fromkeys(lock_hints))

    return out


def compute_annual_operating_pct(
    management: float | None,
    custody: float | None,
    sales: float | None,
) -> float | None:
    parts = [x for x in (management, custody, sales) if x is not None]
    if not parts:
        return None
    return round(sum(parts), 4)


def build_holding_cost_summary(
    annual_operating: float | None,
    redemption_detail: str | None,
    subscription_note: str | None,
    purchase_note: str | None,
) -> str:
    parts: list[str] = []
    if annual_operating is not None:
        parts.append(
            f"年度运作费率合计约 {annual_operating}%/年（管理费+托管费+销售服务费，"
            "从基金资产每日计提，已反映在净值中）。"
        )
    else:
        parts.append("年度运作费率请以下表或基金公司公告为准。")
    if subscription_note:
        parts.append(subscription_note)
    if purchase_note:
        parts.append(purchase_note)
    if redemption_detail:
        tail = redemption_detail[:280] + ("…" if len(redemption_detail) > 280 else "")
        parts.append(f"赎回分档摘要：{tail}")
    else:
        parts.append("赎回费通常按持有期限分档，持有越久费率越低。")
    parts.append("具体费率以基金合同、招募说明书及基金公司官网为准。")
    return " ".join(parts)


def _fetch_jjfl_html_sync(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


async def fetch_jjfl_fees_async(fund_code: str) -> dict[str, Any]:
    """
    拉取并解析费率页。优先 httpx；失败则用 urllib 同步请求（to_thread），避免
    旧版 httpx 在 aclose/finally 中抛错导致整段基金信息接口失败。
    """
    url = JJFL_URL.format(code=fund_code)

    try:
        async with httpx.AsyncClient(
            headers=HEADERS,
            timeout=20.0,
            trust_env=False,
            follow_redirects=True,
        ) as client:
            r = await client.get(url)
            if r.status_code == 200 and r.text:
                parsed = parse_jjfl_html(r.text)
                if parsed:
                    return parsed
    except Exception as e:
        print(f"[jjfl] httpx failed {fund_code}: {e}")

    try:
        html = await asyncio.to_thread(_fetch_jjfl_html_sync, url)
        if html:
            return parse_jjfl_html(html)
    except Exception as e:
        print(f"[jjfl] urllib fallback failed {fund_code}: {e}")

    return {}
