#!/usr/bin/env bash
# Lepaskan layanan dashboard dari terminal: pakai logika tools/live.sh,
# dijalankan dengan nohup supaya menutup terminal tidak mematikannya.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
PORT=${HESTIA_PORT:-8787}
LOG=data/layanan.log
PIDF=data/layanan.pid
mkdir -p data
if curl -s -o /dev/null --max-time 3 "http://127.0.0.1:$PORT/api/health"; then
  echo "  sudah hidup di :$PORT"
else
  nohup bash tools/live.sh pasang >> "$LOG" 2>&1 &
  echo $! > "$PIDF"
  disown 2>/dev/null || true
  sleep 6
  echo "  dimulai pid $(cat "$PIDF")"
fi
echo -n "  ppid: "; ps -o ppid= -p "$(cat "$PIDF" 2>/dev/null)" 2>/dev/null | tr -d ' ' || echo "-"
for u in / /api/health /api/targets /api/audit; do
  printf "  %-14s -> " "$u"
  curl -s -o /dev/null -w '%{http_code}\n' --max-time 5 "http://127.0.0.1:$PORT$u" || echo 000
done
