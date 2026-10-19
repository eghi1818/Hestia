"""Hestia API. Satu origin: /api untuk data, / untuk dashboard."""
import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
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
    tipe: str | None = None
    status: str | None = None
    owner: str | None = None
    tags: str | None = None
    catatan: str | None = None

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
def daftar_target(status: str | None = None, q: str | None = None):
    sql, arg = "SELECT * FROM targets", []
    if status:
        sql += " AND status = ?" if "WHERE" in sql else " WHERE status = ?"
        arg.append(status)
    if q:
        sql += " AND domain LIKE ?" if "WHERE" in sql else " WHERE domain LIKE ?"
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
    for k, v in u.model_dump(exclude_none=True).items():
        kolom.append(k + " = ?")
        nilai.append(v)
    if not kolom:
        return ambil(tid)
    kolom.append("updated_at = datetime('now')")
    nilai.append(tid)
    with db.conn() as c:
        c.execute("UPDATE targets SET " + ", ".join(kolom) + " WHERE id = ?", nilai)
    return ambil(tid)

@app.delete("/api/targets/{tid}", status_code=204)
def hapus_target(tid: int):
    ambil(tid)
    with db.conn() as c:
        c.execute("DELETE FROM targets WHERE id = ?", (tid,))

@app.get("/")
def beranda():
    return FileResponse(ROOT / "dashboard" / "index.html")
