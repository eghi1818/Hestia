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
if python3 tools/gate_api.py; then :; else fail=1; fi

echo "== gate: layanan dashboard (fail-closed) =="
BASE="http://127.0.0.1:8787"; KURVA=""
if grep -q '^HESTIA_TLS=1' "$HOME/.hestia/live.env" 2>/dev/null; then BASE="https://127.0.0.1:8787"; KURVA="-k"; fi
code=$(curl -s${KURVA:-} -o /dev/null -w '%{http_code}' --max-time 3 "$BASE/" 2>/dev/null || true)
api=$(curl -s${KURVA:-} -o /dev/null -w '%{http_code}' --max-time 3 "$BASE/api/health" 2>/dev/null || true)
if [ "$code" = "401" ] && [ "$api" = "200" ]; then
  echo "  ok      tanpa sandi http $code"
  echo "  ok      /api/health http $api"
  echo "  layanan HIDUP"
else
  echo "  /            http ${code:-000}"
  echo "  /api/health  http ${api:-000}"
  if [ "${HESTIA_ALLOW_DOWN:-0}" = "1" ]; then
    echo "  layanan MATI (diizinkan lewat HESTIA_ALLOW_DOWN=1)"
  else
    echo "  layanan MATI" ; fail=1
  fi
fi

echo "== gate: placeholder bukti =="
if ! bash tools/cek_placeholder.sh; then fail=1; fi

echo "== gate: bukti langkah terakhir =="
langkah=$(ls docs/steps/S-*.md 2>/dev/null | sed 's#.*/S-##;s#\.md##' | sort -n | tail -1)
if [ -n "$langkah" ]; then
  if [ -f "docs/evidence/S-$langkah.txt" ]; then
    echo "  ok      docs/evidence/S-$langkah.txt (S-$langkah)"
  else
    echo "  KURANG  docs/evidence/S-$langkah.txt (S-$langkah)"
    exit 1
  fi
fi

echo "== gate: skrip dashboard disajikan =="
for berkas in $(grep -o '<script src="/[a-z0-9_-]*\.js' dashboard/index.html | sed 's#.*/##' | sort -u); do
  if grep -q "@app.get(\"/$berkas\")" app/main.py; then
    echo "  ok      /$berkas"
  else
    echo "  KURANG  /$berkas tidak punya rute di app/main.py"; fail=1
  fi
done

echo "== gate: rute api utama (hidup) =="
SANDI_H=$(sed -n 's/^HESTIA_SANDI=//p' "$HOME/.hestia/live.env" 2>/dev/null || true)
if [ -n "$SANDI_H" ]; then
  for pasangan in "/api/health:200" "/api/targets:200" "/api/teknologi-ringkas:200" "/api/status/ringkas:200" "/api/audit:200" "/api/driver/rules?domain=waspadaweb.com:200" "/api/driver/plan?domain=waspadaweb.com:200"; do
    jalur="${pasangan%:*}"
    harap="${pasangan##*:}"
    dapat=$(curl -s${KURVA:-} -o /dev/null -w '%{http_code}' --max-time 8 -u "eghi:$SANDI_H" "$BASE$jalur" 2>/dev/null || true)
    if [ "$dapat" = "$harap" ]; then
      echo "  ok      $jalur -> $dapat"
    else
      echo "  KURANG  $jalur -> $dapat (harap $harap)"; fail=1
    fi
  done
else
  echo "  lewat   sandi live belum ada"
fi

echo "== gate: dokumen spec =="
for f in docs/PROLOG-HESTIA-DASHBOARD.md docs/GOAL-Hestia-SEO.md docs/SKILL-AGENT-HESTIA.md docs/PROMPT-TAMBAHAN-AGENT-DASHBOARD.md; do
  if [ -f "$f" ]; then echo "  ok      $f"; else echo "  KURANG  $f"; fail=1; fi
done

if [ "$fail" -eq 0 ]; then echo "GATE: LULUS" ; exit 0 ; else echo "GATE: GAGAL" ; exit 1 ; fi
