# SESSION STATE - Hestia

Dibuat otomatis oleh tools/sync_jejak.py pada 2026-10-25 20:05.
JANGAN sunting berkas ini untuk sisa kerja - sunting docs/SISA-KERJA.md.

HEAD: 4f92a12 S-224 F-5/F-6: BUNUH 410 + idempoten dan rollback teruji
branch: main | kotor: D docs/steps/S-224.md
rute app/main.py: 75 | berkas bukti: 119 | dokumen langkah: 192

## 12 commit terakhir

```
4f92a12 S-224 F-5/F-6: BUNUH 410 + idempoten dan rollback teruji
576bd89 S-223 F-4b: reload nginx lewat host, BUNUH 404 terbukti [jejak]
4b2f840 S-223 F-4b: reload nginx lewat host, BUNUH 404 terbukti
ed36908 S-222 F-4: BUNUH 404 halaman uji lewat jalur J5, snapshot + rollback [jejak]
480b775 S-222 F-4: BUNUH 404 halaman uji lewat jalur J5, snapshot + rollback
3473304 S-221 F-3c: perbaiki pembaca publik (UA), jalur J5 terbukti menulis [jejak]
d5ee9f2 S-221 F-3c: perbaiki pembaca publik (UA), jalur J5 terbukti menulis
4003715 S-220 F-3b: diagnosa 403 baca publik, chmod 644 penanda [jejak]
37e9c07 S-220 F-3b: diagnosa 403 baca publik, chmod 644 penanda
b8bd036 S-219 F-3: uji tulis jalur waspadaweb J5 dengan penanda [jejak]
7410e97 S-219 F-3: uji tulis jalur waspadaweb J5 dengan penanda
8acc50f S-218 F-2c: tutup kebocoran stub dokumen langkah [jejak]
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
