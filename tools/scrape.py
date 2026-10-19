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
        waf TEXT, skor INTEGER DEFAULT 0, catatan TEXT, diperiksa_at TEXT)""")
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
        cur = c.execute("INSERT OR IGNORE INTO kandidat(domain,suffix,sumber) VALUES(?,?,?)",
                        (d, s, sumber))
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

def discover_web(suf, limit=0):
    hasil = set()
    try:
        url = "https://api.hackertarget.com/hostsearch/?q=" + suf
        with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=30) as r:
            txt = r.read(500000).decode("utf-8", "ignore")
        if "API count exceeded" not in txt:
            for baris in txt.splitlines():
                h = baris.split(",")[0].strip().lower()
                if h.endswith("." + suf):
                    hasil.add(h)
        print("    hackertarget: %d" % len(hasil))
    except Exception as e:
        print("    hackertarget gagal: %s" % e)
    if not hasil:
        try:
            url = ("https://api.certspotter.com/v1/issuances?domain=%s"
                   "&include_subdomains=true&expand=dns_names" % suf)
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=45) as r:
                data = json.load(r)
            for row in data:
                for n in row.get("dns_names", []):
                    n = n.strip().lower()
                    if n.endswith("." + suf) and "*" not in n:
                        hasil.add(n)
            print("    certspotter: %d" % len(hasil))
        except Exception as e:
            print("    certspotter gagal: %s" % e)
    if not hasil:
        try:
            url = "https://rapiddns.io/subdomain/%s?full=1" % suf
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=45) as r:
                html = r.read(900000).decode("utf-8", "ignore")
            for m in DOM_RE.findall(html):
                if m.lower().endswith("." + suf):
                    hasil.add(m.lower())
            print("    rapiddns: %d" % len(hasil))
        except Exception as e:
            print("    rapiddns gagal: %s" % e)
    return hasil


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
    h = {"status": "mati", "http_status": None, "server": None, "waf": None}
    try:
        socket.getaddrinfo(domain, 443, proto=socket.IPPROTO_TCP)
    except Exception as e:
        h["catatan"] = "dns:" + type(e).__name__
        return h
    for skema in ("https", "http"):
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
                     catatan=?,diperiksa_at=? WHERE domain=?""",
                  (h["status"], h["http_status"], h["server"], h["waf"], skor(h),
                   h.get("catatan"), datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   r["domain"]))
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
    top = c.execute("""SELECT domain,status,skor,waf FROM kandidat
                       WHERE status IN ('hidup','dijaga','alih')
                       ORDER BY skor DESC LIMIT 15""").fetchall()
    if top:
        print("PRIORITAS:")
        for r in top:
            print("  %3d  %-42s%-8s%s" % (r["skor"], r["domain"], r["status"], r["waf"] or ""))


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
    m = sub.add_parser("map"); m.set_defaults(f=cmd_map)
    e = sub.add_parser("export"); e.add_argument("--out", default="kandidat.csv"); e.set_defaults(f=cmd_export)
    a = p.parse_args()
    print("basis:", db_path())
    a.f(a)


if __name__ == "__main__":
    main()
