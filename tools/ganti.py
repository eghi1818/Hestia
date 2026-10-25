#!/usr/bin/env python3
"""M2 GANTI: pasang konten donor ke halaman target lewat jalur J5 (blok F-8/F-9).

Aturan: penanda wajib, snapshot diambil HANYA saat halaman belum pernah disentuh Hestia,
verifikasi dari 2 vantage, idempoten, dan rollback kembali ke isi asli.
"""
import argparse
import base64
import hashlib
import html
import json
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import bunuh as B

AKAR = Path(__file__).resolve().parents[1]
DB = AKAR / "data" / "hestia.db"
SNAP = AKAR / "data" / "snapshot"
DOCROOT = B.DOCROOT
TANDA = "hestia-ganti donor="


def baca_file(path):
    return B.ct("cat %s" % path) or ""


def tulis_file(path, isi):
    b64 = base64.b64encode(isi.encode("utf-8")).decode()
    B.ct("mkdir -p $(dirname %s)" % path)
    B.ct('printf "%%s" %s | base64 -d > %s' % (b64, path))
    B.ct("chmod 644 %s" % path)


def hapus_file(path):
    B.ct("rm -f %s" % path)


def penanda(donor):
    return ("<!-- hestia-ganti donor=%s donor_sha=%s nonce=%s utc=%s -->"
            % (donor["url"], donor["sha256"][:16], donor["sha256"][:12], donor["diambil"]))


def bangun(donor):
    return "\n".join([
        penanda(donor),
        "<!doctype html>",
        '<html lang="id"><head><meta charset="utf-8">',
        "<title>GANTI: %s</title>" % html.escape(donor["judul"] or donor["url"]),
        "</head><body>",
        "<h1>Halaman ini diganti oleh Hestia</h1>",
        '<p>Donor: <a href="%s">%s</a><br>sha256 donor: %s</p>'
        % (donor["url"], html.escape(donor["url"]), donor["sha256"][:16]),
        '<pre id="hestia-isi">%s</pre>' % html.escape(donor["isi_bersih"] or ""),
        "</body></html>",
        "<!-- hestia-ganti end -->",
        "",
    ])


def ambil_donor(donor_id):
    with sqlite3.connect(DB) as c:
        c.row_factory = sqlite3.Row
        r = c.execute("select * from donor where id=?", (donor_id,)).fetchone()
    return dict(r) if r else None


def pid_dan_snap_asli(target_id, url):
    """id page, dan snapshot asli (event ganti paling awal) bila ada."""
    with sqlite3.connect(DB) as c:
        c.execute("insert or ignore into page (target_id,url) values (?,?)", (target_id, url))
        pid = c.execute("select id from page where target_id=? and url=?", (target_id, url)).fetchone()[0]
        r = c.execute("select nilai_lama from change_event where jenis in ('ganti','ganti-asli')"
                      " and page_id=? order by id asc limit 1", (pid,)).fetchone()
    nama = None
    if r and r[0]:
        try:
            nama = json.loads(r[0]).get("snapshot")
        except Exception:
            nama = None
    return pid, nama


def asli(target_id, path, url=None):
    """Tetapkan isi SEKARANG sebagai isi asli (dasar rollback). Hapus riwayat ganti page ini."""
    url = url or ("https://waspadaweb.com%s" % path)
    with sqlite3.connect(DB) as c:
        c.execute("insert or ignore into page (target_id,url) values (?,?)", (target_id, url))
        pid = c.execute("select id from page where target_id=? and url=?", (target_id, url)).fetchone()[0]
        c.execute("delete from change_event where page_id=?", (pid,))
        c.commit()
    snap, sha, ada = snapshot_halaman(path)
    with sqlite3.connect(DB) as c:
        c.execute("insert into change_event (target_id,page_id,jenis,jalur,nilai_lama,nilai_baru,penanda,vantage,waktu)"
                  " values (?,?,?,?,?,?,?,?,?)",
                  (target_id, pid, "ganti-asli", "J5", json.dumps({"snapshot": str(snap)}),
                   sha[:16], 0, "lokal", time.strftime("%Y-%m-%dT%H:%M:%S")))
        c.commit()
    print("isi asli ditetapkan:", snap.name, "| sha:", sha[:16], "| ada isi:", ada)
    return 0


def snapshot_halaman(path):
    SNAP.mkdir(parents=True, exist_ok=True)
    lama = baca_file("%s%sindex.html" % (DOCROOT, path))
    cap = time.strftime("%Y%m%d-%H%M%S")
    nama = "halaman-%s-%s.html" % (path.strip("/").replace("/", "-") or "akar", cap)
    p = SNAP / nama
    n = 0
    while p.exists():
        n += 1
        p = SNAP / nama.replace(".html", "-%d.html" % n)
    p.write_text(lama, encoding="utf-8")
    return p, hashlib.sha256(lama.encode("utf-8")).hexdigest(), bool(lama.strip())


def catat(target_id, pid, path, url, sha, st, penanda_ada, snap, aksi, harap_penanda):
    cap = time.strftime("%Y-%m-%dT%H:%M:%S")
    lulus = (st.get("lokal") == "200") and (bool(penanda_ada) == bool(harap_penanda))
    with sqlite3.connect(DB) as c:
        c.execute("update page set status_http=?, sha256_konten=?, penanda_ada=?, diambil=?, vantage=? where id=?",
                  (int(st.get("lokal", "0")) if st.get("lokal", "").isdigit() else 0, sha,
                   1 if penanda_ada else 0, cap, "vps+lokal", pid))
        c.execute("insert into change_event (target_id,page_id,jenis,jalur,nilai_lama,nilai_baru,penanda,vantage,waktu)"
                  " values (?,?,?,?,?,?,?,?,?)",
                  (target_id, pid, aksi, "J5", json.dumps({"status": st, "snapshot": str(snap)}),
                   sha[:16], penanda_ada, "vps+lokal", cap))
        for vantage, nilai in st.items():
            c.execute("insert into status_check (page_id,url,status_http,vantage,sha256_konten,waktu)"
                      " values (?,?,?,?,?,?)",
                      (pid, url, int(nilai) if nilai.isdigit() else 0, vantage, sha, cap))
            c.execute("insert into bukti (mata,metode,verdict,nilai,sha256,keterangan,waktu)"
                      " values (?,?,?,?,?,?,?)",
                      (1, aksi, "lulus" if lulus else "gagal", vantage, sha,
                       json.dumps({"target_id": target_id, "path": path, "url": url, "vantage": vantage,
                                   "penanda_ada": penanda_ada, "harap_penanda": harap_penanda,
                                   "snapshot": str(snap)}), cap))
        c.commit()
    return lulus


def pasang(target_id, path, donor_id, url=None, dry_run=False):
    donor = ambil_donor(donor_id)
    if not donor:
        sys.exit("donor id=%s tidak ada" % donor_id)
    url = url or ("https://waspadaweb.com%s" % path)
    pid, snap_asli = pid_dan_snap_asli(target_id, url)
    isi_lama = baca_file("%s%sindex.html" % (DOCROOT, path))

    if TANDA in isi_lama and snap_asli and Path(snap_asli).exists():
        snap = Path(snap_asli)
        sha_lama = hashlib.sha256(snap.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        print("sudah pernah diganti; snapshot asli dipakai:", snap.name)
    else:
        snap, sha_lama, _ = snapshot_halaman(path)
        print("snapshot asli dibuat:", snap.name, "| sha isi asli:", sha_lama[:16])

    isi = bangun(donor)
    sha_baru = hashlib.sha256(isi.encode("utf-8")).hexdigest()
    print("penanda:", penanda(donor))
    print("sha berkas baru:", sha_baru[:16])
    if dry_run:
        print("dry-run: tidak menulis")
        return 0
    tulis_file("%s%sindex.html" % (DOCROOT, path), isi)
    st = B.status(url)
    pen = penanda(donor) in B.baca_penuh(url)[1]
    print("status:", st, "| penanda terlihat publik:", pen)
    lulus = catat(target_id, pid, path, url, sha_baru, st, pen, snap, "ganti", True)
    print("HASIL:", "LULUS" if lulus else "GAGAL")
    return 0 if lulus else 1


def pulih(target_id, path, url=None):
    url = url or ("https://waspadaweb.com%s" % path)
    pid, snap_asli = pid_dan_snap_asli(target_id, url)
    berkas = "%s%sindex.html" % (DOCROOT, path)
    isi_asli = ""
    if snap_asli and Path(snap_asli).exists():
        isi_asli = Path(snap_asli).read_text(encoding="utf-8")
    if isi_asli.strip():
        tulis_file(berkas, isi_asli)
        print("dipulihkan dari snapshot ASLI:", Path(snap_asli).name)
    else:
        hapus_file(berkas)
        print("tidak ada isi asli; berkas dihapus")
    st = B.status(url)
    pen = TANDA in B.baca_penuh(url)[1]
    sha = hashlib.sha256(isi_asli.encode("utf-8")).hexdigest()
    print("status:", st, "| penanda ganti masih ada:", pen, "(harus False)")
    lulus = catat(target_id, pid, path, url, sha, st, pen, Path(snap_asli) if snap_asli else SNAP,
                  "pulih-ganti", False)
    print("HASIL:", "LULUS" if lulus else "GAGAL")
    return 0 if lulus else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pasang")
    p.add_argument("--target-id", type=int, required=True)
    p.add_argument("--path", required=True)
    p.add_argument("--donor-id", type=int, required=True)
    p.add_argument("--url")
    p.add_argument("--dry-run", action="store_true")
    x = sub.add_parser("asli")
    x.add_argument("--target-id", type=int, required=True)
    x.add_argument("--path", required=True)
    x.add_argument("--url")
    q = sub.add_parser("pulih")
    q.add_argument("--target-id", type=int, required=True)
    q.add_argument("--path", required=True)
    q.add_argument("--url")
    s = sub.add_parser("status")
    s.add_argument("--path", required=True)
    a = ap.parse_args()
    if a.cmd == "pasang":
        sys.exit(pasang(a.target_id, a.path, a.donor_id, a.url, a.dry_run))
    if a.cmd == "asli":
        sys.exit(asli(a.target_id, a.path, a.url))
    if a.cmd == "pulih":
        sys.exit(pulih(a.target_id, a.path, a.url))
    print(B.status("https://waspadaweb.com%s" % a.path))


if __name__ == "__main__":
    main()
