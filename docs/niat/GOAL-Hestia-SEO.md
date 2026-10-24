# GOAL - Hestia SEO (salinan dari dokumen niat, 2026-10-24)

Hestia adalah Dashboard Siklus Hidup Halaman: satu sumber kebenaran untuk menjawab
"setiap halaman yang kita kelola atau publikasikan di domain orang - masih hidup?
masih punya equity? kalau dihapus, apa konsekuensinya?"

## 5 modul wajib
1. Parasite SEO Registry - daftar aset (URL, domain, tipe, pemilik, tag, status)
2. Content Replacement Monitor - deteksi halaman yang isinya diganti pemilik domain
3. URL Hijacking Radar - deteksi domain yang membajak/menggantikan URL kita
4. 404 / Prune Manager - eksekutor 301/410 dengan keputusan eksplisit
5. Link Rot Monitor - status berkala + metrik equity hangus

## Prinsip
- aksi destruktif wajib punya jejak audit
- tidak ada perubahan status HTTP tanpa keputusan eksplisit modul 4
- data wajib berlabel sumber
- idempoten
- read-only dulu, write dengan dry-run

## Urutan kerja
Modul 5 dan 4 DULU, lalu 1, 2, 3.

## Definition of Done
1. kelima modul berjalan dengan data nyata dari minimal satu domain
2. semua job terjadwal dan idempoten
3. modul 4 bisa mengeksekusi 301 dan 410 lewat minimal satu driver pada minimal satu
   target, terverifikasi berubah di server, dengan dry-run dan audit log
4. audit log terlihat di UI
5. dry-run untuk semua operasi write
6. alert berfungsi
7. README
8. tanpa kredensial hardcoded

## Pertanyaan wajib dijawab dulu
jumlah domain dan apakah semua di HestiaCP - akses GSC API - vendor atau crawler sendiri -
stack dan hosting - kanal alert
