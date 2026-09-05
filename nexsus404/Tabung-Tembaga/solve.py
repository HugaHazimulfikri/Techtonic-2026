#!/usr/bin/env python3
"""
Tabung Tembaga - Techtonic Expo Vol.3 2026 (Cryptography, 689 pts)
Solver: nexsus404

Dua jalur, dua-duanya dijalankan:
  A) Cube root langsung  - jalan karena m^3 < n (tidak ada reduksi modulo)
  B) Franklin-Reiter     - jalur yang dimaksud soal, dipakai sebagai verifikasi
"""
from params import n, e, c1, c2

def icbrt(x):
    """akar pangkat tiga bilangan bulat, binary search (tanpa float)"""
    lo, hi = 0, 1 << ((x.bit_length() + 2) // 3 + 2)
    while lo < hi:
        mid = (lo + hi) // 2
        if mid ** 3 < x: lo = mid + 1
        else: hi = mid
    return lo

def tobytes(m):
    return m.to_bytes((m.bit_length() + 7) // 8, "big")

print(f"n  : {n.bit_length()} bit")
print(f"c1 : {c1.bit_length()} bit   (ambang n^(1/3) = {n.bit_length()//3} bit)")
print(f"c1 < n^(1/3)? {c1.bit_length() < n.bit_length()//3}  -> m^3 tidak pernah dikurangi mod n\n")

# ---------- A. cube root langsung ----------
m1 = icbrt(c1)
assert m1 ** 3 == c1, "c1 bukan kubik sempurna"
print("[A] CUBE ROOT LANGSUNG")
print(f"    m1 = {m1}")
print(f"    m1^3 == c1 : {m1**3 == c1}")
print(f"    pesan      : {tobytes(m1).decode()}\n")

# ---------- B. Franklin-Reiter related-message ----------
# m2 = m1 + 1, jadi m1 adalah akar bersama dari:
#     g1(x) = x^3       - c1
#     g2(x) = (x+1)^3   - c2
# gcd(g1, g2) di Z_n[x] runtuh jadi (x - m1), sehingga m1 = -suku_konstanta.
def polymod(a, b, n):
    """sisa pembagian polinom a mod b di Z_n[x] (koefisien indeks 0 = pangkat 0)"""
    a = a[:]
    inv = pow(b[-1], -1, n)
    while len(a) >= len(b) and any(a):
        while a and a[-1] == 0: a.pop()
        if len(a) < len(b): break
        k = (a[-1] * inv) % n
        for i in range(len(b)):
            a[len(a) - len(b) + i] = (a[len(a) - len(b) + i] - k * b[i]) % n
        while a and a[-1] == 0: a.pop()
    return a

def polygcd(a, b, n):
    while any(b):
        a, b = b, polymod(a, b, n)
        while b and b[-1] == 0: b.pop()
    return a

g1 = [(-c1) % n, 0, 0, 1]                       # x^3 - c1
g2 = [(1 - c2) % n, 3, 3, 1]                    # (x+1)^3 - c2 = x^3+3x^2+3x+1-c2
g  = polygcd(g1, g2, n)
g  = [(x * pow(g[-1], -1, n)) % n for x in g]   # jadikan monik
m1b = (-g[0]) % n

print("[B] FRANKLIN-REITER (a = 1)")
print(f"    derajat gcd = {len(g)-1}  -> {'(x - m1), akar tunggal' if len(g)-1 == 1 else 'GAGAL'}")
print(f"    m1 = {m1b}")
print(f"    cocok dengan jalur A : {m1b == m1}")
print(f"    pesan      : {tobytes(m1b).decode()}\n")

print("PESAN 1 :", tobytes(m1).decode())
print("PESAN 2 :", tobytes(icbrt(c2)).decode(), "(m1 + 1, byte terakhir naik satu)")
print("\nFLAG    : TechtonicExpoCTF{" + tobytes(m1).decode() + "_66394FFC}")
