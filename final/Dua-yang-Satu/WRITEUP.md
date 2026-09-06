<!-- category: reverse | points: - -->
# Dua yang Satu

| | |
| :--- | :--- |
| **Challenge** | Dua yang Satu |
| **Kategori** | reverse |
| **Poin** | - |
| **Author** | - |
| **Connection** | file attachment: `kiri.bin`, `kanan.bin` |
| **Solver** | nexsus404 |
| **Status** | Solved |

> Dua berkas yang di-urutkan ulang. Gabungkan dengan operasi bitwise untuk membaca pesan.

![soal](img/01-recon.png)

---

## 1. Flag

```
TechtonicExpoCTF{gabung_xor_66394FFC}
```

> Flag **case-sensitive**. Tidak ada spasi/karakter tambahan saat submit.

![flag](img/04-flag.png)

---

## 2. Analisis Awal

- **Yang dikasih:** dua berkas mungil, `kiri.bin` dan `kanan.bin`, **masing-masing tepat 10 byte**. Plus sebuah arsip `identitas_utuh.zip` yang terkunci.
- **Observasi pertama:** `file` menyebut keduanya sebagai teks berkode aneh (`ISO-8859` dan `Non-ISO extended-ASCII`) — artinya isinya byte di luar ASCII, bukan teks sungguhan. Tidak ada header, tidak ada struktur.

```
kiri.bin   2e d9 98 3d de b7 67 b5 3e 4c
kanan.bin  49 b8 fa 48 b0 d0 38 cd 51 3e
```

- **Hipotesis awal:** deskripsi menyebut "operasi bitwise" untuk *menggabungkan* dua berkas. Dari semua operasi bitwise, hanya **XOR** yang masuk akal di sini. AND dan OR bersifat merusak — keduanya membuang informasi dan tidak bisa dibalik. XOR mempertahankan seluruh informasi dan merupakan pola one-time-pad standar: dua bagian yang masing-masing terlihat acak, tapi bermakna saat disatukan.

Panjang keduanya identik (10 byte) juga penunjuk kuat: XOR berpasangan menuntut panjang yang sama persis.

```bash
ls -l kiri.bin kanan.bin ; xxd kiri.bin ; xxd kanan.bin
```

![recon](img/01-recon.png)

---

## 3. Langkah Penyelesaian

### 3.1 XOR posisi-per-posisi

```bash
python3 -c "
a=open('kiri.bin','rb').read(); b=open('kanan.bin','rb').read()
x=bytes(i^j for i,j in zip(a,b))
print('kiri ^ kanan =', x)
print('ASCII printable semua?', all(32<=c<127 for c in x))
"
```

Hasil:

```
kiri ^ kanan = b'gabung_xor'
ASCII printable semua? True
```

Langsung terbaca, tanpa perlu perlakuan apa pun. Verifikasinya ada pada hasilnya sendiri: **10 dari 10 byte** jatuh di rentang ASCII printable dan membentuk kata Indonesia yang bermakna. XOR dua blob acak praktis mustahil menghasilkan itu secara kebetulan — peluang 10 byte acak semuanya printable saja sekitar 1 banding 30.000, apalagi tersusun jadi kata yang persis mendeskripsikan tekniknya sendiri.

![analisis](img/02-analisis.png)

### 3.2 Pesannya ternyata juga kunci arsip

Kata `gabung_xor` bukan sekadar pesan — ia password `identitas_utuh.zip` yang ikut dilampirkan:

```bash
unzip -o -P gabung_xor identitas_utuh.zip -d /tmp/cek_xor
cat /tmp/cek_xor/catatan.txt
```

Hasil: arsip terbuka berisi `catatan.txt`, `boarding.txt`, `boarding2.txt`, dan `tugu_pensil.jpg` — bahan untuk soal OSINT lanjutan. Ini mengonfirmasi ulang bahwa `gabung_xor` memang string yang dimaksud, bukan artefak kebetulan: server/arsip menerimanya sebagai password yang sah.

![zip](img/03-zip.png)

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| Python | 3.14.6 | XOR dua berkas (stdlib, tanpa dependensi) |
| xxd / file / ls | coreutils | recon awal, lihat byte mentah |
| unzip | 6.x | verifikasi pesan sebagai password arsip |
| Pillow | 12.3.0 | render screenshot langkah (`screenshot.py`) |

Seluruh kode yang dipakai ditulis lengkap di bawah ini — bukan potongan. Salin ke berkas dengan nama yang tertera lalu jalankan; tidak ada dependensi tersembunyi selain yang tercantum di tabel di atas.

### `solve.py`

> solver utama

```python
#!/usr/bin/env python3
"""Dua yang Satu - gabungkan dua berkas dengan XOR untuk memulihkan pesan.

Dua berkas berukuran sama yang masing-masing tampak acak = pola XOR berpasangan.
XOR bekerja per posisi, jadi bagian "di-urutkan ulang" pada deskripsi soal tidak
perlu dipulihkan: selama kedua berkas diacak dengan permutasi yang sama,
kiri[i] ^ kanan[i] tetap menghasilkan plain[i].
"""
import sys, zipfile

KIRI, KANAN, ARSIP = "kiri.bin", "kanan.bin", "identitas_utuh.zip"


def gabung(pa, pb):
    a, b = open(pa, "rb").read(), open(pb, "rb").read()
    if len(a) != len(b):
        sys.exit(f"[-] panjang beda ({len(a)} vs {len(b)}) - bukan pasangan XOR")
    return bytes(i ^ j for i, j in zip(a, b))


def main():
    pesan = gabung(KIRI, KANAN)
    print(f"[+] {KIRI} ^ {KANAN} = {pesan!r}")

    # Verifikasi: XOR dua blob acak nyaris mustahil menghasilkan ASCII penuh.
    # Peluang 10 byte acak semuanya printable ~ (95/256)^10 = 1 : 30.000.
    printable = sum(32 <= c < 127 for c in pesan)
    print(f"[+] byte printable: {printable}/{len(pesan)}")
    if printable != len(pesan):
        sys.exit("[-] hasil bukan teks bersih - operasi/pasangan salah")

    kunci = pesan.decode()
    print(f"[+] kunci     = {kunci}")
    print(f"[+] FLAG      = TechtonicExpoCTF{{{kunci}_66394FFC}}")

    # Konfirmasi kedua: pesan yang sama juga membuka arsip lanjutannya.
    try:
        with zipfile.ZipFile(ARSIP) as z:
            z.setpassword(kunci.encode())
            isi = z.namelist()
            z.read(isi[0])                      # lempar RuntimeError kalau salah
        print(f"[+] {ARSIP} terbuka dengan kunci yang sama: {', '.join(isi)}")
    except FileNotFoundError:
        print(f"[!] {ARSIP} tidak ada - lewati verifikasi arsip")
    except RuntimeError:
        print(f"[-] {ARSIP} menolak kunci - kunci mungkin salah")


if __name__ == "__main__":
    main()
```

### `screenshot.py`

> render screenshot tiap langkah dari keluaran perintah sungguhan

```python
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
```

### `_shot.py`

> helper render bersama, ada di root repo

```python
#!/usr/bin/env python3
"""
Helper screenshot bersama untuk writeup nexsus404.

Dua mode, keduanya merekam hal yang SUNGGUHAN terjadi - tidak ada teks yang
diketik ulang atau tampilan yang direka:

  terminal(...)  menjalankan perintahnya, menangkap stdout/stderr apa adanya,
                 lalu menggambar keluaran itu ke PNG bergaya terminal (Pillow).
  web(...)       memotret halaman langsung dari server target pakai Chromium
                 headless.
  web_html(...)  memotret BODY RESPONSE ASLI dari server (mis. hasil POST yang
                 tidak bisa dilakukan Chromium lewat URL). HTML-nya utuh dari
                 server, cuma disisipi <base> supaya CSS-nya tetap termuat.
"""
import os, subprocess, tempfile, textwrap
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/TTF/JetBrainsMono-Regular.ttf"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
BG, FG, PROMPT, CMD, JUDUL = "#0d1117", "#c9d1d9", "#3fb950", "#d29922", "#58a6ff"
UK, PAD, SPASI = 15, 22, 6


def jalankan(perintah, timeout=300):
    """Jalankan perintah sungguhan; kembalikan stdout+stderr apa adanya."""
    h = subprocess.run(perintah, shell=True, capture_output=True, text=True, timeout=timeout)
    return (h.stdout + h.stderr).rstrip("\n")


def terminal(folder, nama, judul, blok, sorot=(), lebar_maks=132):
    """blok = [(perintah, keluaran)]. sorot = kata yang diwarnai merah."""
    f = ImageFont.truetype(FONT, UK)
    fb = ImageFont.truetype(FONT, UK + 3)
    baris = [(judul, JUDUL, fb), ("", FG, f)]
    for perintah, keluaran in blok:
        for i, p in enumerate(textwrap.wrap(perintah, lebar_maks) or [""]):
            baris.append((("$ " if i == 0 else "  ") + p, CMD, f))
        for k in keluaran.split("\n"):
            for w in (textwrap.wrap(k, lebar_maks) or [""]):
                baris.append((w, "#f85149" if any(s in w for s in sorot) else FG, f))
        baris.append(("", FG, f))

    th = UK + SPASI
    lebar = max(int(ft.getlength(t)) for t, _, ft in baris) + PAD * 2
    img = Image.new("RGB", (max(lebar, 720), len(baris) * th + PAD * 2), BG)
    d = ImageDraw.Draw(img)
    for i, (t, w, ft) in enumerate(baris):
        x = PAD
        if t.startswith("$ "):
            d.text((x, PAD + i * th), "$", font=ft, fill=PROMPT)
            x += ft.getlength("$ ")
            t = t[2:]
        d.text((x, PAD + i * th), t, font=ft, fill=w)
    return _simpan(img, folder, nama)


def _chromium(url, keluar, ukuran="1100,900"):
    subprocess.run(["chromium", "--headless", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", f"--window-size={ukuran}",
                    f"--user-agent={UA}", f"--screenshot={keluar}", url],
                   capture_output=True, timeout=120)


def web(folder, nama, url, ukuran="1100,900"):
    """Potret halaman langsung dari server target."""
    p = _jalur(folder, nama)
    _chromium(url, p, ukuran)
    return _lapor(p)


def web_html(folder, nama, html, base, ukuran="1100,700"):
    """Potret body response ASLI dari server (untuk hasil POST)."""
    html = html.replace("<head>", f'<head><base href="{base}">', 1)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as t:
        t.write(html)
        tmp = t.name
    p = _jalur(folder, nama)
    _chromium("file://" + tmp, p, ukuran)
    os.unlink(tmp)
    return _lapor(p)


def _jalur(folder, nama):
    """img/ selalu relatif ke direktori kerja script pemanggil (tiap script
    sudah chdir ke foldernya sendiri), BUKAN ke lokasi _shot.py - supaya
    folder soal bisa dipindah-pindah tanpa gambar nyasar."""
    d = os.path.join(os.getcwd(), "img")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, nama + ".png")


def _simpan(img, folder, nama):
    p = _jalur(folder, nama)
    img.save(p)
    return _lapor(p)


def _lapor(p):
    if os.path.exists(p):
        w, h = Image.open(p).size
        print(f"  tersimpan: {os.path.relpath(p)}  ({w}x{h})")
    else:
        print(f"  GAGAL: {p}")
    return p
```

---

## 5. Trial-and-Error / Langkah yang Gagal

| # | Yang dicoba | Hasil | Kenapa gagal / berhasil |
| :-- | :--- | :--- | :--- |
| 1 | Baca tiap berkas sendiri-sendiri (`strings`, `file`) | Gagal | Masing-masing memang dirancang tak bermakna sendirian — itu inti skema XOR berpasangan. |
| 2 | Cari cara "mengurutkan ulang" byte lebih dulu, sesuai kalimat soal | Tidak perlu | Lihat catatan di bawah. |
| 3 | XOR posisi-per-posisi langsung | **Berhasil** | Langsung menghasilkan `gabung_xor`, 10/10 byte printable. |

**Catatan soal #2 — bagian "di-urutkan ulang" itu pengalih perhatian.** Kalimat soal membuat saya sempat mengira ada permutasi yang harus dibetulkan dulu sebelum XOR. Ternyata tidak: XOR bekerja *per posisi*, jadi `kiri[i] ^ kanan[i]` menghasilkan `plain[i]` terlepas dari bagaimana pasangan-pasangan itu diurutkan. Selama kedua berkas diacak dengan permutasi yang **sama**, urutannya tidak pernah perlu dipulihkan.

Kalau saya menuruti kalimat itu secara harfiah, saya akan membuang waktu mencari kunci pengurutan yang tidak pernah ada. Yang menyelamatkan: mencoba operasi termurah lebih dulu (satu baris XOR) sebelum membangun teori yang rumit.

---

## 6. Insight Utama & Teknik Unik

- **Kunci soal ini:** dua berkas berukuran **persis sama** yang masing-masing terlihat acak hampir selalu berarti XOR berpasangan. Ukuran identik itu sinyalnya, dan "operasi bitwise" di deskripsi mempersempitnya — dari AND/OR/XOR, hanya XOR yang tidak merusak informasi sehingga hanya XOR yang bisa "menggabungkan" tanpa kehilangan.
- **Teknik unik:** memakai *keterbacaan hasil* sebagai verifikasi. Tidak ada checksum atau flag literal untuk dicocokkan, tapi 10 dari 10 byte mendarat di ASCII printable dan membentuk kata bermakna — itu bukti statistik yang cukup kuat, diperkuat lagi ketika string yang sama diterima sebagai password zip.
- **Pelajaran:** jangan percaya setiap kata di deskripsi soal secara harfiah. "Di-urutkan ulang" terdengar seperti langkah wajib, padahal sifat komutatif XOR per posisi membuatnya tidak relevan. **Coba operasi paling murah lebih dulu** — kalau satu baris kode menyelesaikannya, teori rumit yang sudah disiapkan tidak pernah perlu diuji.
- Pesan yang dipulihkan sering kali bukan tujuan akhir. Di sini `gabung_xor` sekaligus jadi password arsip yang membuka rantai soal berikutnya, jadi selalu periksa apakah hasil dekripsi punya kegunaan kedua.

---
