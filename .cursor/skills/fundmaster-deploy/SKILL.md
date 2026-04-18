---
name: fundmaster-deploy
description: Use when deploying FundMaster, troubleshooting Docker/Nginx/rsync 局域网远端运行、检查健康接口，或排查 FundMaster API 不可达问题。
---

# FundMaster 部署

## 生产环境事实
- 前后端通过 Docker Compose 编排
- Nginx 做同域反代，`/` 静态资源 + `/api` 转发到 backend:8000
- SSE 流式: Nginx 已关闭 proxy_buffering，超时设置 300s
- 环境变量通过 `deploy.env` 注入

## 局域网远端事实
- 远端 macOS 路径使用 `scripts/deploy-remote-192.sh`
- 远端当前活跃 IP / 运行事实以 `docs/memory.md` 为准
- 远端运行模式不是 Docker，而是 `backend/venv + uvicorn` 与 `frontend/node_modules/.bin/vite preview`
- 若远端 IP 变化，需同时更新远端 `frontend/.env` 的 `VITE_API_URL` 与 `backend/.env` 的 `CORS_ORIGINS`

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

### 局域网验证
```bash
# 开发机本身有代理时，避免把局域网请求走到 127.0.0.1:7890
curl --noproxy '*' http://<LAN-IP>:8000/health
curl --noproxy '*' http://<LAN-IP>:5173/
curl --noproxy '*' "http://<LAN-IP>:8000/api/funds/featured?limit=3"
```

## 常见故障排查

| 问题 | 检查方向 |
|------|----------|
| 401 Unauthorized | 检查 deploy.env 中 DEEPSEEK_API_KEY 是否正确；检查是否有 shell 环境变量覆盖 |
| 前端白屏 | `docker compose logs web` 查看 Nginx 日志；检查构建是否成功 |
| SSE 流式中断 | 检查 nginx.conf 的 proxy_buffering off 和超时设置 |
| API 超时 | DeepSeek reasoner 模型较慢（30-60s），检查 Nginx 超时配置 |
| 数据源无响应 | 天天基金接口可能被限流，检查 backend 日志 |
| 局域网 curl 超时 | 检查本机 `http_proxy` / `https_proxy`；对 LAN 地址使用 `--noproxy '*'` |
| 远端切网后打不开 | 更新远端 `.env` 里的 `VITE_API_URL` / `CORS_ORIGINS`，再重启 backend/frontend |
| 远端前端起不来 | 非交互 shell 可能找不到 `npx`；改用 `./node_modules/.bin/vite preview` 或显式补 `/opt/homebrew/bin` |
| `/health` 返回 200 但不像 FundMaster | 再请求 `/api/funds/featured?limit=3` 或搜索接口，避免误命中别的本地服务 |
