# SOP - ESKALASI CHAT DAN PEMULIHAN

Versi 1.0 - khusus HESTIA - WAJIB, bukan saran

## 0. Ringkasan

Chat bisa mati mendadak. Maka setiap langkah harus bisa dipulihkan dari repo.
Repo adalah memori. Chat hanya sementara. Kalau repo dan chat berbeda, repo yang benar.

## 1. Aturan kerja

1. Satu balasan = satu blok perintah, maks 250 baris. Pecah A/B/C bila lebih.
2. Baca dulu, tulis kemudian. Jangan menebak bentuk API.
3. Commit hanya bila `make gate` keluar rc=0. Cek exit code, bukan grep.
4. Satu langkah = satu commit + satu berkas bukti.
5. Push setiap langkah selesai.
6. Jangan hentikan layanan dashboard tanpa cek health.
7. Rahasia hanya di .env (mode 600). Lapor pakai prefix saja.

## 2. Kondisi lingkungan

| Item | Nilai |
|---|---|
| Repo | ~/Documents/REPO/Hestia |
| Remote | git@github.com:eghi1818/Hestia.git |
| Layanan | dashboard di 127.0.0.1:8787 |
| Rahasia | .env mode 600 |
| Bahasa kerja | Indonesia |

## 3. Pemicu eskalasi

Pindah chat bila salah satu terjadi:
- "Response failed" dua kali berturut-turut
- Blok perintah melewati batas dan terpotong
- Konteks hilang, agen mengulang pekerjaan yang sudah selesai
- Layanan tidak sehat dan tidak pulih dalam dua langkah
- Satu blok gagal tiga kali berturut-turut

## 4. Prosedur pemulihan

1. Buka Terminal baru
2. `bash tools/resume.sh`
3. `make pack`
4. Buka chat baru
5. Tempel pesan pembuka di bagian 5
6. Lampirkan `docs/RESUME-PACK.md`

## 5. Template pesan pembuka

    Lanjutkan proyek HESTIA. Kamu agen baru, bukan lanjutan.
    Langkah wajib sebelum bicara:
      1. Baca docs/SOP-NEW-CHAT.md
      2. Baca docs/ONBOARDING_PROMPT.txt
      3. Baca docs/SESSION_STATE.md
      4. Baca docs/PENDING.md
      5. Jalankan: bash tools/resume.sh
      6. Jalankan: make gate
    Aturan: satu balasan = satu blok perintah. Commit hanya bila gate rc=0.
    Artefak tim wajib steril dari kata parasite dan reframing.
    Bahasa: Indonesia.

## 6. Aturan blok panjang

- Maks 250 baris per blok. Lebih dari itu, pecah.
- Mulai setiap blok dengan: `if [ -n "${ZSH_VERSION:-}" ]; then setopt nobanghist; fi`
- Hindari karakter non-ASCII di dalam blok.
- Kalau gagal dua kali dengan keluaran sama, pindah ke chat baru.
- Jangan ulangi blok panjang yang sama; pecah lebih kecil.

## 7. Bukti wajib

- Keluaran mentah perintah verifikasi
- Kode keluar (rc) apa adanya, bukan hasil grep
- Potongan isi berkas bila berkas baru dibuat
- Tidak ada klaim tanpa bukti

## 8. Larangan

- Menulis berkas sebelum mengirim blok read-only
- Mengklaim tanpa bukti mentah
- Menulis parasite atau reframing di artefak tim
- Janji tanggal; semua "segera"
- Menghapus atau menulis ulang riwayat
- Commit saat gate gagal
