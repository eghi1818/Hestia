#!/usr/bin/env python3
# tala_siapkan.py - siapkan baris label kosong dari daftar URL mati.
# Kandidat diambil dari indeks seksi situs, BUKAN dari penskor kita,
# supaya penskor tidak pernah menguji dirinya sendiri.
import csv, os, random, re, sys, urllib.request

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(AKAR, "data", "tala")
UA = "HestiaTala/0.1"

def ambil(url, timeout=20):
    try:
        r = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(r, timeout=timeout) as h:
            return h.read().decode("utf-8", "replace")
    except Exception as e:
        print("  gagal ambil %s: %s" % (url, e))
        return ""

def host_dari(url):
    m = re.match(r"https?://([^/]+)", url)
    return m.group(1) if m else ""

def sama_host(a, b):
    return host_dari(a).replace("www.", "") == host_dari(b).replace("www.", "")

def tautan(html, contoh):
    out = []
    for m in re.finditer(r"""href=['"]([^'"#]+)['"]""", html):
        u = m.group(1)
        if u.startswith("//"):
            u = "https:" + u
        elif u.startswith("/"):
            u = "https://" + host_dari(contoh) + u
        if not u.startswith("http") or not sama_host(u, contoh):
            continue
        if re.search(r"\.(jpg|jpeg|png|gif|css|js|webp|svg|ico)$", u, re.I):
            continue
        u = u.split("#")[0]
        if u not in out:
            out.append(u)
    return out

def main():
    fm = os.path.join(DIR, "url_mati.txt")
    if not os.path.exists(fm):
        print("tidak ada %s" % fm); return 1
    mati = [x.strip() for x in open(fm) if x.strip() and not x.startswith("#")]
    print("url mati: %d" % len(mati))
    os.makedirs(DIR, exist_ok=True)
    fp = os.path.join(DIR, "pasangan.csv")
    fh = os.path.join(DIR, "halaman.csv")
    if os.path.exists(fp):
        print("!! %s sudah ada - hapus dulu kalau mau dibangun ulang" % fp); return 0
    nhal = 0; npas = 0; kosong = 0
    with open(fp, "w", newline="") as g, open(fh, "w", newline="") as h:
        wp = csv.writer(g); wh = csv.writer(h)
        wp.writerow(["id","id_halaman","url_mati","url_kandidat","asal_kandidat","label_pasangan","catatan","dilabeli_pada"])
        wh.writerow(["id","url_mati","backlink","label_halaman","rujukan_pasangan","status_saat_label","catatan"])
        for i, u in enumerate(mati, 1):
            m = re.match(r"(https?://[^/]+)(/.*)?$", u)
            if not m:
                print("  lewat (bukan URL): %s" % u); continue
            basis = m.group(1)
            bagian = (m.group(2) or "/").strip("/").split("/")[0]
            html = ambil("%s/%s/" % (basis, bagian))
            semua = tautan(html, u) if html else []
            seksi = [x for x in semua if ("/%s/" % bagian) in x and x != u]
            lintas = [x for x in semua if ("/%s/" % bagian) not in x]
            rnd = random.Random(i)
            sa = seksi[:]; rnd.shuffle(sa)
            la = lintas[:]; rnd.shuffle(la)
            pilih = []; sudah = set()
            def tambah(x, asal):
                if x and x not in sudah and x != u:
                    sudah.add(x); pilih.append((x, asal))
            for x in sa[:3]:
                tambah(x, "seksi")
            if la: tambah(la[0], "lintas")
            if semua: tambah(rnd.choice(semua), "acak")
            if not html: catatan = "ambil gagal"
            elif not semua: catatan = "tak ada tautan di indeks seksi"
            elif not pilih: catatan = "kandidat kosong"
            else: catatan = ""
            if not pilih: kosong += 1
            awal = npas + 1
            for url, asal in pilih:
                npas += 1
                wp.writerow([npas, i, u, url, asal, "", "", ""])
            wh.writerow([i, u, "", "", (awal if pilih else ""), "", catatan])
            nhal += 1
    print("halaman=%d pasangan=%d tanpa_kandidat=%d" % (nhal, npas, kosong))
    return 0

if __name__ == "__main__":
    sys.exit(main())
