<!-- category: Cryptography | points: 689 -->
# Tabung Tembaga

| | |
| :--- | :--- |
| **Challenge** | Tabung Tembaga |
| **Kategori** | Cryptography · Eliminasi |
| **Poin** | 689 (dynamic scoring, awal 750) |
| **Connection** | `techtonicexpo.online/tantangan/14` → service `http://168.110.219.59:5015` |
| **Solver** | nexsus404 |
| **Status** | Solved |

> Dua pesan terlahir dari akar yang sama. Pesan kedua hanya berselisih satu langkah dari yang
> pertama, dan keduanya dipanggang dengan pangkat tiga di dalam tabung yang sama.
>
> Dengan eksponen sekecil itu, dua teks sandi yang saling berkerabat bisa diadu hingga saling
> menguak. Selisih satu langkah sudah cukup untuk merobek keduanya.
>
> Bedah polinomnya, cari akar bersama, dan pesan pertama akan menampakkan diri.

![soal](img/01-soal.png)

---

## 1. Flag

```
TechtonicExpoCTF{kembar_terkait_66394FFC}
```

![flag diterima](img/05-flag.png)

---

## 2. Analisis Awal

Parameter dari service ([`params.py`](params.py)):

```
n  = 1275260566276744489586657928796077778931862729424816816531496673960724863907...
e  = 3
c1 = 10335354943553817684128269459125640869543408673459156221113376806064396203025084848809372118592586048
c2 = 10335354943553817684128269459125655103911277562519634088612780080817002159742722129877229347027178317
```

RSA dengan **e = 3** dan dua ciphertext yang berkerabat. Deskripsi menyebut serangannya nyaris
apa adanya:

| Kalimat di deskripsi | Maksudnya |
| :--- | :--- |
| "dipanggang dengan pangkat tiga di dalam tabung yang sama" | `e = 3`, modulus `n` sama untuk kedua pesan |
| "pesan kedua hanya berselisih satu langkah" | `m2 = m1 + 1` |
| "dua teks sandi yang berkerabat bisa diadu" | **Franklin-Reiter related-message attack** |
| "bedah polinomnya, cari akar bersama" | `gcd(x³ − c1, (x+1)³ − c2)` di `Z_n[x]` |

Jadi jalur yang dimaksud sudah jelas. Tapi sebelum menulis aritmetika polinom, satu hal diperiksa
dulu — **ukuran ciphertext-nya**:

```python
print('bit n :', n.bit_length())
print('bit c1:', c1.bit_length())
print('n^(1/3) bit :', n.bit_length()//3)
```

```
bit n : 1021
bit c1: 333
bit c2: 333
n^(1/3) bit : 340
```

Ini yang menentukan segalanya. `c1` hanya **333 bit**, sedangkan `m³` baru mulai terbungkus modulo
kalau melewati `n^(1/3) ≈ 340 bit`. Karena `c1 < n`, berarti **`m³` tidak pernah dikurangi mod `n`
sama sekali** — jadi `c1` adalah bilangan kubik biasa, bukan hasil aritmetika modular. Akar pangkat
tiga bilangan bulat langsung membukanya, tanpa perlu Franklin-Reiter.

![recon](img/02-recon.png)

---

## 3. Langkah Penyelesaian

### 3.1 Jalur A — akar pangkat tiga langsung

Karena `m³ < n`, cukup cari akar pangkat tiga bilangan bulat dari `c1`. Dipakai binary search, bukan
`round(c1 ** (1/3))` — float 64-bit sama sekali tidak sanggup memegang 333 bit dan pasti meleset:

```python
def icbrt(x):
    lo, hi = 0, 1 << ((x.bit_length() + 2) // 3 + 2)
    while lo < hi:
        mid = (lo + hi) // 2
        if mid ** 3 < x: lo = mid + 1
        else: hi = mid
    return lo
```

```
m1 = 2178253724805649638202285427353972
m1^3 == c1 : True          <- kubik sempurna, konfirmasi tidak ada reduksi modulo
m2 = 2178253724805649638202285427353973
m2^3 == c2 : True
m2 - m1 = 1                <- persis "berselisih satu langkah"
```

Identitas selisihnya juga cocok, memastikan `m2 = m1 + 1` bukan kebetulan:

```python
c2 - c1 == 3*m1**2 + 3*m1 + 1     # True
```

### 3.2 Jalur B — Franklin-Reiter sebagai verifikasi

Jalur yang dimaksud soal tetap diimplementasikan, supaya hasilnya diverifikasi dua metode
independen. Karena `m2 = m1 + a` dengan `a = 1`, maka `m1` adalah **akar bersama** dari:

```
g1(x) = x³ − c1
g2(x) = (x + 1)³ − c2  =  x³ + 3x² + 3x + 1 − c2
```

Keduanya habis dibagi `(x − m1)`. Menghitung `gcd(g1, g2)` di `Z_n[x]` meruntuhkannya jadi polinom
derajat 1, dan setelah dijadikan monik, `m1 = −suku_konstanta`:

```python
g1 = [(-c1) % n, 0, 0, 1]      # x^3 - c1
g2 = [(1 - c2) % n, 3, 3, 1]   # (x+1)^3 - c2
g  = polygcd(g1, g2, n)
g  = [(x * pow(g[-1], -1, n)) % n for x in g]   # monik
m1 = (-g[0]) % n
```

```
derajat gcd = 1  -> (x - m1), akar tunggal
m1 = 2178253724805649638202285427353972
cocok dengan jalur A : True
```

Dua metode, angka identik.

![dua jalur cocok](img/03-solver.png)

### 3.3 Decode ke teks

```python
m.to_bytes((m.bit_length() + 7) // 8, "big")
```

```
m1 -> b'kembar_terkait'
m2 -> b'kembar_terkaiu'
```

`m2` adalah `m1` dengan byte terakhir naik satu (`t` = 0x74 → `u` = 0x75) — itulah wujud fisik dari
"pesan kedua ditulis satu langkah setelah pesan pertama". Pesan pertama adalah kata kuncinya:

```
TechtonicExpoCTF{kembar_terkait_66394FFC}
```

![decode](img/04-decode.png)

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| Python 3 | 3.14 | seluruh perhitungan — `int` presisi tak terbatas bawaan Python sudah cukup |
| `pow(x, -1, n)` | stdlib | invers modular untuk menjadikan polinom monik |

**Tanpa dependensi luar sama sekali.** Tidak perlu SageMath, `gmpy2`, maupun PyCryptodome — GCD
polinom di `Z_n[x]` ditulis manual dalam ~15 baris (`polymod` + `polygcd` di dalam
[`solve.py`](solve.py)).

File:

- [`params.py`](params.py) — parameter `n`, `e`, `c1`, `c2` dari service
- [`solve.py`](solve.py) — kedua jalur serangan

```bash
python3 solve.py
```

```
n  : 1021 bit
c1 : 333 bit   (ambang n^(1/3) = 340 bit)
c1 < n^(1/3)? True  -> m^3 tidak pernah dikurangi mod n

[A] CUBE ROOT LANGSUNG
    m1 = 2178253724805649638202285427353972
    m1^3 == c1 : True
    pesan      : kembar_terkait

[B] FRANKLIN-REITER (a = 1)
    derajat gcd = 1  -> (x - m1), akar tunggal
    m1 = 2178253724805649638202285427353972
    cocok dengan jalur A : True
    pesan      : kembar_terkait

FLAG    : TechtonicExpoCTF{kembar_terkait_66394FFC}
```

---

## 5. Trial-and-Error / Langkah yang Gagal

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | Langsung tulis Franklin-Reiter tanpa cek ukuran | Berlebihan | Bukan salah, tapi 40 baris aritmetika polinom untuk sesuatu yang sebenarnya selesai dengan satu binary search |
| 2 | `round(c1 ** (1/3))` sebagai akar kubik | **Gagal** | `float` hanya 53 bit mantissa vs `c1` 333 bit — hasilnya meleset jauh dan `m**3 == c1` langsung `False` |
| 3 | Asumsi `c1` hasil reduksi mod `n` | **Salah asumsi** | Dibantah oleh `c1.bit_length() = 333 < 340`. Kalau diteruskan, waktu habis mengejar akar kubik modular yang tidak pernah ada |
| 4 | Cek ukuran bit dulu, baru pilih metode | **Berhasil** | Ketahuan `m³ < n`, cube root polos langsung tembus |
| 5 | Franklin-Reiter dijalankan tetap | **Berhasil** | Dipakai sebagai verifikasi silang, hasilnya identik |

Kesalahan #2 layak dicatat karena diam-diam: `round(c1 ** (1/3))` **tidak error**, ia mengembalikan
angka yang kelihatan wajar. Yang membongkarnya cuma pengecekan `m**3 == c1`. Setiap akar kubik
bilangan besar harus diverifikasi dengan mengalikannya kembali, tidak boleh dipercaya begitu saja.

---

## 6. Insight Utama & Teknik Unik

- **Kunci soal ini:** ukur dulu, baru pilih senjata. Deskripsi soal mengarahkan ke Franklin-Reiter,
  dan itu memang benar — tapi satu perbandingan `c1.bit_length()` vs `n.bit_length()//3` menunjukkan
  serangan yang jauh lebih murah sudah cukup. Petunjuk panitia menjelaskan *desain* soal, bukan
  selalu *jalur termurah* untuk memecahkannya.

- **Teknik unik — bit-length sebagai alat diagnosis.** `e = 3` dengan `m³ < n` adalah kegagalan
  RSA tanpa padding yang klasik: operasi "modular" tidak pernah benar-benar modular. Ini terbaca
  gratis dari panjang bit, sebelum satu baris serangan pun ditulis. Kebiasaan yang murah: pada tiap
  soal RSA eksponen kecil, bandingkan `len(c)` dengan `len(n)/e` **lebih dulu**.

- **Franklin-Reiter tidak butuh library berat.** Serangan ini sering dianggap wajib SageMath, padahal
  intinya cuma GCD Euclid pada polinom dengan koefisien mod `n` — sekitar 15 baris Python murni.
  Satu-satunya operasi non-sepele adalah invers modular untuk koefisien pemimpin, dan `pow(x, -1, n)`
  sudah ada di stdlib sejak Python 3.8. Bonus: kalau invers itu gagal, `gcd` yang muncul justru
  **memfaktorkan `n`** — jadi kegagalannya pun menang.

- **Verifikasi silang itu murah.** Dua jalur independen yang menghasilkan integer 34 digit yang
  sama persis meniadakan seluruh keraguan sebelum submit. Untuk soal yang flag-nya adalah hasil
  dekripsi (bukan pesan "Correct" dari server), tidak ada oracle yang bisa dipakai mengecek — jadi
  metode kedua itulah oracle-nya.

- **Pelajaran:** jangan percaya akar dari aritmetika float pada bilangan besar. Selalu tutup dengan
  `m ** e == c`.

<!--
CHECKLIST ISI MINIMAL (slide "Format dan Isi Write-up")
  [x] 1. Judul dan kategori challenge     -> tabel info + metadata
  [x] 2. Flag yang ditemukan              -> bagian 1
  [x] 3. Analisis awal                    -> bagian 2
  [x] 4. Langkah penyelesaian             -> bagian 3 (3.1 - 3.3)
  [x] 5. Tools atau script                -> bagian 4 + solve.py + params.py
  [x] 6. Trial-and-error / langkah gagal  -> bagian 5 (5 poin, 3 gagal)
  [x] 7. Insight utama / teknik unik      -> bagian 6
-->
