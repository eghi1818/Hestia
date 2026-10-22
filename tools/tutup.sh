#!/usr/bin/env bash
# HESTIA - tutup langkah: gate -> commit -> push -> segarkan. Commit HARUS terakhir.
set -u
cd "$(dirname "$0")/.." || exit 1
MSG="${1:?pesan commit wajib}"
if bash tools/gate.sh; then
  bash tools/stempel.sh >/dev/null 2>&1
  git add -A
  git commit -m "$MSG" || true
  git push
  bash tools/siapkan_newchat.sh >/dev/null 2>&1
  echo "langkah ditutup. DIRTY: $(git status --porcelain | wc -l | tr -d ' ')"
else
  echo "GATE GAGAL - commit ditolak"; exit 1
fi

# salin basis data sebelum ditutup
python3 tools/backup.py

# sisakan 200 catatan klien terakhir
curl -sS -X POST --max-time 5 "http://127.0.0.1:8787/api/clientlog/bersih?simpan=200" >/dev/null 2>&1 || true
