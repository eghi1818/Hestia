"""Gate: setiap rute /api/... yang dipakai dashboard harus ada di app/main.py."""
import glob
import re
import sys


def bentuk(x):
    return re.sub(r"\$\{[^}]+\}|\{[^}]+\}", "{}", x)


api = set(bentuk(m) for m in re.findall(r'"/api/[^"]+"', open("app/main.py").read()))
kurang = []
for js in sorted(glob.glob("dashboard/*.js")):
    isi = open(js).read()
    for p in set(re.findall(r"[\"'`](/api/[A-Za-z0-9_/{}.$-]+)", isi)):
        inti = bentuk(p.split("?")[0])
        if inti not in api:
            kurang.append((js, p))
print("== gate: rute api dipakai dashboard ==")
for js, p in kurang:
    print("  HILANG  %s -> %s" % (js, p))
if kurang:
    print("  %d rute tidak ada di app/main.py" % len(kurang))
    sys.exit(1)
print("  ok      semua rute api ada di app/main.py")
