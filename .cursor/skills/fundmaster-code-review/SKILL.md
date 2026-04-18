---
name: fundmaster-code-review
description: Use when reviewing FundMaster 代码变更、后端 API/前端页面/部署脚本/项目文档更新，或用户明确要求进行 code review。
---

# FundMaster Code Review Checklist

## 分层检查
- [ ] Router 只做请求解析和响应组装，业务逻辑在 services
- [ ] Service 不直接 import router 或 main
- [ ] Schema 变更同步更新了前端 types/
- [ ] 新增 API 端点有对应的 Pydantic schema
- [ ] 改动 API 面、部署方式或能力边界时，同步更新了 `AGENTS.md` / `CLAUDE.md` / `docs/memory.md`

## 后端检查
- [ ] 函数有完整类型标注（参数 + 返回值）
- [ ] 数据抓取通过 DataFetcher，未直接调 fetcher
- [ ] LLM 调用通过 llm_service，使用正确的 task_type
- [ ] 未无意修改 `config.py` 里的 `TASK_MODEL_MAPPING`
- [ ] 异常处理使用 HTTPException + 明确的 status_code
- [ ] 无硬编码配置值（应通过 Settings）
- [ ] 未假设 `FundBasicInfo.type` 一定有值；若做分类逻辑，已考虑 fallback
- [ ] 无 .env / API Key 泄露风险

## 前端检查
- [ ] API 调用通过 api/client.ts
- [ ] 数据查询使用 TanStack Query hooks
- [ ] 类型定义在 types/ 目录
- [ ] 使用 Ant Design 6 API（非 antd5 已废弃的 API）
- [ ] 无内联 interface 定义（应提取到 types/）
- [ ] `watchlist/recent` 仍只是本地列表，不被误当成真实用户持仓/组合

## 运维/运行时检查
- [ ] 若改了局域网远端运行路径，已考虑 `VITE_API_URL` / `CORS_ORIGINS` / `--noproxy '*'`
- [ ] 若改了远端前端启动方式，已考虑非交互 shell 下 `npx` / PATH 问题

## 已知问题（review 时注意）
- AKShare 兜底在 macOS 上可能失败，确保天天基金路径可用
- SSE 流式需要前端正确处理 ReadableStream
- DeepSeek reasoner 响应较慢，确保有合理的超时和加载状态
- 当前自动化测试不足，很多结论仍需靠 lint/build/手工验证支撑

## 输出格式
```markdown
### ✅ 通过项
- {检查项}: {简要说明}

### ⚠️ 建议改进
- {检查项}: {具体问题} → {建议修复方式}

### ❌ 必须修复
- {检查项}: {问题} → {修复方式}
```
