#!/usr/bin/env python3
"""Pangkas bukti ke N terbaru + log R-*.txt ke M terbaru.

Baris bukti yang masih dirujuk status_konten.bukti_terakhir TIDAK dihapus,
supaya tautan tetap sahih walau umurnya sudah lewat batas.
"""
import argparse, glob, os, sqlite3, sys

DB = os.environ.get("HESTIA_DB", "data/hestia.db")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--simpan", type=int, default=5000)
    ap.add_argument("--r-simpan", type=int, default=50)
    ap.add_argument("--kering", action="store_true", help="hitung saja, tidak menghapus")
    a = ap.parse_args()

    if not os.path.exists(a.db):
        raise SystemExit("db tidak ada: %s" % a.db)

    c = sqlite3.connect(a.db)
    c.execute("pragma busy_timeout=5000")
    total = c.execute("select count(*) from bukti").fetchone()[0]
    dirujuk = {r[0] for r in c.execute(
        "select bukti_terakhir from status_konten where bukti_terakhir is not null")}
    id_urut = [r[0] for r in c.execute("select id from bukti order by id desc")]
    calon = [i for i in id_urut[a.simpan:] if i not in dirujuk]
    dilindungi = len([i for i in id_urut[a.simpan:] if i in dirujuk])

    print("bukti: %d baris | disimpan %d | dilindungi(tautan) %d | akan dihapus %d"
          % (total, a.simpan, dilindungi, len(calon)))
    if not a.kering and calon:
        for i in range(0, len(calon), 500):
            bagian = calon[i:i + 500]
            c.execute("delete from bukti where id in (%s)" % ",".join("?" * len(bagian)), bagian)
        c.commit()
    sisa = c.execute("select count(*) from bukti").fetchone()[0]
    c.close()

    berkas = sorted(glob.glob("docs/evidence/R-*.txt"),
                    key=lambda f: os.path.getmtime(f))
    hapus_r = berkas[:-a.r_simpan] if len(berkas) > a.r_simpan else []
    print("log R: %d berkas | akan dihapus %d" % (len(berkas), len(hapus_r)))
    if not a.kering:
        for f in hapus_r:
            try:
                os.remove(f)
            except OSError:
                pass

    print("bukti sisa:", sisa)
    return 0


if __name__ == "__main__":
    sys.exit(main())
