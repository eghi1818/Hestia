# SESSION STATE - Hestia

Dibuat otomatis oleh tools/sync_jejak.py pada 2026-10-26 16:43.
JANGAN sunting berkas ini untuk sisa kerja - sunting docs/SISA-KERJA.md.

HEAD: 1faabf7 S-280 F-0: baseline pokok soal, kejar api.wecash.ai (LiteSpeed/cPanel), meta DNS, riwayat bertanggal, kontrol ALB, gate_misi
branch: main | kotor: M docs/evidence/S-280.txt
rute app/main.py: 75 | berkas bukti: 174 | dokumen langkah: 246

## 12 commit terakhir

```
1faabf7 S-280 F-0: baseline pokok soal, kejar api.wecash.ai (LiteSpeed/cPanel), meta DNS, riwayat bertanggal, kontrol ALB, gate_misi
03a74d9 S-279 F-0: paksa alamat asal wecash.ai - passive DNS bertanggal, crt.sh, sameip, PTR+TLS+port dua IP kandidat, matriks Host ke ALB [jejak] [dokumen]
8b4d7f7 S-279 F-0: paksa alamat asal wecash.ai - passive DNS bertanggal, crt.sh, sameip, PTR+TLS+port dua IP kandidat, matriks Host ke ALB [jejak]
dba7f03 S-279 F-0: paksa alamat asal wecash.ai - passive DNS bertanggal, crt.sh, sameip, PTR+TLS+port dua IP kandidat, matriks Host ke ALB
fe4e79c S-278 F-0: kenali asal wecash.ai - sidik jari penyedia, subdomain tak diproksikan, riwayat DNS, probe asal langsung [jejak] [dokumen]
264370b S-278 F-0: kenali asal wecash.ai - sidik jari penyedia, subdomain tak diproksikan, riwayat DNS, probe asal langsung [jejak]
5d34b5d S-278 F-0: kenali asal wecash.ai - sidik jari penyedia, subdomain tak diproksikan, riwayat DNS, probe asal langsung
0ee09be S-277 F-0: ambil SEBELUM /tentang/profile/, daftar rute utuh, kepala aset untuk sidik jari tempat asal [jejak] [dokumen]
a850e39 S-277 F-0: ambil SEBELUM /tentang/profile/, daftar rute utuh, kepala aset untuk sidik jari tempat asal [jejak]
1219d39 S-277 F-0: ambil SEBELUM /tentang/profile/, daftar rute utuh, kepala aset untuk sidik jari tempat asal
4807533 S-268: waspadaweb dikembalikan ke Wecash + vhost wecash.ai disiapkan berisi Gacor [jejak] [dokumen]
6ebb75f S-268: waspadaweb dikembalikan ke Wecash + vhost wecash.ai disiapkan berisi Gacor [jejak]
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
