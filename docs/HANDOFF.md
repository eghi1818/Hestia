# SERAH-TERIMA - SEO V1.0
chat ini: SEO V1.0  |  lanjutan bila gagal: SEO V1.1
waktu: 2026-10-19 14:50:56 WIB
repo: /Users/eghi/Documents/REPO/Hestia   cabang: main
commit terakhir: 1313d93 S-13g: bedah rapiddns + sumber ketiga subdomain.center
gate: LULUS   layanan(8787): 200
python: Python 3.9.6   (ingat: 3.9, pakai Optional[str])

## 0. CARA PAKAI
1) Lampirkan ONBOARDING_PROMPT.txt + SESSION_STATE.md di chat baru bernama SEO V1.1.
2) Jalankan: bash tools/resume.sh  lalu tempel keluarannya.
3) Tulis: "Baca SERAH-TERIMA ini sampai habis, lanjut dari bagian 8."

## 1. STATUS
- gate: LULUS | layanan: 200 | commit: 1313d93 S-13g: bedah rapiddns + sumber ketiga subdomain.center
- kandidat: 317
- target  : 10

## 2. SUDAH SELESAI - JANGAN DIULANG
```
# STEPLOG - HESTIA

| Langkah | Tanggal | HEAD | Ringkas | Gate |
|---|---|---|---|---|
| S-01 | 2026-10-18 | - | pasang SOP, tools, gerbang | - |
| S-04 s/d S-09 | 2026-10-19 | - | sambungan dashboard ke API, bukti browser | LULUS |
| S-10 | 2026-10-19 | - | tonggak: 10 target nyata terkelola | LULUS |
```

## 3. PENDING - URUTAN KERJA
```
# PENDING - HESTIA

| ID | Pending | Pemilik | Status |
|---|---|---|---|
| P-01 | Isi About repo (Description, Topics) | user | menunggu |
| P-02 | Putuskan arsitektur: HTML+API atau React | user | menunggu |
| P-03 | Commit prototipe dashboard ke repo | agen | SELESAI |
| P-04 | Kembalikan modul Penyamaran di UI | agen | menunggu |
| P-05 | Seragamkan istilah UI: "kredensial" ke "kunci akses" | agen | menunggu |
| P-06 | Isi docs/CONTEXT.md | agen | menunggu |
| P-07 | Buat GOAL.md | agen | menunggu |
| P-08 | Buat docs/EKSPERIMEN.md | agen | menunggu |
| P-09 | Backend minimal + basis data | agen | SELESAI |
| P-10 | Sambungkan dashboard ke API | agen | SELESAI |
| P-11 | Simpan target dari UI | agen | SELESAI |
| P-12 | Ganti data contoh yang tersisa | agen | menunggu |
| P-13 | Jalankan eksperimen E1 | agen | menunggu |
```

## 4. GAGAL / TERBLOKIR - JANGAN DIULANG TANPA SEBAB BARU
- crt.sh: 502 (sisi mereka); cadangan rapiddns + hackertarget sudah ada
- certspotter: 403 (ac.id bukan eTLD) - wajar
- komdigi.go.id: 403 semua variasi, kemungkinan blokir fingerprint TLS
- bps.go.id: 403 di HTTP/2, 301 di HTTP/1.1 - wajib --http1.1

## 5. ATURAN PANTANG DILANGGAR
- istilah tim: 'Authority Hosting'; dilarang 'parasite' dan 'reframing' di berkas tim
- satu blok maks 250 baris; satu langkah = satu commit + satu berkas bukti
- commit hanya bila gate rc=0, selalu push
- wajib izin pengguna sebelum menyentuh internet
- gate fail-closed: layanan mati = GAGAL

## 6. PETA TEKNIS
- app/main.py FastAPI :8787 | app/db.py SQLite data/hestia.db
- dashboard/index.html + dashboard/live.js (window.addTarget ditimpa)
- tools/gate.sh, tools/scrape.py, tools/serve.sh, tools/smoke.sh, tools/step_guard.sh, tools/resume.sh
- tabel: targets, kandidat, clientlog

## 7. EKOR BUKTI
```
git log -5:
1313d93 S-13g: bedah rapiddns + sumber ketiga subdomain.center
3492c80 S-13f: pulihkan izin eksekusi, backfill jenis, gate cek mode, verify desa.id
2731b32 S-13e: perbaiki conn() + gate kompilasi tools/*.py; sapu sch/mil/desa
8a0a855 S-13d: discover_web gabung sumber + paginasi, kolom jenis, sapu sch/mil/desa
f8e0c27 H-05: folder unggah siap-pakai untuk chat baru di Desktop
status:
 M docs/steps/S-13g.md
 M tools/siapkan_newchat.sh
?? docs/steps/H-06.md
```

## 8. LANGKAH BERIKUT - TEPAT
```
1. Bangun /api/kandidat + tab dashboard.
2. Bersihkan tabel clientlog.
3. Naikkan kandidat terbaik menjadi target.
4. E1 crawl dari benih, kedalaman 1.
5. Ganti sisa data palsu dashboard.
```
