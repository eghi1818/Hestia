# Deploy Hestia di VPS

## Sekali jalan
    rsync -a --exclude .git --exclude .venv --exclude 'data/backup' ./ root@VPS:/opt/hestia/
    ssh root@VPS 'cd /opt/hestia && bash deploy/pasang.sh'

## Hasil
- systemd unit hestia.service (enable + Restart=always), log di /var/log/hestia/serve.log
- vhost nginx port 8791 (80/443 dipakai waspadaweb) -> proxy ke 127.0.0.1:8787
- sandi dashboard di /etc/hestia/live.env (640, root:hestia)
- backup DB terjadwal 03:17 lewat /etc/cron.d/hestia-backup
- port 8791 dibuka di ufw bila ada

## HTTPS
Butuh nama domain mengarah ke VPS. Setelah DNS siap:
    certbot --nginx -d hestia.domain.tld

## Yang berbeda dibanding di Mac
- launchd -> systemd. TCC / Full Disk Access TIDAK relevan di VPS.
- tools/live.sh (macOS) tidak dipakai; ganti dengan systemctl restart hestia.
- tools/jalur.py dkk tetap jalan: ssh ke host yang sama.

## Rollback
    systemctl disable --now hestia.service
    rm -f /etc/nginx/sites-enabled/hestia.conf && systemctl reload nginx
    rm -f /etc/cron.d/hestia-backup
Data DB tetap di /opt/hestia/data/hestia.db (cadangan di /opt/hestia/data/backup).
