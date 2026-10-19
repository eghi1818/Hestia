"""Hestia API. Satu origin: /api untuk data, / untuk dashboard.
Kompatibel Python 3.8+ (memakai Optional, bukan sintaks pipa)."""
import sqlite3
from pathlib import Path
from typing import List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
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

def _ambil(domain, skema="https"):
    """Satu request saja. Kembalikan dict hasil."""
    import urllib.request, urllib.error, time, re
    url = skema + "://" + domain
    req = urllib.request.Request(url, headers={
        "User-Agent": "Hestia/0.1 (+panel internal)",
        "Accept": "text/html,application/xhtml+xml",
    })
    mulai = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            isi = r.read(60000).decode("utf-8", "ignore")
            return {
                "http_status": r.status,
                "server": r.headers.get("Server", ""),
                "content_type": r.headers.get("Content-Type", ""),
                "redirect": "",
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
    k.close()
    return {"total": tot, "per_suffix_status": per, "per_suffix_jenis": jen}


@app.get("/api/kandidat")
def api_kandidat(suffix: Optional[str] = None, status: Optional[str] = None,
                 jenis: Optional[str] = None, q: Optional[str] = None,
                 limit: int = 100, offset: int = 0,
                 tanpa_infra: bool = False):
    w, a = [], []
    if suffix: w.append("suffix=?"); a.append(suffix)
    if status: w.append("status=?"); a.append(status)
    if jenis: w.append("jenis=?"); a.append(jenis)
    if q: w.append("domain LIKE ?"); a.append("%" + q + "%")
    if tanpa_infra: w.append("infra=0")
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
                         catatan=?,diperiksa_at=? WHERE domain=?""",
                      (h["status"], h["http_status"], h["server"], h["waf"], scrape.skor(h),
                       h.get("catatan"), _dt.now().isoformat(timespec="seconds"), r["domain"]))
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
