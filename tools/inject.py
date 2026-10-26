#!/usr/bin/env python3
"""Bukti A->B: ambil konten situs A, tulis ke berkas situs B lewat jalur J5.
Jalankan di VPS dengan HESTIA_LOKAL=1, atau di laptop (memakai ssh)."""
import argparse, datetime, hashlib, os, re, sqlite3, subprocess, urllib.request

DB = "data/hestia.db"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124 Safari/537.36 Hestia/1.0")
SSH = ["ssh", "-p", "10053", "-i", os.path.expanduser("~/.ssh/wesearch_vps_key"),
       "-o", "StrictHostKeyChecking=no", "administrator@93.127.133.160"]
LOKAL = os.environ.get("HESTIA_LOKAL") == "1"
SNAP = "data/snapshot"


def sh(p, masuk=None):
    argv = ["bash", "-lc", p] if LOKAL else SSH + [p]
    r = subprocess.run(argv, input=masuk, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def baca(url, t=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "id,en"})
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.status, r.read().decode("utf-8", "replace")


def utama():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dari", required=True)
    ap.add_argument("--ke", required=True)
    ap.add_argument("--berkas", default="/var/www/waspadaweb/index.html")
    ap.add_argument("--penanda", default="HESTIA-INJECT")
    ap.add_argument("--db", default=DB)
    ap.add_argument("--terapkan", action="store_true")
    ap.add_argument("--pulih", action="store_true")
    a = ap.parse_args()

    os.makedirs(SNAP, exist_ok=True)
    fsnap = os.path.join(SNAP, re.sub(r"[^a-z0-9]+", "-", a.ke.lower()).strip("-") + ".html")

    if a.pulih:
        if not os.path.exists(fsnap):
            raise SystemExit("snapshot tidak ada: " + fsnap)
        rc, _, err = sh("sudo tee %s >/dev/null" % a.berkas, open(fsnap).read())
        print("  pulih rc=%s %s" % (rc, err.strip()[:90]))
        return

    kode_a, isi_a = baca(a.dari)
    sha_a = hashlib.sha256(isi_a.encode()).hexdigest()
    print("  A %s -> http %s | sha256=%s | panjang=%d" % (a.dari, kode_a, sha_a[:16], len(isi_a)))

    rc, asli, _ = sh("sudo cat %s" % a.berkas)
    ada = asli.strip() != "" and "No such file" not in asli
    sha_asli = hashlib.sha256(asli.encode()).hexdigest()
    print("  B %s -> %s | sha256_asli=%s | panjang=%d" % (a.ke, a.berkas, sha_asli[:16], len(asli)))

    if a.terapkan and a.penanda in asli and sha_a[:16] in asli:
        print("  sudah terpasang (idempoten) - tidak menulis ulang")
        return

    isi = re.sub(r'(href|src)="/', r'\1="%s/' % a.dari.rstrip("/"), isi_a)
    cap = ('<!-- %s sumber=%s sha256=%s waktu=%s -->'
           % (a.penanda, a.dari, sha_a, datetime.datetime.now().astimezone().isoformat(timespec="seconds")))
    banner = ('<div id="hestia-penanda" style="font:14px/1.5 -apple-system,Segoe UI,sans-serif;'
              'background:#111;color:#eee;padding:10px 14px">'
              '<b>%s</b> &middot; sumber: <a style="color:#8cf" href="%s">%s</a> &middot; sha256 %s'
              '</div>' % (a.penanda, a.dari, a.dari, sha_a[:16]))
    baru = cap + "\n" + banner + "\n" + isi

    if not a.terapkan:
        print("  (belum --terapkan) cuplikan:", baru[:120].replace("\n", " "))
        return

    if ada:
        open(fsnap, "w").write(asli)
        print("  snapshot asli disimpan: %s" % fsnap)
    rc, _, err = sh("sudo tee %s >/dev/null" % a.berkas, baru)
    print("  tulis ke B rc=%s %s" % (rc, err.strip()[:90]))

    c = sqlite3.connect(a.db)
    kols = [r[1] for r in c.execute("pragma table_info(change_event)")]
    b = {"jenis": "inject-a-b", "jalur": "J5", "nilai_lama": sha_asli[:16], "nilai_baru": sha_a[:16],
         "vantage": "lokal+vps", "catatan": "%s -> %s" % (a.dari, a.ke),
         "waktu": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    b = {k: v for k, v in b.items() if k in kols}
    c.execute("insert into change_event (%s) values (%s)" % (", ".join(b), ", ".join("?" * len(b))), tuple(b.values()))
    c.commit()
    print("  change_event dicatat (jenis inject-a-b)")


if __name__ == "__main__":
    utama()
