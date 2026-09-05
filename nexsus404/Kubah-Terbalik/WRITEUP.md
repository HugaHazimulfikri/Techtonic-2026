<!-- category: Cryptography | points: 750 -->
# Kubah Terbalik

| | |
| :--- | :--- |
| **Challenge** | Kubah Terbalik |
| **Kategori** | Cryptography · Eliminasi |
| **Poin** | 750 |
| **Connection** | `techtonicexpo.online/tantangan/15` → service `http://168.110.219.59:5016` |
| **Solver** | nexsus404 |
| **Status** | Solved |

> Dua pintu berlapis. Pintu pertama dikunci kartu terenkripsi yang rantainya saling memengaruhi.
> Mengubah satu kotak di depan akan mengubah isi di belakangnya. Ubah satu angka di kartu, dan
> peranmu berubah.
>
> Pintu kedua dijaga tanda tangan yang dibuat dari rahasia pendek yang disambung di depan data,
> lalu dicincang. Tanda itu bisa diulur tanpa tahu rahasianya, selama kamu paham cara cincang
> bekerja.
>
> Kedua lapis memberi separuh kata kunci.

![soal](img/01-soal.png)

---

## 1. Flag

```
TechtonicExpoCTF{balik_ulur_panjang_66394FFC}
```

Dirakit dari dua potongan: lapis satu memberi `balik`, lapis dua memberi `ulur_panjang`.

---

## 2. Analisis Awal

Service punya dua endpoint independen, masing-masing satu serangan kripto klasik. Deskripsinya
sudah menyebut nama serangannya secara tersamar:

| Kalimat di deskripsi | Serangan yang dimaksud |
| :--- | :--- |
| "rantainya saling memengaruhi" / "mengubah satu kotak di depan akan mengubah isi di belakangnya" | **CBC** (Cipher Block Chaining) → **bit-flipping** |
| "ubah satu angka di kartu, dan peranmu berubah" | target berupa **satu digit**, bukan kata |
| "rahasia pendek yang disambung **di depan** data, lalu dicincang" | `SHA256(rahasia ‖ data)` → **length extension** |
| "tanda itu bisa diulur tanpa tahu rahasianya" | konfirmasi: length extension, bukan brute force |

Bahan dari kedua endpoint:

```
/izin  kartu : 34bb4f272ce495247f66df02e7a85ac71c1100c7472a8e1b62e9c1235a23ca03
               e18c18db42ab52ad68f647aa3eda68f81951088e74311b41d536fee11bffa323
/ulur  data  : halaman=utama
       tanda : 0be8eb5f8bc38356bbf06ad423ccf71581991159ccf49b133d7f50be0d72431e
```

Struktur kartu:

```bash
echo "$KARTU" | fold -w32 | nl
```

```
1  34bb4f272ce495247f66df02e7a85ac7
2  1c1100c7472a8e1b62e9c1235a23ca03
3  e18c18db42ab52ad68f647aa3eda68f8
4  1951088e74311b41d536fee11bffa323
```

64 byte = **4 blok × 16 byte** → AES-CBC, blok 1 kemungkinan IV.

![recon](img/02-recon.png)

---

## 3. Langkah Penyelesaian

### 3.1 Petakan respons server jadi oracle

Kirim kartu asli dan beberapa kartu rusak, catat pesan yang keluar:

```bash
H=168.110.219.59:5016
curl -s "http://$H/izin/buka?data=$KARTU"      | sed 's/<[^>]*>//g'   # asli
curl -s "http://$H/izin/buka?data="            | sed 's/<[^>]*>//g'   # kosong
curl -s "http://$H/izin/buka?data=${KARTU:0:32}" | sed 's/<[^>]*>//g' # 1 blok
```

```
asli    -> TERTOLAK  Kartu tidak diakui sebagai admin.
kosong  -> TERTOLAK  Kartu tidak terbaca.
1 blok  -> TERTOLAK  Kartu tidak terbaca.
```

Dua pesan berbeda = **oracle**. "tidak terbaca" hanya muncul untuk masalah panjang, sedangkan
"tidak diakui sebagai admin" berarti kartu berhasil didekripsi dan di-parse. Artinya parser-nya
longgar — dikonfirmasi dengan membalik tiap byte IV, semuanya tetap "tidak diakui" (bukan
"tidak terbaca"). Bagus: berarti bit-flipping tidak akan tersandung validasi struktur.

### 3.2 Lapis satu — CBC bit-flipping

Pada CBC, dekripsi blok ke-*i* adalah:

```
P[i] = D(C[i]) XOR C[i-1]
```

Karena `C[-1]` adalah IV, **mengubah IV byte ke-j membalik plaintext blok-0 byte ke-j dengan delta
yang persis sama**, tanpa merusak blok lain. Itulah "mengubah satu kotak di depan akan mengubah isi
di belakangnya".

Petunjuk "ubah satu **angka**" dibaca harfiah: target adalah satu digit ASCII. Mengubah `'0'`
(0x30) jadi `'1'` (0x31) cukup XOR `0x01`. Posisinya belum diketahui, jadi disapu semua posisi yang
mengendalikan plaintext (byte 0–47):

```python
for p in range(48):
    m = bytearray(KARTU); m[p] ^= 0x01
    kirim(bytes(m))
```

Kena di posisi 6 pada percobaan pertama:

```
posisi  6 -> HIT: // LAPIS SATU  Kubah terbuka. Kata lapis pertama: balik
```

Posisi 6 masuk akal begitu dipetakan ke plaintext — blok 0 berisi `admin=0&...`:

```
index :  0  1  2  3  4  5  6
byte  :  a  d  m  i  n  =  0     <- XOR 0x01 -> '1'
```

**Kata lapis pertama: `balik`**

![lapis satu](img/03-lapis1.png)

### 3.3 Lapis dua — SHA-256 length extension

Endpoint `/ulur` memverifikasi `tanda == SHA256(rahasia ‖ data)`. Kirim pasangan asli dulu untuk
memastikan jalur verifikasinya:

```bash
curl -s "http://$H/ulur/buka?data=$(printf 'halaman=utama' | xxd -p)&tanda=0be8eb5f...431e"
```

```
DITERIMA  Tanda sah, tapi tidak ada perintah khusus di dalam data.
```

Tanda tangan valid, tinggal butuh perintah di dalam data. Karena lapis satu memakai `admin=1`,
perintah yang sama dicoba di sini.

SHA-256 adalah konstruksi **Merkle–Damgård**: digest akhir *adalah* state internal setelah blok
terakhir. Jadi digest yang diketahui bisa dipakai sebagai titik awal untuk melanjutkan hashing data
tambahan — tanpa pernah tahu rahasianya. Yang perlu ditebak hanya **panjang rahasia**, karena itu
menentukan padding yang harus disisipkan.

`hashpump` tidak tersedia, jadi SHA-256 ditulis ulang dengan state yang bisa di-set
([`sha256ext.py`](sha256ext.py)), diverifikasi dulu terhadap `hashlib`:

```python
for t in [b"", b"abc", b"halaman=utama", b"x"*200]:
    assert sha256(t).hex() == hashlib.sha256(t).hexdigest()
```

```
[+] self-test SHA-256 LULUS (cocok dengan hashlib)
```

Serangannya, untuk tiap tebakan panjang rahasia:

```python
L      = slen + len(DATA)                 # panjang pesan asli
glue   = md_pad(L)                        # padding asli -> ikut jadi bagian data
palsu  = DATA + glue + b"&admin=1"
tanda  = sha256(b"&admin=1", state=bytes.fromhex(SIG), prelen=L + len(glue)).hex()
```

```
[&admin=1] panjang rahasia = 16 -> HIT
// LAPIS DUA  Tali berhasil diulur. Kata lapis kedua: ulur_panjang
```

**Panjang rahasia 16 byte. Kata lapis kedua: `ulur_panjang`**

![lapis dua](img/04-lapis2.png)

### 3.4 Rakit flag

`balik` + `ulur_panjang` → `balik_ulur_panjang`, lalu tambahkan kode tim:

```
TechtonicExpoCTF{balik_ulur_panjang_66394FFC}
```

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| `curl` | 8.x | recon endpoint & pemetaan pesan error |
| `xxd` | — | konversi data ke hex untuk parameter `data=` |
| Python 3 | 3.14 | otomasi serangan (`urllib` stdlib, tanpa dependensi) |
| `hashlib` | stdlib | pembanding self-test SHA-256 |
| **SHA-256 custom** | — | [`sha256ext.py`](sha256ext.py) — SHA-256 dengan state bisa di-set |

`hashpump` / `hashpumpy` tidak terinstall, jadi length extension ditulis manual. Implementasinya
lengkap dengan self-test terhadap `hashlib`, supaya kalau serangan gagal bisa dipastikan penyebabnya
tebakan panjang rahasia — bukan bug di SHA-256-nya.

Solver lengkap: [`solve.py`](solve.py) (butuh `sha256ext.py` di folder yang sama)

```bash
python3 solve.py
```

```
[LAPIS 1] IV[6] ^= 0x01  ('0' -> '1')
          // LAPIS SATU Kubah terbuka. Kata lapis pertama: balik

[LAPIS 2] panjang rahasia = 16 byte, sambung '&admin=1'
          // LAPIS DUA Tali berhasil diulur. Kata lapis kedua: ulur_panjang
```

---

## 5. Trial-and-Error / Langkah yang Gagal

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | Kirim kartu asli apa adanya | Gagal | `Kartu tidak diakui sebagai admin` — memang harus dimodifikasi |
| 2 | Cari komentar/hint di HTML `/izin` & `/ulur` | Gagal | Halaman bersih, tidak ada bocoran format plaintext |
| 3 | Rusak byte terakhir kartu, harap bocor error padding | Gagal | Tetap `tidak diakui` — server tidak membocorkan padding oracle |
| 4 | Balik 0xFF tiap byte IV, cari posisi yang merusak parsing | Gagal | 16/16 tetap `tidak diakui` — parser longgar, tidak bisa dipakai memetakan struktur |
| 5 | Script Python pertama pakai `urllib` polos | **Gagal** | `HTTP 403 FORBIDDEN` — server memfilter User-Agent. Diperbaiki dengan `User-Agent: curl/8.5.0` |
| 6 | **Sapu XOR 0x01 di posisi 0–47** | **Berhasil** | Kena di posisi 6 → `admin=0` jadi `admin=1` |
| 7 | Length extension, filter respons cari `"tidak sah"` | **Gagal (bug sendiri)** | Pesan server ternyata `Tanda tidak cocok`, bukan `tidak sah`. Script salah lapor "HIT" di slen=1 padahal body-nya `[403] DITOLAK` |
| 8 | Ulangi dengan klasifikasi respons dibetulkan | **Berhasil** | Panjang rahasia 16 → `ulur_panjang` |

Dua kegagalan yang paling mahal justru bukan soal kriptografinya:

- **#5 (403)** — mudah disalahartikan sebagai "serangan ditolak" padahal cuma filter User-Agent.
  Ketahuan karena `curl` sudah lebih dulu berhasil untuk URL yang sama.
- **#7** — script menganggap "bukan pesan gagal" berarti sukses, jadi respons `403 DITOLAK` lolos
  jadi false positive. Pelajarannya: klasifikasikan respons dengan **mencocokkan pola sukses**,
  bukan dengan menegasikan pola gagal.

Percobaan #3 dan #4 sebenarnya tidak sia-sia — dua-duanya membuktikan parser server longgar, yang
justru menjamin sapuan bit-flip di #6 tidak akan tersandung validasi struktur.

---

## 6. Insight Utama & Teknik Unik

- **Kunci soal ini:** dua serangan yang sama-sama mengeksploitasi *integritas*, bukan *kerahasiaan*.
  Tidak ada kunci AES maupun rahasia HMAC yang pernah dipecahkan — CBC tanpa MAC membiarkan
  ciphertext dimodifikasi secara terarah, dan `SHA256(rahasia ‖ data)` membiarkan pesan diperpanjang.
  Keduanya adalah kegagalan otentikasi, dan keduanya lenyap kalau memakai HMAC atau AES-GCM.

- **Teknik unik — baca petunjuk deskripsi secara harfiah.** "Ubah satu **angka**" memangkas ruang
  pencarian dari 48 posisi × 256 delta (12.288 permintaan) jadi 48 posisi × **1 delta** (48
  permintaan), karena `'0' XOR '1' = 0x01`. Ketemu di percobaan ke-7. Menebak isi plaintext dulu
  ternyata tidak perlu sama sekali — cukup menebak *bentuk* targetnya.

- **Bedakan "tidak valid" dari "valid tapi kurang".** Respons `Tanda sah, tapi tidak ada perintah
  khusus` memastikan jalur verifikasi lapis dua sudah benar sebelum satu pun serangan dijalankan.
  Tanpa itu, kegagalan length extension jadi ambigu: salah panjang rahasia, atau salah perintah?

- **Self-test primitif kripto sebelum dipakai menyerang.** Menulis SHA-256 sendiri itu rawan salah
  ketik pada tabel K atau urutan rotasi, dan bug diam-diam akan terlihat identik dengan "panjang
  rahasia tidak ketemu" setelah 64 percobaan. Tiga baris `assert` terhadap `hashlib` menghilangkan
  seluruh kelas keraguan itu.

- **Pelajaran:** klasifikasi respons adalah bagian dari eksploit, bukan sekadar logging. Kegagalan
  #7 membuktikan filter yang ditulis asal bisa menyembunyikan hasil yang benar — atau lebih buruk,
  melaporkan sukses palsu.

<!--
CHECKLIST ISI MINIMAL (slide "Format dan Isi Write-up")
  [x] 1. Judul dan kategori challenge     -> tabel info + metadata
  [x] 2. Flag yang ditemukan              -> bagian 1
  [x] 3. Analisis awal                    -> bagian 2
  [x] 4. Langkah penyelesaian             -> bagian 3 (3.1 - 3.4)
  [x] 5. Tools atau script                -> bagian 4 + solve.py + sha256ext.py
  [x] 6. Trial-and-error / langkah gagal  -> bagian 5 (8 percobaan, 5 gagal)
  [x] 7. Insight utama / teknik unik      -> bagian 6
-->
