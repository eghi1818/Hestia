#!/usr/bin/env python3
"""Uji tulis jalur (blok F-3 / M0 MASUK).

Menulis penanda ke docroot target lewat jalur SSH -> lxc -> host root (J5), membaca ulang
dari dua vantage (lxc dan publik), lalu menghapus penanda. Hasil dicatat ke tabel jalur,
page, status_check, change_event, dan bukti.
"""
import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

AKAR = Path(__file__).resolve().parents[1]
DB = AKAR / "data" / "hestia.db"

VPS = os.environ.get("HESTIA_VPS", "administrator@93.127.133.160")
PORT = os.environ.get("HESTIA_VPS_PORT", "10053")
KUNCI = os.environ.get("HESTIA_VPS_KEY", str(Path.home() / ".ssh" / "wesearch_vps_key"))
KONTAINER = os.environ.get("HESTIA_LCX", "hx")
AKAR_HOST = os.environ.get("HESTIA_HOST_ROOT", "/mnt/host")


def shq(s):
    return "'" + s.replace("'", "'\\''") + "'"


def ssh(perintah_remote, waktu=25):
    dasar = ["ssh", "-i", KUNCI, "-p", PORT, "-o", "BatchMode=yes",
             "-o", "StrictHostKeyChecking=accept-new",
             "-o", "ConnectTimeout=%d" % waktu, VPS, perintah_remote]
    return subprocess.run(dasar, capture_output=True, text=True, timeout=waktu + 15)


def rantai(perintah_host):
    """kandidat rantai; dipilih yang berhasil saat dipakai"""
    return [
        ("lxc", "lxc exec %s -- sh -c %s" % (KONTAINER, shq(perintah_host))),
        ("sudo-lxc", "sudo lxc exec %s -- sh -c %s" % (KONTAINER, shq(perintah_host))),
    ]


def jalankan(perintah_host):
    for nama, cmd in rantai(perintah_host):
        try:
            h = ssh(cmd)
        except subprocess.TimeoutExpired:
            continue
        if h.returncode == 0:
            return nama, h.stdout
    return None, ""


UA = os.environ.get("HESTIA_UA", "Mozilla/5.0 (Hestia uji-jalur) Hestia/1.0")


def baca_publik(url, ua=None):
    """Baca dari luar. User-Agent penting: Cloudflare menolak UA bawaan python-urllib."""
    try:
        req = Request(url, headers={"User-Agent": ua or UA, "Accept": "*/*",
                                    "Cache-Control": "no-cache"})
        with urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return getattr(e, "code", 0), ""


def catat(conn, target_id, kode_j, url, isi, sha, vantage_ok, vantage_gagal, cara, mode=""):
    cap = time.strftime("%Y-%m-%dT%H:%M:%S")
    conn.execute(
        "insert or replace into jalur (target_id,kode_J,bukti,terbukti_bisa_tulis,waktu_uji,cara_tulis,catatan,diperbarui)"
        " values (?,?,?,?,?,?,?,?)",
        (target_id, kode_j, "%s sha256=%s" % (url, sha), 1 if not vantage_gagal else 0,
         cap, cara, "uji tulis penanda; gagal: %s" % (",".join(vantage_gagal) or "-"), cap))
    conn.execute("insert or ignore into page (target_id,url,dibuat_dummy) values (?,?,?)"
                 if False else
                 "insert or ignore into page (target_id,url) values (?,?)", (target_id, url))
    pid = conn.execute("select id from page where target_id=? and url=?", (target_id, url)).fetchone()[0]
    conn.execute("update page set status_http=?, sha256_konten=?, penanda_ada=?, diambil=?, vantage=? where id=?",
                 (200 if not vantage_gagal else 0, sha, 1 if not vantage_gagal else 0, cap,
                  "lxc+publik", pid))
    for vantage, ok in (("lxc", "lxc" not in vantage_gagal), ("publik", "publik" not in vantage_gagal)):
        conn.execute("insert into status_check (page_id,url,status_http,vantage,sha256_konten,waktu)"
                     " values (?,?,?,?,?,?)", (pid, url, 200 if ok else 0, vantage, sha, cap))
    for vantage, ok in (("lxc", "lxc" not in vantage_gagal), ("publik", "publik" not in vantage_gagal)):
        conn.execute("insert into bukti (mata,metode,verdict,nilai,sha256,keterangan,waktu)"
                     " values (?,?,?,?,?,?,?)",
                     (1, "uji-tulis-jalur", "lulus" if ok else "gagal", vantage, sha,
                      json.dumps({"target_id": target_id, "kode_j": kode_j, "url": url,
                                  "vantage": vantage, "cara": cara, "mode": mode}), cap))
    conn.execute("insert into change_event (target_id,page_id,jenis,jalur,nilai_baru,penanda,vantage,waktu)"
                 " values (?,?,?,?,?,?,?,?)",
                 (target_id, pid, "uji-tulis", kode_j, url, sha, "lxc+publik", cap))
    conn.commit()


def uji(target_id, kode_j="J5", docroot="/var/www/waspadaweb", url_publik=None, bersihkan=True):
    nonce = os.urandom(6).hex()
    cap = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    isi = "hestia-penanda %s %s %s" % (target_id, nonce, cap)
    sha = hashlib.sha256(isi.encode("utf-8")).hexdigest()
    berkas_host = "%s%s/hestia-penanda.txt" % (AKAR_HOST, docroot)
    url = url_publik or ("https://waspadaweb.com/hestia-penanda.txt")

    print("penanda:", isi)
    print("sha256 :", sha[:16])

    perintah_tulis = 'echo "%s" > %s' % (isi, berkas_host)
    cara, _ = jalankan(perintah_tulis)
    print("tulis  :", cara or "GAGAL SEMUA RANTAI")
    if not cara:
        return 1

    # berkas dibuat sebagai root; nginx worker bukan root -> harus bisa dibaca semua
    jalankan("chmod 644 %s" % berkas_host)
    mode = (jalankan("ls -l %s" % berkas_host)[1] or "").strip()
    print("mode   :", mode[:90])

    gagal = []
    _, keluaran = jalankan("cat %s" % berkas_host)
    ok_lxc = isi in keluaran
    print("baca lxc    :", "cocok" if ok_lxc else "TIDAK cocok")
    if not ok_lxc:
        gagal.append("lxc")

    status, badan = baca_publik(url)
    ok_pub = status == 200 and isi in badan
    print("baca publik :", ("cocok (%s, UA %s)" % (status, UA[:34])) if ok_pub else "TIDAK cocok (status %s)" % status)
    if not ok_pub:
        gagal.append("publik")

    with sqlite3.connect(DB) as conn:
        catat(conn, target_id, kode_j, url, isi, sha, [], gagal, cara, mode)

    if bersihkan:
        jalankan("rm -f %s" % berkas_host)
        status2, _ = baca_publik(url)
        print("hapus       : selesai, baca ulang status", status2)
        with sqlite3.connect(DB) as conn:
            conn.execute("update jalur set catatan=? where target_id=? and kode_J=?",
                         ("penanda dihapus; baca ulang status %s" % status2, target_id, kode_j))
            conn.commit()

    if gagal:
        print("HASIL: GAGAL pada vantage", ",".join(gagal))
        return 1
    print("HASIL: LULUS, jalur %s terbukti bisa menulis" % kode_j)
    return 0


def cek(docroot, url):
    berkas = "%s%s/hestia-penanda.txt" % (AKAR_HOST, docroot)
    print("ls docroot :", (jalankan("ls -ld %s" % ("%s%s" % (AKAR_HOST, docroot)))[1] or "").strip())
    print("ls berkas  :", (jalankan("ls -l %s" % berkas)[1] or "").strip() or "(tidak ada)")
    print("worker user:", (jalankan("ps aux | grep -m1 '[n]ginx' | awk '{print $1}'")[1] or "").strip())
    for f in ("%s/etc/nginx/sites-enabled/waspadaweb.com" % AKAR_HOST, "%s/etc/nginx/sites-available/waspadaweb.com" % AKAR_HOST):
        o = (jalankan("test -f %s && grep -n 'root\|location\|\.txt\|deny' %s | head -20" % (f, f))[1] or "").strip()
        print("--- %s" % f)
        print(o[:700] or "(tidak ada)")
    st, badan = baca_publik(url)
    print("publik     : status", st, "| panjang", len(badan))


def daftar():
    with sqlite3.connect(DB) as c:
        for r in c.execute("select target_id,kode_J,terbukti_bisa_tulis,waktu_uji,cara_tulis from jalur order by target_id"):
            print("  ", r)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("uji")
    u.add_argument("--target-id", type=int, required=True)
    u.add_argument("--kode", default="J5")
    u.add_argument("--docroot", default="/var/www/waspadaweb")
    u.add_argument("--url")
    sub.add_parser("daftar")
    k = sub.add_parser("cek")
    k.add_argument("--docroot", default="/var/www/waspadaweb")
    k.add_argument("--url", default="https://waspadaweb.com/hestia-penanda.txt")
    a = ap.parse_args()
    if a.cmd == "uji":
        sys.exit(uji(a.target_id, a.kode, a.docroot, a.url))
    if a.cmd == "cek":
        cek(a.docroot, a.url)
        return
    daftar()


if __name__ == "__main__":
    main()
