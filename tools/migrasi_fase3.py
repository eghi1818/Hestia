#!/usr/bin/env python3
"""Fase 3 (blok F-1): skema jalur dan tabel pendukung M0-M4. Idempoten.

Tabel: jalur, berkas_rea, blok, page, change_event, status_check.
Tidak menyentuh tabel lama.
"""
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
CREATE TABLE IF NOT EXISTS jalur (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_id INTEGER NOT NULL,
  kode_J TEXT NOT NULL,
  bukti TEXT,
  terbukti_bisa_tulis INTEGER NOT NULL DEFAULT 0,
  waktu_uji TEXT,
  cara_tulis TEXT,
  catatan TEXT,
  diperbarui TEXT,
  UNIQUE (target_id, kode_J)
);
CREATE INDEX IF NOT EXISTS idx_jalur_target ON jalur(target_id);
CREATE INDEX IF NOT EXISTS idx_jalur_bisa ON jalur(terbukti_bisa_tulis);

CREATE TABLE IF NOT EXISTS berkas_rea (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_id INTEGER,
  nama TEXT NOT NULL,
  format TEXT,
  ukuran INTEGER,
  sha256 TEXT,
  sumber TEXT,
  isi_asli TEXT,
  diunggah TEXT,
  catatan TEXT
);
CREATE INDEX IF NOT EXISTS idx_rea_target ON berkas_rea(target_id);
CREATE INDEX IF NOT EXISTS idx_rea_sha ON berkas_rea(sha256);

CREATE TABLE IF NOT EXISTS blok (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  berkas_rea_id INTEGER NOT NULL,
  urutan INTEGER,
  jenis TEXT,
  asli TEXT,
  normalisasi TEXT,
  sha256 TEXT,
  kunci_json TEXT,
  catatan TEXT
);
CREATE INDEX IF NOT EXISTS idx_blok_rea ON blok(berkas_rea_id);

CREATE TABLE IF NOT EXISTS page (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_id INTEGER NOT NULL,
  url TEXT NOT NULL,
  judul TEXT,
  status_http INTEGER,
  penanda_ada INTEGER DEFAULT 0,
  sha256_konten TEXT,
  diambil TEXT,
  vantage TEXT,
  catatan TEXT,
  UNIQUE (target_id, url)
);
CREATE INDEX IF NOT EXISTS idx_page_target ON page(target_id);

CREATE TABLE IF NOT EXISTS change_event (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_id INTEGER,
  page_id INTEGER,
  jenis TEXT NOT NULL,
  jalur TEXT,
  nilai_lama TEXT,
  nilai_baru TEXT,
  penanda TEXT,
  bukti_id INTEGER,
  vantage TEXT,
  waktu TEXT
);
CREATE INDEX IF NOT EXISTS idx_ce_target ON change_event(target_id);
CREATE INDEX IF NOT EXISTS idx_ce_page ON change_event(page_id);

CREATE TABLE IF NOT EXISTS status_check (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  page_id INTEGER,
  url TEXT,
  status_http INTEGER,
  vantage TEXT,
  sha256_konten TEXT,
  bukti_id INTEGER,
  waktu TEXT
);
CREATE INDEX IF NOT EXISTS idx_sc_page ON status_check(page_id);
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


TABEL = ("jalur", "berkas_rea", "blok", "page", "change_event", "status_check")


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
        catat_versi(c, "fase3", "skema jalur + pendukung M0-M4" + (" (dipaksa)" if a.paksa_akhir else ""))
        n_versi = c.execute("select count(*) from skema_versi where nama=?", ("fase3",)).fetchone()[0]
        print("catatan versi fase3:", n_versi)
        if n_versi < 1:
            sys.exit("GAGAL: catatan versi tidak tertulis")

        integritas = c.execute("PRAGMA integrity_check").fetchone()[0]
        print("integritas:", integritas)
        if integritas != "ok":
            sys.exit("GAGAL: integritas")

        for t in TABEL:
            kol = [r[1] for r in c.execute("PRAGMA table_info(%s)" % t)]
            idx = [r[1] for r in c.execute("PRAGMA index_list(%s)" % t)]
            print("  %-13s kolom %2d | indeks %d" % (t, len(kol), len(idx)))

        for t in TABEL:
            ada = c.execute("select count(*) from sqlite_master where type='table' and name=?", (t,)).fetchone()[0]
            if ada != 1:
                sys.exit("GAGAL: tabel %s tidak ada" % t)
        print("semua tabel F-1 ada")

    if a.paksa_gagal:
        print("(dipaksa gagal)")


if __name__ == "__main__":
    main()
