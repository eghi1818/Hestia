Jawaban langsung: **kendalanya bukan investigasi, tapi tiga kredensial yang belum pernah ada.** Kerja lokal sudah habis.

## Kendala sebenarnya

| Target | Yang menghalangi | Yang persisnya dibutuhkan |
|---|---|---|
| `juraganit.com` | Pure-FTPd mode TLS, anonymous rusak, port 22 ditutup | **satu baris `user:sandi` FTP** dari panel liqu.id |
| `waspadaweb.com` | web root `root:root`, `sudo` minta sandi, `wesearch` hanya di grup `users` | **satu sandi sudo** (atau izin masuk sebagai root) |
| `persaudaraan.com` | nama `*.netlify.app` tidak ada di DNS — `www` tanpa CNAME, TXT kosong, NS di parking Hostinger | **nama site dari dashboard Netlify**, atau token API |

Tiga tebakan `netlify.app` gagal (semua 404). Nama itu hanya tersimpan di akun Netlify Anda — tidak bisa dibaca dari DNS.

## Kenapa terasa muter-muter

Dua sebab, dua-duanya nyata:

1. **Kredensial** — sejak awal `NEXT.md` sudah menulis tiga kunci ini sebagai "menunggu kunci". Selama belum dikirim, semua yang bisa dikerjakan cuma yang tidak butuh akses.
2. **Cara saya** — tiap langkah saya sisipkan babak recon sendiri, jadi 2-3 tempelan per langkah. Itu yang bikin lambat. Sudah saya kurangi sejak S-162.

## Yang sudah selesai (lokal, semua ter-push)

S-152 bug `_tambah` · S-153 migrasi masuk repo + cache kolom segar · S-154 WAL · S-155 sinkron SESSION_STATE · S-156 retensi cadangan · S-157 pemeriksa placeholder di gate · S-158–S-160 koreksi jejak · S-161 penyaring Audit Log · S-162 hapus kedipan demo · S-163 retensi clientlog.

Yang tersisa di lokal cuma **persiapan LIVE**: naikkan `HESTIA_SANDI`, jadikan `serve.sh` layanan, HTTPS. Semua butuh host dulu.

## Dua perbaikan probe (satu blok, read-only)

Satu salah saya: `grep -r` tidak mengikuti symlink, jadi konfigurasi nginx `waspadaweb.com` tidak terbaca. Dan `ftp` CLI sudah dihapus dari macOS — harus `curl --ftp-ssl`.

```bash
cd /Users/eghi/Documents/REPO/Hestia
export GIT_PAGER=cat

echo "=== waspadaweb: nginx ikuti symlink + cek yang bisa ditulis ==="
ssh -i ~/.ssh/wesearch_vps_key -p 10053 -o BatchMode=yes -o ConnectTimeout=8 wesearch@93.127.133.160 '
  grep -Rhn "server_name\|root \|listen " /etc/nginx/sites-enabled/ 2>/dev/null | head -20
  echo "--- izin ---"; ls -ld /var/www /var/www/waspadaweb
  echo "--- writable di /var/www ---"; find /var/www -maxdepth 2 -writable 2>/dev/null | head
  echo "--- nginx ---"; nginx -v 2>&1
'

echo "=== juraganit: FTP anonymous pakai TLS ==="
curl -sS --max-time 12 --ftp-ssl-reqd -u anonymous:anonymous --list-only ftp://juraganit.com/ 2>&1 | head -10

echo "=== persaudaraan: brute nama lain ==="
for n in persaudaraan persaudaraan-com persaudaraanweb persaudaraan-org persaudaraan-ai; do
  c=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 "https://$n.netlify.app" 2>/dev/null)
  echo "$n.netlify.app -> $c"
done
```

## Yang saya butuh — tiga baris saja

1. **FTP `juraganit.com`**: `user:sandi` dari panel liqu.id
2. **Sudo `waspadaweb.com`**: sandi untuk `wesearch` — atau bilang "pakai root" kalau ada akses root
3. **Netlify `persaudaraan.com`**: nama site-nya (mis. `sesuatu.netlify.app`)

Kirim ketiganya (atau satu-satu), dan tiap satu langsung saya kerjakan jadi satu blok: tanam → uji → bukti → commit. Tanpa babak recon lagi.