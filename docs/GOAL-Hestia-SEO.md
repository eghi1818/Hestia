# GOAL — HESTIA
## Kendali Konten & Status pada Situs Orang Lain

---

## 0. SATU GOAL — kalau ragu, baca ini

> ### Hestia HARUS bisa mengganti konten di situs orang dengan konten dari situs lain, dan HARUS bisa membuat halaman itu 404, blank, atau error.

Dua kemampuan. Tidak ada yang lain.

| # | Kemampuan | Arti |
|---|---|---|
| **K1** | **GANTI** | Ambil konten dari web A → pasang di web B, menggantikan yang ada |
| **K2** | **BUNUH** | Buat halaman di web B jadi 404, blank, atau error |

**Mantra:**

> **Tujuanku: mengganti konten di situs orang dengan konten dari situs lain, dan bisa membuatnya 404, blank, atau error.**
> **Caranya: temukan jalur masuk, buktikan jalurnya bisa menulis, baru bertindak.**
> **Buktinya: penanda. Tanpa penanda, belum selesai.**

---

## 1. DEFINISI TERCAPAI — kapan GOAL dinyatakan berhasil

Ini ujiannya. Kalau belum lulus, GOAL belum tercapai.

### K1 (GANTI) dinyatakan TERCAPAI bila:
1. Konten diambil dari situs A (tersimpan, ber-hash).
2. Konten itu terpasang di situs B, menggantikan yang lama.
3. `curl` **dari jaringan luar** menampilkan **penanda kita** di URL situs B.
4. Nilai lama disimpan dan bisa dikembalikan.

### K2 (BUNUH) dinyatakan TERCAPAI bila:
1. Sebuah halaman di situs B yang tadinya normal, kini berperilaku sesuai yang dituju — 404, blank, atau error.
2. `curl` **dari jaringan luar** membuktikan perubahannya.
3. Terverifikasi ulang minimal 2 kali, dari 2 vantage berbeda.

### GOAL dinyatakan TERCAPAI bila:
> **K1 dan K2 terbukti pada minimal satu situs orang lain, dengan bukti yang bisa ditunjukkan ke pihak ketiga.**

**HARUS.** Bukan "sebaiknya". Bukan "sudah dirancang". Kalau belum ada satu pun perubahan nyata di situs orang, GOAL belum tercapai.

---

## 2. FAKTA DASAR — tidak boleh dilupakan

1. **Kita tidak punya situs apa pun.** Tidak ada domain, tidak ada hosting. Semua target = **situs orang lain**.
2. **Kita tidak punya akses apa pun di awal.** Tidak ada FTP, SSH, panel, database, API. Tidak kenal pemiliknya, tidak ada izin.
3. Karena itu: **akses bukan diasumsikan — akses DITEMUKAN.**
4. **REA dan Hestia terpisah, tanpa API.** Penyambungnya **berkas** yang diunggah manual.
5. **Hasil REA itu klaim, bukan bukti.** Hestia wajib menguji ulang.

## 3. KEBENARAN PAHIT — yang harus dihafal

| Kalau kita punya… | Yang bisa kita lakukan |
|---|---|
| Hanya HTTP biasa (J1) | **membaca saja.** Tidak bisa mengubah apa pun. |
| Sebuah jalur masuk | baru bisa mengganti dan mematikan |

**Tanpa jalur, tidak ada perubahan.** Titik.

---

## 4. PRASYARAT — JALUR MASUK (J1–J7)

Jalur adalah segalanya. Tanpa ini, Hestia hanya penonton.

| Jalur | Cara masuk | Bisa GANTI | Bisa BUNUH |
|---|---|---|---|
| J1 | HTTP biasa | ✗ | ✗ |
| J2 | form / komentar | ✓ (terbatas) | ✗ |
| J3 | kredensial CMS/panel lemah | ✓ | ✓ (404, blank) |
| J4 | kebocoran kredensial (`.env`, `.git`, backup) | ✓ | ✓ (404, blank) |
| J5 | layanan terbuka (FTP/SSH/DB/panel) | ✓ | ✓ **penuh** |
| J6 | kerentanan (SQLi, LFI, RCE) | ✓ (SQLi: via DB) | ✓ (404, blank **saja**) |
| J7 | API terbuka | ✓ | ~ |

**Aturan:** selalu pakai jalur **terdalam yang tersedia**, bukan yang paling mudah. Jalur dangkal gampang hilang.

---

## 5. MODUL — lima saja

### M0 — MASUK *(prasyarat, bukan tujuan)*
**Tujuan:** tahu jalur apa yang kita punya, dan **buktikan bisa menulis**.
- Masukan: berkas REA (JSON/PDF/MD/CSV)
- Cara: urai → normalisasi → uji tulis (tulis penanda → baca ulang → hapus)
- **SELESAI bila:** ada ≥1 jalur yang terbukti bisa menulis, dengan bukti
- **GAGAL bila:** semua jalur hanya J1

### M1 — AMBIL
**Tujuan:** tarik konten dari web donor.
- Cara: fetch, parse, simpan apa adanya + hash
- **SELESAI bila:** konten donor tersimpan, ber-hash, bisa diputar ulang

### M2 — GANTI *(TUJUAN INTI 1)*
**Tujuan:** konten donor terpasang di target, menggantikan yang ada.
- Butuh jalur: J3–J7
- Cara: lihat §6
- **SELESAI bila:** `curl` dari luar menampilkan penanda kita
- **Wajib:** dry-run, snapshot nilai lama, bisa dikembalikan

### M3 — BUNUH *(TUJUAN INTI 2)*
**Tujuan:** halaman jadi 404, blank, atau error.
- Butuh jalur: J3 ke atas (**410 dan 403 butuh J5**)
- Cara: lihat §7
- **SELESAI bila:** `curl` dari luar menunjukkan status/isi yang dituju

### M4 — BUKTI
**Tujuan:** perubahan terbukti, bisa ditunjukkan ke pihak ketiga.
- **SELESAI bila:** ada penanda + status sebelum/sesudah + hash + screenshot + waktu + SHA-256

---

## 6. CARA MENGGANTI KONTEN

| Cara | Butuh jalur | Ketahanan |
|---|---|---|
| Tulis file langsung | J5, J4 | kuat |
| Ubah template | J5, J4, J3 | kuat (berlaku global) |
| wp-cli / WP REST API | J3 | sedang |
| Edit lewat CMS | J3 | sedang |
| Tulis DB langsung | J4, J6 | sedang |
| Rewrite | J5 | kuat |

## 7. CARA MEMBUNUH — tabel lengkap

| Hasil yang dituju | Cara | Butuh jalur |
|---|---|---|
| **404** | hapus file / hapus baris / nonaktifkan status | J3–J6 |
| **blank** (200 tapi kosong) | kosongkan isi / ganti file kosong | J3–J6 |
| **error** (500) | arahkan ke path rusak / rusak sengaja | J5 |
| **410** | rewrite `return 410` | **J5 / RCE** |
| **403** | `.htaccess deny` / ubah permission | **J5** |
| **redirect** | 301 ke tempat lain | J5 |

**Hafal:** jalur **J6-SQLi hanya bisa 404 dan blank**. Tidak bisa 410, tidak bisa 403. **Jangan janji.**

---

## 8. ALUR KERJA — jangan dilompati

```
1. Pilih target
2. Analisa di REA  →  keluarkan berkas (JSON / PDF / MD / CSV)
3. Unggah berkas ke Hestia
4. Hestia urai → normalisasi → konfirmasi manusia
5. Hestia VALIDASI JALUR  ← langkah paling penting, tidak boleh dilewati
6. Jalankan M1 → M2 (GANTI) atau M3 (BUNUH)
7. Rekam bukti
```

---

## 9. BUKTI — penanda wajib

Setiap aksi menempelkan penanda unik tak terlihat:
```html
<!-- hestia:8f3a91c2 -->
```
Bukti wajib: status sebelum/sesudah · hash body sebelum/sesudah · header respons · `curl` dari luar · screenshot · waktu UTC + vantage · SHA-256 artefak.

**Tanpa penanda, belum selesai.** Ini bukan formalitas — ini satu-satunya cara membedakan "berhasil" dari "kelihatannya berhasil".

---

## 10. ATURAN ANTI-MELENCENG — bagian paling kritis

**A. Kalau ragu, tanya satu pertanyaan:**
> *"Apakah ini membuat saya bisa MENGUBAH konten atau STATUS di situs orang?"*
> Kalau tidak → **tunda**.

**B. DILARANG membangun monitoring dulu.** Dashboard yang bisa melaporkan 100 halaman tapi tidak bisa mengubah satu pun = **GAGAL**. Tujuan kita mengubah, bukan melaporkan.

**C. DILARANG menyerang tanpa peta.** Peta jalur dulu, baru bertindak.

**D. DILARANG percaya berkas REA mentah.** `confirmed` dan `proven` dari REA masih klaim. Uji ulang dulu.

**E. DILARANG menganggap SQLi bisa menulis.** SQLi yang hanya `SELECT` tidak berguna untuk mengganti konten. Buktikan `INSERT`/`UPDATE`.

**F. DILARANG menjanjikan kemampuan yang jalurnya belum ada.** Terutama 410 dan 403.

**G. DILARANG lupa penanda.** Tanpa penanda, tidak ada bukti.

**H. DILARANG menulis sebelum read-only.** Semua integrasi dimulai dalam mode aman.

**I. DILARANG membulatkan gagal jadi "berhasil".** Kalau gagal, katakan gagal.

**J. DILARANG pindah ke VPS sebelum terbukti di lokal.** VPS bukan tempat mencari bug.

**K. DILARANG mengubah berkas REA.** Simpan apa adanya.

**L. Satu langkah, satu bukti.** Tidak ada bukti = langkah belum selesai.

**M. Kalau harus memilih antara membangun fitur baru vs membuktikan kemampuan inti → pilih MEMBUKTIKAN.**

---

## 11. NON-GOALS — apa yang harus DITUNDA

- Audit SEO menyeluruh
- Machine learning, LLM fine-tuning
- Kubernetes, service mesh, Kafka/RabbitMQ
- SSO, RBAC granular
- Data warehouse terpisah
- Panel admin yang cantik

Cukup: **Python/Node, satu database relasional, cron/systemd timer, HTTP client.**

**GSC tidak bisa dipakai** (butuh verifikasi kepemilikan). Pakai Ahrefs/Semrush/Moz/Open PageRank/Common Crawl.

---

## 12. URUTAN PENGERJAAN

1. **Fase 0** — Skema data (Target, Jalur, Berkas, Aksi, Bukti) + M0 untuk 5–10 target.
2. **Fase 1** — Buktikan **M3 (BUNUH)** di satu target berjalur. 404 dulu, lalu 410.
3. **Fase 2** — Buktikan **M1 + M2 (GANTI)** di target yang sama.
4. **Fase 3** — Perluas: target lain, template, sub-halaman.
5. **Fase 4** — Bukti, pemantauan, link rot.

**Alasan urutan:** membuktikan bisa menulis > membuat laporan.

---

## 13. SEBELUM MENULIS KODE

1. Jalankan **M0** pada 5–10 target. Hasilkan peta jalur + bukti.
2. Pilih **satu target dengan jalur tertinggi**.
3. Ajukan rencana: jalur mana, mekanisme apa, bukti apa.
4. Konfirmasi. **Baru implementasi.**

**DILARANG menulis kode sebelum ada peta.** Kalau tidak, Anda membangun tangan untuk pintu yang belum ketemu.

---

## 14. TARGET UJI

| Target | Dugaan jalur | Bisa apa |
|---|---|---|
| `waspadaweb.com` | J5 (SSH root) + nginx | **GANTI + BUNUH penuh**, termasuk 410 |
| `juraganit.com` | J5 (FTP) + LiteSpeed | GANTI + BUNUH (410 lewat `.htaccess`) |
| `persaudaraan.com` | J1 / J7 (Netlify) | GANTI terbatas |
| `wecash.ai` | belum dipetakan | — |

**Mulai dari `waspadaweb.com`.** Kalau di situ GANTI dan BUNUH belum terbukti, **jangan lanjut ke yang lain**.

---

## 15. ATURAN MUTLAK

1. Tujuan hanya dua: **GANTI** dan **BUNUH**.
2. Tanpa jalur, tidak ada perubahan.
3. Peta dulu, baru serang.
4. Validasi jalur sebelum bertindak.
5. Dry-run sebelum menulis.
6. Snapshot sebelum menimpa.
7. Penanda di setiap injeksi.
8. Bukti, atau belum selesai.
9. Jangan janji yang jalurnya belum ada.
10. Kalau ragu — kembali ke §0.

---

> ### Kalau semua modul selesai tapi belum ada satu pun halaman situs orang yang berubah — **GOAL BELUM TERCAPAI.**
> ### Buktikan dulu satu perubahan nyata. Baru bangun yang lain.