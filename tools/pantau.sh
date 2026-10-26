#!/usr/bin/env bash
# Pemantauan berkala Hestia. Dipanggil systemd timer. Selalu keluar 0.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
LOG=${HESTIA_LOG:-/var/log/hestia/pantau.log}
PY=python3
for c in .venv/bin/python venv/bin/python; do [ -x "$c" ] && PY="$c" && break; done
{
  echo "=== $(date -Is) mulai (py=$PY) ==="
  if [ -f tools/status_periksa.py ]; then
    timeout 900 "$PY" tools/status_periksa.py 2>&1 | tail -40
  else
    echo "  tools/status_periksa.py tidak ada"
  fi
  echo "=== $(date -Is) selesai ==="
} >> "$LOG" 2>&1
exit 0
