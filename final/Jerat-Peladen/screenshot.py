#!/usr/bin/env python3
"""Screenshot langkah penyelesaian Jerat Peladen (RSA LSB oracle).

Halaman web dipotret LANGSUNG dari server 168.110.219.59:5017.
Keluaran terminal adalah stdout sungguhan saat script ini dijalankan.
CATATAN: langkah 4 menjalankan solve.py = 511 request ke server panitia.
"""
import sys, os
_d = os.path.dirname(os.path.abspath(__file__))          # cari _shot.py ke atas
while _d != "/" and not os.path.exists(os.path.join(_d, "_shot.py")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)
from _shot import terminal, web, jalankan

F, B = "Jerat-Peladen", "http://168.110.219.59:5017"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Jerat Peladen:")
web(F, "01-soal", B + "/")

terminal(F, "02-recon", "LANGKAH 1 - Recon: ukuran modulus", [
    ("cat params.py", jalankan("cat params.py")),
    ("python3 -c \"from params import n,e,c; print('n bits =',n.bit_length()); print('c < n  =',c<n)\"",
     jalankan("python3 -c \"from params import n,e,c; print('n bits =',n.bit_length()); print('c < n  =',c<n)\"")),
])

kal = ("UA='%s'\n" % UA +
       "curl -s -A \"$UA\" \"%s/bisik?c=1\"                       # m=1 -> harus ganjil\n" % B +
       "curl -s -A \"$UA\" \"%s/bisik?c=$(python3 -c 'from params import n,e; print(pow(2,e,n))')\"  # m=2 -> harus genap" % B)
terminal(F, "03-analisis", "LANGKAH 2 - Kalibrasi oracle dengan plaintext yang sudah diketahui", [
    (kal, jalankan(f"""UA='{UA}'
echo -n 'c=1      -> '; curl -s -A "$UA" "{B}/bisik?c=1" | grep -oP '(?<=abu">)\\w+'
echo -n 'c=2^e    -> '; curl -s -A "$UA" "{B}/bisik?c=$(python3 -c 'from params import n,e; print(pow(2,e,n))')" | grep -oP '(?<=abu">)\\w+'""")),
], sorot=("ganjil", "genap"))

terminal(F, "04-exploit", "LANGKAH 3 - Binary search 511 bit lewat oracle paritas", [
    ("python3 solve.py", jalankan("python3 solve.py", timeout=400)),
], sorot=("VERIFIED", "penuh", "kunci_gudang"))

web(F, "05-flag", B + "/gudang?kata=kunci_gudang", "1100,600")
print("Selesai.")
