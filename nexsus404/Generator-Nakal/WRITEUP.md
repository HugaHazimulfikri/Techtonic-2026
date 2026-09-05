<!-- category: Cryptography | points: 653 -->
# Generator Nakal

| | |
| :--- | :--- |
| **Challenge** | Generator Nakal |
| **Kategori** | Cryptography · Eliminasi |
| **Poin** | 653 (dynamic scoring, awal 750) |
| **Connection** | `techtonicexpo.online/tantangan/13` → service `http://168.110.219.59:5014` |
| **Solver** | nexsus404 |
| **Status** | Solved |

> Mesin ini membangkitkan angka dengan rumus yang kaku. Setiap angka adalah anak dari angka
> sebelumnya. Rumusnya memakai pengali, penambah, dan sisa bagi besar yang semuanya tersembunyi.
>
> Tapi deret keluarannya bicara lebih banyak dari yang disangka. Dari beberapa angka berurutan,
> semua parameter rahasia bisa dibedah satu per satu.
>
> Tebak angka berikutnya dan kirim ke mesin. Kalau tepat, mesin mengakui kuncinya.

![soal](img/01-soal.png)

---

## 1. Flag

```
TechtonicExpoCTF{ramal_lcg_nakal_66394FFC}
```

---

## 2. Analisis Awal

Service memberi 8 keluaran berurutan dan satu endpoint tebakan:

```
x0 = 987654321012345678      x4 = 2381187045401728115
x1 = 6729977692791834322     x5 = 16223185267011201142
x2 = 6578750652915850225     x6 = 249113833186806331
x3 = 16888812019745501733    x7 = 7114183187174364876

tebak: /tebak?angka=...
```

Deskripsi menyebut tiga parameter — "pengali, penambah, dan sisa bagi besar". Itu definisi
**Linear Congruential Generator**:

```
x[n+1] = (a · x[n] + c) mod m
```

dengan `a` (pengali), `c` (penambah), `m` (modulus) semuanya rahasia. Tugasnya: pulihkan ketiganya
dari deret keluaran, lalu ramal `x8`.

Yang membuat ini bisa dikerjakan adalah **urutan pemulihannya**. `a` dan `c` tidak bisa dicari
selama `m` belum diketahui, karena keduanya hidup di aritmetika mod `m`. Jadi `m` harus jatuh lebih
dulu — dan `m` justru satu-satunya yang bisa dicari tanpa mengetahui dua lainnya.

![recon](img/02-recon.png)

---

## 3. Langkah Penyelesaian

### 3.1 Pulihkan `m` lewat GCD determinan selisih

Trik intinya: ambil **selisih** antar keluaran berurutan untuk melenyapkan `c`.

```
t[i] = x[i+1] − x[i]
```

Karena `x[i+1] = a·x[i] + c` dan `x[i+2] = a·x[i+1] + c`, penambah `c` saling hapus saat dikurangkan:

```
t[i+1] = x[i+2] − x[i+1] = a·(x[i+1] − x[i]) = a · t[i]   (mod m)
```

Sekarang deret `t` adalah barisan geometrik ber-rasio `a` mod `m`. Untuk melenyapkan `a` juga,
susun determinan 2×2 — hasilnya nol mod `m`, artinya **kelipatan `m`**:

```
u[i] = t[i+2]·t[i] − t[i+1]²  ≡  a²·t[i]² − (a·t[i])²  ≡  0   (mod m)
```

Beberapa `u[i]` yang berbeda hampir pasti hanya berbagi faktor `m` saja, jadi:

```python
t = [X[i+1] - X[i] for i in range(len(X)-1)]
u = [t[i+2]*t[i] - t[i+1]**2 for i in range(len(t)-2)]
m = abs(reduce(gcd, u))
```

```
[1] m = 18446744073709551557   (64 bit)
```

### 3.2 Pulihkan `a`, lalu `c`

Setelah `m` diketahui, sisanya aljabar biasa. Dari `t[1] = a·t[0] (mod m)`:

```python
a = (t[1] * pow(t[0], -1, m)) % m
c = (X[1] - a*X[0]) % m
```

```
[2] a = 6364136223846793005
[3] c = 1442695040888963407
```

Ketiga angka itu ternyata bukan acak:

| Parameter | Nilai | Identitas |
| :--- | :--- | :--- |
| `m` | 18446744073709551557 | `2^64 − 59` — bilangan prima terbesar di bawah 2⁶⁴ |
| `a` | 6364136223846793005 | pengali LCG **MMIX milik Knuth** |
| `c` | 1442695040888963407 | penambah MMIX (rasio emas × 2⁶⁴) |

MMIX aslinya memakai `m = 2^64`. Di sini modulusnya diganti prima `2^64 − 59` — justru membuat
pemulihan **lebih mudah**, karena setiap elemen tak-nol dijamin punya invers modular.

### 3.3 Verifikasi ke seluruh deret sebelum menebak

Endpoint tebakan kemungkinan hanya sekali pakai, jadi parameter diuji dulu ke semua 8 keluaran:

```python
ok = all((a*X[i] + c) % m == X[i+1] for i in range(len(X)-1))
```

```
[4] verifikasi seluruh deret: LULUS
```

Ketujuh transisi cocok. Baru setelah itu `x8` dihitung:

```python
x8 = (a*X[-1] + c) % m
```

```
x8 = 359657071830169386
```

![parameter terpulihkan](img/03-solver.png)

### 3.4 Kirim ramalan

```bash
curl -s "http://168.110.219.59:5014/tebak?angka=359657071830169386" | sed 's/<[^>]*>//g'
```

```
// TERKAIT  Prediksimu tepat. Mesin mengakui: kunci ramal_lcg_nakal
```

![tebakan diterima](img/04-tebak.png)

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| Python 3 | 3.14 | seluruh pemulihan parameter (`int` presisi tak terbatas) |
| `math.gcd` + `functools.reduce` | stdlib | GCD berantai untuk memulihkan `m` |
| `pow(x, -1, m)` | stdlib | invers modular untuk memulihkan `a` |
| `urllib` | stdlib | kirim tebakan ke `/tebak` |
| `curl` | 8.x | recon endpoint |

**Tanpa dependensi luar.** Seluruh serangan muat dalam ~30 baris Python murni:
[`solve.py`](solve.py).

```bash
python3 solve.py
```

```
[1] m = 18446744073709551557   (64 bit)
[2] a = 6364136223846793005
[3] c = 1442695040888963407

[4] verifikasi seluruh deret: LULUS

x8 (ramalan) = 359657071830169386
[5] respons mesin: // TERKAIT Prediksimu tepat. Mesin mengakui: kunci ramal_lcg_nakal
```

Catatan: `urllib` polos kena `HTTP 403` di service Techtonic (filter User-Agent), sama seperti pada
soal *Kubah Terbalik*. Header `User-Agent: curl/8.5.0` dipasang sejak awal di sini karena sudah
tahu polanya dari soal sebelumnya.

---

## 5. Trial-and-Error / Langkah yang Gagal

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | Asumsi `m = 2^64` (default LCG paling umum) | **Gagal keras** | `ValueError: base is not invertible for the given modulus` — `t[0]` genap, jadi tidak punya invers mod 2⁶⁴ |
| 2 | Pulihkan `a` lebih dulu, baru `m` | Buntu | `a` hidup di mod `m`; tanpa `m` tidak ada persamaan yang bisa diselesaikan. Urutannya wajib `m → a → c` |
| 3 | GCD dari **1** nilai `u` saja (4 keluaran) | **Gagal** | Dapat `59180836733637035300392479396766569743`, yaitu `m × 3208199587805960899` — kelipatan `m`, bukan `m` |
| 4 | GCD dari **2** nilai `u` (5 keluaran) | **Berhasil** | Tepat `18446744073709551557` |
| 5 | Pakai semua 5 nilai `u` (8 keluaran) | **Berhasil** | Nilai sama, tapi tanpa risiko faktor sisa — inilah yang dipakai |

Kegagalan #1 paling menjebak karena `m = 2^64` adalah tebakan yang sangat wajar (itu default di
banyak implementasi LCG). Untungnya ia gagal dengan **exception**, bukan dengan diam-diam
menghasilkan `a` dan `c` yang salah — jadi langsung ketahuan.

Kegagalan #3 jauh lebih berbahaya: hasilnya **kelihatan seperti jawaban** — satu bilangan besar,
tidak ada error. Yang membongkarnya cuma memeriksa panjang bitnya (127 bit, padahal LCG 64-bit) dan
verifikasi di langkah 3.3. Ini alasan konkret kenapa harus pakai sebanyak mungkin keluaran: tiap
`u` tambahan memangkas peluang faktor asing ikut terbawa di GCD.

---

## 6. Insight Utama & Teknik Unik

- **Kunci soal ini:** urutan pemulihan adalah keseluruhan serangannya. Tiga parameter tidak
  diketahui terlihat mustahil, tapi sebenarnya bisa dikupas berlapis — **selisih melenyapkan `c`**,
  **determinan melenyapkan `a`**, dan yang tersisa adalah kelipatan `m` murni. Setelah `m` jatuh,
  `a` dan `c` tinggal aljabar satu baris.

- **Teknik unik — GCD sebagai alat pemulihan, bukan sekadar pembagi.** Pola "bangun beberapa
  bilangan yang dijamin ≡ 0 mod rahasia, lalu GCD-kan" berlaku umum jauh melampaui LCG. Yang perlu
  dipastikan hanya satu: bilangan-bilangan itu tidak berbagi faktor lain. Karena itu **jumlah sampel
  adalah parameter keamanan bagi penyerang** — 4 keluaran memberi jawaban salah yang meyakinkan,
  5 keluaran memberi jawaban benar.

- **Parameter rahasia sering bukan rahasia.** `a` dan `c` yang terpulihkan persis konstanta MMIX
  Knuth, dan `m` adalah prima 64-bit yang terkenal. Menyembunyikan parameter LCG tidak memberi
  keamanan apa pun — LCG bocor total begitu beberapa keluaran berurutan terlihat, dan itulah kenapa
  LCG tidak boleh dipakai untuk apa pun yang bersifat keamanan (token, nonce, ID sesi).

- **Verifikasi dulu kalau percobaan hanya sekali.** Endpoint `/tebak` bukan oracle yang bisa
  di-brute force. Mencocokkan parameter ke ketujuh transisi yang diketahui mengubah tebakan
  jadi kepastian — biaya tiga baris kode.

- **Pelajaran:** hasil yang "kelihatan wajar" wajib diperiksa dimensinya. GCD di #3 memberi
  bilangan 127-bit untuk generator yang jelas-jelas 64-bit; ketidakcocokan ukuran itu sinyal
  paling awal bahwa jawabannya salah.

<!--
CHECKLIST ISI MINIMAL (slide "Format dan Isi Write-up")
  [x] 1. Judul dan kategori challenge     -> tabel info + metadata
  [x] 2. Flag yang ditemukan              -> bagian 1
  [x] 3. Analisis awal                    -> bagian 2
  [x] 4. Langkah penyelesaian             -> bagian 3 (3.1 - 3.4)
  [x] 5. Tools atau script                -> bagian 4 + solve.py
  [x] 6. Trial-and-error / langkah gagal  -> bagian 5 (5 poin, 3 gagal, semua diuji nyata)
  [x] 7. Insight utama / teknik unik      -> bagian 6
-->
