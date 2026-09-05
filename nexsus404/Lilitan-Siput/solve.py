#!/usr/bin/env python3
"""
Lilitan Siput - Techtonic Expo Vol.3 2026 (Cryptography, 500 pts)
Solver: nexsus404

Dua lapis, dibongkar dari luar ke dalam:
  lapis 2  transposisi kolom 6, urutan baca 3-1-5-0-4-2  (urutan diumumkan)
  lapis 1  Vigenere kunci 5 huruf                        (kunci RAHASIA -> dipecahkan)
"""
import itertools

CT    = "LLUZQXMRIQGVNTUCJGGCAXFCIXLCCNJHRIAHNUIXDUIQYYDYVQQLES"
ORDER = [3, 1, 5, 0, 4, 2]
NC    = 6
ROWS  = len(CT) // NC          # 54 / 6 = 9, grid penuh tanpa baris parsial

# frekuensi huruf bahasa Indonesia (%) - dipakai chi-square per coset
FREQ = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
 [19.0,2.5,1.0,4.0,8.5,0.3,3.5,2.0,8.0,1.0,4.5,3.2,3.8,9.5,2.0,2.8,0.1,4.5,4.5,5.5,5.0,0.3,0.8,0.1,1.2,0.2]))
NGRAM = ["YANG","ADALAH","KUNCI","DAN","KAN","NGA","AN","NG","ITU","INI","DENGAN","UNTUK","ADA","KATA"]

# ---------- lapis 2: balikkan transposisi kolom ----------
# ciphertext = kolom[3] ++ kolom[1] ++ kolom[5] ++ kolom[0] ++ kolom[4] ++ kolom[2]
def undo_transposisi(ct):
    kol = {}
    for i, c in enumerate(ORDER):
        kol[c] = ct[i*ROWS:(i+1)*ROWS]
    return "".join(kol[c][r] for r in range(ROWS) for c in range(NC))

# ---------- lapis 1: pecahkan Vigenere ----------
def chi(s):
    return sum((s.count(ch)/len(s)*100 - FREQ[ch])**2 / max(FREQ[ch], 0.1) for ch in FREQ)

def skor(t):
    return sum(t.count(g) * len(g)**2 for g in NGRAM)

def pecah_vigenere(mid, klen=5, top=4):
    """tiap coset = Caesar. ambil `top` geseran terbaik per coset (chi-square),
       lalu adu semua kombinasinya pakai skor n-gram bahasa Indonesia."""
    kandidat = []
    for i in range(klen):
        coset = mid[i::klen]
        urut = sorted(range(26),
                      key=lambda s: chi("".join(chr((ord(c)-65-s) % 26 + 65) for c in coset)))
        kandidat.append(urut[:top])
    hasil = []
    for combo in itertools.product(*kandidat):
        pt = "".join(chr((ord(c)-65-combo[i % klen]) % 26 + 65) for i, c in enumerate(mid))
        hasil.append((skor(pt), "".join(chr(65+s) for s in combo), pt))
    return max(hasil)

# ---------- jalankan ----------
mid = undo_transposisi(CT)
print("ciphertext            :", CT)
print("setelah transposisi   :", mid)

sc, key, pt = pecah_vigenere(mid)
print(f"\nkunci Vigenere        : {key}   (skor n-gram {sc})")
print("plaintext             :", pt)

# ---------- verifikasi: enkripsi ulang harus identik ----------
v = "".join(chr((ord(c)-65 + ord(key[i % 5])-65) % 26 + 65) for i, c in enumerate(pt))
kol = ["".join(v[r*NC + c] for r in range(ROWS)) for c in range(NC)]
ulang = "".join(kol[c] for c in ORDER)
print(f"\nre-enkripsi == ciphertext asli : {ulang == CT}")
assert ulang == CT

print("\nbaca kalimatnya       : LILIT PUTAR DUA | SEDANG TERKUNCI DALAM DUA LAPIS | RANGKAI KEMBALI")
print("kata kunci            : lilit_putar_dua")
print("\nFLAG : TechtonicExpoCTF{lilit_putar_dua_66394FFC}")
