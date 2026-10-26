#!/usr/bin/env bash
# Sinkronisasi DB Hestia. ATURAN: VPS KANONIK untuk data operasional.
#   tarik   = VPS -> laptop   (jalankan SEBELUM kerja di laptop)
#   kirim   = laptop -> VPS   (hanya bila hasil kerja laptop harus dilihat VPS)
#   banding = bandingkan sidik jari kedua sisi
set -uo pipefail
KEY="$HOME/.ssh/wesearch_vps_key"
HOST=administrator@93.127.133.160
PORT=10053
SSH=(ssh -p "$PORT" -i "$KEY" -o StrictHostKeyChecking=no "$HOST")
LDB=data/hestia.db
aksi="${1:-banding}"

case "$aksi" in
  tarik)
    "${SSH[@]}" 'sudo -u hestia /opt/hestia/.venv/bin/python -c "import sqlite3;a=sqlite3.connect(\"/opt/hestia/data/hestia.db\");b=sqlite3.connect(\"/tmp/hestia_tarik.db\");a.backup(b);b.close()" && sudo chown administrator /tmp/hestia_tarik.db && echo "  VPS: cadangan konsisten dibuat"'
    mkdir -p data/arsip
    [ -f "$LDB" ] && cp -a "$LDB" "data/arsip/hestia-laptop-$(date +%Y%m%d-%H%M%S).db"
    scp -P "$PORT" -i "$KEY" "$HOST:/tmp/hestia_tarik.db" "$LDB"
    echo "  tarik selesai -> $LDB"
    ;;
  kirim)
    python3 - "$LDB" /tmp/hestia_kirim.db <<'PY'
import sqlite3, sys
a = sqlite3.connect(sys.argv[1]); b = sqlite3.connect(sys.argv[2]); a.backup(b); b.close(); a.close()
PY
    scp -P "$PORT" -i "$KEY" /tmp/hestia_kirim.db "$HOST:/tmp/hestia_kirim.db"
    "${SSH[@]}" 'sudo cp /tmp/hestia_kirim.db /opt/hestia/data/hestia.db && sudo rm -f /opt/hestia/data/hestia.db-wal /opt/hestia/data/hestia.db-shm && sudo systemctl restart hestia.service && echo "  kirim selesai + layanan VPS di-restart"'
    ;;
  *)
    echo -n "  laptop: "; python3 -c "import hashlib,os;p='$LDB';print(hashlib.sha256(open(p,'rb').read()).hexdigest()[:16], os.path.getsize(p), 'bita')"
    echo -n "  VPS   : "; "${SSH[@]}" "sha256sum /opt/hestia/data/hestia.db | cut -c1-16; stat -c%s /opt/hestia/data/hestia.db" | tr '\n' ' '; echo " bita"
    ;;
esac
