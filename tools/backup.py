"""Salin basis data Hestia, sisakan 10 berkas terbaru."""
import glob
import os
import shutil
import time

d = "data/backup"
os.makedirs(d, exist_ok=True)
shutil.copy2("data/hestia.db", os.path.join(d, "hestia-%s.db" % time.strftime("%Y%m%d-%H%M%S")))
f = sorted(glob.glob(os.path.join(d, "*.db")))
for x in f[:-10]:
    os.remove(x)
print("backup: %d berkas tersimpan | terbaru: %s" % (min(len(f), 10), os.path.basename(f[-1])))
