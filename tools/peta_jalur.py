#!/usr/bin/env python3
"""M0 peta jalur: cari sinyal jalur masuk pada target. Read-only."""
import argparse, datetime, socket, sqlite3, urllib.error, urllib.request

DB = "data/hestia.db"
UA = "Hestia/1.0 peta-jalur"
JEJAK = ["/.env", "/.git/HEAD", "/wp-login.php", "/wp-json/", "/xmlrpc.php",
         "/administrator/", "/api/", "/robots.txt"]


def ambil(u, t=12):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=t)
        return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("domain", nargs="+")
    ap.add_argument("--db", default=DB)
    ap.add_argument("--terapkan", action="store_true")
    a = ap.parse_args()
    c = sqlite3.connect(a.db)
    kolj = [r[1] for r in c.execute("pragma table_info(jalur)")]
    for d in a.domain:
        d = d.strip().lower()
        kode = ambil("https://" + d + "/") or ambil("http://" + d + "/")
        temuan = []
        for j in JEJAK:
            k = ambil("https://" + d + j)
            if k in (200, 401, 403):
                temuan.append("%s=%s" % (j, k))
        ftp = ""
        try:
            s = socket.create_connection((d, 21), 6)
            s.settimeout(4)
            ftp = s.recv(100).decode("utf-8", "replace").strip()
            s.close()
            temuan.append("ftp:21")
        except Exception:
            pass
        print("%-24s http=%s ftp=%s" % (d, kode, ftp[:28] or "-"))
        print("   temuan:", ", ".join(temuan) or "-")
        if a.terapkan:
            tid = 0
            row = c.execute("select id from targets where domain like ?", ("%" + d + "%",)).fetchone()
            if row:
                tid = row[0]
            b = {"target_id": tid, "kode_J": "J1", "bukti": "peta: " + ", ".join(temuan)[:280],
                 "terbukti_bisa_tulis": 0,
                 "waktu_uji": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
            b = {k: v for k, v in b.items() if k in kolj}
            c.execute("insert into jalur (%s) values (%s)" % (", ".join(b), ", ".join("?" * len(b))), tuple(b.values()))
    if a.terapkan:
        c.commit()
    print("total jalur:", c.execute("select count(*) from jalur").fetchone()[0])


if __name__ == "__main__":
    main()
