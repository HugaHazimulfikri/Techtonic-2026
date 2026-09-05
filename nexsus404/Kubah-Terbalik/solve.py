#!/usr/bin/env python3
"""
Kubah Terbalik - Techtonic Expo Vol.3 2026 (Cryptography, 750 pts)
Solver: nexsus404

Lapis 1: CBC bit-flipping  -> ubah admin=0 jadi admin=1 lewat IV
Lapis 2: SHA-256 length extension -> sambung &admin=1 tanpa tahu rahasianya
"""
import urllib.request, urllib.error, re
from sha256ext import sha256, md_pad

H = "http://168.110.219.59:5016"
UA = {"User-Agent": "curl/8.5.0"}
KARTU = bytes.fromhex("34bb4f272ce495247f66df02e7a85ac71c1100c7472a8e1b62e9c1235a23ca03"
                      "e18c18db42ab52ad68f647aa3eda68f81951088e74311b41d536fee11bffa323")
DATA = b"halaman=utama"
SIG  = "0be8eb5f8bc38356bbf06ad423ccf71581991159ccf49b133d7f50be0d72431e"

def get(u):
    try:
        return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=10).read().decode()
    except urllib.error.HTTPError as e:
        return e.read().decode()

def teks(u):
    return " ".join(re.sub(r"<[^>]*>", " ", get(u)).split())

# ---------- LAPIS 1: CBC bit-flipping ----------
# Kartu = IV || C1 || C2 || C3 (4 x 16 byte). Pada CBC: P[i] = D(C[i]) XOR C[i-1],
# jadi mengubah IV byte j membalik plaintext blok-0 byte j dengan delta yang sama.
# Plaintext blok 0 = "admin=0&..." -> byte ke-6 adalah digit '0' (0x30).
# XOR 0x01 mengubahnya jadi '1' (0x31) => admin=1.
POS, DELTA = 6, 0x01
kartu = bytearray(KARTU); kartu[POS] ^= DELTA
r1 = teks(f"{H}/izin/buka?data={bytes(kartu).hex()}")
print("[LAPIS 1] IV[6] ^= 0x01  ('0' -> '1')")
print("         ", r1[r1.find("//"):])

# ---------- LAPIS 2: SHA-256 length extension ----------
# tanda = SHA256(rahasia || data). Karena rahasia ada DI DEPAN dan SHA-256 itu
# Merkle-Damgard, state akhir = tanda bisa dipakai lanjut meng-hash data tambahan
# tanpa tahu rahasianya. Yang perlu ditebak hanya panjang rahasianya.
TAMBAH = b"&admin=1"
for slen in range(1, 65):
    L = slen + len(DATA)
    glue = md_pad(L)                       # padding asli yang jadi bagian pesan
    palsu = DATA + glue + TAMBAH
    tanda = sha256(TAMBAH, state=bytes.fromhex(SIG), prelen=L + len(glue)).hex()
    r2 = teks(f"{H}/ulur/buka?data={palsu.hex()}&tanda={tanda}")
    if "tidak cocok" in r2:
        continue
    print(f"\n[LAPIS 2] panjang rahasia = {slen} byte, sambung {TAMBAH.decode()!r}")
    print("         ", r2[r2.find("//"):])
    break
