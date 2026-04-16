# FundMaster 远端部署说明

本文说明如何在 **Linux 云服务器** 上用 Docker 部署前后端。无法在本文中替你执行 SSH，请在本机或 CI 按步骤操作。

## 架构（生产）

- **web**：Nginx 提供前端静态资源，并把浏览器请求 **`/api/*`** 反代到 **backend:8000**（同域，无需在前端写死后端地址）。
- **backend**：FastAPI + Uvicorn，仅在内网暴露 8000，不直接对公网（除非你自己改端口映射）。

## 1. 服务器准备

- Ubuntu 22.04 / Debian 12 等，已安装 **Docker** 与 **Docker Compose V2**（`docker compose` 子命令）。
- 安全组 / 防火墙放行 **`HTTP_PORT`**（默认 80，或你改的端口）。
- 建议内存 **≥ 2GB**（Python + 依赖 + Nginx）。

安装 Docker（示例，Ubuntu）：

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# 重新登录后生效
```

## 2. 获取代码

```bash
git clone <你的仓库地址> fundmaster
cd fundmaster
```

## 3. 配置密钥与端口

```bash
cp deploy.env.example deploy.env
nano deploy.env   # 填写 DEEPSEEK_API_KEY，按需改 HTTP_PORT
```

**不要将 `deploy.env` 提交到 Git。**

## 4. 构建并启动

在仓库根目录执行：

```bash
docker compose --env-file deploy.env -f docker-compose.prod.yml up -d --build
```

查看状态：

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f --tail=100
```

浏览器访问：`http://<服务器公网 IP>`（若 `HTTP_PORT` 非 80，则 `http://IP:端口`）。

## 5. HTTPS（推荐）

在 **Nginx/Caddy/宝塔** 前做反向代理并申请证书，或把 `web` 服务只绑内网，由宿主机 Nginx 处理 TLS。无论哪种方式，请把对外 **`/api`** 仍转到本机 **`127.0.0.1:80`**（或你映射的端口），以保持「同域 + `/api` 反代」结构。

若前后端必须跨域分离部署，需：

1. 前端构建时设置 `VITE_API_URL=https://api.你的域名`（需单独改 `Dockerfile.prod` 构建参数或增加 compose 覆盖）；
2. 后端 `CORS_ORIGINS` 包含前端页面 origin。

## 6. 更新版本

```bash
cd fundmaster
git pull
docker compose --env-file deploy.env -f docker-compose.prod.yml up -d --build
```

## 7. 常见问题

| 现象 | 处理 |
|------|------|
| 前端能开，接口 502 | 看 `docker compose logs backend`，确认 Key 与网络出网 |
| 对比 / AI 超时 | Nginx 已设较长 `proxy_read_timeout`；若前面还有 CDN/网关，需同步放大超时 |
| 静态资源 404 | 确认使用 `Dockerfile.prod` 构建，且访问路径为主站根路径 |

## 8. 仅后端 / 仅调试

- 本地开发仍可用原 `docker-compose.yml`（开发模式）。
- 仅跑 API：`docker compose -f docker-compose.prod.yml run --rm backend` 不推荐；直接 `docker run` 或 `uvicorn` 见 README。

## 9. 局域网 Mac（无 Docker）：`scripts/deploy-remote-192.sh`

适用于与开发机同网段的 Mac：用 **rsync + venv + `vite preview`** 部署到 `~/fundmaster`。

**`.env` 策略：**

| 方式 | 说明 |
|------|------|
| **默认** | 会把本地的 `backend/.env`、`frontend/.env` **一并同步**到远端（与开发机密钥、配置一致）。部署前请确保本机已存在 `backend/.env`。 |
| **远端独立配置** | 执行前设置 `SKIP_LOCAL_ENV=1`，则 rsync **不同步**两个 `.env`，远端沿用服务器上已有文件。 |

部署脚本在远端只会**合并** `frontend/.env` 里的 `VITE_API_URL`（指向 `http://<远端IP>:8000`），不会清空其它行；`backend/.env` 里会合并/写入 `CORS_ORIGINS`（含局域网前端地址）。

```bash
# 首次在远端准备好密钥（若默认不同步 .env）
ssh user@远端 'cp ~/fundmaster/backend/.env.example ~/fundmaster/backend/.env'
# 再编辑远端 backend/.env 填入 DEEPSEEK_API_KEY

export SSHPASS='...'   # 未配 SSH 公钥时
./scripts/deploy-remote-192.sh
```
