"""Jejak kebocoran server asli: riwayat DNS + favicon-hash.

Melengkapi tools/asal.py dengan dua sumber lain: riwayat DNS dan
pencarian favicon-hash (teknik HackTricks 'Uncovering CloudFlare').
"""
import base64
import json
import re
import sys
import urllib.request

HDR = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}


def http(url, t=25, biner=False):
    try:
        r = urllib.request.Request(url, headers=HDR)
        with urllib.request.urlopen(r, timeout=t) as x:
            d = x.read()
        return d if biner else d.decode("utf-8", "ignore")
    except Exception:
        return b"" if biner else ""


def mmh3(data, seed=0):
    c1, c2 = 0xCC9E2D51, 0x1B873593
    n = len(data)
    h1 = seed
    bulat = n & 0xFFFFFFFC
    for i in range(0, bulat, 4):
        k1 = (data[i] & 0xFF) | ((data[i + 1] & 0xFF) << 8) | ((data[i + 2] & 0xFF) << 16) | (data[i + 3] << 24)
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF
        h1 ^= k1
        h1 = ((h1 << 13) | (h1 >> 19)) & 0xFFFFFFFF
        h1 = (h1 * 5 + 0xE6546B64) & 0xFFFFFFFF
    k1 = 0
    sisa = n & 3
    if sisa == 3:
        k1 = (data[bulat + 2] & 0xFF) << 16
    if sisa in (2, 3):
        k1 |= (data[bulat + 1] & 0xFF) << 8
    if sisa in (1, 2, 3):
        k1 |= data[bulat] & 0xFF
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF
        h1 ^= k1
    h1 ^= n
    h1 ^= h1 >> 16
    h1 = (h1 * 0x85EBCA6B) & 0xFFFFFFFF
    h1 ^= h1 >> 13
    h1 = (h1 * 0xC2B2AE35) & 0xFFFFFFFF
    h1 ^= h1 >> 16
    return h1 - 0x100000000 if h1 > 0x7FFFFFFF else h1


def riwayat(d):
    keluar = set()
    t = http("https://dns.bufferover.run/dns?q=." + d)
    if t:
        try:
            j = json.loads(t)
            for kunci in ("FDNS_A", "RDNS"):
                for baris in (j.get(kunci) or []):
                    b = baris.split(",")
                    if len(b) == 2 and d in b[1]:
                        keluar.add((b[1], b[0]))
        except Exception:
            pass
    t = http("https://jldc.me/anubis/subdomains/" + d)
    if t:
        try:
            for n in json.loads(t):
                keluar.add((n, "?"))
        except Exception:
            pass
    return keluar


def favicon(d):
    ico = http("https://" + d + "/favicon.ico", 20, biner=True)
    if not ico:
        return None, 0
    return mmh3(base64.encodebytes(ico)), len(ico)


def main(d):
    print("== jejak %s ==" % d)
    r = riwayat(d)
    print("   riwayat DNS: %d nama" % len(r))
    for n, ip in sorted(r)[:20]:
        print("     %-42s %s" % (n, ip))
    h, uk = favicon(d)
    if h is None:
        print("   favicon: tidak ada")
        return
    print("   favicon: %d byte | hash mmh3 %d" % (uk, h))
    t = http("https://www.shodan.io/search?query=http.favicon.hash%%3A%d" % h, 30)
    ips = sorted(set(re.findall(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b", t)))
    ips = [i for i in ips if not i.startswith(("0.", "127.", "255."))][:20]
    print("   shodan (favicon sama): %d IP" % len(ips))
    for i in ips:
        print("     %s" % i)
    print()


if __name__ == "__main__":
    for d in (sys.argv[1:] or ["wecash.ai"]):
        main(d)
