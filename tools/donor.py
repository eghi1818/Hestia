#!/usr/bin/env python3
"""M1 AMBIL: ambil konten dari situs lain sebagai donor (blok F-7).

Simpan mentah apa adanya + versi bersih (tag dibuang) + sha256 + judul.
"""
import argparse
import hashlib
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

AKAR = Path(__file__).resolve().parents[1]
DB = AKAR / "data" / "hestia.db"
UA = os.environ.get("HESTIA_UA", "Mozilla/5.0 (Hestia donor) Hestia/1.0")


def bersihkan(html):
    judul = ""
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    if m:
        judul = re.sub(r"\s+", " ", m.group(1)).strip()[:200]
    t = re.sub(r"(?is)<script.*?</script>", " ", html)
    t = re.sub(r"(?is)<style.*?</style>", " ", t)
    t = re.sub(r"(?is)<!--.*?-->", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return judul, re.sub(r"\s+", " ", t).strip()


def ambil(url, target_id=None, catatan=None):
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*",
                                "Cache-Control": "no-cache"})
    try:
        with urlopen(req, timeout=25) as r:
            html = r.read().decode("utf-8", "replace")
            st = r.status
            tipe = r.headers.get("Content-Type", "")
    except Exception as e:
        print("GAGAL ambil:", url, "->", getattr(e, "code", e))
        return None
    judul, bersih = bersihkan(html)
    sha = hashlib.sha256(html.encode("utf-8")).hexdigest()
    cap = time.strftime("%Y-%m-%dT%H:%M:%S")
    with sqlite3.connect(DB) as c:
        c.execute("delete from donor where sha256=?", (sha,))
        cur = c.execute(
            "insert into donor (url,target_id,diambil,status_http,tipe_konten,sha256,panjang_mentah,"
            "panjang_bersih,judul,isi_mentah,isi_bersih,catatan) values (?,?,?,?,?,?,?,?,?,?,?,?)",
            (url, target_id, cap, st, tipe, sha, len(html), len(bersih), judul, html, bersih, catatan))
        rid = cur.lastrowid
    print("donor id=%d | %s | status %s | sha %s" % (rid, url, st, sha[:16]))
    print("  judul:", judul or "(tidak ada)")
    print("  panjang mentah/bersih: %d / %d" % (len(html), len(bersih)))
    print("  cuplikan bersih:", bersih[:150])
    return rid


def daftar():
    with sqlite3.connect(DB) as c:
        for r in c.execute("select id,url,status_http,substr(sha256,1,12),panjang_bersih,judul from donor order by id"):
            print("  ", r)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("ambil")
    a1.add_argument("--url", required=True)
    a1.add_argument("--target-id", type=int)
    a1.add_argument("--catatan")
    sub.add_parser("daftar")
    a = ap.parse_args()
    if a.cmd == "ambil":
        sys.exit(0 if ambil(a.url, a.target_id, a.catatan) else 1)
    daftar()


if __name__ == "__main__":
    main()
