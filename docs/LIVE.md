# Hestia hidup 24/7

## Pasang
    bash tools/live.sh pasang          # HTTP, sandi acak 32 heksa
    bash tools/live.sh pasang --tls    # + HTTPS self-signed

Agen launchd `id.hestia.serve` dijalankan saat login dan dijaga hidup (`KeepAlive`).
Sandi disimpan HANYA di `~/.hestia/live.env` (mode 600) sehingga tidak ikut repo publik.

## Periksa / ganti / lepas
    bash tools/live.sh status
    bash tools/live.sh sandi-baru
    bash tools/live.sh hapus

## Catatan
- Alamat: `http://127.0.0.1:8787` (atau `https://` bila `--tls`). Sertifikat self-signed
  sehingga peramban memperingatkan; itu wajar untuk localhost.
- "24/7" berarti Mac tidak tidur. Bila perlu: `caffeinate -s` atau atur Energy Saver.
- Sertifikat publik sungguhan butuh domain mengarah ke Mac. Sudah ada agen
  `com.wesearch.tunnel.plist` (Cloudflare Tunnel) yang bisa dipakai untuk itu.
- `tools/serve.sh` tetap jalur terminal dan kini ikut membaca `~/.hestia/live.env`.
- Log layanan: `~/.hestia/serve.log`.

## Kalau layanan mati dengan "Operation not permitted"
Repo berada di `~/Documents`, dan macOS menutup folder itu bagi proses yang dijalankan
launchd. Gejalanya: `launchctl list` menunjukkan agen, tetapi `/` balas 000 dan log
memuat `PermissionError ... pyvenv.cfg`.

    bash tools/live.sh tcc      # cetak langkah perbaikannya

Ringkasnya: System Settings > Privacy & Security > Full Disk Access > tambah `/bin/bash`,
lalu `launchctl kickstart -k gui/$(id -u)/id.hestia.serve`. Selama izin belum diberikan,
`live.sh pasang` menyalakan `serve.sh` sebagai cadangan agar dashboard tetap hidup.

## Selama izin belum diberikan
Agen launchd belum bisa membaca repo, jadi `live.sh pasang` menyalakan cadangan
(uvicorn langsung). Cadangan itu tidak ikut start saat login, sehingga **sesudah reboot
jalankan `bash tools/live.sh pasang --tls` sekali** sampai izin Full Disk Access diberikan.

## Layanan mati sendiri?
Cadangan berjalan lepas dari sesi Terminal dan tidak diawasi launchd (selama izin belum
diberikan), jadi bisa mati tanpa dihidupkan lagi. `bash tools/live.sh status` kini
memeriksa kedua kanal dan menyalakan ulang cadangan bila ada yang mati.
