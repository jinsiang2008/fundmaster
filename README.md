# FundMaster 基金分析助手

AI 驱动的中国公募基金分析平台，帮助投资者做出更明智的投资决策。

## 功能特性

- 🔍 **基金搜索** - 支持按名称或代码搜索中国公募基金
- 📊 **数据分析** - 自动计算收益率、最大回撤、夏普比率等核心指标
- 🤖 **AI 分析报告** - 使用 DeepSeek 生成专业的基金分析报告
- 💬 **个性化对话** - 根据用户投资画像提供定制化建议
- ⚖️ **多基金对比** - 支持 2-5 只基金同时对比分析
- 📈 **实时估值** - 交易时段获取基金实时估值

## 技术栈

### 后端
- **FastAPI** - 高性能 Python API 框架
- **AKShare** - 中国金融数据获取
- **DeepSeek API** - AI 分析（支持 chat + reasoner 双模型）
- **Pandas/NumPy** - 数据分析

### 前端
- **Vite + React 18** - 现代前端框架
- **TypeScript** - 类型安全
- **Ant Design** - UI 组件库
- **ECharts** - 图表可视化
- **TanStack Query** - 数据获取

## 快速开始

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 启动服务
uvicorn app.main:app --reload
```

API 文档: http://localhost:8000/docs

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问: http://localhost:5173

## API 端点

### 基金数据
- `GET /api/funds/search?q={query}` - 搜索基金
- `GET /api/funds/{code}` - 基金详情
- `GET /api/funds/{code}/nav?period=1y` - 历史净值
- `GET /api/funds/{code}/holdings` - 持仓数据
- `GET /api/funds/{code}/metrics` - 业绩指标
- `GET /api/funds/{code}/realtime` - 实时估值

### AI 分析
- `GET /api/funds/{code}/analysis` - AI 分析报告
- `GET /api/funds/{code}/analysis/stream` - 流式分析报告

### 多基金对比
- `POST /api/compare` - 多基金对比分析

### 对话交互
- `POST /api/chat/sessions` - 创建对话会话
- `POST /api/chat/messages` - 发送消息
- `POST /api/chat/messages/stream` - 流式消息

## 智能模型路由

系统根据任务复杂度自动选择模型：

| 任务类型 | 模型 | 说明 |
|----------|------|------|
| 简单问答 | deepseek-chat | 快速响应 |
| 深度分析 | deepseek-reasoner | 深度推理 |
| 基金对比 | deepseek-reasoner | 多维度分析 |
| 投资建议 | deepseek-reasoner | 复杂决策 |

## 项目结构

```
fundmaster/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 应用入口
│   │   ├── config.py       # 配置管理
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务逻辑
│   │   └── schemas/        # 数据模型
│   └── requirements.txt
│
├── frontend/               # React 前端
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── hooks/         # 自定义 Hooks
│   │   └── api/           # API 客户端
│   └── package.json
│
└── README.md
```

## License

MIT
