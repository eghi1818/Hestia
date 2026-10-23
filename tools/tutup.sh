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
else
  echo "GATE GAGAL - commit ditolak"; exit 1
fi

# salin basis data sebelum ditutup
python3 tools/backup.py

# sisakan 200 catatan klien terakhir
curl -sS -X POST --max-time 5 "http://127.0.0.1:8787/api/clientlog/bersih?simpan=200" >/dev/null 2>&1 || true

# tulis dokumen langkah untuk commit ini
python3 - "$1" <<'PYEOF'
import re, subprocess, sys
pesan = sys.argv[1] if len(sys.argv) > 1 else ""
m = re.search(r"S-(\d+)", pesan)
if m:
    n = m.group(1)
    h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    d = "docs/steps"
    import os
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "S-%s.md" % n)
    if not os.path.exists(f):
        open(f, "w").write("# S-%s - %s\n\n- commit: %s\n- bukti: docs/evidence/S-%s.txt\n" % (n, pesan, h, n))
        print("+ dokumen langkah ditulis: %s" % f)
PYEOF

# catatan: dokumen langkah ditulis SESUDAH commit karena hash commit baru ada
# setelah commit; karena itu dokumen ikut masuk commit langkah berikutnya.
# DIRTY dicetak di sini, bukan sebelumnya, supaya angkanya jujur.
echo "langkah ditutup. DIRTY: $(git status --porcelain | wc -l | tr -d ' ')"
