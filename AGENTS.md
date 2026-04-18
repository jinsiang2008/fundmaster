# FundMaster Agent Notes

## Multi-Tool Instruction Files
| 工具 | 指令文件 | 说明 |
|------|----------|------|
| Cursor | AGENTS.md + `.cursor/rules/` + `.cursor/skills/` | repo 内指令入口 |
| Codex / Copilot | AGENTS.md | 原生读取 |
| Claude Code | CLAUDE.md → `@AGENTS.md` | 继承本文件 |
| OpenClaw | AGENTS.md + `docs/memory.md` | repo 事实在这里；用户私有 managed skills 在仓库外维护 |

AGENTS.md 是 **repo-scoped single source of truth**。用户私有的远端 OpenClaw managed skills 不在本仓库中维护。

## Quick Orientation
- **项目**: AI 驱动的中国公募基金智能分析平台
- **语言偏好**: 代码注释/变量用英文，UI/用户可见文案用中文
- **技术栈**: FastAPI (Python 3.11) + Vite/React 19 (TypeScript) + Ant Design 6
- **当前能力**: 基金搜索、净值/持仓/指标、AI 分析报告、会话问答、多基对比、定投模拟、规则化选基、前端本地 watchlist/recent

## Architecture
```
fundmaster/
├── backend/           # FastAPI API 服务（→ backend/README.md）
│   └── app/
│       ├── main.py         # 入口，注册路由
│       ├── config.py       # 配置 + LLM 模型路由
│       ├── routers/        # API 端点（funds, analysis, compare, chat）
│       ├── services/       # 业务逻辑（抓取、指标、LLM、推荐、对话）
│       └── schemas/        # Pydantic 请求/响应模型
├── frontend/          # Vite + React SPA（→ frontend/README.md）
│   └── src/
│       ├── pages/          # 页面组件
│       ├── components/     # 共享组件
│       ├── hooks/          # 查询/状态 hooks
│       ├── api/            # Axios + SSE 客户端
│       ├── utils/storage.ts# watchlist / recent 本地持久化
│       └── types/          # TypeScript 类型
├── scripts/           # 局域网远端部署脚本等运维入口
├── docker-compose*.yml
└── docs/memory.md     # 决策、坑点、运行事实
```

依赖方向: `config → schemas → services → routers → main`。前端统一走 `api/client.ts`，不要在组件里直接请求外部 API。

## Key Data Context
- **数据源**: 天天基金为主，AKShare 为备用；AKShare 在 macOS 上仍有兼容性风险
- **LLM**: 默认 `deepseek`，支持 `qwen` / `openai` 切换
- **模型路由**: `deep_analysis` 走 reason；`compare_funds` 当前显式走 fast，避免对比接口超时
- **用户资产不落库**: 后端不保存用户真实持仓；前端只保存 watchlist/recent，组合/调仓分析依赖外部输入或仓库外私有 skill
- **流式输出**: 分析报告与对话均支持 SSE

## Operational Context
- V1 无数据库，所有基金数据实时抓取
- 生产部署: `docker-compose.prod.yml` + Nginx 同域反代 `/api` → backend:8000
- 另有局域网远端 macOS 运行方式: `scripts/deploy-remote-192.sh`（rsync + venv + `vite preview`）
- 当前运行事实、远端 IP、OpenClaw managed skill 状态见 `docs/memory.md`
- 环境变量入口: `backend/.env`（开发/局域网运行），`deploy.env`（Docker 生产）

## Agent Behavior
- **安全红线**: 绝不提交 `.env`、API Key、密码、用户私有运行时路径到 Git
- **依赖管理**: 后端用 `pip + requirements.txt`，前端用 `npm + package.json`
- **提交前检查**:
  - `pre-commit run --all-files`
  - `cd backend && ruff check app/ && ruff format --check app/`
  - `cd frontend && npm run lint && npm run build`
- **不要**修改 `config.py` 中的 `TASK_MODEL_MAPPING`，除非明确要求调整模型路由
- **不要**在前端直接调用外部 API，所有数据请求通过后端代理
- **不要**假设 repo 内存在 OpenClaw/FundMaster 调仓 skill；那是用户私有的远端 managed skill，repo 只维护项目事实和命令入口
