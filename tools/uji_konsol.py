#!/usr/bin/env python3
"""S-137: uji penerimaan konsol. Exit 0 = LULUS, 1 = GAGAL."""
import base64
import json
import os
import sys
import time
import urllib.request

BASIS = "http://127.0.0.1:8787"
AKUN = "%s:%s" % (os.environ.get("HESTIA_USER", "eghi"), os.environ.get("HESTIA_SANDI", "hestia"))
HDR = {"Authorization": "Basic " + base64.b64encode(AKUN.encode()).decode(),
       "Content-Type": "application/json"}


def panggil(jalur, muatan=None):
    data = json.dumps(muatan).encode() if muatan is not None else None
    r = urllib.request.Request(BASIS + jalur, data=data, headers=HDR,
                               method="POST" if data else "GET")
    with urllib.request.urlopen(r, timeout=20) as x:
        return json.loads(x.read().decode())


def uji(label, muatan, batas, harus_ada=None):
    print("--- uji: %s ---" % label)
    h = panggil("/api/konsol/jalankan", muatan)
    if not h.get("ok"):
        print("   GAGAL: %s" % h.get("sebab"))
        return False
    jid = h["job_id"]
    print("   job_id=%s r=%s" % (jid, h.get("r_nomor")))
    terlihat_saat_jalan, baris_maks, status = False, 0, "jalan"
    t0 = time.time()
    while time.time() - t0 < batas:
        time.sleep(2)
        status = panggil("/api/job/%d" % jid)["job"]["status"]
        lb = panggil("/api/job/%d/log?sejak=0" % jid).get("baris", [])
        baris_maks = max(baris_maks, len(lb))
        if status == "jalan" and lb:
            terlihat_saat_jalan = True
        if status != "jalan":
            break
    j = panggil("/api/job/%d" % jid)["job"]
    path = j["stdout_path"]
    ukuran = os.path.getsize(path) if os.path.exists(path) else 0
    isi = open(path, encoding="utf-8", errors="ignore").read() if ukuran else ""
    ok = True
    if status == "jalan":
        print("   GAGAL: masih jalan setelah %ss" % batas); ok = False
    if baris_maks < 2:
        print("   GAGAL: log kosong (%d baris)" % baris_maks); ok = False
    if not terlihat_saat_jalan:
        print("   GAGAL: tidak ada baris terlihat selama status masih 'jalan'"); ok = False
    if ukuran == 0:
        print("   GAGAL: berkas bukti kosong"); ok = False
    if harus_ada and harus_ada not in isi:
        print("   GAGAL: keluaran tidak memuat %r" % harus_ada); ok = False
    print("   status=%s baris=%d ukuran=%d terlihat_saat_jalan=%s" % (status, baris_maks, ukuran, terlihat_saat_jalan))
    return ok


def main():
    hasil = [uji("aksi cepat (sql)", {"aksi": "sql", "extra": "SELECT 1"}, 20, harus_ada="1"),
             uji("aksi nyata (teknologi)", {"aksi": "teknologi", "domain": "badungkab.go.id"}, 100)]
    print("UJI KONSOL: %s" % ("LULUS" if all(hasil) else "GAGAL"))
    return 0 if all(hasil) else 1


if __name__ == "__main__":
    sys.exit(main())
