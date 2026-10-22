#!/usr/bin/env python3
"""Deteksi kanal 'kunci mesin': host di ~/.ssh/config yang benar-benar melayani domain target."""
import subprocess
import sys
from pathlib import Path

CFG = Path.home() / ".ssh" / "config"


def blok():
    if not CFG.exists():
        return []
    hasil, kini = [], None
    for baris in CFG.read_text(errors="ignore").splitlines():
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


def main():
    if len(sys.argv) < 2:
        print("pakai: kunci.py <domain>")
        return 2
    target = sys.argv[1]
    akar = target.split(".")[0]
    daftar = [b for b in blok() if b["hostname"]]
    print("target:", target, "| host di ssh config:", len(daftar))
    ketemu = False
    for b in daftar:
        key = Path(b["key"].replace("~", str(Path.home())))
        user = b["user"] or ("wesearch" if "wesearch" in b["alias"] else b["alias"])
        print("--- alias=%s host=%s:%s kunci=%s" % (b["alias"], b["hostname"], b["port"], "ADA" if key.exists() else "TIDAK ADA"))
        if not key.exists():
            continue
        remote = ('echo "vhost:"; grep -rl "server_name" /etc/nginx/sites-enabled /etc/apache2/sites-enabled 2>/dev/null | head -5; '
                  'echo "sebut-target:"; grep -rh "server_name[^;]*%s" /etc/nginx/sites-enabled /etc/apache2/sites-enabled 2>/dev/null | head -3; '
                  'echo "www:"; ls -d /var/www/* 2>/dev/null | head -10; '
                  'echo "bisa-ditulis:"; find /var/www -maxdepth 2 -writable 2>/dev/null | head -8; '
                  'echo "id:"; id -un') % target
        try:
            r = subprocess.run(["ssh", "-i", str(key), "-p", b["port"],
                                "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
                                "-o", "ConnectTimeout=8", "%s@%s" % (user, b["hostname"]), remote],
                               capture_output=True, text=True, timeout=45)
            keluar = (r.stdout or "") + (r.stderr or "")
        except Exception as e:
            print("   ssh gagal: %r" % (e,))
            continue
        for l in keluar.strip().splitlines():
            print("   " + l)
        if akar in keluar:
            print("KUNCI MESIN: BUKA alias=%s porta=%s user=%s" % (b["alias"], b["port"], user))
            ketemu = True
    if not ketemu:
        print("KUNCI MESIN: tidak ada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
