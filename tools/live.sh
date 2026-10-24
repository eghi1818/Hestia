#!/usr/bin/env bash
# HESTIA - jadikan layanan hidup 24/7: sandi naik, agen launchd, opsi TLS.
set -euo pipefail

AKAR="$(cd "$(dirname "$0")/.." && pwd)"
HOME_H="${HESTIA_HOME:-$HOME/.hestia}"
ENV="$HOME_H/live.env"
PLIST="$HOME/Library/LaunchAgents/id.hestia.serve.plist"
LABEL="id.hestia.serve"
PORT="${HESTIA_PORT:-8787}"
LOG="$HOME_H/serve.log"
TLS="$HOME_H/tls"
PY="$AKAR/.venv/bin/python"

siap_dir() { mkdir -p "$HOME_H"; chmod 700 "$HOME_H"; }
sandi() { sed -n 's/^HESTIA_SANDI=//p' "$ENV"; }
sandi_ada() { [ -f "$ENV" ] && grep -q '^HESTIA_SANDI=' "$ENV"; }

sandi_baru() {
  siap_dir; umask 077
  printf 'HESTIA_SANDI=%s\n' "$(openssl rand -hex 16)" > "$ENV"
  chmod 600 "$ENV"
  echo "sandi baru ditulis ke $ENV (mode 600)"
}

tls_buat() {
  siap_dir; mkdir -p "$TLS"; chmod 700 "$TLS"
  if [ ! -f "$TLS/hestia.key" ]; then
    openssl req -x509 -newkey rsa:2048 -nodes -days 825 \
      -keyout "$TLS/hestia.key" -out "$TLS/hestia.crt" \
      -subj "/CN=hestia.local" >/dev/null 2>&1
    chmod 600 "$TLS/hestia.key"
    echo "TLS: sertifikat self-signed dibuat di $TLS"
  fi
}

tls_aktif() { [ -f "$PLIST" ] && grep -q 'ssl-keyfile' "$PLIST"; }
cek_tcc() { [ -f "$LOG" ] && grep -q "Operation not permitted" "$LOG"; }

pesan_tcc() {
  cat <<TXT
SEBAB: macOS (TCC) menutup folder Documents bagi proses yang dijalankan launchd.
PERBAIKAN, sekali saja, lewat GUI:
  1. System Settings > Privacy & Security > Full Disk Access
  2. klik +, Cmd+Shift+G, ketik /bin/bash, pilih, lalu aktifkan
  3. launchctl kickstart -k gui/$(id -u)/$LABEL
  4. bash tools/live.sh status
TXT
}

plist_tulis() {
  local tls_args=""
  if [ "${PAKAI_TLS:-0}" = "1" ]; then
    tls_args=" --ssl-keyfile \$HOME/.hestia/tls/hestia.key --ssl-certfile \$HOME/.hestia/tls/hestia.crt"
  fi
  cat > "$PLIST" <<PLISTX
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>WorkingDirectory</key><string>$AKAR</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>set -a; . \$HOME/.hestia/live.env; set +a; exec $PY -m uvicorn app.main:app --host 127.0.0.1 --port $PORT$tls_args</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>10</integer>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
PLISTX
  plutil -lint "$PLIST" >/dev/null
  echo "plist ditulis: $PLIST"
}

muat_ulang() {
  launchctl unload "$PLIST" >/dev/null 2>&1 || true
  pkill -f "app.main" >/dev/null 2>&1 || true
  sleep 1
  launchctl load "$PLIST"
  sleep 3
}

uji() {
  local skema="http" k="" s a b
  s="$(sandi 2>/dev/null || true)"
  if tls_aktif; then skema="https"; k="-k"; fi
  a="$(curl -s $k -o /dev/null -w '%{http_code}' "$skema://127.0.0.1:$PORT/" || true)"
  b="$(curl -s $k -o /dev/null -w '%{http_code}' -u "eghi:$s" "$skema://127.0.0.1:$PORT/" || true)"
  echo "layanan: $skema tanpa sandi http $a | dengan sandi http $b"
  if [ "$b" != "200" ]; then return 1; fi
  if [ "$a" != "401" ]; then echo "PERINGATAN: tanpa sandi tidak 401 (dapat $a)"; fi
}

cadangan() {
  echo "sementara menyalakan tools/serve.sh sebagai cadangan..."
  bash "$AKAR/tools/serve.sh" >/dev/null 2>&1 || true
  sleep 3
}

case "${1:-status}" in
  pasang)
    shift || true
    PAKAI_TLS=0
    for a in "$@"; do if [ "$a" = "--tls" ]; then PAKAI_TLS=1; fi; done
    if ! sandi_ada; then sandi_baru; fi
    if [ "$PAKAI_TLS" = "1" ]; then tls_buat; fi
    plist_tulis
    muat_ulang
    if uji; then
      echo "agen launchd: $LABEL | port: $PORT"
    elif cek_tcc; then
      pesan_tcc
      cadangan
      if uji; then echo "layanan hidup via cadangan; agen menunggu izin di atas."; else echo "GAGAL: layanan tetap mati."; exit 1; fi
    else
      echo "GAGAL: layanan tidak melayani, dan bukan sebab TCC. Lihat $LOG"; exit 1
    fi
    ;;
  sandi-baru)
    sandi_baru
    if [ -f "$PLIST" ]; then plist_tulis; muat_ulang; if ! uji; then cek_tcc && pesan_tcc; cadangan; uji || true; fi; fi
    ;;
  status)
    launchctl list | grep "$LABEL" || echo "agen belum terpasang"
    if sandi_ada; then echo "sandi: $(sandi | cut -c1-6)... (dari $ENV)"; else echo "sandi: belum ada, bawaan 'hestia'"; fi
    if cek_tcc; then echo "catatan: log memuat penolakan TCC -> agen belum bisa membaca repo"; fi
    uji || { echo "layanan tidak melayani"; cek_tcc && pesan_tcc; }
    ;;
  tcc) pesan_tcc ;;
  hapus)
    launchctl unload "$PLIST" >/dev/null 2>&1 || true
    pkill -f "app.main" >/dev/null 2>&1 || true
    rm -f "$PLIST"
    echo "agen dihapus; sandi tetap di $ENV"
    ;;
  *)
    echo "pakai: live.sh {pasang [--tls]|status|sandi-baru|tcc|hapus}"; exit 2 ;;
esac
