<!-- category: OSINT | points: 464 -->
# Dua Jejak

| | |
| :--- | :--- |
| **Challenge** | Dua Jejak |
| **Kategori** | OSINT · Eliminasi |
| **Poin** | 464 (dynamic scoring) |
| **Connection** | `techtonicexpo.online/tantangan/39` — attachment `dua_jejak.zip` |
| **Solver** | nexsus404 |
| **Status** | Solved |

> Dua buah foto ditemukan dari dua hari yang berbeda, diduga diambil oleh orang yang sama di lokasi
> yang sama. Kamu diminta mengidentifikasi pemilik jejak berdasarkan konsistensi data.
>
> Berkas: dua foto (jejak_a, jejak_b) dan catatan analisis awal.
>
> Bandingkan kedua foto secara mendalam — termasuk data yang tidak terlihat langsung. Ada nama yang
> konsisten di antara keduanya.
>
> Kunci adalah nama pemilik dalam format tanpa spasi, contoh: `rani_desa`

![soal](img/01-soal.png)

---

## 1. Flag

```
TechtonicExpoCTF{rani_desa_66394FFC}
```

Bukti diterima platform ada di tangkapan halaman soal di atas — status **SOLVED** dengan
keterangan *"✓ FLAG BENAR"*.

![flag diterima](img/01-soal.png)

---

## 2. Analisis Awal

Isi arsip:

```bash
unzip -l dua_jejak.zip
```

```
     2949  2026-09-01 12:18   jejak_a.png
       82  2026-09-01 12:18   analisis.txt
     3058  2026-09-01 12:18   jejak_b.png
```

```bash
cat analisis.txt
```

```
Dua jejak berbeda hari, lokasi sama. Cari nama pemilik yang konsisten di keduanya.
```

Kedua PNG berukuran sama (800×600 RGB) dan sama-sama sangat kecil (±3 kB). Deskripsi menekankan
tiga hal yang jadi kerangka kerja:

| Kalimat | Artinya secara teknis |
| :--- | :--- |
| "data yang tidak terlihat langsung" | metadata dan/atau steganografi piksel |
| "konsistensi data" | jawaban harus dikuatkan **dua sumber**, bukan satu |
| "contoh: `rani_desa`" | format jawaban — **tapi lihat catatan penting di bawah** |

> ⚠️ **Jebakan kepercayaan diri.** Contoh format di deskripsi kebetulan **identik** dengan jawaban
> akhirnya. Artinya, siapa pun yang asal menebak `rani_desa` akan benar tanpa mengerti soalnya —
> dan sebaliknya, menemukan string `rani_desa` di dalam berkas **belum membuktikan apa-apa**, karena
> bisa saja itu cuma echo dari contoh. Karena itu jawaban di sini tidak diterima sampai ada bukti
> **independen** dari berkas kedua.

![recon](img/02-recon.png)

---

## 3. Langkah Penyelesaian

### 3.1 Metadata — hanya satu berkas yang bicara

```bash
exiftool jejak_a.png
exiftool jejak_b.png
```

`jejak_a.png` bersih, hanya field PNG standar. `jejak_b.png` punya satu field tambahan:

```
Comment  : bmFtYSBrb25zaXN0ZW46IHJhbmlfZGVzYQ==
```

Dikonfirmasi di tingkat chunk, bukan cuma lewat exiftool:

```python
# enumerasi chunk PNG mentah
jejak_a.png: IHDR, IDAT, IEND                      -> tidak ada chunk teks
jejak_b.png: IHDR, tEXt(44), IDAT, IEND            -> ada tEXt
```

```bash
echo 'bmFtYSBrb25zaXN0ZW46IHJhbmlfZGVzYQ==' | base64 -d
```

```
nama konsisten: rani_desa
```

Jawabannya sudah muncul di sini — **tapi baru satu sumber**, dan persis sama dengan contoh di
deskripsi. Belum cukup. `jejak_a` harus dibuat bicara juga.

### 3.2 Menemukan modulasi piksel di jejak_a

`jejak_a.png` dibuka: warnanya rata, tidak ada apa-apa yang terlihat.

Dugaan pertama saya adalah ukuran IDAT: 2892 byte terasa besar untuk gambar satu warna. Dugaan itu
**dibantah sendiri** dengan membuat pembanding:

```python
Image.fromarray(np.full((600,800,3),(100,80,90),np.uint8)).save('/tmp/polos.png')
```

```
/tmp/polos.png   IDAT = 2734 byte
jejak_a.png      IDAT = 2892 byte     (+158)
jejak_b.png      IDAT = 2945 byte     (+211)
```

Selisihnya cuma ±150–200 byte — **bukan** anomali mencolok. Jadi ukuran berkas bukan petunjuk yang
bisa diandalkan di sini.

Yang benar-benar membongkar adalah **menghitung nilai piksel unik per channel**:

```python
for c, ch in enumerate("RGB"):
    print(ch, np.unique(a[:, :, c]))
```

```
jejak_a.png  R: 2 nilai [100 101]   <== dua nilai, selisih tepat 1
jejak_a.png  G: 1 nilai [80]
jejak_a.png  B: 1 nilai [90]
```

Channel G dan B benar-benar konstan, tapi **R punya tepat dua nilai yang berselisih 1** (100/101).
Itu tanda tangan LSB steganography yang tidak bisa salah: bit terendah channel merah dipakai sebagai
kanal data, sedangkan mata melihatnya sebagai satu warna rata.

![temuan piksel](img/03-piksel.png)

### 3.3 Membaca payload LSB dari kedua foto

```python
bits = (a[:, :, 0] & 1).flatten()
data = np.packbits(bits, bitorder="big").tobytes()
pesan = data.split(b"\x7f\x7f\x7f")[0]        # 7f 7f 7f = terminator
```

```
jejak_a.png : 'pemilik: Rani, dari Semarang'
jejak_b.png : 'foto kedua diambil di kota lama Semarang'
```

Sisa aliran bit setelah terminator `7f 7f 7f` diperiksa dan **seluruhnya nol** (59.969 dan 59.957
byte), jadi tidak ada payload lain yang terlewat.

### 3.4 Menyatukan bukti

| Sumber | Isi | Perannya |
| :--- | :--- | :--- |
| LSB `jejak_a` | `pemilik: Rani, dari Semarang` | **nama pemilik** — bukti independen |
| LSB `jejak_b` | `foto kedua diambil di kota lama Semarang` | **lokasi sama** — memvalidasi premis soal |
| tEXt `jejak_b` | `nama konsisten: rani_desa` | **format jawaban** |

Ketiganya saling menguatkan: nama `Rani` muncul dari berkas yang **tidak** punya tEXt, dan kota
`Semarang` muncul di kedua foto — persis "lokasi sama" seperti kata `analisis.txt`. Jadi `rani_desa`
bukan sekadar echo dari contoh di deskripsi, melainkan memang nama pemiliknya.

```
TechtonicExpoCTF{rani_desa_66394FFC}
```

![solver](img/04-solver.png)

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| `unzip` | — | membuka arsip |
| `exiftool` | 13.55 | pemindaian metadata awal |
| `base64` | coreutils | decode isi tEXt |
| Python 3 + **NumPy** | 2.5.1 | hitung nilai unik + ekstraksi LSB |
| Python 3 + **Pillow** | 12.3.0 | baca piksel PNG |

Enumerasi chunk PNG ditulis manual dengan `struct.unpack(">I", ...)` supaya terlihat bahwa
`jejak_a` benar-benar **tidak punya** chunk teks — `exiftool` hanya menampilkan yang ada, tidak
menegaskan yang tidak ada.

Solver lengkap: [`solve.py`](solve.py)

```bash
python3 solve.py
```

```
=== chunk PNG ===
  jejak_a.png: tidak ada chunk teks
  jejak_b.png: [('Comment', 'bmFtYSBrb25zaXN0ZW46IHJhbmlfZGVzYQ==')]
     decode      : nama konsisten: rani_desa

=== nilai piksel unik (kunci penemuan) ===
  jejak_a.png R: 2 nilai [100 101]  <== 2 nilai, beda 1 -> LSB dipakai

=== payload LSB channel merah ===
  jejak_a.png: 'pemilik: Rani, dari Semarang'
  jejak_b.png: 'foto kedua diambil di kota lama Semarang'

FLAG : TechtonicExpoCTF{rani_desa_66394FFC}
```

---

## 5. Trial-and-Error / Langkah yang Gagal

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | `exiftool jejak_a.png` | **Gagal** | Hanya field PNG standar. Sempat menyimpulkan berkas ini memang kosong |
| 2 | Buka `jejak_a.png` secara visual | **Gagal** | Satu warna rata, tidak ada apa pun terlihat |
| 3 | Asumsi "kedua berkas menyembunyikan dengan cara yang sama" | **Salah** | Hanya `jejak_b` punya tEXt. Teknik yang sama pada `jejak_a` tidak menghasilkan apa-apa |
| 4 | Menyimpulkan ada data dari **ukuran IDAT** (2892 byte) | **Penalaran salah** | Dibuat PNG satu warna pembanding: 2734 byte. Selisih cuma +158 byte, bukan anomali. Petunjuk ini tidak valid |
| 5 | Unpack LSB dengan `bitorder="little"` | **Gagal** | Keluar biner acak `\x0e\xa6\xb6\x966...`. Yang benar `big` |
| 6 | Berhenti di base64 `jejak_b` sebagai jawaban | **Tidak aman** | String-nya identik dengan contoh di deskripsi, jadi bisa saja decoy. Butuh bukti kedua |
| 7 | **Hitung nilai piksel unik per channel** | **Berhasil** | R punya tepat 2 nilai berselisih 1 → LSB terbongkar di kedua berkas |

Kegagalan #4 paling layak dicatat karena itu **kesalahan penalaran saya sendiri, bukan jalan buntu
soal**. "File-nya terasa terlalu besar" adalah intuisi yang enak dipercaya tapi tidak pernah saya
uji. Begitu dibuatkan pembanding, dugaan itu langsung runtuh. Kalau tidak diuji, saya akan menulis
alasan yang salah di write-up ini — kebetulan menuju kesimpulan yang benar, yang justru lebih
berbahaya.

Kegagalan #6 adalah godaan terbesar soal ini: jawaban benar sudah tersedia di langkah pertama, dan
kebetulan sama dengan contoh di deskripsi. Berhenti di situ akan tetap dapat poin, tapi tanpa tahu
kenapa.

---

## 6. Insight Utama & Teknik Unik

- **Kunci soal ini: penyembunyian yang asimetris.** Dua berkas yang terlihat kembar memakai **teknik
  berbeda** — `jejak_b` lewat metadata (tEXt), `jejak_a` lewat piksel (LSB). Menjalankan satu teknik
  pemeriksaan pada kedua berkas hanya membuka separuh soal. Justru berkas yang "bersih" menurut
  `exiftool` yang menyimpan bukti paling penting, yaitu nama pemiliknya.

- **Teknik unik — hitung nilai unik per channel, bukan ukuran berkas.** Untuk gambar sintetis,
  `len(np.unique(kanal))` adalah detektor anomali yang jauh lebih tajam daripada ukuran berkas.
  Dua nilai yang berselisih tepat 1 pada satu channel, sementara channel lain benar-benar konstan,
  adalah sidik jari LSB yang tidak mungkin muncul secara alami. Satu baris kode, dan hasilnya biner:
  ada atau tidak ada.

- **`exiftool` menjawab "apa yang ada", bukan "apa yang tidak ada".** Output bersih mudah dibaca
  sebagai "berkas ini kosong", padahal artinya cuma "tidak ada field yang saya kenali". Enumerasi
  chunk mentah memberi jawaban yang tegas — dan di soal ini, ketiadaan tEXt di `jejak_a` justru
  informasi penting: ia memaksa pencarian pindah ke ranah piksel.

- **Jawaban yang benar bukan berarti penalaran yang benar.** Contoh format di deskripsi kebetulan
  sama dengan kuncinya, jadi tebakan buta pun berhasil. Ini kasus bagus untuk membiasakan
  **konfirmasi silang**: satu sumber memberi jawaban, sumber kedua yang independen memberi keyakinan.
  Di sini `pemilik: Rani` dari `jejak_a` dan `Semarang` di kedua foto yang mengubah tebakan jadi
  kesimpulan.

- **Pelajaran:** uji dugaanmu sendiri sebelum menulisnya sebagai alasan. Membuat satu PNG pembanding
  butuh sepuluh detik dan menyelamatkan write-up ini dari memuat penjelasan yang keliru.

<!--
CHECKLIST ISI MINIMAL (slide "Format dan Isi Write-up")
  [x] 1. Judul dan kategori challenge     -> tabel info + metadata
  [x] 2. Flag yang ditemukan              -> bagian 1
  [x] 3. Analisis awal                    -> bagian 2
  [x] 4. Langkah penyelesaian             -> bagian 3 (3.1 - 3.4)
  [x] 5. Tools atau script                -> bagian 4 + solve.py
  [x] 6. Trial-and-error / langkah gagal  -> bagian 5 (7 poin, 6 gagal, semua nyata & diuji)
  [x] 7. Insight utama / teknik unik      -> bagian 6
-->
