Sebelum masuk daftar, satu koreksi teknis penting yang harus agent kamu tahu duluan — kalau tidak, dia akan salah desain dari awal:

**Redirect bawaan HestiaCP itu level-domain, bukan level-URL.** Signature aslinya `v-add-web-domain-redirect USER DOMAIN REDIRECT [HTTPCODE] [RESTART]`. Argumen ketiga adalah **tujuan**, dan tidak ada argumen **sumber path**. Jadi perintah ini bisa mengalihkan seluruh `domain.tld` ke `domain.tld/baru`, tapi **tidak bisa** mengalihkan `/halaman-lama/` ke `/halaman-baru/`. Untuk per-URL, agent harus pakai file include custom di `/home/<user>/conf/web/<domain>/nginx.conf_<nama>` (di-include otomatis oleh template) atau `.htaccess` kalau stack-nya Apache tanpa nginx. Ini keterbatasan nyata Hestia, bukan bug.

---

# Skill yang dibutuhkan agent

## A. Skill tingkat wajib

### 1. Sistem operasi & server
- Linux (Debian/Ubuntu, karena HestiaCP di situ), permission model, ownership, symlink
- Bash scripting level menengah: pipe, exit code, `set -e`, parsing output CLI
- systemd (service, timer) dan cron
- Manajemen proses & port, `ss`/`lsof`, restart service aman
- Isolasi user HestiaCP: setiap domain terikat ke user sistem, path `/home/<user>/`

### 2. HestiaCP spesifik
- **REST API**: `POST https://<host>:8083/api/` dengan parameter `hash="<access_key>:<secret_key>"`, `returncode="yes"`, `cmd`, lalu `arg1..argN`. Paham beda auth legacy `user`/`password` vs access key.
- **CLI `v-*`** di `/usr/local/hestia/bin/`: paham bahwa semuanya script bash dan bisa dibaca langsung untuk verifikasi argumen — dokumentasi API Hestia masih berstatus work in progress.
- Perintah yang akan sering dipakai: `v-list-web-domains`, `v-list-web-domain`, `v-add-web-domain-redirect`, `v-delete-web-domain-redirect`, `v-list-web-domain-accesslog`, `v-list-web-domain-errorlog`, `v-rebuild-web-domain`, `v-log-action`.
- **Cara membaca redirect yang sedang aktif**: tidak ada `v-list-web-domain-redirect`. Nilainya tersimpan sebagai key `REDIRECT` dan `REDIRECT_CODE` di objek domain, jadi harus dibaca lewat `v-list-web-domain`.
- **Paham efek samping**: perintah redirect menulis ke `/home/<user>/conf/web/<domain>/nginx.conf_redirect` dan `nginx.ssl.conf_redirect`, hanya jalan kalau `WEB_SYSTEM` atau `PROXY_SYSTEM` = nginx, dan kalau Apache murni akan keluar dengan pesan "Non supported please use .htaccess instead".
- Paham Hestia punya **mode read-only / demo mode** (`check_hestia_demo_mode`) yang memblokir aksi write.
- Paham bahwa edit manual di config akan tertimpa regenerate — cara yang benar adalah file include custom berpola `nginx.conf_<nama>`, bukan mengedit `nginx.conf` langsung.

### 3. HTTP & semantik status code
- Hafal semantik dan konsekuensi SEO: `301` permanen, `302`/`307` temporer, `308` permanen + mempertahankan method, `404` tidak ditemukan, `410` hilang permanen, `soft 404`.
- Tahu bahwa Google menjatuhkan halaman 410 lebih cepat daripada 404, dan bahwa 404 baru benar kalau halaman dihapus dan tidak ada pengganti setara.
- Tahu bahwa `return 410 <teks>` di nginx menghasilkan status 410 dengan body teks dan **tanpa header Location** — jadi secara teknis bisa dicapai lewat perintah redirect Hestia, tapi semantiknya bukan redirect.
- Paham header: `Location`, `X-Robots-Tag`, `Link: rel=canonical`, `Retry-After`.
- Paham `robots.txt`, meta robots, sitemap XML, directive `noindex` vs `disallow` (dan bedanya — `disallow` mencegah crawl, `noindex` mencegah index).

### 4. Crawling & pengambilan data
- HTTP client dengan kontrol: timeout, retry dengan backoff, concurrency limit, connection pool
- Kepatuhan `robots.txt` saat crawl sendiri, pengaturan crawl rate agar tidak membebani server
- Verifikasi bot sungguhan: reverse DNS lalu forward-confirm untuk Googlebot (`*.googlebot.com`, `*.google.com`) — jangan percaya `User-Agent` mentah
- Headless browser (Playwright/Puppeteer) untuk halaman yang butuh render JS
- Parsing HTML: ekstraksi judul, H1, body, canonical, meta robots; pembuangan boilerplate (nav, footer, sidebar)

### 5. Deteksi kemiripan & diff konten
- Shingling + MinHash/LSH, atau simhash, untuk near-duplicate detection
- Normalisasi teks sebelum hashing: lowercase, hapus whitespace berlebih, buang markup, stem opsional
- Threshold kemiripan yang bisa dikalibrasi — modul 3 butuh "kemiripan <30% = takeover", modul 2 butuh perubahan sedang
- Diff viewer dua kolom di level blok, bukan karakter

### 6. Pengetahuan domain SEO untuk kelima poin
Ini skill yang paling sering dianggap remeh padahal penentu. Agent harus paham persis:

| Poin | Yang harus benar-benar dipahami |
|---|---|
| Parasite SEO | Kenapa otoritas tidak lagi ditransfer, apa yang masih transfer (kecepatan indeksasi, distribusi, kelayakan sitasi AI), dan bahwa manual action mendarat di domain host bukan di kita |
| Content replacement / repurposing | Risiko relevance mismatch antara anchor backlink lama dan konten baru; bahwa URL yang dipertahankan mempertahankan equity tapi bisa kehilangan relevansi |
| URL hijacking / page hijacking | Perbedaan dengan parasite SEO, peran tag canonical, dan bagaimana menilai siapa pemegang SERP saat ini |
| Pruning / hard delete | Aturan keputusan 301 vs 410 vs 404, dan kenapa 404 adalah pilihan terakhir kalau ada backlink |
| Link rot | Bedanya inbound rot dan outbound rot, cara mengukur equity terdampar, dan alur link reclamation |

### 7. Sumber data backlink & data pencarian
- **Google Search Console API**: OAuth2 atau service account; Search Analytics API (16 bulan data, 25.000 baris per request, jeda 2–3 hari); URL Inspection API (kuota 2.000 query/hari dan 600/menit per properti — ini harus dihormati, gampang kena limit); Sitemaps API; laporan index coverage.
- API vendor berbayar (Ahrefs / Semrush) beserta kuota dan format responsnya.
- Crawler sendiri sebagai fallback, plus kesadaran bahwa setiap sumber punya bias dan harus dilabeli asalnya.

## B. Skill tingkat penting

### 8. Data engineering
- Desain skema relasional: entitas `Page`, `Host`, `ChangeEvent`, `StatusCheck`, `Backlink`, `Decision`, `ActionLog`, `MetricSnapshot`
- Time-series snapshot: semua modul butuh "sebelum vs sesudah", jadi tidak boleh ada overwrite
- Idempotensi: kunci unik, upsert, watermark per job
- Migrasi skema, retensi data, deduplikasi
- Antrean job dan worker terpisah dari proses web

### 9. Backend
- Desain REST API, validasi input, penanganan error yang konsisten
- Manajemen secret (env / file config terpisah, tidak hardcoded)
- Autentikasi dan otorisasi minimal (satu admin dulu boleh, tapi harus benar)
- Pencegahan SSRF saat dashboard melakukan fetch ke URL sembarang

### 10. Frontend dashboard
- Tabel dengan filter, sort, dan paginasi server-side (data bisa ratusan ribu baris — jangan render semua di klien)
- Chart untuk trend dan heatmap
- Drilldown: setiap angka bisa diklik sampai ke sumbernya
- Diff viewer, badge status, indikator severity
- Aksesibilitas dasar dan layout yang tidak pecah di data panjang

### 11. Penjadwalan & orkestrasi
- cron atau systemd timer per modul, dengan locking supaya job tidak tumpang tindih
- Retry, backoff, dead-letter untuk job yang gagal
- **Mode dry-run wajib** untuk semua aksi write, dan hasil dry-run harus bisa ditinjau sebelum eksekusi

### 12. Alerting
- SMTP atau webhook (Slack/Discord)
- Deduplikasi alert supaya tidak spam
- Level severity dan aturan eskalasi
- Alert harus punya konteks: URL, status lama, status baru, waktu, sumber data

### 13. Keamanan
- Prinsip least privilege untuk access key HestiaCP dan kredensial API vendor
- Rotasi kredensial, penyimpanan terenkripsi
- Rate limiting pada endpoint dashboard sendiri
- Audit log yang tidak bisa diubah — manfaatkan `v-log-action` untuk menulis ke log aksi Hestia juga

### 14. Observability
- Structured logging (JSON), korelasi request ID
- Metrik: durasi job, jumlah halaman dicek, tingkat kegagalan fetch
- Health check dan error tracking

### 15. Testing & verifikasi
- Unit test untuk logika skoring keputusan (ini logika paling berbahaya kalau salah)
- Integration test terhadap instance HestiaCP uji, bukan produksi
- Fixture data untuk kasus tepi: halaman dengan 1 backlink, halaman dengan traffic 0 tapi 500 backlink, halaman yang 404 lalu hidup lagi
- Verifikasi bahwa aksi benar-benar berubah di server, bukan hanya sukses di level API
- Uji rollback

### 16. DevOps & dokumentasi
- Deploy, backup, rollback
- README: setup, kredensial yang dibutuhkan, cara tambah domain, cara rollback
- Runbook untuk kasus "job mati", "alert tidak masuk", "redirect salah pasang"

## C. Skill khas agent (bukan teknis)

- **Bertanya sebelum berasumsi.** Stack, sumber data backlink, dan cakupan domain harus dikonfirmasi.
- **Pengiriman bertahap** dengan laporan per modul: apa yang jalan, apa yang belum, apa yang butuh keputusan.
- **Read-only dulu, write kemudian.** Semua integrasi eksekusi dimulai dalam mode aman.
- **Jujur soal batas.** Kalau sesuatu tidak bisa (misalnya per-URL redirect lewat API Hestia), katakan, jangan pura-pura bisa.

## D. Matriks: skill mana untuk modul mana

| Skill | Modul 1 | Modul 2 | Modul 3 | Modul 4 | Modul 5 |
|---|---|---|---|---|---|
| HestiaCP API & CLI | sedang | rendah | rendah | **kritis** | sedang |
| Semantik status code | sedang | rendah | sedang | **kritis** | **kritis** |
| Crawling & bot verification | sedang | sedang | **kritis** | rendah | **kritis** |
| Diff & similarity | rendah | **kritis** | **kritis** | rendah | rendah |
| GSC / vendor API | **kritis** | sedang | sedang | sedang | **kritis** |
| Data engineering | **kritis** | **kritis** | **kritis** | **kritis** | **kritis** |
| Pengetahuan SEO | **kritis** | **kritis** | **kritis** | **kritis** | **kritis** |
| Testing logika keputusan | rendah | sedang | sedang | **kritis** | rendah |

## E. Lima skill yang paling sering diremehkan

1. **Semantik 404 vs 410 vs 301.** Salah di sini langsung jadi kerugian nyata, bukan bug kosmetik.
2. **Kesadaran bahwa redirect Hestia itu level-domain.** Tanpa ini, agent akan membangun fitur per-URL yang tidak jalan.
3. **Verifikasi Googlebot lewat DNS.** Kalau asal percaya User-Agent, data crawler-mu bisa dipalsukan dan laporan jadi ngawur.
4. **Idempotensi dan dry-run.** Job harian yang tidak idempoten akan mengeksekusi redirect ganda.
5. **Time-series snapshot.** Kalau data ditimpa, seluruh konsep "dampak sebelum vs sesudah" di modul 2, 3, dan 5 hilang.

## F. Skill yang tidak perlu (biar tidak overengineer)

- Machine learning berat atau LLM fine-tuning
- Kubernetes, service mesh
- Message broker kelas berat (Kafka/RabbitMQ) — Redis atau tabel antrean di database sudah cukup
- Multi-tenant RBAC granular, SSO
- Data warehouse terpisah

## G. Realistis soal siapa yang mengerjakan

Ini sebenarnya gabungan tiga profil: **sysadmin Linux**, **full-stack developer**, dan **SEO teknis**. Satu agent jarang kuat di ketiganya sekaligus. Pembagian yang paling masuk akal:

- Agent utama: orkestrasi, backend, data, HestiaCP
- Manusia: validasi aturan keputusan pruning dan strategi link reclamation, karena di situ pertimbangan SEO tidak bisa sepenuhnya diotomatisasi

---
