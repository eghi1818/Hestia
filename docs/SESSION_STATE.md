# SESSION STATE - Hestia

Dibuat otomatis oleh tools/sync_jejak.py pada 2026-10-26 17:31.
JANGAN sunting berkas ini untuk sisa kerja - sunting docs/SISA-KERJA.md.

HEAD: e4015aa S-283 F-0: parser href benar, sumber IP baru, certspotter per-sertifikat, uji cPanel pada wecash.ai, sisir ulang dengan SNI benar
branch: main | kotor: (bersih)
rute app/main.py: 75 | berkas bukti: 177 | dokumen langkah: 249

## 12 commit terakhir

```
e4015aa S-283 F-0: parser href benar, sumber IP baru, certspotter per-sertifikat, uji cPanel pada wecash.ai, sisir ulang dengan SNI benar
d7faa54 S-282 F-0: tanggal mnemonic, CT certspotter, partner+merchant, isi REA, sisir ulang dengan status, tee ke luar repo [jejak] [dokumen]
a7b35cb S-282 F-0: tanggal mnemonic, CT certspotter, partner+merchant, isi REA, sisir ulang dengan status, tee ke luar repo [jejak]
b0d5e48 S-282 F-0: tanggal mnemonic, CT certspotter, partner+merchant, isi REA, sisir ulang dengan status, tee ke luar repo
7fdb735 S-281 F-0: mnemonic bertanggal, sisir nama tak-diproksikan, panel cPanel lewat Cloudflare, Location ALB utuh, jejak REA, sisir 3.64.0.0/16 [jejak] [dokumen]
c884791 S-281 F-0: mnemonic bertanggal, sisir nama tak-diproksikan, panel cPanel lewat Cloudflare, Location ALB utuh, jejak REA, sisir 3.64.0.0/16 [jejak]
e3f9cd5 S-281 F-0: mnemonic bertanggal, sisir nama tak-diproksikan, panel cPanel lewat Cloudflare, Location ALB utuh, jejak REA, sisir 3.64.0.0/16
e0e1c15 S-280 F-0: baseline pokok soal, kejar api.wecash.ai (LiteSpeed/cPanel), meta DNS, riwayat bertanggal, kontrol ALB, gate_misi [jejak] [dokumen]
cf53e96 S-280 F-0: baseline pokok soal, kejar api.wecash.ai (LiteSpeed/cPanel), meta DNS, riwayat bertanggal, kontrol ALB, gate_misi [jejak]
1faabf7 S-280 F-0: baseline pokok soal, kejar api.wecash.ai (LiteSpeed/cPanel), meta DNS, riwayat bertanggal, kontrol ALB, gate_misi
03a74d9 S-279 F-0: paksa alamat asal wecash.ai - passive DNS bertanggal, crt.sh, sameip, PTR+TLS+port dua IP kandidat, matriks Host ke ALB [jejak] [dokumen]
8b4d7f7 S-279 F-0: paksa alamat asal wecash.ai - passive DNS bertanggal, crt.sh, sameip, PTR+TLS+port dua IP kandidat, matriks Host ke ALB [jejak]
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
