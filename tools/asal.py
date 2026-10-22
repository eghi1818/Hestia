"""Cari server asli sebuah domain di balik CDN.

CDN (Cloudflare) menyembunyikan IP asli. Modul ini mengumpulkan nama
subdomain dari sumber publik, memisahkan yang masih di belakang CDN dari
yang terbuka, lalu memeriksa porta panel dan menyapa HTTP-nya.
"""
import json
import re
import socket
import subprocess
import sys
import urllib.request

KAMUS = """www mail ftp cpanel webmail smtp pop imap ns1 ns2 dev staging api admin portal
direct origin server host vps cloud backup db mysql cdn static assets test old new blog shop
app m mobile secure login panel whm autodiscover autoconfig gw vpn remote git jenkins
beta demo crm erp kb support help docs store ftp2 server1 server2 host1 cpanel2""".split()

CF = ["173.245", "103.21", "103.22", "103.31", "141.101", "108.162", "190.93",
      "188.114", "197.234", "198.41", "162.158", "162.159", "131.0.72"]
CF += ["104.%d" % i for i in range(16, 28)]
CF += ["172.%d" % i for i in range(64, 72)]

PORTA = [21, 22, 80, 443, 2083, 2087, 3306, 8443, 8888, 10000]


def http(url, t=15, host=None):
    h = {"User-Agent": "Mozilla/5.0 (Macintosh) Chrome/121.0.0.0"}
    if host:
        h["Host"] = host
    try:
        r = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(r, timeout=t) as x:
            return x.status, x.read(300000).decode("utf-8", "ignore")
    except Exception:
        return 0, ""


def crtsh(d):
    s, t = http("https://crt.sh/?q=%25." + d + "&output=json", 45)
    if s != 200:
        return set()
    out = set()
    try:
        for e in json.loads(t):
            for n in str(e.get("name_value", "")).split("\n"):
                n = n.strip().lower()
                if n.endswith(d) and "*" not in n:
                    out.add(n)
    except Exception:
        pass
    return out


def rapiddns(d):
    s, t = http("https://rapiddns.io/subdomain/" + d + "?full=1", 30)
    return set(re.findall(r"\b([a-z0-9_-]+\." + re.escape(d) + r")\b", t.lower())) if s == 200 else set()


def hackertarget(d):
    s, t = http("https://api.hackertarget.com/hostsearch/?q=" + d, 25)
    return set(l.split(",")[0].lower() for l in t.splitlines() if "," in l) if s == 200 else set()


def dig(d, jenis):
    try:
        o = subprocess.run(["dig", "+short", d, jenis], capture_output=True, text=True, timeout=15)
        return [x.strip() for x in o.stdout.splitlines() if x.strip()]
    except Exception:
        return []


def ip_dari(nama):
    try:
        return sorted(set(a[4][0] for a in socket.getaddrinfo(nama, None, socket.AF_INET)))
    except Exception:
        return []


def di_cf(ip):
    return any(ip.startswith(p + ".") for p in CF)


def porta(ip, p, t=3):
    try:
        s = socket.create_connection((ip, p), timeout=t)
        s.settimeout(2)
        try:
            b = s.recv(140).decode("utf-8", "ignore").strip()
        except Exception:
            b = ""
        s.close()
        return b or "(tanpa spanduk)"
    except Exception:
        return None


def periksa(d):
    print("== asal %s ==" % d)
    kump = {}
    for label, fn in (("crt.sh", crtsh), ("rapiddns", rapiddns), ("hackertarget", hackertarget)):
        n = fn(d)
        print("   %-12s: %d nama" % (label, len(n)))
        for x in n:
            kump[x] = 1
    for x in KAMUS:
        kump[x + "." + d] = 1
    kump[d] = 1
    print("   total nama : %d" % len(kump))
    print("   NS         :", ", ".join(dig(d, "NS")) or "-")
    print("   MX         :", ", ".join(dig(d, "MX")) or "-")
    print("   TXT        :", " | ".join(x[:90] for x in dig(d, "TXT")[:3]) or "-")

    terbuka = {}
    for nama in sorted(kump):
        for ip in ip_dari(nama):
            if not di_cf(ip):
                terbuka.setdefault(ip, set()).add(nama)
    print("   IP DI LUAR CDN (calon server asli):")
    if not terbuka:
        print("     tidak ada - semua di belakang CDN")
    for ip, namas in sorted(terbuka.items()):
        rev = dig(ip, "-x")
        print("     %-16s <- %s %s" % (ip, ", ".join(sorted(namas)[:4]), ("| ptr " + rev[0]) if rev else ""))
        for p in PORTA:
            b = porta(ip, p)
            if b:
                print("        porta %-6s BUKA | %s" % (p, b[:60]))
        for skema in ("http", "https"):
            s, t = http("%s://%s/" % (skema, ip), 15, host=d)
            print("        %s://%s -> http=%s byte=%d" % (skema, ip, s, len(t)))
    print("   KESIMPULAN:", "server asli TERBUKA" if terbuka else "tersembunyi penuh di CDN")
    print()


if __name__ == "__main__":
    for d in (sys.argv[1:] or ["wecash.ai"]):
        periksa(d)
