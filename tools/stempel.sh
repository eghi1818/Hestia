#!/usr/bin/env bash
# HESTIA - stempel versi pada tag live.js supaya cache peramban tidak menyajikan salinan lama
cd "$(dirname "$0")/.." || exit 1
python3 - <<'PY'
import re, pathlib, subprocess, time
h = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                   capture_output=True, text=True).stdout.strip() or "x"
stamp = "%s-%d" % (h, int(time.time()))
p = pathlib.Path("dashboard/index.html"); s = p.read_text()
if re.search(r"live\.js", s):
    s2 = re.sub(r"live\.js(\?v=[0-9A-Za-z.-]+)?", "live.js?v=" + stamp, s, count=1)
    if s2 != s:
        p.write_text(s2); print("stempel live.js -> v=" + stamp)
    else:
        print("stempel tidak berubah")
PY
