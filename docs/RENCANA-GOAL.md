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

## Fakta terkini (S-208)
- registri: 903 baris (dari kandidat; level HOST, belum level HALAMAN).
- tautan: 775 baris berbentuk graf host (kolom dari, ke, dibuat) -- bukan daftar URL.
- kandidat: 903 baris, punya http_status, latensi_ms, diperiksa_at, dicrawl, ukuran, hollow.
- 47 rute /api, 13 skrip dashboard, gate 10 seksi penjaga, 183 dokumen langkah.

## Backlog berurut (tiap blok = satu langkah tutup penuh)
Aturan tiap blok: patch ber-assert, bukti di docs/evidence/S-<n>.txt, gate lulus, commit
lewat tools/tutup.sh. Kriteria terima ditulis di akhir tiap blok.

### Modul 1 -- Registry Parasite SEO (lokal, tanpa API)
- B-1: petakan HALAMAN per host (pakai tools/scrape.py yang sudah ada), isi registri level
  url + jenis penempatan. Terima: registri memuat url halaman, bukan hanya host.
- B-2: metrik registry (lifespan, equity terlantar, biaya per sitasi, hit rate 90 hari),
  tiap metrik berlabel sumber di tabel metrik. Terima: nilai terisi, bukan 'tanpa_sumber'.
- B-3: panel Registry (tabel + filter + ekspor) meniru pola ekspor.js. Terima: rute +
  halaman + ekspor CSV berjalan, gate memeriksa rutenya.
- B-4: heatmap host + alert (pakai /api/putaran dan /api/monitoring). Terima: heatmap
  tampil; alert muncul saat status host jatuh.

### Modul 4 -- Prune Manager (lokal)
- B-5: mesin skor KEEP/301/410/404 dari sinyal (status konten, tautan masuk, duplikat,
  kedalaman) + tabel keputusan. Terima: skor bisa dihitung ulang dan diuji.
- B-6: antrean bulk + eksekusi bertahap lewat driver + audit. Terima: dry-run dulu, lalu
  terapkan sebagian, semua tercatat.
- B-7: rollback + laporan sebelum/sesudah equity. Terima: satu perintah mengembalikan
  keadaan sebelum.

### Modul 5 -- Link Rot Monitor (lokal)
- B-8: rot tautan keluar: ambil tautan dari tabel tautan, probe, tulis baris bukti.
  Terima: tautan mati terdaftar dengan bukti.
- B-9: pipeline reklamasi + template outreach (tabel + panel). Terima: status pipeline
  berubah dan terekam.
- B-10: grafik tren + metrik equity hangus. Terima: grafik tampil dari data nyata.

### Modul 3 -- URL Hijacking Radar (butuh sumber SERP)
- B-11 [LOKAL]: simhash halaman + deteksi kemiripan <30% + cek canonical. Terima: pasangan mirip
  terdeteksi.
- B-12 [BUTUH SERP]: penilaian pemegang SERP + peta sengketa + alert.

### Modul 2 -- Content Replacement Monitor (butuh sumber peringkat)
- B-13 [LOKAL]: snapshot konten + simhash + kata kunci sebelum/sesudah + tanggal perubahan.
- B-14 [BUTUH PERINGKAT]: delta peringkat 7/14/30 hari + tanda tidakcocokan + diff viewer.

### Lintas modul
- B-15: halaman ringkasan 5 metrik + angka bisa diklik (drilldown).
- B-16: alert email/webhook (DoD #6) + README setup/kredensial/rollback (DoD #7).

## Keputusan yang menunggu pemilik proyek
- Sumber posisi SERP: Google Search Console API (gratis, perlu OAuth) atau Brave Search API.
- Sumber backlink: Brave Search API atau layanan berbayar.
Tanpa keputusan ini, B-11..B-14 tetap tertahan; B-1..B-10 dan B-15..B-16 bisa jalan.

Sumber data SERP/backlink: docs/DATA-SUMBER.md (disusun S-210).

## Titik mulai untuk sesi berikutnya
Mulai dari B-1. Bacaan wajib: docs/RENCANA-GOAL.md ini, docs/SISA-KERJA.md, dan
docs/SKILL-AGENT-HESTIA.md. Jangan membangun ulang apa pun di bagian "Yang SUDAH ada".

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
