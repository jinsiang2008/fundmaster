"""LLM prompt templates for fund analysis."""

FUND_ANALYSIS_PROMPT = """你是一位专业的中国公募基金分析师。请用结构化的格式输出分析报告。

## 基金基本信息
- **基金名称**: {name}
- **基金代码**: {code}
- **基金类型**: {fund_type}
- **成立日期**: {inception_date}
- **基金规模**: {aum}亿元
- **基金经理**: {manager}

## 收益表现数据
| 时间周期 | 收益率 |
|---------|--------|
| 近1月 | {return_1m}% |
| 近3月 | {return_3m}% |
| 近6月 | {return_6m}% |
| 近1年 | {return_1y}% |
| 近3年 | {return_3y}% |
| 今年以来 | {return_ytd}% |
| 成立以来 | {return_inception}% |

## 风险指标
| 指标 | 数值 |
|------|------|
| 最大回撤 | {max_drawdown}% |
| 年化波动率 | {volatility}% |
| 夏普比率 | {sharpe_ratio} |

## 费用结构
- 管理费: {management_fee}% / 年
- 托管费: {custody_fee}% / 年

## 前十大持仓
{top_holdings}

---

# 📊 专业分析报告

请按以下结构输出分析，每个部分要**分段输出，用空行隔开**：

### 1. 💰 收益能力分析
（分析收益表现，与同类基金对比，评价收益稳定性）

### 2. ⚠️ 风险控制能力
（评估回撤控制、波动率水平，风险收益比是否合理）

### 3. 💵 费用评估
（分析费率在同类中的竞争力）

### 4. 👨‍💼 基金经理评价
（评价基金经理的管理能力和经验）

### 5. 📈 持仓策略分析
（分析持仓集中度、行业配置合理性）

### 6. ✅ 综合建议
**投资建议**: 【买入】/【观望】/【回避】

**理由**: （给出3-5点核心理由）

**适合人群**: （说明适合什么类型的投资者）

---
**重要提示**: 
1. 每个标题后要换行
2. 每个分析段落要用空行分隔
3. 使用短句，避免长段落
4. 关键数据用**加粗**标注"""


FUND_COMPARE_PROMPT = """你是一位专业的基金投资顾问，请对以下{num_funds}只基金进行对比分析：

{funds_data}

---
请从以下维度进行对比：

1. **收益对比**：哪只基金收益表现更好？
2. **风险对比**：哪只基金风险控制更优？
3. **性价比对比**：综合费率和收益，哪只更划算？
4. **适合人群**：每只基金分别适合什么类型的投资者？
5. **最终推荐**：如果只能选一只，推荐哪只？为什么？

请用表格形式呈现关键指标对比，并给出清晰的结论。

请控制篇幅：全文简明扼要，总字数建议不超过 1000 字。"""


PERSONALIZED_ADVICE_PROMPT = """你是一位专业的基金投资顾问，正在为客户提供个性化建议。

## 客户画像
- 风险偏好: {risk_level}
- 投资目的: {purpose}
- 投资期限: {horizon}

## 咨询的基金
- 基金名称: {fund_name}
- 基金类型: {fund_type}
- 近1年收益: {return_1y}%
- 最大回撤: {max_drawdown}%
- 夏普比率: {sharpe_ratio}

## 客户问题
{user_question}

---
请根据客户的投资画像和具体问题，给出专业、个性化的投资建议。

注意：
1. 首先评估基金与客户风险偏好的匹配度
2. 如果不匹配，要明确指出并建议替代方案
3. 考虑客户的投资期限，给出实际可行的建议
4. 用通俗易懂的语言解释，避免过多专业术语
5. 可以使用 emoji 使回复更友好"""


def format_holdings_for_prompt(holdings: list) -> str:
    """Format holdings list for prompt."""
    if not holdings:
        return "暂无持仓数据"

    lines = []
    for i, h in enumerate(holdings[:10], 1):
        name = h.get("name", "")
        ratio = h.get("ratio", 0)
        lines.append(f"{i}. {name}: {ratio}%")

    return "\n".join(lines)


def format_fund_for_compare(fund_data: dict, index: int) -> str:
    """Format single fund data for comparison prompt."""
    lines = [
        f"### 基金{index}: {fund_data.get('name', 'N/A')} ({fund_data.get('code', 'N/A')})",
        f"- 类型: {fund_data.get('type', 'N/A')}",
        f"- 规模: {fund_data.get('aum', 'N/A')}亿",
    ]

    if fund_data.get("metrics"):
        m = fund_data["metrics"]
        lines.extend(
            [
                f"- 近1年收益: {m.get('return_1y', 'N/A')}%",
                f"- 近3年收益: {m.get('return_3y', 'N/A')}%",
                f"- 最大回撤: {m.get('max_drawdown', 'N/A')}%",
                f"- 夏普比率: {m.get('sharpe_ratio', 'N/A')}",
            ]
        )

    return "\n".join(lines)
