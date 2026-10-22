"""Hestia API. Satu origin: /api untuk data, / untuk dashboard.
Kompatibel Python 3.8+ (memakai Optional, bukan sintaks pipa)."""
import sqlite3
from pathlib import Path
from typing import List, Optional

from fastapi import Body, BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import db

ROOT = Path(__file__).resolve().parent.parent
STATUS_SAH = {"kandidat", "dianalisis", "aktif", "rusak", "dibersihkan", "nonaktif"}

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
    hasil = _ambil(t["domain"], skema)
    with db.conn() as c:
        cur = c.execute(
            "INSERT INTO recon (target_id,http_status,server,content_type,redirect,ms,judul,catatan)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (tid, hasil["http_status"], hasil["server"], hasil["content_type"],
             hasil["redirect"], hasil["ms"], hasil["judul"], hasil["catatan"]))
        rid = cur.lastrowid
    with db.conn() as c:
        r = c.execute("SELECT * FROM recon WHERE id = ?", (rid,)).fetchone()
    _st = ("hidup" if 200 <= h["http_status"] < 400 else
           "dijaga" if h["http_status"] in (401, 403, 406, 418, 429, 503) else
           "mati" if h["http_status"] == 0 else "galat")
    c.execute("UPDATE targets SET status=? WHERE id=?", (_st, tid))
    c.commit()
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
                  (h["status"], h["http_status"], h["server"], h["waf"], scrape.skor(h),
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
                      (h["status"], h["http_status"], h["server"], h["waf"], scrape.skor(h),
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
                      (h["status"], h["http_status"], h["server"], h["waf"], scrape.skor(h),
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
def api_audit(batas: int = 60):
    c = _db_kandidat()
    tot = c.execute("SELECT count(*) FROM clientlog").fetchone()[0]
    rows = [dict(r) for r in c.execute(
        "SELECT id, waktu, peristiwa, rincian FROM clientlog ORDER BY id DESC LIMIT ?", (batas,))]
    c.close()
    return {"total": tot, "item": rows}


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


# ---------- kredensial / deployment / konten ----------
_TABEL = {
    "kredensial": ("target TEXT, nama TEXT, tipe TEXT, level TEXT, secret TEXT, "
                   "berlaku_sd TEXT, created_at TEXT",
                   ["target", "nama", "tipe", "level", "secret", "berlaku_sd", "created_at"]),
    "deployment": ("waktu TEXT, target TEXT, path TEXT, template TEXT, status TEXT",
                   ["waktu", "target", "path", "template", "status"]),
    "konten": ("url TEXT, target TEXT, kata_kunci TEXT, template TEXT, "
               "status_indeks TEXT, posisi REAL",
               ["url", "target", "kata_kunci", "template", "status_indeks", "posisi"]),
}


def _siap_tabel():
    c = _db_kandidat()
    for n, (kol, _x) in _TABEL.items():
        c.execute("CREATE TABLE IF NOT EXISTS %s(id INTEGER PRIMARY KEY AUTOINCREMENT, %s)"
                  % (n, kol))
    c.commit()
    return c


def _daftar(nama, target=None):
    c = _siap_tabel()
    if target:
        rows = [dict(r) for r in c.execute(
            "SELECT * FROM " + nama + " WHERE target=? ORDER BY id DESC LIMIT 200", (target,))]
    else:
        rows = [dict(r) for r in c.execute(
            "SELECT * FROM " + nama + " ORDER BY id DESC LIMIT 200")]
    c.close()
    return {"total": len(rows), "item": rows}


def _tambah(nama, body):
    kol = _TABEL[nama][1]
    nilai = [body.get(k) for k in kol]
    c = _siap_tabel()
    c.execute("INSERT INTO %s(%s) VALUES(%s)"
              % (nama, ",".join(kol), ",".join("?" * len(kol))), nilai)
    c.commit()
    c.close()
    return {"ok": True, "tabel": nama}


@app.get("/api/kredensial")
def api_kredensial(target: Optional[str] = None):
    return _daftar("kredensial", target)


@app.get("/api/deployment")
def api_deployment(target: Optional[str] = None):
    return _daftar("deployment", target)


@app.get("/api/konten")
def api_konten(target: Optional[str] = None):
    return _daftar("konten", target)


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
