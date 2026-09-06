#!/usr/bin/env python3
"""Simulasi lokal: bandingkan binary search versi integer // vs Fraction.
Pakai kunci RSA buatan sendiri supaya oracle bisa dijalankan offline."""
from fractions import Fraction
import random, sympy

random.seed(1337)
gagal_int = gagal_frac = 0
for percobaan in range(20):
    p, q = sympy.randprime(2**255, 2**256), sympy.randprime(2**255, 2**256)
    N, E = p*q, 65537
    d = pow(E, -1, (p-1)*(q-1))
    m0 = int.from_bytes(b"kunci_gudang", "big")
    c0 = pow(m0, E, N)
    orc = lambda ct: pow(ct, d, N) & 1     # oracle paritas lokal
    dua = pow(2, E, N)

    # versi A: integer floor division
    lo, hi, ct = 0, N, c0
    for _ in range(N.bit_length()):
        ct = ct * dua % N
        mid = (lo + hi) // 2
        if orc(ct): lo = mid
        else:       hi = mid
    if pow(hi, E, N) != c0: gagal_int += 1

    # versi B: Fraction (eksak)
    lo, hi, ct = Fraction(0), Fraction(N), c0
    for _ in range(N.bit_length()):
        ct = ct * dua % N
        mid = (lo + hi) / 2
        if orc(ct): lo = mid
        else:       hi = mid
    if pow(int(hi), E, N) != c0: gagal_frac += 1

print(f"versi integer //  : {gagal_int}/20 gagal")
print(f"versi Fraction    : {gagal_frac}/20 gagal")
