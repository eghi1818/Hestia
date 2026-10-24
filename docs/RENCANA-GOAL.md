# Rencana menutup 5 modul GOAL

Disusun S-203, DIPERBARUI S-205 setelah inventaris S-204. Rujukan spec: docs/GOAL-Hestia-SEO.md.
Urutan GOAL: modul 5, lalu 4, lalu 1, 2, 3.

## Koreksi S-205 (penting)
Daftar celah S-203 melebih-lebihkan kekosongan. Repo ini sudah memuat 47 rute /api, 41
perkakas, dan halaman untuk kandidat, konten, tautan, recon, monitoring, deployment,
kredensial, audit, konsol, ekspor, detail.

## Yang SUDAH ada dan dipakai ulang (jangan dibangun ulang)
- Registry kandidat: tabel kandidat (903 baris), /api/kandidat, /api/kandidat/ringkas,
  /api/kandidat.csv, /api/kandidat/periksa, /api/kandidat/periksa-latar,
  /api/kandidat/periksa-status; kolom http_status, latensi_ms, diperiksa_at, catatan.
- Pemeriksa berkala: /api/putaran, /api/putaran/status (dipakai live.js).
- Monitoring + alert dasar: /api/monitoring (alerts, riwayat, kesehatan), monitorAlerts,
  latencyList, opsMetrics.
- Recon: /api/recon, /api/targets/{tid}/recon, recon.js, tools/scrape.py, net.py, jalur.py.
- Tautan: tabel tautan (775 baris), /api/tautan, /api/tautan/ringkas, tautan.js.
- Konten: /api/konten, /api/konten/{tid}, /api/konten/{tid}/indeks, konten.js.
- Driver: /api/driver/{rules,plan,apply,verify}, tools/driver.py (301/410, dry-run, audit).
- Status konten: /api/status/{periksa,ringkas}, tools/status_periksa.py, monitor.js.
- Ekspor: /api/kandidat.csv, ekspor.js. Konsol/pekerjaan: /api/konsol/*, /api/job/*.
- Tanam: /api/tanam, tools/tanam.py, tools/tanam_ssh.py, tanam.js.

## Celah NYATA per modul
### Modul 1 -- Registry Parasite SEO
Kurang: field GOAL (platform, jenis penempatan, tanggal tayang, kata kunci, biaya, kontrak,
pemilik host, kendali editorial); metrik lifespan, equity terlantar, biaya per sitasi, hit
rate 90 hari; heatmap host.
### Modul 2 -- Content Replacement Monitor
Kurang: snapshot simhash, kata kunci sebelum/sesudah, tanggal perubahan, delta peringkat
7/14/30 hari, tanda ketidakcocokan, diff viewer.
### Modul 3 -- URL Hijacking Radar
Kurang: simhash, deteksi kemiripan <30%, cek canonical, pemegang SERP, peta sengketa.
### Modul 4 -- Prune Manager
Kurang: mesin skor KEEP/301/410/404 dari sinyal, antrean bulk, rollback, sebelum/sesudah
equity.
### Modul 5 -- Link Rot Monitor
Kurang: rot tautan keluar (crawl + probe), rot tautan masuk (butuh sumber backlink),
metrik equity hangus, pipeline reklamasi, template outreach, grafik tren.

## Lintas modul
Halaman ringkasan 5 metrik + angka bisa diklik (drilldown); alert email/webhook (DoD #6);
README setup/kredensial/rollback (DoD #7).

## Urutan kerja
1. Modul 1: field GOAL + metrik + heatmap host (lokal).
2. Modul 4: mesin skor + antrean bulk + rollback (lokal).
3. Modul 5: rot tautan keluar + pipeline reklamasi + grafik tren (lokal).
4. Keputusan sumber data SERP dan backlink.
5. Modul 3, lalu Modul 2 (setelah sumber data ada).
6. Lintas modul.

## Keputusan yang menunggu pemilik proyek
- Sumber posisi SERP: Google Search Console API (gratis, perlu OAuth) atau Brave Search API.
- Sumber backlink: Brave Search API atau layanan berbayar.
Selama belum diputuskan, kolom metrik terkait tetap berstatus 'tanpa_sumber'.

## Inventaris yang sudah ada (diperiksa S-204)

Rute /api di app/main.py: 47

- /api/anggota
- /api/anggota/{tid}
- /api/audit
- /api/audit/peristiwa
- /api/clientlog
- /api/clientlog/bersih
- /api/deployment
- /api/deployment/{tid}
- /api/driver/apply
- /api/driver/plan
- /api/driver/rules
- /api/driver/verify
- /api/health
- /api/job/{jid}
- /api/job/{jid}/batal
- /api/job/{jid}/log
- /api/kandidat
- /api/kandidat.csv
- /api/kandidat/periksa
- /api/kandidat/periksa-latar
- /api/kandidat/periksa-status
- /api/kandidat/ringkas
- /api/konsol/aksi
- /api/konsol/jalankan
- /api/konten
- /api/konten/{tid}
- /api/konten/{tid}/indeks
- /api/kredensial
- /api/kredensial-uji
- /api/kredensial/rotasi
- /api/kredensial/{kid}/uji
- /api/kredensial/{tid}
- /api/monitoring
- /api/putaran
- /api/putaran/status
- /api/recon
- /api/setelan
- /api/status/periksa
- /api/status/ringkas
- /api/tanam
- /api/targets
- /api/targets/{tid}
- /api/targets/{tid}/recon
- /api/tautan
- /api/tautan/ringkas
- /api/teknologi-ringkas
- /api/teknologi/pindai

Panggilan /api dari skrip dashboard:

- aksi.js: /api/anggota, /api/clientlog, /api/clientlog/bersih, /api/deployment, /api/deployment/, /api/konten, /api/kredensial/rotasi, /api/monitoring, /api/setelan, /api/tanam, /api/tautan
- audit.js: /api/audit, /api/audit/peristiwa, /api/clientlog, /api/monitoring
- detail.js: /api/clientlog, /api/konten, /api/kredensial, /api/targets, /api/targets/
- driver.js: /api/driver/apply, /api/driver/plan, /api/driver/verify, /api/targets
- ekspor.js: /api/clientlog, /api/kandidat.csv
- ikhtisar.js: /api/clientlog, /api/kandidat/ringkas, /api/targets, /api/teknologi-ringkas, /api/teknologi/pindai
- konsol.js: /api/clientlog, /api/job/, /api/konsol/aksi, /api/konsol/jalankan, /api/kredensial, /api/kredensial-uji, /api/kredensial/
- konten.js: /api/clientlog, /api/deployment, /api/konten, /api/konten/, /api/kredensial, /api/targets
- live.js: /api/clientlog, /api/kandidat, /api/kandidat/periksa, /api/kandidat/periksa-latar, /api/kandidat/periksa-status, /api/putaran, /api/putaran/status, /api/targets
- monitor.js: /api/status/periksa, /api/status/ringkas, /api/targets
- recon.js: /api/clientlog, /api/recon, /api/targets, /api/targets/
- tanam.js: /api/tanam, /api/targets
- tautan.js: /api/clientlog, /api/tautan/ringkas
