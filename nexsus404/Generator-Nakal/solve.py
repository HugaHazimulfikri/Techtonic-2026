#!/usr/bin/env python3
"""
Generator Nakal - Techtonic Expo Vol.3 2026 (Cryptography, 653 pts)
Solver: nexsus404

LCG: x[n+1] = (a*x[n] + c) mod m, ketiga parameter rahasia.
Pulihkan m -> a -> c dari deret keluaran, lalu ramal x8.
"""
from math import gcd
from functools import reduce

X = [987654321012345678, 6729977692791834322, 6578750652915850225,
     16888812019745501733, 2381187045401728115, 16223185267011201142,
     249113833186806331, 7114183187174364876]

print("deret keluaran:")
for i, v in enumerate(X): print(f"  x{i} = {v}")

# --- 1. pulihkan m ---------------------------------------------------------
# t[i] = x[i+1] - x[i]  =>  t[i+1] = a*t[i] (mod m)
# maka  u[i] = t[i+2]*t[i] - t[i+1]^2  ==  0 (mod m)  untuk semua i.
# gcd dari beberapa u[i] hampir pasti tepat m.
t = [X[i+1] - X[i] for i in range(len(X)-1)]
u = [t[i+2]*t[i] - t[i+1]**2 for i in range(len(t)-2)]
m = abs(reduce(gcd, u))
print(f"\n[1] m = {m}   ({m.bit_length()} bit)")

# --- 2. pulihkan a ---------------------------------------------------------
# t[1] = a*t[0] (mod m)  =>  a = t[1] * t[0]^-1 (mod m)
a = (t[1] * pow(t[0], -1, m)) % m
print(f"[2] a = {a}")

# --- 3. pulihkan c ---------------------------------------------------------
c = (X[1] - a*X[0]) % m
print(f"[3] c = {c}")

# --- 4. verifikasi ke seluruh deret ----------------------------------------
ok = all((a*X[i] + c) % m == X[i+1] for i in range(len(X)-1))
print(f"\n[4] verifikasi seluruh deret: {'LULUS' if ok else 'GAGAL'}")
assert ok

x8 = (a*X[-1] + c) % m
print(f"\nx8 (ramalan) = {x8}")

# --- 5. kirim ramalan ke mesin ---------------------------------------------
import urllib.request, urllib.error, re
u = f"http://168.110.219.59:5014/tebak?angka={x8}"
req = urllib.request.Request(u, headers={"User-Agent": "curl/8.5.0"})
try:
    html = urllib.request.urlopen(req, timeout=10).read().decode()
except urllib.error.HTTPError as ex:
    html = ex.read().decode()
r = " ".join(re.sub(r"<[^>]*>", " ", html).split())
print("[5] respons mesin:", r[r.find("//"):])
