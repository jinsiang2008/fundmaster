@AGENTS.md

## Commands
- Backend dev: `cd backend && uvicorn app.main:app --reload`
- Frontend dev: `cd frontend && npm run dev`
- Backend lint/fmt: `cd backend && ruff check app/ --fix && ruff format app/`
- Frontend lint: `cd frontend && npm run lint`
- Frontend build: `cd frontend && npm run build`
- Pre-commit: `pre-commit run --all-files`
- Docker dev: `docker compose up --build`
- Docker prod: `docker compose --env-file deploy.env -f docker-compose.prod.yml up -d --build`
- LAN deploy: `bash scripts/deploy-remote-192.sh`
- Local health check: `curl http://localhost:8000/health && curl http://localhost:5173`
- LAN health check: `curl --noproxy '*' http://192.168.71.128:8000/health && curl --noproxy '*' http://192.168.71.128:5173/`

## Additional Context
- [README.md](README.md) — 项目概览 & 快速开始
- [backend/README.md](backend/README.md) — 后端分层、约定与本地开发
- [frontend/README.md](frontend/README.md) — 前端目录、路由与约定
- [DEPLOY.md](DEPLOY.md) — 生产部署详细步骤
- [docs/memory.md](docs/memory.md) — 项目决策记录 & 已知问题
- 仓库外可能存在用户私有的 OpenClaw managed skills；repo 只维护项目事实、命令入口和公共规则
