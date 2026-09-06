<!-- category: crypto | points: - -->
# Jerat Peladen

| | |
| :--- | :--- |
| **Challenge** | Jerat Peladen |
| **Kategori** | crypto |
| **Poin** | - |
| **Author** | - |
| **Connection** | http://168.110.219.59:5017/ |
| **Solver** | nexsus404 |
| **Status** | Solved |

> Peladen ini memegang kunci rahasia di dalam tabung RSA, tapi ia terlalu banyak bicara. Setiap kali disodori angka, ia hanya membalas satu hal: apakah hasil pembukaannya genap atau ganjil.
>
> Satu bit per jawaban terdengar sepele. Tapi dari ribuan bisikan kecil itu, seluruh pesan bisa disusun kembali. Pangkal pesan menyimpan kata sandi gudang.
>
> Kata sandi itu lalu membuka gudang di ujung perjalanan, tempat kunci terakhir menunggu.

![soal](img/01-soal.png)

---

## 1. Flag

```
TechtonicExpoCTF{jerat_lsb_berlapis_66394FFC}
```

> Flag **case-sensitive**. Tidak ada spasi/karakter tambahan saat submit.

![flag diterima](img/05-flag.png)

---

## 2. Analisis Awal

- **Yang dikasih:** satu service HTTP di `http://168.110.219.59:5017/` berisi `n`, `e`, `c`, plus dua endpoint: `/bisik?c=...` dan `/gudang?kata=...`.
- **Observasi pertama:** `/bisik` mengembalikan tepat satu kata — `genap` atau `ganjil`. Itu bukan pesan error, itu **paritas dari hasil dekripsi**. Server dengan sukarela membocorkan LSB dari `c^d mod n` untuk ciphertext apa pun yang saya kirim.
- **Hipotesis awal:** ini **RSA LSB (parity) oracle attack**. Kalau saya bisa menanyakan paritas `m` untuk ciphertext pilihan saya sendiri, saya bisa mengalikan plaintext dengan 2 berulang kali dan melakukan binary search pada nilai `m` — tanpa perlu memfaktorkan `n` sama sekali.

Kenapa hipotesis itu langsung kuat: RSA bersifat *homomorphic* terhadap perkalian. `(c · 2^e) mod n` mendekripsi menjadi `(2m) mod n`. Nilai `2m` selalu genap, jadi kalau oracle menjawab **ganjil**, satu-satunya penjelasan adalah terjadi reduksi modulo — artinya `2m > n`, artinya `m > n/2`. Satu bit jawaban = satu bit posisi `m`.

Perintah recon paling awal:

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
curl -s -A "$UA" http://168.110.219.59:5017/
```

Hasil: halaman parameter, `n` = 511 bit, `e` = 65537, `c < n`.

![recon](img/02-recon.png)

---

## 3. Langkah Penyelesaian

### 3.1 Rekam parameter dan cek ukurannya

`params.py`:

```python
n = 6682764709973167036946049701211903120437113287577349111212467596058858742508078964195459986429833628450564838432660462469348985968359623292925433644729943
e = 65537
c = 5812302952503080065017368916479880836704948815091623009626511897423953357353715014657215167264460510609979240699551562949522354078288213435296810308965727
```

```bash
python3 -c "from params import n,e,c; print(n.bit_length(), c.bit_length(), c<n)"
```

Hasil: `511 511 True`. Modulus 511 bit → butuh **511 query** untuk mempersempit `m` sampai satu nilai.

### 3.2 Kalibrasi oracle sebelum dipakai serius

Saya tidak mau membakar 511 query di atas asumsi yang salah, jadi saya uji oracle dengan dua plaintext yang sudah saya tahu jawabannya. `c = 1` mendekripsi jadi `m = 1` (ganjil), dan `c = 2^e mod n` mendekripsi jadi `m = 2` (genap).

```bash
curl -s -A "$UA" "http://168.110.219.59:5017/bisik?c=1"
curl -s -A "$UA" "http://168.110.219.59:5017/bisik?c=$(python3 -c 'from params import n,e; print(pow(2,e,n))')"
```

Hasil: `ganjil` lalu `genap`. Oracle jujur dan arah interpretasinya benar.

![temuan](img/03-analisis.png)

### 3.3 Binary search 511 bit

Invariannya: pertahankan interval `[lo, hi)` yang pasti memuat `m`. Di iterasi ke-`i` saya kirim `c · 2^(i·e) mod n`, yang mendekripsi jadi `2^i · m mod n`.

- jawaban **genap** → tidak ada reduksi mod → `m` ada di paruh **bawah** → `hi = tengah`
- jawaban **ganjil** → terjadi reduksi mod → `m` ada di paruh **atas** → `lo = tengah`

```bash
python3 solve.py
```

Hasil:

```
[+] sanity oracle OK (m=1 ganjil, m=2 genap)
     64/511 bit  (4s)
    ...
    448/511 bit  (30s)
[+] selesai 511 query dalam 34s
[+] VERIFIED: pow(m,e,n) == c  (m = hi+0)
[+] m (hex) = 0x6b756e63695f677564616e67
[+] plaintext = b'kunci_gudang'
```

Saya tidak berhenti di "hasilnya kelihatan seperti teks". Solver mengenkripsi ulang kandidatnya dan membandingkan dengan `c` asli — `pow(m, e, n) == c` cocok persis, jadi `m` yang direkonstruksi memang benar, bukan kebetulan yang mirip ASCII.

### 3.4 Buka gudang

"Pangkal pesan menyimpan kata sandi gudang" — plaintextnya pendek, jadi seluruh pesan itu sendiri kata sandinya.

```bash
curl -s -A "$UA" "http://168.110.219.59:5017/gudang?kata=kunci_gudang" \
  | sed -e 's|</p>|</p>\n|g' -e 's/<[^>]*>//g' | grep -v '^\s*$'
```

Hasil:

```
Gudang Terbuka// JERAT PELADEN// KUNCI AKHIR
Gudang terbuka. Bendera di tanganmu: jerat_lsb_berlapis
```

![exploit](img/04-exploit.png)

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| Python | 3.14.6 | solver LSB oracle |
| `fractions.Fraction` | stdlib | batas binary search eksak (lihat bagian 5) |
| `urllib.request` | stdlib | 511 query berurutan ke oracle |
| curl | - | recon awal + buka `/gudang` |
| sympy | 1.14.0 | bangkitkan kunci RSA lokal untuk uji pembulatan |

Seluruh kode yang dipakai ditulis lengkap di bawah ini — bukan potongan. Salin ke berkas dengan nama yang tertera lalu jalankan; tidak ada dependensi tersembunyi selain yang tercantum di tabel di atas.

### `params.py`

> parameter soal, dipisah supaya bisa langsung di-import solver

```python
# Jerat Peladen - Techtonic Expo Vol.3 2026 (Cryptography)
# Service: http://168.110.219.59:5017/
n = 6682764709973167036946049701211903120437113287577349111212467596058858742508078964195459986429833628450564838432660462469348985968359623292925433644729943
e = 65537
c = 5812302952503080065017368916479880836704948815091623009626511897423953357353715014657215167264460510609979240699551562949522354078288213435296810308965727
```

### `solve.py`

> solver utama

```python
#!/usr/bin/env python3
"""Jerat Peladen - RSA LSB (parity) oracle attack."""
import re, sys, time
from fractions import Fraction
import urllib.request
from params import n, e, c

BASE = "http://168.110.219.59:5017"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"
POLA = re.compile(r'// BISIKAN.*?<p class="abu">(\w+)</p>', re.S)

def bisik(ct, retry=5):
    """Tanya paritas m = ct^d mod n. True = ganjil (LSB 1)."""
    for i in range(retry):
        try:
            req = urllib.request.Request(f"{BASE}/bisik?c={ct}", headers={"User-Agent": UA})
            body = urllib.request.urlopen(req, timeout=20).read().decode()
            m = POLA.search(body)
            if not m:
                raise ValueError("jawaban tak terbaca: " + body[:200])
            return m.group(1) == "ganjil"
        except Exception as ex:
            if i == retry - 1:
                raise
            time.sleep(1 + i)

# sanity check: m=1 ganjil, m=2 genap
assert bisik(1) is True,  "sanity m=1 gagal"
assert bisik(pow(2, e, n)) is False, "sanity m=2 gagal"
print("[+] sanity oracle OK (m=1 ganjil, m=2 genap)", flush=True)

dua_e = pow(2, e, n)
lo, hi = Fraction(0), Fraction(n)
ct = c
bits = n.bit_length()
t0 = time.time()

for i in range(bits):
    ct = (ct * dua_e) % n          # kalikan m dengan 2
    tengah = (lo + hi) / 2
    if bisik(ct):                  # ganjil -> terjadi reduksi mod n -> m di paruh atas
        lo = tengah
    else:                          # genap -> tanpa reduksi -> m di paruh bawah
        hi = tengah
    if (i + 1) % 64 == 0:
        print(f"    {i+1:3d}/{bits} bit  ({time.time()-t0:.0f}s)", flush=True)

m = int(hi)
print(f"[+] selesai {bits} query dalam {time.time()-t0:.0f}s", flush=True)

for kand in (m, m - 1, m + 1):
    if pow(kand, e, n) == c:
        print(f"[+] VERIFIED: pow(m,e,n) == c  (m = hi{kand-m:+d})")
        m = kand
        break
else:
    print("[!] verifikasi gagal, m mungkin meleset", file=sys.stderr)

data = m.to_bytes((m.bit_length() + 7) // 8, "big")
print("[+] m (hex) =", hex(m))
print("[+] plaintext =", repr(data))
open("pesan.bin", "wb").write(data)
```

### `uji_pembulatan.py`

> uji lokal Fraction vs integer // (lihat bagian 5)

```python
#!/usr/bin/env python3
"""Simulasi lokal: bandingkan binary search versi integer // vs Fraction.
Pakai kunci RSA buatan sendiri supaya oracle bisa dijalankan offline."""
from fractions import Fraction
import random, sympy

random.seed(1337)
gagal_int = gagal_frac = 0
for percobaan in range(20):
    p, q = sympy.randprime(2**255, 2**256), sympy.randprime(2**255, 2**256)
    N, E = p*q, 65537
    d = pow(E, -1, (p-1)*(q-1))
    m0 = int.from_bytes(b"kunci_gudang", "big")
    c0 = pow(m0, E, N)
    orc = lambda ct: pow(ct, d, N) & 1     # oracle paritas lokal
    dua = pow(2, E, N)

    # versi A: integer floor division
    lo, hi, ct = 0, N, c0
    for _ in range(N.bit_length()):
        ct = ct * dua % N
        mid = (lo + hi) // 2
        if orc(ct): lo = mid
        else:       hi = mid
    if pow(hi, E, N) != c0: gagal_int += 1

    # versi B: Fraction (eksak)
    lo, hi, ct = Fraction(0), Fraction(N), c0
    for _ in range(N.bit_length()):
        ct = ct * dua % N
        mid = (lo + hi) / 2
        if orc(ct): lo = mid
        else:       hi = mid
    if pow(int(hi), E, N) != c0: gagal_frac += 1

print(f"versi integer //  : {gagal_int}/20 gagal")
print(f"versi Fraction    : {gagal_frac}/20 gagal")
```

### `screenshot.py`

> render screenshot tiap langkah dari keluaran perintah sungguhan

```python
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

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | Cari endpoint soal lewat platform: `curl https://techtonicexpo.online/tantangan` | Gagal | Balas `307 Temporary Redirect` ke `/masuk`. Daftar challenge ada di balik login, dan halaman login Next.js kirim kredensial ke `/api/masuk` — jalur ini muter jauh sebelum sampai ke soal. Ditinggal begitu URL service didapat langsung. |
| 2 | Binary search pakai integer `//` (`mid = (lo+hi)//2`) | Gagal | Pembulatan ke bawah tiap iterasi menumpuk. Setelah 511 iterasi, error akumulatifnya melewati 1, jadi `hi` mendarat di angka yang salah. |
| 3 | Binary search pakai `Fraction` | **Berhasil** | Batas interval tetap eksak sepanjang 511 iterasi, `int(hi)` mendarat tepat di `m`. |

Poin #2 tidak saya tebak — saya ukur. Karena oracle asli tidak bisa dipakai bereksperimen bebas (tiap tes = 511 request ke server panitia), saya bangkitkan kunci RSA 512-bit sendiri, jalankan oracle paritas secara lokal, lalu adu kedua versi pada 20 kunci acak:

```bash
python3 uji_pembulatan.py
```

```
versi integer //  : 20/20 gagal
versi Fraction    : 0/20 gagal
```

Jadi bukan "kadang meleset" — versi integer gagal **setiap kali**. Itulah alasan `Fraction` dipakai di solver final, dan alasan solver tetap punya jaring pengaman `m-1 / m / m+1` sebelum menyatakan berhasil.

---

## 6. Insight Utama & Teknik Unik

- **Kunci soal ini:** RSA itu homomorphic terhadap perkalian, jadi `c · 2^e mod n` mendekripsi jadi `2m mod n`. Karena `2m` mustahil ganjil secara alami, jawaban "ganjil" hanya bisa berarti terjadi reduksi modulo — dan itu memberi tahu `m` ada di paruh atas atau bawah interval. Satu bit bocor per query × 511 query = seluruh plaintext, **tanpa memfaktorkan `n`**.
- **Teknik unik:** kalibrasi oracle dengan plaintext yang sudah diketahui (`c=1` → `m=1`, `c=2^e` → `m=2`) sebelum menembakkan 511 query. Ini memastikan arah interpretasi genap/ganjil tidak kebalik — kalau kebalik, hasilnya tetap "sukses" tanpa error, cuma plaintextnya sampah, dan debugnya mahal.
- **Pelajaran:** di serangan yang mempersempit interval selama ratusan iterasi, **presisi aritmetika itu bagian dari eksploitnya**, bukan detail implementasi. Dan selalu tutup solver dengan verifikasi mandiri (`pow(m,e,n) == c`) — plaintext yang "kelihatan benar" bukan bukti; enkripsi ulang yang cocok, itu bukti.
- Oracle satu-bit tampak tidak berbahaya bagi yang mendesain server. Mitigasinya: padding (OAEP) yang membuat ciphertext hasil manipulasi ditolak sebelum sempat dijawab paritasnya.

---
