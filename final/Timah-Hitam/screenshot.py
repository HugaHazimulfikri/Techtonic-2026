#!/usr/bin/env python3
"""Screenshot langkah penyelesaian Timah Hitam (pwn: format string + stack overflow).

Semua teks adalah stdout SUNGGUHAN dari perintah yang dijalankan script ini,
termasuk eksploit yang benar-benar menembak server 168.110.219.59:5026.
"""
import sys, os
_d = os.path.dirname(os.path.abspath(__file__))          # cari _shot.py ke atas
while _d != "/" and not os.path.exists(os.path.join(_d, "_shot.py")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)
from _shot import terminal, jalankan

F = "Timah-Hitam"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("Timah Hitam:")

terminal(F, "01-recon", "LANGKAH 1 - Recon: semua proteksi aktif", [
    ("file timah_hitam.bin", jalankan("file timah_hitam.bin")),
    ("checksec --file=timah_hitam.bin", jalankan("checksec --file=timah_hitam.bin 2>&1 | head -8")),
], sorot=("Canary", "PIE", "NX"))

terminal(F, "02-analisis", "LANGKAH 2 - Dua celah sesuai deskripsi soal", [
    ("# menu 5 'Lapor' -> printf(buf) tanpa format string = FORMAT STRING",
     jalankan("r2 -q -A -c 'pdf @ fcn.000017b7' timah_hitam.bin 2>/dev/null "
              "| sed 's/\\x1b\\[[0-9;]*m//g' | grep -E 'lea rax, \\[format\\]|call sym.imp.printf|read' | head -6")),
    ("# menu 6 'Buka kunci' -> buffer 0x30 tapi read() 0x80 = STACK OVERFLOW",
     jalankan("r2 -q -A -c 'pdf @ fcn.000019bb' timah_hitam.bin 2>/dev/null "
              "| sed 's/\\x1b\\[[0-9;]*m//g' | grep -E 'sub rsp|lea rax, \\[buf\\]|mov edx, 0x80|call sym.imp.read' | head -6")),
])

terminal(F, "03-tersembunyi", "LANGKAH 3 - Fungsi tersembunyi 0x1a1d menghitung kunci sendiri", [
    ("objdump -d -M intel --start-address=0x1a1d --stop-address=0x1a52 timah_hitam.bin | tail -8",
     jalankan("objdump -d -M intel --start-address=0x1a1d --stop-address=0x1a52 timah_hitam.bin | tail -8")),
    ("# pecahkan XOR-nya: plain[i] = enc[i] ^ ((i+1)*0x2d + 0x11)",
     jalankan("""python3 -c "
import struct
b=bytearray(struct.pack('<Q',0x183e409ab0f60e4e))
b[7:11]=struct.pack('<I',0x6ea6c518)   # DWORD di rbp-0x24 MENIMPA byte indeks 7
print('enc   =', b.hex(' '))
print('kunci =', bytes(b[i]^(((i+1)*0x2d+0x11)&0xff) for i in range(11)).decode())
" """)),
], sorot=("penuh_racun",))

terminal(F, "04-exploit", "LANGKAH 4 - Eksploit lokal (leak canary + PIE, lalu overflow)", [
    ("python3 solve.py", jalankan("python3 solve.py", timeout=200)),
], sorot=("BENAR", "penuh_racun"))

terminal(F, "05-flag", "LANGKAH 5 - Eksploit ke server panitia", [
    ("python3 solve.py 168.110.219.59:5026", jalankan("python3 solve.py 168.110.219.59:5026", timeout=200)),
], sorot=("BENAR", "penuh_racun"))
print("Selesai.")
