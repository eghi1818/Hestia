"""Deteksi teknologi, pintu, dan tingkat kanal tiap target, lalu simpan ke DB."""
import re
import sqlite3
import sys
import urllib.error
import urllib.request

HDR = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
}
PINTU = [("/wp-login.php", "wp"), ("/wp-json/wp/v2/types", "wp-rest"),
         ("/administrator/", "joomla"), ("/user/login", "drupal"),
         ("/login/index.php", "moodle"), ("/admin/", "admin"), ("/panel/", "panel")]
TANDA = [(r"wp-content|wp-includes", "wordpress"), (r"/media/jui|option=com_", "joomla"),
         (r"sites/default/files|Drupal\.settings", "drupal"), (r"/theme/|moodle", "moodle"),
         (r"/_next/", "next.js"), (r"/_nuxt/", "nuxt"), (r"laravel_session|XSRF-TOKEN", "laravel"),
         (r"csrfmiddlewaretoken", "django"), (r"ci_session", "codeigniter"),
         (r"bootstrap", "bootstrap"), (r"jquery", "jquery"), (r"tailwind", "tailwind")]
WAF = [("cf-ray", "cloudflare"), ("x-sucuri-id", "sucuri"), ("x-iinfo", "imperva"),
       ("x-amz-cf-id", "cloudfront"), ("x-vercel-id", "vercel")]
KOLOM = [("teknologi", "TEXT"), ("server", "TEXT"), ("waf", "TEXT"),
         ("pintu", "TEXT"), ("kanal", "TEXT"), ("dianalisa", "TEXT")]


def ambil(domain, jalur, t=10):
    try:
        r = urllib.request.Request("https://" + domain + jalur, headers=HDR)
        with urllib.request.urlopen(r, timeout=t) as x:
            return x.status, x.read(80000).decode("utf-8", "ignore"), {k.lower(): v for k, v in x.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, "", {k.lower(): v for k, v in e.headers.items()}
    except Exception:
        return 0, "", {}


def periksa(domain):
    st, isi, hd = ambil(domain, "/")
    hdr = " ".join("%s=%s" % (k, v) for k, v in hd.items()).lower()
    tek = sorted(set(nama for pola, nama in TANDA if re.search(pola, isi + " " + hdr, re.I)))
    versi = ""
    m = re.search(r"<meta[^>]+generator[^>]+content=[\"']([^\"']+)", isi, re.I)
    if m:
        versi = m.group(1)[:40]
    waf = ", ".join(sorted(set(nama for k, nama in WAF if k in hd)))
    server = hd.get("server", "")[:40]
    if "php" in hd.get("x-powered-by", "").lower():
        server = (server + " | " + hd["x-powered-by"][:24]).strip(" |")
    pintu = []
    for jalur, nama in PINTU:
        k, _, _ = ambil(domain, jalur)
        if k in (200, 401, 403):
            pintu.append("%s(%s)" % (nama, k))
    kanal = []
    if re.search(r"comment-form|commentform", isi, re.I):
        kanal.append("t0 komentar")
    if "wp" in " ".join(pintu) or "wordpress" in tek:
        kanal.append("t1 wp (user+pass)")
    if "joomla" in " ".join(pintu):
        kanal.append("t1 joomla")
    if "moodle" in " ".join(pintu):
        kanal.append("t1 moodle")
    if "cloudflare" in waf:
        kanal.append("t4 worker (akun CDN)")
    return {"teknologi": (", ".join(tek) + (" [" + versi + "]" if versi else ""))[:120],
            "server": server, "waf": waf or "-", "pintu": ", ".join(pintu) or "-",
            "kanal": " | ".join(kanal) or "-", "dianalisa": "2026-10-22"}


def main():
    c = sqlite3.connect("data/hestia.db")
    ada = [r[1] for r in c.execute("PRAGMA table_info(targets)")]
    for n, j in KOLOM:
        if n not in ada:
            c.execute("ALTER TABLE targets ADD COLUMN %s %s" % (n, j))
    c.commit()
    batas = int(sys.argv[1]) if len(sys.argv) > 1 else 999
    rows = list(c.execute("select id, domain from targets order by id limit ?", (batas,)))
    print("memeriksa %d target" % len(rows))
    for i, (tid, dom) in enumerate(rows, 1):
        d = periksa(dom)
        c.execute("update targets set teknologi=?, server=?, waf=?, pintu=?, kanal=?, dianalisa=? where id=?",
                  (d["teknologi"], d["server"], d["waf"], d["pintu"], d["kanal"], d["dianalisa"], tid))
        c.commit()
        print("%3d. %-32s %-26s %-12s %s" % (i, dom, (d["teknologi"] or "-")[:26], (d["waf"] or "-")[:12], (d["pintu"] or "-")[:40]))
    print()
    print("--- rekap ---")
    for w, n in c.execute("select waf, count(*) from targets group by waf order by 2 desc"):
        print("   waf %-14s : %d" % (w, n))
    for k, n in c.execute("select kanal, count(*) from targets group by kanal order by 2 desc limit 10"):
        print("   kanal %-28s : %d" % (k[:28], n))


if __name__ == "__main__":
    main()
