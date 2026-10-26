# SESSION STATE - Hestia

Dibuat otomatis oleh tools/sync_jejak.py pada 2026-10-26 12:46.
JANGAN sunting berkas ini untuk sisa kerja - sunting docs/SISA-KERJA.md.

HEAD: 23a14f0 S-254 F-14d: pahami logika dorong/usul/kontrol + jalankan pemantauan luas --batas 120 --terapkan
branch: main | kotor: M docs/evidence/S-254.txt
 D docs/steps/S-254.md
rute app/main.py: 75 | berkas bukti: 149 | dokumen langkah: 224

## 12 commit terakhir

```
23a14f0 S-254 F-14d: pahami logika dorong/usul/kontrol + jalankan pemantauan luas --batas 120 --terapkan
dbc3313 S-253 F-14c: bukti jalur timer ujung-ke-ujung + kenali opsi --terapkan [jejak]
480e2fd S-253 F-14c: bukti jalur timer ujung-ke-ujung + kenali opsi --terapkan
0120204 S-252 F-14b: pantau.sh menulis nyata (log + --terapkan), izin log dibereskan, bukti hitungan tabel [jejak]
9ac24f2 S-252 F-14b: pantau.sh menulis nyata (log + --terapkan), izin log dibereskan, bukti hitungan tabel
481e096 S-251 F-14: pemantauan berkala di VPS via systemd timer 30 menit + rapikan sisa berkas [jejak]
d3a56da S-251 F-14: pemantauan berkala di VPS via systemd timer 30 menit + rapikan sisa berkas
7ebf2d0 S-250 F-17n: jalur luar https://waspadaweb.com/hestia/ terbukti 401, layanan lokal dihidupkan (membawa S-247..S-249) [jejak]
2fdc11b S-250 F-17n: jalur luar https://waspadaweb.com/hestia/ terbukti 401, layanan lokal dihidupkan (membawa S-247..S-249)
e29ad93 S-246 F-17j: baca ingress tunnel cloudflared, siapkan hostname dashboard [jejak]
9f9b826 S-246 F-17j: baca ingress tunnel cloudflared, siapkan hostname dashboard
effa504 S-245 F-17i: tentukan jalur masuk luar nyata (tunnel Cloudflare vs tepi provider) [jejak]
```

## SISA KERJA

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

## Status terhadap GOAL (M0-M4)
Rencana: docs/RENCANA-GOAL.md. **K1 GANTI dan K2 BUNUH SUDAH TERBUKTI** (waspadaweb, jalur J5).
- M0 MASUK: selesai. M1 AMBIL: selesai. M2 GANTI: selesai. M3 BUNUH: selesai (404 + 410).
- M4 BUKTI: sebagian (ekspor pihak ketiga belum).
- Sisa: Fase 3 (F-10..F-12 perluas), Fase 4 (F-13..F-16), F-17 VPS.
- Target uji: waspadaweb.com.

## Cara melanjutkan

bash tools/step_guard.sh && bash tools/resume.sh
baca docs/NEXT.md, docs/evidence/ terbaru, lalu kerjakan sisa kerja di atas.
