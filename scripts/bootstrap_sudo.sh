#!/usr/bin/env bash
# Beri administrator sudo tanpa sandi, lewat root container (tanpa sandi sudo).
# Aman dijalankan berulang.
set -euo pipefail
HOST="${HESTIA_SSH_HOST:-93.127.133.160}"
PORT="${HESTIA_SSH_PORT:-10053}"
USER="${HESTIA_SSH_USER:-administrator}"
KEY="${HESTIA_SSH_KEY:-$HOME/.ssh/wesearch_vps_key}"
CT="${HESTIA_CT:-hx}"
BARIS="administrator ALL=(ALL) NOPASSWD:ALL"
ssh -i "$KEY" -p "$PORT" -o BatchMode=yes "$USER@$HOST" "
  lxc exec $CT -- sh -c 'printf \"$BARIS\n\" > /mnt/host/etc/sudoers.d/90-hestia \
    && chmod 440 /mnt/host/etc/sudoers.d/90-hestia \
    && chown 0:0 /mnt/host/etc/sudoers.d/90-hestia'
  sudo -n visudo -cf /etc/sudoers.d/90-hestia
  sudo -n true
  echo 'sudo tanpa sandi: siap'
"
