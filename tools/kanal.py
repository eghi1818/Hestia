"""Pilih kanal tulis untuk sebuah domain, dari yang paling ringan.

Tingkat 0 tanpa akun | 1 akun aplikasi | 2 berkas server | 3 pipa deploy | 4 tepi CDN
"""
import re
import socket
import sys
import urllib.error
import urllib.request

HDR = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
       "Accept-Language": "id-ID,id;q=0.9,en;q=0.8"}
T0 = [("/wp-login.php?action=register", "registrasi WP"), ("/buku-tamu", "buku tamu"), ("/guestbook", "buku tamu")]
T1 = [("/wp-login.php", "wp"), ("/wp-json/wp/v2/pages", "wp-rest"), ("/administrator/", "joomla"),
      ("/user/login", "drupal"), ("/login/index.php", "moodle"), ("/phpmyadmin/", "phpmyadmin"),
      ("/admin/", "admin"), ("/panel/", "panel")]
T3 = [("/.git/HEAD", "git terbuka"), ("/package.json", "package.json")]
NAMA2 = ["ftp", "mail", "cpanel", "direct", "server", "host", "webmail", "smtp", "ns1", "dev"]


def ambil(d, jalur, t=12):
    try:
        r = urllib.request.Request("https://" + d + jalur, headers=HDR)
        with urllib.request.urlopen(r, timeout=t) as x:
            return x.status, x.read(40000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def ip_dari(n):
    try:
        return sorted(set(a[4][0] for a in socket.getaddrinfo(n, None, socket.AF_INET)))
    except Exception:
        return []


def porta(host, p, t=3):
    try:
        s = socket.create_connection((host, p), timeout=t)
        s.settimeout(2)
        try:
            b = s.recv(120).decode("utf-8", "ignore").strip()
        except Exception:
            b = ""
        s.close()
        return b or "(tanpa spanduk)"
    except Exception:
        return None


def periksa(d):
    print("== %s ==" % d)
    st, isi = ambil(d, "/")
    tek = []
    if re.search(r"/_next/", isi):
        tek.append("next.js")
    if re.search(r"wp-content|wp-includes", isi):
        tek.append("wordpress")
    if re.search(r"comment-form|commentform|name=[\"']comment", isi):
        tek.append("kolom komentar")
    print("   muka   : http=%s | teknologi=%s" % (st, ", ".join(tek) or "-"))
    t0 = []
    for jalur, nama in T0:
        k, body = ambil(d, jalur)
        if k == 200 and re.search(r"<form|user_login|register", body, re.I):
            t0.append(nama)
    if "kolom komentar" in tek:
        t0.append("komentar")
    print("   t0 tanpa akun :", ", ".join(t0) or "-")
    t1 = []
    for jalur, nama in T1:
        k, _ = ambil(d, jalur)
        if k in (200, 401, 403):
            t1.append("%s(%s)" % (nama, k))
    print("   t1 akun CMS   :", ", ".join(t1) or "-")
    t2 = []
    for n in NAMA2:
        for ip in ip_dari(n + "." + d):
            if not ip.startswith(("104.", "172.")):
                for p in (21, 22, 2083, 2087):
                    b = porta(ip, p)
                    if b:
                        t2.append("%s:%s/%s" % (n, p, b[:22]))
    print("   t2 berkas     :", ", ".join(t2) or "-")
    t3 = []
    for jalur, nama in T3:
        k, _ = ambil(d, jalur)
        if k == 200:
            t3.append(nama)
    if tek:
        t3.append("build " + tek[0])
    print("   t3 pipa deploy:", ", ".join(t3) or "-")
    print("   KANAL TERPILIH:", " -> ".join(t0 + t1 + t2 + t3) or "tidak ada")
    print()


if __name__ == "__main__":
    for d in (sys.argv[1:] or ["wecash.ai"]):
        periksa(d)
