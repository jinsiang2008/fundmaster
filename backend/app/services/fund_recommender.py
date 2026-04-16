"""
基于全市场基金元数据（类型 + 名称关键词）的规则推荐。

非量化回测排序，不替代投顾；用于缩小选基范围并给出可读理由。
"""

from __future__ import annotations

import hashlib
from typing import Any, Literal

from app.schemas.fund import FundRecommendRequest, FundRecommendResponse, RecommendedFund

Risk = Literal["conservative", "stable", "balanced", "aggressive", "radical"]
Horizon = Literal["short", "medium", "long"]
Liquidity = Literal["high", "medium", "low"]

# 主题：前端传 theme id → 名称中需命中任一关键词
THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "broad_index": ("沪深300", "中证500", "上证50", "创业板指", "MSCI", "联接", "宽基"),
    "dividend": ("红利", "股息", "低波动", "低波"),
    "tech": ("科技", "半导体", "芯片", "人工智能", "TMT", "互联网", "软件", "信息"),
    "medical": ("医药", "医疗", "生物", "健康", "创新药"),
    "consumption": ("消费", "白酒", "食品", "饮料", "家电"),
    "new_energy": ("新能源", "光伏", "锂电", "碳中和", "电池", "新能源车"),
    "hk": ("港股", "恒生", "恒生科技", "H股"),
    "gold": ("黄金", "贵金属"),
    "us": ("纳斯达克", "标普", "美国", "纳指", "美股"),
    "bond": ("债", "纯债", "短债", "中短债", "转债", "信用债"),
}


def _hash_seed(parts: tuple[str, ...]) -> int:
    h = hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()
    return int(h[:12], 16)


def _type_bucket(ft: str) -> str:
    ft = (ft or "").lower()
    if "货币" in ft:
        return "money"
    if "债" in ft or "纯债" in ft or "短债" in ft:
        return "bond"
    if "指数" in ft or "etf" in ft or "联接" in ft:
        return "index"
    if "qdii" in ft or "境外" in ft:
        return "qdii"
    if "混合" in ft:
        return "mixed"
    if "股票" in ft:
        return "stock"
    return "other"


def _passes_risk_horizon_liquidity(
    ft: str,
    risk: Risk,
    horizon: Horizon,
    liquidity: Liquidity,
) -> tuple[bool, list[str]]:
    """返回 (是否入选, 命中的规则说明)."""
    reasons: list[str] = []
    bucket = _type_bucket(ft)

    # 流动性：高流动性时，保守/稳健 + 短期 才明显排斥权益；进取型短期仍可考虑股票（T+1）
    if liquidity == "high":
        if bucket == "money" or "短" in (ft or "") or "中短" in (ft or ""):
            reasons.append("符合「高流动性」：偏货币或短久期债类")
        elif (
            bucket in ("stock", "qdii")
            and risk in ("conservative", "stable")
            and horizon == "short"
            or bucket == "bond"
            and "长" in (ft or "")
            and horizon == "short"
        ):
            return False, []

    if liquidity == "low" and bucket == "money" and not (risk == "conservative" and horizon == "short"):
        return False, []

    # 风险偏好 × 期限（简化为类型约束）
    if risk == "conservative":
        if bucket not in ("money", "bond"):
            return False, []
        reasons.append("保守型：以货币、债券等波动较低品类为主")
        if horizon == "short" and bucket != "money" and "短" not in (ft or "") and "中短" not in (ft or ""):
            # 短期保守仍允许中短债
            pass

    elif risk == "stable":
        if bucket == "money" and horizon == "long":
            return False, []
        if bucket in ("money",) and horizon != "short":
            reasons.append("稳健型：可接受债类与部分固收+策略")
        if bucket not in ("money", "bond", "mixed", "index"):
            return False, []
        if bucket == "stock":
            return False, []
        reasons.append("稳健型：侧重债类、混合与指数")

    elif risk == "balanced":
        if bucket in ("money",) and horizon == "long":
            return False, []
        if bucket not in ("mixed", "index", "bond", "stock", "qdii"):
            return False, []
        reasons.append("平衡型：股债搭配、宽基或部分 QDII")

    elif risk == "aggressive":
        if bucket in ("money",) and horizon != "short":
            return False, []
        if bucket not in ("mixed", "index", "stock", "qdii"):
            return False, []
        reasons.append("进取型：可含权益、行业与 QDII")

    else:  # radical
        if bucket in ("money", "bond") and horizon == "long":
            return False, []
        if bucket not in ("mixed", "index", "stock", "qdii"):
            return False, []
        reasons.append("激进型：可接受较高波动与主题/境外品种")

    # 投资期限微调
    if horizon == "short":
        if bucket in ("stock", "qdii") and risk in ("conservative", "stable"):
            return False, []
        reasons.append("短期持有：已弱化长周期权益品种权重逻辑")
    elif horizon == "long":
        reasons.append("中长期视角：更关注资产配置与复利")

    return True, reasons


def _theme_match(name: str, themes: list[str]) -> tuple[bool, list[str]]:
    if not themes:
        return True, []
    name_u = name or ""
    hit_reasons: list[str] = []
    for tid in themes:
        kws = THEME_KEYWORDS.get(tid)
        if not kws:
            continue
        if any(k in name_u for k in kws):
            hit_reasons.append(f"命中主题：{tid}")
    if not hit_reasons:
        return False, []
    return True, hit_reasons


def _dedupe_reasons(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out[:5]


def recommend_from_list(
    funds_data: list[Any],
    req: FundRecommendRequest,
) -> FundRecommendResponse:
    """从原始列表筛选并抽样。"""
    disclaimer = (
        "本推荐基于基金类型与名称关键词的规则筛选，非业绩排名或持牌投顾建议；"
        "投资有风险，请结合招募说明书与个人情况决策。"
    )

    candidates: list[RecommendedFund] = []
    themes = [t for t in req.themes if t]

    for fund in funds_data:
        if len(fund) < 4:
            continue
        code, name, ft = fund[0], fund[2], fund[3]
        ok, r1 = _passes_risk_horizon_liquidity(ft, req.risk_level, req.horizon, req.liquidity)
        if not ok:
            continue
        if themes:
            ok2, r2 = _theme_match(name, themes)
            if not ok2:
                continue
            reasons = _dedupe_reasons(r1 + r2)
        else:
            reasons = _dedupe_reasons(r1)
            if not reasons:
                reasons = ["符合当前风险与期限组合"]

        candidates.append(
            RecommendedFund(
                code=code,
                name=name,
                type=ft or "",
                reasons=reasons,
            )
        )

    # 确定性抽样：同一请求参数在同一天结果稳定，换参数会变
    seed = _hash_seed(
        (
            str(req.risk_level),
            str(req.horizon),
            str(req.liquidity),
            ",".join(sorted(themes)),
            str(date_ordinal()),
        )
    )
    if len(candidates) > req.limit:
        # 按 seed 打散后取前 limit 个
        scored = sorted(
            enumerate(candidates),
            key=lambda x: (_hash_seed((str(seed), x[1].code, str(x[0]))), x[0]),
        )
        candidates = [x[1] for x in scored[: req.limit]]
    else:
        candidates = candidates[: req.limit]

    # 选了主题但无匹配：自动去掉主题重试一次
    if not candidates and themes:
        req_relaxed = req.model_copy(update={"themes": []})
        relaxed = recommend_from_list(funds_data, req_relaxed)
        if relaxed.funds:
            relaxed.profile_summary = "在所选主题下暂无匹配，已自动放宽为「不限主题」。" + relaxed.profile_summary
        return relaxed

    summary = _profile_summary(req)
    if not candidates:
        summary += "（当前条件可能过严，可尝试放宽风险等级、取消部分主题或调整期限。）"

    return FundRecommendResponse(
        funds=candidates,
        profile_summary=summary,
        disclaimer=disclaimer,
    )


def date_ordinal() -> int:
    from datetime import date

    return date.today().toordinal()


def _profile_summary(req: FundRecommendRequest) -> str:
    risk_map = {
        "conservative": "保守",
        "stable": "稳健",
        "balanced": "平衡",
        "aggressive": "进取",
        "radical": "激进",
    }
    hz_map = {"short": "短期", "medium": "中期", "long": "长期"}
    liq_map = {"high": "高流动性（偏活钱管理）", "medium": "中等流动性", "low": "流动性要求低（可长期持有）"}
    parts = [
        f"风险取向：{risk_map.get(req.risk_level, req.risk_level)}",
        f"投资期限：{hz_map.get(req.horizon, req.horizon)}",
        f"流动性：{liq_map.get(req.liquidity, req.liquidity)}",
    ]
    if req.themes:
        parts.append(f"关注主题：{', '.join(req.themes)}")
    else:
        parts.append("未限定行业主题（全类型候选中筛选）")
    return "；".join(parts) + "。"
