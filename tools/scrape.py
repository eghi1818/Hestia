#!/usr/bin/env python3
# Hestia - modul pemetaan domain (discovery + verifikasi)
#
#   discover  kumpulkan kandidat dari sumber
#   verify    periksa DNS + HTTP (403 = hidup tapi dijaga)
#   map       ringkasan per akhiran
#   export    tulis CSV
#
# contoh:
#   python3 tools/scrape.py discover --suffix ac.id --source crt --limit 40
#   python3 tools/scrape.py verify --limit 5 --sleep 1
#   python3 tools/scrape.py map
import argparse, csv, json, os, re, socket, sqlite3, sys, time
import urllib.error, urllib.request
from datetime import datetime, timezone

INFRA = {"mail", "cpanel", "webmail", "autoconfig", "autodiscover", "smtp",
         "pop", "imap", "ftp", "ns", "ns1", "ns2", "ns3", "dns", "dns1", "dns2",
         "cp", "cp1", "cp2", "cp01", "cp02", "cdn", "api", "mx", "mx1", "mx2"}
SUFFIX = ["go.id", "desa.id", "mil.id", "ac.id", "sch.id"]
BOBOT = {"go.id": 30, "desa.id": 15, "mil.id": 25, "ac.id": 20, "sch.id": 20}
SKOR_STATUS = {"hidup": 50, "alih": 35, "dijaga": 40}
WAF_MARK = ["cloudflare", "akamai", "imperva", "incapsula", "radware",
            "sucuri", "big-ip", "barracuda", "cloudfront", "fastly"]
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
HDR = {"User-Agent": UA,
       "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
       "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
       "Upgrade-Insecure-Requests": "1", "Connection": "close"}
SEEDS = ["komdigi.go.id", "bps.go.id", "kemdikbud.go.id", "jogjaprov.go.id",
         "baliprov.go.id", "surabaya.go.id", "bandung.go.id", "medan.go.id",
         "semarangkota.go.id", "tangselkota.go.id"]
DOM_RE = re.compile(r"\b((?:[a-z0-9][a-z0-9-]*\.)+(?:go|desa|mil|ac|sch)\.id)\b", re.I)


def suffix_of(d):
    for s in SUFFIX:
        if d.endswith("." + s):
            return s
    return None


def infra_of(d):
    return 1 if d.split(".")[0].lower() in INFRA else 0


def jenis_of(d, suf):
    return "akar" if d.count(".") == suf.count(".") + 1 else "sub"


def db_path():
    p = os.environ.get("HESTIA_DB")
    if p:
        return p
    try:
        sys.path.insert(0, ".")
        from app import db as adb
        for a in ("DB_PATH", "PATH", "DB", "DBFILE"):
            v = getattr(adb, a, None)
            if isinstance(v, str) and v:
                return v
    except Exception:
        pass
    for c in ("data/hestia.db", "app/hestia.db", "hestia.db"):
        if os.path.exists(c):
            return c
    return "data/hestia.db"


def conn():
    path = db_path()
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS kandidat(
        domain TEXT PRIMARY KEY, suffix TEXT, sumber TEXT,
        status TEXT DEFAULT 'baru', http_status INTEGER, server TEXT,
        waf TEXT, skor INTEGER DEFAULT 0, catatan TEXT, diperiksa_at TEXT,
        jenis TEXT, infra INTEGER DEFAULT 0)""")
    kol = [r[1] for r in c.execute("PRAGMA table_info(kandidat)")]
    if "jenis" not in kol:
        c.execute("ALTER TABLE kandidat ADD COLUMN jenis TEXT")
    if "infra" not in kol:
        c.execute("ALTER TABLE kandidat ADD COLUMN infra INTEGER DEFAULT 0")
    if "dicrawl" not in kol:
        c.execute("ALTER TABLE kandidat ADD COLUMN dicrawl INTEGER DEFAULT 0")
    if "ukuran" not in kol:
        c.execute("ALTER TABLE kandidat ADD COLUMN ukuran INTEGER DEFAULT 0")
    if "hollow" not in kol:
        c.execute("ALTER TABLE kandidat ADD COLUMN hollow INTEGER DEFAULT 0")
    if "petunjuk" not in kol:
        c.execute("ALTER TABLE kandidat ADD COLUMN petunjuk TEXT")
    if "latensi_ms" not in kol:
        c.execute("ALTER TABLE kandidat ADD COLUMN latensi_ms INTEGER DEFAULT 0")
    c.commit()
    return c


def simpan(c, domains, sumber):
    n = 0
    for d in sorted(set(domains)):
        d = d.lower().strip().rstrip(".")
        if d.startswith("*."):
            d = d[2:]
        s = suffix_of(d)
        if not s:
            continue
        cur = c.execute("INSERT OR IGNORE INTO kandidat(domain,suffix,sumber,jenis,infra) VALUES(?,?,?,?,?)",
                        (d, s, sumber, jenis_of(d, s), infra_of(d)))
        if cur.rowcount:
            n += 1
    c.commit()
    return n


def discover_crt(suf, limit, timeout=60):
    bentuk = ["https://crt.sh/?q=%25.{s}&output=json",
              "https://crt.sh/?q=%25.{s}&output=json&exclude=expired",
              "https://crt.sh/?q=.{s}&output=json"]
    sebab = "-"
    for b in bentuk:
        for coba in range(2):
            url = b.format(s=suf)
            try:
                req = urllib.request.Request(url, headers=HDR)
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    data = json.load(r)
                out = set()
                for row in data:
                    for name in str(row.get("name_value", "")).split("\n"):
                        name = name.strip().lower()
                        if name.endswith("." + suf) and "*" not in name:
                            out.add(name)
                    if limit and len(out) >= limit:
                        break
                if out:
                    return out
                sebab = "respons kosong"
            except urllib.error.HTTPError as e:
                sebab = "http %s" % e.code
            except Exception as e:
                sebab = type(e).__name__
            time.sleep(2 + coba * 3)
        print("    bentuk gagal: %s -> %s" % (b, sebab))
    raise RuntimeError("crt.sh gagal (%s)" % sebab)

def _web_rapiddns(suf, limit=0, max_hal=5):
    out = set()
    for hal in range(1, max_hal + 1):
        try:
            url = "https://rapiddns.io/subdomain/%s?full=1&page=%d" % (suf, hal)
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=45) as r:
                html = r.read(1500000).decode("utf-8", "ignore")
        except Exception as e:
            print("    rapiddns hal %d gagal: %s" % (hal, e))
            break
        dapat = set(m.lower() for m in DOM_RE.findall(html) if m.lower().endswith("." + suf))
        tambah = len(dapat - out)
        out |= dapat
        print("    rapiddns hal %d: +%d (total %d)" % (hal, tambah, len(out)))
        if not tambah or (limit and len(out) >= limit):
            break
        time.sleep(1)
    return out


def _web_sdcenter(suf):
    out = set()
    try:
        url = "https://api.subdomain.center/?domain=" + suf
        with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=45) as r:
            data = json.load(r)
        for n in data:
            n = str(n).strip().lower().rstrip(".")
            if n.endswith("." + suf) and "*" not in n:
                out.add(n)
    except Exception as e:
        print("    sdcenter gagal: %s" % e)
    print("    sdcenter: %d" % len(out))
    return out


def _web_hackertarget(suf):
    out = set()
    try:
        url = "https://api.hackertarget.com/hostsearch/?q=" + suf
        with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=30) as r:
            txt = r.read(500000).decode("utf-8", "ignore")
        if "API count exceeded" not in txt:
            for baris in txt.splitlines():
                h = baris.split(",")[0].strip().lower()
                if h.endswith("." + suf):
                    out.add(h)
    except Exception as e:
        print("    hackertarget gagal: %s" % e)
    print("    hackertarget: %d" % len(out))
    return out


def discover_web(suf, limit=0):
    hasil = _web_rapiddns(suf, limit)
    hasil |= _web_sdcenter(suf)
    if not (limit and len(hasil) >= limit):
        hasil |= _web_hackertarget(suf)
    print("    gabungan web: %d" % len(hasil))
    return hasil


PANEL = {"cpanel", "webmail", "cpcalendars", "cpcontacts", "webdisk", "plesk",
         "roundcube", "squirrelmail", "directadmin", "whm", "panel"}
PETUNJUK = [
    ("404 - page not found", "halaman 404"),
    ("page not found", "halaman 404"),
    ("expired domain", "domain kedaluwarsa"),
    ("index of /", "daftar berkas"),
    ("welcome to nginx", "nginx bawaan"),
    ("apache2 ubuntu default page", "apache bawaan"),
    ("apache2 default page", "apache bawaan"),
    ("under construction", "dalam pengerjaan"),
    ("coming soon", "segera hadir"),
    ("default web page", "halaman bawaan"),
    ("idcloudhost", "halaman parkir"),
    ("parked", "halaman parkir"),
    ("this domain", "halaman parkir"),
    ("roundcube", "halaman panel"),
    ("directadmin", "halaman panel"),
    ("plesk", "halaman panel"),
    ("webmail", "halaman panel"),
    ("cpanel", "halaman panel"),
]


def teks_terlihat(html):
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\\1>", " ", html)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\\s+", " ", t).strip().lower()


def hollow_of(html):
    t = teks_terlihat(html)
    for pola, nama in PETUNJUK:
        if pola in t:
            return nama
    return "halaman sangat tipis" if len(t) < 300 else ""


def ambil_html(domain, timeout=12):
    """Ambil HTML dengan fallback http, sama seperti verify_one."""
    for skema in ("https", "http"):
        _t0 = time.time()
        try:
            req = urllib.request.Request(skema + "://" + domain, headers=HDR)
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return r.read(400000).decode("utf-8", "ignore")
            except urllib.error.HTTPError as e:
                return e.read(400000).decode("utf-8", "ignore")
        except Exception:
            continue
    return None


def discover_seed(suf, timeout=12):
    daftar = [s for s in SEEDS if s.endswith("." + suf)] or SEEDS
    out = set(daftar)
    for host in daftar:
        try:
            req = urllib.request.Request("https://" + host, headers=HDR)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                html = r.read(300000).decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            html = e.read(300000).decode("utf-8", "ignore")
        except Exception:
            continue
        for m in DOM_RE.findall(html):
            if m.lower().endswith("." + suf):
                out.add(m.lower())
    return out


def verify_one(domain, timeout=10):
    h = {"status": "mati", "http_status": None, "server": None, "waf": None,
         "latensi_ms": 0}
    try:
        socket.getaddrinfo(domain, 443, proto=socket.IPPROTO_TCP)
    except Exception as e:
        h["catatan"] = "dns:" + type(e).__name__
        return h
    for skema in ("https", "http"):
        _t0 = time.time()
        try:
            req = urllib.request.Request(skema + "://" + domain, headers=HDR, method="GET")
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    kode, hdr = r.status, dict(r.headers)
            except urllib.error.HTTPError as e:
                kode, hdr = e.code, dict(e.headers)
        except Exception as e:
            h["catatan"] = skema + ":" + type(e).__name__
            continue
        gab = " ".join("%s:%s" % (k, v) for k, v in hdr.items()).lower()
        h["latensi_ms"] = int((time.time() - _t0) * 1000)
        h["http_status"] = kode
        h["server"] = hdr.get("Server")
        h["waf"] = next((w for w in WAF_MARK if w in gab), None)
        h["status"] = ("hidup" if kode < 300 else "alih" if kode < 400
                       else "dijaga" if kode in (401, 403, 406, 418, 429, 503) else "galat")
        return h
    return h


def skor(h):
    s = BOBOT.get(h.get("suffix"), 10) + SKOR_STATUS.get(h["status"], 0)
    return min(s + (5 if h.get("waf") else 0), 100)


def cmd_discover(a):
    c = conn()
    kumpul = set()
    for suf in ([a.suffix] if a.suffix else SUFFIX):
        d = set()
        if a.source in ("crt", "auto"):
            try:
                d = discover_crt(suf, a.limit)
                print("  crt  %-9s %5d" % (suf, len(d)))
            except Exception as e:
                print("  crt  %-9s GAGAL %s" % (suf, e))
        if not d and a.source in ("web", "auto"):
            d = discover_web(suf, a.limit)
        if not d and a.source in ("seed", "auto"):
            d = discover_seed(suf)
            print("  seed %-9s %5d" % (suf, len(d)))
        kumpul |= d
    n = simpan(c, kumpul, a.source)
    tot = c.execute("SELECT count(*) FROM kandidat").fetchone()[0]
    print("kandidat baru: %d  (total di basis: %d)" % (n, tot))


def cmd_verify(a):
    c = conn()
    q, args = "SELECT domain,suffix FROM kandidat WHERE status='baru'", []
    if a.suffix:
        q += " AND suffix=?"
        args.append(a.suffix)
    q += " ORDER BY domain LIMIT ?"
    args.append(a.limit)
    baris = c.execute(q, args).fetchall()
    print("memeriksa %d domain (jeda %ss)" % (len(baris), a.sleep))
    ringkas = {}
    for r in baris:
        h = verify_one(r["domain"])
        h["suffix"] = r["suffix"]
        c.execute("""UPDATE kandidat SET status=?,http_status=?,server=?,waf=?,skor=?,
                     catatan=?,diperiksa_at=?,latensi_ms=? WHERE domain=?""",
                  (h["status"], h["http_status"], h["server"], h["waf"], skor(h),
                   h.get("catatan"), datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   h.get("latensi_ms", 0), r["domain"]))
        c.commit()
        ringkas[h["status"]] = ringkas.get(h["status"], 0) + 1
        print("  %-42s %-8s %s" % (r["domain"], h["status"], h["http_status"] or "-"))
        time.sleep(a.sleep)
    print("ringkas:", ringkas)


def cmd_map(a):
    c = conn()
    total = c.execute("SELECT count(*) FROM kandidat").fetchone()[0]
    per = {}
    for r in c.execute("SELECT suffix,status,count(*) n FROM kandidat GROUP BY suffix,status"):
        per.setdefault(r["suffix"], {})[r["status"]] = r["n"]
    print("PETA KANDIDAT  (total %d)" % total)
    print("-" * 54)
    print("%-10s%7s%8s%8s%7s%7s" % ("akhiran", "total", "hidup", "dijaga", "alih", "mati"))
    for s in SUFFIX:
        d = per.get(s, {})
        t = sum(d.values())
        print("%-10s%7d%8d%8d%7d%7d" % (s, t, d.get("hidup", 0), d.get("dijaga", 0),
                                        d.get("alih", 0), d.get("mati", 0)))
    print("-" * 54)
    ak = c.execute("SELECT suffix, jenis, count(*) n FROM kandidat GROUP BY suffix, jenis").fetchall()
    if ak:
        print("sebaran jenis:")
        for r in ak:
            print("   %-9s %-5s %d" % (r["suffix"], r["jenis"] or "?", r["n"]))
    try:
        pin = c.execute("SELECT dari, count(*) n FROM tautan GROUP BY dari ORDER BY n DESC LIMIT 8").fetchall()
        if pin:
            print("pintu masuk teratas (paling banyak membuka domain lain):")
            for r in pin:
                print("   %3d  %s" % (r["n"], r["dari"]))
    except Exception:
        pass
    kosong = c.execute("SELECT count(*) FROM kandidat WHERE ukuran>0 AND ukuran<3000").fetchone()[0]
    print("halaman tipis (<3KB): %d" % kosong)
    top = c.execute("""SELECT domain,status,skor,waf FROM kandidat
                       WHERE status IN ('hidup','dijaga','alih') AND infra=0 AND hollow=0
                       ORDER BY skor DESC LIMIT 15""").fetchall()
    if top:
        print("PRIORITAS:")
        for r in top:
            print("  %3d  %-42s%-8s%s" % (r["skor"], r["domain"], r["status"], r["waf"] or ""))


def cmd_crawl(a):
    c = conn()
    c.execute("""CREATE TABLE IF NOT EXISTS tautan(
        dari TEXT, ke TEXT, dibuat TEXT, PRIMARY KEY(dari,ke))""")
    q = ("SELECT domain FROM kandidat WHERE status IN ('hidup','alih','dijaga')"
         " AND (dicrawl IS NULL OR dicrawl=0")
    if a.ulang:
        q += " OR dicrawl=2"
    q += ")"
    arg = []
    if a.suffix:
        q += " AND suffix=?"; arg.append(a.suffix)
    q += " ORDER BY skor DESC LIMIT ?"; arg.append(a.batas)
    sumber = [r["domain"] for r in c.execute(q, arg)]
    print("crawl: %d domain (jeda %ss)" % (len(sumber), a.jeda))
    ketemu = set()
    gagal = 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for d in sumber:
        html = ambil_html(d)
        if html is None:
            gagal += 1
            c.execute("UPDATE kandidat SET dicrawl=2 WHERE domain=?", (d,)); c.commit()
            print("  %-42s gagal (dicoba lagi nanti)" % d)
            time.sleep(a.jeda); continue
        dapat = set(m.lower() for m in DOM_RE.findall(html))
        for t in dapat:
            if t != d:
                c.execute("INSERT OR IGNORE INTO tautan(dari,ke,dibuat) VALUES(?,?,?)", (d, t, now))
        baru = dapat - ketemu
        ketemu |= dapat
        pet = hollow_of(html)
        if not pet and d.split(".")[0].lower() in PANEL:
            pet = "halaman panel"
        c.execute("UPDATE kandidat SET dicrawl=1, ukuran=?, hollow=?, petunjuk=? WHERE domain=?",
                  (len(html), 1 if pet else 0, pet, d)); c.commit()
        print("  %-42s +%d (total %d) ukuran=%d%s" % (d, len(baru), len(ketemu), len(html),
                                                 (" KOSONG:" + pet) if pet else ""))
        time.sleep(a.jeda)
    n = simpan(c, ketemu, "crawl")
    print("kandidat baru: %d  total: %d  tautan: %d  gagal: %d" % (
        n, c.execute("SELECT count(*) FROM kandidat").fetchone()[0],
        c.execute("SELECT count(*) FROM tautan").fetchone()[0], gagal))


def cmd_export(a):
    c = conn()
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["domain", "suffix", "sumber", "status", "http_status", "server", "waf", "skor"])
        for r in c.execute("SELECT * FROM kandidat ORDER BY skor DESC, domain"):
            w.writerow([r["domain"], r["suffix"], r["sumber"], r["status"],
                        r["http_status"], r["server"], r["waf"], r["skor"]])
    print("ditulis:", a.out)


def main():
    p = argparse.ArgumentParser(description="Hestia - pemetaan domain")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("discover"); d.add_argument("--suffix"); d.add_argument("--source", default="auto", choices=["auto", "crt", "web", "seed"]); d.add_argument("--limit", type=int, default=0); d.set_defaults(f=cmd_discover)
    v = sub.add_parser("verify"); v.add_argument("--suffix"); v.add_argument("--limit", type=int, default=20); v.add_argument("--sleep", type=float, default=1.0); v.set_defaults(f=cmd_verify)
    cr = sub.add_parser("crawl")
    cr.add_argument("--suffix")
    cr.add_argument("--batas", type=int, default=25)
    cr.add_argument("--jeda", type=float, default=1.0)
    cr.add_argument("--ulang", action="store_true", default=False)
    cr.set_defaults(f=cmd_crawl)
    m = sub.add_parser("map"); m.set_defaults(f=cmd_map)
    e = sub.add_parser("export"); e.add_argument("--out", default="kandidat.csv"); e.set_defaults(f=cmd_export)
    a = p.parse_args()
    print("basis:", db_path())
    a.f(a)


if __name__ == "__main__":
    main()
