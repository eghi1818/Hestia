"""Baca export REA Deep Lab dari docs/intel/<host>/ lalu ringkas jadi peta target.

REA pasif (tanpa probing), Hestia aktif. Modul ini hanya membaca hasil REA
supaya Hestia tidak mengulang kerja pasif yang sudah ada.
"""
import glob
import os
import re

AKAR = "docs/intel"

POLA = {
    "stack": r"Next\.js|React|Express|WordPress|Strapi|Ghost|Directus|Vue|Angular",
    "grade": r"Header keamanan\*\* \(grade ([A-F])",
    "iframe": r"Frame embedding \| ([^|]+)\|",
    "sub": r"\b([a-z0-9][a-z0-9-]*\.[a-z0-9.-]+\.(?:ai|id|com|net))\b",
    "rute": r"\| ANY \| ([^|]+)\|",
    "api": r"Panggilan API runtime \((\d+)\)",
}


def baca_semua(host_dir):
    teks = ""
    for p in sorted(glob.glob(os.path.join(host_dir, "*"))):
        if os.path.isfile(p):
            teks += "\n" + open(p, encoding="utf-8", errors="ignore").read()
    return teks


def ringkas(teks):
    d = {}
    d["edge"] = "cloudflare" if re.search(r"server: cloudflare|Edge / CDN: Cloudflare", teks, re.I) else "-"
    st = sorted(set(re.findall(POLA["stack"], teks)))
    d["stack"] = ", ".join(st) if st else "-"
    m = re.search(POLA["grade"], teks)
    d["grade"] = m.group(1) if m else "-"
    m = re.search(POLA["iframe"], teks)
    d["iframe"] = m.group(1).strip() if m else "-"
    d["sub"] = sorted(set(re.findall(POLA["sub"], teks)))
    d["rute"] = sorted(set(x.strip() for x in re.findall(POLA["rute"], teks)))
    m = re.search(POLA["api"], teks)
    d["api_runtime"] = m.group(1) if m else "-"
    d["ada_form"] = "tidak" if re.search(r"Tidak ada form", teks) else "ya"
    return d


def kanal(d):
    out = []
    if d["edge"] == "cloudflare":
        out.append("edge_cf   : Worker suntik HTML di tepi (tanpa sentuh kode situs)")
    if re.search(r"WordPress|Strapi|Ghost|Directus", d["stack"]):
        out.append("cms_api   : REST tulis CMS")
    if d["ada_form"] == "ya":
        out.append("form_post : login + kirim form admin")
    out.append("deploy    : git push / deploy hook")
    out.append("ftp_sftp  : unggah berkas")
    return out


def main():
    if not os.path.isdir(AKAR):
        print("belum ada", AKAR)
        return
    for host in sorted(os.listdir(AKAR)):
        hd = os.path.join(AKAR, host)
        if not os.path.isdir(hd):
            continue
        d = ringkas(baca_semua(hd))
        print("== %s ==" % host)
        print("   edge      :", d["edge"])
        print("   stack     :", d["stack"])
        print("   header    :", d["grade"])
        print("   iframe    :", d["iframe"])
        print("   form      :", d["ada_form"], "| API runtime:", d["api_runtime"])
        print("   subdomain :", ", ".join(d["sub"]) or "-")
        print("   rute statis:", ", ".join(d["rute"]) or "-")
        print("   kanal tulis (urutan usul):")
        for k in kanal(d):
            print("     -", k)


if __name__ == "__main__":
    main()
