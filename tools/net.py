"""Resolusi DNS untuk Hestia.

Bawaan memakai resolver sistem. Bila HESTIA_DOH=1, resolusi dialihkan
ke Cloudflare DoH supaya kebal terhadap DNS lokal yang basi/diracuni.
"""
import json
import os
import socket
import urllib.request

DOH = os.environ.get("HESTIA_DOH") == "1"
DOH_URL = "https://cloudflare-dns.com/dns-query"

_asli = socket.getaddrinfo
_sedang = False
_peta = {}


def _ip(host):
    b = host.split(".")
    return len(b) == 4 and all(x.isdigit() for x in b)


def _tanya(nama):
    req = urllib.request.Request(
        DOH_URL + "?name=" + nama + "&type=A",
        headers={"accept": "application/dns-json"},
    )
    with urllib.request.urlopen(req, timeout=6) as r:
        data = json.loads(r.read().decode("utf-8", "ignore"))
    return [a.get("data") for a in data.get("Answer", []) if a.get("type") == 1 and a.get("data")]


def _getaddrinfo(host, port, family=0, tipe=0, proto=0, flags=0):
    global _sedang
    if host and not _ip(host) and not _sedang:
        if host not in _peta:
            _sedang = True
            try:
                _peta[host] = _tanya(host)
            except Exception:
                _peta[host] = []
            finally:
                _sedang = False
        if _peta[host]:
            p = port if port else 0
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, p)) for ip in _peta[host]]
    return _asli(host, port, family, tipe, proto, flags)


def pasang():
    if DOH:
        socket.getaddrinfo = _getaddrinfo
    return DOH


def info():
    return "DoH=%s url=%s cache=%d" % ("1" if DOH else "0", DOH_URL, len(_peta))
