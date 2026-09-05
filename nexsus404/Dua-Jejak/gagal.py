#!/usr/bin/env python3
"""Reproduksi percobaan yang GAGAL (lihat 'Yang gagal' di WRITEUP.md)."""
import struct, subprocess
import numpy as np
from PIL import Image

print("=== GAGAL 1: exiftool pada jejak_a, dikira berkas kosong ===")
out = subprocess.run(["exiftool", "jejak_a.png"], capture_output=True, text=True).stdout
print("  field yang mengandung comment/text:",
      [l for l in out.splitlines() if "omment" in l or "ext" in l] or "TIDAK ADA")
print("  -> output bersih. Gampang disimpulkan 'berkas ini kosong', padahal artinya")
print("     cuma 'tidak ada field yang exiftool kenali'.\n")

print("=== GAGAL 2: menyimpulkan ada data dari ukuran IDAT ===")
Image.fromarray(np.full((600, 800, 3), (100, 80, 90), np.uint8)).save("/tmp/polos.png")
def idat(p):
    d = open(p, "rb").read(); i, t = 8, 0
    while i < len(d):
        ln = struct.unpack(">I", d[i:i+4])[0]; typ = d[i+4:i+8]
        if typ == b"IDAT": t += ln
        i += 12 + ln
        if typ == b"IEND": break
    return t
a, b, c = idat("/tmp/polos.png"), idat("jejak_a.png"), idat("jejak_b.png")
print(f"  PNG satu warna murni : {a} byte  (pembanding yang saya buat sendiri)")
print(f"  jejak_a.png          : {b} byte  (+{b-a})")
print(f"  jejak_b.png          : {c} byte  (+{c-a})")
print("  -> selisihnya cuma ~150-200 byte. BUKAN anomali. Dugaan saya salah.")
print("     Kalau tidak saya uji, saya akan menulis alasan yang keliru di writeup.\n")

print("=== GAGAL 3: unpack LSB dengan bitorder yang salah ===")
arr = np.array(Image.open("jejak_a.png").convert("RGB"))
for order in ("little", "big"):
    d = np.packbits((arr[:, :, 0] & 1).flatten(), bitorder=order).tobytes()
    tanda = "  <- yang benar" if order == "big" else ""
    print(f"  {order:6}: {d[:34]!r}{tanda}")
print()

print("=== YANG BENAR-BENAR MEMBONGKAR: hitung nilai piksel unik ===")
for nm in ("jejak_a.png", "jejak_b.png"):
    x = np.array(Image.open(nm).convert("RGB"))
    for i, ch in enumerate("RGB"):
        u = np.unique(x[:, :, i])
        print(f"  {nm} {ch}: {len(u)} nilai {u}" + ("   <== beda 1, LSB dipakai" if len(u) == 2 else ""))
