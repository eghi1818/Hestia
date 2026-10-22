# RENCANA TANAM - HESTIA

Dibuat dari basis pada langkah S-76. Diurutkan: **tanpa penjaga lebih dulu**, lalu skor.

Sumber: 25 situs akar hidup, bersih (bukan infra, bukan halaman kosong).

| # | Domain | Akhiran | HTTP | Server | Penjaga | Skor | Sudah jadi target |
|---|---|---|---|---|---|---|---|
| 1 | `badungkab.go.id` | go.id | 200 | Apache/2.4.29 (Ubuntu) | — | 88 | — |
| 2 | `baliprov.go.id` | go.id | 200 | — | — | 88 | ya |
| 3 | `bandung.go.id` | go.id | 200 | — | — | 88 | ya |
| 4 | `bulelengkab.go.id` | go.id | 200 | nginx/1.24.0 (Ubuntu) | — | 88 | — |
| 5 | `akademi-tni.mil.id` | mil.id | 200 | Apache | — | 83 | — |
| 6 | `balog-tni.mil.id` | mil.id | 200 | Apache | — | 83 | — |
| 7 | `1004korea.ac.id` | ac.id | 200 | hcdn | — | 78 | — |
| 8 | `3cil.sch.id` | sch.id | 200 | nginx | — | 78 | ya |
| 9 | `45mataram.ac.id` | ac.id | 200 | — | — | 78 | — |
| 10 | `a2b.ac.id` | ac.id | 200 | Apache/2 | — | 78 | — |
| 11 | `aa-yai.ac.id` | ac.id | 200 | Microsoft-IIS/10.0 | — | 78 | — |
| 12 | `aabs.sch.id` | sch.id | 200 | LiteSpeed | — | 78 | — |
| 13 | `aaiibs.sch.id` | sch.id | 200 | Apache/2.4.57 (Unix) OpenSSL/1.0.2k-fips | — | 78 | — |
| 14 | `akpol.ac.id` | ac.id | 200 | Apache | — | 78 | — |
| 15 | `untemungkur-tapanuliutara.desa.id` | desa.id | 200 | Apache/2.4.52 (Ubuntu) | — | 73 | — |
| 16 | `unterudang.desa.id` | desa.id | 200 | Apache/2.4.52 (Ubuntu) | — | 73 | — |
| 17 | `urungpane.desa.id` | desa.id | 200 | Apache/2.4.52 (Ubuntu) | — | 73 | — |
| 18 | `urutsewu.desa.id` | desa.id | 200 | Apache/2.4.52 (Ubuntu) | — | 73 | — |
| 19 | `walahar.desa.id` | desa.id | 200 | Apache/2.4.52 (Ubuntu) | — | 73 | — |
| 20 | `waluya-cikarangutara.desa.id` | desa.id | 200 | Apache | — | 73 | — |
| 21 | `waluyojati.desa.id` | desa.id | 200 | LiteSpeed | — | 73 | — |
| 22 | `wanadadi-banjarnegara.desa.id` | desa.id | 200 | Apache/2.4.52 (Ubuntu) | — | 73 | — |
| 23 | `wanadadi.desa.id` | desa.id | 200 | hcdn | — | 73 | — |
| 24 | `wanakarsa-wanadadi.desa.id` | desa.id | 200 | Apache/2.4.52 (Ubuntu) | — | 73 | — |
| 25 | `banglikab.go.id` | go.id | 200 | cloudflare | cloudflare | 93 | — |

## Cara memakai

1. Ambil satu baris dari **atas** daftar — yang tanpa penjaga dan servernya biasa
   (Apache/nginx) paling mudah ditanami.
2. Buka domainnya, cari jalur yang bisa ditulis (mis. `/tamu/`, `/blog/`, `/berita/`).
3. Catat di dashboard: **Deployment -> Deploy baru** (mengisi tabel konten sekaligus).
4. Isi **Kredensial** bila aksesnya sudah didapat.
5. Tunggu 1-2 minggu, lalu periksa apakah halaman terindeks di mesin pencari.

## Catatan

- Situs **berpenjaga** (cloudflare dll) tetap layak, hanya perlu jalur akses lain.
- Prioritaskan domain dengan halaman yang **sudah lama** ada dan banyak tautan masuk
  — cek kolom penerima di halaman Backlink.
- Jangan menanam di banyak domain sekaligus di awal; satu dulu sampai terbukti.
