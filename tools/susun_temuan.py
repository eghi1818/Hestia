#!/usr/bin/env python3
"""Susun docs/audit/temuan.json dengan nomor baris diambil dari grep, bukan diketik."""
import json
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent


def cari(berkas, kandidat):
    p = AKAR / berkas
    try:
        baris = p.read_text(errors="ignore").splitlines()
    except Exception:
        return 1, "(berkas tidak ada)"
    for k in kandidat:
        for i, l in enumerate(baris, 1):
            if k in l:
                return i, l.strip()[:110]
    return 1, "(anchor tidak ketemu)"


def t(kind, berkas, kandidat, scope, ket):
    ln, teks = cari(berkas, kandidat)
    return {"kind": kind, "file": berkas, "line": ln, "scope": scope,
            "description": ket + (" | " + teks if teks else "")}


def e(berkas, kandidat, ket):
    ln, teks = cari(berkas, kandidat)
    return {"file": berkas, "line": ln, "description": ket + (" | " + teks if teks else "")}


TEMUAN = [
    {
        "verdict": "needs_validation",
        "fingerprint": "deploy/juraganit/ftp-anonim-mati",
        "title": "juraganit.com: kanal FTP terkunci karena sesi anonim ditolak server",
        "description": "Pure-FTPd menolak sesi anonim dengan 421 pada tahap USER, baik plain maupun TLS. Sapuan lima pasangan user dan sandi umum semuanya 530. HTTP PUT ditolak LiteSpeed dengan 403. Tanpa kredensial nyata, tidak ada kanal tulis yang terbukti.",
        "claimed_root_cause": "Konfigurasi Pure-FTPd tidak mengizinkan login anonim, dan akun FTP nyata hanya diketahui dari panel hosting liqu.id.",
        "trace": [t("entrypoint", "tools/tanam.py", ["f.login("], "klien FTP", "login ftplib"),
                  t("sink", "docs/evidence/S-120.txt", ["530"], "bukti sapuan", "sandi ditolak")],
        "evidence": [e("docs/evidence/S-113.txt", ["421"], "anonim ditolak di tahap USER"),
                     e("docs/evidence/S-120.txt", ["530"], "sapuan umum gagal"),
                     e("docs/evidence/S-121.txt", ["403"], "PUT ditolak")],
        "blockers": ["satu pasangan user dan sandi FTP dari panel liqu.id",
                     "sapuan lima pasangan umum gagal dengan 530",
                     "HTTP PUT ditolak LiteSpeed dengan 403"],
        "validation_plan": {"deployment": "setelah kredensial ada: tools/tanam.py juraganit.com -u <user> -p <sandi>, lalu cek marker di https://juraganit.com/"},
    },
    {
        "verdict": "needs_validation",
        "fingerprint": "deploy/persaudaraan/netlify-nama-situs-tak-diketahui",
        "title": "persaudaraan.com: isi tidak bisa ditulis karena nama situs Netlify tidak diketahui",
        "description": "A record menunjuk IP load balancer Netlify, DNS dikelola Hostinger. API Netlify membalas 401 dan nama internal netlify.app tidak bocor di HTML, header, maupun DNS. gh dan netlify CLI tidak terpasang di mesin ini.",
        "claimed_root_cause": "Situs di-deploy ke Netlify tanpa jejak nama internal yang terbaca dari luar, sehingga jalur tulis hanya lewat repo Git atau token API.",
        "trace": [t("entrypoint", "tools/hosting.py", ["netlify"], "probe hosting", "cari kebocoran"),
                  t("sink", "docs/evidence/S-123.txt", ["Access Denied"], "bukti API", "API netlify menolak tanpa token")],
        "evidence": [e("docs/evidence/S-123.txt", ["Access Denied"], "API Netlify membalas 401 Access Denied"),
                     e("docs/evidence/S-107.txt", ["netlify api"], "probe awal: netlify api tidak ketemu"),
                     e("docs/evidence/S-123.txt", ["75.2.60.5"], "A record load balancer"),
                     e("docs/evidence/S-135.txt", ["netlify"], "token lokal tidak ada")],
        "blockers": ["token Netlify atau repo Git yang terhubung",
                     "nama situs internal tidak terbaca dari luar"],
        "validation_plan": {"deployment": "GET https://api.netlify.com/api/v1/sites dengan Bearer token untuk dapat nama situs dan hak tulis"},
    },
    {
        "verdict": "needs_validation",
        "fingerprint": "deploy/waspadaweb/docroot-tidak-bisa-ditulis",
        "title": "waspadaweb.com: docroot root:root tanpa jalur tulis bebas sandi",
        "description": "nginx menyajikan /var/www/waspadaweb dengan pemilik root:root. find -writable kosong sampai kedalaman empat, tidak ada skrip writable di /etc /usr/local /opt /srv, tidak ada cron root maupun unit systemd kustom yang menjalankan skrip writable. user wesearch hanya berada di grup wesearch dan users. Situs dilayani lewat Cloudflare Tunnel sehingga tidak ada port 443 di VPS.",
        "claimed_root_cause": "vhost nginx menunjuk docroot milik root, dan user SSH tidak punya jalur tulis maupun eksekusi root tanpa sandi.",
        "trace": [t("entrypoint", "tools/jalur.py", ["writable"], "probe jalur tulis", "find -writable"),
                  t("sink", "docs/evidence/S-144.txt", ["JALUR TANPA SANDI"], "bukti", "kesimpulan probe")],
        "evidence": [e("docs/evidence/S-144.txt", ["JALUR TANPA SANDI"], "tidak ada jalur tulis"),
                     e("docs/evidence/S-145.txt", ["administrator"], "user alternatif menerima kunci"),
                     e("docs/evidence/S-146.txt", ["docroot tidak ketemu"], "bug pencarian vhost")],
        "blockers": ["sandi sudo untuk wesearch atau administrator",
                     "tidak ada jalur tulis tanpa sandi"],
        "validation_plan": {"local": "tools/tanam_ssh.py --cek membaca docroot tanpa sandi",
                            "deployment": "setelah sandi ada: tanam_ssh --tanam, lalu cocokkan sha256 docroot dengan halaman publik"},
    },
]

keluar = AKAR / "docs" / "audit" / "temuan.json"
keluar.parent.mkdir(parents=True, exist_ok=True)
keluar.write_text(json.dumps(TEMUAN, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("+ tulis %s (%d record)" % (keluar.relative_to(AKAR), len(TEMUAN)))
for r in TEMUAN:
    for x in r["trace"] + r["evidence"]:
        tanda = "" if x["line"] > 1 else "  <-- anchor tidak ketemu"
        print("   %-28s baris %-4d %s%s" % (x["file"], x["line"], x["description"][:60], tanda))
