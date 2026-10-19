#!/usr/bin/env bash
# Rakit paket pemulihan ke docs/RESUME-PACK.md
set -uo pipefail
cd "$(dirname "$0")/.."
out=docs/RESUME-PACK.md
{
  echo "# RESUME-PACK - HESTIA"
  echo "Dibuat: $(date '+%Y-%m-%d %H:%M:%S')"
  echo
  for pair in \
    "1. ATURAN:docs/ONBOARDING_PROMPT.txt" \
    "2. STATUS TERAKHIR:docs/SESSION_STATE.md" \
    "3. PENDING:docs/PENDING.md" \
    "4. RIWAYAT ESKALASI:docs/CHAT-LOG.md" \
    "5. RIWAYAT LANGKAH:docs/STEPLOG.md" ; do
    title="${pair%%:*}"; file="${pair#*:}"
    echo "## $title"
    if [ -f "$file" ]; then cat "$file"; else echo "(belum ada: $file)"; fi
    echo
  done
  echo "## 6. KONDISI LANGSUNG"
  echo '```'
  git status --short
  git log --oneline -5
  bash tools/gate.sh
  echo '```'
} > "$out"
echo "paket ditulis: $out"
