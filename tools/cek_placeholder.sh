#!/usr/bin/env bash
# Pemeriksa placeholder yang belum diisi di berkas bukti. rc=1 kalau ada.
set -uo pipefail
cd "$(dirname "$0")/.."
POLA='<isi dari|<tempel|<hasil uji|<hasil dari|<belum diisi|<diganti dari'
hits=$(grep -rn "$POLA" docs/evidence/*.txt 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "$hits"
  exit 1
fi
echo "  ok      tidak ada placeholder"
