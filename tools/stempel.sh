#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit 1
python3 - <<'PY'
import re, pathlib, subprocess, time
h = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                   capture_output=True, text=True).stdout.strip() or "x"
stamp = "%s-%d" % (h, int(time.time()))
p = pathlib.Path("dashboard/index.html"); s = p.read_text()
for nama in ("live", "ikhtisar", "tautan", "audit"):
    s = re.sub(r"%s\.js(\?v=[0-9A-Za-z.-]+)?" % nama, "%s.js?v=%s" % (nama, stamp), s, count=1)
p.write_text(s)
print("stempel -> v=" + stamp)
PY
