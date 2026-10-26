#!/usr/bin/env bash
# Pasang Hestia Dashboard di VPS. Idempoten: aman dijalankan berulang.
set -euo pipefail

AKAR="${HESTIA_SRC:-/opt/hestia}"
USER_H="${HESTIA_USER:-hestia}"
ENV_DIR="/etc/hestia"
LOG_DIR="/var/log/hestia"
PORT="${HESTIA_PORT:-8787}"

[ "$(id -u)" = "0" ] || { echo "jalankan sebagai root"; exit 1; }

echo "== 1. user & direktori =="
id "$USER_H" >/dev/null 2>&1 || useradd -r -m -d "$AKAR" -s /usr/sbin/nologin "$USER_H"
mkdir -p "$AKAR" "$ENV_DIR" "$LOG_DIR"
chmod 750 "$ENV_DIR" "$LOG_DIR"

echo "== 2. berkas aplikasi =="
if [ "$(pwd)" != "$AKAR" ]; then
  rsync -a --delete --exclude '.git' --exclude '.venv' --exclude 'data/backup' ./ "$AKAR"/
fi
chown -R "$USER_H:$USER_H" "$AKAR"

echo "== 3. venv & dependensi =="
if [ ! -x "$AKAR/.venv/bin/python" ]; then
  python3 -m venv "$AKAR/.venv"
fi
"$AKAR/.venv/bin/python" -m pip install --upgrade pip >/dev/null
if [ -f "$AKAR/requirements.txt" ]; then
  "$AKAR/.venv/bin/python" -m pip install -r "$AKAR/requirements.txt" >/dev/null
fi
chown -R "$USER_H:$USER_H" "$AKAR/.venv"

echo "== 4. rahasia (HESTIA_SANDI) =="
if [ ! -f "$ENV_DIR/live.env" ]; then
  printf 'HESTIA_SANDI=%s\nHESTIA_TLS=0\n' "$(openssl rand -hex 16)" > "$ENV_DIR/live.env"
  chmod 640 "$ENV_DIR/live.env"
  chown root:"$USER_H" "$ENV_DIR/live.env"
  echo "  sandi baru dibuat di $ENV_DIR/live.env"
else
  echo "  sandi sudah ada, dibiarkan"
fi

echo "== 5. unit systemd =="
install -m 644 "$AKAR/deploy/hestia.service" /etc/systemd/system/hestia.service
systemctl daemon-reload
systemctl enable hestia.service
systemctl restart hestia.service
sleep 3
systemctl is-active hestia.service

echo "== 6. vhost nginx =="
install -m 644 "$AKAR/deploy/nginx-hestia.conf" /etc/nginx/sites-available/hestia.conf
ln -sf /etc/nginx/sites-available/hestia.conf /etc/nginx/sites-enabled/hestia.conf
nginx -t
systemctl reload nginx

echo "== 7. firewall =="
if command -v ufw >/dev/null 2>&1; then
  ufw allow 8791/tcp >/dev/null 2>&1 || true
fi

echo "== 8. backup terjadwal =="
printf '17 3 * * * %s cd %s && %s/.venv/bin/python tools/backup.py >/dev/null 2>&1\n' "$USER_H" "$AKAR" "$AKAR" > /etc/cron.d/hestia-backup
chmod 644 /etc/cron.d/hestia-backup

echo "== 9. uji =="
sandi=$(sed -n 's/^HESTIA_SANDI=//p' "$ENV_DIR/live.env")
printf '  langsung : '; curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:$PORT/" || true
printf '  via nginx: '; curl -s -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8791/" || true
printf '  dengan sandi via nginx: '; curl -s -o /dev/null -w '%{http_code}\n' -u "eghi:$sandi" "http://127.0.0.1:8791/" || true
echo "selesai. sandi ada di $ENV_DIR/live.env"
