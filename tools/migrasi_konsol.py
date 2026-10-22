#!/usr/bin/env python3
"""S-136: kolom mode, tabel konsol, whitelist, daftar 3 situs uji. Idempoten."""
import json
import shutil
import sqlite3
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
DB = AKAR / "data" / "hestia.db"

DDL = {
"job": """CREATE TABLE IF NOT EXISTS job(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 target_id INTEGER,
 aksi TEXT NOT NULL,
 argv TEXT NOT NULL,
 r_nomor TEXT UNIQUE,
 status TEXT NOT NULL DEFAULT 'antre'
   CHECK(status IN ('antre','jalan','lulus','gagal','tak_konklusif','batal','timeout','terputus')),
 stdout_path TEXT,
 pid INTEGER,
 detak TEXT,
 mulai TEXT,
 selesai TEXT,
 created_at TEXT NOT NULL DEFAULT (datetime('now')))""",
"job_log": """CREATE TABLE IF NOT EXISTS job_log(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 job_id INTEGER NOT NULL,
 urutan INTEGER NOT NULL,
 aliran TEXT NOT NULL DEFAULT 'out' CHECK(aliran IN ('out','err','sys')),
 baris TEXT,
 waktu TEXT NOT NULL DEFAULT (datetime('now')))""",
"langkah": """CREATE TABLE IF NOT EXISTS langkah(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 job_id INTEGER NOT NULL,
 urutan INTEGER NOT NULL,
 argv TEXT NOT NULL,
 kode_keluar INTEGER,
 mulai TEXT,
 selesai TEXT)""",
"bukti": """CREATE TABLE IF NOT EXISTS bukti(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 job_id INTEGER,
 mata INTEGER NOT NULL,
 metode TEXT NOT NULL,
 nilai TEXT,
 sha256 TEXT,
 verdict TEXT NOT NULL CHECK(verdict IN ('lulus','gagal','tak_konklusif')),
 keterangan TEXT,
 waktu TEXT NOT NULL DEFAULT (datetime('now')))""",
"status_konten": """CREATE TABLE IF NOT EXISTS status_konten(
 konten_id INTEGER PRIMARY KEY,
 status TEXT NOT NULL CHECK(status IN ('belum','tertanam','kedaluwarsa','ditimpa','gagal','dicabut')),
 basis TEXT NOT NULL DEFAULT 'bukti' CHECK(basis IN ('bukti','manual')),
 bukti_terakhir INTEGER,
 diperbarui TEXT NOT NULL DEFAULT (datetime('now')))""",
"kredensial_uji": """CREATE TABLE IF NOT EXISTS kredensial_uji(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 kredensial_id INTEGER NOT NULL,
 metode TEXT NOT NULL,
 hasil TEXT NOT NULL CHECK(hasil IN ('lulus','gagal')),
 pesan TEXT,
 diuji_pada TEXT NOT NULL DEFAULT (datetime('now')))""",
"whitelist": """CREATE TABLE IF NOT EXISTS whitelist(
 nama TEXT PRIMARY KEY,
 biner TEXT NOT NULL,
 argumen_tetap TEXT NOT NULL DEFAULT '[]',
 pola TEXT NOT NULL DEFAULT '',
 argumen_utuh INTEGER NOT NULL DEFAULT 0,
 menulis INTEGER NOT NULL DEFAULT 0,
 batas_detik INTEGER NOT NULL DEFAULT 120,
 deskripsi TEXT DEFAULT '',
 aktif INTEGER NOT NULL DEFAULT 1)""",
}
INDEKS = ["CREATE INDEX IF NOT EXISTS idx_job_log_job ON job_log(job_id, urutan)",
          "CREATE INDEX IF NOT EXISTS idx_bukti_job ON bukti(job_id)",
          "CREATE INDEX IF NOT EXISTS idx_job_status ON job(status)"]

UJI = [("waspadaweb.com", "uji"), ("persaudaraan.com", "uji"), ("juraganit.com", "uji")]

def py_venv():
    p = AKAR / ".venv" / "bin" / "python"
    return str(p) if p.exists() else str(Path(sys.executable).resolve())

POLA = r"^[-A-Za-z0-9@._:+=/,]+$"
POLA_LUAS = r"^[-A-Za-z0-9@._:+=/,;!$%&*?()'\"]+$"
PY, BASH, SQL = py_venv(), shutil.which("bash") or "/bin/bash", shutil.which("sqlite3") or "sqlite3"

WHITELIST = [
 ("teknologi", PY, ["tools/teknologi.py"], POLA, 0, 0, 120, "tebak teknologi target"),
 ("pintu",     PY, ["tools/pintu.py"],     POLA, 0, 0, 120, "petakan pintu target"),
 ("kanal",     PY, ["tools/kanal.py"],     POLA, 0, 0, 120, "nilai kanal target"),
 ("asal",      PY, ["tools/asal.py"],      POLA, 0, 0, 180, "cari origin"),
 ("jejak",     PY, ["tools/jejak.py"],     POLA, 0, 0, 180, "lacak jejak"),
 ("hosting",   PY, ["tools/hosting.py"],   POLA, 0, 0, 120, "cek kebocoran hosting"),
 ("tanam",     PY, ["-u", "tools/tanam.py"], POLA_LUAS, 0, 1, 240, "tanam konten (menulis)"),
 ("gate",      BASH, ["tools/gate.sh"], "", 0, 0, 180, "jalankan gate"),
 ("smoke",     BASH, ["tools/smoke.sh"], "", 0, 0, 120, "smoke test layanan"),
 ("sql",       SQL, ["data/hestia.db"], POLA_LUAS, 1, 0, 60, "query baca"),
]

c = sqlite3.connect(str(DB))
kol = [r[1] for r in c.execute("PRAGMA table_info(targets)")]
if "mode" not in kol:
    c.execute("ALTER TABLE targets ADD COLUMN mode TEXT NOT NULL DEFAULT 'pantau'")
    print("+ kolom targets.mode ditambahkan")
else:
    print("= kolom targets.mode sudah ada")
c.execute("UPDATE targets SET mode='pantau' WHERE mode IS NULL OR mode=''")
print("+ semua target lama disetel mode='pantau'")

for nama, ddl in DDL.items():
    c.execute(ddl)
    print("+ tabel siap:", nama)
for ix in INDEKS:
    c.execute(ix)

for dom, mode in UJI:
    c.execute("INSERT OR IGNORE INTO targets(domain,tipe,status,mode,owner,tags,catatan) "
              "VALUES(?,?,?,?,?,?,?)", (dom, "lain", "baru", mode, "eghi", "situs-uji", "situs uji"))
    print("+ situs uji didaftarkan:", dom, "mode=%s" % mode)

for w in WHITELIST:
    c.execute("INSERT OR REPLACE INTO whitelist(nama,biner,argumen_tetap,pola,argumen_utuh,menulis,batas_detik,deskripsi,aktif) "
              "VALUES(?,?,?,?,?,?,?,?,1)",
              (w[0], w[1], json.dumps(w[2]), w[3], w[4], w[5], w[6], w[7]))
print("+ whitelist terisi:", len(WHITELIST), "aksi")

c.commit()
print("--- ringkas ---")
print("targets:", c.execute("SELECT COUNT(*) FROM targets").fetchone()[0])
print("mode uji:", c.execute("SELECT COUNT(*) FROM targets WHERE mode='uji'").fetchone()[0])
print("mode pantau:", c.execute("SELECT COUNT(*) FROM targets WHERE mode='pantau'").fetchone()[0])
print("tabel baru:", ", ".join(sorted(DDL)))
c.close()
