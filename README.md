# 🏦 FundMaster 基金分析助手

<div align="center">

AI 驱动的中国公募基金智能分析平台

[功能特性](#功能特性) • [技术架构](#技术架构) • [快速开始](#快速开始) • [API 文档](#api-文档)

</div>

---

## 📋 目录

- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [使用说明](#使用说明)
- [API 文档](#api-文档)
- [智能模型路由](#智能模型路由)
- [数据源说明](#数据源说明)
- [开发指南](#开发指南)
- [常见问题](#常见问题)

## ✨ 功能特性

### 核心功能
- 🔍 **智能搜索** - 支持基金名称或代码模糊搜索，覆盖全部中国公募基金
- 📊 **专业分析** - 自动计算年化收益、最大回撤、夏普比率、波动率等核心指标
- 🤖 **AI 分析报告** - 使用 DeepSeek Reasoner 深度推理生成专业分析报告
- 💬 **个性化对话** - 基于用户投资画像（风险偏好、投资目的、期限）提供定制建议
- ⚖️ **多基金对比** - 支持 2-5 只基金同时对比，雷达图可视化
- 📈 **实时估值** - 交易时段获取基金盘中估算净值

### 特色功能
- 🎯 **智能模型路由** - 根据任务复杂度自动选择 `deepseek-chat` (快) 或 `deepseek-reasoner` (强)
- 🔄 **双数据源容错** - 天天基金 + AKShare 互为备份，确保数据可用性
- 💡 **流式输出** - 打字机效果展示 AI 分析过程
- 👤 **用户画像** - 支持保守型、稳健型、平衡型、进取型、激进型投资者分类

## 🛠 技术架构

### 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 运行环境 |
| FastAPI | 0.115+ | 高性能 API 框架 |
| DeepSeek API | - | AI 智能分析（支持双模型） |
| 天天基金接口 | - | 主数据源（稳定） |
| AKShare | 1.18+ | 备用数据源 |
| Pandas/NumPy | - | 金融指标计算 |

### 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18 | UI 框架 |
| Vite | 7+ | 构建工具 |
| TypeScript | 5.9+ | 类型安全 |
| Ant Design | 6+ | UI 组件库 |
| ECharts | 6+ | 图表可视化 |
| TanStack Query | 5+ | 数据状态管理 |

## 🏗 系统架构

```
用户 → React 前端 → FastAPI 后端 → 数据源 (天天基金/AKShare)
                              ↓
                         LLM 服务 (DeepSeek)
                         ├─ chat (简单问答)
                         └─ reasoner (深度分析)
```

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- DeepSeek API Key（[获取地址](https://platform.deepseek.com/)）

### 1️⃣ 克隆项目

```bash
git clone <your-repo>
cd fundmaster
```

### 2️⃣ 后端设置

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# ⚠️ 重要：编辑 .env 文件，填入真实的 API Key
# DEEPSEEK_API_KEY=sk-your-actual-key-here

# 启动服务
uvicorn app.main:app --reload
```

✅ 后端启动成功后访问：http://localhost:8000/docs

### 3️⃣ 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量（可选，默认使用代理）
cp .env.example .env

# 启动开发服务器
npm run dev
```

✅ 前端启动成功后访问：http://localhost:5173

## 📖 使用说明

### 基金搜索与分析
1. 在首页搜索框输入基金名称或代码（如"易方达"或"110011"）
2. 点击搜索结果进入基金详情页
3. 查看净值走势图、持仓数据
4. 点击"生成分析报告"获取 AI 深度分析

### 个性化对话
1. 在基金详情页切换到"智能问答"标签
2. 点击"设置投资偏好"配置您的风险偏好、投资目的和期限
3. 输入问题，如：
   - "我是稳健型投资者，这只基金适合我吗？"
   - "这只基金的风险有多大？"
   - "有没有类似但更稳健的基金推荐？"

### 多基金对比
1. 点击首页"多基对比"
2. 搜索并添加 2-5 只基金
3. 点击"开始对比分析"
4. 查看雷达图、指标对比表和 AI 综合建议

## 📡 API 文档

### 基金数据接口
```
GET  /api/funds/search?q={query}&limit=20
     搜索基金，支持名称或代码模糊匹配
     
GET  /api/funds/{code}
     获取基金基本信息（类型、规模、经理、费率等）
     
GET  /api/funds/{code}/nav?period={1m|3m|6m|1y|3y|5y|max}
     获取历史净值数据
     
GET  /api/funds/{code}/holdings
     获取前十大持仓数据
     
GET  /api/funds/{code}/metrics?period={1y|3y|5y}
     获取业绩指标（收益率、回撤、夏普比率等）
     
GET  /api/funds/{code}/realtime
     获取实时估值（交易时段）
```

### AI 分析接口
```
GET  /api/funds/{code}/analysis
     获取 AI 分析报告（使用 deepseek-reasoner）
     
GET  /api/funds/{code}/analysis/stream
     获取流式分析报告（SSE）
```

### 多基金对比
```
POST /api/compare
     Body: { "fund_codes": ["110011", "000961"] }
     多基金对比分析，返回雷达图数据和 AI 建议
```

### 对话交互接口
```
POST /api/chat/sessions
     Body: { "fund_code": "110011" }
     创建对话会话
     
POST /api/chat/messages/stream
     Body: { "session_id": "xxx", "message": "问题", "user_profile": {...} }
     发送消息（流式响应）
     
GET  /api/chat/sessions/{session_id}/messages
     获取对话历史
```

完整 API 文档：启动后端后访问 http://localhost:8000/docs

## 🧠 智能模型路由

系统根据任务复杂度自动选择最合适的模型，优化成本和效果：

| 任务类型 | 模型 | 特点 | 应用场景 |
|----------|------|------|----------|
| 简单问答 | `deepseek-chat` | 快速、低成本 | "基金成立时间？"、"费率多少？" |
| 意图识别 | `deepseek-chat` | 快速分类 | 判断用户想做什么 |
| **深度分析** | `deepseek-reasoner` | 深度推理 | 生成专业分析报告 |
| **基金对比** | `deepseek-reasoner` | 多维度权衡 | 对比多只基金并推荐 |
| **投资建议** | `deepseek-reasoner` | 复杂决策 | 基于用户画像的个性化建议 |

**成本优化效果**：混合使用可节省约 50% 的 API 调用成本

## 📊 数据源说明

### 主数据源：天天基金网
- **搜索功能**: 全部公募基金列表
- **基金详情**: 名称、类型、公司、经理、规模等
- **历史净值**: 从成立至今的完整净值数据
- **实时估值**: 交易时段的盘中估算净值
- **持仓数据**: 前十大股票持仓
- **优势**: 稳定、数据全面、更新及时

### 备用数据源：AKShare
- **状态**: 目前因 libmini_racer 库在 macOS 上崩溃而暂时禁用
- **用途**: 作为天天基金的补充和备份
- **计划**: 未来可能切换到其他稳定的数据源

## 📁 项目结构

```
fundmaster/
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── main.py              # 应用入口，CORS 配置
│   │   ├── config.py            # 配置管理，模型路由配置
│   │   ├── routers/             # API 路由
│   │   │   ├── funds.py         # 基金数据 API
│   │   │   ├── analysis.py      # AI 分析 API
│   │   │   ├── compare.py       # 多基金对比 API
│   │   │   └── chat.py          # 对话交互 API
│   │   ├── services/            # 业务逻辑层
│   │   │   ├── data_fetcher.py  # 统一数据获取（含 failover）
│   │   │   ├── ttfund_fetcher.py   # 天天基金数据源
│   │   │   ├── ttfund_enhanced.py  # 增强的天天基金解析
│   │   │   ├── akshare_fetcher.py  # AKShare 数据源（已禁用）
│   │   │   ├── metrics.py          # 金融指标计算
│   │   │   ├── llm_service.py      # LLM 服务（智能路由）
│   │   │   ├── llm_prompts.py      # Prompt 模板
│   │   │   └── chat_service.py     # 对话会话管理
│   │   └── schemas/             # Pydantic 数据模型
│   │       ├── fund.py          # 基金相关模型
│   │       └── chat.py          # 对话相关模型
│   ├── requirements.txt         # Python 依赖
│   ├── .env.example            # 环境变量模板
│   └── Dockerfile              # Docker 配置
│
├── frontend/                    # Vite + React 前端
│   ├── src/
│   │   ├── pages/              # 页面组件
│   │   │   ├── Home.tsx        # 首页（搜索）
│   │   │   ├── FundDetail.tsx  # 基金详情页
│   │   │   └── Compare.tsx     # 对比页
│   │   ├── components/         # 可复用组件
│   │   │   ├── FundSearch.tsx
│   │   │   ├── FundCard.tsx
│   │   │   ├── PerformanceChart.tsx
│   │   │   ├── HoldingsTable.tsx
│   │   │   ├── AnalysisReport.tsx
│   │   │   ├── ChatPanel.tsx
│   │   │   ├── UserProfileForm.tsx
│   │   │   └── CompareRadar.tsx
│   │   ├── hooks/              # 自定义 Hooks
│   │   │   ├── useFund.ts
│   │   │   └── useChat.ts
│   │   ├── api/                # API 客户端
│   │   │   └── client.ts
│   │   ├── types/              # TypeScript 类型
│   │   │   ├── fund.ts
│   │   │   └── chat.ts
│   │   └── styles/             # 样式文件
│   │       └── markdown.css
│   ├── package.json
│   ├── .env.example
│   └── Dockerfile
│
├── .gitignore                   # Git 忽略配置
├── docker-compose.yml          # Docker Compose 配置
└── README.md                   # 本文件
```

## 🎯 快速开始

### 方式一：本地开发（推荐）

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# ⚠️ 编辑 .env 文件，填入 DeepSeek API Key
nano .env  # 或使用其他编辑器

# 启动服务
uvicorn app.main:app --reload
```

✅ 启动成功：http://localhost:8000

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

✅ 启动成功：http://localhost:5173

### 方式二：Docker 部署

```bash
# 配置环境变量
echo "DEEPSEEK_API_KEY=your-key" > .env

# 启动所有服务
docker-compose up -d
```

访问：http://localhost:5173
