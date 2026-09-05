#!/usr/bin/env python3
"""Reproduksi percobaan yang GAGAL di soal ini (lihat bagian 'Yang gagal' di WRITEUP.md)."""
from params import n, e, c1, c2

print("=== GAGAL 1: akar kubik pakai float ===")
akar = round(c1 ** (1/3))
print(f"  round(c1 ** (1/3)) = {akar}")
print(f"  akar**3 == c1 ?      {akar**3 == c1}")
print(f"  selisihnya           {abs(akar**3 - c1)}")
print("  -> float 64-bit cuma 53 bit mantissa, c1 butuh 333 bit. Meleset jauh,")
print("     tapi TIDAK error. Ketahuan hanya karena dicek balik dengan **3.\n")

def icbrt(x):
    lo, hi = 0, 1 << ((x.bit_length()+2)//3 + 2)
    while lo < hi:
        mid = (lo+hi)//2
        if mid**3 < x: lo = mid+1
        else: hi = mid
    return lo

print("=== GAGAL 2: asumsi c1 adalah hasil reduksi mod n ===")
print(f"  bit c1            = {c1.bit_length()}")
print(f"  ambang n^(1/3)    = {n.bit_length()//3}")
print(f"  c1 di bawah ambang? {c1.bit_length() < n.bit_length()//3}")
print("  -> kalau diasumsikan sudah ter-reduksi, saya akan mengejar akar kubik")
print("     modular yang sebenarnya tidak pernah ada.\n")

print("=== PEMBANDING: binary search (yang benar) ===")
m1 = icbrt(c1)
print(f"  icbrt(c1)   = {m1}")
print(f"  m1**3 == c1 ? {m1**3 == c1}")
print(f"  pesan       = {m1.to_bytes((m1.bit_length()+7)//8,'big').decode()}")
