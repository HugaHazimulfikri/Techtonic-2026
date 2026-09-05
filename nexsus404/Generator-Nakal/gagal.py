#!/usr/bin/env python3
"""Reproduksi percobaan yang GAGAL (lihat 'Yang gagal sebelum berhasil' di WRITEUP.md)."""
from math import gcd
from functools import reduce

X = [987654321012345678, 6729977692791834322, 6578750652915850225,
     16888812019745501733, 2381187045401728115, 16223185267011201142,
     249113833186806331, 7114183187174364876]
t = [X[i+1]-X[i] for i in range(len(X)-1)]
u = [t[i+2]*t[i] - t[i+1]**2 for i in range(len(t)-2)]
M_BENAR = 18446744073709551557

print("=== GAGAL 1: asumsi m = 2^64 (default LCG paling umum) ===")
print(f"  t[0] = {t[0]}   genap? {t[0] % 2 == 0}")
try:
    pow(t[0], -1, 2**64)
    print("  invers ketemu (tidak seharusnya)")
except ValueError as ex:
    print(f"  ValueError: {ex}")
print("  -> t[0] genap, tidak punya invers mod 2^64. Untung gagal dengan exception,")
print("     bukan diam-diam mengeluarkan a dan c yang salah.\n")

print("=== GAGAL 2: GCD dari terlalu sedikit keluaran ===")
for k in range(1, len(u)+1):
    g = abs(reduce(gcd, u[:k]))
    if g == M_BENAR:
        print(f"  {k+3} keluaran ({k} nilai u): {g}  <- TEPAT m")
    else:
        print(f"  {k+3} keluaran ({k} nilai u): {g}")
        print(f"       = m x {g//M_BENAR}, jadi KELIPATAN m, bukan m")
        print(f"       panjangnya {g.bit_length()} bit padahal generatornya 64-bit  <- ini sinyalnya")
print()
print("  -> hasil 4 keluaran kelihatan seperti jawaban: satu bilangan besar, tanpa error.")
print("     Yang membongkarnya cuma panjang bit yang tidak masuk akal.")
