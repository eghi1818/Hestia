#!/usr/bin/env python3
"""Bukti A->B: ambil konten situs A, tulis ke berkas situs B lewat jalur J5.
Base href membuat semua URL relatif menunjuk ke situs A, jadi aset ikut tampil.
Jalankan di VPS dengan HESTIA_LOKAL=1."""
import argparse, datetime, hashlib, os, re, sqlite3, subprocess, urllib.request

DB = "data/hestia.db"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124 Safari/537.36 Hestia/1.0")
SSH = ["ssh", "-p", "10053", "-i", os.path.expanduser("~/.ssh/wesearch_vps_key"),
       "-o", "StrictHostKeyChecking=no", "administrator@93.127.133.160"]
LOKAL = os.environ.get("HESTIA_LOKAL") == "1"
SNAP = "data/snapshot"


def sh(p, masuk=None):
    argv = ["bash", "-lc", p] if LOKAL else SSH + [p]
    r = subprocess.run(argv, input=masuk, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def ambil(url, t=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "id,en"})
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.status, dict(r.headers), r.read().decode("utf-8", "replace")


def teks_terlihat(html):
    b = re.search(r"(?is)<body.*?>(.*)</body>", html)
    isi = b.group(1) if b else html
    isi = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", isi)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", isi)).strip()


def boleh_bingkai(hdr):
    xfo = str(hdr.get("X-Frame-Options", "")).lower()
    csp = str(hdr.get("Content-Security-Policy", "")).lower()
    if "deny" in xfo or "sameorigin" in xfo:
        return False
    if "frame-ancestors" in csp and "*" not in csp:
        return False
    return True


def rapikan(html, dasar):
    d = dasar.rstrip("/")
    sisip = ""
    if "<base" not in html.lower():
        sisip += '<base href="%s/">' % d
    if re.search(r"(?is)<head[^>]*>", html):
        html = re.sub(r"(?is)(<head[^>]*>)", r"\1" + sisip, html, count=1)
    else:
        html = sisip + html
    html = re.sub(r'((?:href|src|srcset|action)=")(?!https?:|//|/|#|data:|mailto:|javascript:)([^"]+)"',
                  r"\1" + d + r'/\2"', html)
    html = re.sub(r'((?:href|src|srcset|action)=")/', r"\1" + d + "/", html)
    html = re.sub(r"url\((/[^)]*)\)", r"url(" + d + r"\1)", html)
    html = html.replace('"/_next', '"' + d + '/_next').replace("'/_next", "'" + d + "/_next")
    return html


def halaman_bingkai(dasar, judul):
    return ('<!doctype html><html lang="id"><head><meta charset="utf-8"><title>%s</title>'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<style>html,body{margin:0;height:100%%;background:#fff}'
            'iframe{border:0;position:fixed;inset:0;width:100%%;height:100%%}</style></head>'
            '<body><iframe src="%s" referrerpolicy="no-referrer-when-downgrade"></iframe></body></html>'
            % (judul, dasar))


def halaman_teks(dasar, judul, html):
    t = teks_terlihat(html)
    par = "\n".join("<p>%s</p>" % p.strip() for p in re.split(r"(?<=[.!?])\s+", t)[:60] if p.strip())
    return ('<!doctype html><html lang="id"><head><meta charset="utf-8"><title>%s</title>'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<style>body{margin:0;font:17px/1.7 -apple-system,Segoe UI,sans-serif;color:#222}'
            'main{max-width:760px;margin:0 auto;padding:32px 20px}h1{font-size:26px}a{color:#0a6}'
            '</style></head><body><main><h1>%s</h1><p><a href="%s">%s</a></p>%s</main></body></html>'
            % (judul, judul, dasar, dasar, par))


def utama():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dari", required=True)
    ap.add_argument("--ke", required=True)
    ap.add_argument("--berkas", default="/var/www/waspadaweb/index.html")
    ap.add_argument("--penanda", default="HESTIA-INJECT")
    ap.add_argument("--mode", default="auto", choices=["auto", "salin", "bingkai", "teks"])
    ap.add_argument("--banner", default="off", choices=["on", "off"])
    ap.add_argument("--db", default=DB)
    ap.add_argument("--terapkan", action="store_true")
    ap.add_argument("--pulih", action="store_true")
    a = ap.parse_args()

    os.makedirs(SNAP, exist_ok=True)
    fsnap = os.path.join(SNAP, re.sub(r"[^a-z0-9]+", "-", a.ke.lower()).strip("-") + ".html")

    if a.pulih:
        if not os.path.exists(fsnap):
            raise SystemExit("snapshot tidak ada: " + fsnap)
        rc, _, err = sh("sudo tee %s >/dev/null" % a.berkas, open(fsnap).read())
        print("  pulih rc=%s %s" % (rc, err.strip()[:80]))
        return

    kode, hdr, html = ambil(a.dari)
    sha = hashlib.sha256(html.encode()).hexdigest()
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    judul = (m.group(1).strip()[:80] if m else a.dari)
    teks = teks_terlihat(html)
    print("  A %s http=%s sha256=%s panjang=%d teks_terlihat=%d"
          % (a.dari, kode, sha[:16], len(html), len(teks)))

    mode = a.mode
    if mode == "auto":
        mode = "salin" if len(teks) >= 300 else ("bingkai" if boleh_bingkai(hdr) else "teks")
    print("  mode dipakai: %s" % mode)

    if mode == "salin":
        isi = rapikan(html, a.dari)
    elif mode == "bingkai":
        isi = halaman_bingkai(a.dari, judul)
    else:
        isi = halaman_teks(a.dari, judul, html)

    if a.banner == "on":
        bar = ('<div id="hestia-penanda" style="font:14px/1.5 -apple-system,sans-serif;'
               'background:#111;color:#eee;padding:10px 14px"><b>%s</b> &middot; %s &middot; sha256 %s</div>'
               % (a.penanda, a.dari, sha[:16]))
        isi = isi.replace("</body>", bar + "</body>")

    cap = "<!-- %s sumber=%s sha256=%s mode=%s waktu=%s -->" % (
        a.penanda, a.dari, sha, mode, datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
    if re.search(r"(?is)<head[^>]*>", isi):
        isi = re.sub(r"(?is)(<head[^>]*>)", r"\1" + cap, isi, count=1)
    else:
        isi = cap + isi

    rc, asli, _ = sh("sudo cat %s" % a.berkas)
    ada = asli.strip() != "" and "No such file" not in asli

    if a.terapkan and a.penanda in asli and sha in asli:
        print("  sudah terpasang (idempoten) - dilewati")
        return
    if not a.terapkan:
        print("  cuplikan:", isi[:160].replace("\n", " "))
        return

    if ada and a.penanda not in asli:
        open(fsnap, "w").write(asli)
        print("  snapshot asli disimpan:", fsnap)
    rc, _, err = sh("sudo tee %s >/dev/null" % a.berkas, isi)
    print("  tulis ke B rc=%s %s" % (rc, err.strip()[:80]))

    c = sqlite3.connect(a.db)
    kols = [r[1] for r in c.execute("pragma table_info(change_event)")]
    b = {"jenis": "inject-a-b", "jalur": "J5", "nilai_lama": hashlib.sha256(asli.encode()).hexdigest()[:16],
         "nilai_baru": sha[:16], "vantage": "lokal+vps",
         "catatan": "%s -> %s (mode %s, base href)" % (a.dari, a.ke, mode),
         "waktu": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    b = {k: v for k, v in b.items() if k in kols}
    c.execute("insert into change_event (%s) values (%s)" % (", ".join(b), ", ".join("?" * len(b))), tuple(b.values()))
    c.commit()
    print("  change_event dicatat")


if __name__ == "__main__":
    utama()
