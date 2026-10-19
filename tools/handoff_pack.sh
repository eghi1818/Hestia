#!/usr/bin/env bash
# HESTIA - susun berkas serah-terima untuk chat baru
set -u
cd "$(dirname "$0")/.." || exit 1
mkdir -p docs
CHAT="docs/CHAT.md"; OUT="docs/HANDOFF.md"

NAMA=$(sed -n 's/^nama_chat:[[:space:]]*//p' "$CHAT" 2>/dev/null | head -1); NAMA=${NAMA:-SEO}
VER=$(sed -n 's/^versi_terakhir:[[:space:]]*//p' "$CHAT" 2>/dev/null | head -1); VER=${VER:-1.0}
VER_NEXT=$(python3 -c "v='$VER'.split('.');print('%s.%d'%(v[0],int(v[1])+1))")

if [ "${1:-}" = "--naik" ]; then
  printf 'nama_chat: %s\nversi_terakhir: %s\n' "$NAMA" "$VER_NEXT" > "$CHAT"
  echo "versi dinaikkan: $NAMA V$VER -> V$VER_NEXT"
  VER="$VER_NEXT"; VER_NEXT=$(python3 -c "v='$VER'.split('.');print('%s.%d'%(v[0],int(v[1])+1))")
fi

TS=$(date '+%Y-%m-%d %H:%M:%S %Z')
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '-')
HEAD=$(git log -1 --format='%h %s' 2>/dev/null || echo '(belum ada commit)')
KOTOR=$(git status --porcelain 2>/dev/null | head -15)
bash tools/gate.sh >/tmp/hgate.txt 2>&1; GRC=$?
GATE=$([ $GRC -eq 0 ] && echo LULUS || echo GAGAL)
SVC=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8787/api/targets 2>/dev/null || echo 000)
[ "$SVC" = "000" ] && SVC="mati"
bag() { [ -f "$1" ] && cat "$1" || echo "(berkas $1 belum ada)"; }

{
echo "# SERAH-TERIMA - $NAMA V$VER"
echo "chat ini: $NAMA V$VER  |  lanjutan bila gagal: $NAMA V$VER_NEXT"
echo "waktu: $TS"
echo "repo: $(pwd)   cabang: $BRANCH"
echo "commit terakhir: $HEAD"
echo "gate: $GATE   layanan(8787): $SVC"
echo "python: $(python3 -V 2>&1)   (ingat: 3.9, pakai Optional[str])"
echo
echo "## 0. CARA PAKAI"
echo "1) Buat chat baru bernama $NAMA V$VER_NEXT. Unggah SELURUH isi ~/Desktop/HESTIA-RESUME."
echo "2) Pesan pertama: tempel isi 1-ONBOARDING-PROMPT.txt apa adanya."
echo "3) Tulis: \"Baca SERAH-TERIMA ini sampai habis, lanjut dari bagian 8.\""
echo
echo "## 1. STATUS"
echo "- gate: $GATE | layanan: $SVC | commit: $HEAD"
echo "- kandidat: $(python3 -c 'import sqlite3;print(sqlite3.connect("data/hestia.db").execute("select count(*) from kandidat").fetchone()[0])' 2>/dev/null || echo '?')" 
echo "- target  : $(python3 -c 'import sqlite3;print(sqlite3.connect("data/hestia.db").execute("select count(*) from targets").fetchone()[0])' 2>/dev/null || echo '?')" 
echo
echo "## 2. SUDAH SELESAI - JANGAN DIULANG"
echo '```'
tail -60 docs/STEPLOG.md 2>/dev/null || echo "(docs/STEPLOG.md belum ada)"
echo '```'
echo
echo "## 3. PENDING - URUTAN KERJA"
echo '```'; bag docs/PENDING.md; echo '```'
echo
echo "## 4. GAGAL / TERBLOKIR - JANGAN DIULANG TANPA SEBAB BARU"
echo "- crt.sh: 502 (sisi mereka); cadangan rapiddns + hackertarget sudah ada"
echo "- certspotter: 403 (ac.id bukan eTLD) - wajar"
echo "- komdigi.go.id: 403 semua variasi, kemungkinan blokir fingerprint TLS"
echo "- bps.go.id: 403 di HTTP/2, 301 di HTTP/1.1 - wajib --http1.1"
echo
echo "## 5. ATURAN PANTANG DILANGGAR"
echo "- istilah tim: 'Authority Hosting'; dilarang 'parasite' dan 'reframing' di berkas tim"
echo "- satu blok maks 250 baris; satu langkah = satu commit + satu berkas bukti"
echo "- commit hanya bila gate rc=0, selalu push"
echo "- wajib izin pengguna sebelum menyentuh internet"
echo "- gate fail-closed: layanan mati = GAGAL"
echo
echo "## 6. PETA TEKNIS"
echo "- app/main.py FastAPI :8787 | app/db.py SQLite data/hestia.db"
echo "- dashboard/index.html + dashboard/live.js (window.addTarget ditimpa)"
echo "- tools/gate.sh, tools/scrape.py, tools/serve.sh, tools/smoke.sh, tools/step_guard.sh, tools/resume.sh"
echo "- tabel: targets, kandidat, clientlog"
echo
echo "## 7. EKOR BUKTI"
echo '```'
echo "git log -5:"; git log --oneline -5 2>/dev/null || true
echo "status:"; echo "$KOTOR"
echo '```'
echo
echo "## 8. LANGKAH BERIKUT - TEPAT"
echo '```'; bag docs/NEXT.md; echo '```'
} > "$OUT"
echo "ditulis: $OUT ($(wc -l < "$OUT") baris)"
echo "chat: $NAMA V$VER  ->  lanjutan: $NAMA V$VER_NEXT"
