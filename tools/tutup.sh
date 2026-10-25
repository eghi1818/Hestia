#!/usr/bin/env bash
# S-<n> otomatis: judul langkah wajib memuat S-<n> supaya dokumen langkah dan
# pemeriksaan bukti selalu selaras, walau judul ditulis dengan penamaan F-<n>.
if ! printf '%s' "${1:-}" | grep -qE 'S-[0-9]+'; then
  _s=$(git log --oneline --pretty=%s 2>/dev/null | grep -oE 'S-[0-9]+' | grep -oE '[0-9]+' | sort -n | tail -1)
  _s=$(( ${_s:-0} + 1 ))
  set -- "S-$_s ${1:-}"
fi

# HESTIA - tutup langkah: gate -> commit -> push -> segarkan. Commit HARUS terakhir.
set -u
cd "$(dirname "$0")/.." || exit 1
MSG="${1:?pesan commit wajib}"
# siapkan dokumen langkah lebih awal agar pemeriksaan bukti di gate menilai
# langkah yang sedang dikerjakan, bukan langkah sebelumnya
_langkah=$(printf '%s' "${1:-}" | grep -oE 'S-[0-9]+' | head -1)
if [ -n "$_langkah" ] && [ ! -f "docs/steps/$_langkah.md" ]; then
  mkdir -p docs/steps
  printf '# %s\n\n- commit: (menyusul)\n- bukti: docs/evidence/%s.txt\n' "${1:-}" "$_langkah" > "docs/steps/$_langkah.md"
  echo "+ dokumen langkah disiapkan lebih awal: docs/steps/$_langkah.md"
fi

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

# buang stub (tanpa commit) agar sync_jejak menulis dokumen langkah yang lengkap
if [ -n "${_langkah:-}" ] && [ -f "docs/steps/$_langkah.md" ] && grep -q '(menyusul)' "docs/steps/$_langkah.md"; then
  rm -f "docs/steps/$_langkah.md"
fi
python3 tools/sync_jejak.py --resume
python3 tools/pangkas_bukti.py --simpan 5000 --r-simpan 50

# sync_jejak menulis docs/steps + SESSION_STATE SESUDAH commit, sehingga pohon
# bisa tetap kotor. Tutup celahnya: commit susulan + dorong ulang.
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -q -m "$(git log -1 --pretty=%s) [jejak]"
  for i in 1 2 3 4 5; do
    git push origin main && break || sleep 5
  done
  echo "commit susulan: $(git rev-parse --short HEAD) | DIRTY: $(git status --porcelain | wc -l | tr -d ' ')"
else
  echo "pohon bersih setelah sinkron"
fi
