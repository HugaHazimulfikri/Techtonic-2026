<!-- category: Cryptography | points: 500 -->
# Lilitan Siput

| | |
| :--- | :--- |
| **Challenge** | Lilitan Siput |
| **Kategori** | Cryptography · Eliminasi |
| **Poin** | 500 |
| **Connection** | `techtonicexpo.online/tantangan/12` → service `http://168.110.219.59:5013` |
| **Solver** | nexsus404 |
| **Status** | Solved |

> Jejak siput berputar dua kali. Lapisan pertama menggeser tiap huruf mengikuti irama lima ketukan.
> Lapisan kedua membungkus hasilnya dalam enam kolom yang dibaca dengan urutan ganjil.
>
> Urutan pembacaan kolom sudah diumumkan, dan panjang irama juga bukan rahasia. Yang tersisa
> hanyalah membalik dua lapisan itu dengan teliti.
>
> Kalimat asli memakai huruf besar tanpa spasi, dan di dalamnya terselip kata kunci yang sedang
> kamu cari.

![soal](img/01-soal.png)

---

## 1. Flag

```
TechtonicExpoCTF{lilit_putar_dua_66394FFC}
```

![flag diterima](img/05-flag.png)

---

## 2. Analisis Awal

Bahan dari service:

```
jejak  : LLUZQXMRIQGVNTUCJGGCAXFCIXLCCNJHRIAHNUIXDUIQYYDYVQQLES
catatan: Irama vigenere memakai kata sandi lima huruf.
         Enam kolom dibaca dengan urutan: 3-1-5-0-4-2.
```

Dua lapis enkripsi bertumpuk:

| Lapis | Jenis | Parameter | Status |
| :--- | :--- | :--- | :--- |
| 1 (dalam) | **Vigenère** | kunci 5 huruf | **rahasia** — harus dipecahkan |
| 2 (luar) | **Transposisi kolom** | 6 kolom, urutan baca `3-1-5-0-4-2` | diumumkan |

Karena enkripsi berjalan plaintext → Vigenère → transposisi, dekripsi harus **dari luar ke dalam**:
bongkar transposisi lebih dulu, baru serang Vigenère. Urutan ini wajib — analisis frekuensi pada
ciphertext mentah tidak akan berarti apa-apa selama huruf-hurufnya masih teracak posisinya.

Ukuran grid dicek dulu:

```python
print('panjang :', len(CT))          # 54
print('baris   :', -(-54//6))        # 9
print('sisa    :', 54 % 6)           # 0
```

54 = 6 × 9 **pas**, tanpa baris parsial. Ini menyederhanakan pembalikan transposisi: keenam kolom
sama panjang (9 huruf), jadi ciphertext tinggal dipotong rata enam.

![recon](img/02-recon.png)

---

## 3. Langkah Penyelesaian

### 3.1 Balikkan lapis 2 — transposisi kolom

Enkripsinya: tulis teks baris demi baris ke grid 6 kolom, lalu baca kolom sesuai urutan
`3-1-5-0-4-2`. Jadi:

```
ciphertext = kolom[3] ++ kolom[1] ++ kolom[5] ++ kolom[0] ++ kolom[4] ++ kolom[2]
```

Membalikkannya berarti memotong ciphertext jadi enam blok 9 huruf, mengembalikan tiap blok ke
nomor kolomnya, lalu membaca grid per baris:

```python
kol = {}
for i, c in enumerate([3,1,5,0,4,2]):
    kol[c] = CT[i*9:(i+1)*9]
mid = "".join(kol[c][r] for r in range(9) for c in range(6))
```

```
CQYLNGCGDLUCNVYUIAJNVZXXHTQQDFRUQXUCICLMIIAJERQXHGSIYL
```

Catatan: permutasi `[3,1,5,0,4,2]` kebetulan merupakan **involusi** (pasangannya sendiri), jadi dua
tafsir lazim atas kalimat "urutan baca" — *"blok ke-i adalah kolom order[i]"* versus *"kolom c
dibaca di posisi order[c]"* — menghasilkan susunan yang sama persis. Kedua tafsir diuji dan
outputnya identik, jadi ambiguitas ini tidak perlu diperdebatkan.

### 3.2 Pecahkan lapis 1 — Vigenère kunci 5 huruf

Panjang kunci sudah diketahui (5), jadi teks dipecah jadi **5 coset**: huruf ke-0, 5, 10, … dikunci
geseran yang sama, begitu pula coset lainnya. Tiap coset otomatis menjadi **sandi Caesar biasa**.

Tiap coset cuma berisi ~11 huruf — terlalu pendek untuk chi-square sendirian, jadi dipakai dua
tahap:

1. **Per coset**, peringkat 26 geseran dengan chi-square terhadap frekuensi huruf bahasa Indonesia,
   ambil **4 teratas**.
2. **Adu semua kombinasi** (4⁵ = 1024 kandidat kunci), skor tiap plaintext utuh dengan hitungan
   n-gram Indonesia (`YANG`, `KUNCI`, `DAN`, `NG`, `AN`, …).

```python
for i in range(5):
    coset = mid[i::5]
    urut  = sorted(range(26), key=lambda s: chi(geser(coset, s)))
    kandidat.append(urut[:4])
best = max((skor(pt), key, pt) for combo in itertools.product(*kandidat))
```

```
kunci Vigenere : RINDU   (skor n-gram 50)
plaintext      : LILITPUTARDUASEDANGTERKUNCIDALAMDUALAPISRANGKAIKEMBALI
```

Pemenangnya menang telak — kandidat kedua hanya berskor 45 dan hasilnya jelas sampah
(`SILIPWUTANKUASAKANGPLRKUJJIDAHHM...`).

![kunci terpecahkan](img/03-solver.png)

### 3.3 Verifikasi dengan enkripsi ulang

Karena tidak ada endpoint verifikasi di service, satu-satunya oracle adalah **round-trip**:
plaintext dienkripsi ulang melalui kedua lapis, hasilnya harus identik dengan ciphertext asli.

```python
v     = vigenere_encrypt(pt, "RINDU")
kol   = ["".join(v[r*6 + c] for r in range(9)) for c in range(6)]
ulang = "".join(kol[c] for c in [3,1,5,0,4,2])
assert ulang == CT
```

```
re-enkripsi     : LLUZQXMRIQGVNTUCJGGCAXFCIXLCCNJHRIAHNUIXDUIQYYDYVQQLES
ciphertext asli : LLUZQXMRIQGVNTUCJGGCAXFCIXLCCNJHRIAHNUIXDUIQYYDYVQQLES
COCOK PERSIS    : True
```

Cocok byte demi byte. Kunci `RINDU` dan plaintext-nya pasti benar, bukan sekadar "kelihatan
Indonesia".

### 3.4 Ambil kata kunci dari kalimat

```
LILITPUTARDUASEDANGTERKUNCIDALAMDUALAPISRANGKAIKEMBALI
```

Dipenggal:

```
LILIT PUTAR DUA | SEDANG TERKUNCI DALAM DUA LAPIS | RANGKAI KEMBALI
```

Subjek kalimatnya — hal yang "sedang terkunci dalam dua lapis" — adalah **LILIT PUTAR DUA**. Itulah
"kata kunci yang terselip" yang dimaksud deskripsi, dan bentuknya konsisten dengan kunci soal-soal
lain di event ini (`lsb_tersembunyi`, `kembar_terkait`, `ramal_lcg_nakal`): frasa nomina huruf kecil
dipisah garis bawah.

```
TechtonicExpoCTF{lilit_putar_dua_66394FFC}
```

![decode](img/04-decode.png)

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| Python 3 | 3.14 | seluruh serangan |
| `itertools.product` | stdlib | adu 1024 kombinasi kandidat kunci |
| `curl` | 8.x | ambil jejak & catatan dari service |

**Tanpa dependensi luar**, tanpa `pycipher`/`cryptanalysis` toolkit. Chi-square dan skor n-gram
ditulis manual (~10 baris) di [`solve.py`](solve.py).

```bash
python3 solve.py
```

```
ciphertext            : LLUZQXMRIQGVNTUCJGGCAXFCIXLCCNJHRIAHNUIXDUIQYYDYVQQLES
setelah transposisi   : CQYLNGCGDLUCNVYUIAJNVZXXHTQQDFRUQXUCICLMIIAJERQXHGSIYL

kunci Vigenere        : RINDU   (skor n-gram 50)
plaintext             : LILITPUTARDUASEDANGTERKUNCIDALAMDUALAPISRANGKAIKEMBALI

re-enkripsi == ciphertext asli : True

kata kunci            : lilit_putar_dua
```

---

## 5. Trial-and-Error / Langkah yang Gagal

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | Tebak kunci `SIPUT` (5 huruf, sesuai judul soal) | **Gagal** | `KIJRUOURJSCUYBFCALPUDRIDOBIBJMZM...` — sampah |
| 2 | Tebak kunci `LILIT` | **Gagal** | `RINDUVUVVSJUCNFJAPBUKRMPOIIFVMGM...` — sampah, tapi 5 huruf pertamanya justru `RINDU` (kebetulan yang lucu) |
| 3 | Tebak kunci `JEJAK`, `IRAMA` | **Gagal** | Sama-sama sampah. Menebak kunci dari tema soal ternyata buang waktu |
| 4 | Konvensi transposisi alternatif (grid dibalik, baca kolom-lalu-baris) | **Gagal** | `mid` jadi `CCNJHRIAHQGVNTUCJGYDYVQQLESLLUZ...`, skor n-gram terbaiknya cuma 17 vs 50 — jelas salah |
| 5 | Chi-square per coset, ambil **1** geseran terbaik saja | Rapuh | Coset cuma 11 huruf; peringkat teratas belum tentu benar. Butuh top-4 + adu kombinasi |
| 6 | **Top-4 per coset + skor n-gram atas 1024 kombinasi** | **Berhasil** | Kunci `RINDU`, skor 50 unggul jauh dari runner-up (45) |

Percobaan #1–#3 adalah jebakan yang paling wajar: judul soal berteriak "SIPUT" dan "LILIT", jadi
naluri pertama adalah menebak kunci dari tema. Padahal kunci sebenarnya `RINDU` — tidak berhubungan
sama sekali dengan tema soal. Menebak kunci tematik memakan waktu lebih lama daripada langsung
menulis pemecah frekuensi, yang toh cuma ~20 baris.

Percobaan #4 berguna sebagai kontrol: konvensi transposisi yang salah menghasilkan skor n-gram 17
melawan 50 pada konvensi yang benar. Selisih setajam itu berarti **skor n-gram sekaligus bisa
dipakai memilih konvensi transposisi**, bukan cuma memilih kunci.

---

## 6. Insight Utama & Teknik Unik

- **Kunci soal ini:** sandi berlapis harus dibongkar dari lapis terluar. Selama transposisi belum
  dibalik, tiap alat statistik yang mengandalkan **posisi** huruf (coset Vigenère, indeks
  koinsidensi, chi-square) mengukur data yang salah. Membalik urutannya membuat soal terasa
  mustahil padahal parameternya sudah setengah diumumkan.

- **Teknik unik — chi-square untuk menyaring, n-gram untuk memutuskan.** Coset 11 huruf terlalu
  pendek untuk dipercayai chi-square sendirian, tapi cukup andal untuk menyempitkan 26 geseran jadi
  4 kandidat. Ruang pencarian runtuh dari 26⁵ = 11.881.376 menjadi 4⁵ = 1.024 — cukup kecil untuk
  diadu satu per satu dengan skor n-gram atas teks utuh, yang jauh lebih kuat karena melihat seluruh
  54 huruf sekaligus, bukan 11.

- **Skor n-gram juga memilih konvensi, bukan cuma kunci.** Ambiguitas "urutan baca kolom" biasanya
  diselesaikan dengan menebak dan melihat. Dengan menjalankan pemecah Vigenère penuh untuk **tiap**
  konvensi lalu membandingkan skor akhirnya (50 vs 17), pilihan konvensi jadi keputusan terukur,
  bukan firasat.

- **Round-trip adalah oracle untuk soal tanpa oracle.** Service ini tidak menyediakan endpoint
  verifikasi, dan flag-nya adalah hasil dekripsi. Mengenkripsi ulang plaintext melalui kedua lapis
  lalu membandingkannya byte demi byte dengan ciphertext asli mengubah "kelihatannya benar" jadi
  bukti — biaya empat baris kode.

- **Pelajaran:** jangan menebak kunci dari tema soal. `RINDU` tidak ada hubungannya dengan siput,
  lilitan, maupun jejak. Menulis pemecah otomatis lebih cepat daripada ronde ketiga menebak-nebak.

<!--
CHECKLIST ISI MINIMAL (slide "Format dan Isi Write-up")
  [x] 1. Judul dan kategori challenge     -> tabel info + metadata
  [x] 2. Flag yang ditemukan              -> bagian 1
  [x] 3. Analisis awal                    -> bagian 2
  [x] 4. Langkah penyelesaian             -> bagian 3 (3.1 - 3.4)
  [x] 5. Tools atau script                -> bagian 4 + solve.py
  [x] 6. Trial-and-error / langkah gagal  -> bagian 5 (6 poin, 5 gagal, semua diuji nyata)
  [x] 7. Insight utama / teknik unik      -> bagian 6
-->
