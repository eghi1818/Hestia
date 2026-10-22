#!/usr/bin/env python3
import base64, json, os, sys, time, urllib.request

B = "http://127.0.0.1:8787"
AK = "%s:%s" % (os.environ.get("HESTIA_USER", "eghi"), os.environ.get("HESTIA_SANDI", "hestia"))
H = {"Authorization": "Basic " + base64.b64encode(AK.encode()).decode(), "Content-Type": "application/json"}


def p(j, m=None):
    d = json.dumps(m).encode() if m is not None else None
    r = urllib.request.Request(B + j, data=d, headers=H, method="POST" if d else "GET")
    return json.loads(urllib.request.urlopen(r, timeout=30).read().decode())


def tunggu(jid, batas):
    lihat, n, s = False, 0, "jalan"
    t0 = time.time()
    while time.time() - t0 < batas:
        time.sleep(1)
        s = p("/api/job/%d" % jid)["job"]["status"]
        b = p("/api/job/%d/log?sejak=0" % jid).get("baris", [])
        n = max(n, len(b))
        if s == "jalan" and b:
            lihat = True
        if s != "jalan":
            break
    return s, n, lihat, time.time() - t0


def uji(label, m, batas, ada=None, tolak=False):
    print("--- uji:", label)
    h = p("/api/konsol/jalankan", m)
    if tolak:
        print("   tolak:", h.get("sebab") if not h.get("ok") else "TIDAK ditolak")
        return not h.get("ok")
    if not h.get("ok"):
        print("   GAGAL:", h.get("sebab"))
        return False
    jid = h["job_id"]
    print("   job=%s r=%s argv=%s" % (jid, h.get("r_nomor"), " ".join(h.get("argv", []))))
    s, n, lihat, durasi = tunggu(jid, batas)
    path = p("/api/job/%d" % jid)["job"]["stdout_path"]
    uk = os.path.getsize(path) if os.path.exists(path) else 0
    isi = open(path, encoding="utf-8", errors="ignore").read() if uk else ""
    ok = True
    if s == "jalan":
        print("   GAGAL: masih jalan %ss" % batas); ok = False
    if n < 2:
        print("   GAGAL: log %d baris" % n); ok = False
    if durasi >= 2.0 and not lihat:
        print("   GAGAL: tak ada baris terlihat selama job berjalan (%.1fs)" % durasi); ok = False
    if not isi.startswith("[sys] mulai"):
        print("   GAGAL: baris pertama bukti bukan [sys] mulai"); ok = False
    if uk == 0:
        print("   GAGAL: bukti kosong"); ok = False
    if ada and ada not in isi:
        print("   GAGAL: tak memuat %r" % ada); ok = False
    print("   status=%s durasi=%.1fs baris=%d ukuran=%d lihat=%s" % (s, durasi, n, uk, lihat))
    return ok


def main():
    hasil = [uji("aksi cepat (sql)", {"aksi": "sql", "extra": "SELECT 1"}, 20, ada="1")]
    d = p("/api/konsol/aksi").get("aksi", [])
    pakai = [a for a in d if a.get("pakai_domain") and not a.get("menulis")]
    print("--- aksi berdomain tanpa menulis:", [a["nama"] for a in pakai] or "TIDAK ADA")
    if pakai:
        a = min(pakai, key=lambda x: x.get("batas_detik") or 9999)
        hasil.append(uji("berdomain (%s)" % a["nama"], {"aksi": a["nama"], "domain": "waspadaweb.com"},
                         int(a.get("batas_detik") or 120) + 20))
    hasil.append(uji("penjaga mode=pantau", {"aksi": "tanam", "domain": "badungkab.go.id"}, 5, tolak=True))
    print("UJI KONSOL:", "LULUS" if all(hasil) else "GAGAL")
    return 0 if all(hasil) else 1


if __name__ == "__main__":
    sys.exit(main())
