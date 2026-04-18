# FundMaster Memory

## 产品/功能演进时间线
| 时间 | 里程碑 |
|------|--------|
| V1.0 | 基金搜索、详情数据、AI 深度分析报告、个性化对话、多基金对比 |
| V1.x | 首页 featured funds、前端 watchlist/recent、本地存储、定投模拟、规则化选基 |
| 2026-04 | Harness 刷新：`AGENTS.md` / `CLAUDE.md` / `.cursor/rules` / `docs/memory.md` 对齐；补充局域网远端运行事实 |
| 2026-04 | 远端 OpenClaw managed skill `fundmaster_rebalance` 部署完成，用外部 `portfolio.json` + FundMaster API 做调仓建议 |
| V2.0 (规划中) | 全球市场支持、用户账户系统、持久化组合分析、监控/CI/CD、测试体系 |

## 关键架构决策
| 决策 | 原因 |
|------|------|
| 天天基金为主数据源，AKShare 备用 | 天天基金接口覆盖完整；AKShare 在 macOS 上仍有兼容性/稳定性风险 |
| 双模型路由（fast / reason） | 简单问答与结构化任务走快模型，长文分析走推理模型，平衡延迟与成本 |
| `compare_funds` 当前走 fast 模型 | 输入已是结构化指标，多基对比不值得用 reasoner，避免接口超时 |
| 固定从 `backend/.env` 读取配置 | 避免从错误工作目录启动时读到空配置或其它目录的 `.env` |
| 无数据库（V1） | 当前所有基金数据实时抓取，减少 MVP 架构复杂度 |
| 用户真实持仓不落库 | repo 内后端不保存用户资产；前端只维护 watchlist/recent，调仓分析依赖外部输入 |
| 生产环境走 Nginx 同域反代 | 浏览器统一访问主站，`/api` 转发到后端，减少 CORS 与 SSE 问题 |
| 局域网远端运行单独保留一条 rsync 路径 | 对无 Docker 的远端 macOS，用 `venv + vite preview` 更直接，适合家庭/办公网络环境 |
| OpenClaw managed skill 维持在仓库外 | 用户私有 skill 放远端 `~/.openclaw/skills`，repo 只维护项目事实、命令入口和公共约定 |

## 已解决的坑
| 现象 | 根因 | 修复 |
|------|------|------|
| `.env` 已换 Key 但仍 401 | shell 环境变量覆盖了 `.env`（Pydantic 默认优先级） | `config.py` 加入 `warn_if_deepseek_key_env_overrides_dotenv()`，启动时提示覆盖风险 |
| 首页无数据时白屏 | 数据源接口不稳定或返回空列表 | `DataFetcher` 加入 featured funds 静态兜底 |
| SSE 流式输出被截断 | Nginx 默认 buffering/超时不适合长连接 | `nginx.conf` 设置 `proxy_buffering off` + 长超时 |
| 子路由白屏 | 首页 `path="/"` 与子路由嵌套冲突 | 改为 `<Route index>` + 无 path 布局路由 |
| 本机 `localhost:8000` 健康检查误命中别的服务 | 某无关服务也暴露了 `/health`，仅测 health 不足以识别 FundMaster | agent / skill 探活改为 health + `GET /api/funds/featured?limit=3` 双重校验 |
| 局域网请求远端 71.128 超时 | 开发机存在 `http_proxy=http://127.0.0.1:7890`，内网请求被错误走代理 | 访问局域网服务时使用 `NO_PROXY` 或 `curl --noproxy '*'`；相关脚本已内置 |
| 远端切换网段后前后端打不开 | 远端 IP 从 `192.168.31.170` 变为 `192.168.71.128`，前端 `VITE_API_URL` 和后端 `CORS_ORIGINS` 仍指向旧地址 | 更新远端 `frontend/.env` 与 `backend/.env`，并重新启动 backend/frontend |
| 远端前端服务起不来 | 非交互 shell 下 `npx` 不在 PATH | 启动时显式注入 `/opt/homebrew/bin` 或直接用 `./node_modules/.bin/vite preview` |

## Code Review / Harness Backlog（按优先级）
1. **补自动化测试** — 后端仍无 pytest，前端仍无 vitest/jest；目前回归主要靠手工验证
2. **建设 CI/CD** — 还没有 GitHub Actions 或等价流水线，pre-commit 只在本地生效
3. **统一错误处理** — 部分路由仍以局部 `HTTPException` 为主，缺统一异常处理中间件/响应格式
4. **持续补类型和接口契约** — 后端 service 仍有少量类型信息不完整；前后端 schema/type 对齐仍靠人工约束
5. **README / memory 持续防漂移** — 功能、模型路由、运行事实已经多次变更，文档需要跟随代码更新
6. **明确官方组合分析边界** — 当前调仓能力由仓库外的私有 OpenClaw skill 承载；若后续转正，需要决定是否把组合输入格式和流程并入 repo

## 基础设施现状
| 组件 | 技术 | 状态 | 备注 |
|------|------|------|------|
| 后端 API | FastAPI 0.115 + Python 3.11 | 运行中 | 本地开发 + 局域网远端均可运行 |
| 前端 SPA | Vite 7 + React 19 + TypeScript | 运行中 | `vite preview` 作为局域网远端静态服务 |
| UI 库 | Ant Design 6 | 生产 | 与 React 19 对齐 |
| 数据查询 | TanStack Query 5 | 生产 | 前端查询入口稳定 |
| 图表 | ECharts 6 | 生产 | 净值图 / 对比图 |
| Lint / 格式化 | Ruff + ESLint + pre-commit | 已启用 | 本地可跑，尚未进 CI |
| Docker 生产路径 | Docker Compose + Nginx | 可用 | 同域 `/api` 反代 |
| 局域网远端路径 | rsync + venv + `vite preview` | 当前活跃 | 截至 2026-04-18 当前主机 `192.168.71.128` |
| OpenClaw managed skill | `fundmaster_rebalance` | 当前活跃 | 位于远端 `~/.openclaw/skills/`，不在 repo 内 |
| CI/CD | 无 | 待建设 | |
| 自动化测试 | 无 | 待建设 | |
| 监控 / 告警 | 无 | 待建设 | |
