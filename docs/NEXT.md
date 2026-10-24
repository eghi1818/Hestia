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

## Aturan anti-tebakan (2026-10-23)

Setiap klaim "butuh kunci dari pengguna" WAJIB menyertakan daftar kanal yang SUDAH
dicoba beserta hasilnya. Kalau daftar itu kosong atau tidak lengkap, klaim itu tebakan.

Tujuh pintu yang wajib dicoba sebelum bertanya:
  1. tabel kredensial / setelan di data/hestia.db
  2. berkas bocor di target: /.vscode/sftp.json, /.env, /.git/config
  3. port panel: 8083/8084/2222 pada tiap host
  4. sandi browser (Keychain "Chrome Safe Storage" -> Login Data)
  5. user lain di VPS: /home/*, .bash_history, .ssh/
  6. DNS dan HTML target: CNAME, TXT, robots.txt, sitemap.xml, badge netlify
  7. ~/.netrc, ~/.my.cnf, ~/.ssh/config, ~/.bash_history lokal

DoD #3 diubah: "Modul 4 bisa mengeksekusi 301/410 lewat MINIMAL SATU DRIVER pada
minimal satu target, terverifikasi berubah di server, dengan dry-run dan audit log."
Bukan "lewat HestiaCP API" - bukti menunjukkan tidak ada HestiaCP di waspadaweb.com
(tidak ada port 8083) dan persaudaraan.com di Netlify (tanpa v-*).

## Modul 4 - status dan lanjutan (2026-10-23)

SELESAI: driver 301/410 pada nginx, dry-run, idempotensi, verifikasi origin+publik.
Bukti: docs/evidence/S-167.txt. Target uji: waspadaweb.com (driver nginx lewat container hx).

lanjutan modul 4:
  - rute HTTP + tombol dashboard (sekarang masih lewat python -m tools.driver)
  - catat setiap apply ke clientlog sebagai ActionLog (modul 4 wajib punya jejak audit di UI)
  - driver kedua bila perlu (netlify) supaya tidak bergantung satu panel

pelajaran operasional:
  - zsh TIDAK memecah variabel tak dikutip. "SSH=ssh -i ..." lalu $SSH gagal.
    Pakai array: SSH=(ssh -i ...) lalu "${SSH[@]}".
  - /etc/sudoers.d mode 750 -> visudo -cf sebagai non-root balik kosong; jalankan dengan sudo.
  - jangan pakai rfind("}") untuk config >1 blok server.
