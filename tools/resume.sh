#!/usr/bin/env bash
# HESTIA - resume ringkas untuk sesi chat baru. Output sengaja dipangkas.
cd "$(dirname "$0")/.." || exit 1
echo "== HESTIA RESUME $(date -u +%Y-%m-%dT%H:%M:%SZ) =="
echo "HEAD   : $(git rev-parse --short HEAD) $(git log -1 --pretty=%s)"
echo "BRANCH : $(git branch --show-current)"
set -- $(git rev-list --left-right --count origin/main...HEAD 2>/dev/null)
echo "TRACK  : behind=$1 ahead=$2"
echo "DIRTY  : $(git status --porcelain | wc -l | tr -d ' ') file"
git status --porcelain | head -n 8
echo "-- 3 langkah terakhir --"
grep -E '^\| (S|H)-[0-9]' docs/STEPLOG.md | tail -n 3
echo "-- langkah berikut (HANDOFF bagian 8) --"
awk '/^#{1,4}[[:space:]]*8[.)[:space:]]/{f=1;next} f&&/^#{1,4}[[:space:]]*[0-9]+[.)[:space:]]/{exit} f' docs/HANDOFF.md | head -n 12
echo "-- bukti terbaru --"
ls -1t docs/steps 2>/dev/null | head -n 3
echo "-- guard --"
bash tools/step_guard.sh >/dev/null 2>&1 && echo "step_guard OK" || echo "step_guard GAGAL"
