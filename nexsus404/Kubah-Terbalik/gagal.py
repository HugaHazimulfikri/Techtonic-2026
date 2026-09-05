#!/usr/bin/env python3
"""Reproduksi percobaan yang GAGAL (lihat 'Yang gagal' di WRITEUP.md)."""
import urllib.request, urllib.error, re
H = "http://168.110.219.59:5016"
KARTU = "34bb4f272ce495247f66df02e7a85ac71c1100c7472a8e1b62e9c1235a23ca03e18c18db42ab52ad68f647aa3eda68f81951088e74311b41d536fee11bffa323"

def ambil(url, ua=True):
    hdr = {"User-Agent": "curl/8.5.0"} if ua else {}
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=10).read().decode()
    except urllib.error.HTTPError as e:
        return f"[HTTP {e.code}] " + e.read().decode()

def teks(t):
    return " ".join(re.sub(r"<[^>]*>", " ", t).split())

print("=== GAGAL 1: urllib tanpa User-Agent ===")
r = ambil(f"{H}/izin/buka?data={KARTU}", ua=False)
print(f"  {teks(r)[:90]}")
print("  -> server memfilter User-Agent. Sempat saya kira serangannya yang ditolak,")
print("     padahal curl untuk URL yang sama sudah berhasil.\n")

print("=== dengan User-Agent curl ===")
print(f"  {teks(ambil(f'{H}/izin/buka?data={KARTU}'))[-60:]}\n")

print("=== GAGAL 2: balik 0xFF tiap byte IV, harap merusak parsing ===")
for j in (0, 3, 7, 11, 15):
    m = bytearray(bytes.fromhex(KARTU)); m[j] ^= 0xFF
    print(f"  IV[{j:2}] -> {teks(ambil(f'{H}/izin/buka?data={bytes(m).hex()}'))[-42:]}")
print("  -> 16 dari 16 tetap 'tidak diakui', tidak ada yang jadi 'tidak terbaca'.")
print("     Gagal sebagai cara memetakan struktur, tapi membuktikan parsernya longgar.\n")

print("=== GAGAL 3: filter respons saya cari string yang salah ===")
DATA = bytes.fromhex("68616c616d616e3d7574616d61")
r = teks(ambil(f"{H}/ulur/buka?data={DATA.hex()}&tanda={'00'*32}"))
print(f"  respons tanda salah : {r[-40:]}")
print("  script saya mencari : 'tidak sah'")
print(f"  ada di respons?     : {'tidak sah' in r}")
print("  -> makanya script lapor HIT palsu. Saya menegasikan pola gagal,")
print("     bukan mencocokkan pola sukses.")
