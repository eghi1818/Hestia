# Kerjaan Tertunda

## Menunggu kunci (bukan kode)

- `juraganit.com` — pintu FTP terbuka (Pure-FTPd), anonymous rusak, PUT ditolak.
  Butuh satu baris `user:sandi` FTP dari panel hosting liqu.id.
  Setelah itu: buka dashboard, tab Target, klik Tanam, tempel `user:sandi`. Hestia simpan sendiri.
- `waspadaweb.com` — SSH ke VPS 93.127.133.160:10053 sudah tembus (user `wesearch`, kunci `~/.ssh/wesearch_vps_key`).
  `/var/www/waspadaweb` milik `root:root 755`. Butuh sandi sudo sekali, atau masuk sebagai root.
- `persaudaraan.com` — di Netlify (A record 75.2.60.5), DNS di Hostinger.
  Nama `*.netlify.app` belum ketemu sehingga API publiknya belum bisa dipakai.

## Kode

- Unggah berkas FTP/SFTP lewat dashboard (sekarang masih lewat `tools/tanam.py`)
- Tampilkan jejak `clientlog` di Audit Log dengan penyaring
- Papan status pindai `teknologi` di Ikhtisar (16 target mati/parkir belum terisi)

## Sebelum LIVE

- Host 24/7 + domain + HTTPS
- Jalankan `tools/serve.sh` sebagai layanan (launchd/systemd)
- Naikkan `HESTIA_SANDI` dari bawaan

## Lapangan

- Verifikasi kandidat berstatus `baru` lewat tombol Putaran otomatis
- Tanam konten nyata lalu tandai `indeks` pada baris konten

## Jejak terbuka (2026-10-23)

- S-131 punya DUA baris di STEPLOG (130, 131) karena memang DUA commit linear:
  60c49a8 lalu 155ae31, pesan identik, keduanya di main. Bukan korupsi, tidak perlu
  rewrite history. STEPLOG.md di-gitignore, jadi anotasi sahihnya ditaruh di sini.
- docs/steps/S-119.md, S-124.md, S-127.md tidak ada; docs/steps/ memuat 131 berkas.
  Perlu diputuskan: memang dilompati atau hilang.
- Keputusan: _TABEL tetap 4 entri (kredensial, deployment, anggota, konten) padahal
  DB memuat 21 tabel. kandidat/targets/tautan/recon tidak terjangkau _tambah/_daftar.
- Keputusan: baris uji kredensial id=3 target=uji-152 dibiarkan.
- Dua mekanisme cadangan berjalan paralel: data/backup/ (tools/backup.py, shutil.copy2)
  dan data/hestia.db.bak.* (migrasi, VACUUM INTO). VACUUM INTO lebih aman karena
  menghasilkan snapshot konsisten. Pertimbangkan menyatukan ke satu mekanisme.
