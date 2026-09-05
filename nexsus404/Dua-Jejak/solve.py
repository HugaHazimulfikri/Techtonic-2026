#!/usr/bin/env python3
"""
Dua Jejak - Techtonic Expo Vol.3 2026 (OSINT, 464 pts)
Solver: nexsus404

Tiga lapis bukti yang harus disatukan:
  1) tEXt chunk PNG di jejak_b  -> base64
  2) LSB channel merah jejak_a  -> nama pemilik
  3) LSB channel merah jejak_b  -> lokasi (konfirmasi "lokasi sama")
"""
import base64, struct
import numpy as np
from PIL import Image

FILES = ("jejak_a.png", "jejak_b.png")

print("=== catatan panitia ===")
print(open("analisis.txt").read().strip(), "\n")

# ---------- 1. chunk PNG ----------
print("=== chunk PNG ===")
teks = {}
for nm in FILES:
    d = open(nm, "rb").read(); i = 8; found = []
    while i < len(d):
        ln = struct.unpack(">I", d[i:i+4])[0]
        typ = d[i+4:i+8].decode("latin1")
        if typ in ("tEXt", "iTXt", "zTXt"):
            key, _, val = d[i+8:i+8+ln].partition(b"\x00")
            found.append((key.decode(), val.decode()))
            teks[nm] = val.decode()
        i += 12 + ln
        if typ == "IEND": break
    print(f"  {nm}: {found if found else 'tidak ada chunk teks'}")

for nm, v in teks.items():
    print(f"  -> base64 di {nm}: {v}")
    print(f"     decode      : {base64.b64decode(v).decode()}")

# ---------- 2. deteksi modulasi piksel ----------
print("\n=== nilai piksel unik (kunci penemuan) ===")
for nm in FILES:
    a = np.array(Image.open(nm).convert("RGB"))
    for c, ch in enumerate("RGB"):
        u = np.unique(a[:, :, c])
        tanda = "  <== 2 nilai, beda 1 -> LSB dipakai" if len(u) == 2 else ""
        print(f"  {nm} {ch}: {len(u)} nilai {u[:4]}{tanda}")

# ---------- 3. baca LSB merah ----------
print("\n=== payload LSB channel merah ===")
for nm in FILES:
    a = np.array(Image.open(nm).convert("RGB"))
    d = np.packbits((a[:, :, 0] & 1).flatten(), bitorder="big").tobytes()
    pesan = d.split(b"\x7f\x7f\x7f")[0].decode()
    print(f"  {nm}: {pesan!r}")

print("\n=== kesimpulan ===")
print("  jejak_a  -> pemilik bernama Rani, asal Semarang")
print("  jejak_b  -> lokasi kota lama Semarang (cocok: 'lokasi sama')")
print("  tEXt     -> nama konsisten: rani_desa")
print("\nFLAG : TechtonicExpoCTF{rani_desa_66394FFC}")
