# SERAH-TERIMA - SEO V1.0
chat ini: SEO V1.0  |  lanjutan bila gagal: SEO V1.1
waktu: 2026-10-19 15:30:58 WIB
repo: /Users/eghi/Documents/REPO/Hestia   cabang: main
commit terakhir: 68b0d51 H-08: STEPLOG dihasilkan dari git log, PENDING dirapikan, panduan disamakan
gate: LULUS   layanan(8787): 200
python: Python 3.9.6   (ingat: 3.9, pakai Optional[str])

## 0. CARA PAKAI
1) Buat chat baru bernama SEO V1.1. Unggah SELURUH isi ~/Desktop/HESTIA-RESUME.
2) Pesan pertama: tempel isi 1-ONBOARDING-PROMPT.txt apa adanya.
3) Tulis: "Baca SERAH-TERIMA ini sampai habis, lanjut dari bagian 8."

## 1. STATUS
- gate: LULUS | layanan: 200 | commit: 68b0d51 H-08: STEPLOG dihasilkan dari git log, PENDING dirapikan, panduan disamakan
- kandidat: 317
- target  : 10

## 2. SUDAH SELESAI - JANGAN DIULANG
```
# STEPLOG - HESTIA

| Langkah | Tanggal | HEAD | Ringkas | Gate |
|---|---|---|---|---|
| S-12 | 2026-10-19 | cb3a6e7 | PATCH domain field + guard 409; probe lapisan penjaga WAF | LULUS |
| H-02/H-03 | 2026-10-19 | d5c650c | berkas ketahanan sesi + generator serah-terima yang benar | LULUS |
| H-04 | 2026-10-19 | c21014c | perbaiki hitung basis pada generator serah-terima | LULUS |
| H-05 | 2026-10-19 | f8e0c27 | folder unggah siap-pakai untuk chat baru di Desktop | LULUS |
| S-13d | 2026-10-19 | 8a0a855 | discover_web gabung sumber + paginasi, kolom jenis, sapu sch/mil/desa | LULUS |
| S-13e | 2026-10-19 | 2731b32 | perbaiki conn() + gate kompilasi tools/*.py; sapu sch/mil/desa | LULUS |
| S-13f | 2026-10-19 | 3492c80 | pulihkan izin eksekusi, backfill jenis, gate cek mode, verify desa.id | LULUS |
| S-13g | 2026-10-19 | 1313d93 | bedah rapiddns + sumber ketiga subdomain.center | LULUS |
| H-06 | 2026-10-19 | 78e6567 | rapikan panduan folder unggah + segarkan | LULUS |
| H-07 | 2026-10-19 | 79dcd50 | rapikan panduan folder + urutan segarkan | LULUS |
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
| P-06 | Isi docs/CONTEXT.md | agen | SELESAI |
| P-07 | Buat GOAL.md | agen | SELESAI |
| P-08 | Buat docs/EKSPERIMEN.md | agen | SELESAI |
| P-09 | Backend minimal + basis data | agen | SELESAI |
| P-10 | Sambungkan dashboard ke API | agen | SELESAI |
| P-11 | Simpan target dari UI | agen | SELESAI |
| P-12 | Ganti data contoh yang tersisa | agen | menunggu |
| P-13 | Jalankan eksperimen E1 | agen | menunggu |
| P-14 | Bangun /api/kandidat + tab dashboard | agen | menunggu |
| P-15 | Bersihkan tabel clientlog berkala | agen | menunggu |
| P-16 | Naikkan kandidat terbaik menjadi target | agen | menunggu |
| P-17 | Jalankan eksperimen E1 (crawl dari benih) | agen | menunggu |
| P-18 | Sumber discovery keempat (crt.sh pulih / crawl benih) | agen | menunggu |
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
68b0d51 H-08: STEPLOG dihasilkan dari git log, PENDING dirapikan, panduan disamakan
79dcd50 H-07: rapikan panduan folder + urutan segarkan
78e6567 H-06: rapikan panduan folder unggah + segarkan
1313d93 S-13g: bedah rapiddns + sumber ketiga subdomain.center
3492c80 S-13f: pulihkan izin eksekusi, backfill jenis, gate cek mode, verify desa.id
status:
 M docs/steps/H-08.md
```

## 8. LANGKAH BERIKUT - TEPAT
```
1. Bangun /api/kandidat + tab dashboard.
2. Bersihkan tabel clientlog.
3. Naikkan kandidat terbaik menjadi target.
4. E1 crawl dari benih, kedalaman 1.
5. Ganti sisa data palsu dashboard.
```
