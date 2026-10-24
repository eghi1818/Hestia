#!/usr/bin/env bash
# HESTIA - nyalakan layanan
cd "$(dirname "$0")/.." || exit 1
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
[ -f "$HOME/.hestia/live.env" ] && { set -a; . "$HOME/.hestia/live.env"; set +a; }
pkill -f "app.main" 2>/dev/null; sleep 1
nohup $PY -m uvicorn app.main:app --host 127.0.0.1 --port 8787 >/tmp/hestia.log 2>&1 &
sleep 3
curl -s -o /dev/null -w "layanan: http %{http_code}\n" http://127.0.0.1:8787/api/targets
