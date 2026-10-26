#!/usr/bin/env python3
"""M4 BUKTI: bungkus bukti satu halaman siap diverifikasi pihak ketiga (blok F-13).

Isi bundel: meta.json, header + sha256 badan dari 2 vantage, cuplikan DB, MANIFEST berisi
sha256 tiap berkas, dan sha256 bundel. Semua waktu dalam UTC.
"""
import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

AKAR = Path(__file__).resolve().parents[1]
DB = AKAR / "data" / "hestia.db"
KELUAR = AKAR / "data" / "bukti"
UA = "Mozilla/5.0 (Hestia ekspor-bukti) Hestia/1.0"
VPS = "administrator@93.127.133.160"
PORT = "10053"
KUNCI = str(Path.home() / ".ssh" / "wesearch_vps_key")


def sha(teks):
    return hashlib.sha256(teks.encode("utf-8")).hexdigest()


def ambil_lokal(url):
    try:
        req = Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
        with urlopen(req, timeout=25) as r:
            badan = r.read().decode("utf-8", "replace")
            return r.status, dict(r.headers), badan
    except Exception as e:
        return getattr(e, "code", 0), {}, ""


def ambil_vps(url):
    dasar = ["ssh", "-i", KUNCI, "-p", PORT, "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", VPS]
    h = subprocess.run(dasar + ["curl -sS -o /tmp/_hestia_badan -D - -A %s %s" % (json.dumps(UA), json.dumps(url))],
                       capture_output=True, text=True, timeout=45)
    badan = subprocess.run(dasar + ["cat /tmp/_hestia_badan"], capture_output=True, text=True, timeout=45).stdout
    return h.stdout, badan


def normal(teks):
    """Bandingkan isi yang bermakna: buang spasi berlebih (Cloudflare menyuntik HTML)."""
    return " ".join((teks or "").split())


def baris_db(url):
    with sqlite3.connect(DB) as c:
        c.row_factory = sqlite3.Row
        pid = c.execute("select id from page where url=?", (url,)).fetchone()
        if not pid:
            return {"page": None, "change_event": [], "status_check": [], "bukti": []}
        pid = pid[0]
        return {
            "page": dict(c.execute("select * from page where id=?", (pid,)).fetchone()),
            "change_event": [dict(r) for r in c.execute("select * from change_event where page_id=? order by id", (pid,))],
            "status_check": [dict(r) for r in c.execute("select * from status_check where page_id=? order by id", (pid,))],
            "bukti": [dict(r) for r in c.execute("select * from bukti where keterangan like ?", ("%" + url + "%",))],
        }


def ekspor(target_id, path, url=None):
    url = url or ("https://waspadaweb.com%s" % path)
    cap = time.strftime("%Y%m%d-%H%M%S")
    utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    nama = "%s-%s" % (path.strip("/").replace("/", "-") or "akar", cap)
    d = KELUAR / nama
    d.mkdir(parents=True, exist_ok=True)

    st_lokal, hd_lokal, bd_lokal = ambil_lokal(url)
    hd_vps, bd_vps = ambil_vps(url)
    st_vps = "000"
    for baris in hd_vps.splitlines():
        if baris.startswith("HTTP/"):
            st_vps = baris.split()[1]

    (d / "lokal-headers.txt").write_text(
        "status: %s\n\n" % st_lokal + "\n".join("%s: %s" % (k, v) for k, v in hd_lokal.items()), encoding="utf-8")
    (d / "lokal-body.sha256").write_text("%s  %s\n" % (sha(bd_lokal), url), encoding="utf-8")
    (d / "vps-headers.txt").write_text(hd_vps or "(kosong)", encoding="utf-8")
    (d / "vps-body.sha256").write_text("%s  %s\n" % (sha(bd_vps), url), encoding="utf-8")
    (d / "db-snapshot.json").write_text(json.dumps(baris_db(url), indent=2, ensure_ascii=False), encoding="utf-8")
    (d / "meta.json").write_text(json.dumps({
        "url": url, "target_id": target_id, "jalur": "J5", "waktu_utc": utc,
        "vantage": {"lokal": st_lokal, "vps": st_vps},
        "sha256_badan": {"lokal": sha(bd_lokal), "vps": sha(bd_vps)},
        "cocok_mentah": bd_lokal == bd_vps,
        "cocok_normal": normal(bd_lokal) == normal(bd_vps),
        "status_sama": str(st_lokal) == str(st_vps),
        "penanda_ganti": "hestia-ganti donor=" in bd_lokal,
        "panjang_badan": len(bd_lokal),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    baris_manifest = []
    for f in sorted(d.iterdir()):
        if f.name == "MANIFEST.txt":
            continue
        baris_manifest.append("%s  %s" % (hashlib.sha256(f.read_bytes()).hexdigest(), f.name))
    (d / "MANIFEST.txt").write_text("\n".join(baris_manifest) + "\n", encoding="utf-8")
    sha_bundel = hashlib.sha256((d / "MANIFEST.txt").read_bytes()).hexdigest()

    with sqlite3.connect(DB) as c:
        c.execute("insert into bukti (mata,metode,verdict,nilai,sha256,keterangan,waktu) values (?,?,?,?,?,?,?)",
                  (1, "ekspor-bukti", "lulus" if st_lokal == 200 and st_vps == "200" else "gagal",
                   "bundel", sha_bundel,
                   json.dumps({"url": url, "bundel": str(d.relative_to(AKAR)), "vantage": {"lokal": st_lokal, "vps": st_vps}}),
                   utc))
        c.commit()

    print("bundel:", d.relative_to(AKAR))
    print("vantage: lokal", st_lokal, "| vps", st_vps)
    print("status sama:", str(st_lokal) == str(st_vps),
          "| badan identik mentah:", bd_lokal == bd_vps,
          "| identik ternormalisasi:", normal(bd_lokal) == normal(bd_vps))
    print("catatan: Cloudflare menyuntik HTML, jadi badan mentah bisa berbeda antar vantage")
    print("sha256 bundel:", sha_bundel[:32])
    for b in baris_manifest:
        print("  ", b[:16], b.split("  ")[-1])
    return 0 if st_lokal == 200 and st_vps == "200" else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-id", type=int, required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--url")
    a = ap.parse_args()
    sys.exit(ekspor(a.target_id, a.path, a.url))


if __name__ == "__main__":
    main()
