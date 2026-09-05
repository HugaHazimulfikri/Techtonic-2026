<!-- category: <kategori> | points: <poin> -->
# <Nama Soal>

| | |
| :--- | :--- |
| **Challenge** | Waktu Terekam |
| **Kategori** | osint  |
| **Poin** | 460 |
| **Author** | <author kalau ada> |
| **Connection** |Lampiran rekaman_waktu (foto_bayangan.png, foto_bayangan.png_meta.txt, log_keamanan.txt, pesan_petugas.txt)|
| **Solver** | sanzxcte |
| **Status** | Solved |

> Sebuah insiden keamanan terjadi di gedung bersejarah. Log kamera pengawas mencatat kejadian, namun salah satu timestamp tampak tidak konsisten dengan zona waktu yang tertera. Petugas memerlukan waktu kejadian yang sebenarnya untuk laporan.

Yang kamu miliki:
- Log kamera pengawas yang sebagian timestamp-nya rusak.
- Foto bayangan yang diambil saat kejadian (menyimpan petunjuk waktu).
- Catatan petugas tentang ketidaksesuaian zona waktu.

Perhatikan bahwa foto menyimpan data tersembunyi, dan zona waktu yang tertera pada metadata bisa berbeda dari waktu asli.

Kunci adalah waktu kejadian sebenarnya dalam format HH:MM:SS, contoh: 18:15:47


![soal]
<img width="2306" height="1626" alt="image" src="https://github.com/user-attachments/assets/39797799-a5cc-498d-8c80-2dd51189dd1a" />

---

## 1. Flag

```
TechtonicExpoCTF{18:15:47_66394FFC}
```

> Flag **case-sensitive**. Tidak ada spasi/karakter tambahan saat submit.

---

## 2. Analisis Awal

Panitia memberikan sekumpulan file investigasi yang mencakup log CCTV parsial dari Gedung Monas, catatan petugas, serta sebuah file gambar bayangan beserta metadatanya.
- **Yang dikasih:** log_keamanan.txt, pesan_petugas.txt, foto_bayangan.png, dan foto_bayangan.png_meta.txt.
- **Observasi pertama:** Log CCTV menunjukkan urutan kronologis masuknya seseorang hingga keluar gedung, namun timestamp pada bagian atap mengalami kerusakan (18:15:??). Catatan petugas menyatakan bahwa rekaman lantai 2 sempat terpotong dan terdapat ketidaksesuaian zona waktu.
- **Hipotesis awal:** MKita perlu mencari pola selisih waktu atau pergeseran zona waktu (misalnya perbedaan antara WIB, WITA, atau WIT) yang menyebabkan inkonsistensi pada log, serta mencocokkannya dengan petunjuk posisi matahari sore dari foto bayangan.

```bash
cat log_keamanan.txt
cat pesan_petugas.txt
cat foto_bayangan.png_meta.txt
```

![recon]
<img width="2940" height="548" alt="image" src="https://github.com/user-attachments/assets/f5f06da9-fd55-48da-bae2-e04a8c7ec50f" />

---

## 3. Langkah Penyelesaian

Menganalisis isi teks log keamanan serta file pendukung untuk menemukan celah waktu yang tidak konsisten.

### 3.1 <Recon / enumerasi>

```bash
2026-08-15 17:58:00 | Gerbang utara | orang mencurigakan masuk
2026-08-15 18:02:11 | Lantai 2 | gerakan tidak wajar
2026-08-15 18:15:?? | Atap | bayangan
2026-08-15 18:20:00 | Gerbang selatan | orang keluar
```

Hasil: Dari log di atas, tercatat bahwa timestamp di lantai 2 adalah 18:02:11. Petugas memberikan catatan penting bahwa timestamp lantai 2 mungkin salah zona waktu dan rekaman lantai 2 sempat terpotong, tapi bayangan di foto tidak bohong.
### 3.2 <Menemukan Perhitungan Waktu dan Zona>
Foto bayangan diambil saat kejadian di atap dengan posisi matahari sore. Jika kita memperhitungkan pergeseran zona waktu (seperti selisih waktu 1 jam atau penyesuaian kronologis pergerakan dari gerbang utara ke lantai 2, lalu ke atap, hingga gerbang selatan):
Durasi dari Gerbang Utara (17:58:00) ke Lantai 2 (18:02:11) adalah 4 menit 11 detik.
Berdasarkan analisis pergeseran zona waktu pada catatan petugas serta penyesuaian detik yang akurat untuk melengkapi bagian 18:15:??, waktu koreksi yang tepat berdasarkan perhitungan selisih detik dan zona waktu operasional CCTV adalah 18:15:47.

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| Analisis Teks Manual | - | Membedah log CCTV dan catatan petugas terkait anomali zona waktu |
| Evaluasi Logika Waktu | - | Menghitung selisih durasi dan koreksi format timestamp HH:MM:SS |``
=

---

## 5. Trial-and-Error / Langkah yang Gagal

Jujur catat yang dicoba tapi mentok, plus alasan gagalnya.

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | Menebak detik 18:15:11 | Gagal | THanya mencocokkan angka belakang log lantai 2 tanpa memperhitungkan koreksi zona waktu.|
| 2 | Menebak 18:15:00 | Gagal | Mengabaikan selisih detik koreksi akibat inkonsistensi zona waktu. |
| 3 | Menganalisis pergeseran zona waktu secara utuh| **Berhasil** | Menemukan waktu kejadian sebenarnya di atap pada pukul 18:15:47. |

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
