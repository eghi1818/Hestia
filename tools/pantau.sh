#!/usr/bin/env bash
# Pemantauan berkala Hestia. Dipanggil systemd timer. Selalu keluar 0.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
LOG=${HESTIA_PANTAU_LOG:-data/pantau.log}
OUT=$(mktemp /tmp/hestia-pantau.XXXXXX)
PY=python3
for c in .venv/bin/python venv/bin/python; do [ -x "$c" ] && PY="$c" && break; done
{
  echo "=== $(date -Is) mulai (py=$PY)"
  if [ -f tools/status_periksa.py ]; then
    timeout 900 "$PY" tools/status_periksa.py --batas 500 --jeda 0.2 --terapkan > "$OUT" 2>&1
    echo "  status_periksa rc=$?"
    tail -40 "$OUT"
  fi
  if [ -f tools/link_rot.py ]; then
    timeout 900 "$PY" tools/link_rot.py --batas 40 --jeda 0.2 --terapkan > "$OUT" 2>&1
    echo "  link_rot rc=$?"
    tail -25 "$OUT"
  fi
  echo "=== $(date -Is) selesai"
} >> "$LOG" 2>&1
rm -f "$OUT"
exit 0
