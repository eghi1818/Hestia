#!/usr/bin/env bash
# HESTIA - layanan hidup 24/7: sandi naik, agen launchd (HTTP 8787), opsi HTTPS (8788).
set -euo pipefail

AKAR="$(cd "$(dirname "$0")/.." && pwd)"
HOME_H="${HESTIA_HOME:-$HOME/.hestia}"
ENV="$HOME_H/live.env"
AGEN="$HOME/Library/LaunchAgents"
LABEL="id.hestia.serve"
LABEL_TLS="id.hestia.serve.tls"
PLIST="$AGEN/$LABEL.plist"
PLIST_TLS="$AGEN/$LABEL_TLS.plist"
PORT="${HESTIA_PORT:-8787}"
PORT_TLS="${HESTIA_PORT_TLS:-8788}"
LOG="$HOME_H/serve.log"
TLS="$HOME_H/tls"
PY="$AKAR/.venv/bin/python"

siap_dir() { mkdir -p "$HOME_H"; chmod 700 "$HOME_H"; }
sandi() { sed -n 's/^HESTIA_SANDI=//p' "$ENV"; }
sandi_ada() { [ -f "$ENV" ] && grep -q '^HESTIA_SANDI=' "$ENV"; }
cek_tcc() { [ -f "$LOG" ] && grep -q "Operation not permitted" "$LOG"; }

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

_tulis_plist() {
  local label="$1" berkas="$2" port="$3" extra="$4"
  cat > "$berkas" <<PLISTX
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$label</string>
  <key>WorkingDirectory</key><string>$AKAR</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>set -a; . \$HOME/.hestia/live.env; set +a; exec $PY -m uvicorn app.main:app --host 127.0.0.1 --port $port$extra</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>10</integer>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
PLISTX
  plutil -lint "$berkas" >/dev/null
}

plist_tulis() {
  _tulis_plist "$LABEL" "$PLIST" "$PORT" ""
  echo "plist http ditulis: $PLIST"
  if [ "${PAKAI_TLS:-0}" = "1" ]; then
    _tulis_plist "$LABEL_TLS" "$PLIST_TLS" "$PORT_TLS" \
      " --ssl-keyfile \$HOME/.hestia/tls/hestia.key --ssl-certfile \$HOME/.hestia/tls/hestia.crt"
    echo "plist https ditulis: $PLIST_TLS"
  fi
}

muat_ulang() {
  launchctl unload "$PLIST" >/dev/null 2>&1 || true
  if [ -f "$PLIST_TLS" ]; then launchctl unload "$PLIST_TLS" >/dev/null 2>&1 || true; fi
  pkill -f "app.main" >/dev/null 2>&1 || true
  sleep 1
  launchctl load "$PLIST"
  if [ -f "$PLIST_TLS" ]; then launchctl load "$PLIST_TLS"; fi
  sleep 3
}

uji() {
  local s a b c d gagal=0
  s="$(sandi 2>/dev/null || true)"
  a="$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/" || true)"
  b="$(curl -s -o /dev/null -w '%{http_code}' -u "eghi:$s" "http://127.0.0.1:$PORT/" || true)"
  echo "http  :$PORT tanpa sandi $a | dengan sandi $b"
  if [ "$b" != "200" ]; then gagal=1; fi
  if [ -f "$PLIST_TLS" ]; then
    c="$(curl -sk -o /dev/null -w '%{http_code}' "https://127.0.0.1:$PORT_TLS/" || true)"
    d="$(curl -sk -o /dev/null -w '%{http_code}' -u "eghi:$s" "https://127.0.0.1:$PORT_TLS/" || true)"
    echo "https :$PORT_TLS tanpa sandi $c | dengan sandi $d"
    if [ "$d" != "200" ]; then gagal=1; fi
  fi
  [ "$gagal" = "0" ]
}

cadangan() {
  echo "sementara menyalakan uvicorn langsung sebagai cadangan..."
  set -a; . "$ENV"; set +a
  pkill -f "app.main" >/dev/null 2>&1 || true
  sleep 1
  nohup "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT" >> "$LOG" 2>&1 &
  echo $! > "$HOME_H/cadangan.pid"
  if [ -f "$PLIST_TLS" ]; then
    nohup "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT_TLS" \
      --ssl-keyfile "$TLS/hestia.key" --ssl-certfile "$TLS/hestia.crt" >> "$LOG" 2>&1 &
    echo $! > "$HOME_H/cadangan-tls.pid"
  fi
  sleep 4
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
      echo "agen launchd: $LABEL${PAKAI_TLS:+ (+TLS)}"
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
    if [ -f "$PLIST" ]; then muat_ulang; if ! uji; then cek_tcc && pesan_tcc; cadangan; uji || true; fi; fi
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
    launchctl unload "$PLIST_TLS" >/dev/null 2>&1 || true
    pkill -f "app.main" >/dev/null 2>&1 || true
    rm -f "$PLIST" "$PLIST_TLS"
    echo "agen dihapus; sandi tetap di $ENV"
    ;;
  *)
    echo "pakai: live.sh {pasang [--tls]|status|sandi-baru|tcc|hapus}"; exit 2 ;;
esac
