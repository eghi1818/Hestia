# REA Deep Lab - Export Hasil Analisis Lengkap

- **Target:** https://wecash.ai/
- **Host:** wecash.ai
- **Dibuat:** 2026-10-22T07:49:57.909Z
- **Cakupan:** 26 seksi (urutan penuh, tanpa PRD)
- **Sifat:** PASIF - read-only, tanpa probing; kredensial tidak termasuk

---

## 1 - DOM & Asset Surface Profiler


### 1 - DOM & Asset Surface Profiler

- Judul: Home -  Wecash
- Bahasa / generator: en / -
- Aset terreferensi: 12 script / 1 stylesheet / 10 img / 0 iframe / 0 form / 1 inline
- Stack terdeteksi: React / Next.js / Express (Next.js)
- Host pihak ketiga: wecash.ai (13)

**Aset yang dianalisis** (13/13 terreferensi)

| Jenis | URL | Status | Ukuran | Waktu |
| --- | --- | --- | --- | --- |
| JS | https://wecash.ai/_next/static/chunks/polyfills-c67a75d1b6f99dc8.js | 200 | 89 KB | 456 ms |
| JS | https://wecash.ai/_next/static/chunks/webpack-bd65c8f53bc5b33a.js | 200 | 4 KB | 269 ms |
| JS | https://wecash.ai/_next/static/chunks/framework-2c79e2a64abdb08b.js | 200 | 138 KB | 277 ms |
| JS | https://wecash.ai/_next/static/chunks/main-81fa9cced5cdea31.js | 200 | 88 KB | 262 ms |
| JS | https://wecash.ai/_next/static/chunks/pages/_app-e75e9954a61875c4.js | 200 | 120 KB | 269 ms |
| JS | https://wecash.ai/_next/static/chunks/664-8af8765c6fed5950.js | 200 | 5 KB | 259 ms |
| JS | https://wecash.ai/_next/static/chunks/769-9e1ba79a71eeac7a.js | 200 | 110 KB | 304 ms |
| JS | https://wecash.ai/_next/static/chunks/250-aee9aa5e16d19e88.js | 200 | 15 KB | 235 ms |
| JS | https://wecash.ai/_next/static/chunks/pages/index-ea96027c59d0b3ce.js | 200 | 9 KB | 267 ms |
| JS | https://wecash.ai/_next/static/fYvk3d2HCCaFDHqB9Hr2n/_buildManifest.js | 200 | 2 KB | 261 ms |
| JS | https://wecash.ai/_next/static/fYvk3d2HCCaFDHqB9Hr2n/_ssgManifest.js | 200 | 1 KB | 261 ms |
| JS | https://wecash.ai/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js | 200 | 1 KB | 250 ms |
| CSS | https://wecash.ai/_next/static/css/a697c4f1186e3e1c.css | 200 | 44 KB | 256 ms |

---

## 1b - Form & Input Analysis

_Tidak ada form pada halaman target (terverifikasi runtime CDP)._

---

## 2 - JavaScript Source Map & Bundle Inspector

| Berkas | Ukuran | Rute | Library | Source map |
| --- | --- | --- | --- | --- |
| polyfills-c67a75d1b6f99dc8.js | 89 KB | 1 | - | tidak dipublikasikan |
| webpack-bd65c8f53bc5b33a.js | 4 KB | 0 | - | tidak dipublikasikan |
| framework-2c79e2a64abdb08b.js | 138 KB | 6 | React | tidak dipublikasikan |
| main-81fa9cced5cdea31.js | 88 KB | 4 | Next.js | tidak dipublikasikan |
| _app-e75e9954a61875c4.js | 120 KB | 3 | - | tidak dipublikasikan |
| 664-8af8765c6fed5950.js | 5 KB | 0 | - | tidak dipublikasikan |
| 769-9e1ba79a71eeac7a.js | 110 KB | 2 | - | tidak dipublikasikan |
| 250-aee9aa5e16d19e88.js | 15 KB | 1 | - | tidak dipublikasikan |
| index-ea96027c59d0b3ce.js | 9 KB | 0 | - | tidak dipublikasikan |
| _buildManifest.js | 2 KB | 0 | - | tidak dipublikasikan |
| _ssgManifest.js | 1 KB | 0 | - | tidak dipublikasikan |
| email-decode.min.js | 1 KB | 0 | - | tidak dipublikasikan |

---

## 3 - Network & API Route Extractor (3a kandidat rute)

- Kandidat rute first-party: 1
- GraphQL: - / WebSocket: -

| Method | Rute | Provenance | Sumber | Validasi |
| --- | --- | --- | --- | --- |
| ANY | /production-error/ | STATIC_CANDIDATE | regex-fallback | UNVALIDATED |

---

## 3b - Endpoint & Payload Matrix

Tidak ada literal payload yang dapat direkonstruksi dari aset publik.

---

## 3c - Third-Party Services Ledger

| Vendor | Kategori | Bukti | File |
| --- | --- | --- | --- |
| Facebook / Meta Pixel | iklan | facebook.com | 2 |

---

## 3d - Runtime Network & Traffic Flow (HAR/CDP Bridge)

- Final URL: https://wecash.ai/
- Requests: 51

**Panggilan API runtime (0)**

| Method | URL | Status | Tipe | Durasi |
| --- | --- | --- | --- | --- |

---

## 3e - Advanced Payload Schema Extractor (nested <=2)

Tidak ada skema yang dapat direkonstruksi.

---

## 3f - Infrastructure & CDN Gateway Fingerprint

- Edge / CDN: Cloudflare (confidence high)
- Bukti header: cf-ray: a4e6e309eb621057-HKG (POP HKG); server: cloudflare; penanda /cdn-cgi/ pada HTML
- Server software: cloudflare
- X-Powered-By / Via: Next.js

| Host | Vendor (dugaan) | Brand/Platform | Klasifikasi | Req | Bytes | Jenis |
| --- | --- | --- | --- | --- | --- | --- |
| wecash.ai | - | - | utama (same-site) | 63 | 625 KB | js,css |
| fonts.gstatic.com | Google | - | pihak ketiga (belum teridentifikasi) | 1 | 1 KB | - |

---

## 3h - Engine / Platform Attribution

_Tidak ada brand platform teridentifikasi dari host aset pada scan ini._

---

## 3i - Engine Backbone (pasif, evidence-based)

- Label: tidak terdeteksi dari sumber pasif
- Sumber diperiksa: runtime (CDP) + landing + aset JS / request runtime: 51 / aset JS: 0 / HTML: 29355 bytes

---

## 3j - Architecture Blueprint (Advanced Expansion, pasif)

- Runtime CDP: DIGABUNG

**Software Composition Analysis (SCA)**

| Pustaka | Versi | Status | Advisory (NVD NIST) |
| --- | --- | --- | --- |
| jQuery | ? | versi tidak terbaca — advisory disajikan sebagai referensi | CVE-2020-11022 (medium), CVE-2020-11023 (medium) |
| axios | ? | versi tidak terbaca — advisory disajikan sebagai referensi | CVE-2020-28168 (high), CVE-2023-45857 (medium) |
| lodash | ? | versi tidak terbaca — advisory disajikan sebagai referensi | CVE-2019-10744 (high), CVE-2020-8203 (high) |
| Bootstrap | ? | versi tidak terbaca — advisory disajikan sebagai referensi | CVE-2019-8331 (medium), CVE-2024-6531 (medium) |
| moment.js | ? | versi tidak terbaca — advisory disajikan sebagai referensi | CVE-2022-24785 (high), CVE-2022-31129 (medium) |
| AngularJS (1.x) | ? | versi tidak terbaca — advisory disajikan sebagai referensi | CVE-2022-25844 (medium), CVE-2024-21490 (medium) |

0 dari 6 pustaka diberi flag PERIKSA (pola versi) — referensi advisory publik, bukan hasil pengujian aktif

**Authentication & Session Lifecycle**

| Aspek | Temuan | Catatan |
| --- | --- | --- |
| Tipe token | opaque/session (tidak teramati eksplisit) | tidak ada pola token eksplisit — kemungkinan session cookie server-side |

**Administrative & Back-Office Discovery (pasif)**

Tidak ada path administratif terreferensi (REA tidak menebak / tanpa probing).

Pasif murni: hanya path yang terreferensi di kode/HTML atau teramati di runtime. TANPA probing/brute-force path — tebakan direktori tidak dilakukan dan tidak akan dilakukan REA.

**Technology Stack & Framework**

| Platform | Sumber | Bukti |
| --- | --- | --- |
| Next.js (Node SSR) | HTML/header | artefak _next |
| Cloudflare Pages/Workers (edge) | header | cf-ray: a4e6e309eb621057-HKG |

**Runtime API Transaksional (CDP)**

Tidak ada endpoint transaksional teramati pada sesi satu halaman.

Endpoint POST/PUT/PATCH/DELETE/XHR teramati saat runtime CDP — struktur payload berupa NAMA key saja (nilai tidak direkam); respKeys = key level-1 respons JSON.

**Sensitive Artifact & Source Map Exposure**

- Source map terreferensi: 0 / terunduh saat scan: 0 / total sumber terbuka: 0

Semua 7 modul PASIF; advisory CVE = referensi yang butuh konfirmasi manual.

---

## 3g - Structured Intelligence Matrix (intelligence-matrix-1.0)

| Aspek | Temuan | Bukti | Provenance | Catatan |
| --- | --- | --- | --- | --- |
| Edge / CDN | Cloudflare | cf-ray: a4e6e309eb621057-HKG (POP HKG) · server: cloudflare · penanda /cdn-cgi/ pada HTML | OBSERVED | kemungkinan besar Cloudflare menopang trafik edge |
| Gateway / server software | cloudflare · Next.js | server: cloudflare · x-powered-by: Next.js | OBSERVED | - |
| CDN aset pihak ketiga | tidak ada vendor dikenali | — | OBSERVED | 1 host aset total |
| Rute API (statis) | 1 kandidat first-party | AST/regex atas 12 berkas JS | STATIC_CANDIDATE | - |
| Pola payload (statis) | 0 pola unik | — | STATIC_CANDIDATE | skema nested ≤2 level; validasi tetap di server |
| Framework / stack | React · Next.js · Express (Next.js) | DOM + header + pola bundle | STATIC_CANDIDATE | - |
| Header keamanan | grade D (0/100) | evaluasi 10 header · skala tunggal pass/(pass+fail)×100 | OBSERVED | unknown = NOT TESTED, tidak menghukum |
| Cookie respons utama | 0 Set-Cookie | — | OBSERVED | - |
| Third-party SDK | 1 vendor | Facebook / Meta Pixel | STATIC_CANDIDATE | - |
| CORS / lintas-origin | CORS header respons utama: tidak ada (normal utk halaman, bukan API) · Frame embedding: bebas di-embed · Stylesheet lintas-origin: tidak ada · Iframe lintas-origin: tidak ada | tanpa ACAO | OBSERVED | - |

---

## 4 - Security Score Model (multi-kategori, transparan)

Interpretasi WAJIB: null = NOT TESTED (butuh alat/sesi lain) - BUKAN 0 risiko.

| Kategori | Score | Pass | Fail | Unknown | Not tested |
| --- | --- | --- | --- | --- | --- |
| Header Configuration | 0/100 | 0 | 7 | 3 | 0 |
| Application Security Tests | NOT TESTED | 0 | 0 | 0 | 6 |
| API Coverage (bukan skor keamanan) | 0/100 | 0 | 0 | 0 | 1 |
| Infrastructure Coverage | 50/100 | 1 | 0 | 1 | 2 |
| Evidence Quality | 100/100 | 19 | 0 | 0 | 0 |
| Scope/Safety Compliance | 100/100 | 3 | 0 | 0 | 0 |

**Detail per kategori**

### Header Configuration - pass / (pass+fail) × 100 — unknown = NOT TESTED, tidak menghukum; skala TUNGGAL sama dengan grade 4a

| Check | Status | Detail |
| --- | --- | --- |
| STRICT-TRANSPORT-SECURITY-HS | fail | tidak ada pada respons HTTPS |
| CONTENT-SECURITY-POLICY | fail | tidak ada |
| KLIKJACKING-DEFENSE-XFO-FRAM | fail | tidak ada |
| X-CONTENT-TYPE-OPTIONS | fail | tidak ada |
| REFERRER-POLICY | fail | tidak ada |
| PERMISSIONS-POLICY | unknown | tidak ada (opsional) |
| COOP-COEP-ISOLATION | unknown | tidak ada (opsional) |
| SERVER-BANNER | fail | terekspos: cloudflare |
| X-POWERED-BY | fail | terekspos: Next.js |
| COOKIE-FLAGS-HTTPONLY-SECURE | unknown | tidak ada cookie pada respons utama |

Keterbatasan: hanya header respons halaman tunggal; kehadiran header ≠ efektivitas konfigurasi

### Application Security Tests - null — NOT TESTED; jangan ditafsirkan 0 risiko

| Check | Status | Detail |
| --- | --- | --- |
| AUTH-BYPASS | not_tested | butuh sesi + approval + tool aktif (tidak terpasang) |
| IDOR | not_tested | butuh akun uji terotorisasi |
| INJECTION | not_tested | di luar mode pasif |
| UPLOAD | not_tested | di luar mode pasif |
| RATELIMIT | not_tested | stability probe ≠ pengujian rate-limit |
| SESSFIX | not_tested | butuh sesi terautentikasi |

Keterbatasan: seluruh kategori BELUM DIUJI

### API Coverage (bukan skor keamanan) - ast_verified_calls / static_candidates × 100

| Check | Status | Detail |
| --- | --- | --- |
| STATIC-CAND | info | 1 kandidat (STATIC_CANDIDATE) |
| AST-VER | info | 0 panggilan |

Keterbatasan: coverage ≠ keamanan

### Infrastructure Coverage - heuristik kedalaman info edge

| Check | Status | Detail |
| --- | --- | --- |
| WAF-EDGE | pass | Cloudflare |
| TLS-CERT | not_tested | butuh cert analyzer |
| DNS | not_tested | di luar cakupan pasif |

Keterbatasan: pasif hanya melihat yang diumumkan respons

### Evidence Quality - seksi output ber-provenance / total seksi

| Check | Status | Detail |
| --- | --- | --- |
| PROVENANCE | pass | 19 seksi berlabel |
| REDACTION | pass | 3 temuan kredensial ter-audit |

### Scope/Safety Compliance - kepatuhan mode pasif

| Check | Status | Detail |
| --- | --- | --- |
| SCOPE | pass | validateScope dipanggil sebelum fetch target |
| PASSIVE | pass | tanpa login/transaksi — selamanya |
| KILL | pass | control plane /api/kill-switch |

---

## 4a - Security Header & WAF Posture (detail OBSERVED)

**Header keamanan** (grade D / 0/100):

| Header | Status | Detail |
| --- | --- | --- |
| Strict-Transport-Security (HSTS) | perlu perhatian | tidak ada pada respons HTTPS |
| Content-Security-Policy | perlu perhatian | tidak ada |
| Klikjacking defense (XFO / frame-ancestors) | perlu perhatian | tidak ada |
| X-Content-Type-Options | perlu perhatian | tidak ada |
| Referrer-Policy | perlu perhatian | tidak ada |
| Permissions-Policy | n/a | tidak ada (opsional) |
| COOP/COEP isolation | n/a | tidak ada (opsional) |
| Server banner | perlu perhatian | terekspos: cloudflare |
| X-Powered-By | perlu perhatian | terekspos: Next.js |
| Cookie flags (HttpOnly/Secure/SameSite) | n/a | tidak ada cookie pada respons utama |

**WAF / Edge & Cookie**

- Vendor: Cloudflare (terdeteksi)
- Tidak ada Set-Cookie pada respons utama

---

## 4a-2 - Cross-Origin Resource & CORS Posture

| Aspek | Status | Detail |
| --- | --- | --- |
| CORS header respons utama | tidak ada (normal utk halaman, bukan API) | tidak ada header Access-Control-* pada dokumen utama |
| Frame embedding | bebas di-embed | tanpa XFO/frame-ancestors — halaman bisa di-iframe pihak lain |
| Stylesheet lintas-origin | tidak ada | semua CSS same-origin |
| Iframe lintas-origin | tidak ada | tidak ada iframe eksternal di HTML |

Blokiran CORB/ORB = indikasi konfigurasi header pihak eksternal tidak selaras (observasi pasif, bukan galat engine).

---

## 4a-3 - Frontend Form Hygiene

_Tidak ada field password pada halaman ini._

---

## 4b - Authentication Flow & Token Inspector

_Alur login tidak teridentifikasi pada scan pasif ini._

---

## 4c - Static Credential & Plain-Text Storage Audit

| Rule | Severity | Temuan | Lokasi |
| --- | --- | --- | --- |
| hardcoded-credential | high | token = "${v}…(len 4, ekspresi)" | 769-9e1ba79a71eeac7a.js:24 |
| hardcoded-credential | high | token = "${c}…(len 4, ekspresi)" | 769-9e1ba79a71eeac7a.js:24 |
| hardcoded-credential | high | token = "${n}…(len 4, ekspresi)" | 769-9e1ba79a71eeac7a.js:24 |

Severity = dampak teknis pola; confidence = kualitas bukti; nilai selalu dimasked.

---

## 4d - Secret Candidates (Context-Aware)

_Tidak ada kandidat secret pada scan ini._

---

## 0 - Intel Manifest (target-intel-manifest/v1 — TTL & deteksi intel basi)

| Field | Nilai |
|---|---|
| skema | target-intel-manifest/v1 (version 1) |
| target / host | https://wecash.ai/ / wecash.ai |
| generated_at | 2026-10-22T07:46:17.543Z |
| ttl | 60 menit → expires 2026-10-22T08:46:17.543Z |
| status saat dibaca | FRESH (4 menit) |
| cakupan | passive single-page + referenced assets (+ runtime bila diaktifkan) |

Intel lebih tua dari TTL dianggap BASI — re-scan sebelum dipakai keputusan. TTL bukan jaminan kebaruan konten (cache edge bisa lebih tua).

---

## 0b - Target Layers (DNS → edge → origin → app)

Pemetaan lapisan agar verdict tidak salah alamat:

| Lapisan | Teramati | Bukti |
| --- | --- | --- |
| DNS / resolusi | tidak di-query aktif (subdomain finder memakai database publik, bukan DNS lookup ke target) | — |
| Edge / CDN / WAF | Cloudflare | cf-ray: a4e6e309eb621057-HKG (POP HKG); server: cloudflare; penanda /cdn-cgi/ pada HTML |
| Origin / server software | cloudflare · Next.js | — |
| Aplikasi / frontend | React · Next.js | DOM + aset JS + pola bundle |

**Pemetaan verdict → lapisan:**
- temuan header keamanan / CORS / cookie → lapisan EDGE atau ORIGIN (bukan otomatis "aplikasinya bermasalah")
- temuan rute / payload / secret / form → lapisan APP
- temuan TLS / sertifikat → butuh analyzer khusus (NOT TESTED)

---

## Tab: CDP Live - Request terekam

- Final URL: https://wecash.ai/
- Requests: 45 / WS: 0 / Console: 0 / Durasi: 2.76 s

| Method | URL | Status | Tipe | Payload |
| --- | --- | --- | --- | --- |
| GET | https://wecash.ai/ | 200 | document | - |
| GET | https://wecash.ai/_next/image/?url=%2Fassets%2Fimages%2Flanding%2Fheader%2Fpolkadot.png&w=750&q=75 | 200 | image | - |
| GET | https://wecash.ai/_next/image/?url=%2Fassets%2Fvideos%2Fwebp%2Fheader2.webp&w=750&q=75 | 200 | image | - |
| GET | https://wecash.ai/_next/static/css/a697c4f1186e3e1c.css | 200 | stylesheet | - |
| GET | https://wecash.ai/_next/static/chunks/webpack-bd65c8f53bc5b33a.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/framework-2c79e2a64abdb08b.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/main-81fa9cced5cdea31.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/pages/_app-e75e9954a61875c4.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/664-8af8765c6fed5950.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/769-9e1ba79a71eeac7a.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/250-aee9aa5e16d19e88.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/pages/index-ea96027c59d0b3ce.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/fYvk3d2HCCaFDHqB9Hr2n/_buildManifest.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/fYvk3d2HCCaFDHqB9Hr2n/_ssgManifest.js | 200 | script | - |
| GET | https://wecash.ai/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js | 200 | script | - |
| GET | https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7W0Q5nw.woff2 | 200 | font | - |
| GET | https://wecash.ai/assets/images/landing/wecash-logo-new.svg | 200 | image | - |
| GET | https://wecash.ai/assets/icons/landing/arrow-right.svg | 200 | image | - |
| GET | https://wecash.ai/_next/image/?url=%2Fassets%2Fimages%2Flanding%2Fheader%2Frect.png&w=750&q=75 | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/coretan.svg | 200 | image | - |
| GET | https://wecash.ai/assets/icons/landing/flash.svg | 200 | image | - |
| GET | https://wecash.ai/assets/icons/landing/discount-shape.svg | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/wecash-logo-footer.svg | 200 | image | - |
| GET | https://wecash.ai/_next/static/chunks/122.86ffa8edfccea5aa.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/910.188ab390722e4ea6.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/507.7bd48b6760f14111.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/637.17265ea30be90f45.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/480.b34948622088f644.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/780.fe644e47a627af5c.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/152.6f05f2727e3ec134.js | 200 | script | - |
| GET | https://wecash.ai/_next/static/chunks/pages/qris-134d8f27ac4c9376.js | 200 | other | - |
| GET | https://wecash.ai/_next/image/?url=%2Fassets%2Fvideos%2Fwebp%2Fmaps2.webp&w=750&q=75 | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/pembayaran/polkadot.svg | 200 | image | - |
| GET | https://wecash.ai/_next/image/?url=%2Fassets%2Fvideos%2Fgif%2Fphone.gif&w=640&q=75 | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/partner/gopay-color.svg | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/partner/mandiri-color.svg | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/partner/bca-color.svg | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/partner/bni-color.svg | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/partner/bri-color.svg | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/partner/cimb-color.svg | 200 | image | - |
| GET | https://wecash.ai/_next/static/chunks/pages/qris-134d8f27ac4c9376.js | 200 | script | - |
| GET | https://wecash.ai/assets/images/landing/pembayaran/one.svg | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/pembayaran/two.svg | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/pembayaran/three.svg | 200 | image | - |
| GET | https://wecash.ai/assets/images/landing/pembayaran/four.svg | 200 | image | - |

---

## Tab: Stabilitas & Rate-Limit (termasuk Detail per probe)

- Target: https://wecash.ai/ / probe: 30/30
- Stability Index: 100 (stabil) - error/backpressure(40) / jitter(30) / ok-rate(15) / sinyal rate-limit(-20)
- Latensi min/median/p95/max: 333 / 339 / 368 / 888 ms
- Jitter (p95-median): 555 ms (rasio 0.09, noise-level)
- Error/backpressure: 0 error (0%) / 0 backpressure
- Status code: 200x30
- Header rate-limit server: tidak ada (server tidak mengumumkan kuota)
- Durasi: 37.07 s

**Detail per probe**

| # | Waktu (WIB) | ms | Status | RateLimit remaining | Catatan |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-10-22 14:48:39 WIB | 888 | 200 | - | ok |
| 2 | 2026-10-22 14:48:41 WIB | 364 | 200 | - | ok |
| 3 | 2026-10-22 14:48:42 WIB | 338 | 200 | - | ok |
| 4 | 2026-10-22 14:48:44 WIB | 368 | 200 | - | ok |
| 5 | 2026-10-22 14:48:45 WIB | 349 | 200 | - | ok |
| 6 | 2026-10-22 14:48:46 WIB | 342 | 200 | - | ok |
| 7 | 2026-10-22 14:48:47 WIB | 336 | 200 | - | ok |
| 8 | 2026-10-22 14:48:49 WIB | 354 | 200 | - | ok |
| 9 | 2026-10-22 14:48:50 WIB | 342 | 200 | - | ok |
| 10 | 2026-10-22 14:48:51 WIB | 355 | 200 | - | ok |
| 11 | 2026-10-22 14:48:52 WIB | 337 | 200 | - | ok |
| 12 | 2026-10-22 14:48:54 WIB | 359 | 200 | - | ok |
| 13 | 2026-10-22 14:48:55 WIB | 336 | 200 | - | ok |
| 14 | 2026-10-22 14:48:56 WIB | 335 | 200 | - | ok |
| 15 | 2026-10-22 14:48:57 WIB | 335 | 200 | - | ok |
| 16 | 2026-10-22 14:48:59 WIB | 337 | 200 | - | ok |
| 17 | 2026-10-22 14:49:00 WIB | 337 | 200 | - | ok |
| 18 | 2026-10-22 14:49:01 WIB | 352 | 200 | - | ok |
| 19 | 2026-10-22 14:49:02 WIB | 360 | 200 | - | ok |
| 20 | 2026-10-22 14:49:04 WIB | 350 | 200 | - | ok |
| 21 | 2026-10-22 14:49:05 WIB | 339 | 200 | - | ok |
| 22 | 2026-10-22 14:49:06 WIB | 337 | 200 | - | ok |
| 23 | 2026-10-22 14:49:07 WIB | 333 | 200 | - | ok |
| 24 | 2026-10-22 14:49:08 WIB | 341 | 200 | - | ok |
| 25 | 2026-10-22 14:49:10 WIB | 337 | 200 | - | ok |
| 26 | 2026-10-22 14:49:11 WIB | 344 | 200 | - | ok |
| 27 | 2026-10-22 14:49:12 WIB | 334 | 200 | - | ok |
| 28 | 2026-10-22 14:49:13 WIB | 338 | 200 | - | ok |
| 29 | 2026-10-22 14:49:15 WIB | 337 | 200 | - | ok |
| 30 | 2026-10-22 14:49:16 WIB | 337 | 200 | - | ok |

Probe read-only low-rate untuk mengukur stabilitas respons — BUKAN load/stress test. INDIKATOR, bukan verdict. Trigger point rate-limit hanya teramati jika server mengirim 429/503 atau header rate-limit.

---

## Tab: Subdomain Finder - 5 Database Publik (pasif)

- Host: wecash.ai / total: 3 subdomain / wildcard: 2
- Sumber: crt.sh ok(145), RapidDNS ok(0), urlscan.io ok(0), Wayback gagal(This operation was aborted), HackerTarget ok(1)

| Hostname | Tipe | Sumber |
| --- | --- | --- |
| dev.wecash.ai | sub | hackertarget |
| wecash.ai | apex | ct-logs |
| www.wecash.ai | sub | ct-logs |

Wildcard tercatat: *.dev.wecash.ai, *.wecash.ai

Pasif murni (5 database publik); hasil = riwayat, belum tentu aktif hari ini.

---

## Tab: Signature Pack Terpasang

| Pack ID | Kategori | Versi | Pattern | Update terakhir |
| --- | --- | --- | --- | --- |
| auth-patterns | auth | 1.0.0 | 11 | 2026-10-11 |
| bank-va-id | payment | 1.0.0 | 17 | 2026-10-11 |
| common-library-noise | noise-filter | 1.0.0 | 15 | 2026-10-11 |
| emvco-qris | payment | 1.0.0 | 10 | 2026-10-11 |
| gambling-id | gambling | 1.0.0 | 10 | 2026-10-11 |
| gateways-legal-chain | payment | 1.0.0 | 8 | 2026-10-11 |
| payment-gateways-id | payment | 1.0.0 | 19 | 2026-10-11 |

---
