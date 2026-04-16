@AGENTS.md

## Commands
- Backend dev: `cd backend && uvicorn app.main:app --reload`
- Frontend dev: `cd frontend && npm run dev`
- Backend lint: `cd backend && ruff check app/ --fix`
- Frontend lint: `cd frontend && npm run lint`
- Frontend build: `cd frontend && npm run build`
- Docker dev: `docker compose up --build`
- Docker prod: `docker compose --env-file deploy.env -f docker-compose.prod.yml up -d --build`
- Health check: `curl http://localhost:8000/health`

## Additional Context
- [README.md](README.md) — 项目概览 & 快速开始
- [DEPLOY.md](DEPLOY.md) — 生产部署详细步骤
- [docs/memory.md](docs/memory.md) — 项目决策记录 & 已知问题
