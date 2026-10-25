# Sumber data: posisi SERP dan backlink

Disusun S-210. Menjawab satu-satunya keputusan yang menahan Modul 2 dan 3.

## Fakta yang menentukan
1. Backlink TIDAK wajib beli data. tools/scrape.py sudah ada dan tabel tautan sudah memuat
   775 relasi host (kolom dari, ke). Memperluas crawl menghasilkan graf backlink sendiri,
   gratis. Jadi Modul 5 dan bagian Modul 3 tidak terhalang.
2. Posisi SERP memang butuh API. Google Search Console HANYA memberi data untuk properti
   yang sudah diverifikasi pemiliknya, sehingga host pihak ketiga tidak tercakup.

## Pilihan
### A. Brave Search API (disarankan)
- Yang dibutuhkan: akun di api-dashboard.search.brave.com, satu API key, paket layanan.
- Ada paket gratis sekitar 2.000 kueri/bulan (1 kueri/detik) -- cukup untuk uji.
- Dipakai untuk: posisi sebuah URL pada kata kunci, dan penemuan halaman/host.
- Batasan: bukan data backlink sungguhan; itu tetap dari crawl sendiri.

### B. Google Search Console API
- Yang dibutuhkan: project Google Cloud, Search Console API diaktifkan, service account +
  file JSON, lalu email service account ditambahkan sebagai pengguna di tiap properti.
- Gratis, kuota harian besar.
- Batasan: hanya properti milik sendiri dan terverifikasi. waspadaweb.com (target latihan)
  kemungkinan kosong kecuali diverifikasi.

## Cara menyimpan kunci (repo ini publik)
- Brave: tambahkan baris BRAVE_API_KEY=... ke ~/.hestia/live.env (mode 600). Tidak masuk git.
- Google: simpan file JSON di ~/.hestia/gsc.json (mode 600), catat path-nya di live.env
  sebagai GSC_JSON=...
- tools/live.sh sudah menyimpan live.env; jangan pernah menaruh kunci di berkas repo.

## Yang diminta dari pemilik proyek
1. Keputusan: pakai API pencarian atau tidak.
2. Bila ya: API key Brave, atau file JSON + daftar properti untuk Google.
3. Daftar 3-10 host dan 5-20 kata kunci untuk uji awal.
4. Konfirmasi penyimpanan kunci di ~/.hestia/live.env.

## Dampak ke backlog
- B-11 (simhash + kemiripan <30% + canonical): LOKAL, tidak menunggu.
- B-12 (pemegang SERP + peta sengketa): butuh sumber SERP.
- B-13 (snapshot konten + kata kunci sebelum/sesudah): LOKAL.
- B-14 (delta peringkat 7/14/30 hari): butuh sumber peringkat.
- B-1..B-10 dan B-15..B-16: LOKAL, tidak menunggu.
