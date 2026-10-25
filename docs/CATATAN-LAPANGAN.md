# Catatan lapangan

Temuan nyata saat uji, supaya tidak diulang.

## S-220/F-3b -- Cloudflare menolak User-Agent bawaan python
Berkas penanda di docroot: mode 644 root:root, docroot 755. curl -I publik -> 200
(content-length 52, server: cloudflare). Tetapi pembaca python dengan UA bawaan
"Python-urllib/3.9" mendapat 403.
Kesimpulan: baca dari luar WAJIB memakai User-Agent yang wajar. tools/jalur.py memakai
HESTIA_UA (bawaan: Mozilla/5.0 (Hestia uji-jalur) Hestia/1.0).
Dugaan awal (mode berkas 600) SALAH -- dibuktikan dengan ls -l.

## S-220 -- di dalam container, nginx host ada di /mnt/host/etc/nginx
Container tidak melihat /etc/nginx milik host. Yang benar: /mnt/host/etc/nginx/...
Root docroot terkonfirmasi: /var/www/waspadaweb (baris 7 pada sites-available).
Aturan driver terlihat di conf: /artikel/lama -> 301, /halaman-mati -> 410.

## S-219/F-3 -- jalur J5 bisa menulis
ssh -> lxc exec hx -> tulis ke /mnt/host/var/www/... berhasil (rc 0).
Tulis jalan tanpa sudo; rantai "lxc" dipakai, "sudo-lxc" cadangan.
