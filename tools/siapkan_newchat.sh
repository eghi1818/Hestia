#!/usr/bin/env bash
# HESTIA - susun folder unggah siap-pakai untuk chat baru (di Desktop)
set -u
cd "$(dirname "$0")/.." || exit 1
TUJUAN="$HOME/Desktop/HESTIA-RESUME"

bash tools/serve.sh >/dev/null 2>&1
if [ "${1:-}" = "--naik" ]; then
  bash tools/handoff_pack.sh --naik >/dev/null
fi
bash tools/handoff_pack.sh >/dev/null

mkdir -p "$TUJUAN"
cp docs/ONBOARDING_PROMPT.txt "$TUJUAN/1-ONBOARDING-PROMPT.txt"
cp docs/SESSION_STATE.md      "$TUJUAN/2-SESSION-STATE.md"
bash tools/resume.sh > "$TUJUAN/3-KELUARAN-RESUME.txt" 2>&1
cp docs/HANDOFF.md            "$TUJUAN/4-SERAH-TERIMA-lengkap.md"

VER=$(sed -n 's/^versi_terakhir:[[:space:]]*//p' docs/CHAT.md 2>/dev/null | head -1)
NAMA=$(sed -n 's/^nama_chat:[[:space:]]*//p' docs/CHAT.md 2>/dev/null | head -1)
NAMA=${NAMA:-SEO}
VER_NEXT=$(python3 -c "v='${VER:-1.0}'.split('.');print('%s.%d'%(v[0],int(v[1])+1))")

cat > "$TUJUAN/0-CARA-PAKAI.txt" <<TXT
CARA PAKAI - dipakai saat chat Hestia keluar "Response failed. Please try again."

SIAPKAN (saat chat sekarang masih hidup):
    bash tools/siapkan_newchat.sh

PINDAH (saat chat gagal):
    bash tools/siapkan_newchat.sh --naik

LALU:
 1. Buat chat baru. NAMA CHAT: $NAMA V$VER_NEXT
 2. Lampirkan berkas 1 dan 2 dari folder ini.
 3. Jalankan: bash tools/resume.sh
    lalu tempel SELURUH keluarannya ke chat.
    (berkas 3-KELUARAN-RESUME.txt = cadangan bila mau diunggah)
 4. Pesan pertama: tempel isi berkas 1 di antara dua garis, apa adanya.
 5. Kalau agent masih ragu, lampirkan 4-SERAH-TERIMA-lengkap.md.

PANTANGAN
 - Jangan unggah folder repo. Cukup berkas di folder ini.
 - Jangan sunting berkas di folder ini; dihasilkan ulang oleh skrip di atas.
 - Naikkan versi SEBELUM mulai kerja di chat baru, bukan sesudah.
 - Jangan lupa: bash tools/handoff_pack.sh --naik sebelum menutup sesi.

Folder ini: $TUJUAN
Dibuat   : $(date '+%Y-%m-%d %H:%M:%S %Z')
TXT

echo "folder: $TUJUAN"
ls -l "$TUJUAN"
echo "chat ini: $NAMA V${VER:-1.0}  ->  buat chat baru bernama: $NAMA V$VER_NEXT"
