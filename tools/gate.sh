#!/usr/bin/env bash
# Gerbang verifikasi Hestia v2. rc=0 berarti boleh commit.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0

echo "== gate: berkas wajib =="
for f in README.md CHANGELOG.md GOAL.md \
         docs/PRD-Authority-Hosting-v1.5.md docs/CONTEXT.md \
         docs/EKSPERIMEN.md docs/ONBOARDING_PROMPT.txt docs/SOP-NEW-CHAT.md ; do
  if [ -f "$f" ]; then echo "  ok      $f"; else echo "  HILANG  $f"; fail=1; fi
done

echo
echo "== gate: sterilisasi pada artefak tim =="
team=""
for f in README.md CHANGELOG.md ; do [ -f "$f" ] && team="$team $f" ; done
for f in docs/PRD-*.md ; do [ -f "$f" ] && team="$team $f" ; done
for d in dashboard web app ; do
  if [ -d "$d" ]; then
    found=$(find "$d" -type f \( -name '*.html' -o -name '*.js' -o -name '*.css' -o -name '*.md' -o -name '*.py' \) 2>/dev/null | sort)
    for f in $found ; do team="$team $f" ; done
  fi
done
if [ -z "$team" ]; then echo "  (tidak ada berkas tim)"; fi
for f in $team ; do
  n=$(grep -ciE 'parasite|reframing' "$f" 2>/dev/null || true) ; [ -z "$n" ] && n=0
  if [ "$n" -eq 0 ]; then echo "  bersih  $f" ; else echo "  BOCOR   $f ($n baris)" ; fail=1 ; fi
done

echo
echo "== gate: dokumen internal (boleh memuat istilah) =="
for f in GOAL.md docs/CONTEXT.md docs/EKSPERIMEN.md docs/ONBOARDING_PROMPT.txt docs/SOP-NEW-CHAT.md ; do
  [ -f "$f" ] || continue
  n=$(grep -ciE 'parasite' "$f" 2>/dev/null || true) ; [ -z "$n" ] && n=0
  echo "  $f memuat 'parasite': $n baris"
done

echo
echo "== gate: layanan dashboard =="
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8787/ 2>/dev/null || true)
[ -z "$code" ] && code=000
echo "  http $code"

echo
if [ "$fail" -eq 0 ]; then echo "GATE: LULUS" ; exit 0 ; else echo "GATE: GAGAL" ; exit 1 ; fi
