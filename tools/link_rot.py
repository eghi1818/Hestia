#!/usr/bin/env python3
"""Periksa tautan (link rot). Kolom bisa URL penuh atau hostname; hostname diberi https://."""
import argparse, datetime, sqlite3

import uji_probe

DB = "data/hestia.db"
PETA = {200: "hidup", 301: "pindah", 302: "pindah", 307: "pindah", 308: "pindah",
        401: "terkunci", 403: "terkunci", 404: "mati", 410: "mati", 0: "tak_jawab"}
KANDIDAT = ("url", "tautan", "ke", "dari", "alamat", "href", "link", "target")


def kelas(kode):
    return PETA.get(kode, "lain")


def kolom_url(c):
    kol = [r[1] for r in c.execute("pragma table_info(tautan)")]
    for k in KANDIDAT:
        if k in kol:
            return k
    raise SystemExit("kolom url tidak ketemu; kolom: %s" % kol)


def rapikan(v):
    v = str(v or "").strip()
    if not v:
        return ""
    return v if v.startswith("http") else "https://" + v


def siap(c):
    c.execute("create table if not exists tautan_rot (id integer primary key, "
              "tautan_id integer, kode integer, kelas text, vantage text, waktu text)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batas", type=int, default=40)
    ap.add_argument("--jeda", type=float, default=0.2)
    ap.add_argument("--db", default=DB)
    ap.add_argument("--terapkan", action="store_true")
    a = ap.parse_args()

    c = sqlite3.connect(a.db)
    c.row_factory = sqlite3.Row
    siap(c)
    ukol = kolom_url(c)
    print("  kolom url dipakai:", ukol)

    sudah = set(r[0] for r in c.execute("select tautan_id from tautan_rot"))
    semua = []
    for r in c.execute("select id, %s as u from tautan where %s is not null" % (ukol, ukol)):
        u = rapikan(r["u"])
        if u:
            semua.append({"id": r["id"], "u": u})
    baris = [r for r in semua if r["id"] not in sudah][:a.batas] or semua[:a.batas]

    hit = {}
    for r in baris:
        try:
            h = uji_probe.uji(r["u"], None, a.jeda)
            kode = int(h.get("kode") if isinstance(h, dict) else h)
        except Exception as e:
            kode = 0
            print("   galat", r["u"][:60], e)
        k = kelas(kode)
        hit[k] = hit.get(k, 0) + 1
        if a.terapkan:
            c.execute("insert into tautan_rot (tautan_id,kode,kelas,vantage,waktu) values (?,?,?,?,?)",
                      (r["id"], kode, k, "vps", datetime.datetime.now().astimezone().isoformat(timespec="seconds")))
        print("   %-4s %-10s %s" % (kode, k, r["u"][:70]))
    if a.terapkan:
        c.commit()
    print("  ringkas:", hit, "| diperiksa:", len(baris))
    print("  total tautan_rot:", c.execute("select count(*) from tautan_rot").fetchone()[0])


if __name__ == "__main__":
    main()
