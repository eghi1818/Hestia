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
    timeout 900 "$PY" tools/status_periksa.py --terapkan > "$OUT" 2>&1
    echo "  rc=$?"
    tail -60 "$OUT"
  else
    echo "  tools/status_periksa.py tidak ada"
  fi
  echo "=== $(date -Is) selesai"
} >> "$LOG" 2>&1
rm -f "$OUT"
exit 0
