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

## S-223 -- reload nginx harus lewat HOST langsung
Empat kandidat lewat "lxc exec hx -- ..." semuanya gagal. Yang bekerja:
  sudo nginx -t && sudo nginx -s reload        (dijalankan via ssh ke host, bukan lewat lxc)
driver.py sudah memakai pola ini di _ssh_host/_coba; _ssh_ct hanya untuk menyentuh
/mnt/host. Pelajaran: baca dulu mesin yang sudah ada sebelum menulis kandidat baru.

## S-227 -- dua jebakan di tools/ganti.py (F-8 percobaan 1)
1. tools/bunuh.baca() mengembalikan INT (status saja). ganti.py memanggilnya sebagai
   B.baca(url)[1] -> TypeError, sehingga verifikasi penanda dan pencatatan change_event/bukti
   tidak jalan. Perbaikan: tambah bunuh.baca_penuh() -> (status, badan); baca() tetap int.
2. pulih() memotret isi SAAT INI lalu menulisnya kembali, jadi rollback tidak mengembalikan
   isi lama. Perbaikan: snapshot diambil saat pasang dan namanya disimpan di
   change_event.nilai_lama; pulih membacanya dari situ.

## S-234 -- Cloudflare menyuntik HTML, badan mentah beda antar vantage
Ekspor bukti pertama: status lokal dan VPS sama-sama 200, tetapi sha256 badan BERBEDA
(panjang 482 bita padahal berkas kita ~120). Cloudflare menambahkan elemen ke HTML.
Pelajaran: bandingkan badan TERNORMALISASI (spasi dirapatkan) + penanda, jangan badan mentah.
tools/bukti_ekspor.py kini mencatat cocok_mentah, cocok_normal, dan status_sama.

## S-239 -- port 8791 tertutup dari luar; pakai port 80 dengan server_name = IP
Uji luar ke 8791 membalas 000 walau ufw sudah mengizinkan, jadi penutupnya ada di depan
(provider). Solusi: vhost tambahan di port 80 dengan server_name 93.127.133.160 sehingga
permintaan ke IP jatuh ke Hestia, sedangkan waspadaweb.com tetap ke vhost-nya (exact match
server_name menang atas default_server). Berkas: deploy/nginx-hestia-ip.conf.

## S-239 -- DB di VPS adalah SALINAN, bukan kanonik
Repo di-rsync ke /opt/hestia termasuk data/hestia.db. Sampai ada sinkronisasi, DB di laptop
adalah sumber kebenaran dan DB di VPS bisa menyimpang. Catat sebagai butir lanjutan.

## S-240 -- server_name = IP tidak menang; pakai vhost default
Menambah vhost dengan server_name = IP TIDAK cukup: permintaan ke IP tetap dilayani vhost
"default" (bukti: dari VPS balas 200 tanpa sandi, dari laptop 404). Yang bekerja: jadikan
vhost default sebagai proxy ke 127.0.0.1:8787. Salinan asli dicadangkan di
/etc/nginx/sites-available/default.orig.
