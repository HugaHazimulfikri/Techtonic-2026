#!/usr/bin/env python3
"""
Piksel Senyap - Techtonic Expo Vol.3 2026 (Digital Forensics, 500 pts)
Solver: nexsus404

Tiga tahap:
  1) statistik tiap bit-plane  -> cari plane yang bukan noise
  2) render plane berkonten    -> baca teks aslinya
  3) unpack ASCII tiap plane   -> temukan string umpan
"""
import numpy as np
from PIL import Image
import re

IMG = "piksel_senyap.png"
CH = "RGB"
a = np.array(Image.open(IMG).convert("RGB"))
print(f"[*] {IMG} -> {a.shape[1]}x{a.shape[0]} RGB\n")

# --- 1. cari plane yang menyimpang dari noise -------------------------------
# noise murni: tiap bit-plane rasio bit-1 ~= 0.5 dan merata di semua blok.
print("[1] deviasi maksimum per blok 64x64 (>0.05 = ada konten)")
hits = []
for c in range(3):
    for b in range(8):
        p = ((a[:, :, c] >> b) & 1).astype(float)
        dev = np.abs(p.reshape(8, 64, 8, 64).mean(axis=(1, 3)) - 0.5).max()
        if dev > 0.05:
            hits.append((c, b))
            print(f"    {CH[c]}{b}: {dev:.4f}  <== ADA KONTEN")
print()

# --- 2. render plane berkonten jadi gambar ----------------------------------
print("[2] render plane berkonten")
for c, b in hits:
    out = f"plane_{CH[c]}{b}.png"
    Image.fromarray((((a[:, :, c] >> b) & 1) * 255).astype(np.uint8)).save(out)
    print(f"    -> {out}  (buka: teks flag terbaca di sini)")
print()

# --- 3. unpack ASCII tiap plane, buka umpannya ------------------------------
print("[3] string ASCII terpaket di tiap plane")
pat = re.compile(rb"[ -~]{12,}")
for c in range(3):
    for b in range(8):
        bits = ((a[:, :, c] >> b) & 1).flatten()
        data = np.packbits(bits, bitorder="big").tobytes()
        for m in pat.findall(data)[:1]:
            print(f"    {CH[c]}{b}: {m[:60].decode('ascii', 'replace')}")
