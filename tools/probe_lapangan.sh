#!/usr/bin/env bash
set -uo pipefail
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:$PATH"
cd "$(dirname "$0")/.."
mkdir -p .out
LOG=".out/probe-$(date +%Y%m%d-%H%M%S).txt"
exec > >(tee "$LOG") 2>&1

FTP=103.53.194.70
echo "### PATH: $(command -v curl) $(command -v python3)"
echo

echo "### 1. FTP anonim, empat mode, verbose ke berkas"
n=0
for mode in "--ftp-ssl-reqd --disable-epsv" "--ftp-ssl-control --disable-epsv" "--disable-epsv" "-P -"; do
  n=$((n+1))
  f=".out/ftp-$n.txt"
  # shellcheck disable=SC2086
  curl -skv $mode -u anonymous:anonymous --connect-timeout 8 --max-time 20 "ftp://$FTP/" > "$f" 2>&1
  printf 'mode[%d] %-40s rc=%s\n' "$n" "$mode" "$?"
  grep -E '^[<>] ' "$f" | head -20
  echo
done

echo "### 2. member.mcs.co.id: halaman publik"
curl -sk --max-time 10 https://member.mcs.co.id/serverstatus.php > .out/mcs-status.html 2>&1
printf 'serverstatus bytes=%s\n' "$(wc -c < .out/mcs-status.html)"
grep -oiE 'server[a-z0-9._-]*|[a-z0-9.-]+\.(mcs|maxserver|maxindo|hostindo|nusantara)\.(co\.id|com)' .out/mcs-status.html | sort -u | head -20
echo

echo "### 3. cari hostname cPanel di HTML publik"
for u in https://member.mcs.co.id/clientarea.php https://member.mcs.co.id/cart.php; do
  curl -sk --max-time 10 "$u" | grep -oiE '[a-z0-9.-]+\.(mcs|maxserver|maxindo)\.co\.id|:2083|:2087|cpanel' | sort -u | head -10
done
echo

echo "### 4. kalau ada hostname server, cek portnya"
for h in $(grep -oiE '[a-z0-9.-]+\.(mcs|maxserver|maxindo)\.co\.id' .out/mcs-status.html | sort -u | head -5); do
  ip=$(dig +short "$h" A | head -1)
  printf '%s -> %s\n' "$h" "$ip"
  [ -n "$ip" ] || continue
  for p in 2083 2087 2222 21; do
    printf '   %s:%s %s\n' "$h" "$p" "$(nc -vz -G 4 "$ip" "$p" 2>&1 | tail -1)"
  done
done
