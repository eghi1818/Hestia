#!/usr/bin/env python3
"""Pengurai berkas REA (blok F-2). Deteksi format dari ISI, simpan asli, tandai field kurang."""
import argparse, csv, hashlib, io, json, re, sqlite3, sys, time
from pathlib import Path

AKAR = Path(__file__).resolve().parents[1]
DB = AKAR / "data" / "hestia.db"
ALIAS = {
    "kode_j": ("kode_j", "kode j", "jalur", "jalur masuk", "kode", "j", "path"),
    "target": ("target", "host", "domain", "situs", "site"),
    "bukti": ("bukti", "evidence", "proof", "screenshot"),
    "cara_tulis": ("cara_tulis", "cara tulis", "cara", "metode", "write", "tulis"),
    "status": ("status", "keadaan", "state"),
    "confirmed": ("confirmed", "terkonfirmasi", "konfirmasi"),
    "proven": ("proven", "terbukti", "uji"),
    "catatan": ("catatan", "note", "notes", "keterangan"),
}
WAJIB = ("kode_j", "target")


def bersih(t):
    return re.sub(r"[ \t]+", " ", (t or "").strip())


def petakan(k):
    k = re.sub(r"[^a-z0-9_ ]+", "", (k or "").strip().lower())
    for baku, daftar in ALIAS.items():
        if k in daftar:
            return baku
    return k.replace(" ", "_") or "tanpa_nama"


def deteksi(isi):
    t = isi.lstrip()
    if t[:1] in "{[":
        return "json"
    baris = [b for b in isi.splitlines() if b.strip()]
    if baris and all(b.count(",") >= 1 for b in baris[:5]) and not baris[0].lstrip().startswith("#"):
        return "csv"
    if any(b.lstrip().startswith("#") for b in baris[:20]) or ":" in isi:
        return "md"
    return "tidak_dikenal"


def _b(u, j, k, v, a):
    return {"urutan": u, "jenis": j, "kunci": petakan(k), "nilai": bersih(v), "asli": a}


def urai_md(isi):
    out, u = [], 0
    for baris in isi.splitlines():
        if baris.lstrip().startswith("#"):
            u += 1
            out.append(_b(u, "judul", "judul", baris.lstrip("#").strip(), baris))
            continue
        m = re.match(r"^\s*[-*]?\s*([^:]{2,40}):\s*(.+)$", baris)
        if m:
            u += 1
            out.append(_b(u, "field", m.group(1), m.group(2), baris))
    return out


def urai_json(isi):
    out, u = [], 0

    def jalan(o, p=""):
        nonlocal u
        if isinstance(o, dict):
            for k, v in o.items():
                jalan(v, (p + "." + k) if p else k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                jalan(v, "%s[%d]" % (p, i))
        else:
            u += 1
            out.append(_b(u, "field", p.split(".")[-1], str(o), "%s=%s" % (p, o)))

    jalan(json.loads(isi))
    return out


def urai_csv(isi):
    out, u = [], 0
    for i, baris in enumerate(csv.DictReader(io.StringIO(isi))):
        for k, v in baris.items():
            if k is None:
                continue
            u += 1
            out.append(_b(u, "baris%d" % (i + 1), k, v or "", "%s=%s" % (k, v)))
    return out


def urai(isi):
    f = deteksi(isi)
    blok = {"json": urai_json, "csv": urai_csv, "md": urai_md}.get(f, lambda x: [])(isi)
    kunci = {b["kunci"] for b in blok}
    return {"format": f, "blok": blok, "kurang": [w for w in WAJIB if w not in kunci],
            "sha256": hashlib.sha256(isi.encode("utf-8")).hexdigest()}


def simpan(nama, isi, hasil, target_id=None):
    with sqlite3.connect(DB) as c:
        for rid_lama in [r[0] for r in c.execute("select id from berkas_rea where sha256=?", (hasil["sha256"],))]:
            c.execute("delete from blok where berkas_rea_id=?", (rid_lama,))
            c.execute("delete from berkas_rea where id=?", (rid_lama,))
        cur = c.execute(
            "insert into berkas_rea (target_id,nama,format,ukuran,sha256,sumber,isi_asli,diunggah,catatan)"
            " values (?,?,?,?,?,?,?,?,?)",
            (target_id, nama, hasil["format"], len(isi.encode("utf-8")), hasil["sha256"],
             "urai:rea.py", isi, time.strftime("%Y-%m-%dT%H:%M:%S"),
             ("kurang: " + ",".join(hasil["kurang"])) if hasil["kurang"] else None))
        rid = cur.lastrowid
        for b in hasil["blok"]:
            c.execute(
                "insert into blok (berkas_rea_id,urutan,jenis,asli,normalisasi,sha256,kunci_json)"
                " values (?,?,?,?,?,?,?)",
                (rid, b["urutan"], b["jenis"], b["asli"], b["nilai"],
                 hashlib.sha256(b["nilai"].encode("utf-8")).hexdigest()[:16],
                 json.dumps({"kunci": b["kunci"]}, ensure_ascii=False)))
    return rid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("berkas")
    ap.add_argument("--target-id", type=int)
    ap.add_argument("--simpan", action="store_true")
    a = ap.parse_args()
    p = Path(a.berkas)
    if not p.exists():
        sys.exit("berkas tidak ada: %s" % p)
    isi = p.read_text(encoding="utf-8", errors="replace")
    h = urai(isi)
    print("format:", h["format"], "| blok:", len(h["blok"]), "| sha256:", h["sha256"][:16])
    print("field wajib hilang:", h["kurang"] or "tidak ada")
    for b in h["blok"][:10]:
        print("   %2d %-10s %-12s %s" % (b["urutan"], b["jenis"], b["kunci"], b["nilai"][:58]))
    if a.simpan:
        print("disimpan: berkas_rea id=%d" % simpan(p.name, isi, h, a.target_id))


if __name__ == "__main__":
    main()
