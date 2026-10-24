#!/usr/bin/env bash
# HESTIA - tutup langkah: gate -> commit -> push -> segarkan. Commit HARUS terakhir.
set -u
cd "$(dirname "$0")/.." || exit 1
MSG="${1:?pesan commit wajib}"
if bash tools/gate.sh; then
  bash tools/stempel.sh "$MSG" >/dev/null 2>&1
  git add -A
  if git commit -m "$MSG" >/dev/null 2>&1 ; then echo "+ commit: $(git rev-parse --short HEAD)" ; else echo "! commit tidak dibuat (tidak ada perubahan?)" ; fi
  git push || echo "! push gagal"
  bash tools/siapkan_newchat.sh >/dev/null 2>&1
else
  echo "GATE GAGAL - commit ditolak"; exit 1
fi

# salin basis data sebelum ditutup
python3 tools/backup.py

# sisakan 200 catatan klien terakhir
curl -sS -X POST --max-time 5 "http://127.0.0.1:8787/api/clientlog/bersih?simpan=4000" >/dev/null 2>&1 || true

# tulis dokumen langkah untuk commit ini
python3 - "$1" <<'PYEOF'
import os, re, subprocess, sys
pesan = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
m = re.search(r"S-(\d+)", pesan)
if m:
    n = m.group(1)
    judul = re.sub(r"^S-\d+\s*[:\-]\s*", "", pesan.splitlines()[0]).strip()
    h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    f = "docs/steps/S-%s.md" % n
    b = "docs/evidence/S-%s.txt" % n
    os.makedirs("docs/steps", exist_ok=True)
    if not os.path.exists(f):
        isi = "# S-%s - %s\n\n- commit: %s\n" % (n, judul, h)
        isi += ("- bukti: %s\n" % b) if os.path.exists(b) else ("- bukti: (belum ada: %s)\n" % b)
        open(f, "w").write(isi)
        print("+ dokumen langkah ditulis: %s" % f)
PYEOF

# catatan: dokumen ditulis SESUDAH commit (hash baru ada setelah commit), jadi
# dokumen ikut masuk commit langkah berikutnya. DIRTY dicetak di bawah agar jujur.
echo "langkah ditutup. DIRTY: $(git status --porcelain | wc -l | tr -d ' ')"

python3 tools/sync_jejak.py --resume
