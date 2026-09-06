#!/usr/bin/env python3
"""Jerat Peladen - RSA LSB (parity) oracle attack."""
import re, sys, time
from fractions import Fraction
import urllib.request
from params import n, e, c

BASE = "http://168.110.219.59:5017"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
POLA = re.compile(r'// BISIKAN.*?<p class="abu">(\w+)</p>', re.S)

def bisik(ct, retry=5):
    """Tanya paritas m = ct^d mod n. True = ganjil (LSB 1)."""
    for i in range(retry):
        try:
            req = urllib.request.Request(f"{BASE}/bisik?c={ct}", headers={"User-Agent": UA})
            body = urllib.request.urlopen(req, timeout=20).read().decode()
            m = POLA.search(body)
            if not m:
                raise ValueError("jawaban tak terbaca: " + body[:200])
            return m.group(1) == "ganjil"
        except Exception as ex:
            if i == retry - 1:
                raise
            time.sleep(1 + i)

# sanity check: m=1 ganjil, m=2 genap
assert bisik(1) is True,  "sanity m=1 gagal"
assert bisik(pow(2, e, n)) is False, "sanity m=2 gagal"
print("[+] sanity oracle OK (m=1 ganjil, m=2 genap)", flush=True)

dua_e = pow(2, e, n)
lo, hi = Fraction(0), Fraction(n)
ct = c
bits = n.bit_length()
t0 = time.time()

for i in range(bits):
    ct = (ct * dua_e) % n          # kalikan m dengan 2
    tengah = (lo + hi) / 2
    if bisik(ct):                  # ganjil -> terjadi reduksi mod n -> m di paruh atas
        lo = tengah
    else:                          # genap -> tanpa reduksi -> m di paruh bawah
        hi = tengah
    if (i + 1) % 64 == 0:
        print(f"    {i+1:3d}/{bits} bit  ({time.time()-t0:.0f}s)", flush=True)

m = int(hi)
print(f"[+] selesai {bits} query dalam {time.time()-t0:.0f}s", flush=True)

for kand in (m, m - 1, m + 1):
    if pow(kand, e, n) == c:
        print(f"[+] VERIFIED: pow(m,e,n) == c  (m = hi{kand-m:+d})")
        m = kand
        break
else:
    print("[!] verifikasi gagal, m mungkin meleset", file=sys.stderr)

data = m.to_bytes((m.bit_length() + 7) // 8, "big")
print("[+] m (hex) =", hex(m))
print("[+] plaintext =", repr(data))
open("pesan.bin", "wb").write(data)
