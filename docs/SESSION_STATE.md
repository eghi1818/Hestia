# SESSION STATE - Hestia

Dibuat otomatis oleh tools/sync_jejak.py pada 2026-10-26 13:52.
JANGAN sunting berkas ini untuk sisa kerja - sunting docs/SISA-KERJA.md.

HEAD: 778dab3 S-261 F-15: pemeriksa link rot (tautan mati) + tempel ke timer pemantauan
branch: main | kotor: M docs/evidence/S-261.txt
rute app/main.py: 75 | berkas bukti: 156 | dokumen langkah: 236

## 12 commit terakhir

```
778dab3 S-261 F-15: pemeriksa link rot (tautan mati) + tempel ke timer pemantauan
e4ba46f S-260 F-19: dokumen langkah bolong dipulihkan, stub tutup.sh tidak dibuang, tunggu-siap diperbaiki [jejak] [dokumen]
71adaef S-260 F-19: dokumen langkah bolong dipulihkan, stub tutup.sh tidak dibuang, tunggu-siap diperbaiki [jejak]
f836fa6 S-260 F-19: dokumen langkah bolong dipulihkan, stub tutup.sh tidak dibuang, tunggu-siap diperbaiki
56d3341 S-259 F-18b: layanan lepas didelegasikan ke live.sh (env benar, rute api kembali 200) [jejak]
7c02627 S-259 F-18b: layanan lepas didelegasikan ke live.sh (env benar, rute api kembali 200)
34f870a S-257 F-14g: pantau menulis change_event saat transisi otomatis + isi 2 aturan transisi yang bolong [jejak]
eaedd8a S-257 F-14g: pantau menulis change_event saat transisi otomatis + isi 2 aturan transisi yang bolong
d421466 S-256 F-14f: bukti perubahan nyata tercatat otomatis (konten uji tertanam -> terverifikasi) [jejak]
3bb72ce S-256 F-14f: bukti perubahan nyata tercatat otomatis (konten uji tertanam -> terverifikasi)
69a071d S-255 F-14e: baca aturan transisi + skema konten, lebarkan sapuan pantau ke --batas 500 [jejak]
141f860 S-255 F-14e: baca aturan transisi + skema konten, lebarkan sapuan pantau ke --batas 500
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
