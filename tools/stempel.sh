#!/usr/bin/env bash
# stempel.sh - cap versi untuk cache-busting aset dashboard.
# Dipakai SEBELUM commit, jadi HEAD masih commit INDUK; karena itu cap memakai
# nomor langkah dari pesan, bukan hash, supaya tidak mengaku asal yang salah.
cd "$(dirname "$0")/.." || exit 1
python3 - "$1" <<'PY'
import re, pathlib, sys, time
pesan = sys.argv[1] if len(sys.argv) > 1 else ""
m = re.search(r"S-(\d+)", pesan)
stamp = "%s-%d" % (("S" + m.group(1)) if m else "x", int(time.time()))
p = pathlib.Path("dashboard/index.html"); s = p.read_text()
for nama in ("live", "ikhtisar", "tautan", "audit", "konten", "detail", "recon", "ekspor", "aksi"):
    s = re.sub(r"%s\.js(\?v=[0-9A-Za-z.-]+)?" % nama, "%s.js?v=%s" % (nama, stamp), s, count=1)
p.write_text(s)
print("stempel -> v=" + stamp)
PY
