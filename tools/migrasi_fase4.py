#!/usr/bin/env python3
"""Fase 4 (blok F-7): tabel donor -- konten dari situs lain. Idempoten."""
import argparse
import hashlib
import sqlite3
import sys
import time
from pathlib import Path

AKAR = Path(__file__).resolve().parents[1]
DB = AKAR / "data" / "hestia.db"
CADANGAN = AKAR / "data" / "backup"

DDL = """
CREATE TABLE IF NOT EXISTS donor (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT NOT NULL,
  target_id INTEGER,
  diambil TEXT,
  status_http INTEGER,
  tipe_konten TEXT,
  sha256 TEXT,
  panjang_mentah INTEGER,
  panjang_bersih INTEGER,
  judul TEXT,
  isi_mentah TEXT,
  isi_bersih TEXT,
  catatan TEXT
);
CREATE INDEX IF NOT EXISTS idx_donor_url ON donor(url);
CREATE INDEX IF NOT EXISTS idx_donor_sha ON donor(sha256);
"""


def cadangkan():
    CADANGAN.mkdir(parents=True, exist_ok=True)
    cap = time.strftime("%Y%m%d-%H%M%S")
    t = CADANGAN / ("hestia-%s.db" % cap)
    n = 0
    while t.exists():
        n += 1
        t = CADANGAN / ("hestia-%s-%d.db" % (cap, n))
    with sqlite3.connect(DB) as c:
        c.execute("VACUUM INTO ?", (str(t),))
    return t


def catat_versi(c, versi, ket):
    kol = [r[1] for r in c.execute("PRAGMA table_info(skema_versi)")]
    if not kol:
        return
    kunci = "nama" if "nama" in kol else "versi"
    cap = time.strftime("%Y-%m-%dT%H:%M:%S")
    h = hashlib.sha256((DDL + versi).encode()).hexdigest()[:16]
    peta = [("nama", versi), ("versi", versi), ("keterangan", ket), ("dijalankan_pada", cap),
            ("waktu", cap), ("diterapkan", cap), ("hash", h)]
    nilai = {k: v for k, v in peta if k in kol}
    c.execute("DELETE FROM skema_versi WHERE %s=?" % kunci, (versi,))
    c.execute("INSERT INTO skema_versi (%s) VALUES (%s)" % (", ".join(nilai), ", ".join("?" * len(nilai))),
              tuple(nilai.values()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paksa-akhir", action="store_true")
    a = ap.parse_args()
    if not DB.exists():
        sys.exit("DB tidak ada")
    print("cadangan:", cadangkan().relative_to(AKAR))
    with sqlite3.connect(DB) as c:
        c.executescript(DDL)
        catat_versi(c, "fase4", "tabel donor (konten dari situs lain)")
        n = c.execute("select count(*) from skema_versi where nama='fase4'").fetchone()[0]
        print("catatan versi fase4:", n)
        if n < 1:
            sys.exit("GAGAL: catatan versi")
        print("integritas:", c.execute("PRAGMA integrity_check").fetchone()[0])
        print("kolom donor:", len([r[1] for r in c.execute("PRAGMA table_info(donor)")]))


if __name__ == "__main__":
    main()
