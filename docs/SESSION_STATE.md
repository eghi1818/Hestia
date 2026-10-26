# SESSION STATE - Hestia

Dibuat otomatis oleh tools/sync_jejak.py pada 2026-10-26 11:42.
JANGAN sunting berkas ini untuk sisa kerja - sunting docs/SISA-KERJA.md.

HEAD: 9f9b826 S-246 F-17j: baca ingress tunnel cloudflared, siapkan hostname dashboard
branch: main | kotor: D docs/steps/S-246.md
rute app/main.py: 75 | berkas bukti: 141 | dokumen langkah: 211

## 12 commit terakhir

```
9f9b826 S-246 F-17j: baca ingress tunnel cloudflared, siapkan hostname dashboard
effa504 S-245 F-17i: tentukan jalur masuk luar nyata (tunnel Cloudflare vs tepi provider) [jejak]
346ec49 S-245 F-17i: tentukan jalur masuk luar nyata (tunnel Cloudflare vs tepi provider)
aec8107 S-244 F-17h: sidik jari penghadang luar :80, VPS terbukti di belakang NAT [jejak]
3586b9d S-244 F-17h: sidik jari penghadang luar :80, VPS terbukti di belakang NAT
ddbec89 S-243 F-17g: nginx host memakai vhost default Hestia di :80 [jejak]
beb6558 S-243 F-17g: nginx host memakai vhost default Hestia di :80
4eee90d S-242 F-17f: lacak pemilik port 80, terapkan vhost di nginx yang benar [jejak]
43a99aa S-242 F-17f: lacak pemilik port 80, terapkan vhost di nginx yang benar
dfd020b S-241 F-17e: perbaiki akses luar dashboard VPS (vhost aktif) [jejak]
5b571b9 S-241 F-17e: perbaiki akses luar dashboard VPS (vhost aktif)
8fa0981 S-240 F-17d: dashboard dapat diakses dari luar lewat vhost default [jejak]
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
