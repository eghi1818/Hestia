"""Hestia API. Satu origin: /api untuk data, / untuk dashboard.
Kompatibel Python 3.8+ (memakai Optional, bukan sintaks pipa)."""
import sqlite3
from pathlib import Path
from typing import List, Optional

from fastapi import Body, BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import db

# tools/ di sys.path + impor scrape tingkat modul (S-101)
import os as _op
import sys as _sp
_TOOLS = _op.path.join(_op.path.dirname(_op.path.dirname(_op.path.abspath(__file__))), "tools")
if _TOOLS not in _sp.path:
    _sp.path.insert(0, _TOOLS)
import scrape  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STATUS_SAH = {"baru", "kandidat", "dianalisis", "aktif", "rusak", "dibersihkan", "nonaktif", "hidup", "mati", "dijaga", "hilang"}

app = FastAPI(title="Hestia API", version="0.1.0")
db.init()

class TargetMasuk(BaseModel):
    domain: str
    tipe: str = "lain"
    status: str = "kandidat"
    owner: str = ""
    tags: str = ""
    catatan: str = ""

class TargetUbah(BaseModel):
    domain: Optional[str] = None
    tipe: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[str] = None
    tags: Optional[str] = None
    catatan: Optional[str] = None

def ambil(tid: int) -> dict:
    with db.conn() as c:
        r = c.execute("SELECT * FROM targets WHERE id = ?", (tid,)).fetchone()
    if r is None:
        raise HTTPException(404, "target tidak ditemukan")
    return dict(r)

@app.get("/api/health")
def health():
    with db.conn() as c:
        n = c.execute("SELECT COUNT(*) AS n FROM targets").fetchone()["n"]
    return {"ok": True, "service": "hestia", "targets": n}

@app.get("/api/targets")
def daftar_target(status: Optional[str] = None, q: Optional[str] = None) -> List[dict]:
    sql = "SELECT * FROM targets"
    arg = []
    if status:
        sql += " WHERE status = ?"
        arg.append(status)
    if q:
        sql += " AND domain LIKE ?" if status else " WHERE domain LIKE ?"
        arg.append("%" + q + "%")
    sql += " ORDER BY id DESC"
    with db.conn() as c:
        return [dict(r) for r in c.execute(sql, arg).fetchall()]

@app.post("/api/targets", status_code=201)
def tambah_target(t: TargetMasuk):
    if t.status not in STATUS_SAH:
        raise HTTPException(400, "status tidak dikenal: " + t.status)
    try:
        with db.conn() as c:
            cur = c.execute(
                "INSERT INTO targets (domain,tipe,status,owner,tags,catatan)"
                " VALUES (?,?,?,?,?,?)",
                (t.domain.strip(), t.tipe, t.status, t.owner, t.tags, t.catatan))
            tid = cur.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(409, "domain sudah terdaftar: " + t.domain)
    return ambil(tid)

@app.get("/api/targets/{tid}")
def detail_target(tid: int):
    return ambil(tid)

@app.patch("/api/targets/{tid}")
def ubah_target(tid: int, u: TargetUbah):
    ambil(tid)
    if u.status is not None and u.status not in STATUS_SAH:
        raise HTTPException(400, "status tidak dikenal: " + u.status)
    kolom, nilai = [], []
    for k, v in u.dict(exclude_none=True).items():
        kolom.append(k + " = ?")
        nilai.append(v)
    if not kolom:
        return ambil(tid)
    kolom.append("updated_at = datetime('now')")
    nilai.append(tid)
    try:
        with db.conn() as c:
            c.execute("UPDATE targets SET " + ", ".join(kolom) + " WHERE id = ?", nilai)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "domain sudah dipakai target lain")
    return ambil(tid)

@app.delete("/api/targets/{tid}", status_code=204)
def hapus_target(tid: int):
    ambil(tid)
    with db.conn() as c:
        c.execute("DELETE FROM targets WHERE id = ?", (tid,))

@app.get("/")
def beranda():
    return FileResponse(ROOT / "dashboard" / "index.html")


@app.get("/live.js")
def live_js():
    return FileResponse(ROOT / "dashboard" / "live.js",
                        media_type="application/javascript")


# --- catatan dari sisi klien, untuk membuktikan uji di browser ---
with db.conn() as _c:
    _c.executescript("""
    CREATE TABLE IF NOT EXISTS clientlog (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      waktu TEXT NOT NULL DEFAULT (datetime('now')),
      peristiwa TEXT NOT NULL,
      rincian TEXT NOT NULL DEFAULT ''
    );
    """)

@app.post("/api/clientlog", status_code=201)
def catat_client(peristiwa: str, rincian: str = ""):
    with db.conn() as c:
        c.execute("INSERT INTO clientlog (peristiwa, rincian) VALUES (?, ?)",
                  (peristiwa, rincian))
    return {"ok": True}

@app.get("/api/clientlog")
def lihat_client(batas: int = 30):
    with db.conn() as c:
        rows = c.execute(
            "SELECT * FROM clientlog ORDER BY id DESC LIMIT ?", (batas,)
        ).fetchall()
    return [dict(r) for r in rows]


# --- recon: sentuhan pertama ke domain target ---
with db.conn() as _c:
    _c.executescript("""
    CREATE TABLE IF NOT EXISTS recon (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      target_id INTEGER NOT NULL,
      waktu TEXT NOT NULL DEFAULT (datetime('now')),
      http_status INTEGER,
      server TEXT DEFAULT '',
      content_type TEXT DEFAULT '',
      redirect TEXT DEFAULT '',
      ms INTEGER,
      judul TEXT DEFAULT '',
      catatan TEXT DEFAULT ''
    );
    """)

_HDR_BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Connection": "close",
}


def _ambil(domain, skema="https"):
    """Satu request saja. Kembalikan dict hasil."""
    import urllib.request, urllib.error, time, re
    url = skema + "://" + domain
    req = urllib.request.Request(url, headers=_HDR_BROWSER)
    mulai = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            isi = r.read(60000).decode("utf-8", "ignore")
            return {
                "http_status": r.status,
                "server": r.headers.get("Server", ""),
                "content_type": r.headers.get("Content-Type", ""),
                "redirect": (r.geturl() if r.geturl() != url else ""),
                "ms": int((time.time() - mulai) * 1000),
                "judul": (re.search(r"<title[^>]*>(.*?)</title>", isi, re.S | re.I).group(1).strip()[:120]
                          if re.search(r"<title[^>]*>(.*?)</title>", isi, re.S | re.I) else ""),
                "catatan": "",
            }
    except urllib.error.HTTPError as e:
        return {"http_status": e.code, "server": e.headers.get("Server", ""),
                "content_type": e.headers.get("Content-Type", ""), "redirect": "",
                "ms": int((time.time() - mulai) * 1000), "judul": "",
                "catatan": "HTTPError"}
    except Exception as e:
        if skema == "https":
            h = _ambil(domain, "http")
            if h["http_status"] != 0:
                return h
        return {"http_status": 0, "server": "", "content_type": "", "redirect": "",
                "ms": int((time.time() - mulai) * 1000), "judul": "",
                "catatan": type(e).__name__ + ": " + str(e)[:80]}

@app.post("/api/targets/{tid}/recon")
def recon_target(tid: int, skema: str = "https"):
    t = ambil(tid)
    if not t:
        raise HTTPException(404, "target tidak ada")
    hasil = _ambil(t["domain"], skema)
    _st = scrape.status_dari_kode(hasil["http_status"])
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO recon (target_id,http_status,server,content_type,redirect,ms,judul,catatan)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (tid, hasil["http_status"], hasil["server"], hasil["content_type"],
             hasil["redirect"], hasil["ms"], hasil["judul"], hasil["catatan"]))
        rid = cur.lastrowid
        c.execute("UPDATE targets SET status=? WHERE id=?", (_st, tid))
    with db.conn() as c:
        r = c.execute("SELECT * FROM recon WHERE id = ?", (rid,)).fetchone()
    return dict(r)


@app.get("/api/targets/{tid}/recon")
def lihat_recon(tid: int):
    with db.conn() as c:
        rows = c.execute(
            "SELECT * FROM recon WHERE target_id = ? ORDER BY id DESC LIMIT 20", (tid,)
        ).fetchall()
    return [dict(r) for r in rows]


# ---------- kandidat (hasil sapuan) ----------
def _db_kandidat():
    import sqlite3, os
    p = os.environ.get("HESTIA_DB")
    if not p:
        try:
            from app import db as _d
            for at in ("DB_PATH", "PATH", "DB", "DBFILE"):
                v = getattr(_d, at, None)
                if isinstance(v, str) and v:
                    p = v
                    break
        except Exception:
            pass
    c = sqlite3.connect(p or "data/hestia.db")
    c.execute("pragma busy_timeout = 5000")
    c.execute("pragma journal_mode = wal")
    c.row_factory = sqlite3.Row
    return c


@app.get("/api/kandidat/ringkas")
def api_kandidat_ringkas():
    k = _db_kandidat()
    tot = k.execute("SELECT count(*) FROM kandidat").fetchone()[0]
    per = [dict(r) for r in k.execute(
        "SELECT suffix,status,count(*) n FROM kandidat GROUP BY suffix,status")]
    jen = [dict(r) for r in k.execute(
        "SELECT suffix,jenis,count(*) n FROM kandidat GROUP BY suffix,jenis")]

    def _c(sql):
        return k.execute(sql).fetchone()[0]

    ang = {
        "hidup": _c("SELECT count(*) FROM kandidat WHERE status='hidup'"),
        "dijaga": _c("SELECT count(*) FROM kandidat WHERE status='dijaga'"),
        "mati": _c("SELECT count(*) FROM kandidat WHERE status='mati'"),
        "galat": _c("SELECT count(*) FROM kandidat WHERE status='galat'"),
        "baru": _c("SELECT count(*) FROM kandidat WHERE status='baru'"),
        "infra": _c("SELECT count(*) FROM kandidat WHERE infra=1"),
        "kosong": _c("SELECT count(*) FROM kandidat WHERE hollow=1"),
        "panel": _c("SELECT count(*) FROM kandidat WHERE petunjuk='halaman panel'"),
        "bersih": _c("SELECT count(*) FROM kandidat WHERE (infra IS NULL OR infra=0)"
                     " AND (hollow IS NULL OR hollow=0)"),
    }
    k.close()
    out = {"total": tot, "per_suffix_status": per, "per_suffix_jenis": jen}
    out.update(ang)
    return out


@app.get("/api/kandidat")
def api_kandidat(suffix: Optional[str] = None, status: Optional[str] = None,
                 jenis: Optional[str] = None, q: Optional[str] = None,
                 limit: int = 100, offset: int = 0,
                 tanpa_infra: bool = False,
                 tanpa_kosong: bool = False):
    w, a = [], []
    if suffix: w.append("suffix=?"); a.append(suffix)
    if status: w.append("status=?"); a.append(status)
    if jenis: w.append("jenis=?"); a.append(jenis)
    if q: w.append("domain LIKE ?"); a.append("%" + q + "%")
    if tanpa_infra: w.append("infra=0")
    if tanpa_kosong: w.append("(hollow IS NULL OR hollow=0)")
    where = (" WHERE " + " AND ".join(w)) if w else ""
    k = _db_kandidat()
    tot = k.execute("SELECT count(*) FROM kandidat" + where, a).fetchone()[0]
    rows = [dict(r) for r in k.execute(
        "SELECT * FROM kandidat" + where + " ORDER BY skor DESC, domain LIMIT ? OFFSET ?",
        a + [limit, offset])]
    k.close()
    return {"total": tot, "limit": limit, "offset": offset, "item": rows}


@app.post("/api/kandidat/periksa")
def api_kandidat_periksa(limit: int = 5, suffix: Optional[str] = None):
    import sys as _sys, os as _os
    from datetime import datetime as _dt
    _t = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "tools")
    if _t not in _sys.path:
        _sys.path.insert(0, _t)
    import scrape
    c = scrape.conn()
    q, a = "SELECT domain,suffix FROM kandidat WHERE status='baru'", []
    if suffix:
        q += " AND suffix=?"; a.append(suffix)
    q += " ORDER BY domain LIMIT ?"
    a.append(max(1, min(limit, 20)))
    baris = c.execute(q, a).fetchall()
    ringkas = {}
    for r in baris:
        h = scrape.verify_one(r["domain"]); h["suffix"] = r["suffix"]
        c.execute("""UPDATE kandidat SET status=?,http_status=?,server=?,waf=?,skor=?,
                     catatan=?,diperiksa_at=? WHERE domain=?""",
                  (h["status"], h["http_status"], h["server"], h["waf"], scrape.skor(h, r["domain"]),
                   h.get("catatan"), _dt.now().isoformat(timespec="seconds"), r["domain"]))
        c.commit()
        ringkas[h["status"]] = ringkas.get(h["status"], 0) + 1
    c.close()
    return {"diperiksa": len(baris), "ringkas": ringkas}


# ---------- periksa massal di latar belakang ----------
_PS = {"jalan": False, "selesai": 0, "target": 0, "ringkas": {}}


def _jalankan_periksa(limit, suffix):
    import sys as _sys, os as _os, time as _t
    from datetime import datetime as _dt
    _t2 = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "tools")
    if _t2 not in _sys.path:
        _sys.path.insert(0, _t2)
    import scrape
    _PS.update({"jalan": True, "selesai": 0, "target": 0, "ringkas": {}})
    try:
        c = scrape.conn()
        q, a = "SELECT domain,suffix FROM kandidat WHERE status='baru'", []
        if suffix:
            q += " AND suffix=?"; a.append(suffix)
        q += " ORDER BY skor DESC, domain LIMIT ?"
        a.append(max(1, min(limit, 500)))
        baris = c.execute(q, a).fetchall()
        _PS["target"] = len(baris)
        for r in baris:
            h = scrape.verify_one(r["domain"]); h["suffix"] = r["suffix"]
            c.execute("""UPDATE kandidat SET status=?,http_status=?,server=?,waf=?,skor=?,
                         catatan=?,diperiksa_at=?,latensi_ms=? WHERE domain=?""",
                      (h["status"], h["http_status"], h["server"], h["waf"], scrape.skor(h, r["domain"]),
                       h.get("catatan"), _dt.now().isoformat(timespec="seconds"),
                       h.get("latensi_ms", 0), r["domain"]))
            c.commit()
            _PS["selesai"] += 1
            _PS["ringkas"][h["status"]] = _PS["ringkas"].get(h["status"], 0) + 1
            _t.sleep(0.6)
        c.close()
    finally:
        _PS["jalan"] = False


@app.post("/api/kandidat/periksa-latar")
def api_periksa_latar(bg: BackgroundTasks, limit: int = 50, suffix: Optional[str] = None):
    if _PS["jalan"]:
        return {"sudah_jalan": True, "status": _PS}
    bg.add_task(_jalankan_periksa, limit, suffix)
    return {"mulai": True, "limit": limit}


@app.get("/api/kandidat/periksa-status")
def api_periksa_status():
    return _PS


# ---------- putaran otomatis: verifikasi lalu crawl ----------
_PUT = {"jalan": False, "fase": "", "verif": 0, "crawl": 0, "kandidat_baru": 0, "ringkas": {}}


def _jalankan_putaran(verif, crawl, suffix):
    import sys as _sys, os as _os, time as _t
    from datetime import datetime as _dt
    _t2 = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "tools")
    if _t2 not in _sys.path:
        _sys.path.insert(0, _t2)
    import scrape
    _PUT.update({"jalan": True, "fase": "verifikasi", "verif": 0, "crawl": 0,
                 "kandidat_baru": 0, "ringkas": {}})
    try:
        c = scrape.conn()
        now = _dt.now().isoformat(timespec="seconds")
        q, a = "SELECT domain,suffix FROM kandidat WHERE status='baru'", []
        if suffix:
            q += " AND suffix=?"; a.append(suffix)
        q += " ORDER BY skor DESC, domain LIMIT ?"; a.append(max(0, verif))
        for r in c.execute(q, a).fetchall():
            h = scrape.verify_one(r["domain"]); h["suffix"] = r["suffix"]
            c.execute("""UPDATE kandidat SET status=?,http_status=?,server=?,waf=?,skor=?,
                         catatan=?,diperiksa_at=?,latensi_ms=? WHERE domain=?""",
                      (h["status"], h["http_status"], h["server"], h["waf"], scrape.skor(h, r["domain"]),
                       h.get("catatan"), now, h.get("latensi_ms", 0), r["domain"]))
            c.commit()
            _PUT["verif"] += 1
            _PUT["ringkas"][h["status"]] = _PUT["ringkas"].get(h["status"], 0) + 1
            _t.sleep(0.6)

        _PUT["fase"] = "crawl"
        q2 = ("SELECT domain FROM kandidat WHERE status IN ('hidup','alih','dijaga')"
              " AND (dicrawl IS NULL OR dicrawl=0)")
        a2 = []
        if suffix:
            q2 += " AND suffix=?"; a2.append(suffix)
        q2 += " ORDER BY skor DESC LIMIT ?"; a2.append(max(0, crawl))
        ketemu = set()
        for (d,) in c.execute(q2, a2).fetchall():
            html = scrape.ambil_html(d)
            if html is None:
                c.execute("UPDATE kandidat SET dicrawl=2 WHERE domain=?", (d,)); c.commit()
                _t.sleep(0.6); continue
            dapat = set(m.lower() for m in scrape.DOM_RE.findall(html))
            pet = scrape.hollow_of(html)
            if not pet and d.split(".")[0].lower() in scrape.PANEL:
                pet = "halaman panel"
            for t in dapat:
                if t != d:
                    c.execute("INSERT OR IGNORE INTO tautan(dari,ke,dibuat) VALUES(?,?,?)", (d, t, now))
            ketemu |= dapat
            c.execute("""UPDATE kandidat SET dicrawl=1, ukuran=?, hollow=?, petunjuk=?
                         WHERE domain=?""", (len(html), 1 if pet else 0, pet, d))
            c.commit()
            _PUT["crawl"] += 1
            _t.sleep(0.6)
        _PUT["kandidat_baru"] = scrape.simpan(c, ketemu, "crawl")
        c.close()
    finally:
        _PUT["fase"] = "selesai"
        _PUT["jalan"] = False


@app.post("/api/putaran")
def api_putaran(bg: BackgroundTasks, verif: int = 20, crawl: int = 15, suffix: Optional[str] = None):
    if _PUT["jalan"]:
        return {"sudah_jalan": True, "status": _PUT}
    bg.add_task(_jalankan_putaran, verif, crawl, suffix)
    return {"mulai": True, "verif": verif, "crawl": crawl}


@app.get("/api/putaran/status")
def api_putaran_status():
    return _PUT


@app.get("/ikhtisar.js")
def ikhtisar_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/ikhtisar.js", media_type="application/javascript")


@app.get("/api/tautan/ringkas")
def api_tautan_ringkas():
    c = _db_kandidat()

    def q(s):
        return c.execute(s).fetchone()[0]

    out = {
        "total": q("SELECT count(*) FROM tautan"),
        "sumber": q("SELECT count(DISTINCT dari) FROM tautan"),
        "penerima": q("SELECT count(DISTINCT ke) FROM tautan"),
        "kandidat": q("SELECT count(*) FROM kandidat"),
        "per_akhiran": [dict(r) for r in c.execute(
            "SELECT k.suffix, count(DISTINCT t.ke) n FROM tautan t "
            "JOIN kandidat k ON k.domain=t.ke GROUP BY k.suffix")],
        "teratas": [dict(r) for r in c.execute(
            "SELECT ke, count(*) n FROM tautan GROUP BY ke ORDER BY n DESC LIMIT 10")],
    }
    c.close()
    return out


@app.get("/api/tautan")
def api_tautan(limit: int = 200, dari: Optional[str] = None, ke: Optional[str] = None):
    c = _db_kandidat()
    w, a = [], []
    if dari:
        w.append("dari=?"); a.append(dari)
    if ke:
        w.append("ke=?"); a.append(ke)
    where = (" WHERE " + " AND ".join(w)) if w else ""
    tot = c.execute("SELECT count(*) FROM tautan" + where, a).fetchone()[0]
    rows = [dict(r) for r in c.execute(
        "SELECT * FROM tautan" + where + " ORDER BY dari, ke LIMIT ?", a + [limit])]
    c.close()
    return {"total": tot, "item": rows}


@app.get("/tautan.js")
def tautan_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/tautan.js", media_type="application/javascript")


@app.get("/api/audit")
def api_audit(batas: int = 60, peristiwa: str = "", cari: str = ""):
    c = _db_kandidat()
    w, a = [], []
    if peristiwa:
        w.append("peristiwa=?"); a.append(peristiwa)
    if cari:
        w.append("(peristiwa LIKE ? OR rincian LIKE ?)")
        a += ["%" + cari + "%", "%" + cari + "%"]
    where = (" WHERE " + " AND ".join(w)) if w else ""
    tot = c.execute("SELECT count(*) FROM clientlog" + where, a).fetchone()[0]
    rows = [dict(r) for r in c.execute(
        "SELECT id, waktu, peristiwa, rincian FROM clientlog" + where
        + " ORDER BY id DESC LIMIT ?", a + [batas])]
    c.close()
    return {"total": tot, "item": rows}


@app.get("/api/audit/peristiwa")
def api_audit_peristiwa():
    c = _db_kandidat()
    rows = [dict(r) for r in c.execute(
        "SELECT peristiwa, count(*) AS n FROM clientlog GROUP BY peristiwa ORDER BY n DESC")]
    c.close()
    return {"item": rows}


@app.get("/api/monitoring")
def api_monitoring(batas: int = 25):
    c = _db_kandidat()
    alerts = [dict(r) for r in c.execute(
        "SELECT domain,status,http_status,catatan,diperiksa_at FROM kandidat "
        "WHERE status IN ('galat','dijaga') AND (infra IS NULL OR infra=0) "
        "ORDER BY diperiksa_at DESC LIMIT 12")]
    riwayat = [dict(r) for r in c.execute(
        "SELECT domain,status,http_status,latensi_ms,diperiksa_at FROM kandidat "
        "WHERE diperiksa_at IS NOT NULL ORDER BY diperiksa_at DESC LIMIT ?", (batas,))]
    sehat = [dict(r) for r in c.execute(
        "SELECT suffix, "
        "SUM(CASE WHEN status IN ('hidup','dijaga','alih') THEN 1 ELSE 0 END) baik, "
        "SUM(CASE WHEN status IN ('mati','galat') THEN 1 ELSE 0 END) buruk, count(*) total "
        "FROM kandidat GROUP BY suffix")]
    c.close()
    return {"alerts": alerts, "riwayat": riwayat, "kesehatan": sehat}


@app.get("/audit.js")
def audit_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/audit.js", media_type="application/javascript")


@app.get("/tanam.js")
def tanam_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/tanam.js", media_type="application/javascript")


@app.get("/driver.js")
def driver_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/driver.js", media_type="application/javascript")


@app.get("/monitor.js")
def monitor_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/monitor.js", media_type="application/javascript")


# ---------- kredensial / deployment / konten ----------
_TABEL = {
    "kredensial": ("target TEXT, nama TEXT, tipe TEXT, level TEXT, secret TEXT, "
                   "berlaku_sd TEXT, created_at TEXT",
                   ["target", "nama", "tipe", "level", "secret", "berlaku_sd", "created_at"]),
    "deployment": ("waktu TEXT, target TEXT, path TEXT, template TEXT, status TEXT",
                   ["waktu", "target", "path", "template", "status"]),
    "anggota": ("nama TEXT, peran TEXT, ditambah TEXT",
                ["nama", "peran", "ditambah"]),
    "konten": ("url TEXT, target TEXT, kata_kunci TEXT, template TEXT, "
               "status_indeks TEXT, posisi REAL",
               ["url", "target", "kata_kunci", "template", "status_indeks", "posisi"]),
}


_KOLOM = {}


def _siap_tabel():
    """DB adalah sumber daftar kolom; _TABEL hanya untuk membuat tabel di clone bersih.
    Kolom disegarkan setiap panggilan supaya kolom baru dari migrasi ikut terbaca."""
    global _KOLOM
    c = _db_kandidat()
    _KOLOM.clear()
    for n, (kol, _x) in _TABEL.items():
        c.execute("CREATE TABLE IF NOT EXISTS %s(id INTEGER PRIMARY KEY AUTOINCREMENT, %s)"
                  % (n, kol))
    for n in _TABEL:
        _KOLOM[n] = [r[1] for r in c.execute("pragma table_info(%s)" % n)]
    c.commit()
    return c


def _daftar(nama, target=None, limit=200, offset=0):
    limit = max(1, min(int(limit or 200), 2000))
    offset = max(0, int(offset or 0))
    c = _siap_tabel()
    if target:
        total = c.execute("SELECT COUNT(*) FROM " + nama + " WHERE target=?", (target,)).fetchone()[0]
        rows = [dict(r) for r in c.execute(
            "SELECT * FROM " + nama + " WHERE target=? ORDER BY id DESC LIMIT ? OFFSET ?",
            (target, limit, offset))]
    else:
        total = c.execute("SELECT COUNT(*) FROM " + nama).fetchone()[0]
        rows = [dict(r) for r in c.execute(
            "SELECT * FROM " + nama + " ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))]
    c.close()
    return {"total": total, "jumlah": len(rows), "limit": limit, "offset": offset, "item": rows}


def _tambah(nama, body):
    c = _siap_tabel()
    kol = [k for k in _KOLOM[nama] if k != "id"]
    dibuang = sorted(k for k in body if k not in kol)
    nilai = [body.get(k) for k in kol]
    cur = c.execute("INSERT INTO %s(%s) VALUES(%s)"
                    % (nama, ",".join(kol), ",".join("?" * len(kol))), nilai)
    c.commit()
    baru = dict(c.execute("SELECT * FROM %s WHERE id=?" % nama, (cur.lastrowid,)).fetchone())
    c.close()
    return {"ok": True, "tabel": nama, "item": baru, "dibuang": dibuang}


@app.get("/api/kredensial")
def api_kredensial(target: Optional[str] = None, limit: int = 200, offset: int = 0):
    return _daftar("kredensial", target, limit, offset)


@app.get("/api/deployment")
def api_deployment(target: Optional[str] = None, limit: int = 200, offset: int = 0):
    return _daftar("deployment", target, limit, offset)


@app.get("/api/konten")
def api_konten(target: Optional[str] = None, limit: int = 200, offset: int = 0):
    return _daftar("konten", target, limit, offset)


@app.post("/api/kredensial")
def api_kredensial_tambah(body: dict = Body(...)):
    return _tambah("kredensial", body)


@app.post("/api/deployment")
def api_deployment_tambah(body: dict = Body(...)):
    return _tambah("deployment", body)


@app.post("/api/konten")
def api_konten_tambah(body: dict = Body(...)):
    return _tambah("konten", body)


@app.get("/konten.js")
def konten_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/konten.js", media_type="application/javascript")


def _hapus(nama, tid):
    c = _siap_tabel()
    c.execute("DELETE FROM %s WHERE id=?" % nama, (tid,))
    c.commit()
    c.close()
    return {"ok": True, "tabel": nama, "id": tid}


@app.delete("/api/kredensial/{tid}")
def api_kredensial_hapus(tid: int):
    return _hapus("kredensial", tid)


@app.delete("/api/deployment/{tid}")
def api_deployment_hapus(tid: int):
    return _hapus("deployment", tid)


@app.delete("/api/konten/{tid}")
def api_konten_hapus(tid: int):
    return _hapus("konten", tid)


@app.get("/api/recon")
def api_recon(batas: int = 50):
    c = _db_kandidat()
    rows = [dict(r) for r in c.execute(
        "SELECT * FROM recon ORDER BY id DESC LIMIT ?", (batas,))]
    c.close()
    return {"total": len(rows), "item": rows}


@app.get("/detail.js")
def detail_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/detail.js", media_type="application/javascript")


@app.get("/recon.js")
def recon_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/recon.js", media_type="application/javascript")


@app.get("/api/kandidat.csv")
def api_kandidat_csv(suffix: Optional[str] = None, status: Optional[str] = None,
                     tanpa_infra: bool = True, tanpa_kosong: bool = True):
    import csv as _csv, io
    from fastapi.responses import Response
    c = _db_kandidat()
    w, a = [], []
    if suffix:
        w.append("suffix=?"); a.append(suffix)
    if status:
        w.append("status=?"); a.append(status)
    if tanpa_infra:
        w.append("(infra IS NULL OR infra=0)")
    if tanpa_kosong:
        w.append("(hollow IS NULL OR hollow=0)")
    where = (" WHERE " + " AND ".join(w)) if w else ""
    rows = c.execute(
        "SELECT domain,suffix,jenis,status,http_status,server,waf,skor FROM kandidat"
        + where + " ORDER BY skor DESC, domain", a).fetchall()
    c.close()
    buf = io.StringIO()
    wr = _csv.writer(buf)
    wr.writerow(["domain", "suffix", "jenis", "status", "http_status", "server", "waf", "skor"])
    for r in rows:
        wr.writerow(list(r))
    return Response(content=buf.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=kandidat.csv"})


@app.get("/ekspor.js")
def ekspor_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/ekspor.js", media_type="application/javascript")


@app.get("/api/anggota")
def api_anggota():
    return _daftar("anggota")


@app.post("/api/anggota")
def api_anggota_tambah(body: dict = Body(...)):
    return _tambah("anggota", body)


@app.delete("/api/anggota/{tid}")
def api_anggota_hapus(tid: int):
    return _hapus("anggota", tid)


@app.post("/api/tautan")
def api_tautan_tambah(body: dict = Body(...)):
    import datetime as _d
    c = _db_kandidat()
    c.execute("CREATE TABLE IF NOT EXISTS tautan(dari TEXT, ke TEXT, dibuat TEXT,"
              " PRIMARY KEY(dari,ke))")
    c.execute("INSERT OR IGNORE INTO tautan(dari,ke,dibuat) VALUES(?,?,?)",
              (body.get("dari"), body.get("ke"), _d.date.today().isoformat()))
    c.commit()
    c.close()
    return {"ok": True}


@app.post("/api/kredensial/rotasi")
def api_kredensial_rotasi():
    import datetime as _d
    baru = (_d.date.today() + _d.timedelta(days=365)).isoformat()
    c = _siap_tabel()
    cur = c.execute("UPDATE kredensial SET berlaku_sd=?", (baru,))
    c.commit()
    c.close()
    return {"ok": True, "diubah": cur.rowcount, "berlaku_sd": baru}


def _siap_setelan(c):
    c.execute("CREATE TABLE IF NOT EXISTS setelan(id INTEGER PRIMARY KEY AUTOINCREMENT,"
              " kunci TEXT, nilai TEXT)")


@app.get("/api/setelan")
def api_setelan():
    c = _siap_tabel()
    _siap_setelan(c)
    rows = [dict(r) for r in c.execute("SELECT kunci,nilai FROM setelan")]
    c.close()
    return {"total": len(rows), "item": rows}


@app.post("/api/setelan")
def api_setelan_simpan(body: dict = Body(...)):
    c = _siap_tabel()
    _siap_setelan(c)
    c.execute("DELETE FROM setelan WHERE kunci=?", (body.get("kunci"),))
    c.execute("INSERT INTO setelan(kunci,nilai) VALUES(?,?)",
              (body.get("kunci"), body.get("nilai")))
    c.commit()
    c.close()
    return {"ok": True}


@app.get("/aksi.js")
def aksi_js():
    from fastapi.responses import FileResponse
    return FileResponse("dashboard/aksi.js", media_type="application/javascript")


@app.post("/api/konten/{tid}/indeks")
def api_konten_indeks(tid: int, nilai: str = "terindeks"):
    c = _siap_tabel()
    c.execute("UPDATE konten SET status_indeks=? WHERE id=?", (nilai, tid))
    c.commit()
    c.close()
    return {"ok": True, "id": tid, "status_indeks": nilai}


@app.post("/api/clientlog/bersih")
@app.get("/api/clientlog/bersih")
def clientlog_bersih(simpan: int = 0):
    with db.conn() as c:
        sebelum = c.execute("select count(*) from clientlog").fetchone()[0]
        if simpan > 0:
            c.execute("delete from clientlog where id not in (select id from clientlog order by id desc limit ?)", (simpan,))
        else:
            c.execute("delete from clientlog")
        c.commit()
        sesudah = c.execute("select count(*) from clientlog").fetchone()[0]
    return {"ok": True, "sebelum": sebelum, "sesudah": sesudah, "dihapus": sebelum - sesudah}

# --- DoH + TLS santai opsional (HESTIA_DOH=1 / HESTIA_TLS_RELAX=1) ---
try:
    import os as _os, sys as _sys
    if _os.environ.get("HESTIA_DOH") == "1" or _os.environ.get("HESTIA_TLS_RELAX") == "1":
        _sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "tools"))
        import net as _net
        _net.pasang()
        _net.pasang_tls()
        print("[net]", _net.info())
except Exception as _e:
    print("[net] dilewati:", _e)


@app.get("/api/teknologi-ringkas")
def teknologi_ringkas():
    with db.conn() as c:
        waf = [dict(r) for r in c.execute("select coalesce(waf,'-') as waf, count(*) as n from targets group by waf order by n desc")]
        kanal = [dict(r) for r in c.execute("select coalesce(kanal,'-') as kanal, count(*) as n from targets group by kanal order by n desc limit 12")]
        teknologi = [dict(r) for r in c.execute("select coalesce(teknologi,'-') as teknologi, count(*) as n from targets group by teknologi order by n desc limit 12")]
        pintu = c.execute("select count(*) from targets where pintu is not null and pintu != '-'").fetchone()[0]
        kosong = c.execute("select count(*) from targets where coalesce(teknologi,'')=''").fetchone()[0]
    return {"waf": waf, "kanal": kanal, "teknologi": teknologi, "ada_pintu": pintu, "kosong": kosong}


@app.post("/api/teknologi/pindai")
def teknologi_pindai(body: dict):
    import datetime as _dt
    try:
        import teknologi
    except ImportError:
        from tools import teknologi
    tid = body.get("target_id")
    batas = int(body.get("batas") or 0)
    hari = _dt.date.today().isoformat()
    with db.conn() as c:
        if tid:
            rows = [dict(r) for r in c.execute("select id, domain from targets where id=?", (tid,))]
        elif body.get("kosong"):
            rows = [dict(r) for r in c.execute("select id, domain from targets where coalesce(teknologi,'')='' order by id")]
        else:
            rows = [dict(r) for r in c.execute("select id, domain from targets order by id")]
    if batas:
        rows = rows[:batas]
    hasil = []
    for r in rows:
        try:
            d = teknologi.periksa(r["domain"])
        except Exception as e:
            hasil.append({"id": r["id"], "domain": r["domain"], "galat": str(e)[:120]})
            continue
        with db.conn() as c:
            c.execute("update targets set teknologi=?, server=?, waf=?, pintu=?, kanal=?, dianalisa=? where id=?",
                      (d["teknologi"], d["server"], d["waf"], d["pintu"], d["kanal"], hari, r["id"]))
        hasil.append({"id": r["id"], "domain": r["domain"], "teknologi": d["teknologi"] or "-",
                      "waf": d["waf"] or "-", "pintu": d["pintu"] or "-"})
    return {"ok": True, "diperiksa": len(hasil), "tanggal": hari, "item": hasil}


@app.post("/api/tanam")
def jalankan_tanam(body: dict):
    import tanam
    tid = int(body.get("target_id") or 0)
    t = ambil(tid)
    if not t:
        raise HTTPException(404, "target tidak ada")
    u = (body.get("user") or "").strip()
    pw = (body.get("sandi") or "").strip()
    if u and pw:
        tanam.simpan_kredensial(t["domain"], u, pw, tid=tid)
    if not u:
        u, pw = tanam.kredensial_dari_db(t["domain"], tid=tid)
    return tanam.tanam(t["domain"], user=u, sandi=pw, sapu_dulu=bool(body.get("sapu")))





@app.middleware("http")
async def _auth(request, call_next):
    import base64 as _b64
    import os as _o
    from fastapi.responses import JSONResponse as _JR
    if request.url.path in ("/api/health",):
        return await call_next(request)
    sandi = _o.environ.get("HESTIA_SANDI", "hestia")
    h = request.headers.get("authorization", "")
    if h.startswith("Basic "):
        try:
            _u, p2 = _b64.b64decode(h[6:]).decode("utf-8", "ignore").split(":", 1)
            if p2 == sandi:
                return await call_next(request)
        except Exception:
            pass
    return _JR({"detail": "perlu login"}, status_code=401,
               headers={"WWW-Authenticate": 'Basic realm="Hestia"'})

# ===== KONSOL (S-136) =====
import asyncio as _asyncio
import fcntl as _fcntl
import json as _json
import os as _os
import re as _re
from pathlib import Path as _Path

_AKAR = _Path(__file__).resolve().parent.parent
_DOK_EV = _AKAR / "docs" / "evidence"
_KUNCI = "/tmp/hestia-r.lock"
_JALAN = {}


def _job_terputus():
    with db.conn() as c:
        baris = c.execute("SELECT id,pid FROM job WHERE status='jalan'").fetchall()
    for _jid, _pid in baris:
        if _pid:
            try:
                _os.killpg(_pid, 15)
            except Exception:
                try:
                    _os.kill(_pid, 15)
                except Exception:
                    pass
    with db.conn() as c:
        c.execute("UPDATE job SET status='terputus', selesai=datetime('now') WHERE status='jalan'")


def _nomor_r(c=None):
    """Nomor R berikutnya. Numerik, dari SELURUH tabel job termasuk yang gagal.

    r_nomor bertipe TEXT 'R-<n>', jadi MAX() langsung salah (R-9 > R-10).
    Sebelumnya nomor dihitung dari berkas R-*.txt, padahal job zombie tidak
    menghasilkan berkas -> nomor mengulang dan kena UNIQUE constraint.
    """
    sendiri = c is None
    if sendiri:
        c = _db_kandidat()
    try:
        return c.execute("SELECT COALESCE(MAX(CAST(SUBSTR(r_nomor,3) AS INTEGER)),0)+1"
                         " FROM job").fetchone()[0]
    finally:
        if sendiri:
            c.close()


def _aksi_baris(nama):
    with db.conn() as c:
        return c.execute("SELECT nama,biner,argumen_tetap,pola,argumen_utuh,menulis,batas_detik,pakai_domain "
                         "FROM whitelist WHERE nama=? AND aktif=1", (nama,)).fetchone()


def _target_baris(domain=None, tid=None):
    with db.conn() as c:
        if tid:
            return c.execute("SELECT id,domain,mode FROM targets WHERE id=?", (tid,)).fetchone()
        if domain:
            return c.execute("SELECT id,domain,mode FROM targets WHERE domain=?", (domain,)).fetchone()
    return None


@app.get("/api/konsol/aksi")
def _konsol_aksi():
    with db.conn() as c:
        r = c.execute("SELECT nama,biner,pola,argumen_utuh,menulis,batas_detik,deskripsi,pakai_domain "
                      "FROM whitelist WHERE aktif=1 ORDER BY nama").fetchall()
    kol = ["nama", "biner", "pola", "argumen_utuh", "menulis", "batas_detik", "deskripsi", "pakai_domain"]
    return {"aksi": [dict(zip(kol, x)) for x in r]}


@app.post("/api/konsol/jalankan")
async def _pid_hidup(pid):
    try:
        _os.kill(int(pid), 0)
        return True
    except Exception:
        return False


def _bersihkan_job_mati():
    """Job berstatus jalan yang pid-nya sudah mati ditutup jadi gagal.

    Tanpa ini, satu zombie memblokir semua job berikutnya (batas konkurensi 1).
    """
    c = _db_kandidat()
    waktu = _time.strftime("%Y-%m-%d %H:%M:%S")
    n = 0
    for r in c.execute("select id, pid from job where status='jalan'"):
        if not r["pid"] or not _pid_hidup(r["pid"]):
            c.execute("update job set status='gagal', selesai=? where id=?", (waktu, r["id"]))
            n += 1
    if n:
        c.commit()
    c.close()
    return n


def _konsol_jalankan(muatan: dict):
    nama = (muatan.get("aksi") or "").strip()
    a = _aksi_baris(nama)
    if not a:
        return {"ok": False, "sebab": "aksi tidak ada di whitelist: %s" % nama}
    biner = a[1]
    if not _os.path.isabs(biner) or not _os.path.exists(biner):
        return {"ok": False, "sebab": "biner tidak ada: %s" % biner}
    extra_utuh = (muatan.get("extra") or "").strip()
    if a[4]:
        tambahan = [extra_utuh] if extra_utuh else []
        if tambahan and a[3] and not _re.match(a[3], tambahan[0]):
            return {"ok": False, "sebab": "argumen utuh ditolak pola"}
    else:
        tambahan = extra_utuh.split()
        for tok in tambahan:
            if a[3] and not _re.match(a[3], tok):
                return {"ok": False, "sebab": "argumen ditolak pola: %s" % tok}
    t = _target_baris(muatan.get("domain"), muatan.get("target_id"))
    if (muatan.get("domain") or muatan.get("target_id")) and not t:
        return {"ok": False, "sebab": "target tidak ada"}
    if a[5] and t and t[2] == "pantau" and not muatan.get("paksa"):
        return {"ok": False, "sebab": "target mode=pantau (situs pemerintah) - kirim paksa=1 untuk menulis"}
    with db.conn() as c:
        sedang = c.execute("SELECT COUNT(*) FROM job WHERE status='jalan'").fetchone()[0]
    if sedang:
        return {"ok": False, "sebab": "masih ada job jalan - batas konkurensi 1"}
    argv = [biner] + _json.loads(a[2])
    if a[7] and t:
        argv.append(t[1])
    argv += tambahan
    n = _nomor_r()
    berkas = _DOK_EV / ("R-%d.txt" % n)
    with db.conn() as c:
        c.execute("INSERT INTO job(target_id,aksi,argv,r_nomor,status,stdout_path,mulai) "
                  "VALUES(?,?,?,?, 'jalan', ?, datetime('now'))",
                  (t[0] if t else None, nama, _json.dumps(argv), "R-%d" % n, str(berkas)))
        jid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    tugas = _asyncio.ensure_future(_jalankan(jid, argv, muatan.get("rahasia"), berkas, a[6]))
    _JALAN[jid] = tugas
    return {"ok": True, "job_id": jid, "r_nomor": "R-%d" % n, "argv": argv, "berkas": str(berkas)}


async def _jalankan(jid, argv, rahasia, berkas, batas):
    env = dict(_os.environ)
    env["HESTIA_JOB_ID"] = str(jid)
    if rahasia:
        env["HESTIA_RAHASIA"] = rahasia
    try:
        p = await _asyncio.create_subprocess_exec(
            *argv, cwd=str(_AKAR), env=env,
            stdout=_asyncio.subprocess.PIPE, stderr=_asyncio.subprocess.PIPE)
    except Exception as e:
        with db.conn() as c:
            c.execute("UPDATE job SET status='gagal', selesai=datetime('now') WHERE id=?", (jid,))
        with open(berkas, "a", encoding="utf-8") as f:
            f.write("! gagal start: %r\n" % (e,))
        return
    with db.conn() as c:
        c.execute("UPDATE job SET pid=?, detak=datetime('now') WHERE id=?", (p.pid, jid))
    f = open(berkas, "a", encoding="utf-8")
    kotak = [0]

    async def baca(aliran, stream):
        while True:
            baris = await stream.readline()
            if not baris:
                break
            teks = baris.decode("utf-8", "ignore").rstrip("\n")
            kotak[0] += 1
            with db.conn() as c:
                c.execute("INSERT INTO job_log(job_id,urutan,aliran,baris) VALUES(?,?,?,?)",
                          (jid, kotak[0], aliran, teks))
                c.execute("UPDATE job SET detak=datetime('now') WHERE id=?", (jid,))
            f.write("[%s] %s\n" % (aliran, teks))
            f.flush()

    try:
        await _asyncio.gather(baca("out", p.stdout), baca("err", p.stderr))
        await _asyncio.wait_for(p.wait(), timeout=batas)
        status = "lulus" if p.returncode == 0 else "gagal"
        kode = p.returncode
    except _asyncio.TimeoutError:
        p.kill()
        await p.wait()
        status, kode = "timeout", -1
    except _asyncio.CancelledError:
        p.kill()
        await p.wait()
        status, kode = "batal", -1
    f.write("[sys] selesai status=%s kode=%s\n" % (status, kode))
    f.close()
    with db.conn() as c:
        c.execute("UPDATE job SET status=?, selesai=datetime('now') WHERE id=?", (status, jid))
    _JALAN.pop(jid, None)


@app.get("/api/job/{jid}")
def _job_lihat(jid: int):
    with db.conn() as c:
        r = c.execute("SELECT id,aksi,status,r_nomor,stdout_path,pid,detak,mulai,selesai "
                      "FROM job WHERE id=?", (jid,)).fetchone()
    if not r:
        return {"ok": False}
    kol = ["id", "aksi", "status", "r_nomor", "stdout_path", "pid", "detak", "mulai", "selesai"]
    return {"ok": True, "job": dict(zip(kol, r))}


@app.get("/api/job/{jid}/log")
def _job_log(jid: int, sejak: int = 0):
    with db.conn() as c:
        r = c.execute("SELECT urutan,aliran,baris FROM job_log WHERE job_id=? AND urutan>? "
                      "ORDER BY urutan LIMIT 800", (jid, sejak)).fetchall()
    return {"baris": [{"urutan": x[0], "aliran": x[1], "baris": x[2]} for x in r]}


@app.post("/api/job/{jid}/batal")
def _job_batal(jid: int):
    t = _JALAN.get(jid)
    if not t:
        return {"ok": False, "sebab": "job tidak sedang jalan"}
    t.cancel()
    return {"ok": True}


@app.on_event("startup")
async def _konsol_startup():
    try:
        _job_terputus()
    except Exception:
        pass

# ===== PATCH S-137: runner v2 (denyut, stdin DEVNULL, grup proses) =====
async def _jalankan2(jid, argv, rahasia, berkas, batas):
    env = dict(_os.environ)
    env["HESTIA_JOB_ID"] = str(jid)
    if rahasia:
        env["HESTIA_RAHASIA"] = rahasia
    f = open(berkas, "a", encoding="utf-8")
    kotak = [0]

    def catat(aliran, teks):
        kotak[0] += 1
        with db.conn() as c:
            c.execute("INSERT INTO job_log(job_id,urutan,aliran,baris) VALUES(?,?,?,?)",
                      (jid, kotak[0], aliran, teks))
            c.execute("UPDATE job SET detak=datetime('now') WHERE id=?", (jid,))
        f.write("[%s] %s\n" % (aliran, teks))
        f.flush()

    catat("sys", "mulai: " + " ".join(argv))
    try:
        p = await _asyncio.create_subprocess_exec(
            *argv, cwd=str(_AKAR), env=env,
            stdin=_asyncio.subprocess.DEVNULL,
            stdout=_asyncio.subprocess.PIPE, stderr=_asyncio.subprocess.PIPE,
            start_new_session=True)
    except Exception as e:
        catat("sys", "gagal start: %r" % (e,))
        with db.conn() as c:
            c.execute("UPDATE job SET status='gagal', selesai=datetime('now') WHERE id=?", (jid,))
        f.close()
        return
    with db.conn() as c:
        c.execute("UPDATE job SET pid=?, detak=datetime('now') WHERE id=?", (p.pid, jid))

    async def baca(aliran, stream):
        while True:
            baris = await stream.readline()
            if not baris:
                break
            catat(aliran, baris.decode("utf-8", "ignore").rstrip("\n"))

    async def denyut():
        while p.returncode is None:
            await _asyncio.sleep(5)
            if p.returncode is None:
                catat("sys", "denyut")

    tugas_denyut = _asyncio.ensure_future(denyut())
    status, kode = "gagal", -1
    try:
        await _asyncio.gather(baca("out", p.stdout), baca("err", p.stderr))
        kode = await _asyncio.wait_for(p.wait(), timeout=batas)
        status = "lulus" if kode == 0 else "gagal"
    except _asyncio.TimeoutError:
        try:
            _os.killpg(p.pid, 15)
        except Exception:
            p.kill()
        await p.wait()
        status, kode = "timeout", -1
    except _asyncio.CancelledError:
        try:
            _os.killpg(p.pid, 15)
        except Exception:
            p.kill()
        await p.wait()
        status, kode = "batal", -1
    finally:
        tugas_denyut.cancel()
    catat("sys", "selesai status=%s kode=%s" % (status, kode))
    f.close()
    with db.conn() as c:
        c.execute("UPDATE job SET status=?, selesai=datetime('now') WHERE id=?", (status, jid))
    _JALAN.pop(jid, None)


_jalankan = _jalankan2


@app.get("/konsol.js")
def _konsol_js():
    from fastapi.responses import Response
    p = _Path(__file__).resolve().parent.parent / "dashboard" / "konsol.js"
    isi = p.read_text(encoding="utf-8") if p.exists() else "// kosong"
    return Response(isi, media_type="application/javascript")

# ===== UJI KREDENSIAL (S-143) =====
def _ssh_alias_untuk(host):
    try:
        c = _Path.home() / ".ssh" / "config"
        if not c.exists():
            return ""
        for baris in c.read_text(errors="ignore").splitlines():
            b = baris.strip()
            if b.lower().startswith("hostname ") and b.split(None, 1)[1].strip() == host:
                return b.split(None, 1)[1].strip()
        return ""
    except Exception:
        return ""


def _uji_ftp(target, nama, secret):
    import ftplib
    import ssl
    host = target.split("/")[0]
    pesan = "tidak dicoba"
    for porta in (21, 990):
        try:
            f = ftplib.FTP_TLS(context=ssl._create_unverified_context(), timeout=10)
            f.connect(host, porta)
            try:
                f.login(nama or "anonymous", secret or "")
                pwd = f.pwd()
                f.quit()
                return ("ftp:%d" % porta, "lulus", "login OK pwd=%s" % pwd)
            except Exception as e:
                pesan = str(e)[:140]
                try:
                    f.close()
                except Exception:
                    pass
        except Exception as e:
            pesan = str(e)[:140]
    return ("ftp", "gagal", pesan)


def _uji_sudo(target, nama, secret):
    import subprocess
    host = target.split("/")[0]
    user = nama or "root"
    alias = _ssh_alias_untuk(host)
    sasaran = alias or ("%s@%s" % (user, host))
    opsi = ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=8"]
    if not alias:
        opsi = ["-p", "22"] + opsi
    try:
        r = subprocess.run(["ssh"] + opsi + [sasaran, "sudo -S -p '' true"],
                           input=(secret or "") + "\n", capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return ("ssh-sudo", "lulus", "sudo -S OK lewat %s" % sasaran)
        return ("ssh-sudo", "gagal", (r.stderr or "").strip()[:140] or "kode %s" % r.returncode)
    except Exception as e:
        return ("ssh-sudo", "gagal", repr(e)[:140])


def _uji_netlify(secret):
    import json as _j
    import urllib.request
    try:
        r = urllib.request.Request("https://api.netlify.com/api/v1/sites",
                                   headers={"Authorization": "Bearer " + (secret or "")})
        with urllib.request.urlopen(r, timeout=20) as x:
            d = _j.loads(x.read().decode())
        return ("netlify-api", "lulus", "%d situs" % len(d))
    except Exception as e:
        return ("netlify-api", "gagal", repr(e)[:140])


def _uji_http(target, nama, secret, t):
    import base64
    import urllib.request
    url = target if target.startswith("http") else "https://" + target.split("/")[0] + "/"
    try:
        hdr = {}
        if nama:
            hdr["Authorization"] = "Basic " + base64.b64encode(("%s:%s" % (nama, secret or "")).encode()).decode()
        r = urllib.request.Request(url, headers=hdr)
        with urllib.request.urlopen(r, timeout=20) as x:
            return ("http:%s" % x.status, "lulus" if x.status < 400 else "gagal", "http=%s" % x.status)
    except Exception as e:
        return ("http", "gagal", repr(e)[:140])


def _uji_jalankan(tipe, target, nama, secret, level):
    t = ("%s %s" % (tipe or "", level or "")).lower()
    if "ftp" in t:
        return _uji_ftp(target, nama, secret)
    if "netlify" in t:
        return _uji_netlify(secret)
    if "sudo" in t or "ssh" in t or "vps" in t:
        return _uji_sudo(target, nama, secret)
    return _uji_http(target, nama, secret, t)


@app.post("/api/kredensial/{kid}/uji")
def _kredensial_uji(kid: int):
    with db.conn() as c:
        r = c.execute("SELECT id,target,nama,tipe,level,secret FROM kredensial WHERE id=?", (kid,)).fetchone()
    if not r:
        return {"ok": False, "sebab": "kredensial tidak ada"}
    _id, target, nama, tipe, level, secret = r
    metode, hasil, pesan = _uji_jalankan(tipe, target, nama, secret, level)
    with db.conn() as c:
        c.execute("INSERT INTO kredensial_uji(kredensial_id,metode,hasil,pesan) VALUES(?,?,?,?)",
                  (_id, metode, hasil, pesan[:300]))
    return {"ok": True, "id": _id, "metode": metode, "hasil": hasil, "pesan": pesan[:300]}


@app.get("/api/kredensial-uji")
def _kredensial_uji_daftar():
    with db.conn() as c:
        r = c.execute("SELECT kredensial_id,metode,hasil,pesan,diuji_pada FROM kredensial_uji ORDER BY id DESC LIMIT 100").fetchall()
    return {"item": [{"kredensial_id": x[0], "metode": x[1], "hasil": x[2], "pesan": x[3], "diuji_pada": x[4]} for x in r]}


# ===================== Modul 4: driver redirect 301/410 =====================
import os as _os
import time as _time

_DIR_RULES = _os.path.join("data", "rules")
_os.makedirs(_DIR_RULES, exist_ok=True)


def _driver():
    from tools import driver as drv
    return drv.DRIVER[_os.environ.get("HESTIA_DRIVER", "nginx")]()


def _berkas_rules(domain: str) -> str:
    """Berkas rules dinamai menurut domain penuh. Cadangan: label pertama."""
    p = _os.path.join(_DIR_RULES, domain + ".json")
    if _os.path.exists(p):
        return p
    pendek = _os.path.join(_DIR_RULES, domain.split(".")[0] + ".json")
    return pendek if _os.path.exists(pendek) else p


def _muat_rules(domain: str):
    from tools import driver as drv
    p = _berkas_rules(domain)
    if not _os.path.exists(p):
        return []
    return drv._muat(p)


def _catat(peristiwa: str, rincian: str) -> None:
    try:
        c = _db_kandidat()
        c.execute("INSERT INTO clientlog(waktu, peristiwa, rincian) VALUES(?,?,?)",
                  (_time.strftime("%Y-%m-%d %H:%M:%S"), peristiwa, rincian[:300]))
        c.commit()
        c.close()
    except Exception:
        pass


@app.get("/api/driver/rules")
def api_driver_rules(domain: str):
    rules = _muat_rules(domain)
    return {"domain": domain, "ada": bool(rules),
            "item": [{"path": r.path, "code": r.code, "target": r.target} for r in rules]}


@app.get("/api/driver/plan")
def api_driver_plan(domain: str):
    langkah = _driver().plan(domain, _muat_rules(domain))
    return {"domain": domain,
            "item": [{"op": s.op, "line": s.rule.line()} for s in langkah],
            "ringkas": {k: sum(s.op == k for s in langkah)
                        for k in ("add", "update", "remove", "noop")}}


@app.post("/api/driver/apply")
def api_driver_apply(body: dict):
    domain = (body or {}).get("domain") or ""
    terapkan = bool((body or {}).get("terapkan"))
    if not domain:
        return {"ok": False, "pesan": "domain kosong"}
    h = _driver().apply(domain, _muat_rules(domain), dry_run=not terapkan)
    _catat("driver-terapkan" if terapkan else "driver-rencana",
           "%s changed=%s applied=%s tested=%s reloaded=%s"
           % (domain, h["changed"], h["applied"], h["tested"], h["reloaded"]))
    return {"ok": True,
            "hasil": {k: h[k] for k in ("domain", "changed", "applied", "tested", "reloaded") if k in h},
            "diff": h.get("diff", ""), "pesan": h.get("pesan", "")}


@app.get("/api/driver/verify")
def api_driver_verify(domain: str, base_url: str = ""):
    d = _driver()
    base = base_url or ("https://" + domain)
    hasil = []
    for r in _muat_rules(domain):
        ok, pesan = d.verify(domain, r, base)
        hasil.append({"path": r.path, "code": r.code, "ok": ok,
                      "pesan": pesan, "alasan": pesan})
    return {"domain": domain, "item": hasil,
            "lulus": all(x["ok"] for x in hasil) if hasil else False}


# ===================== Modul 5: Link Rot Monitor =====================
import sys as _sys


@app.post("/api/status/periksa")
def api_status_periksa(body: dict):
    import subprocess
    b = body or {}
    argv = [_sys.executable, "-u", "tools/status_periksa.py",
            "--batas", str(int(b.get("batas") or 3))]
    if b.get("domain"):
        argv += ["--domain", str(b["domain"])]
    if b.get("terapkan"):
        argv += ["--terapkan"]
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return {"ok": False, "kode": 504, "galat": "periksa melewati 600 detik", "hasil": {}}
    try:
        data = json.loads(r.stdout or "{}")
    except Exception:
        data = {"ringkas": {}, "item": [], "keluaran": (r.stdout or "")[-2000:]}
    return {"ok": r.returncode == 0, "kode": r.returncode,
            "galat": (r.stderr or "")[-800:], "hasil": data}


@app.get("/api/status/ringkas")
def api_status_ringkas(batas: int = 300):
    c = _db_kandidat()
    kol = [r[1] for r in c.execute("pragma table_info(status_konten)")]
    baris = [dict(r) for r in c.execute(
        "select s.konten_id, s.status, s.basis, s.bukti_terakhir, s.diperbarui,"
        "       k.url, k.target"
        "  from status_konten s left join konten k on k.id = s.konten_id"
        " order by s.diperbarui desc limit ?", (batas,))]
    metrik = [dict(r) for r in c.execute(
        "select nama, sumber, status_sumber, terisi_terakhir, catatan, nilai, satuan"
        "  from metrik order by nama")]
    c.close()
    hitung = {}
    for b in baris:
        hitung[b.get("status")] = hitung.get(b.get("status"), 0) + 1
    return {"kolom": kol, "total": len(baris), "per_status": hitung,
            "item": baris, "metrik": metrik}