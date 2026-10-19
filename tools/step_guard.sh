#!/usr/bin/env bash
# HESTIA - penjaga langkah: berkas wajib + kompilasi + gate
cd "$(dirname "$0")/.." || exit 1
rc=0
for f in app/main.py app/db.py dashboard/index.html dashboard/live.js tools/gate.sh \
         tools/scrape.py docs/HANDOFF.md docs/SESSION_STATE.md docs/STEPLOG.md; do
  [ -f "$f" ] || { echo "HILANG: $f"; rc=1; }
done
python3 -m py_compile app/main.py tools/scrape.py 2>/dev/null || { echo "py_compile GAGAL"; rc=1; }
svc=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8787/api/targets 2>/dev/null || echo 000)
if [ "$svc" = "200" ]; then
  bash tools/gate.sh >/dev/null 2>&1 && echo "gate OK" || { echo "gate GAGAL"; rc=1; }
else
  echo "catatan: layanan 8787 http=$svc (jalankan bash tools/serve.sh)"
fi
[ $rc -eq 0 ] && echo "step_guard OK" || echo "step_guard GAGAL"
exit $rc
