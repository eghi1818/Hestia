# SESSION STATE - Hestia

Dibuat otomatis oleh tools/sync_jejak.py pada 2026-10-24 20:37.
JANGAN sunting berkas ini untuk sisa kerja - sunting docs/SISA-KERJA.md.

HEAD: 0b2268b S-191: LIVE sandi naik, agen launchd, HTTPS self-signed, deteksi TCC
branch: main | kotor: ?? docs/steps/S-191.md
rute app/main.py: 73 | berkas bukti: 86 | dokumen langkah: 166

## 12 commit terakhir

```
0b2268b S-191: LIVE sandi naik, agen launchd, HTTPS self-signed, deteksi TCC
1ee20f1 S-190: pindai teknologi dari dashboard, target kosong ditandai [jejak]
5430705 S-190: pindai teknologi dari dashboard, target kosong ditandai
934cd2a S-189: pemilih target Tanam pakai /api/targets, galat server ditampilkan [jejak]
4fe7e9b S-189: pemilih target Tanam pakai /api/targets, galat server ditampilkan
f542d30 S-188: halaman Tanam di dashboard, rute /api/tanam tersambung [jejak]
64b1312 S-188: halaman Tanam di dashboard, rute /api/tanam tersambung
380597f S-187: tutup.sh berakhir dengan pohon bersih (commit jejak otomatis) [jejak]
a7060f3 S-187: tutup.sh berakhir dengan pohon bersih (commit jejak otomatis)
dde51c6 S-186: retensi bukti dan log R, tautan status_konten dilindungi
b491e15 S-185: migrasi fase1 metrik.nilai + satuan, panel menampilkan angka
fd6360a S-184: panel Monitor Modul 5 (tabel status + jalankan pemeriksa dari dashboard)
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
