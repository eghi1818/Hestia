
## Probe dan pengalihan

- Probe harus menyondong URL FINAL, bukan yang mengalihkan. Pakai bentuk akhir atau -L.
- Kalau semua probe membalas byte identik, kita menyondong satu hal, bukan banyak.
- Cloudflare hanya memproksi port tertentu; menguji port lain lewat hostname terproksi memberi timeout yang tidak menyimpulkan apa pun.

## Probe dan galat shell

- Baris probe yang mengeluarkan galat shell hasilnya TIDAK SAH, bukan kosong. Salurkan 2>&1, dan cetak [GALAT] untuk: no matches found, No such file, command not found.
- Glob selalu dikutip: --include='*.py'.
- Probe harus menyondong URL FINAL, bukan yang mengalihkan.
