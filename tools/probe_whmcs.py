#!/usr/bin/env python3
"""Coba login WHMCS member.mcs.co.id dengan sandi dari docs/kredensial.md."""
import re, sys, urllib.parse, urllib.request, http.cookiejar

BASE = "https://member.mcs.co.id"
teks = open("docs/kredensial.md").read()
emails = sorted(set(re.findall(r'[\w.+-]+@[\w.-]+\.\w+', teks)))
pws = sorted(set(re.findall(r'`([^`]+)`', teks)))
if len(sys.argv) > 1:
    emails = [e for e in emails if any(a.lower() in e.lower() for a in sys.argv[1:])] or emails
print("email:", emails)
print("sandi:", len(pws))

def coba(email, sandi):
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    html = op.open(BASE + "/clientarea.php", timeout=12).read().decode("utf-8", "replace")
    m = re.search(r'name="token"\s+value="([^"]+)"', html)
    data = urllib.parse.urlencode({"username": email, "password": sandi,
                                   "token": m.group(1) if m else "", "redirect": ""}).encode()
    r = op.open(BASE + "/dologin.php", data=data, timeout=12)
    body = r.read().decode("utf-8", "replace")
    if "Incorrect" in body or "clientarea.php" not in r.geturl():
        return None
    return op, body

for e in emails:
    for p in pws:
        try:
            hasil = coba(e, p)
        except Exception as ex:
            continue
        if hasil:
            op, body = hasil
            print("\n*** COCOK: %s | %s" % (e, p))
            open(".out/whmcs-masuk.html", "w", encoding="utf-8").write(body)
            ids = sorted(set(re.findall(r'productdetails&id=(\d+)', body)))
            print("layanan id:", ids[:10])
            for i in ids[:5]:
                d = op.open(BASE + "/clientarea.php?action=productdetails&id=" + i, timeout=12)
                t = d.read().decode("utf-8", "replace")
                open(".out/whmcs-produk-%s.html" % i, "w", encoding="utf-8").write(t)
                nama = re.search(r'<h1[^>]*>([^<]{3,80})</h1>', t)
                print("  produk %s: %s" % (i, nama.group(1).strip() if nama else "?"))
            sys.exit(0)
    print("gagal:", e)
print("\ntidak ada kombinasi yang cocok")
