#!/usr/bin/env bash
# Gerbang verifikasi Hestia v5. rc=0 berarti boleh commit.
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
for f in $team ; do
  n=$(grep -ciE 'parasite|reframing' "$f" 2>/dev/null || true) ; [ -z "$n" ] && n=0
  if [ "$n" -eq 0 ]; then echo "  bersih  $f" ; else echo "  BOCOR   $f ($n baris)" ; fail=1 ; fi
done

echo
echo "== gate: integrasi skrip dashboard dengan index.html =="
if [ -f dashboard/live.js ] && [ -f dashboard/index.html ] ; then
  # tangkap rujukan literal, baik lewat getElementById("x") maupun val("x")
  ids=$(grep -oE '(getElementById|val|nilai|\$)\("[A-Za-z0-9_-]+"\)' dashboard/*.js 2>/dev/null \
        | sed 's/.*("//; s/")$//' | sort -u)
  if [ -z "$ids" ] ; then
    echo "  PERINGATAN tidak ada rujukan elemen yang terdeteksi" ; fail=1
  fi
  jumlah=0
  for id in $ids ; do
    jumlah=$((jumlah + 1))
    case "$id" in liveBadge) echo "  lewat   #$id (dibuat live.js/ikhtisar.js)" ; continue ;; esac
    if grep -q "id=\"$id\"" dashboard/index.html ; then
      echo "  ok      #$id"
    else
      echo "  HILANG  #$id dirujuk skrip dashboard tapi tidak ada di index.html" ; fail=1
    fi
  done
  echo "  total rujukan diperiksa: $jumlah"
fi

echo
echo "== gate: dokumen internal (boleh memuat istilah) =="
for f in GOAL.md docs/CONTEXT.md docs/EKSPERIMEN.md docs/ONBOARDING_PROMPT.txt docs/SOP-NEW-CHAT.md ; do
  [ -f "$f" ] || continue
  n=$(grep -ciE 'parasite' "$f" 2>/dev/null || true) ; [ -z "$n" ] && n=0
  echo "  $f memuat 'parasite': $n baris"
done

echo
echo "== gate: sintaks python =="
if [ -f app/main.py ] ; then
  if .venv/bin/python -m py_compile app/main.py 2>/dev/null ; then
for _f in tools/*.py; do python3 -m py_compile "$_f" >/dev/null 2>&1 || { echo "  GAGAL kompilasi: $_f"; exit 1; }; done
for _f in tools/*.sh; do [ -x "$_f" ] || { echo "  TIDAK EKSEKUTABEL: $_f"; exit 1; }; done
    echo "  ok      app/main.py bisa dikompilasi"
  else
    echo "  GAGAL   app/main.py tidak bisa dikompilasi" ; fail=1
  fi
fi

echo
echo "== gate: layanan dashboard (fail-closed) =="
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8787/ 2>/dev/null || true)
[ -z "$code" ] && code=000
api=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8787/api/health 2>/dev/null || true)
[ -z "$api" ] && api=000
echo "  /            http $code"
echo "  /api/health  http $api"
if [ -f app/main.py ] ; then
  if [ "$code" = "200" ] && [ "$api" = "200" ] ; then
    echo "  layanan HIDUP"
  elif [ "${HESTIA_ALLOW_DOWN:-0}" = "1" ] ; then
    echo "  layanan MATI (diizinkan lewat HESTIA_ALLOW_DOWN=1)"
  else
    echo "  layanan MATI" ; fail=1
  fi
fi

echo
if [ "$fail" -eq 0 ]; then echo "GATE: LULUS" ; exit 0 ; else echo "GATE: GAGAL" ; exit 1 ; fi
