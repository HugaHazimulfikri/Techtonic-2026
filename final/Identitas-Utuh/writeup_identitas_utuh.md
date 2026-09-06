<!-- category: osint - final | points: 766 -->
# Identitas Utuh

| | |
| :--- | :--- |
| **Challenge** | Identitas Utuh |
| **Kategori** | OSINT · Final |
| **Poin** | 766 |
| **Author** | - |
| **Connection** | `identitas_utuh.zip` (catatan.txt, boarding_GA139.txt, boarding_GA601.txt, tugu_pensil.jpg) + service `http://168.110.219.59:5030/manifest` |
| **Solver** | sanzxcte |
| **Status** | Solved |

> Perjalanan seorang fotografer dimulai dari sebuah kasus lama: jejak pensil_hitam yang pernah terkuak di lomba fotografi. Namanya sempat terungkap, namun penyelidikan belum tuntas.
> Fotografer yang sama kemudian mendokumentasikan Tugu Pensil di Kulon Progo, gerbang menuju Yogyakarta. Dari unggahan ini, jejak digitalnya kembali terbuka. Telusuri lebih dalam: nama di balik metadata, dan dari mana ia benar-benar berasal melalui rute penerbangannya.
>
> **Berkas:**
> - Catatan perjalanan (teks).
> - Dua boarding pass lanjutan (teks).
> - Foto Tugu Pensil (gambar).
>
> Jangan terkecoh dengan nama yang sudah pernah terungkap sebelumnya. Identitas final hanya bisa ditemukan dengan menelusuri seluruh lapisan. Kunci adalah gabungan nama asli dan kota asal dalam format tanpa spasi dan lowercase.

---

## 1. Flag

```
TechtonicExpoCTF{waliyalhuzanmakassar_66394FFC}
```

> Flag **case-sensitive**. Tidak ada spasi/karakter tambahan saat submit.

---
<img width="2060" height="1580" alt="image" src="https://github.com/user-attachments/assets/e1e3ed58-d974-4181-801b-9b672112f9cb" />

## 2. Analisis Awal

Panitia memberikan sekumpulan arsip digital (folder `identitas_utuh`) yang merekam jejak perjalanan seorang fotografer beralias **pensil_hitam**, yang identitas aslinya sempat terkuak sebagian pada sebuah kasus lomba fotografi lama.

- **Yang dikasih:** Dua boarding pass teks (`boarding.txt`, `boarding2.txt`), satu catatan perjalanan (`catatan.txt`), dan satu foto (`tugu_pensil.jpg`).
- **Observasi pertama:**
  - Kedua boarding pass menunjukkan nama **W. HUZAN** dengan rute penerbangan berurutan: `TJQ → CGK` (GA139) lalu `CGK → UPG` (GA601).
  - `catatan.txt` menjelaskan bahwa lokasi foto (Tugu Pensil, Kulon Progo) hanyalah **gerbang** menuju Yogyakarta — bukan tujuan akhir maupun kota asal.
  - Deskripsi soal secara eksplisit memperingatkan agar **tidak terkecoh dengan nama yang sudah terungkap sebelumnya** — sinyal kuat bahwa nama di boarding pass (`W. HUZAN`) adalah umpan sebagian, bukan jawaban utuh.
- **Hipotesis awal:** Nama lengkap asli dan kota asal sebenarnya tersembunyi di metadata EXIF foto, dan kemungkinan ada lapisan tambahan (server/backend) yang harus dieksplorasi untuk mengonfirmasi data tersebut.

```bash
cat boarding.txt
cat boarding2.txt
cat catatan.txt
```
<img width="1888" height="960" alt="image" src="https://github.com/user-attachments/assets/e2fbfcd2-8e12-45fb-a1ae-ded02df509d7" />

---

## 3. Langkah Penyelesaian

### 3.1 Recon / Enumerasi Berkas Awal

Membaca seluruh berkas teks untuk merangkum kronologi perjalanan dan mengidentifikasi nama serta rute yang tersedia.

```bash
cat boarding.txt
cat boarding2.txt
cat catatan.txt
```
<img width="1888" height="960" alt="image" src="https://github.com/user-attachments/assets/53ab9b97-0c1b-4343-bd18-84fa941e421e" />

**Hasil:**
- `boarding.txt`: Nama **W. HUZAN**, rute **TJQ → CGK**, penerbangan **GA139**, kursi 21A.
- `boarding2.txt`: Nama **W. HUZAN**, rute **CGK → UPG**, penerbangan **GA601**, kursi 14C.
- `catatan.txt`: Mengonfirmasi identitas pensil_hitam sempat terkuak sebagian di lomba fotografi, dan foto Tugu Pensil di Kulon Progo hanyalah **pintu masuk (gerbang) menuju Yogyakarta** — bukan lokasi akhir.

### 3.2 Ekstraksi Metadata Foto (Menemukan Nama Asli)

Memeriksa metadata EXIF pada `tugu_pensil.jpg` untuk mencari identitas asli di balik alias pensil_hitam.

```bash
exiftool -a -G1 -s -ee tugu_pensil.jpg
```
<img width="2154" height="1042" alt="image" src="https://github.com/user-attachments/assets/ee6540cc-a314-4981-8d90-d16f66d9ef94" />

**Hasil:**
```
Artist    : Waliyal
Copyright : Waliyal Prasetyo - 2026
Comment   : Tersimpan: GA139 TJQ-CGK lalu GA601 CGK-UPG - siapa pemilik nama ini?
```

Field `Comment` berisi pertanyaan retoris yang menegaskan bahwa rute penerbangan pada boarding pass terkait erat dengan identitas asli si fotografer, sekaligus memperkuat dugaan bahwa nama `W. HUZAN` bukan jawaban final.

### 3.3 Eksplorasi Endpoint Rahasia (Cross-check via Server)

Mengingat deskripsi soal meminta penelusuran "seluruh lapisan", dicoba eksplorasi endpoint tambahan yang disediakan panitia di luar berkas lokal.

```bash
curl http://168.110.219.59:5030/manifest
```
<img width="2940" height="1676" alt="image" src="https://github.com/user-attachments/assets/be0e5e6a-8cdc-4af5-9139-96765f125554" />

Endpoint ini menampilkan daftar berkas arsip (`tugu_pensil.jpg`, `boarding_GA139.txt`, `boarding_GA601.txt`, `rahasia_perjalanan.txt`) dengan catatan bahwa berkas `rahasia_perjalanan.txt` berstatus **akses terbatas** dan petunjuk kredensialnya tersebar di metadata dan isi arsip lain.

Setelah merakit kombinasi dari metadata EXIF dan isi boarding pass, akses ke berkas rahasia berhasil dibuka melalui salah satu petunjuk di metadata yaitu 'GA601':

<img width="2940" height="1686" alt="image" src="https://github.com/user-attachments/assets/51d2358e-2458-4ca8-917b-8194a16b89d1" />


**Isi `rahasia_perjalanan.txt`:**
```
pemilik arsip: Waliyal Huzan
rute terakhir: GA601 menuju UPG
asal: dari sanalah ia berasal
berkas ini bagian dari arsip identitas_utuh
```

Berkas ini menjadi konfirmasi resmi dari panitia sekaligus **pembalik logika** dugaan awal:
1. **Nama asli** dikonfirmasi sebagai **Waliyal Huzan** — cocok dengan inisial "W. HUZAN" di boarding pass, bukan "Waliyal Prasetyo" dari field Copyright EXIF (yang ternyata adalah red herring/nama alias tambahan).
2. **Kota asal** bukan titik keberangkatan pertama (TJQ/Tanjung Pandan) seperti dugaan intuitif, melainkan **titik tujuan rute terakhir** (UPG), sesuai kalimat eksplisit *"asal: dari sanalah ia berasal"*.

### 3.4 Konversi Kode Bandara ke Kota Asal

Kode IATA **UPG** merujuk pada Bandara Sultan Hasanuddin, yang melayani kota **Makassar** (dahulu dikenal dengan nama Ujung Pandang — asal muasal kode "UPG").

```bash
echo "UPG -> Bandara Sultan Hasanuddin -> Makassar"
```

### 3.5 Menyusun Flag

Menggabungkan nama asli yang telah dikonfirmasi dengan kota asal sesuai format yang diminta soal (tanpa spasi, lowercase):

```
Waliyal Huzan + Makassar
→ waliyalhuzanmakassar
```

Flag final:
```
TechtonicExpoCTF{waliyalhuzanmakassar_66394FFC}
```

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| ExifTool | 13.36 | Mengekstrak metadata (Artist, Copyright, Comment) pada `tugu_pensil.jpg` |
| cURL | Built-in | Mengakses endpoint `/manifest` dan `/berkas/rahasia_perjalanan.txt` pada server tantangan |
| cat | Built-in | Membaca isi berkas teks (boarding pass & catatan perjalanan) |

---

## 5. Trial-and-Error / Langkah yang Gagal

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | Menyimpulkan flag langsung dari nama di boarding pass (`whuzan`) tanpa menelusuri metadata | Gagal | Soal secara eksplisit memperingatkan untuk tidak terkecoh dengan nama yang sudah terungkap sebelumnya; nama di boarding pass hanya inisial, bukan bentuk final yang diminta. |
| 2 | Menggunakan nama dari field Copyright EXIF (`Waliyal Prasetyo`) sebagai nama asli | Gagal | Field ini ternyata adalah jebakan/alias tambahan; konfirmasi resmi di `rahasia_perjalanan.txt` menyatakan nama asli adalah "Waliyal Huzan". |
| 3 | Menetapkan kota asal sebagai titik keberangkatan pertama rute (TJQ / Tanjung Pandan) | Gagal | Asumsi intuitif "asal = titik awal rute" ini terbalik oleh clue eksplisit di `rahasia_perjalanan.txt`: *"asal: dari sanalah ia berasal"* justru merujuk ke rute terakhir (UPG), bukan rute pertama. |
| 4 | Menggabungkan nomor penerbangan sebagai password akses (`GA139GA601`, dsb) untuk membuka `rahasia_perjalanan.txt` | Gagal | Password/akses ternyata memerlukan kombinasi spesifik nama dan istilah dari metadata + isi arsip lain, bukan sekadar nomor penerbangan. |
| 5 | Menyimpulkan kota asal sebagai Yogyakarta (tujuan akhir perjalanan menurut `catatan.txt`) | Gagal | Yogyakarta hanyalah tujuan wisata/dokumentasi terkini si fotografer, bukan kota asal kelahirannya; klarifikasi resmi hanya ada di `rahasia_perjalanan.txt` yang menunjuk ke UPG (Makassar). |

---

## 6. Insight Utama / Teknik Unik

- **Multi-layer misdirection:** Soal ini sengaja menumpuk beberapa lapisan nama dan lokasi umpan (nama di boarding pass, nama di field Copyright EXIF, lokasi foto di Kulon Progo/Yogyakarta) untuk menguji apakah solver benar-benar menelusuri **seluruh** sumber data, bukan berhenti di petunjuk pertama yang "kelihatan masuk akal".
- **Metadata sebagai jembatan, bukan jawaban akhir:** Field `Comment` pada EXIF tidak langsung memberi jawaban, melainkan berfungsi sebagai pertanyaan pemandu yang mengarahkan solver untuk mengaitkan rute penerbangan dengan identitas — jawaban final tetap harus dikonfirmasi lewat sumber tambahan (endpoint server).
- **Server tantangan sebagai lapisan verifikasi:** Endpoint `/manifest` dan berkas berproteksi `rahasia_perjalanan.txt` menunjukkan bahwa CTF ini menggabungkan teknik forensik file statis dengan eksplorasi web sederhana — solver perlu merakit kredensial dari clue offline untuk membuka data konfirmasi online.
- **Kode IATA sebagai representasi kota:** Pemahaman dasar kode bandara (`UPG` = Makassar/eks-Ujung Pandang) menjadi kunci penerjemahan akhir dari data rute penerbangan menjadi nama kota yang dibutuhkan format flag.
