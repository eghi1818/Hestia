# Strategi Tanam Hestia

Tidak ada satu pintu yang berlaku untuk semua situs. Hestia memilih kanal dari tangga,
dari yang paling ringan ke paling berat. Kanal dicoba berurutan; yang pertama berhasil dipakai.

| Tingkat | Kanal | Butuh apa |
|---|---|---|
| 0 | kolom komentar, buku tamu, registrasi terbuka | tanpa akun |
| 1 | CMS admin: `/wp-login.php`, `/administrator/`, `/user/login` | user + sandi |
| 2 | berkas server: FTP/FTPS, panel | kredensial hosting |
| 3 | pipa deploy: git push, deploy hook | akses repo |
| 4 | tepi: Worker/Snippet | akun CDN |

Catatan penting: **Cloudflare bukan tembok.** Cloudflare hanya menyembunyikan IP asli.
`/wp-login.php` tetap bisa diakses lewat Cloudflare di port 443. Yang butuh IP asli hanya
tingkat 2, karena Cloudflare tidak mem-proxy port 21/22.

## Alat di Hestia

- `tools/pintu.py` — peta pintu tulis sebuah domain
- `tools/kanal.py` — pilih tingkat kanal
- `tools/teknologi.py` — deteksi program/CMS/WAF tiap target
- `tools/hosting.py` — cari penyedia + repo sumber
- `tools/asal.py` — cari server asli di balik CDN
- `tools/jejak.py` — riwayat DNS + favicon-hash
- `tools/tanam.py` — jalankan kanal (PUT tanpa kredensial, lalu FTP)

## Status uji

| Situs | Kanal | Status | Penghalang |
|---|---|---|---|
| juraganit.com | FTP (port 21) | pintu terbuka | anonymous rusak, butuh sandi FTP |
| waspadaweb.com | SSH ke VPS | SSH tembus | `/var/www/waspadaweb` milik root |
| persaudaraan.com | Netlify | belum | nama `*.netlify.app` belum ketemu |
