<!-- category: Digital Forensics | points: 500 -->
# Piksel Senyap

| | |
| :--- | :--- |
| **Challenge** | Piksel Senyap |
| **Kategori** | Digital Forensics · Eliminasi |
| **Poin** | 500 |
| **Connection** | `techtonicexpo.online/tantangan/17` — attachment `piksel_senyap.png` |
| **Solver** | nexsus404 |
| **Status** | Solved |

> Selembar gambar yang sekilas hanya derau warna, seperti saluran televisi yang kehilangan sinyal.
> Di balik setiap piksel ada cerita, tapi tidak semua lapisan menceritakan hal yang sama. Sebagian
> lapisan sengaja berbohong, sebagian baru bicara setelah cara pandang digeser. Jangan berhenti di
> permukaan yang paling mudah terlihat, karena lapisan yang paling ramai bicara sering kali paling
> banyak menutupi.

![soal](img/01-soal.png)

---

## 1. Flag

```
TechtonicExpoCTF{lsb_tersembunyi_66394FFC}
```

![flag diterima](img/05-flag.png)

---

## 2. Analisis Awal

**Yang dikasih:** satu file `piksel_senyap.png`, tanpa layanan/URL tambahan.

Deskripsi soal sebenarnya sudah jadi peta jalan kalau dibaca sebagai istilah teknis, bukan puisi:

| Kalimat di deskripsi | Terjemahan teknis |
| :--- | :--- |
| "derau warna" | citra noise RGB acak, bukan foto |
| "lapisan" | **bit-plane** (tiap channel punya 8 bit-plane) |
| "sebagian lapisan sengaja berbohong" | ada **plane umpan** berisi string palsu |
| "baru bicara setelah cara pandang digeser" | data asli **digeser** dari bit 0 → bit lain |
| "jangan berhenti di permukaan yang paling mudah terlihat" | **jangan berhenti di LSB** (bit 0) |
| "lapisan paling ramai bicara paling banyak menutupi" | plane yang isinya paling mencolok justru umpan |

**Hipotesis awal:** LSB steganography, tapi dengan bit-plane umpan di LSB dan payload asli di
bit-plane yang lebih tinggi. Jadi rencananya bukan "ekstrak LSB", melainkan **audit ke-24 bit-plane
satu per satu** (3 channel × 8 bit).

Recon dasar dulu untuk memastikan tidak ada jalur yang lebih murah:

```bash
file piksel_senyap.png
md5sum piksel_senyap.png
exiftool piksel_senyap.png
binwalk piksel_senyap.png
```

```
piksel_senyap.png: PNG image data, 512 x 512, 8-bit/color RGB, non-interlaced
7d67abcf4c0b53617cc26388e0f82c6d  piksel_senyap.png

DECIMAL   HEXADECIMAL   DESCRIPTION
0         0x0           PNG image, total size: 788035 bytes
```

Tidak ada metadata mencurigakan, tidak ada file yang di-append. Satu petunjuk penting: raw pixel
512×512×3 = **786.432 byte**, sedangkan PNG-nya **788.035 byte** — jadi hasil kompresi Deflate
malah *lebih besar* dari data mentahnya. Artinya isi gambar benar-benar acak/inkompresibel, dan
memang tidak ada gambar "asli" yang disembunyikan di permukaan. Datanya ada di dalam nilai piksel.

![recon](img/02-recon.png)

---

## 3. Langkah Penyelesaian

### 3.1 Audit statistik ke-24 bit-plane

Kunci soal ini: pada noise acak murni, **setiap bit-plane punya rasio bit-1 ≈ 0,5 dan merata di
seluruh area**. Kalau ada satu plane yang menyimpang, di situlah datanya. Uji rasio global dulu:

```python
for c in range(3):
    for b in range(8):
        p = (a[:, :, c] >> b) & 1
        print(CH[c], b, f"{p.mean():.4f}")
```

```
R  0   0.5002      G  0   0.5001      B  0   0.4992
R  1   0.5001      G  1   0.5019      B  1   0.4409   <== MENYIMPANG
R  2   0.4984      G  2   0.5013      B  2   0.5003
...semua plane lain 0.498 - 0.502...
```

**Blue channel bit 1** rasionya 0,4409 sementara 23 plane lainnya rapat di sekitar 0,50. Ini persis
"lapisan yang baru bicara setelah cara pandang digeser" — datanya ada di bit 1, bukan bit 0.

### 3.2 Lokalisasi: di mana konten itu berada

Rasio global saja belum cukup, perlu tahu sebarannya. Peta rasio per blok 64×64:

```python
dev = np.abs(p.reshape(8, 64, 8, 64).mean(axis=(1, 3)) - 0.5).max()
```

```
0.51 0.51 0.50 0.49 0.50 0.50 0.50 0.49
0.50 0.51 0.49 0.49 0.51 0.50 0.50 0.51
0.49 0.50 0.49 0.50 0.50 0.50 0.49 0.50
0.32 0.24 0.26 0.27 0.28 0.26 0.26 0.31   <== pita konten
0.29 0.27 0.25 0.26 0.24 0.26 0.25 0.30   <== pita konten
0.49 0.50 0.49 0.50 0.50 0.50 0.49 0.50
0.50 0.50 0.49 0.48 0.52 0.49 0.50 0.50
0.50 0.49 0.50 0.51 0.51 0.49 0.49 0.49
```

Penyimpangan terkumpul rapi di **pita horizontal y = 192–320**, melebar penuh. Bentuk blok begini
khas **teks yang digambar**, bukan byte yang di-encode. Ini yang mengubah arah pendekatan.

### 3.3 Render plane B1 jadi citra hitam-putih

```python
p = (((a[:, :, 2] >> 1) & 1) * 255).astype(np.uint8)
Image.fromarray(p).save("plane_B1.png")
```

Flag langsung terbaca sebagai teks di tengah noise:

![plane B1 - flag terbaca](plane_B1.png)

Isi teksnya: **`lsb_tersembunyi`**

### 3.4 Verifikasi umpan sebelum submit

Deskripsi menyebut ada lapisan yang "sengaja berbohong", jadi plane lain wajib dicek sebelum submit.
Uji bias hanya menangkap konten *visual*, sedangkan teks yang di-pack jadi byte tetap terlihat
seperti noise. Jadi ke-24 plane di-unpack jadi ASCII:

```python
bits = ((a[:, :, c] >> b) & 1).flatten()
data = np.packbits(bits, bitorder="big").tobytes()
re.findall(rb"[ -~]{12,}", data)
```

```
R0: kunci_salah_arah_2026kunci_salah_arah_2026kunci_salah_arah_2...
```

Umpannya ketemu di **Red channel LSB** — tempat pertama yang dicek semua orang:

```
jumlah pengulangan 'kunci_salah_arah_2026' : 20
panjang plane R0                           : 32768 byte
```

20 pengulangan × 21 byte = 420 byte pertama, sisanya noise. Ditaruh persis di awal plane supaya
langsung kena begitu ada yang jalankan ekstraksi LSB standar.

Hasil akhir audit lengkap:

| Plane | Isi | Peran |
| :--- | :--- | :--- |
| **R bit 0** (LSB) | `kunci_salah_arah_2026` ×20 | **Umpan** |
| **B bit 1** | citra teks `lsb_tersembunyi` | **Payload asli** |
| 22 plane lainnya | noise acak | pengisi |

![hasil solver](img/04-exploit.png)

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| `file` / `md5sum` | coreutils | identifikasi & integritas file |
| `exiftool` | 13.55 | cek metadata PNG — hasilnya nihil |
| `binwalk` | — | cek file ter-append — hasilnya nihil |
| Python 3 + **NumPy** | 2.5.1 | ekstraksi & statistik bit-plane |
| Python 3 + **Pillow** | 12.3.0 | baca PNG, render bit-plane jadi citra |

`zsteg` (tool standar untuk kasus ini) **tidak tersedia** di mesin, jadi analisisnya ditulis manual
pakai NumPy. Ternyata justru menguntungkan: uji bias per blok bukan fitur bawaan `zsteg`, dan
justru itu yang langsung menunjuk plane B1 tanpa perlu memelototi 24 gambar satu-satu.

Solver lengkap ada di [`solve.py`](solve.py), jalankan dengan:

```bash
python3 solve.py
```

```
[1] deviasi maksimum per blok 64x64 (>0.05 = ada konten)
    B1: 0.2603  <== ADA KONTEN

[2] render plane berkonten
    -> plane_B1.png  (buka: teks flag terbaca di sini)

[3] string ASCII terpaket di tiap plane
    R0: kunci_salah_arah_2026kunci_salah_arah_2026kunci_salah_arah_2
```

---

## 5. Trial-and-Error / Langkah yang Gagal

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | `exiftool` cari metadata/komentar | Gagal | PNG bersih, cuma field standar |
| 2 | `binwalk` cari file ter-append | Gagal | Cuma 1 signature PNG di offset 0 |
| 3 | `zsteg piksel_senyap.png` | Gagal | Tool tidak terinstall — terpaksa tulis scanner NumPy sendiri |
| 4 | Ekstrak LSB R0 sebagai jawaban | **Jebakan** | Dapat `kunci_salah_arah_2026`. Kalau langsung disubmit, salah |
| 5 | Pack bit B1 jadi byte (`bitorder="big"`) | Gagal | Output biner acak: `\x0e\xfc\x9d,\x1b\xa4\\x...` |
| 6 | Pack bit B1 jadi byte (`bitorder="little"`) | Gagal | Sama acaknya: `p?\xb94\xd8%:\x1e...` |
| 7 | Pack B1 column-major (transpose) | Gagal | Tetap acak — asumsi "payload = byte" memang keliru |
| 8 | **Render B1 sebagai citra B/W** | **Berhasil** | Payload-nya gambar teks, bukan byte terpaket |

Langkah 5–7 yang paling makan waktu. Refleks setelah menemukan plane menyimpang adalah langsung
`np.packbits()` — padahal peta blok di langkah 3.2 sudah memberi tahu bentuknya pita persegi, yang
seharusnya langsung mengarah ke "ini gambar". **Peta blok dibaca dulu sebelum unpack** akan
memotong tiga percobaan gagal itu.

---

## 6. Insight Utama & Teknik Unik

- **Kunci soal ini:** noise acak itu justru *keuntungan* buat analis. Karena tiap bit-plane noise
  murni pasti punya rasio bit-1 ≈ 0,5 secara merata, penyisipan apa pun langsung merusak
  keseragaman itu. Jadi tidak perlu menebak plane mana — cukup ukur ke-24 plane dan biarkan
  statistiknya yang menunjuk.

- **Teknik unik — deviasi bias per blok, bukan global.** Rasio global bisa menipu: konten kecil di
  gambar besar akan tenggelam jadi ≈0,50. Dengan memecah tiap plane jadi blok 64×64 lalu mengambil
  deviasi *maksimum*, konten lokal tetap muncul (B1 = 0,2603 vs plane lain ≤0,027 — beda 10×).
  Bonus: pola bloknya sekaligus memberi tahu **bentuk** payload, jadi ketahuan itu gambar atau byte
  sebelum salah pilih cara ekstrak.

- **Dua kanal deteksi wajib jalan dua-duanya.** Uji bias hanya menangkap payload visual; string
  ASCII terpaket lolos darinya. Sebaliknya `strings` tidak akan menangkap teks yang digambar.
  Umpan R0 ketemu lewat unpack ASCII, payload asli B1 ketemu lewat render citra — pakai satu metode
  saja pasti salah satu terlewat, dan kalau yang jalan cuma unpack ASCII, yang ketemu justru umpan.

- **Pelajaran:** temuan pertama di LSB jangan langsung disubmit. Soal yang deskripsinya menyinggung
  "kebohongan" atau "permukaan" hampir pasti memasang decoy di lokasi paling standar. Audit seluruh
  ruang pencarian dulu, baru pilih.

<!--
CHECKLIST ISI MINIMAL (slide "Format dan Isi Write-up")
  [x] 1. Judul dan kategori challenge     -> tabel info + metadata
  [x] 2. Flag yang ditemukan              -> bagian 1
  [x] 3. Analisis awal                    -> bagian 2
  [x] 4. Langkah penyelesaian             -> bagian 3 (3.1 - 3.4)
  [x] 5. Tools atau script                -> bagian 4 + solve.py
  [x] 6. Trial-and-error / langkah gagal  -> bagian 5 (8 percobaan)
  [x] 7. Insight utama / teknik unik      -> bagian 6
-->
