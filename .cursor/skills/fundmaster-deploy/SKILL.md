---
name: fundmaster-deploy
description: FundMaster 部署流程与故障排查。当用户提到部署、上线、Docker、Nginx、生产环境时使用。
---

# FundMaster 部署

## 生产环境事实
- 前后端通过 Docker Compose 编排
- Nginx 做同域反代，`/` 静态资源 + `/api` 转发到 backend:8000
- SSE 流式: Nginx 已关闭 proxy_buffering，超时设置 300s
- 环境变量通过 `deploy.env` 注入

## 部署步骤

### Docker 生产部署
```bash
# 1. 配置环境变量
cp deploy.env.example deploy.env
# 编辑 deploy.env: DEEPSEEK_API_KEY=sk-xxx

# 2. 构建并启动
docker compose --env-file deploy.env -f docker-compose.prod.yml up -d --build

# 3. 验证
curl http://localhost/health
curl http://localhost/api/funds/search?q=易方达
```

### 远端服务器部署
```bash
# rsync 同步 + 远端构建
bash scripts/deploy-remote-192.sh
```

## 常见故障排查

| 问题 | 检查方向 |
|------|----------|
| 401 Unauthorized | 检查 deploy.env 中 DEEPSEEK_API_KEY 是否正确；检查是否有 shell 环境变量覆盖 |
| 前端白屏 | `docker compose logs web` 查看 Nginx 日志；检查构建是否成功 |
| SSE 流式中断 | 检查 nginx.conf 的 proxy_buffering off 和超时设置 |
| API 超时 | DeepSeek reasoner 模型较慢（30-60s），检查 Nginx 超时配置 |
| 数据源无响应 | 天天基金接口可能被限流，检查 backend 日志 |
