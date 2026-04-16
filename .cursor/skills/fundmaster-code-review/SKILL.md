---
name: fundmaster-code-review
description: FundMaster 代码审查清单。完成功能开发后使用此 skill 进行自查。
---

# FundMaster Code Review Checklist

## 分层检查
- [ ] Router 只做请求解析和响应组装，业务逻辑在 services
- [ ] Service 不直接 import router 或 main
- [ ] Schema 变更同步更新了前端 types/
- [ ] 新增 API 端点有对应的 Pydantic schema

## 后端检查
- [ ] 函数有完整类型标注（参数 + 返回值）
- [ ] 数据抓取通过 DataFetcher，未直接调 fetcher
- [ ] LLM 调用通过 llm_service，使用正确的 task_type
- [ ] 异常处理使用 HTTPException + 明确的 status_code
- [ ] 无硬编码配置值（应通过 Settings）
- [ ] 无 .env / API Key 泄露风险

## 前端检查
- [ ] API 调用通过 api/client.ts
- [ ] 数据查询使用 TanStack Query hooks
- [ ] 类型定义在 types/ 目录
- [ ] 使用 Ant Design 6 API（非 antd5 已废弃的 API）
- [ ] 无内联 interface 定义（应提取到 types/）

## 已知问题（审查时注意）
- AKShare 兜底在 macOS 上可能失败，确保天天基金路径可用
- SSE 流式需要前端正确处理 ReadableStream
- DeepSeek reasoner 响应较慢，确保有合理的超时和加载状态

## 输出格式
```markdown
### ✅ 通过项
- {检查项}: {简要说明}

### ⚠️ 建议改进
- {检查项}: {具体问题} → {建议修复方式}

### ❌ 必须修复
- {检查项}: {问题} → {修复方式}
```
