#!/usr/bin/env python3
"""Screenshot langkah Identitas Utuh (OSINT). STATUS: BELUM SOLVED - kunci final
masih salah, jadi ini mendokumentasikan lapisan yang sudah terbuka saja.

Halaman web dipotret LANGSUNG dari server 168.110.219.59:5030.
Langkah 05 memotret BODY RESPONSE ASLI hasil POST password (Chromium tidak bisa
POST lewat URL, jadi response server disimpan sementara lalu dipotret).
"""
import sys, os, urllib.request, urllib.parse
_d = os.path.dirname(os.path.abspath(__file__))          # cari _shot.py ke atas
while _d != "/" and not os.path.exists(os.path.join(_d, "_shot.py")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)
from _shot import terminal, web, web_html, jalankan, UA

F, B = "Identitas-Utuh", "http://168.110.219.59:5030"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("Identitas Utuh:")

web(F, "01-soal", B + "/")
web(F, "02-manifest", B + "/manifest", "1100,700")

jalankan("rm -rf berkas && mkdir berkas && unzip -o -P gabung_xor identitas_utuh.zip -d berkas")
terminal(F, "03-metadata", "LANGKAH 1 - Metadata foto DARI ZIP (versi web sudah dibersihkan)", [
    ("exiftool berkas/tugu_pensil.jpg | grep -E 'Artist|Copyright|Comment'",
     jalankan("exiftool berkas/tugu_pensil.jpg 2>/dev/null | grep -E 'Artist|Copyright|Comment'")),
    ("cat berkas/boarding.txt berkas/boarding2.txt | grep -E 'Nama|Rute|Penerbangan'",
     jalankan("cat berkas/boarding.txt berkas/boarding2.txt | grep -E 'Nama|Rute|Penerbangan'")),
    ("# bandingkan: foto versi web metadata-nya KOSONG",
     jalankan(f"curl -s -A '{UA}' -o /tmp/web.jpg {B}/foto/tugu && "
              "echo -n 'tag EXIF versi web: ' && exiftool /tmp/web.jpg 2>/dev/null | grep -cE 'Artist|Copyright'")),
], sorot=("Waliyal", "HUZAN"))

terminal(F, "04-password", "LANGKAH 2 - Nama di metadata jadi password berkas terbatas", [
    ("# Artist='Waliyal' + boarding='W. HUZAN'  ->  coba 'huzan'",
     jalankan("""python3 -c "
import urllib.request, urllib.parse, re
B='http://168.110.219.59:5030/berkas/rahasia_perjalanan.txt'
UA={'User-Agent':'%s'}
for pw in ('salahbanget','huzan'):
    d=urllib.parse.urlencode({'kunci':pw}).encode()
    h=urllib.request.urlopen(urllib.request.Request(B,data=d,headers=UA),timeout=20).read().decode()
    pre=re.search(r'<pre>([\\s\\S]*?)</pre>',h)
    bad=re.search(r'class=.merah.[^>]*>([^<]+)',h)
    print(f'kunci={pw!r:15s} -> ' + (bad.group(1) if bad else 'BERHASIL'))
    if pre:
        for b in pre.group(1).strip().split(chr(10)): print('    '+b)
" """ % UA)),
], sorot=("Waliyal Huzan", "UPG"))

d = urllib.parse.urlencode({"kunci": "huzan"}).encode()
r = urllib.request.Request(B + "/berkas/rahasia_perjalanan.txt", data=d, headers={"User-Agent": UA})
web_html(F, "05-berkas-terbuka", urllib.request.urlopen(r, timeout=20).read().decode(), B)
print("Selesai. CATATAN: kunci final belum ketemu - belum ada 06-flag.")
