# SISA KERJA

Disunting manusia. tools/sync_jejak.py menyalinnya ke SESSION_STATE.

## Berurut
1. Panel Monitor di dashboard untuk Modul 5 (rute /api/status/* sudah ada, halaman belum).
   Pola: tiru dashboard/driver.js (S-172).
2. metrik belum punya kolom nilai; angka disimpan sebagai prosa di catatan.
   Pertimbangkan migrasi kolom nilai.
3. Retensi bukti: bukti tumbuh ~jumlah diperiksa tiap run.
4. Unggah berkas FTP/SFTP lewat dashboard (masih lewat tools/tanam.py).
5. Papan status pindai teknologi di Ikhtisar (16 target mati/parkir kosong).
6. LIVE: HESTIA_SANDI dinaikkan, serve.sh jadi layanan, host 24/7 + HTTPS.

## Kendala yang menunggu keputusan
- Tidak ada HestiaCP di mana pun (waspadaweb=nginx, persaudaraan=Netlify,
  juraganit=LiteSpeed cPanel). DoD #3 sudah dipenuhi lewat driver nginx + lxc.
- Aturan izin='manusia' di transisi_status menuju dicabut/tertanam sehingga tidak bisa
  terpicu probe; jalur usul hidup dari pasangan tak dikenal (sudah diuji).
- 3 kunci lapangan hanya bahan uji, bukan penghalang.
