# SESSION STATE - Hestia

Ditulis: 2026-10-24. Chat: SEO V1.1.
HEAD saat dokumen ini ditulis: ba636d3 S-181: HESTIA_JOB_ID diekspor di _jalankan2 (bukan _jalankan)

## Keadaan
- branch main, tree bersih, gate LULUS, GATE-AUDIT LULUS, smoke 3/0
- 46 rute, 70 rujukan id dashboard tervalidasi, placeholder ok
- layanan :8787 hidup di balik Basic auth

## Yang sudah SELESAI dan tidak perlu diulang
- Fondasi: auth, gate fail-closed, audit, WAL, migrasi fase0, retensi cadangan,
  pemeriksa placeholder, sinkron state
- Modul 4 (driver 301/410): tools/driver.py + data/rules + rute /api/driver/*
  + halaman Driver di dashboard + ActionLog ke clientlog
  Bukti: docs/evidence/S-167.txt, S-169.txt, S-172.txt
- Modul 5 (Link Rot Monitor): tools/status_periksa.py + rute /api/status/*
  + transisi otomatis vs usul + bukti teratribusi ke job
  Bukti: docs/evidence/S-173.txt .. S-181.txt
  Empat cabang teruji: tetap, tak-pasti, transisi(otomatis), usul(izin None)
- Runner job: r_nomor kebal bentrok, penyapu zombie, HESTIA_JOB_ID diekspor
  Bukti: docs/evidence/S-179.txt, S-180.txt, S-181.txt

## SISA KERJA (berurut)
1. Panel Monitor di dashboard untuk Modul 5 (rute /api/status/* sudah ada,
   halaman belum). Pola: tiru dashboard/driver.js (S-172).
2. metrik belum punya kolom nilai; angka disimpan sebagai prosa di catatan.
   Pertimbangkan migrasi kolom nilai (P2).
3. Retensi bukti: bukti tumbuh ~jumlah diperiksa tiap run.
4. unggah berkas FTP/SFTP lewat dashboard (masih lewat tools/tanam.py)
5. papan status pindai teknologi di Ikhtisar (16 target mati/parkir kosong)
6. LIVE: HESTIA_SANDI dinaikkan, serve.sh jadi layanan, host 24/7 + HTTPS

## Kendala / keputusan menunggu
- tidak ada HestiaCP di mana pun (waspadaweb=nginx, persaudaraan=Netlify,
  juraganit=LiteSpeed cPanel). DoD #3 sudah dipenuhi lewat driver nginx + lxc.
- aturan izin='manusia' di transisi_status menuju dicabut/tertanam sehingga tidak
  bisa terpicu probe; usul hidup dari pasangan tak dikenal. Sudah diuji.
- 3 kunci lapangan (FTP juraganit, sudo waspadaweb, nama netlify persaudaraan)
  hanya bahan uji - bukan penghalang.

## Nomor langkah tanpa commit (wajar)
S-158, S-164, S-166, dan docs/steps/S-119, S-124, S-127.

## Cara melanjutkan
bash tools/step_guard.sh && bash tools/resume.sh
baca docs/NEXT.md, docs/evidence/S-17*.txt, docs/evidence/S-18*.txt
jalankan bash tools/tutup.sh di akhir tiap langkah.
