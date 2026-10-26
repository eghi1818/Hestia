#!/usr/bin/env bash
# gate misi - memeriksa POKOK SOAL, bukan perpipaan
set -uo pipefail
F=docs/MISI.md
fail=0
if [ ! -f "$F" ]; then echo "MISI: GAGAL - $F tidak ada"; exit 1; fi
grep -q '^url_soal: http' "$F" || { echo "MISI: GAGAL - url_soal kosong"; fail=1; }
grep -qE '^baseline_sha256: [0-9a-f]{64}' "$F" || { echo "MISI: GAGAL - sha256 baseline kosong"; fail=1; }
grep -qE '^verdict: (ADA|TIDAK)' "$F" || { echo "MISI: GAGAL - verdict tidak tegas"; fail=1; }
grep -qE '^baseline_status: 2[0-9][0-9]' "$F" || { echo "MISI: GAGAL - baseline belum 2xx"; fail=1; }
[ -f docs/evidence/S-280-baseline.html ] || { echo "MISI: GAGAL - berkas baseline hilang"; fail=1; }
if grep -q '^ubah_dari_luar: BELUM' "$F"; then echo "MISI: CATATAN - pokok soal BELUM berubah dari luar"; else echo "MISI: pokok soal sudah berubah dari luar"; fi
if [ "$fail" = 0 ]; then echo "MISI: OK - baseline pokok soal lengkap"; else echo "MISI: GAGAL"; fi
exit "$fail"
