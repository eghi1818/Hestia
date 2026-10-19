#!/usr/bin/env bash
# Cetak status satu layar. Read-only.
set -uo pipefail
cd "$(dirname "$0")/.."
echo "===== RESUME HESTIA ====="
echo "-- git"
git status --short
git log --oneline -5
echo
echo "-- isi repo"
ls -1
echo
echo "-- isi docs"
ls -1 docs 2>/dev/null
echo
echo "-- pending"
[ -f docs/PENDING.md ] && sed -n '1,40p' docs/PENDING.md
echo
echo "-- gate"
bash tools/gate.sh
