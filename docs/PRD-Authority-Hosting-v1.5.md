# PRD — Authority Hosting Control Plane

**Codename internal:** Hestia
**Versi dokumen:** 1.5
**Tanggal:** 18 Oktober 2026
**Status:** Siap dikirim ke tim
**Pemilik dokumen:** Lead Engineer
**Reviewer:** Tim Teknis · Tim Growth/SEO · Manajemen

> **Cara membaca dokumen ini.** Ini adalah PRD untuk **alat kerja** (aplikasi), bukan dokumen strategi. Isinya: aplikasi apa yang dibangun, bentuknya seperti apa, dan siapa yang memakainya. Cara kerja strateginya dibahas pada dokumen terpisah.

---

## 1. Kontrol dokumen

| Field | Nilai |
|---|---|
| Nama program | Authority Hosting |
| Nama internal produk | Hestia |
| Versi | 1.5 |
| Status | Siap dikirim |
| Pemilik | Lead Engineer |
| Reviewer | Tim Teknis, Tim Growth, Manajemen |
| Target rilis MVP | segera |
| Dependensi | VPS/cloud, PostgreSQL, Redis, domain internal |

> Catatan: estimasi berbasis minggu sengaja tidak dipakai. Seluruh tahap ditargetkan bergerak segera, dipercepat oleh eksekusi berbantuan AI.

---

## 2. Ringkasan eksekutif

**Kesimpulan satu baris:** kita membangun satu panel terpusat untuk mengelola seluruh target penempatan konten — daftar targetnya, statusnya, kesehatannya, dan hasilnya.

Authority Hosting adalah program menempatkan konten milik kita di atas domain berotoritas tinggi (contoh: `.go.id`, `.ac.id`, domain media) untuk mempercepat indeksasi dan peringkat, dengan memanfaatkan kredibilitas domain tuan rumah.

Saat ini operasi dijalankan manual dan tersebar, sehingga tidak terukur. **Hestia** hadir sebagai satu tempat untuk mencatat, memantau, dan menjaga seluruh target.

MVP difokuskan pada **visibilitas dan kendali**: tim harus bisa melihat seluruh target, status, dan kesehatannya dalam satu layar, sebelum masuk ke tahap otomasi.

---

## 3. Konsep & cara kerja

### 3.1 Definisi program

Authority Hosting adalah pendekatan menempatkan konten milik kita di atas domain berotoritas tinggi — contoh `.go.id`, `.ac.id`, atau domain media — dengan memanfaatkan kredibilitas domain tersebut untuk mempercepat indeksasi dan peringkat.

Analogi yang dipakai konsisten di seluruh dokumen: domain berotoritas adalah **tuan rumah**, dan konten kita adalah **tamu**. Kita **bertamu** dengan membawa nilai.

### 3.2 Istilah resmi program

| Istilah | Arti |
|---|---|
| Tuan rumah | domain berotoritas tempat konten ditempatkan |
| Tamu | konten milik kita |
| Bertamu | aktivitas penempatan konten di tuan rumah |
| Kunci akses | jalur masuk ke target |
| Penyamaran | penyajian konten berbeda untuk bot dan manusia |

Seluruh dokumen memakai istilah di atas secara konsisten.

### 3.3 Nama & tagline

**Nama program: Authority Hosting** — netral, positif, dan aman disebut di forum formal maupun teknis.

**Tagline internal:** "Bertamu dengan membawa nilai."

**Codename produk (alat kerja):** Hestia — dewi perapian dan rumah dalam mitologi Yunani, lambang tuan rumah yang baik.

### 3.4 Naskah pitch ke tim (kata bijak)

Gunakan tiga kalimat ini saat memperkenalkan program:

1. "Kita tidak sedang menumpang. Kita bertamu dengan membawa nilai."
2. "Tuan rumah yang bijak tahu bahwa tamu yang baik menambah ramai, bukan mengganggu."
3. "Ini bukan biaya tambahan — ini kanal distribusi baru yang bisa diukur."

### 3.5 Mengapa pendekatan ini bekerja

Empat alasan yang bisa disampaikan terbuka ke tim:

1. **Kepercayaan domain.** Mesin pencari sudah mengenal dan mempercayai domain tuan rumah. Konten baru di atasnya memperoleh kredit awal yang lebih tinggi dibanding domain yang baru dibuat.
2. **Kecepatan indeksasi.** Halaman di domain berotoritas lebih cepat ditemukan dan diindeks.
3. **Kedekatan topik.** Bila konten relevan dengan isi tuan rumah, sinyal yang dikirim makin kuat.
4. **Keterukuran.** Karena semua tahap tercatat di panel, hasil bisa dibandingkan, bukan ditebak.

Kalimat kunci untuk tim: **"Yang kita bangun bukan sekadar menempel konten, tetapi proses yang bisa diulang dan diukur."**

### 3.6 Bagaimana kita masuk ke target

Ada tiga jalur masuk, dipilih sesuai kondisi masing-masing target:

| Jalur | Kapan dipakai | Yang dibutuhkan |
|---|---|---|
| Akun resmi | pengelola target bersedia memberi akses | akun panel admin |
| Panel terbuka | panel admin dapat diakses publik tanpa pengaman memadai | akun bawaan atau lemah |
| Celah teknis | tidak tersedia akun sama sekali | celah pada berkas unggahan atau komponen situs |

Apa pun jalurnya, semuanya disimpan sebagai **kunci akses** di panel — lengkap dengan jenis, level akses, dan masa berlakunya. Tujuannya satu: tim tidak perlu lagi mengingat-ingat cara masuk ke tiap target.

### 3.7 Alur kerja singkat

1. Kumpulkan kandidat target.
2. Nilai: otoritas, teknologi, dan kondisi keamanannya.
3. Amankan jalur masuk, lalu catat sebagai kunci akses.
4. Tempatkan konten pada target.
5. Pantau, rawat, dan laporkan.

Seluruh langkah di atas dipetakan menjadi modul di dalam panel.

---

## 4. Problem statement

Saat ini operasi berjalan manual dan terfragmentasi:

- Daftar target tersebar di beberapa spreadsheet, rawan hilang.
- Status target (aktif, sehat, rusak, kena bersih) tidak terpusat.
- Kredensial dan kunci akses tidak terdokumentasi rapi.
- Tidak ada monitoring — kerusakan baru ketahuan ketika sudah parah.
- Tidak ada jejak audit, sehingga sulit menelusuri siapa mengubah apa.

**Dampak:** waktu terbuang untuk pekerjaan administratif, target terlewat, dan keputusan berbasis tebakan.

**Peluang:** satu platform terpusat memangkas waktu operasional, menaikkan jumlah target terkelola, dan mengubah program dari seni menjadi proses.

---

## 5. Tujuan & non-tujuan

### 5.1 Tujuan — Tahap 1 sampai 3

| ID | Tujuan | Indikator |
|---|---|---|
| G1 | Satu sumber kebenaran untuk inventaris target | seluruh target tercatat, 0 spreadsheet liar |
| G2 | Recon & fingerprint otomatis | hasil recon < 60 detik per target |
| G3 | Monitoring kesehatan & integritas otomatis | cek berkala, alert < 15 menit |
| G4 | Penyimpanan akses/kredensial terpusat & aman | 100% kunci tercatat, terenkripsi |
| G5 | Dashboard pengambilan keputusan | ringkasan status dalam 1 layar |

### 5.2 Tujuan — Tahap 4 sampai 5

| ID | Tujuan |
|---|---|
| G6 | Deployment konten semi-otomatis + rollback |
| G7 | Manajemen aturan penyamaran |
| G8 | Pelacakan indeks & peringkat |
| G9 | Manajemen backlink berjenjang |

### 5.3 Non-tujuan (saat ini)

- N1. Bukan pengganti Google Search Console atau analytics.
- N2. Bukan platform CMS penuh.
- N3. Belum otomatis penuh — masih semi-manual.
- N4. Strategi kata kunci mendalam dibedah terpisah.

---

## 6. Persona & peran

| Peran | Deskripsi | Hak akses |
|---|---|---|
| Owner | Pemilik program | penuh |
| Engineer | Menjalankan recon, deploy, perbaikan | kelola target, deploy, kunci akses |
| Analyst | Memantau & melaporkan | baca + ekspor |
| Viewer | Manajemen | dashboard read-only |

RBAC granular per modul. Setiap aksi tulis tercatat di audit log.

---

## 7. Ruang lingkup & tahap

### Tahap 1 — Fondasi & kendali

1. Autentikasi & RBAC
2. Inventaris target
3. Dashboard ringkas

*Selesai bila:* tim dapat menambah target dan melihat status seluruh target dalam satu layar.

### Tahap 2 — Recon & kunci akses

4. Recon & fingerprint
5. Vault kunci akses

*Selesai bila:* setiap target punya hasil penilaian dan jalur masuk yang tercatat.

### Tahap 3 — Monitoring & integritas

6. Monitoring kesehatan & integritas
7. Alerting & notifikasi

*Selesai bila:* perubahan mencurigakan pada target terdeteksi otomatis dan memicu notifikasi.

### Tahap 4 — Penempatan & penyamaran

8. Deployment konten & template
9. Manajemen aturan penyamaran
10. Manajemen halaman & kata kunci
11. Log deployment & rollback

*Selesai bila:* konten dapat ditempatkan pada target dan tampilannya dapat diuji untuk bot maupun manusia.

### Tahap 5 — Pertumbuhan

12. Pelacakan indeks & peringkat
13. Manajemen backlink
14. Mesin skoring & prioritas

*Selesai bila:* peringkat dan halaman terindeks terpantau dari dalam panel.

---

## 8. Arsitektur sistem

```
[ SPA Frontend ] --HTTPS--> [ API Gateway / REST ] --+--> [ Auth & RBAC ]
                                                     +--> [ Service: Target ]
                                                     +--> [ Service: Recon ] --> [ Queue ]
                                                     +--> [ Service: Monitor ] -> [ Scheduler ]
                                                     +--> [ Service: Vault ] --> [ KMS/Envelope ]
                                                     +--> [ Service: Deploy ]
                                                     |
                                              [ PostgreSQL ]  [ Redis ]  [ Object Storage ]
                                                     |
                                              [ Worker Pool ] -> target eksternal
```

- **Frontend:** SPA (React/Next). Tabel besar, filter, detail tabbed, komponen status.
- **Backend:** REST API + worker queue untuk tugas panjang (scan, deploy, cek berkala).
- **Database:** PostgreSQL.
- **Queue:** Redis + worker pool.
- **Vault:** enkripsi secret (envelope encryption), kunci master terpisah dari DB.
- **Scheduler:** cron untuk monitoring periodik.
- **Object storage:** artefak (screenshot, log, dump).
- **Observability:** logging terstruktur, metrics, tracing.

---

## 9. Model data

| Entitas | Atribut kunci |
|---|---|
| User | id, nama, email, role_id, mfa, last_login |
| Role | id, nama, permission[] |
| Target | id, domain, tld, tipe, owner, tag[], status, authority_score, catatan |
| TargetSnapshot | id, target_id, waktu, header, cms, versi, server, ip |
| Finding | id, target_id, jenis, severity, bukti, waktu |
| Access | id, target_id, tipe (akun/kunci akses/ssh/sftp), level, secret_ref, valid_until |
| Deployment | id, target_id, path, template, status, log_ref, rollback_ref, waktu |
| ContentPage | id, target_id, url, kata_kunci, template, status, index_status |
| CloakingRule | id, target_id, kondisi (ua/ip/path), aksi, aktif |
| MonitorCheck | id, target_id, jenis, hasil, latensi, waktu |
| BacklinkNode | id, page_id, tier, sumber, anchor, status |
| Alert | id, target_id, severity, pesan, status, waktu |
| AuditLog | id, actor, aksi, objek, sebelum, sesudah, waktu |
| Integration | id, jenis, kredensial_ref, status |
| ApiKey | id, nama, hash, scope, expired |

Relasi inti: Target 1-N Snapshot/Finding/Access/Deployment/ContentPage/CloakingRule/MonitorCheck.

---

## 10. Permukaan API (contoh)

| Method | Path | Fungsi |
|---|---|---|
| POST | `/auth/login` | masuk |
| GET | `/targets` | daftar target (filter, paginasi) |
| POST | `/targets` | tambah target |
| GET | `/targets/:id` | detail target |
| POST | `/targets/:id/recon` | jalankan recon |
| GET | `/targets/:id/findings` | daftar temuan |
| GET/POST | `/targets/:id/access` | kunci akses |
| POST | `/targets/:id/deploy` | deploy konten |
| GET | `/targets/:id/health` | status kesehatan |
| GET/POST | `/targets/:id/cloak` | aturan penyamaran |
| GET | `/monitor/events` | riwayat cek |
| GET | `/reports/summary` | ringkasan dashboard |
| GET | `/audit` | audit log |

Standar: JSON, paginasi kursor, filter query, error konsisten, versioning `/v1`.

---

## 11. Kebutuhan fungsional

### 11.1 Autentikasi & RBAC
- **FR-01** Login email + kata sandi, dukungan MFA (TOTP).
- **FR-02** Peran & izin granular per modul.
- **FR-03** Sesi kedaluwarsa otomatis, logout paksa oleh admin.
- *Acceptance:* pengguna tanpa izin `deploy` tidak bisa menekan tombol deploy (disabled + alasan).

### 11.2 Inventaris target
- **FR-04** CRUD target dengan field: domain, tipe, pemilik, tag, status, catatan.
- **FR-05** Impor massal via CSV.
- **FR-06** Pencarian, filter (status/tag/tipe), urut, paginasi.
- **FR-07** Status siklus: `kandidat → dianalisis → aktif → rusak → dibersihkan → nonaktif`.
- *Acceptance:* impor 500 baris selesai < 10 detik dengan laporan baris gagal.

### 11.3 Recon & fingerprint
- **FR-08** Ambil header, deteksi CMS & versi, server, IP, redirect.
- **FR-09** Deteksi indikator: direktori `uploads` dapat dieksekusi, `.htaccess` dapat ditulis, versi usang.
- **FR-10** Simpan snapshot bertanggal, bisa dibandingkan antar waktu.
- *Acceptance:* recon tidak memblokir UI; progres tampil real-time; hasil tersimpan otomatis.

### 11.4 Vault kunci akses
- **FR-11** Simpan akun/kunci akses dengan tipe & level akses.
- **FR-12** Secret terenkripsi; UI menampilkan sebagian (masked) + tombol reveal.
- **FR-13** Catat masa berlaku & pengingat rotasi.
- *Acceptance:* secret tidak pernah terkirim dalam bentuk plaintext pada respons daftar.

### 11.5 Monitoring & integritas
- **FR-14** Cek berkala: status HTTP, latensi, perubahan hash berkas kunci, perubahan header.
- **FR-15** Deteksi anomali: berkas baru di direktori unggahan, perubahan `.htaccess`/`index.php`.
- **FR-16** Kirim alert sesuai severity & kanal.
- *Acceptance:* perubahan hash berkas kunci memicu alert < 15 menit.

### 11.6 Deployment
- **FR-17** Pilih target + template, deploy ke path, tampilkan diff.
- **FR-18** Log lengkap tiap deployment, opsi rollback.
- *Acceptance:* rollback mengembalikan kondisi sebelumnya dengan 1 klik.

### 11.7 Penyamaran
- **FR-19** Atur kondisi (User-Agent, rentang IP, path) dan aksi (sajikan konten A/B).
- **FR-20** Uji simulasi: "tampilkan apa yang dilihat bot" vs "yang dilihat manusia".
- *Acceptance:* hasil uji menampilkan dua render berdampingan.

### 11.8 Konten & kata kunci
- **FR-21** Kelola halaman per target: URL, kata kunci, template, status.
- **FR-22** Status indeks manual/otomatis.

### 11.9 Backlink
- **FR-23** Catat node backlink berjenjang (tier 1/2/3) dengan anchor & sumber.

### 11.10 Laporan & audit
- **FR-24** Dashboard ringkas; ekspor CSV/PDF.
- **FR-25** Audit log semua aksi tulis, tidak dapat diubah.

---

## 12. Kebutuhan UI/UX

### 12.1 Navigasi utama (sidebar)

```
Dashboard · Target · Recon · Kunci akses · Deployment ·
Konten · Penyamaran · Monitoring · Backlink · Laporan · Pengaturan
```

### 12.2 Layar dashboard

```
+-----------------------------------------------------------+
| Authority Hosting                         [cari] [profil] |
+-----------------------------------------------------------+
| Target aktif   Kesehatan   Alert aktif   Total deploy     |
|     128           96%          4             31           |
+-----------------------------------------------------------+
| Distribusi status     |  Tren kesehatan                   |
| [bar]                 |  [line chart]                     |
+-----------------------------------------------------------+
| Alert terbaru                                            |
| - target A: berkas baru di uploads       [lihat]          |
+-----------------------------------------------------------+
```

Kartu ringkas: total target, persentase sehat, jumlah alert, total deployment. Aksi cepat: tambah target, jalankan recon massal.

### 12.3 Layar target (daftar)

Tabel dengan kolom: domain, tipe, status, skor otoritas, terakhir dicek, aksi. Filter bar sticky. Bulk action: recon, tandai status, ekspor.

### 12.4 Layar detail target (tabbed)

Tab: `Ringkasan · Teknologi · Kunci akses · Konten · Penyamaran · Kesehatan · Timeline`.
Setiap tab punya state: kosong, memuat, error, dan aksi utama.

### 12.5 Standar komponen

- Badge status dengan warna konsisten (hijau/kuning/merah/abu).
- Tabel: sortable, kolom dapat disembunyikan, kepadatan nyaman/rapat.
- Semua aksi destruktif meminta konfirmasi.
- Empty state selalu memberi satu aksi lanjutan.

---

## 13. Kebutuhan non-fungsional

| Kategori | Target |
|---|---|
| Performa | daftar 1.000 baris < 1,5 detik; aksi < 300 ms |
| Ketersediaan | 99,5% uptime panel |
| Skalabilitas | 5.000 target tanpa penurunan |
| Observability | log terstruktur, metrics, tracing |
| Aksesibilitas | kontras memadai, navigasi keyboard |
| Lokalisasi | antarmuka Bahasa Indonesia |

---

## 14. Kebutuhan keamanan

- **SEC-01** Secret terenkripsi at-rest (envelope encryption), kunci master terpisah.
- **SEC-02** Prinsip hak paling sedikit untuk semua peran.
- **SEC-03** MFA wajib untuk Owner & Engineer.
- **SEC-04** Audit log tak dapat diubah.
- **SEC-05** Proteksi SSRF pada modul recon (validasi target, batas redirect).
- **SEC-06** Rate limit & antrian untuk cegah banjir request ke target.
- **SEC-07** Rotasi kredensial berkala + pengingat.
- **SEC-08** Backup terenkripsi harian, uji pemulihan bulanan.

---

## 15. Integrasi

| Integrasi | Tahap | Catatan |
|---|---|---|
| Google Search Console | 5 | status indeks |
| Analytics | 5 | trafik |
| Pelacak peringkat | 5 | posisi kata kunci |
| Monitor uptime eksternal | 3 | redundansi |
| Kanal notifikasi (email/chat) | 3 | alert |

---

## 16. Risiko & mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Perubahan kebijakan mesin pencari | peringkat turun | pantau kebijakan, diversifikasi tipe target |
| Target memperbaiki & menghapus konten kita | kehilangan halaman | monitoring berkala + cadangan template |
| Kredensial bocor | pengambilalihan | vault + rotasi + hak paling sedikit |
| Update CMS merusak penempatan | halaman hilang | monitoring integritas + rollback |
| Penyamaran terbongkar | kualitas turun | uji berkala bot vs manusia |

---

## 17. Metrik keberhasilan

### 17.1 Metrik operasional

| Metrik | Target awal |
|---|---|
| Jumlah target terkelola | 100+ |
| Persentase target sehat | > 90% |
| Waktu tambah target baru | < 5 menit |
| Waktu deteksi anomali | < 15 menit |
| Waktu deploy konten | < 10 menit |
| Adopsi harian tim | > 80% anggota aktif |

### 17.2 Metrik hasil

| Metrik hasil | Arah |
|---|---|
| Halaman terindeks | bertambah |
| Peringkat kata kunci sasaran | naik |
| Trafik dari halaman tamu | bertambah |
| Jumlah target aktif & sehat | bertambah |

---

## 18. Roadmap

> Estimasi minggu tidak dipakai. Seluruh tahap bergerak segera. **Urutan wajib:** Tahap 1 diselesaikan lebih dulu; Tahap 2 sampai 5 boleh berjalan paralel setelahnya.

| Tahap | Isi | Estimasi |
|---|---|---|
| Tahap 1 | Fondasi: auth, RBAC, target, DB | segera |
| Tahap 2 | Recon + vault kunci akses | segera |
| Tahap 3 | Monitoring + integritas + alert | segera |
| Tahap 4 | Deployment + penyamaran | segera |
| Tahap 5 | Indeks, peringkat, backlink | segera |

---

## 19. Pertanyaan terbuka (dijawab di sesi kickoff)

1. Sumber tunggal daftar target: impor manual atau hasil penemuan otomatis?
2. Apakah deployment harus otomatis penuh atau tetap setujui manusia?
3. Kanal alert apa yang dipakai (email, chat, atau keduanya)?
4. Siapa pemilik data dan berapa lama disimpan?
5. Apakah panel perlu diakses dari luar jaringan internal?

Kelima butir di atas bukan kekurangan dokumen, melainkan keputusan yang memang perlu diambil bersama tim.

---

## Lampiran A — Glosarium

- **Authority Hosting** — program menempatkan konten di domain berotoritas.
- **Tuan rumah** — domain berotoritas tempat konten ditempatkan.
- **Tamu** — konten milik kita.
- **Kunci akses** — jalur masuk ke target (backdoor).
- **Penyamaran** — penyajian konten berbeda untuk bot dan manusia.
- **Snapshot** — potret kondisi target pada satu waktu.

---

## Lampiran B — Naskah pitch

> "Kita tidak sedang menumpang. Kita bertamu dengan membawa nilai. Tuan rumah yang bijak tahu bahwa tamu yang baik menambah ramai, bukan mengganggu. Dan ini bukan biaya tambahan — ini kanal distribusi baru yang bisa diukur."

---

## Lampiran C — Alternatif nama

Dipakai hanya sebagai catatan. **Nama resmi yang berlaku adalah Authority Hosting.**

| Nama | Nuansa |
|---|---|
| Authority Hosting | positif, ramah |
| Guest Authority | netral |
| Simbiosis Konten | akademis, menang-menang |
| Kemitraan Otoritas Domain | formal |

---

## Lampiran D — Isi README repo

Simpan sebagai `README.md` di akar repo.

```markdown
# Hestia

Hestia adalah panel kerja untuk program Authority Hosting — mengelola daftar
target, kunci akses, penempatan konten, dan pemantauannya dalam satu tempat.

- Dokumen kebutuhan: docs/PRD-Authority-Hosting-v1.5.md
- Status: tahap perancangan
```