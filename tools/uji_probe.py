#!/usr/bin/env python3
# uji_probe.py - prober sopan + pengklasifikasi respons.
# Supaya probe tidak lagi sekali-pakai: UA, jeda, probe kontrol, dan
# klasifikasi yang tidak menyamakan "tidak ada" dengan "ditantang".
import argparse, json, os, sys, time, urllib.error, urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
VERSI = "2026-10-23.1"
KUAT = ("cf-mitigated", "_cf_chl_opt", "__cf_chl_f_tk", "cf-chl-")
LEMAH = ("challenges.cloudflare.com", "turnstile", "__cf_bm")
JEDA = 8.0

def ambil(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as x:
            return x.status, dict(x.headers), x.read(400000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), (e.read(400000) or b"").decode("utf-8", "ignore")
    except Exception as e:
        return None, {}, str(e)

def kelas(kode, kepala, badan):
    kk = " ".join("%s: %s" % (a, b) for a, b in kepala.items()).lower()
    gab = kk + " " + badan.lower()
    if any(p in gab for p in KUAT):
        return "tantangan"
    if kode is None:
        return "tidak_dapat_disimpulkan"
    if kode in (404, 410):
        return "tidak_ada"
    if kode in (401, 403) and any(p in gab for p in LEMAH):
        return "tantangan"
    if kode in (401, 403):
        return "blokir"
    if 200 <= kode < 300:
        return "nyata"
    return "tidak_dapat_disimpulkan"

def uji(url, kontrol=None, jeda=JEDA):
    time.sleep(jeda)
    kode, kepala, badan = ambil(url)
    h = {"url": url, "kode": kode, "kelas": kelas(kode, kepala, badan),
         "byte": len(badan), "versi": VERSI}
    if kontrol and kontrol != url:
        time.sleep(jeda)
        kk, kp, kb = ambil(kontrol)
        h["kontrol"] = {"url": kontrol, "kode": kk, "kelas": kelas(kk, kp, kb)}
        if h["kelas"] == "tidak_ada" and h["kontrol"]["kelas"] == "tantangan":
            h["kelas"] = "tidak_dapat_disimpulkan"
    return h

def uji_diri():
    kasus = [("positif", "https://www.portalyogya.com/", "nyata"),
             ("negatif", "https://www.portalyogya.com/tidak-ada-xyz-999999", "tidak_ada"),
             ("tantangan", "https://www.ayobandung.com/", "tantangan")]
    lulus = 0
    for nama, url, harap in kasus:
        h = uji(url)
        ok = h["kelas"] == harap
        lulus += 1 if ok else 0
        print("%-9s %-5s harap=%-14s dapat=%-14s %s" % (nama, h["kode"], harap, h["kelas"], "OK" if ok else "BEDA"))
    print("lulus %d/%d" % (lulus, len(kasus)))
    return 0 if lulus == len(kasus) else 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?")
    ap.add_argument("--kontrol")
    ap.add_argument("--jeda", type=float, default=JEDA)
    ap.add_argument("--simpan")
    ap.add_argument("--uji-diri", action="store_true")
    a = ap.parse_args()
    if a.uji_diri or not a.url:
        return uji_diri()
    h = uji(a.url, a.kontrol, a.jeda)
    print(json.dumps(h, indent=2, ensure_ascii=False))
    if a.simpan:
        with open(a.simpan, "a") as f:
            f.write(json.dumps(h, ensure_ascii=False) + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
