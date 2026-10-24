# SKILL AGENT - Hestia (salinan dari dokumen niat, 2026-10-24)

## HestiaCP
- API REST: POST http://<host>:8083/api/ dengan parameter hash, returncode, cmd, argN
- hash = sha256(user + sandi + returncode) ... (lihat dokumen asli untuk bentuk pasti)
- v-add-web-domain-redirect USER DOMAIN REDIRECT [HTTPCODE]
  PENTING: redirect HestiaCP adalah LEVEL-DOMAIN, bukan level-URL.
  Untuk per-URL: file include /home/<user>/conf/web/<domain>/nginx.conf_<nama>

## Kenyataan di lapangan (terverifikasi sesi ini)
- TIDAK ADA HestiaCP di waspadaweb.com (nginx polos) maupun persaudaraan.com (Netlify)
- juraganit.com = LiteSpeed cPanel, port 22 tertutup, hanya FTP 21 (Pure-FTPd TLS)
- member.mcs.co.id = WHMCS (client area), liqu.id = reseller
- persaudaraan.com = Netlify, apex A 75.2.60.5, nama *.netlify.app tidak ada di DNS

## Driver yang terbukti
- nginx lewat container lxc privileged (hx) + sudo NOPASSWD: 301/410 terbukti live
- nginx -t dan reload TIDAK bisa di dalam container (Alpine musl vs host glibc)
- /run dan /proc host tidak terlihat di container (bind tidak rekursif)

## Operasional
- jangan pakai rfind("}") untuk config dengan lebih dari satu blok server
- Cloudflare bisa meng-cache 301; verifikasi origin DAN publik
- zsh TIDAK memecah variabel tak dikutip: pakai array
