#!/usr/bin/env python3
"""
Ambil screenshot LANGKAH ASLI penyelesaian Firmware Purba.

PENTING: setiap gambar di sini dirender dari stdout SUNGGUHAN hasil menjalankan
perintah pada berkas firmware_purba.bin saat script ini dieksekusi. Teksnya bukan
diketik ulang atau direka - script menjalankan perintahnya, menangkap keluarannya,
lalu menggambar keluaran itu apa adanya ke PNG bergaya terminal.

Beda dengan take_screenshots.py milik x0r yang memotret response web lewat
Playwright, soal ini murni forensik berkas lokal sehingga tidak ada halaman web
untuk dipotret - yang direkam adalah sesi terminal.

Pakai:  python3 screenshot.py
Hasil:  img/01-recon.png ... img/06-flag.png
"""
import os, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/TTF/JetBrainsMono-Regular.ttf"
BIN = "firmware_purba.bin"
OUT = "img"

# palet terminal gelap
BG, FG, PROMPT, CMD, JUDUL, SOROT = "#0d1117", "#c9d1d9", "#3fb950", "#d29922", "#58a6ff", "#f85149"
UK, PAD, SPASI = 15, 22, 6

def jalankan(perintah):
    """Jalankan perintah sungguhan, kembalikan stdout+stderr apa adanya."""
    h = subprocess.run(perintah, shell=True, capture_output=True, text=True)
    return (h.stdout + h.stderr).rstrip("\n")

def render(nama, judul, blok, lebar_maks=132):
    """blok = list of (perintah, keluaran). Gambar sebagai sesi terminal."""
    f = ImageFont.truetype(FONT, UK)
    fb = ImageFont.truetype(FONT, UK + 3)
    baris = []                                   # (teks, warna, font)
    baris.append((judul, JUDUL, fb))
    baris.append(("", FG, f))
    for perintah, keluaran in blok:
        for i, p in enumerate(textwrap.wrap(perintah, lebar_maks) or [""]):
            baris.append((("$ " if i == 0 else "  ") + p, CMD, f))
        for k in keluaran.split("\n"):
            for w in (textwrap.wrap(k, lebar_maks) or [""]):
                baris.append((w, SOROT if "chip_tua" in w else FG, f))
        baris.append(("", FG, f))

    tinggi_baris = UK + SPASI
    lebar = max(int(fb.getlength(t)) for t, _, fb_ in baris for fb in [fb_]) + PAD * 2
    img = Image.new("RGB", (max(lebar, 700), len(baris) * tinggi_baris + PAD * 2), BG)
    d = ImageDraw.Draw(img)
    for i, (t, w, ft) in enumerate(baris):
        x = PAD
        if t.startswith("$ "):                   # prompt hijau, perintah kuning
            d.text((x, PAD + i * tinggi_baris), "$", font=ft, fill=PROMPT)
            x += ft.getlength("$ ")
            t = t[2:]
        d.text((x, PAD + i * tinggi_baris), t, font=ft, fill=w)
    os.makedirs(OUT, exist_ok=True)
    img.save(f"{OUT}/{nama}.png")
    print(f"  tersimpan: {OUT}/{nama}.png  ({img.width}x{img.height})")

# ---- perintah-perintah yang BENAR-BENAR dijalankan ----------------------------

ENTROPI = f'''python3 -c "
import math, collections
d=open('{BIN}','rb').read(); B=256; s=[]
for i in range(0,len(d)-B+1,B):
    b=d[i:i+B]; c=collections.Counter(b)
    s.append((-sum(n/B*math.log2(n/B) for n in c.values()), i))
s.sort()
print('5 blok 256-byte entropi TERENDAH:')
for H,i in s[:5]: print(f'  {{i:#09x}}  H={{H:.3f}}')
print()
print('rata-rata seluruh berkas: H=%.3f' % (sum(H for H,_ in s)/len(s)))
print('titik tengah 1 MiB       = 0x80000')
"'''

TEKS = f'''python3 -c "
import re
d=open('{BIN}','rb').read()
for m in re.finditer(rb'[a-z_ ]{{7,}}', d):
    print(f'{{m.start():#09x}}  {{m.group().decode()!r}}')
"'''

HEX = f'''python3 -c "
d=open('{BIN}','rb').read()
for i in range(0,160,16):
    b=d[0x80000+i:0x80000+i+16]
    t=''.join(chr(c) if 32<=c<127 else '.' for c in b)
    print(f'{{0x80000+i:08x}}  {{b.hex(\\" \\")}}  |{{t}}|')
"'''

NOISE = f'''python3 -c "
import re
d=open('{BIN}','rb').read()
print('rentetan printable >=6 byte (tanpa filter):', len(re.findall(rb'[ -~]{{6,}}', d)))
print('setelah filter [a-z_ ]{{7,}}          :', len(re.findall(rb'[a-z_ ]{{7,}}', d)))
"'''

LANGKAH = [
    ("01-recon", "LANGKAH 1 - Recon: berkas apa ini?", [
        (f"ls -l {BIN}", jalankan(f"ls -l {BIN}")),
        (f"file {BIN}", jalankan(f"file {BIN}")),
        (f"du -b {BIN}", jalankan(f"du -b {BIN}")),
    ]),
    ("02-entropi", "LANGKAH 2 - Peta entropi: cari blok paling tidak acak", [
        ("python3 -c '<pindai entropi per blok 256-byte>'", jalankan(ENTROPI)),
    ]),
    ("03-noise", "LANGKAH 3 - Kenapa strings biasa gagal", [
        ("python3 -c '<hitung false positive>'", jalankan(NOISE)),
        (f"strings -n 6 {BIN} | wc -l", jalankan(f"strings -n 6 {BIN} | wc -l")),
    ]),
    ("04-temuan", "LANGKAH 4 - Filter teks sungguhan -> KUNCI", [
        ("python3 -c '<regex [a-z_ ]{7,} pada seluruh berkas>'", jalankan(TEKS)),
    ]),
    ("05-hexdump", "LANGKAH 5 - Hexdump di offset 0x80000", [
        ("python3 -c '<hexdump 0x80000>'", jalankan(HEX)),
    ]),
    ("06-flag", "LANGKAH 6 - Flag", [
        ("echo \"TechtonicExpoCTF{$(python3 -c \"" +
         f"import re;d=open('{BIN}','rb').read();print(re.search(rb'[a-z_]{{7,}}',d).group().decode())" +
         "\")_66394FFC}\"",
         jalankan(f'''echo "TechtonicExpoCTF{{$(python3 -c "import re;d=open('{BIN}','rb').read();print(re.search(rb'[a-z_]{{7,}}',d).group().decode())")_66394FFC}}"''')),
    ]),
]

if __name__ == "__main__":
    print("Merender screenshot dari keluaran perintah sungguhan...")
    for nama, judul, blok in LANGKAH:
        render(nama, judul, blok)
    print("Selesai. Semua teks di gambar adalah stdout asli saat script ini jalan.")
