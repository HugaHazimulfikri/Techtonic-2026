<img width="2000" height="1668" alt="image" src="https://github.com/user-attachments/assets/a6b77aff-5931-4d9d-bc7d-6a25facd8f34" /><!-- category: <kategori> | points: <poin> -->
# <Nama Soal>

| | |
| :--- | :--- |
| **Challenge** | Nama Tersembunyi |
| **Kategori** | osint  |
| **Poin** | 289 |
| **Author** | <author kalau ada> |
| **Connection** |Lampiran identitas_pensil (email.txt, kunci_arsip.txt, sketsa_awal.png, surat.txt, arsip.zip)|
| **Solver** | sanzxcte |
| **Status** | Solved |

> Seorang kontributor mengirim karya ke sebuah lomba fotografi menggunakan nama samaran. Panitia memerlukan identitas asli untuk verifikasi hak cipta, tetapi penulis hanya meninggalkan jejak digital yang tersebar.

Dalam arsip yang kamu dapatkan:
- Surat elektronik dari panitia yang menjelaskan konteks.
- Surat balasan dari penulis dengan nama samaran.
- Catatan panitia yang mengarah pada kebiasaan penulis.
- Sketsa awal karya (gambar).

Analisislah seluruh berkas. Nama samaran, kebiasaan, dan lokasi yang disebutkan saling terhubung. Beberapa informasi mungkin tersembunyi pada metadata gambar maupun pada data yang tidak terlihat langsung.

Kunci adalah nama lengkap asli penulis dalam format tanpa spasi, contoh: budi_santoso


![soal]
<img width="2000" height="1668" alt="image" src="https://github.com/user-attachments/assets/8c8a485a-ccb4-4a9f-9339-23a8c8c615c0" />

---

## 1. Flag

```
TechtonicExpoCTF{bagas_wicaksono_66394FFC}
```

> Flag **case-sensitive**. Tidak ada spasi/karakter tambahan saat submit.

---

## 2. Analisis Awal

Panitia lomba fotografi menerima kiriman karya dengan metadata terenkripsi dari seseorang yang menggunakan nama samaran pensil_hitam. Kita diberikan sekumpulan file arsip investigasi yang terdiri dari surel, petunjuk kunci arsip dalam bentuk Base64, sebuah file sketsa gambar, serta arsip terenkripsi yang menyimpan identitas asli.

- **Yang dikasih:** email.txt, kunci_arsip.txt, sketsa_awal.png, surat.txt, dan arsip.zip.
- **Observasi pertama:** surat.txt menyebutkan nama samaran penulis (pensil_hitam) dan meminta pemeriksaan metadata atau surel cadangan. kunci_arsip.txt menyimpan string terenkripsi Base64 yang mengarah ke password file arsip.
- **Hipotesis awal:** Kita harus mendekode password arsip terlebih dahulu untuk membuka arsip.zip, di mana file di dalamnya (identitas_asli.txt dan catatan_panitia.txt) akan menyingkap identitas asli sang penulis.

```bash
cat email.txt
cat surat.txt
cat kunci_arsip.txt
```

![recon]
<img width="2940" height="886" alt="image" src="https://github.com/user-attachments/assets/0807fe87-98b7-4e9a-8464-56c63570bbc7" />

---

## 3. Langkah Penyelesaian
Membaca isi berkas teks secara berurutan untuk merangkum petunjuk dan membuka kunci arsip.

### 3.1 <Rekonstruksi Petunjuk & Dekode Kunci Arsip>

```bash
cat kunci_arsip.txt
```

Hasil dekode menghasilkan string: tugu_jogja
<img width="966" height="388" alt="image" src="https://github.com/user-attachments/assets/1ae47183-eeda-4060-aadf-d0b68ad82f5a" />

### 3.2 <Ekstraksi Arsip Terenkripsi>
Menggunakan password tugu_jogja untuk membuka arsip.zip:
```bash
unzip -P tugu_jogja arsip.zip
```

Hasil: 
Di dalam arsip terdapat file identitas_asli.txt dan catatan_panitia.txt.
<img width="2172" height="682" alt="image" src="https://github.com/user-attachments/assets/32ca8c8c-56d9-491e-94bb-800430092b0b" />




### 3.3 <Membaca Identitas Asli Penulis>
Melihat isi dari file identitas_asli.txt:
```bash
cat identitas_asli.txt
```
Sesuai dengan ketentuan format kunci soal (nama lengkap asli penulis dalam format huruf kecil tanpa spasi dengan pemisah garis bawah, contoh: budi_santoso), maka nama Bagas Wicaksono diubah menjadi:
bagas_wicaksono

Flag : TechtonicExpoCTF{bagas_wicaksono_66394FFC}


<img width="818" height="230" alt="image" src="https://github.com/user-attachments/assets/fdd94f72-50c8-4db5-b090-4f7531448e1a" />


---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| cat / Built-in CLI | Bash | Membaca isi file teks penunjang (email.txt, surat.txt, kunci_arsip.txt) |
| Base64 Decoder | Built-in | Mendekode string Base64 pada file kunci_arsip.txt menjadi password |
| Unzip | 6.0 | Mengekstrak berkas arsip.zip menggunakan password hasil dekode |
=

---

## 5. Trial-and-Error / Langkah yang Gagal

Jujur catat yang dicoba tapi mentok, plus alasan gagalnya.

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | Langsung membuka arsip.zip tanpa password | Gagal | Arsip terenkripsi dan membutuhkan sandi otorisasi. |
| 2 | Menganalisis metadata gambar sketsa_awal.png secara mendalam mencari koordinat/teks | tidak relevan | Meskipun surat menyebutkan metadata, petunjuk utama akses dokumen identitas justru tersimpan secara langsung pada string Base64 di kunci_arsip.txt. |
| 3 | menemukan identitas asli | **Berhasil** | berhasil menemukan identitas asli dan benar |

---


<!--
=========================== CHECKLIST SEBELUM SUBMIT ===========================
Isi minimal (slide "Format dan Isi Write-up"):
  [ ] 1. Judul dan kategori challenge        -> tabel info + metadata baris 1
  [ ] 2. Flag yang ditemukan                 -> bagian 1
  [ ] 3. Analisis awal                       -> bagian 2
  [ ] 4. Langkah penyelesaian                -> bagian 3
  [ ] 5. Tools atau script yang digunakan    -> bagian 4
  [ ] 6. Trial-and-error / langkah gagal     -> bagian 5
  [ ] 7. Insight utama atau teknik unik      -> bagian 6

Batas teknis platform:
  [ ] Maksimum 2 MB per file  (cek: du -h WRITEUP.md ; du -sh img/)
  [ ] Format PDF / TXT / Markdown / gambar / ZIP  (rekomendasi panitia: PDF)
  [ ] 1 write-up untuk 1 tim + 1 challenge (jangan digabung)
  [ ] Upload SETELAH flag berhasil didapat
  [ ] Status awal setelah upload: "menunggu review"

Screenshot standar (taruh di img/, path relatif):
  01-soal.png     halaman challenge di platform: judul, kategori, poin, deskripsi
  02-recon.png    output perintah recon pertama
  03-analisis.png bukti celah/temuan yang bikin soal kebuka
  04-exploit.png  solver/exploit lagi jalan
  05-flag.png     flag muncul + notifikasi "Correct" di platform
===============================================================================
-->
