#!/usr/bin/env python3
"""BUNUH: ubah status halaman target lewat jalur J5 (blok F-4).

Menulis region bertanda di conf nginx, snapshot conf lebih dulu, verifikasi dari dua
vantage, idempoten, dan bisa dipulihkan. Mencatat ke change_event + bukti + page.
"""
import argparse
import base64
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

AKAR = Path(__file__).resolve().parents[1]
DB = AKAR / "data" / "hestia.db"
SNAP = AKAR / "data" / "snapshot"

VPS = os.environ.get("HESTIA_VPS", "administrator@93.127.133.160")
PORT = os.environ.get("HESTIA_VPS_PORT", "10053")
KUNCI = os.environ.get("HESTIA_VPS_KEY", str(Path.home() / ".ssh" / "wesearch_vps_key"))
KONTAINER = os.environ.get("HESTIA_LCX", "hx")
CONF = os.environ.get("HESTIA_CONF", "/mnt/host/etc/nginx/sites-available/waspadaweb.com")
DOCROOT = os.environ.get("HESTIA_DOCROOT", "/mnt/host/var/www/waspadaweb")
MARK_A = "    # >>> hestia-bunuh"
MARK_B = "    # <<< hestia-bunuh"
UA = os.environ.get("HESTIA_UA", "Mozilla/5.0 (Hestia uji-bunuh) Hestia/1.0")


def shq(s):
    return "'" + s.replace("'", "'\\''") + "'"


def ssh(cmd, w=25):
    return subprocess.run(["ssh", "-i", KUNCI, "-p", PORT, "-o", "BatchMode=yes",
                           "-o", "ConnectTimeout=%d" % w, VPS, cmd],
                          capture_output=True, text=True, timeout=w + 15)


def ct(perintah, w=25):
    for rantai in ("lxc exec %s -- sh -c %s" % (KONTAINER, shq(perintah)),
                   "sudo lxc exec %s -- sh -c %s" % (KONTAINER, shq(perintah))):
        h = ssh(rantai, w)
        if h.returncode == 0:
            return h.stdout
    return ""


def conf_baca():
    return ct("cat %s" % CONF)


def conf_tulis(teks):
    b64 = base64.b64encode(teks.encode("utf-8")).decode()
    return ct('printf "%%s" %s | base64 -d > %s' % (b64, CONF))


def reload_nginx(bisu=True):
    """Reload nginx. Driver memakai host langsung (_ssh_host), bukan lxc."""
    kandidat_host = ("sudo nginx -t && sudo nginx -s reload",
                     "sudo -n nginx -t && sudo -n nginx -s reload",
                     "nginx -t && nginx -s reload",
                     "sudo systemctl reload nginx",
                     "systemctl reload nginx",
                     "sudo service nginx reload")
    for c in kandidat_host:
        h = ssh(c)
        if h.returncode == 0:
            return "host:" + c
        if not bisu:
            print("    gagal host:", c, "|", (h.stderr or h.stdout).strip()[:90])
    for c in ("nginx -t && nginx -s reload", "systemctl reload nginx"):
        h = ssh("lxc exec %s -- sh -c %s" % (KONTAINER, shq(c)))
        if h.returncode == 0:
            return "lxc:" + c
        if not bisu:
            print("    gagal lxc:", c, "|", (h.stderr or h.stdout).strip()[:90])
    return None


def snapshot():
    SNAP.mkdir(parents=True, exist_ok=True)
    teks = conf_baca()
    cap = time.strftime("%Y%m%d-%H%M%S")
    p = SNAP / ("nginx-waspadaweb-%s.conf" % cap)
    n = 0
    while p.exists():
        n += 1
        p = SNAP / ("nginx-waspadaweb-%s-%d.conf" % (cap, n))
    p.write_text(teks, encoding="utf-8")
    return p, hashlib.sha256(teks.encode("utf-8")).hexdigest()


def region(teks, kode, path):
    isi = "\n".join([MARK_A,
                     "    location = %s { return %d; }" % (path, kode),
                     MARK_B])
    if MARK_A in teks:
        awal = teks.index(MARK_A)
        akhir = teks.index(MARK_B) + len(MARK_B)
        return teks[:awal] + isi + teks[akhir:]
    baris = teks.rstrip("\n").splitlines()
    for i in range(len(baris) - 1, -1, -1):
        if baris[i].strip() == "}":
            return "\n".join(baris[:i] + isi.splitlines() + baris[i:]) + "\n"
    return teks


def hapus_region(teks):
    if MARK_A not in teks:
        return teks
    awal = teks.index(MARK_A)
    akhir = teks.index(MARK_B) + len(MARK_B)
    sisa = teks[:awal] + teks[akhir:]
    return "\n".join([b for b in sisa.splitlines() if b.strip() != "" or True]) + "\n"


def baca_penuh(url, ua=None):
    """Kembalikan (status, badan). baca() sengaja tetap mengembalikan status saja."""
    try:
        req = Request(url, headers={"User-Agent": ua or UA, "Cache-Control": "no-cache"})
        with urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", 0), ""


def baca(url):
    try:
        with urlopen(Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"}), timeout=20) as r:
            return r.status
    except Exception as e:
        return getattr(e, "code", 0)


def status(url):
    hasil = {}
    try:
        h = ssh("curl -s -o /dev/null -w '%%{http_code}' -A %s %s" % (shq(UA), shq(url)), 25)
        hasil["vps"] = h.stdout.strip() or "000"
    except Exception:
        hasil["vps"] = "000"
    hasil["lokal"] = str(baca(url))
    return hasil


def catat(target_id, path, url, kode, aksi, sha_conf, st, snap):
    cap = time.strftime("%Y-%m-%dT%H:%M:%S")
    with sqlite3.connect(DB) as c:
        c.execute("insert or ignore into page (target_id,url) values (?,?)", (target_id, url))
        pid = c.execute("select id from page where target_id=? and url=?", (target_id, url)).fetchone()[0]
        c.execute("insert into change_event (target_id,page_id,jenis,jalur,nilai_lama,nilai_baru,penanda,vantage,waktu)"
                  " values (?,?,?,?,?,?,?,?,?)",
                  (target_id, pid, "bunuh-%d" % kode, "J5", json.dumps(st), str(kode),
                   sha_conf[:16], "vps+lokal", cap))
        for vantage, nilai in st.items():
            c.execute("insert into status_check (page_id,url,status_http,vantage,sha256_konten,waktu)"
                      " values (?,?,?,?,?,?)", (pid, url, int(nilai) if nilai.isdigit() else 0, vantage, None, cap))
            c.execute("insert into bukti (mata,metode,verdict,nilai,sha256,keterangan,waktu)"
                      " values (?,?,?,?,?,?,?)",
                      (1, "bunuh-%s" % kode, "lulus" if nilai == str(kode) else "gagal", vantage,
                       sha_conf, json.dumps({"target_id": target_id, "path": path, "url": url,
                                             "kode": kode, "aksi": aksi, "vantage": vantage,
                                             "snapshot": str(snap)}), cap))
        c.commit()


def pasang(target_id, path, kode=404, url=None, dry_run=False):
    url = url or ("https://waspadaweb.com%s" % path)
    snap, sha = snapshot()
    print("snapshot:", snap.name, "sha:", sha[:16])
    teks = conf_baca()
    baru = region(teks, kode, path)
    if dry_run:
        print("dry-run: conf berubah?", baru != teks)
        return 0
    conf_tulis(baru)
    cara = reload_nginx()
    print("reload:", cara or "GAGAL SEMUA CARA")
    st = status(url)
    print("status:", st)
    catat(target_id, path, url, kode, "pasang", sha, st, snap)
    return 0 if st.get("lokal") == str(kode) else 1


def pulih(target_id, path, kode=404, url=None):
    url = url or ("https://waspadaweb.com%s" % path)
    snap, sha = snapshot()
    teks = conf_baca()
    baru = hapus_region(teks)
    if baru == teks:
        print("tidak ada region bertanda; tidak ada yang dipulihkan")
    else:
        conf_tulis(baru)
    cara = reload_nginx()
    print("reload:", cara or "GAGAL SEMUA CARA")
    st = status(url)
    print("status:", st)
    catat(target_id, path, url, kode, "pulih", sha, st, snap)
    return 0 if st.get("lokal") == "200" else 1


def siapkan_halaman(path="/uji-hestia/"):
    nonce = os.urandom(5).hex()
    isi = "hestia-halaman-uji %s" % nonce
    dir_host = "%s%s" % (DOCROOT, path.rstrip("/"))
    ct("mkdir -p %s" % dir_host)
    ct('echo "%s" > %s/index.html' % (isi, dir_host))
    ct("chmod 644 %s/index.html" % dir_host)
    print("halaman uji:", path, "| isi:", isi)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nama in ("pasang", "pulih"):
        x = sub.add_parser(nama)
        x.add_argument("--target-id", type=int, required=True)
        x.add_argument("--path", required=True)
        x.add_argument("--kode", type=int, default=404)
        x.add_argument("--url")
        if nama == "pasang":
            x.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("siapkan")
    s.add_argument("--path", default="/uji-hestia/")
    sub.add_parser("cek-reload")
    st = sub.add_parser("status")
    st.add_argument("--path", required=True)
    a = ap.parse_args()

    if a.cmd == "cek-reload":
        print("cara reload:", reload_nginx(bisu=False))
        return
    if a.cmd == "siapkan":
        siapkan_halaman(a.path)
    elif a.cmd == "status":
        print(status("https://waspadaweb.com%s" % a.path))
    elif a.cmd == "pasang":
        sys.exit(pasang(a.target_id, a.path, a.kode, a.url, a.dry_run))
    else:
        sys.exit(pulih(a.target_id, a.path, a.kode, a.url))


if __name__ == "__main__":
    main()
