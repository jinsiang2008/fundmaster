#!/usr/bin/env bash
# 同步到局域网远端并重启（macOS 无 Docker：venv + vite preview）
#   export SSHPASS='密码'   # 若未配置 SSH 公钥
#   ./scripts/deploy-remote-192.sh
#
# 环境变量文件：
#   默认会 rsync 本地的 backend/.env、frontend/.env 到远端（与开发机一致）。
#   若希望远端保留自己的 .env、不要被本地覆盖：SKIP_LOCAL_ENV=1 ./scripts/deploy-remote-192.sh
#
# 可覆盖：REMOTE_HOST REMOTE_USER（默认 192.168.31.170 / jinsiangbot）

set -euo pipefail
REMOTE_HOST="${REMOTE_HOST:-192.168.31.170}"
REMOTE_USER="${REMOTE_USER:-jinsiangbot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ "${SKIP_LOCAL_ENV:-0}" != "1" ]]; then
  if [[ ! -f "$ROOT/backend/.env" ]]; then
    echo "错误: 本地缺少 $ROOT/backend/.env，无法同步到远端。" >&2
    exit 1
  fi
fi

if [[ -n "${SSHPASS:-}" ]] && command -v sshpass >/dev/null 2>&1; then
  RSYNC_RSH="sshpass -e ssh -o StrictHostKeyChecking=accept-new"
  RSH=(sshpass -e ssh -o StrictHostKeyChecking=accept-new)
else
  RSYNC_RSH="ssh -o StrictHostKeyChecking=accept-new"
  RSH=(ssh -o StrictHostKeyChecking=accept-new)
fi

RSYNC_EXCLUDES=(
  --exclude '.git'
  --exclude 'node_modules'
  --exclude 'frontend/node_modules'
  --exclude 'backend/venv'
  --exclude '__pycache__'
  --exclude '.vite'
  --exclude 'frontend/dist'
)
if [[ "${SKIP_LOCAL_ENV:-0}" == "1" ]]; then
  RSYNC_EXCLUDES+=(--exclude 'backend/.env' --exclude 'frontend/.env')
fi

rsync -avz --delete \
  "${RSYNC_EXCLUDES[@]}" \
  -e "$RSYNC_RSH" \
  "$ROOT/" \
  "${REMOTE_USER}@${REMOTE_HOST}:~/fundmaster/"

"${RSH[@]}" "${REMOTE_USER}@${REMOTE_HOST}" 'zsh -l -s' <<'REMOTE'
set -e
export NO_PROXY="*"
export no_proxy="*"
PY311="/opt/homebrew/opt/python@3.11/bin/python3.11"
[ -x "$PY311" ] || PY311=$(command -v python3.11 || command -v python3)
cd ~/fundmaster
if [ ! -f backend/.env ]; then
  echo "错误: 远端缺少 ~/fundmaster/backend/.env。" >&2
  echo "请确认本机 backend/.env 存在并已 rsync 成功；若使用 SKIP_LOCAL_ENV=1，请在远端自行准备 .env。" >&2
  exit 1
fi
python3 <<'PY'
from pathlib import Path
# 仅合并 VITE_API_URL，不整文件覆盖（远端可保留自己的 frontend/.env）
fe = Path.home() / "fundmaster/frontend/.env"
line = "VITE_API_URL=http://192.168.31.170:8000"
lines = fe.read_text().splitlines() if fe.exists() else []
out, seen = [], False
for x in lines:
    if x.strip().startswith("VITE_API_URL="):
        if not seen:
            out.append(line)
            seen = True
        continue
    out.append(x)
if not seen:
    out.append(line)
fe.parent.mkdir(parents=True, exist_ok=True)
fe.write_text("\n".join(out) + "\n")
print("frontend .env: VITE_API_URL merged")
PY
python3 <<'PY'
from pathlib import Path
p = Path.home() / "fundmaster/backend/.env"
lines = p.read_text().splitlines() if p.exists() else []
cors = "CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://192.168.31.170:5173"
out, seen = [], False
for line in lines:
    if line.strip().startswith("CORS_ORIGINS="):
        if not seen:
            out.append(cors)
            seen = True
        continue
    out.append(line)
if not seen:
    out.append(cors)
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("\n".join(out) + "\n")
PY
[ ! -d backend/venv ] && "$PY311" -m venv backend/venv
source backend/venv/bin/activate
pip install -q -U pip wheel
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple pip install -q -r backend/requirements.txt
(cd frontend && npm ci --silent && npm run build)
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "vite preview" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true
sleep 2
cd ~/fundmaster/backend && source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ~/fundmaster/backend.log 2>&1 &
echo $! > ~/fundmaster/backend.pid
cd ~/fundmaster/frontend
nohup npx vite preview --host 0.0.0.0 --port 5173 > ~/fundmaster/frontend.log 2>&1 &
echo $! > ~/fundmaster/frontend.pid
sleep 2
curl -s -o /dev/null -w "backend /health: %{http_code}\n" http://127.0.0.1:8000/health
curl -s -o /dev/null -w "frontend: %{http_code}\n" http://127.0.0.1:5173/
REMOTE

echo "OK → http://${REMOTE_HOST}:5173/  （API: http://${REMOTE_HOST}:8000）"
