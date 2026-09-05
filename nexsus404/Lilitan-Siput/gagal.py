#!/usr/bin/env python3
"""Reproduksi percobaan yang GAGAL (lihat 'Yang gagal' di WRITEUP.md)."""
CT = 'LLUZQXMRIQGVNTUCJGGCAXFCIXLCCNJHRIAHNUIXDUIQYYDYVQQLES'
ORDER = [3,1,5,0,4,2]

def undo(ct, order):
    kol = {}
    for i, c in enumerate(order): kol[c] = ct[i*9:(i+1)*9]
    return ''.join(kol[c][r] for r in range(9) for c in range(6))

def vig(t, k):
    return ''.join(chr((ord(c)-ord(k[i % len(k)])) % 26 + 65) for i, c in enumerate(t))

mid = undo(CT, ORDER)

print("=== GAGAL 1: menebak kunci dari tema soal ===")
for key in ('SIPUT', 'LILIT', 'JEJAK', 'IRAMA'):
    print(f"  {key} -> {vig(mid, key)}")
print("  -> semuanya sampah. Kunci sebenarnya RINDU, tidak berhubungan dengan tema.")
print("     Perhatikan baris LILIT: 5 huruf pertamanya justru 'RINDU'. Saya tidak sadar.\n")

print("=== GAGAL 2: konvensi transposisi yang salah ===")
kol = {}
for i, c in enumerate(ORDER): kol[c] = CT[i*9:(i+1)*9]
mid_salah = ''.join(kol[c][r] for c in range(6) for r in range(9))   # kolom-lalu-baris
print(f"  benar : {mid}")
print(f"  salah : {mid_salah}")
print("  -> skor n-gram konvensi salah cuma 17, yang benar 50. Selisihnya setajam itu,")
print("     jadi skor n-gram sekaligus bisa dipakai MEMILIH konvensi, bukan cuma kunci.\n")

print("=== PEMBANDING: kunci yang benar ===")
print(f"  RINDU -> {vig(mid, 'RINDU')}")
