# 🏦 FundMaster 基金分析助手

<div align="center">

AI 驱动的中国公募基金智能分析平台

[功能特性](#功能特性) • [快速开始](#快速开始) • [API 文档](#api-文档) • [贡献指南](CONTRIBUTING.md)

</div>

---

## ✨ 功能特性

### 核心功能
- 🔍 **智能搜索** - 支持基金名称或代码模糊搜索，覆盖全部中国公募基金
- 📊 **专业分析** - 自动计算年化收益、最大回撤、夏普比率、波动率等核心指标
- 🤖 **AI 分析报告** - 使用 DeepSeek Reasoner 深度推理生成专业分析报告
- 💬 **个性化对话** - 基于用户投资画像提供定制建议
- ⚖️ **多基金对比** - 支持 2-5 只基金同时对比，雷达图可视化
- 📈 **实时估值** - 交易时段获取基金盘中估算净值

### 特色亮点
- 🎯 **智能模型路由** - 根据任务自动选择 chat(快) 或 reasoner(强)，节省 50% 成本
- 🔄 **双数据源容错** - 天天基金 + AKShare 互为备份
- 💡 **流式输出** - 打字机效果展示 AI 分析过程
- 👤 **用户画像** - 5 种投资者类型（保守/稳健/平衡/进取/激进）

## 🛠 技术栈

### 后端
- **FastAPI** 0.115+ - 高性能 Python API 框架
- **DeepSeek API** - AI 智能分析（双模型）
- **天天基金接口** - 主数据源（稳定）
- **Pandas/NumPy** - 金融指标计算

### 前端
- **Vite + React 18** - 现代前端框架
- **TypeScript** - 类型安全
- **Ant Design 6** - UI 组件库
- **ECharts 6** - 图表可视化
- **TanStack Query** - 数据状态管理

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- DeepSeek API Key（[获取地址](https://platform.deepseek.com/)）

### 1️⃣ 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# ⚠️ 重要：编辑 .env 文件，填入真实的 API Key
# DEEPSEEK_API_KEY=sk-your-actual-key-here
nano .env  # 或使用其他编辑器

# 启动服务
uvicorn app.main:app --reload
```

✅ 后端启动：http://localhost:8000  
📚 API 文档：http://localhost:8000/docs

### 2️⃣ 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量（可选）
cp .env.example .env

# 启动开发服务器
npm run dev
```

✅ 前端启动：http://localhost:5173

### 3️⃣ 开始使用

1. 打开浏览器访问 http://localhost:5173
2. 搜索框输入基金名称（如"易方达"）或代码（如"110011"）
3. 点击搜索结果查看详情
4. 生成 AI 分析报告或开始对话

## 📖 使用说明

### 基金搜索与分析
1. 首页搜索框输入基金名称或代码
2. 点击结果进入详情页
3. 查看净值走势、持仓数据
4. 生成 AI 分析报告

### 个性化对话
1. 详情页切换到"智能问答"标签
2. 设置投资偏好（风险、目的、期限）
3. 提问获取个性化建议

示例问题：
- "我是稳健型投资者，这只基金适合我吗？"
- "这只基金的风险有多大？"
- "有没有类似但更稳健的基金推荐？"

### 多基金对比
1. 首页点击"多基对比"
2. 搜索添加 2-5 只基金
3. 点击"开始对比分析"
4. 查看雷达图和 AI 建议

## 📡 API 文档

### 基金数据
```http
GET  /api/funds/search?q={query}&limit=20
GET  /api/funds/{code}
GET  /api/funds/{code}/nav?period={1m|3m|6m|1y|3y|5y|max}
GET  /api/funds/{code}/holdings
GET  /api/funds/{code}/metrics?period={1y|3y|5y}
GET  /api/funds/{code}/realtime
```

### AI 分析
```http
GET  /api/funds/{code}/analysis
GET  /api/funds/{code}/analysis/stream  # SSE
```

### 对话交互
```http
POST /api/chat/sessions
POST /api/chat/messages/stream
GET  /api/chat/sessions/{id}/messages
```

### 基金对比
```http
POST /api/compare
Body: { "fund_codes": ["110011", "000961"] }
```

完整文档：http://localhost:8000/docs

## 🧠 智能模型路由

| 任务 | 模型 | 说明 |
|------|------|------|
| 简单问答 | deepseek-chat | 快速响应，低成本 |
| 意图识别 | deepseek-chat | 快速分类 |
| **深度分析** | deepseek-reasoner | 深度推理 |
| **基金对比** | deepseek-reasoner | 多维权衡 |
| **投资建议** | deepseek-reasoner | 复杂决策 |

**成本优化**：混合使用节省约 50% API 成本

## 📊 数据源

### 主数据源：天天基金网
- 搜索、详情、历史净值、实时估值、持仓
- 稳定、全面、更新及时

### 备用：AKShare
- 目前因 macOS 兼容性问题暂时禁用
- 后续可能切换到其他数据源

## ❓ 常见问题

<details>
<summary><b>后端启动失败: "API key not found"</b></summary>

```bash
cd backend
cp .env.example .env
nano .env  # 填入 DEEPSEEK_API_KEY
```
</details>

<details>
<summary><b>前端白屏</b></summary>

```bash
cd frontend
rm -rf node_modules/.vite
npm install
npm run dev
```
</details>

<details>
<summary><b>如何获取 DeepSeek API Key?</b></summary>

1. 访问 https://platform.deepseek.com/
2. 注册并创建 API Key
3. 复制到 `backend/.env`
</details>

<details>
<summary><b>搜索无结果</b></summary>

检查：
1. 后端是否正常运行
2. 查看后端日志错误
3. 网络是否能访问天天基金网
</details>

## 🔒 安全说明

⚠️ **重要**：
- ✅ `.env` 文件已被 `.gitignore` 排除
- ✅ `.env.example` 只包含占位符
- ❌ 绝不要将真实 API Key 提交到 Git
- 📘 详见 [SECURITY.md](SECURITY.md)

## 🗺️ 路线图

### V1.0 ✅
- ✅ 基金搜索与数据展示
- ✅ AI 深度分析报告
- ✅ 个性化对话
- ✅ 多基金对比

### V2.0 🚧
- 🔲 全球市场支持
- 🔲 用户账户系统
- 🔲 定投计算器
- 🔲 组合分析
- 🔲 智能推荐

## 👥 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT

## 🙏 致谢

- [天天基金网](http://fund.eastmoney.com/) - 数据来源
- [DeepSeek](https://www.deepseek.com/) - AI 能力
- [FastAPI](https://fastapi.tiangolo.com/) - 后端框架
- [Ant Design](https://ant.design/) - UI 组件

---

<div align="center">
Made with ❤️ for better investment decisions
</div>
