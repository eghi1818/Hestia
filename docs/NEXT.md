# Kerjaan Tertunda

## Menunggu kunci (bukan kode)

- `juraganit.com` — pintu FTP terbuka (Pure-FTPd), anonymous rusak, PUT ditolak.
  Butuh satu baris `user:sandi` FTP dari panel hosting liqu.id.
  Setelah itu: buka dashboard, tab Target, klik Tanam, tempel `user:sandi`. Hestia simpan sendiri.
- `waspadaweb.com` — SSH ke VPS 93.127.133.160:10053 sudah tembus (user `wesearch`, kunci `~/.ssh/wesearch_vps_key`).
  `/var/www/waspadaweb` milik `root:root 755`. Butuh sandi sudo sekali, atau masuk sebagai root.
- `persaudaraan.com` — di Netlify (A record 75.2.60.5), DNS di Hostinger.
  Nama `*.netlify.app` belum ketemu sehingga API publiknya belum bisa dipakai.

## Kode

- Unggah berkas FTP/SFTP lewat dashboard (sekarang masih lewat `tools/tanam.py`)
- Tampilkan jejak `clientlog` di Audit Log dengan penyaring
- Papan status pindai `teknologi` di Ikhtisar (16 target mati/parkir belum terisi)

## Sebelum LIVE

- Host 24/7 + domain + HTTPS
- Jalankan `tools/serve.sh` sebagai layanan (launchd/systemd)
- Naikkan `HESTIA_SANDI` dari bawaan

## Lapangan

- Verifikasi kandidat berstatus `baru` lewat tombol Putaran otomatis
- Tanam konten nyata lalu tandai `indeks` pada baris konten
