#!/usr/bin/env python3
"""Reproduksi percobaan yang GAGAL (lihat 'Yang gagal' di WRITEUP.md)."""
import numpy as np
from PIL import Image

a = np.array(Image.open("piksel_senyap.png").convert("RGB"))
bits = ((a[:, :, 2] >> 1) & 1).flatten()          # plane B1, yang benar

print("=== GAGAL 1: mengira payload B1 adalah byte terpaket ===")
for order in ("big", "little"):
    d = np.packbits(bits, bitorder=order).tobytes()
    print(f"  bitorder={order:6}: {d[:44]!r}")
d = np.packbits(((a[:, :, 2].T >> 1) & 1).flatten(), bitorder="big").tobytes()
print(f"  column-major   : {d[:44]!r}")
print("  -> tiga percobaan, semuanya biner acak. Asumsinya yang salah:")
print("     payload B1 itu GAMBAR TEKS, bukan byte. Peta blok sudah bilang begitu,")
print("     saya cuma tidak membacanya dulu.\n")

print("=== GAGAL 2: berhenti di LSB merah (jebakan) ===")
import re
d = np.packbits((a[:, :, 0] & 1).flatten(), bitorder="big").tobytes()
m = re.findall(rb"[ -~]{12,}", d)[:1]
print(f"  R0: {m[0][:60].decode()}")
print("  -> 'kunci_salah_arah_2026'. Kalau saya submit ini, salah. Namanya juga salah arah.\n")

print("=== PEMBANDING: cara yang benar (render jadi citra) ===")
p = ((bits.reshape(512, 512)) * 255).astype(np.uint8)
Image.fromarray(p).save("plane_B1.png")
print("  plane B1 di-render -> plane_B1.png, teks 'lsb_tersembunyi' terbaca")
