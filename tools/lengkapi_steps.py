#!/usr/bin/env python3
"""Isi docs/steps/S-<n>.md dari git log untuk nomor yang belum punya berkas."""
import os, re, subprocess, sys

os.makedirs("docs/steps", exist_ok=True)
log = subprocess.run(["git", "log", "--format=%H%x09%ad%x09%s%x09%b%x1e", "--date=short"],
                     capture_output=True, text=True).stdout
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
        f.write("\ncatatan: dokumen ini dibuat menyusul (tutup.sh tidak dijalankan).\n")
    tulis.append(m.group(1))
print("ditulis:", sorted(tulis, key=int) or "tidak ada yang kurang")
