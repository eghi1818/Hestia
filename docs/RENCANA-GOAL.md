# Rencana Hestia -- dipetakan ke GOAL (M0-M4, Fase 0-4)

Ditulis ulang S-212 setelah GOAL, PROLOG, dan SKILL diperbarui. Dokumen yang mengikat:
docs/PROLOG-HESTIA-DASHBOARD.md (menang bila bertentangan), docs/GOAL-Hestia-SEO.md,
docs/SKILL-AGENT-HESTIA.md.

Catatan nama: berkas GOAL masih bernama "-SEO" padahal GOAL-nya sudah bukan soal SEO.
Nama dipertahankan supaya tidak memutus rujukan.

## Yang mengikat (dari GOAL)
- Hanya dua kemampuan: K1 GANTI, K2 BUNUH. Fitur lain yang tidak melayani keduanya: TUNDA.
- Tanpa jalur masuk di atas J1, kita hanya bisa membaca.
- Peta jalur dulu, baru bertindak. Validasi jalur tidak boleh dilewatkan.
- Bukti = penanda. Tanpa penanda, belum selesai.
- DILARANG membangun monitoring dulu.
- Jangan janji 410/403 kalau jalurnya belum ada (SQLi hanya 404 dan blank).
- Pindah VPS hanya setelah terbukti lokal.

## Status terhadap GOAL (jujur)
| Modul | Status |
|---|---|
| M0 MASUK | BELUM. Tabel jalur belum ada; uji tulis belum formal. |
| M1 AMBIL | BELUM. |
| M2 GANTI | BELUM PERNAH. Inti tujuan, belum sekali pun. |
| M3 BUNUH | SEBAGIAN. 301/410 hidup di waspadaweb lewat nginx (S-175..S-180), tanpa penanda, snapshot, rollback, 2 vantage. 404 belum diuji. |
| M4 BUKTI | SEBAGIAN. Tabel bukti ada, belum berpenanda, belum ada ekspor pihak ketiga. |

Kesimpulan: GOAL BELUM TERCAPAI. Ditunda ke Fase 4: registry parasite, link rot, panel teknologi.

## Urutan blok
### Fase 0 -- M0 MASUK (prasyarat)
- F-1: migrasi skema: jalur (kode_J, bukti, terbukti_bisa_tulis, waktu_uji), berkas_rea
  (provenance + sha256), blok (asli + normalisasi), page, change_event, status_check.
  Terima: tabel ada, idempoten.
- F-2: urai berkas REA (JSON/CSV/MD, deteksi dari isi, blok tetap, alias, simpan asli).
  Terima: terurai tanpa menebak; field wajib hilang ditandai.
- F-3: uji tulis jalur: tulis penanda -> baca ulang -> hapus, catat ke tabel jalur.
  Terima: minimal satu jalur (waspadaweb J5) tercatat terbukti_bisa_tulis + bukti.

### Fase 1 -- M3 BUNUH (batas 2 blok; kalau lewat, lompat ke Fase 2)
- F-4: 404 di satu halaman waspadaweb + penanda + snapshot + verifikasi 2 vantage.
- F-5: 410 di halaman itu, penanda, verifikasi ulang 2x dari 2 vantage.
- F-6: rollback teruji + idempoten (eksekusi kedua tidak mengubah apa pun).

### Fase 2 -- M1 + M2 GANTI (INTI TUJUAN)
- F-7: M1 ambil konten donor (fetch, hash, simpan mentah, buang boilerplate).
- F-8: M2 pasang di target dengan penanda, dry-run dulu, snapshot nilai lama, rollback.
- F-9: verifikasi dari luar: penanda muncul di URL target; idempoten.

### Fase 3 -- perluas
- F-10..F-12: target lain, template, sub-halaman.

### Fase 4 -- bukti & pemantauan
- F-13: ekspor bukti siap pihak ketiga (status sebelum/sesudah, hash, header, curl luar,
  waktu UTC, vantage, SHA-256).
- F-14..F-16: pemantauan, link rot, registry parasite.
- F-17: systemd + Let's Encrypt + firewall + backup terjadwal.

## Target uji
waspadaweb.com lebih dulu. Kalau GANTI dan BUNUH belum terbukti di situ, jangan lanjut.

## Perkiraan
13-17 blok, 4-6 sesi. Fase 0 dan 1 (F-1..F-6) yang menentukan.

## Sumber data (koreksi)
GSC TIDAK BISA dipakai (butuh verifikasi kepemilikan). Pakai Ahrefs/Semrush/Moz/
Open PageRank/Common Crawl.

## Dampak ke dashboard (dicatat S-214)
Tidak ada fitur yang dihapus. Yang berubah: prioritas, dan dashboard harus menjadi
action-centric (GOAL bagian 10: halaman tanpa satu tombol aksi = belum jadi).

| Fitur sekarang | Perlakuan |
|---|---|
| Ikhtisar, Kandidat, Recon, Kredensial, Deployment, Konten, Tautan, Backlink, Laporan | tetap, prioritas ditunda |
| Driver (plan/apply/verify) | ditingkatkan menjadi mesin aksi K2 BUNUH (404/410, penanda, dry-run) |
| Tanam (FTP/SSH) | ditingkatkan menjadi jalur K1 GANTI |
| Monitor (status konten), Audit | tetap, menjadi tempat bukti M4 |
| Konsol | tetap |
| Panel teknologi | ditunda ke Fase 4 |
| BARU: halaman Jalur (peta J1-J7 + uji tulis) | Fase 0 |
| BARU: tombol TIDAK PUNYA AKSES, Tulis penanda, dry-run | mengikuti GOAL bagian 10 |

## Titik mulai
Mulai dari F-1. Bacaan wajib: PROLOG, GOAL, SKILL, SISA-KERJA.

## Inventaris yang sudah ada (diperiksa S-204)

Rute /api di app/main.py: 47

- /api/anggota
- /api/anggota/{tid}
- /api/audit
- /api/audit/peristiwa
- /api/clientlog
- /api/clientlog/bersih
- /api/deployment
- /api/deployment/{tid}
- /api/driver/apply
- /api/driver/plan
- /api/driver/rules
- /api/driver/verify
- /api/health
- /api/job/{jid}
- /api/job/{jid}/batal
- /api/job/{jid}/log
- /api/kandidat
- /api/kandidat.csv
- /api/kandidat/periksa
- /api/kandidat/periksa-latar
- /api/kandidat/periksa-status
- /api/kandidat/ringkas
- /api/konsol/aksi
- /api/konsol/jalankan
- /api/konten
- /api/konten/{tid}
- /api/konten/{tid}/indeks
- /api/kredensial
- /api/kredensial-uji
- /api/kredensial/rotasi
- /api/kredensial/{kid}/uji
- /api/kredensial/{tid}
- /api/monitoring
- /api/putaran
- /api/putaran/status
- /api/recon
- /api/setelan
- /api/status/periksa
- /api/status/ringkas
- /api/tanam
- /api/targets
- /api/targets/{tid}
- /api/targets/{tid}/recon
- /api/tautan
- /api/tautan/ringkas
- /api/teknologi-ringkas
- /api/teknologi/pindai

Panggilan /api dari skrip dashboard:

- aksi.js: /api/anggota, /api/clientlog, /api/clientlog/bersih, /api/deployment, /api/deployment/, /api/konten, /api/kredensial/rotasi, /api/monitoring, /api/setelan, /api/tanam, /api/tautan
- audit.js: /api/audit, /api/audit/peristiwa, /api/clientlog, /api/monitoring
- detail.js: /api/clientlog, /api/konten, /api/kredensial, /api/targets, /api/targets/
- driver.js: /api/driver/apply, /api/driver/plan, /api/driver/verify, /api/targets
- ekspor.js: /api/clientlog, /api/kandidat.csv
- ikhtisar.js: /api/clientlog, /api/kandidat/ringkas, /api/targets, /api/teknologi-ringkas, /api/teknologi/pindai
- konsol.js: /api/clientlog, /api/job/, /api/konsol/aksi, /api/konsol/jalankan, /api/kredensial, /api/kredensial-uji, /api/kredensial/
- konten.js: /api/clientlog, /api/deployment, /api/konten, /api/konten/, /api/kredensial, /api/targets
- live.js: /api/clientlog, /api/kandidat, /api/kandidat/periksa, /api/kandidat/periksa-latar, /api/kandidat/periksa-status, /api/putaran, /api/putaran/status, /api/targets
- monitor.js: /api/status/periksa, /api/status/ringkas, /api/targets
- recon.js: /api/clientlog, /api/recon, /api/targets, /api/targets/
- tanam.js: /api/tanam, /api/targets
- tautan.js: /api/clientlog, /api/tautan/ringkas
