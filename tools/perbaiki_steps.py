#!/usr/bin/env python3
"""Buat ulang dokumen langkah yang hilang, dari berkas buktinya.

Dipakai karena judul commit lama memakai penamaan F-<m> tanpa S-<n>, sehingga sync_jejak
tidak bisa menurunkan nomor langkah. Idempoten: hanya membuat yang belum ada.
"""
import re
import subprocess
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parents[1]


def commit_pembuat(berkas):
    h = subprocess.run(["git", "log", "--diff-filter=A", "--pretty=%h", "--", berkas],
                       capture_output=True, text=True, cwd=str(AKAR)).stdout.strip().splitlines()
    return h[-1] if h else "(tidak diketahui)"


def judul_dari(berkas):
    try:
        baris = Path(AKAR / berkas).read_text(encoding="utf-8", errors="replace").strip().splitlines()
    except Exception:
        return "langkah"
    if not baris:
        return "langkah"
    t = re.sub(r"^(BLOK|S-\d+)\s*[:/-]?\s*", "", baris[0]).strip()
    return t or "langkah"


def main():
    buat = 0
    ev = sorted((AKAR / "docs" / "evidence").glob("S-*.txt"))
    for e in ev:
        nomor = int(e.stem.split("-")[1])
        if nomor < 218:
            continue
        doc = AKAR / "docs" / "steps" / (e.stem + ".md")
        if doc.exists():
            continue
        rel = str(e.relative_to(AKAR))
        doc.write_text(
            "# %s - %s\n\n- commit: %s\n- bukti: %s\n"
            "- catatan: dibuat menyusul oleh tools/perbaiki_steps.py (judul commit lama memakai penamaan F-<m> tanpa S-<n>).\n"
            % (e.stem, judul_dari(rel), commit_pembuat(rel), rel),
            encoding="utf-8")
        buat += 1
        print("  dibuat:", doc.name, "|", judul_dari(rel)[:60])
    print("  total dibuat:", buat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
