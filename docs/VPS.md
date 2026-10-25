# Rencana menjalankan Hestia di VPS

Disusun S-211, dituntaskan S-214 (S-211 tidak pernah ter-commit). Dashboard akan dipindah
dari MacBook ke VPS.

## Yang berubah dibanding di Mac
- launchd (macOS) -> systemd (Linux). Karena TCC hanya ada di macOS, butir Full Disk Access
  TIDAK relevan lagi di VPS.
- HTTPS: ganti sertifikat self-signed dengan domain + Let's Encrypt, sehingga tidak ada
  peringatan di peramban.
- Kunci API dan sandi dashboard disimpan di VPS (~/.hestia/live.env, mode 600), bukan di Mac.
- Layanan jalan 24/7 tanpa Mac menyala, sehingga pemakaian kueri API menjadi nyata.

## Yang perlu disiapkan
1. Domain/subdomain untuk dashboard (mis. hestia.domain.tld) + DNS.
2. Unit systemd hestia.service (enable + Restart=always).
3. Let's Encrypt lewat certbot + perpanjangan otomatis.
4. Firewall (ufw) + fail2ban untuk Basic auth.
5. Backup DB terjadwal (cron) memakai tools/backup.py yang sudah ada.
6. Rotasi sandi dashboard dan kunci API berkala.
7. Batas kuota API harian supaya tidak jebol saat jalan terus.

## Yang tidak perlu diubah
- app/main.py, seluruh tools/, dashboard/, dan gate: jalan apa adanya.
- tools/serve.sh tetap jalur manual. tools/live.sh perlu varian systemd, atau unit ditulis
  terpisah.

## Perkiraan
2-3 blok: (1) unit systemd + uji layanan, (2) HTTPS Let's Encrypt + firewall, (3) backup
terjadwal + batas kuota API.
