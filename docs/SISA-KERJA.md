# SISA KERJA

Disunting manusia. tools/sync_jejak.py menyalinnya ke SESSION_STATE.

## Berurut
1. [selesai S-184] Panel Monitor di dashboard untuk Modul 5.
2. [selesai S-185] Kolom metrik.nilai + satuan (migrasi fase1).
3. [selesai S-188] Unggah berkas FTP/SFTP lewat dashboard (halaman Tanam).
4. [selesai S-190] Papan pindai teknologi di Ikhtisar + tombol pindai dari dashboard.
5. [selesai S-191] LIVE: sandi naik, agen launchd id.hestia.serve, HTTPS self-signed (tools/live.sh, docs/LIVE.md).
6. Pertimbangkan kolom bukti.konten_id (kini konten_id tersimpan di keterangan JSON)
   supaya retensi bisa per-konten dan kueri tidak perlu json_extract.
7. Beri /bin/bash Full Disk Access (GUI) agar agen launchd menggantikan serve.sh; lihat docs/LIVE.md.

## Kendala yang menunggu keputusan
- Tidak ada HestiaCP di mana pun (waspadaweb=nginx, persaudaraan=Netlify,
  juraganit=LiteSpeed cPanel). DoD #3 sudah dipenuhi lewat driver nginx + lxc.
- Aturan izin='manusia' di transisi_status menuju dicabut/tertanam sehingga tidak bisa
  terpicu probe; jalur usul hidup dari pasangan tak dikenal (sudah diuji).
- 3 kunci lapangan hanya bahan uji, bukan penghalang.

## Celah terhadap spesifikasi GOAL
Rincian dan urutan kerja: docs/RENCANA-GOAL.md (dikoreksi S-205; registry + pemeriksa berkala sudah ada).
- Modul 1: kurang field GOAL (biaya, kontrak, platform, kendali editorial), metrik lifespan/equity/biaya per sitasi, heatmap host.
- Modul 2: kurang simhash, kata kunci sebelum/sesudah, delta peringkat, diff viewer.
- Modul 3: kurang simhash, kemiripan <30%, canonical, pemegang SERP.
- Modul 4: kurang mesin skor KEEP/301/410/404, antrean bulk, rollback, equity.
- Modul 5: kurang rot tautan keluar/masuk, equity hangus, pipeline reklamasi, outreach, tren.
- Lintas: halaman ringkasan 5 metrik + drilldown, alert email/webhook, README setup/kredensial/rollback.
- Menunggu keputusan: sumber data SERP dan backlink.

Backlog berurut 16 blok (B-1..B-16) ada di docs/RENCANA-GOAL.md; mulai dari B-1.
