# FundMaster Agent Notes

## Multi-Tool Instruction Files
| 工具 | 指令文件 | 说明 |
|------|----------|------|
| Cursor | AGENTS.md + .cursor/rules/ | 本文件 + glob 规则 |
| Codex / Copilot | AGENTS.md | 原生读取 |
| Claude Code | CLAUDE.md → @import AGENTS.md | import 本文件 |

AGENTS.md 是 single source of truth。

## Quick Orientation
- **项目**: AI 驱动的中国公募基金智能分析平台
- **语言偏好**: 代码注释/变量用英文，用户界面/文案用中文
- **技术栈**: FastAPI (Python 3.11) + Vite/React 19 (TypeScript) + Ant Design 6

## Architecture

```
fundmaster/
├── backend/           # FastAPI API 服务（→ backend/README.md）
│   └── app/
│       ├── main.py         # 入口，注册路由
│       ├── config.py       # 配置 + LLM 模型路由
│       ├── routers/        # API 端点（funds, analysis, compare, chat）
│       ├── services/       # 业务逻辑（数据抓取、指标计算、LLM、对话）
│       └── schemas/        # Pydantic 请求/响应模型
├── frontend/          # Vite + React SPA（→ frontend/README.md）
│   └── src/
│       ├── pages/          # 页面组件（Home, FundDetail, Compare...）
│       ├── components/     # 共享组件（ChatPanel, FundSearch...）
│       ├── hooks/          # 自定义 hooks（useChat, useFund...）
│       ├── api/            # Axios 封装 + 流式请求
│       └── types/          # TypeScript 类型定义
├── docker-compose.yml      # 开发环境编排
├── docker-compose.prod.yml # 生产环境编排（Nginx 同域反代）
└── docs/memory.md          # 项目记忆 & 决策记录
```

依赖方向: `config → schemas → services → routers → main`

## Key Data Context
- **数据源**: 天天基金（主） + AKShare（备，当前 macOS 兼容性问题暂禁用）
- **LLM**: DeepSeek 为默认 provider，支持 qwen / openai 切换
- **模型路由**: fast (deepseek-chat) 用于简单任务，reason (deepseek-reasoner) 用于深度分析
- **流式输出**: 分析报告和对话均支持 SSE 流式

## Operational Context
- 无数据库（V1），所有数据实时抓取
- 生产部署: `docker-compose.prod.yml` + Nginx 同域反代 `/api` → backend:8000
- 环境变量: `backend/.env`（API Key），`deploy.env`（部署配置）
- 详见 [docs/memory.md](docs/memory.md)

## Agent Behavior
- **安全红线**: 绝不提交 `.env`、API Key、密码到 Git
- **依赖管理**: 后端用 `pip + requirements.txt`，前端用 `npm + package.json`
- **提交前检查**:
  - 后端: `cd backend && ruff check app/`
  - 前端: `cd frontend && npm run lint && npm run build`
- **不要**修改 `config.py` 中的 `TASK_MODEL_MAPPING` 除非明确要求
- **不要**在前端直接调用外部 API，所有数据请求通过后端代理
