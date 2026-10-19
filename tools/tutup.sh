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
