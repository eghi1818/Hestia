# SESSION_STATE — Hestia

- Langkah terakhir: S-131
- Layanan: http://127.0.0.1:8787 (login Basic; sandi dari HESTIA_SANDI, bawaan: hestia)
- Basis data: data/hestia.db (backup otomatis 10 terbaru di data/backup/)
- Gate: tools/gate.sh — fail-closed, memeriksa rute api, id dashboard, sterilisasi, sintaks, layanan
- Kanal tanam: tools/tanam.py (PUT tanpa kredensial, lalu FTP); tombol Tanam di dashboard

## Menunggu

- juraganit.com: butuh sandi FTP (hosting liqu.id)
- waspadaweb.com: SSH tembus, /var/www/waspadaweb milik root, butuh sudo
- persaudaraan.com: nama *.netlify.app belum ketemu
