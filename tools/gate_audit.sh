#!/usr/bin/env bash
# gate_audit.sh - verifikasi vendor security-audit-skill + temuan.json. rc=0 lulus.
set -uo pipefail
cd "$(dirname "$0")/.."
D=tools/audit-skill
T=docs/audit/temuan.json
gagal=0

echo "== audit: berkas vendor =="
for f in report-schema.json validate-findings.cjs validate-findings.test.cjs validate-coverage-ledger.cjs ASAL.md SHA256SUMS ; do
  if [ -f "$D/$f" ] ; then echo "  ok      $f" ; else echo "  HILANG  $f" ; gagal=1 ; fi
done

echo
echo "== audit: pin sha256 =="
if ( cd "$D" && shasum -a 256 -c SHA256SUMS >/dev/null 2>&1 ) ; then
  echo "  ok      sha256 cocok"
else
  echo "  GAGAL   sha256 tidak cocok" ; gagal=1
fi

echo
echo "== audit: temuan.json dibuat ulang tanpa anchor nyasar =="
if python3 tools/susun_temuan.py > /tmp/ga_susun.log 2>&1 ; then
  if grep -q "anchor tidak ketemu" /tmp/ga_susun.log ; then
    grep -n "anchor tidak ketemu" /tmp/ga_susun.log
    echo "  GAGAL   ada anchor tidak ketemu" ; gagal=1
  else
    echo "  ok      semua anchor ketemu"
  fi
else
  echo "  GAGAL   susun_temuan.py gagal" ; tail -5 /tmp/ga_susun.log ; gagal=1
fi

echo
echo "== audit: validator menerima temuan.json =="
if [ -f "$T" ] ; then
  if node "$D/validate-findings.cjs" "$T" > /tmp/ga_val.log 2>&1 ; then
    echo "  ok      $(cat /tmp/ga_val.log)"
  else
    echo "  GAGAL   validator menolak" ; cat /tmp/ga_val.log ; gagal=1
  fi
else
  echo "  HILANG  $T" ; gagal=1
fi

echo
echo "== audit: test upstream =="
if node "$D/validate-findings.test.cjs" >/dev/null 2>&1 ; then
  echo "  ok      test upstream lulus"
else
  echo "  GAGAL   test upstream jatuh" ; gagal=1
fi

echo
echo "== audit: rujukan baris di temuan.json =="
if [ -f "$T" ] ; then
  jml=0
  while IFS=$'\t' read -r f ln ; do
    [ -z "$f" ] && continue
    jml=$((jml + 1))
    if [ ! -f "$f" ] ; then echo "  HILANG  $f" ; gagal=1 ; continue ; fi
    case "$ln" in ''|*[!0-9]*) echo "  BURUK   $f baris '$ln' bukan angka" ; gagal=1 ; continue ;; esac
    n=$(wc -l < "$f" | tr -d ' ')
    if [ "$ln" -lt 1 ] || [ "$ln" -gt "$n" ] ; then
      echo "  BURUK   $f baris $ln dari $n" ; gagal=1
    fi
  done < <(jq -r '.. | objects | select(has("line")) | [(.file // .source // .path // ""), (.line|tostring)] | @tsv' "$T")
  echo "  diperiksa: $jml rujukan"
fi

echo
if [ "$gagal" -eq 0 ] ; then echo "GATE-AUDIT: LULUS" ; exit 0 ; else echo "GATE-AUDIT: GAGAL" ; exit 1 ; fi
