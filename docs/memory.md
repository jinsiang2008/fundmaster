# FundMaster Memory

## 产品/功能演进时间线
| 时间 | 里程碑 |
|------|--------|
| V1.0 | 基金搜索、数据展示、AI 深度分析报告、个性化对话、多基金对比 |
| V2.0 (规划中) | 全球市场支持、用户账户系统、定投计算器、组合分析、智能推荐 |

## 关键架构决策
| 决策 | 原因 |
|------|------|
| 天天基金为主数据源，AKShare 备用 | 天天基金接口稳定全面，AKShare 在 macOS 有兼容性问题 |
| 双模型路由（fast/reason） | 简单任务用 chat 模型节省成本和时间，复杂分析用 reasoner |
| 无数据库（V1） | MVP 阶段所有数据实时抓取，减少架构复杂度 |
| Nginx 同域反代 | 生产环境避免 CORS 问题，前端 `/api` 直接代理到后端 |
| OpenAI 兼容客户端 | 支持 DeepSeek/通义千问/OpenAI 无缝切换 |
| 多基对比用 fast 模型 | 输入已为结构化指标，不需要 reasoner 的深度推理，避免耗时过长 |
| React 19 + Ant Design 6 | 最新稳定版，antd6 原生支持 React 19 |

## 已解决的坑
| 现象 | 根因 | 修复 |
|------|------|------|
| `.env` 已换 Key 但仍 401 | shell 环境变量覆盖了 `.env`（Pydantic 默认优先级） | `config.py` 加入 `warn_if_deepseek_key_env_overrides_dotenv()` 启动时检测并提示 |
| 首页无数据时白屏 | 数据源接口不稳定 | `DataFetcher` 加入静态兜底推荐列表 |
| SSE 流式输出被截断 | Nginx 默认 buffer 行为 | `nginx.conf` 设置 `proxy_buffering off` + 长超时 |
| 子路由白屏 | 首页 path="/" 与子路由嵌套冲突 | 改用 `<Route index>` + 无 path 布局路由 |

## Code Review 待改进项（按优先级）
1. **缺少自动化测试** — 后端无 pytest，前端无 vitest/jest
2. **缺少类型标注** — 后端部分 service 函数缺少完整的类型标注
3. **错误处理不一致** — 部分路由缺少统一的异常处理中间件
4. **README 版本信息过期** — 主 README 写 React 18，实际已升级到 React 19
5. **无 CI/CD 流水线** — 无 GitHub Actions 配置

## 基础设施现状
| 组件 | 技术 | 状态 |
|------|------|------|
| 后端 | FastAPI 0.115 + Python 3.11 | 生产 |
| 前端 | Vite 7 + React 19 + TypeScript | 生产 |
| UI 库 | Ant Design 6 | 生产 |
| 数据查询 | TanStack Query 5 | 生产 |
| 图表 | ECharts 6 | 生产 |
| 容器 | Docker Compose (dev + prod) | 生产 |
| 反代 | Nginx alpine | 生产 |
| CI/CD | 无 | 待建设 |
| 测试 | 无 | 待建设 |
| 监控 | 无 | 待建设 |
