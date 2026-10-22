#!/usr/bin/env bash
# HESTIA - asap: rute inti harus hidup
cd "$(dirname "$0")/.." || exit 1
p=0; f=0
U="${HESTIA_USER:-eghi}:${HESTIA_SANDI:-hestia}"
cek() { c=$(curl -s -u "${HESTIA_USER:-eghi}:${HESTIA_SANDI:-hestia}" -o /dev/null -w '%{http_code}' --max-time 3 "http://127.0.0.1:8787$2"); \
  if [ "$c" = "$3" ]; then echo "ok    $1"; p=$((p+1)); else echo "GAGAL $1 ($c != $3)"; f=$((f+1)); fi; }
cek "targets"   "/api/targets" 200
cek "dashboard" "/"            200
cek "live.js"   "/live.js"     200
echo "smoke: $p lulus / $f gagal"
[ $f -eq 0 ] || exit 1
