#!/usr/bin/env python3
"""Sinkronkan jejak ke keadaan nyata: dokumen langkah yang kurang + SESSION_STATE.

Dijalankan otomatis oleh tools/tutup.sh. Aman diulang.
"""
import os, re, subprocess, sys, time


def jalankan(*argv):
    return subprocess.run(argv, capture_output=True, text=True).stdout.strip()


def lengkapi_steps():
    os.makedirs("docs/steps", exist_ok=True)
    log = jalankan("git", "log", "--format=%H%x09%ad%x09%s%x09%b%x1e", "--date=short")
    tulis = []
    for catatan in log.split("\x1e"):
        b = catatan.strip().split("\t")
        if len(b) < 3:
            continue
        h, tanggal, subjek = b[0], b[1], b[2]
        body = b[3] if len(b) > 3 else ""
        m = re.match(r"^S-(\d+)\s*:\s*(.+)$", subjek)
        if not m:
            continue
        berkas = "docs/steps/S-%s.md" % m.group(1)
        if os.path.exists(berkas):
            continue
        with open(berkas, "w", encoding="utf-8") as f:
            f.write("# S-%s - %s\n\ncommit: %s\ntanggal: %s\n" % (m.group(1), m.group(2), h[:12], tanggal))
            if body.strip():
                f.write("\n%s\n" % body.strip())
        tulis.append(m.group(1))
    return tulis


def tulis_session_state():
    head = jalankan("git", "log", "-1", "--oneline")
    status = jalankan("git", "status", "--porcelain") or "(bersih)"
    n_rute = len(re.findall(r"^@app\.", open("app/main.py", encoding="utf-8").read(), re.M))
    n_bukti = len([f for f in os.listdir("docs/evidence") if re.match(r"^S-\d+\.txt$", f)])
    n_steps = len([f for f in os.listdir("docs/steps") if re.match(r"^S-\d+\.md$", f)])
    log = jalankan("git", "log", "--oneline", "-12")
    sisa = ""
    if os.path.exists("docs/SISA-KERJA.md"):
        sisa = open("docs/SISA-KERJA.md", encoding="utf-8").read().strip()

    with open("docs/SESSION_STATE.md", "w", encoding="utf-8") as f:
        f.write("# SESSION STATE - Hestia\n\n")
        f.write("Dibuat otomatis oleh tools/sync_jejak.py pada %s.\n" % time.strftime("%Y-%m-%d %H:%M"))
        f.write("JANGAN sunting berkas ini untuk sisa kerja - sunting docs/SISA-KERJA.md.\n\n")
        f.write("HEAD: %s\n" % head)
        f.write("branch: main | kotor: %s\n" % status)
        f.write("rute app/main.py: %s | berkas bukti: %s | dokumen langkah: %s\n\n" % (n_rute, n_bukti, n_steps))
        f.write("## 12 commit terakhir\n\n```\n%s\n```\n\n" % log)
        f.write("## SISA KERJA\n\n%s\n\n" % sisa)
        f.write("## Cara melanjutkan\n\n")
        f.write("bash tools/step_guard.sh && bash tools/resume.sh\n")
        f.write("baca docs/NEXT.md, docs/evidence/ terbaru, lalu kerjakan sisa kerja di atas.\n")
    return head, n_rute, n_bukti, n_steps


def main():
    tulis = lengkapi_steps()
    head, r, b, s = tulis_session_state()
    print("dokumen langkah ditulis:", tulis or "tidak ada")
    print("SESSION_STATE:", head, "| rute", r, "| bukti", b, "| steps", s)
    if "--resume" in sys.argv and os.path.exists("tools/siapkan_newchat.sh"):
        subprocess.run(["bash", "tools/siapkan_newchat.sh"])


if __name__ == "__main__":
    main()
