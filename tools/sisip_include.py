#!/usr/bin/env python3
"""Sisipkan satu baris ke dalam blok server yang memuat penanda tertentu.
Pakai: sisip_include.py <berkas> <penanda> <baris-yang-disisipkan>
Fail-closed: galat bila penanda tidak ditemukan."""
import sys
berkas, penanda, baris = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(berkas).read()
if baris.strip() in s:
    print("  sudah ada, dilewati"); sys.exit(0)
i = s.index(penanda)
try:
    j = s.rindex("server {", 0, i)
except ValueError:
    j = s.rindex("server", 0, i)
k = s.index("{", j) + 1
open(berkas, "w").write(s[:k] + "\n    " + baris + s[k:])
print("  disisipkan pada blok server baris %d" % (s[:j].count("\n") + 1))
