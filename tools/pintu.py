"""Peta pintu tulis: cari permukaan yang bisa ditulis pada sebuah domain.

Tanpa kredensial apa pun dan tanpa asumsi pemilik. Hanya membaca yang publik,
lalu menyimpulkan pintu mana yang terbuka dan butuh apa untuk membukanya.
"""
import re
import socket
import sys
import urllib.error
import urllib.request

HDR = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
}

PINTU = [
    ("wp_login", "/wp-login.php", "wp"),
    ("wp_rest", "/wp-json/wp/v2/pages", "wp"),
    ("wp_xmlrpc", "/xmlrpc.php", "wp"),
    ("wp_reg", "/wp-login.php?action=register", "wp"),
    ("joomla", "/administrator/", "joomla"),
    ("drupal", "/user/login", "drupal"),
    ("moodle", "/login/index.php", "moodle"),
    ("admin", "/admin/", "umum"),
    ("panel", "/panel/", "umum"),
    ("cpanel", "/cpanel", "hosting"),
    ("git", "/.git/HEAD", "sumber"),
    ("env", "/.env", "rahasia"),
]

PORTA = [(21, "ftp"), (22, "ssh"), (2083, "cpanel"), (3306, "mysql")]


def ambil(domain, jalur, t=10):
    req = urllib.request.Request("https://" + domain + jalur, headers=HDR)
    try:
        with urllib.request.urlopen(req, timeout=t) as x:
            return x.status, x.read(30000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def porta(domain, port, t=4):
    try:
        s = socket.create_connection((domain, port), timeout=t)
        s.settimeout(2.5)
        try:
            b = s.recv(120).decode("utf-8", "ignore").strip()
        except Exception:
            b = ""
        s.close()
        return b or "(tanpa spanduk)"
    except Exception:
        return None


def periksa(domain):
    print("== %s ==" % domain)
    s, t = ambil(domain, "/")
    jenis = []
    if s == 200:
        if re.search(r"/_next/", t):
            jenis.append("next.js")
        if re.search(r"wp-content|wp-includes", t):
            jenis.append("wordpress")
        if re.search(r"joomla", t, re.I):
            jenis.append("joomla")
        if re.search(r"comment-form|commentform", t):
            jenis.append("form komentar")
    print("   depan : http=%s | jenis=%s" % (s, ", ".join(jenis) or "-"))
    print("   pintu :")
    buka = []
    for nama, jalur, guna in PINTU:
        k, _ = ambil(domain, jalur)
        if k in (200, 301, 302, 401, 403):
            print("     %-10s %-30s http=%-4s %s" % (nama, jalur, k, "BUKA" if k == 200 else "DIJAGA"))
            buka.append(guna)
    print("   porta :")
    for p, nama in PORTA:
        b = porta(domain, p)
        if b:
            print("     %-7s %-5s terbuka | %s" % (nama, p, b[:60]))
    s, t = ambil(domain, "/robots.txt")
    if s == 200:
        d = sorted(set(re.findall(r"(?im)^\s*Disallow:\s*(\S+)", t)))[:15]
        if d:
            print("   robots menunjuk:", ", ".join(d))
    print("   butuh untuk menulis:", ", ".join(sorted(set(buka))) or "-")
    print()


def daftar():
    import sqlite3
    try:
        c = sqlite3.connect("data/hestia.db")
        return [r[0] for r in c.execute("select domain from targets order by id limit 6")]
    except Exception:
        return []


if __name__ == "__main__":
    for d in (sys.argv[1:] or daftar()):
        periksa(d)
