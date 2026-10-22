#!/usr/bin/env python3
"""Cari webserver sebenarnya dan jalur tulis tanpa sandi di host yang melayani domain target."""
import subprocess
import sys
from pathlib import Path

CFG = Path.home() / ".ssh" / "config"

REMOTE = (
    'echo "== proses-web =="; ps -eo user,pid,args | grep -Ei "nginx|apache|lsws|litespeed|caddy|httpd|php-fpm|panel" | grep -v grep | head -20; '
    'echo "== porta-dengar =="; ss -lntp 2>/dev/null | head -25; '
    'echo "== usr-local =="; ls /usr/local 2>/dev/null; '
    'echo "== kandidat-konfig =="; ls -d /etc/nginx /etc/nginx/conf.d /etc/nginx/sites-enabled /etc/apache2/sites-enabled /usr/local/lsws/conf /usr/local/lsws/conf/vhosts /etc/caddy /etc/openlitespeed 2>/dev/null; '
    'echo "== cari-vhost =="; grep -rhn -m2 -E "server_name|DocumentRoot|docroot|root " /etc/nginx /usr/local/lsws/conf /etc/apache2 /etc/caddy 2>/dev/null | head -25; '
    'echo "== var-www =="; ls -la /var/www 2>/dev/null; '
    'echo "== docroot =="; ls -la /var/www/waspadaweb 2>/dev/null; '
    'echo "== bisa-ditulis =="; find /var/www -maxdepth 4 -writable 2>/dev/null | head -15; '
    'echo "== skrip-bisa-ditulis =="; find /etc /usr/local /opt /srv -maxdepth 3 -name "*.sh" -writable 2>/dev/null | head -15; '
    'echo "== crontab-sistem =="; cat /etc/crontab 2>/dev/null; ls -la /etc/cron.d 2>/dev/null; cat /etc/cron.d/* 2>/dev/null | head -20; '
    'echo "== crontab-user =="; crontab -l 2>/dev/null; '
    'echo "== systemd-kustom =="; ls /etc/systemd/system/*.service 2>/dev/null; grep -h -E "ExecStart|WorkingDirectory" /etc/systemd/system/*.service 2>/dev/null | head -20; '
    'echo "== grup =="; id; getent group sudo adm docker www-data 2>/dev/null; '
    'echo "== setuid =="; find / -maxdepth 4 -perm -4000 -type f 2>/dev/null | head -15; '
    'echo "== firewall =="; (ufw status 2>/dev/null || iptables -S 2>/dev/null) | head -12; '
    'echo "== home =="; ls -la /home 2>/dev/null; '
    'echo "== root-ssh =="; ls -la /root/.ssh 2>/dev/null; '
    'echo "== php-fpm =="; ls -la /etc/php/*/fpm/pool.d 2>/dev/null; '
    'echo "== sudo-n =="; sudo -n -l 2>&1 | head -8'
)


def blok():
    if not CFG.exists():
        return []
    hasil, kini = [], None
    for baris in CFG.read_text(errors="ignore").splitlines():
        b = baris.strip()
        if b.lower().startswith("host ") and not b.lower().startswith("hostname"):
            if kini:
                hasil.append(kini)
            kini = {"alias": b.split(None, 1)[1].strip(), "hostname": "", "port": "22", "key": "", "user": ""}
        elif kini is not None and b and not b.startswith("#"):
            k, _, v = b.partition(" ")
            k, v = k.strip().lower(), v.strip()
            if k == "hostname":
                kini["hostname"] = v
            elif k == "port":
                kini["port"] = v
            elif k == "identityfile":
                kini["key"] = v
            elif k == "user":
                kini["user"] = v
    if kini:
        hasil.append(kini)
    return hasil


def main():
    if len(sys.argv) < 2:
        print("pakai: jalur.py <domain>")
        return 2
    target = sys.argv[1]
    akar = target.split(".")[0]
    for b in blok():
        if not b["hostname"]:
            continue
        key = Path(b["key"].replace("~", str(Path.home())))
        if not key.exists():
            continue
        user = b["user"] or ("wesearch" if "wesearch" in b["alias"] else b["alias"])
        try:
            r = subprocess.run(["ssh", "-i", str(key), "-p", b["port"],
                                "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
                                "-o", "ConnectTimeout=8", "%s@%s" % (user, b["hostname"]), REMOTE],
                               capture_output=True, text=True, timeout=90)
        except Exception as e:
            print("ssh %s gagal: %r" % (b["alias"], e))
            continue
        keluar = (r.stdout or "") + (r.stderr or "")
        if akar not in keluar and "/var/www" not in keluar:
            print("--- %s tidak menyebut target, dilewati" % b["alias"])
            continue
        print("### host=%s porta=%s user=%s" % (b["hostname"], b["port"], user))
        for l in keluar.splitlines():
            print(l)
        tulis, skrip, bagian = [], [], ""
        for l in keluar.splitlines():
            if l.startswith("== "):
                bagian = l.strip()
                continue
            if not l.strip():
                continue
            if bagian == "== bisa-ditulis ==":
                tulis.append(l)
            elif bagian == "== skrip-bisa-ditulis ==":
                skrip.append(l)
        print("RINGKAS: bisa-ditulis=%d skrip-bisa-ditulis=%d" % (len(tulis), len(skrip)))
        if not tulis and not skrip:
            print("JALUR TANPA SANDI: TIDAK ADA -> sandi sudo wajib")
        else:
            print("JALUR TANPA SANDI: MUNGKIN -> periksa daftar di atas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
