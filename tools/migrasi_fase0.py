#!/usr/bin/env python3
# migrasi_fase0.py - status 'terverifikasi', konten.peran, indeks url,
# transisi_status, metrik, ledger skema_versi. Idempoten + post-condition.
# Cadangan memakai VACUUM INTO (aman walau ada penulis hidup).
# --paksa-gagal : keluar 1 SESUDAH cadangan (menguji jalur cadangan)
# --paksa-akhir : menandai post-condition gagal (menguji jalur assertion)
import hashlib, os, sqlite3, sys, time

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(AKAR, "data", "hestia.db")
NAMA = "fase0"

STATUS = ("belum", "tertanam", "terverifikasi", "kedaluwarsa", "ditimpa", "gagal", "dicabut")
CHECK = "status TEXT NOT NULL CHECK(status IN (%s))" % ",".join("'%s'" % s for s in STATUS)

TRANSISI = [
    ("belum", "tertanam", "otomatis", "unggah terverifikasi"),
    ("tertanam", "terverifikasi", "otomatis", "cek pasca tanam"),
    ("tertanam", "gagal", "otomatis", "unggah gagal"),
    ("terverifikasi", "ditimpa", "otomatis", "blok kita hilang"),
    ("terverifikasi", "kedaluwarsa", "otomatis", "halaman mati di pihak host"),
    ("terverifikasi", "dicabut", "manusia", "kita pensiunkan"),
    ("ditimpa", "tertanam", "manusia", "tanam ulang"),
    ("gagal", "tertanam", "manusia", "coba ulang"),
    ("kedaluwarsa", "tertanam", "manusia", "tanam ulang"),
]

METRIK = [
    ("konten.posisi", None, "tanpa_sumber", "peringkat keyword, butuh sumber SERP"),
    ("konten.status_indeks", None, "tanpa_sumber", "status indeks, butuh GSC/vendor"),
]

def kolom(k, tabel):
    return [r[1] for r in k.execute("pragma table_info(%s)" % tabel)]

def tambah_kolom(k, tabel, nama, definisi):
    if nama not in kolom(k, tabel):
        k.execute("ALTER TABLE %s ADD COLUMN %s %s" % (tabel, nama, definisi))
        print("  kolom %s.%s: ditambah" % (tabel, nama))


def ada(k, nama):
    return k.execute("select 1 from sqlite_master where name=?", (nama,)).fetchone() is not None

def sambung():
    k = sqlite3.connect(DB, isolation_level=None)
    k.row_factory = sqlite3.Row
    k.execute("pragma busy_timeout = 5000")
    k.execute("pragma journal_mode = wal")
    return k

def main():
    paksa_awal = "--paksa-gagal" in sys.argv
    paksa_akhir = "--paksa-akhir" in sys.argv
    paksa_rebuild = "--paksa-rebuild" in sys.argv
    if not os.path.exists(DB):
        print("[GALAT] tidak ada %s" % DB); return 1
    k = sambung()
    print("journal_mode: %s" % k.execute("pragma journal_mode").fetchone()[0])
    cad = DB + ".bak." + time.strftime("%Y%m%d-%H%M%S")
    _n = 1
    while os.path.exists(cad):
        _n += 1
        cad = "%s-%d" % (DB + ".bak." + time.strftime("%Y%m%d-%H%M%S"), _n)
    k.execute("VACUUM INTO ?", (cad,))
    ic = k.execute("attach database ? as c", (cad,))
    ic = k.execute("pragma c.integrity_check").fetchone()[0]
    k.execute("detach database c")
    print("cadangan: %s (integritas: %s)" % (os.path.basename(cad), ic))
    if ic != "ok":
        print("[GALAT] cadangan tidak sehat, migrasi dibatalkan"); return 1
    if paksa_awal:
        print("[PAKSA] keluar 1 SESUDAH cadangan"); return 1

    sebelum = k.execute("select count(*) from status_konten").fetchone()[0] if ada(k, "status_konten") else 0
    print("status_konten sebelum: %d" % sebelum)

    sql = (k.execute("select sql from sqlite_master where name='status_konten'").fetchone() or {})
    perlu = paksa_rebuild or (not ada(k, "status_konten")) or ("terverifikasi" not in ((sql["sql"] if sql else "") or ""))
    if perlu:
        k.execute("pragma foreign_keys = OFF")
        k.execute("BEGIN")
        k.execute("DROP TABLE IF EXISTS status_konten_b")
        k.execute("""CREATE TABLE status_konten_b(
 konten_id INTEGER PRIMARY KEY, %s,
 basis TEXT NOT NULL DEFAULT 'bukti' CHECK(basis IN ('bukti','manual')),
 bukti_terakhir INTEGER,
 diperbarui TEXT NOT NULL DEFAULT (datetime('now')))""" % CHECK)
        if ada(k, "status_konten"):
            k.execute("""INSERT INTO status_konten_b(konten_id,status,basis,bukti_terakhir,diperbarui)
                         SELECT konten_id,status,basis,bukti_terakhir,diperbarui FROM status_konten""")
            k.execute("DROP TABLE status_konten")
        k.execute("ALTER TABLE status_konten_b RENAME TO status_konten")
        k.execute("COMMIT")
        k.execute("pragma foreign_keys = ON")
        print("status_konten: dibangun ulang")
    else:
        print("status_konten: sudah memuat terverifikasi")

    if "peran" not in [r[1] for r in k.execute("pragma table_info(konten)")]:
        k.execute("ALTER TABLE konten ADD COLUMN peran TEXT NOT NULL DEFAULT 'tanam'")
        print("konten.peran: ditambah")
    else:
        print("konten.peran: sudah ada")
    k.execute("CREATE INDEX IF NOT EXISTS idx_konten_url ON konten(url)")

    k.execute("""CREATE TABLE IF NOT EXISTS transisi_status(
 dari TEXT NOT NULL, ke TEXT NOT NULL, izin TEXT NOT NULL DEFAULT 'otomatis', catatan TEXT,
 PRIMARY KEY(dari,ke))""")
    for a, b, c, d in TRANSISI:
        k.execute("INSERT OR IGNORE INTO transisi_status(dari,ke,izin,catatan) VALUES(?,?,?,?)", (a, b, c, d))
    k.execute("""CREATE TABLE IF NOT EXISTS metrik(
 nama TEXT PRIMARY KEY, sumber TEXT, status_sumber TEXT NOT NULL DEFAULT 'tanpa_sumber',
 terisi_terakhir TEXT, catatan TEXT)""")
    for _k, _d in (("nama", "TEXT"), ("sumber", "TEXT"),
                   ("status_sumber", "TEXT NOT NULL DEFAULT 'tanpa_sumber'"),
                   ("terisi_terakhir", "TEXT"), ("catatan", "TEXT")):
        tambah_kolom(k, "metrik", _k, _d)
    for nama, sumber, st, cat in METRIK:
        k.execute("INSERT OR IGNORE INTO metrik(nama,sumber,status_sumber,catatan) VALUES(?,?,?,?)",
                  (nama, sumber, st, cat))
    k.execute("""CREATE TABLE IF NOT EXISTS skema_versi(
 nama TEXT PRIMARY KEY, dijalankan_pada TEXT NOT NULL, hash TEXT)""")
    k.execute("INSERT OR REPLACE INTO skema_versi(nama,dijalankan_pada,hash) VALUES(?,?,?)",
              (NAMA, time.strftime("%Y-%m-%dT%H:%M:%S"),
               hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]))

    gagal = []
    if not ada(k, "status_konten"):
        gagal.append("status_konten hilang")
    else:
        s2 = k.execute("select sql from sqlite_master where name='status_konten'").fetchone()[0]
        if "terverifikasi" not in s2:
            gagal.append("CHECK tidak memuat terverifikasi")
        n2 = k.execute("select count(*) from status_konten").fetchone()[0]
        if n2 != sebelum:
            gagal.append("baris status_konten %d -> %d" % (sebelum, n2))
    if "peran" not in [r[1] for r in k.execute("pragma table_info(konten)")]:
        gagal.append("konten.peran tidak ada")
    if not ada(k, "idx_konten_url"):
        gagal.append("idx_konten_url tidak ada")
    nm = k.execute("select count(*) from metrik").fetchone()[0]
    if nm < len(METRIK):
        gagal.append("metrik %d baris, harus >= %d" % (nm, len(METRIK)))
    fk = k.execute("pragma foreign_key_check").fetchall()
    if fk:
        gagal.append("pelanggaran FK: %d" % len(fk))
    if paksa_akhir:
        gagal.append("(paksa-akhir)")
    for g in gagal:
        print("  [GAGAL] %s" % g)
    print("post-condition: %s" % ("LULUS" if not gagal else "GAGAL"))
    k.close()
    return 1 if gagal else 0

if __name__ == "__main__":
    sys.exit(main())
