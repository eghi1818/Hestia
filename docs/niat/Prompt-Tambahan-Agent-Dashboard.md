# PROMPT TAMBAHAN - Agent Dashboard Hestia (salinan, 2026-10-24)

## Aturan kerja
- satu blok = patch + uji + bukti + gate + commit
- semua tambalan wajib ber-assert dan gagal aman (berkas tidak diubah kalau pola tak cocok)
- gate dijalankan SEBELUM commit
- wajib export GIT_PAGER=cat
- jangan rewrite history
- tiap langkah wajib punya docs/evidence/S-<n>.txt tanpa placeholder

## Pola kesalahan yang sudah tercatat
menebak dari nama, tidak membaca isi dulu. Keluaran kosong dibaca sebagai "tidak ada".
Zsh tidak memecah variabel tak dikutip. Anchor patch harus unik.

## Urutan prioritas
Modul 4 (aktif) -> Modul 5 -> ActionLog -> unggah berkas lewat dashboard ->
papan status teknologi -> LIVE
