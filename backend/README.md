# Backend — FastAPI API 服务

## 目录结构
```
app/
├── main.py              # 入口，创建 FastAPI app，注册路由
├── config.py            # 配置中心：Settings、LLM 模型路由、provider 配置
├── routers/             # API 路由层
│   ├── funds.py         # /api/funds — 搜索、详情、净值、持仓、指标、实时估值
│   ├── analysis.py      # /api/funds/{code}/analysis — AI 分析报告（含 SSE 流式）
│   ├── compare.py       # /api/compare — 多基金对比
│   └── chat.py          # /api/chat — 会话式对话（含 SSE 流式）
├── services/            # 业务逻辑层
│   ├── data_fetcher.py  # 统一数据抓取入口（天天基金优先，AKShare 兜底）
│   ├── ttfund_fetcher.py      # 天天基金核心抓取
│   ├── ttfund_enhanced.py     # 天天基金增强（费率、经理等）
│   ├── akshare_fetcher.py     # AKShare 备用数据源
│   ├── eastmoney_fees.py      # 东方财富费率查询
│   ├── metrics.py             # 金融指标计算（年化、回撤、夏普、波动率）
│   ├── risk_labels.py         # 风险等级标注
│   ├── llm_service.py         # LLM 调用封装（OpenAI 兼容客户端）
│   ├── llm_prompts.py         # Prompt 模板管理
│   ├── chat_service.py        # 会话管理 + 对话逻辑
│   ├── dca_simulator.py       # 定投模拟计算
│   └── fund_recommender.py    # 基金推荐逻辑
└── schemas/             # Pydantic 数据模型
    ├── fund.py          # 基金相关请求/响应类型
    └── chat.py          # 对话相关请求/响应类型
```

## 分层规则
`config → schemas → services → routers → main`，禁止反向依赖。

## 本地开发
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 填入 DEEPSEEK_API_KEY
uvicorn app.main:app --reload
```

API 文档: http://localhost:8000/docs

## 关键约定
- 所有外部数据抓取必须通过 `DataFetcher`，不要在 router 直接调用 fetcher
- LLM 调用必须通过 `llm_service.py`，使用 `TASK_MODEL_MAPPING` 路由模型
- 新增 API 端点需要在 `schemas/` 中定义对应的 Pydantic 模型
