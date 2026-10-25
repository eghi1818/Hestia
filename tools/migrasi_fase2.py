#!/usr/bin/env python3
"""Fase 2: tabel registri -- registry halaman parasite sesuai GOAL Modul 1. Idempoten."""
import argparse
import sqlite3
import sys
import time
from pathlib import Path

AKAR = Path(__file__).resolve().parents[1]
DB = AKAR / "data" / "hestia.db"
CADANGAN = AKAR / "data" / "backup"

DDL = """
CREATE TABLE IF NOT EXISTS registri (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_id INTEGER,
  host TEXT NOT NULL,
  url TEXT NOT NULL UNIQUE,
  platform TEXT,
  jenis_penempatan TEXT,
  tayang_at TEXT,
  kata_kunci TEXT,
  biaya REAL,
  mata_uang TEXT DEFAULT 'IDR',
  kontrak TEXT,
  pemilik_host TEXT,
  kendali_editorial TEXT,
  status TEXT DEFAULT 'aktif',
  sumber TEXT DEFAULT 'manual',
  catatan TEXT,
  diperbarui TEXT,
  dibuat TEXT
);
CREATE INDEX IF NOT EXISTS idx_registri_host ON registri(host);
CREATE INDEX IF NOT EXISTS idx_registri_status ON registri(status);
CREATE INDEX IF NOT EXISTS idx_registri_tayang ON registri(tayang_at);
"""


def cadangkan():
    CADANGAN.mkdir(parents=True, exist_ok=True)
    cap = time.strftime("%Y%m%d-%H%M%S")
    tujuan = CADANGAN / ("hestia-%s.db" % cap)
    n = 0
    while tujuan.exists():
        n += 1
        tujuan = CADANGAN / ("hestia-%s-%d.db" % (cap, n))
    with sqlite3.connect(DB) as c:
        c.execute("VACUUM INTO ?", (str(tujuan),))
    return tujuan


def catat_versi(c, versi, keterangan):
    """Catat versi memakai kolom skema_versi yang benar-benar ada."""
    import hashlib
    kol = [r[1] for r in c.execute("PRAGMA table_info(skema_versi)")]
    if not kol:
        print("  (skema_versi tidak ada, lewati catatan versi)")
        return
    kunci = "nama" if "nama" in kol else "versi"
    cap = time.strftime("%Y-%m-%dT%H:%M:%S")
    h = hashlib.sha256((DDL + versi).encode("utf-8")).hexdigest()[:16]
    peta = [("nama", versi), ("versi", versi), ("keterangan", keterangan),
            ("dijalankan_pada", cap), ("waktu", cap), ("diterapkan", cap), ("hash", h)]
    nilai = {k: v for k, v in peta if k in kol}
    if not nilai:
        print("  (kolom skema_versi tidak dikenali, lewati)")
        return
    c.execute("DELETE FROM skema_versi WHERE %s=?" % kunci, (versi,))
    kolom = ", ".join(nilai)
    tanda = ", ".join("?" * len(nilai))
    c.execute("INSERT INTO skema_versi (%s) VALUES (%s)" % (kolom, tanda), tuple(nilai.values()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paksa-gagal", action="store_true")
    ap.add_argument("--paksa-akhir", action="store_true")
    a = ap.parse_args()
    if not DB.exists():
        sys.exit("DB tidak ada: %s" % DB)

    tujuan = cadangkan()
    print("cadangan:", tujuan.relative_to(AKAR))

    with sqlite3.connect(DB) as c:
        c.executescript(DDL)
        catat_versi(c, "fase2", "tabel registri untuk Modul 1 GOAL" + (" (dipaksa)" if a.paksa_akhir else ""))
        n_versi = c.execute("select count(*) from skema_versi where nama=?", ("fase2",)).fetchone()[0]
        print("catatan versi fase2:", n_versi)
        if n_versi < 1:
            sys.exit("GAGAL: catatan versi tidak tertulis")
        integritas = c.execute("PRAGMA integrity_check").fetchone()[0]
        print("integritas:", integritas)
        if integritas != "ok":
            sys.exit("integritas gagal")
        kol = [r[1] for r in c.execute("PRAGMA table_info(registri)")]
        n = c.execute("select count(*) from registri").fetchone()[0]
        print("registri: %d kolom, %d baris" % (len(kol), n))
        print("  kolom:", ", ".join(kol))

    if a.paksa_gagal:
        print("(dipaksa gagal: cadangan tetap ada, tanpa catatan versi)")


if __name__ == "__main__":
    main()
