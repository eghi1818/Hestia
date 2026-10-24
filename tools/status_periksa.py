#!/usr/bin/env python3
"""Modul 5 - Link Rot Monitor.

Periksa status setiap halaman konten, lalu dorong transisi status HANYA lewat
aturan izin='otomatis' di tabel transisi_status. Yang izin='manusia' dicatat
sebagai usulan. Read-only tanpa --terapkan.
"""
import argparse, json, os, re, sqlite3, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import uji_probe  # noqa: E402

DB = os.environ.get("HESTIA_DB", "data/hestia.db")
PETA = {"tidak_ada": "kedaluwarsa", "nyata": "terverifikasi"}
TIDAK_PASTI = ("blokir", "tantangan", "tidak_dapat_disimpulkan")


def kolom(c, tabel):
    return [r[1] for r in c.execute("pragma table_info(%s)" % tabel)]


def kolom_wajib(c, tabel):
    """Kolom NOT NULL tanpa default (selain PK) -> wajib diisi saat insert."""
    return [r[1] for r in c.execute("pragma table_info(%s)" % tabel)
            if r[3] and r[4] is None and not r[5]]


def cek_wajib(c, tabel, d):
    kurang = [k for k in kolom_wajib(c, tabel) if k not in d]
    if kurang:
        raise SystemExit("%s: kolom wajib belum diisi -> %s" % (tabel, kurang))


def tipe_kolom(c, tabel, kolom):
    for r in c.execute("pragma table_info(%s)" % tabel):
        if r[1] == kolom:
            return (r[2] or "").upper()
    return ""


def nilai_enum(c, tabel, kolom, prioritas=()):
    """Ambil nilai sah dari CHECK constraint, bukan nilai karangan."""
    row = c.execute("select sql from sqlite_master where name=?", (tabel,)).fetchone()
    sql = (row[0] if row else "") or ""
    m = re.search(r"\b%s\b[^,()]*?check\s*\(([^)]*)\)" % kolom, sql, re.I | re.S)
    if not m:
        return None
    sah = re.findall(r"'([^']+)'", m.group(1))
    for p in prioritas:
        for x in sah:
            if p in x:
                return x
    return sah[0] if sah else None


def pilih(kol, *kandidat):
    for k in kandidat:
        if k in kol:
            return k
    return None


def aturan(c):
    """Baca lewat NAMA kolom, bukan urutan - kolom id di depan pernah bikin bug senyap."""
    kol = kolom(c, "transisi_status")
    d = pilih(kol, "dari", "dari_status", "status_dari")
    k = pilih(kol, "ke", "ke_status", "status_ke", "tujuan")
    i = pilih(kol, "izin", "mode", "tipe")
    assert d and k and i, ("kolom transisi_status tak dikenali", kol)
    return {(a, b): z for a, b, z in c.execute(
        "select %s,%s,%s from transisi_status" % (d, k, i))}


def ambil_daftar(c, domain, batas):
    kk = kolom(c, "konten")
    k_url = pilih(kk, "url", "tautan", "alamat")
    k_id = pilih(kk, "id", "konten_id")
    k_peran = pilih(kk, "peran")
    if not k_url or not k_id:
        return []
    sql = "select %s, %s from konten" % (k_id, k_url)
    if k_peran:
        sql += " where %s='tanam'" % k_peran
    if domain:
        sql += (" and " if k_peran else " where ") + "%s like ?" % k_url
        baris = c.execute(sql + " limit ?", ("%" + domain + "%", batas)).fetchall()
    else:
        baris = c.execute(sql + " limit ?", (batas,)).fetchall()
    return baris


def tautkan_bukti(c, kid, bid):
    """Tandai bukti terakhir untuk konten tanpa menyentuh status."""
    kol = kolom(c, "status_konten")
    if not bid or not kol:
        return
    d = {}
    if "bukti_terakhir" in kol:
        d["bukti_terakhir"] = bid
    if "diperbarui" in kol:
        d["diperbarui"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if not d:
        return
    c.execute("update status_konten set %s where konten_id=?" % ",".join("%s=?" % k for k in d),
              list(d.values()) + [kid])


def catat_bukti(c, kid, hasil):
    """Tulis baris bukti lengkap, kembalikan bukti.id untuk ditautkan."""
    kb = kolom(c, "bukti")
    if not kb:
        return None
    kelas = hasil.get("kelas")
    verdict = {"nyata": "lulus", "tidak_ada": "gagal"}.get(kelas, "tak_konklusif")
    d = {"mata": 1, "metode": "uji_probe.uji",
         "job_id": (int(os.environ["HESTIA_JOB_ID"]) if os.environ.get("HESTIA_JOB_ID") else None),
         "verdict": nilai_enum(c, "bukti", "verdict", (verdict,)) or verdict,
         "nilai": kelas, "keterangan": json.dumps(
             {"konten_id": kid, "url": hasil.get("url"), "kode": hasil.get("kode"),
              "kelas": kelas, "catatan": hasil.get("catatan")},
             ensure_ascii=False)[:2000],
         "waktu": time.strftime("%Y-%m-%d %H:%M:%S")}
    d = {k: v for k, v in d.items() if k in kb}
    if not d:
        return None
    cek_wajib(c, "bukti", d)
    cur = c.execute("insert into bukti(%s) values(%s)" % (",".join(d), ",".join("?" * len(d))),
                    list(d.values()))
    return cur.lastrowid


def tulis_status(c, kid, tujuan, hasil, bukti_id=None):
    kol = kolom(c, "status_konten")
    waktu = time.strftime("%Y-%m-%d %H:%M:%S")
    ada = c.execute("select 1 from status_konten where konten_id=?", (kid,)).fetchone()
    d = {}
    for nama, nilai in (("status", tujuan), ("basis", "bukti" if "bukti" in kol else None),
                        ("bukti_terakhir", bukti_id if "bukti_terakhir" in kol else None),
                        ("diperbarui", waktu)):
        if nama in kol and nilai is not None:
            d[nama] = nilai
    if ada:
        setel = ",".join("%s=?" % k for k in d)
        c.execute("update status_konten set %s where konten_id=?" % setel,
                  list(d.values()) + [kid])
        return "update"
    d["konten_id"] = kid
    cek_wajib(c, "status_konten", d)
    c.execute("insert into status_konten(%s) values(%s)" % (",".join(d), ",".join("?" * len(d))),
              list(d.values()))
    return "insert"


def daftar_metrik(c):
    """metrik hanya punya nama/sumber/status_sumber/terisi_terakhir/catatan.

    Angka taruh di catatan; API yang menghitung. Ini registry, bukan penyimpan nilai.
    """
    kol = kolom(c, "metrik")
    waktu = time.strftime("%Y-%m-%d %H:%M:%S")
    for nama, status in (("konten.kedaluwarsa", "kedaluwarsa"),
                         ("konten.terverifikasi", "terverifikasi")):
        nilai = c.execute("select count(*) from status_konten where status=?", (status,)).fetchone()[0]
        d = {"nama": nama, "sumber": "uji_probe",
             "status_sumber": nilai_enum(c, "metrik", "status_sumber", ("terisi", "ada")) or "terisi",
             "terisi_terakhir": waktu,
             "catatan": "jumlah halaman konten berstatus %s; terakhir: %d" % (status, nilai)}
        d = {k: v for k, v in d.items() if k in kol}
        ada = c.execute("select 1 from metrik where nama=?", (nama,)).fetchone()
        if ada:
            setel = ",".join("%s=?" % k for k in d if k != "nama")
            c.execute("update metrik set %s where nama=?" % setel,
                      [v for k, v in d.items() if k != "nama"] + [nama])
        else:
            cek_wajib(c, "metrik", d)
            c.execute("insert into metrik(%s) values(%s)" % (",".join(d), ",".join("?" * len(d))),
                      list(d.values()))


def catat_clientlog(c, peristiwa, rincian):
    try:
        kol = kolom(c, "clientlog")
        d = {}
        for nama, nilai in (("waktu", time.strftime("%Y-%m-%d %H:%M:%S")),
                            ("peristiwa", peristiwa), ("rincian", rincian[:300])):
            if nama in kol:
                d[nama] = nilai
        cek_wajib(c, "clientlog", d)
        c.execute("insert into clientlog(%s) values(%s)" % (",".join(d), ",".join("?" * len(d))),
                  list(d.values()))
    except Exception as e:
        print("clientlog dilewati:", e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="")
    ap.add_argument("posisi_domain", nargs="?", default="")
    ap.add_argument("--batas", type=int, default=5)
    ap.add_argument("--jeda", type=float, default=uji_probe.JEDA)
    ap.add_argument("--kontrol", default=None)
    ap.add_argument("--terapkan", action="store_true")
    ap.add_argument("--db", default=DB)
    a = ap.parse_args()

    if not a.domain and a.posisi_domain:
        a.domain = a.posisi_domain
    c = sqlite3.connect(a.db)
    c.row_factory = sqlite3.Row
    izin = aturan(c)
    daftar = ambil_daftar(c, a.domain, a.batas)
    hasil, dorong, usul, tak_pasti = [], [], [], []

    for kid, url in daftar:
        h = uji_probe.uji(url, a.kontrol, a.jeda)
        kls = h["kelas"]
        status_lama = None
        try:
            r = c.execute("select status from status_konten where konten_id=?", (kid,)).fetchone()
            status_lama = r["status"] if r else None
        except Exception:
            pass
        tujuan = PETA.get(kls)
        aksi = "tetap"
        if kls in TIDAK_PASTI:
            tak_pasti.append({"konten_id": kid, "url": url, "kelas": kls})
            tujuan = None
            aksi = "tak-pasti"
        if tujuan and status_lama and tujuan != status_lama:
            if izin.get((status_lama, tujuan)) == "otomatis":
                aksi = "transisi"
                dorong.append({"konten_id": kid, "url": url, "dari": status_lama, "ke": tujuan})
            else:
                aksi = "usul"
                usul.append({"konten_id": kid, "url": url, "dari": status_lama, "ke": tujuan})
        elif tujuan and not status_lama:
            aksi = "transisi"
            dorong.append({"konten_id": kid, "url": url, "dari": None, "ke": tujuan})

        bid = None
        if a.terapkan:
            bid = catat_bukti(c, kid, h)
            if aksi == "transisi":
                mode = tulis_status(c, kid, tujuan, h, bid)
                aksi = "terapkan:" + mode
            else:
                tautkan_bukti(c, kid, bid)
        item = {"konten_id": kid, "url": url, "kode": h["kode"], "kelas": kls, "aksi": aksi}
        if bid:
            item["bukti"] = bid
        hasil.append(item)

    ringkas = {"diperiksa": len(hasil), "transisi": len(dorong), "usul_manusia": len(usul),
               "tidak_dapat_disimpulkan": len(tak_pasti), "terapkan": bool(a.terapkan)}
    if a.terapkan:
        daftar_metrik(c)
        catat_clientlog(c, "status-periksa",
                        "diperiksa=%d transisi=%d usul=%d tak_pasti=%d"
                        % (len(hasil), len(dorong), len(usul), len(tak_pasti)))
        c.commit()
    print(json.dumps({"ringkas": ringkas, "item": hasil, "dorong": dorong,
                      "usul": usul, "tak_pasti": tak_pasti}, indent=2, ensure_ascii=False))
    c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
