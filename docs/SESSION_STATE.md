# SESSION STATE - Hestia

Dibuat otomatis oleh tools/sync_jejak.py pada 2026-10-24 21:17.
JANGAN sunting berkas ini untuk sisa kerja - sunting docs/SISA-KERJA.md.

HEAD: bd8dd2c S-196: gate memeriksa bukti langkah yang sedang dikerjakan
branch: main | kotor: M docs/steps/S-196.md
rute app/main.py: 73 | berkas bukti: 91 | dokumen langkah: 171

## 12 commit terakhir

```
bd8dd2c S-196: gate memeriksa bukti langkah yang sedang dikerjakan
79da088 S-195: bukti sah gate fail-closed pada berkas bukti langkah [jejak]
9af480f S-195: bukti sah gate fail-closed pada berkas bukti langkah
ea149ea S-194: betulkan judul seksi gate + bukti fail-closed [jejak]
345d616 S-194: betulkan judul seksi gate + bukti fail-closed
64aa6b2 S-193: gate memeriksa bukti langkah terakhir, bukti S-192 dilengkapi [jejak]
3d97976 S-193: gate memeriksa bukti langkah terakhir, bukti S-192 dilengkapi
7f48ad9 S-192: kanal HTTPS terpisah di 8788, cadangan TLS-aware [jejak]
965d9d3 S-192: kanal HTTPS terpisah di 8788, cadangan TLS-aware
e92aa35 S-191: LIVE sandi naik, agen launchd, HTTPS self-signed, deteksi TCC [jejak]
0b2268b S-191: LIVE sandi naik, agen launchd, HTTPS self-signed, deteksi TCC
1ee20f1 S-190: pindai teknologi dari dashboard, target kosong ditandai [jejak]
```

## SISA KERJA

# SISA KERJA

Disunting manusia. tools/sync_jejak.py menyalinnya ke SESSION_STATE.

## Berurut
1. Panel Monitor di dashboard untuk Modul 5 (rute /api/status/* sudah ada, halaman belum).
   Pola: tiru dashboard/driver.js (S-172).
2. metrik belum punya kolom nilai; angka disimpan sebagai prosa di catatan.
   Pertimbangkan migrasi kolom nilai.
3. [selesai S-188] Unggah berkas FTP/SFTP lewat dashboard (halaman Tanam).
4. [selesai S-190] Papan pindai teknologi di Ikhtisar + tombol pindai dari dashboard.
5. [selesai S-191] LIVE: sandi naik, agen launchd id.hestia.serve, HTTPS self-signed (tools/live.sh, docs/LIVE.md).
6. Pertimbangkan kolom bukti.konten_id (kini konten_id tersimpan di keterangan JSON)
   supaya retensi bisa per-konten dan kueri tidak perlu json_extract.

## Kendala yang menunggu keputusan
- Tidak ada HestiaCP di mana pun (waspadaweb=nginx, persaudaraan=Netlify,
  juraganit=LiteSpeed cPanel). DoD #3 sudah dipenuhi lewat driver nginx + lxc.
- Aturan izin='manusia' di transisi_status menuju dicabut/tertanam sehingga tidak bisa
  terpicu probe; jalur usul hidup dari pasangan tak dikenal (sudah diuji).
- 3 kunci lapangan hanya bahan uji, bukan penghalang.
7. Beri /bin/bash Full Disk Access (GUI) agar agen launchd menggantikan serve.sh; lihat docs/LIVE.md.

## Cara melanjutkan

bash tools/step_guard.sh && bash tools/resume.sh
baca docs/NEXT.md, docs/evidence/ terbaru, lalu kerjakan sisa kerja di atas.
