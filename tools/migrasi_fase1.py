#!/usr/bin/env python3
"""Fase 1: beri metrik kolom nilai + satuan supaya angka bisa dibandingkan antar waktu.

Pola sama dengan migrasi_fase0: cadangan VACUUM INTO + integrity_check, ledger
skema_versi, post-condition, idempoten, opsi paksa untuk uji.
"""
import argparse, hashlib, os, sqlite3, sys, time

DB = os.environ.get("HESTIA_DB", "data/hestia.db")
KOLOM = [("nilai", "REAL"), ("satuan", "TEXT")]


def ada_kolom(c, tabel, kolom):
    return any(r[1] == kolom for r in c.execute("pragma table_info(%s)" % tabel))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--paksa-gagal", action="store_true")
    ap.add_argument("--paksa-akhir", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(a.db):
        raise SystemExit("db tidak ada: %s" % a.db)

    cap = "%s.bak.%s" % (a.db, time.strftime("%Y%m%d-%H%M%S"))
    if os.path.exists(cap):                      # dua jalankan dalam detik yang sama
        n = 1
        while os.path.exists("%s-%d" % (cap, n)):
            n += 1
        cap = "%s-%d" % (cap, n)
    k = sqlite3.connect(a.db, isolation_level=None)
    k.execute("pragma busy_timeout = 5000")
    k.execute("pragma journal_mode = wal")
    k.execute("vacuum into ?", (cap,))
    ic = k.execute("attach database ? as c", (cap,)).fetchone()
    sehat = k.execute("pragma c.integrity_check").fetchone()[0]
    k.execute("detach database c")
    print("cadangan: %s (integritas: %s)" % (os.path.basename(cap), sehat))
    if sehat != "ok":
        print("[GALAT] cadangan tidak sehat, migrasi dibatalkan")
        return 1
    if a.paksa_gagal:
        print("[PAKSA] keluar sesudah cadangan")
        return 1

    if not any(r[1] == "metrik" for r in k.execute("pragma table_info(metrik)")) and \
       not k.execute("select 1 from sqlite_master where name='metrik'").fetchone():
        k.execute("create table metrik(nama text primary key, sumber text,"
                  " status_sumber text not null default 'tanpa_sumber',"
                  " terisi_terakhir text, catatan text)")

    ditambah = []
    for kolom, tipe in KOLOM:
        if not ada_kolom(k, "metrik", kolom):
            k.execute("alter table metrik add column %s %s" % (kolom, tipe))
            ditambah.append(kolom)
    print("kolom ditambah:", ditambah or "(sudah ada)")

    # ledger
    k.execute("create table if not exists skema_versi("
              "nama text primary key, dijalankan_pada text, hash text)")
    with open(__file__, encoding="utf-8") as f:
        h = hashlib.sha256(f.read().encode()).hexdigest()[:16]
    k.execute("insert or replace into skema_versi(nama, dijalankan_pada, hash) values(?,?,?)",
              ("fase1", time.strftime("%Y-%m-%d %H:%M:%S"), h))

    # isi satuan yang masuk akal
    k.execute("update metrik set satuan='halaman' where satuan is null and nama like 'konten.%'")
    k.execute("update metrik set nilai=(select count(*) from status_konten s"
              " where s.status = substr(metrik.nama, 8)) where nama like 'konten.%'")

    gagal = []
    for kolom, _t in KOLOM:
        if not ada_kolom(k, "metrik", kolom):
            gagal.append("kolom %s hilang" % kolom)
    if k.execute("pragma foreign_key_check").fetchone():
        gagal.append("foreign_key_check tidak bersih")
    if a.paksa_akhir:
        gagal.append("[PAKSA] post-condition digagalkan")
    print("post-condition:", "LULUS" if not gagal else "GAGAL %s" % gagal)

    # retensi cadangan
    d = os.path.dirname(a.db) or "."
    b = os.path.basename(a.db)
    lama = sorted(f for f in os.listdir(d) if f.startswith(b + ".bak."))[:-10]
    for f in lama:
        try:
            os.remove(os.path.join(d, f))
        except OSError:
            pass
    if lama:
        print("retensi: %d cadangan lama dihapus" % len(lama))

    k.close()
    return 0 if not gagal else 1


if __name__ == "__main__":
    sys.exit(main())
