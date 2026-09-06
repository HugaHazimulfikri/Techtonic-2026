#!/usr/bin/env python3
"""Screenshot langkah penyelesaian "Dua yang Satu" (kiri.bin ^ kanan.bin).

Semua teks adalah stdout SUNGGUHAN dari perintah yang dijalankan script ini.
"""
import sys, os
_d = os.path.dirname(os.path.abspath(__file__))          # cari _shot.py ke atas
while _d != "/" and not os.path.exists(os.path.join(_d, "_shot.py")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)
from _shot import terminal, jalankan

F = "Dua-yang-Satu"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("Dua yang Satu:")

terminal(F, "01-recon", "LANGKAH 1 - Dua berkas, masing-masing cuma 10 byte", [
    ("ls -l kiri.bin kanan.bin", jalankan("ls -l kiri.bin kanan.bin")),
    ("xxd kiri.bin", jalankan("xxd kiri.bin")),
    ("xxd kanan.bin", jalankan("xxd kanan.bin")),
])

terminal(F, "02-analisis", "LANGKAH 2 - XOR posisi-per-posisi (tanpa perlu permutasi)", [
    ("""python3 -c "
a=open('kiri.bin','rb').read(); b=open('kanan.bin','rb').read()
x=bytes(i^j for i,j in zip(a,b))
print('kiri ^ kanan =', x)
print('ASCII printable semua?', all(32<=c<127 for c in x))
" """, jalankan("""python3 -c "
a=open('kiri.bin','rb').read(); b=open('kanan.bin','rb').read()
x=bytes(i^j for i,j in zip(a,b))
print('kiri ^ kanan =', x)
print('ASCII printable semua?', all(32<=c<127 for c in x))
" """)),
], sorot=("gabung_xor",))

terminal(F, "03-zip", "LANGKAH 3 - Pesan itu juga password arsip lanjutannya", [
    ("unzip -o -P gabung_xor identitas_utuh.zip -d /tmp/cek_xor && cat /tmp/cek_xor/catatan.txt",
     jalankan("unzip -o -P gabung_xor identitas_utuh.zip -d /tmp/cek_xor 2>&1 | tail -5 && echo '--- catatan.txt ---' && cat /tmp/cek_xor/catatan.txt")),
])

terminal(F, "04-flag", "LANGKAH 4 - Flag", [
    ("""echo "TechtonicExpoCTF{$(python3 -c "
print(bytes(i^j for i,j in zip(open('kiri.bin','rb').read(),open('kanan.bin','rb').read())).decode())")_66394FFC}" """,
     jalankan("""echo "TechtonicExpoCTF{$(python3 -c "
print(bytes(i^j for i,j in zip(open('kiri.bin','rb').read(),open('kanan.bin','rb').read())).decode())")_66394FFC}" """)),
], sorot=("TechtonicExpoCTF",))
print("Selesai.")
