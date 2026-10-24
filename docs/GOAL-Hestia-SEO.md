# GOAL: Hestia SEO Lifecycle & Integrity Dashboard

## Peran kamu
Kamu adalah AI coding agent. Tugasmu membangun satu dashboard internal berbasis HestiaCP
yang memantau siklus hidup halaman web pada 5 domain masalah SEO. Kamu bekerja bertahap:
audit dulu, ajukan rencana, konfirmasi, baru implementasi. Jangan menebak — kalau ada
ambigu, tanya sebelum menulis kode.

## Tujuan utama
Membangun satu sumber kebenaran tunggal yang menjawab pertanyaan:
"Setiap halaman yang kita kelola atau kita publikasikan di domain orang lain — apakah
masih hidup, masih relevan, masih punya equity, dan kalau kita hapus, apa konsekuensinya?"

Dashboard ini menyatukan 5 modul di bawah satu UI dan satu model data.

## Prinsip desain (wajib dipatuhi)
1. Setiap aksi destruktif harus punya jejak audit: siapa, kapan, dari modul mana, alasan.
2. Tidak ada halaman yang boleh berubah status HTTP tanpa keputusan eksplisit dari modul 4.
3. Semua data punya timestamp dan sumber (source of truth). Jangan campur data vendor dengan
   data crawl sendiri tanpa label.
4. Idempoten: menjalankan job dua kali tidak boleh menghasilkan duplikat atau aksi ganda.
5. Read-only dulu, write kemudian. Semua integrasi eksekusi harus bisa dijalankan mode dry-run.

## Integrasi & lingkungan
- HestiaCP REST API: POST ke https://<host>:8083/api/
  Parameter: hash="<access_key>:<secret_key>", returncode="yes", cmd="<command>", arg1..argN
- Command yang relevan (verifikasi urutan argumen dari source di bin/ sebelum dipakai):
  v-list-web-domains, v-list-web-domain, v-list-web-domain-redirect,
  v-add-web-domain-redirect, v-delete-web-domain-redirect, v-add-web-domain-alias
- Log akses server: /var/log/nginx/domains/<domain>.log dan /var/log/apache2/domains/<domain>.log
  (parsing: status code, path, referer, user-agent, cek Googlebot/Bingbot)
- Google Search Console API: index coverage (Not found 404, Soft 404, Crawled not indexed),
  Links report (top linked pages, referring domains)
- Opsional: Ahrefs / Semrush API untuk backlink, atau crawler sendiri (fallback, hindari
  ketergantungan vendor tunggal)
- Penjadwalan: cron harian per modul, plus job mingguan untuk laporan

## 5 MODUL WAJIB

### Modul 1 — Parasite SEO Registry
Tujuan: inventaris dan pemantauan halaman yang kita publikasikan di domain pihak ketiga.
Data yang disimpan: host domain, URL lengkap, platform, jenis penempatan (gratis / bayar /
guest post / subfolder sewaan), tanggal publish, target keyword, biaya, apakah ada kontrak,
pemilik halaman (host), status editorial control.
Sinyal yang dipantau: status HTTP harian (200/301/404/410), posisi keyword, branded search
lift, apakah halaman dikutip di AI Overviews / ChatGPT / Perplexity, umur halaman,
apakah host kena manual action.
Metrik yang ditampilkan: parasite page lifespan (umur rata-rata sebelum mati), total equity
terdampar, cost per citation, hit rate halaman yang masih hidup setelah 90 hari.
Aksi: alert kalau status HTTP berubah jadi 404/410 tanpa pemberitahuan, alert kalau host
mengubah kebijakan, tombol "request 301 ke host", ekspor laporan.
Output visual: tabel registry, timeline lifespan per halaman, heatmap host berdasarkan
tingkat kelangsungan hidup.

### Modul 2 — Content Replacement / Page Repurposing Monitor
Tujuan: setiap kali isi sebuah URL dipertahankan tapi topiknya diganti, catat dan ukur
dampaknya.
Sinyal: snapshot konten (simhash / hash judul+H1+body), keyword utama sebelum vs sesudah,
tanggal perubahan, delta ranking 7/14/30 hari, flag relevance mismatch antara anchor
backlink lama dan konten baru.
Aksi: diff viewer dua kolom, alert kalau ada penurunan ranking >20% dalam 30 hari setelah
perubahan, alert kalau anchor backlink dominan sudah tidak relevan.
Output visual: timeline perubahan per URL, grafik delta ranking, daftar URL berisiko.

### Modul 3 — URL Hijacking / Page Hijacking Radar
Tujuan: mendeteksi URL yang diambil alih pihak lain, dan memantau URL yang kita ambil alih.
Sinyal: crawl halaman target, simhash konten, deteksi perubahan besar (kemiripan <30%),
cek siapa yang ranking untuk URL tersebut, cek tag canonical, cek apakah versi kita kalah
dari salinannya di domain lebih tinggi otoritas.
Aksi: alert takeover, tampilkan diff sebelum/sesudah, tombol aksi (klaim, 301, 410),
log riwayat pengambilalihan.
Output visual: peta URL yang disengketakan, status klaim, siapa pemegang SERP saat ini.

### Modul 4 — 404 / Hard Delete / Content Pruning Manager
Tujuan: satu-satunya pintu untuk menghapus atau mengalihkan halaman.
Sinyal input: traffic organik 0 selama N hari, panjang konten, status duplikat/kannibalisasi,
jumlah referring domain, jumlah backlink, posisi rata-rata.
Skoring keputusan: hitung skor untuk 4 opsi — KEEP, 301, 410, 404.
Aturan keputusan (hard rule):
- Punya >=1 backlink DAN ada halaman pengganti relevan -> wajib 301
- Punya >=1 backlink DAN tidak ada pengganti -> 410 (bukan 404)
- Tidak punya backlink DAN tidak ada pengganti -> 404 boleh
- Traffic masih ada tapi konten tipis -> KEEP, jangan hapus
Guardrail: tidak boleh ada halaman dengan backlink berubah jadi 404 tanpa persetujuan
eksplisit. Default aman selalu 301.
Eksekusi: lewat HestiaCP API, wajib mode dry-run dulu, wajib tulis audit log.
Aksi: bulk queue pruning, preview dampak, rollback, ekspor daftar keputusan.
Output visual: queue dengan skor dan rekomendasi, sebelum/sesudah equity, log eksekusi.

### Modul 5 — Link Rot Monitor
Tujuan: deteksi link mati, hitung equity yang hangus, jalankan pemulihan.
Sinyal: broken backlinks (dari GSC + vendor + crawler sendiri), jumlah referring domain,
teks anchor, URL tujuan, status HTTP, tanggal pertama terdeteksi mati.
Cakupan dua arah:
- Inbound: backlink pihak lain yang menunjuk ke 404/410 kita
- Outbound: link keluar di halaman kita yang sudah mati
Metrik: total equity hangus, jumlah referring domain hilang, recovery rate, waktu rata-rata
dari deteksi ke pemulihan.
Aksi: queue reclamation dengan dua jalur — perbaikan internal (301/410/pulihkan konten)
dan outreach ke pemilik situs (template siap kirim), alert harian untuk kasus baru.
Output visual: leaderboard URL dengan equity hangus terbanyak, grafik tren link rot,
status pipeline reclamation.

## Model data inti (satu skema, dipakai semua modul)
Entitas: Page, Host, ChangeEvent, StatusCheck, Backlink, Decision, ActionLog, MetricSnapshot.
Semua entitas Page terhubung ke minimal satu modul. Setiap perubahan status HTTP wajib
menghasilkan ChangeEvent. Setiap eksekusi wajib menghasilkan ActionLog.
Simpan riwayat penuh, jangan overwrite.

## UI
- Satu halaman ringkasan: total halaman dipantau, jumlah alert aktif, equity terdampar,
  halaman berstatus 404/410, link mati baru minggu ini.
- Lima tab sesuai lima modul, dengan tabel yang bisa difilter dan diurutkan.
- Bahasa UI: Indonesia.
- Semua angka harus bisa diklik untuk turun ke detail sumbernya.

## Definition of Done
1. Kelima modul berjalan dengan data nyata dari minimal satu domain HestiaCP, bukan mock.
2. Semua job terjadwal dan idempoten.
3. Modul 4 bisa mengeksekusi 301 dan 410 lewat HestiaCP API, terverifikasi berubah di server.
4. Setiap aksi punya audit log yang bisa dilihat di UI.
5. Ada mode dry-run untuk semua aksi write.
6. Alert berfungsi (minimal email atau webhook).
7. Ada README: cara setup, kredensial yang dibutuhkan, cara menambah domain, cara rollback.
8. Tidak ada kredensial hardcoded — semua lewat env atau file config terpisah.

## Non-goals (jangan dikerjakan dulu)
- Bukan pengganti Google Analytics.
- Bukan tool riset keyword.
- Bukan panel kontrol HestiaCP pengganti.
- Belum perlu multi-user dengan role granular; satu admin dulu.

## Cara kamu bekerja
1. Audit environment dulu: versi HestiaCP, akses API, akses log, akses GSC. Laporkan temuan.
2. Ajukan rencana implementasi bertahap dengan urutan: modul 5 dan 4 dulu (paling
   berdampak), lalu 1, 2, 3.
3. Konfirmasi rencana dan pilihan stack sebelum menulis kode.
4. Implementasi per modul, satu per satu, dengan cara uji yang jelas.
5. Setelah tiap modul: laporkan apa yang sudah jalan, apa yang belum, apa yang butuh
   keputusan dariku.

## Hal yang harus kamu tanyakan lebih dulu (jangan diasumsikan)
- Berapa domain yang akan dipantau dan apakah semua di HestiaCP?
- Sudah punya akses Google Search Console API?
- Pakai vendor backlink berbayar atau crawler sendiri?
- Stack yang diinginkan (Node/Python/PHP) dan di mana dashboard akan dihosting?
- Kirim alert lewat apa?