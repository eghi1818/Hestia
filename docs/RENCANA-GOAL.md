# Rencana menutup 5 modul GOAL

Disusun S-203 setelah pemeriksaan S-202. Rujukan spec: docs/GOAL-Hestia-SEO.md.
Urutan GOAL: modul 5, lalu 4, lalu 1, 2, 3.

## Fakta pemeriksaan S-202
Dari 13 sinyal inti GOAL, sembilan tidak ada sama sekali di app/ tools/ dashboard/:
simhash, canonical, equity, ranking, webhook, lifespan, heatmap, drilldown, outreach.
Yang ada: alert (4 berkas), smtp (3), rollback (3), serp (1) -- dan itu pun belum tentu
terpakai untuk modul terkait.

## Status jujur per modul

### Modul 5 -- Link Rot Monitor
Sudah: pemeriksaan status konten, transisi otomatis, baris bukti, panel Monitor, rute
/api/status/*.
Belum: rot dari tautan keluar (crawl docroot lalu probe), rot dari tautan masuk (butuh
sumber backlink), metrik equity hangus, pipeline reklamasi, template outreach, grafik tren.
Butuh API: tidak untuk sisi keluar.

### Modul 4 -- Prune Manager
Sudah: driver 301/410, dry-run, audit log, terbukti hidup di origin dan publik.
Belum: mesin skor KEEP/301/410/404 dari sinyal, antrean bulk, rollback, sebelum/sesudah
equity.
Butuh API: tidak untuk skor dasar.

### Modul 1 -- Registry Parasite SEO
Sudah: tabel kandidat (903 baris) dan halaman Kandidat.
Belum: field sesuai GOAL (platform, jenis penempatan, tanggal tayang, kata kunci, biaya,
kontrak, pemilik host, kendali editorial), metrik (lifespan, equity terlantar, biaya per
sitasi, hit rate 90 hari), heatmap host, alert.
Butuh API: tidak.

### Modul 2 -- Content Replacement Monitor
Sudah: tabel konten (4 baris) dan halaman Konten.
Belum: snapshot simhash, kata kunci sebelum/sesudah, tanggal perubahan, delta peringkat
7/14/30 hari, tanda ketidakcocokan, diff viewer.
Butuh API: ya, untuk peringkat.

### Modul 3 -- URL Hijacking Radar
Sudah: tabel tautan (775 baris), halaman Tautan dan Recon.
Belum: crawl + simhash, deteksi kemiripan <30%, pemegang SERP, canonical, peta sengketa.
Butuh API: ya, untuk SERP.

## Lintas modul
- Halaman ringkasan 5 metrik, angka bisa diklik untuk drilldown.
- Alert email/webhook (DoD #6).
- README setup, kredensial, rollback (DoD #7).

## Urutan kerja yang diusulkan (lokal dulu)
1. Modul 4 lanjutan: mesin skor + antrean bulk + rollback (pakai data yang ada).
2. Modul 5 lanjutan: rot tautan keluar + pipeline reklamasi + grafik tren.
3. Modul 1 penuh: field + metrik + heatmap host.
4. Keputusan sumber data: SERP dan backlink.
5. Modul 3, lalu Modul 2 (setelah sumber data ada).
6. Lintas modul: halaman ringkasan, alert, README.

## Keputusan yang menunggu pemilik proyek
- Sumber posisi SERP: Google Search Console API (gratis, perlu OAuth) atau Brave Search API.
- Sumber backlink: Brave Search API atau layanan berbayar.
Selama ini belum diputuskan, kolom metrik terkait tetap berstatus 'tanpa_sumber'.

## Kolom tabel yang tersedia sekarang

- kandidat (903 baris): domain, suffix, sumber, status, http_status, server, waf, skor, catatan, diperiksa_at, jenis, infra, dicrawl, ukuran, hollow, petunjuk, latensi_ms
- tautan (775 baris): dari, ke, dibuat
- konten (4 baris): id, url, target, kata_kunci, template, status_indeks, posisi, peran
- recon (56 baris): id, target_id, waktu, http_status, server, content_type, redirect, ms, judul, catatan
- metrik (0 baris): nama, sumber, status_sumber, terisi_terakhir, catatan, nilai, satuan
