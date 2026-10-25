# SESSION STATE - Hestia

Dibuat otomatis oleh tools/sync_jejak.py pada 2026-10-25 11:43.
JANGAN sunting berkas ini untuk sisa kerja - sunting docs/SISA-KERJA.md.

HEAD: 45e509c S-218 F-2c: tutup kebocoran stub dokumen langkah
branch: main | kotor: D docs/steps/S-218.md
rute app/main.py: 75 | berkas bukti: 113 | dokumen langkah: 192

## 12 commit terakhir

```
45e509c S-218 F-2c: tutup kebocoran stub dokumen langkah
191a521 S-217 F-2b: perbaiki konvensi penomoran langkah, rapikan dokumen S-215/S-216 [jejak]
0e590a9 S-217 F-2b: perbaiki konvensi penomoran langkah, rapikan dokumen S-215/S-216
11b00c1 F-2: pengurai berkas REA (deteksi format dari isi, simpan asli + sha256) [jejak]
50f6ae6 F-2: pengurai berkas REA (deteksi format dari isi, simpan asli + sha256)
97eb838 F-1: migrasi skema jalur dan tabel pendukung M0-M4 [jejak]
4a44587 F-1: migrasi skema jalur dan tabel pendukung M0-M4
d7176cd S-214: tuntaskan S-211 (VPS.md), selaraskan dokumen ke F-blok [jejak]
cf42fb7 S-214: tuntaskan S-211 (VPS.md), selaraskan dokumen ke F-blok
7fcca2a S-213: GOAL baru dijadikan landasan di onboarding, SOP, README, dan gate [jejak]
ad1f56a S-213: GOAL baru dijadikan landasan di onboarding, SOP, README, dan gate
31b6e46 S-212: GOAL baru, rencana dipetakan ulang ke M0-M4 Fase 0-4 [jejak]
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
Rencana lengkap: docs/RENCANA-GOAL.md. GOAL BELUM TERCAPAI.
- M0 MASUK: belum (skema jalur + uji tulis).
- M1 AMBIL: belum.
- M2 GANTI: belum pernah -- inti tujuan.
- M3 BUNUH: sebagian (301/410 hidup di waspadaweb, tanpa penanda/snapshot/rollback).
- M4 BUKTI: sebagian.
- Ditunda ke Fase 4: registry parasite, link rot, panel teknologi.
- Target uji: waspadaweb.com lebih dulu.

## Cara melanjutkan

bash tools/step_guard.sh && bash tools/resume.sh
baca docs/NEXT.md, docs/evidence/ terbaru, lalu kerjakan sisa kerja di atas.
