<!-- category: <kategori> | points: <poin> -->
# <Nama Soal>

| | |
| :--- | :--- |
| **Challenge** | <Nama Soal> |
| **Kategori** | <web / crypto / rev / pwn / forensic / osint / misc> |
| **Poin** | <poin> |
| **Author** | <author kalau ada> |
| **Connection** | <nc host port / url / file attachment> |
| **Solver** | nexsus404 |
| **Status** | Solved |

> Deskripsi soal dari panitia (tempel apa adanya di sini).

![soal](img/01-soal.png)

---

## 1. Flag

```
TechtonicExpoCTF{isi_flag_66394FFC}
```

> Flag **case-sensitive**. Tidak ada spasi/karakter tambahan saat submit.

![flag diterima](img/05-flag.png)

---

## 2. Analisis Awal

Apa yang dikasih panitia, dugaan awal, dan kenapa curiga ke arah situ.

- **Yang dikasih:** <file / url / nc>
- **Observasi pertama:** <...>
- **Hipotesis awal:** <...>

```bash
# perintah recon paling awal
```

![recon](img/02-recon.png)

---

## 3. Langkah Penyelesaian

Urut, tiap langkah reprodusibel (perintah + hasilnya).

### 3.1 <Recon / enumerasi>

```bash
# perintah
```

Hasil: <...>

### 3.2 <Menemukan celah / titik lemah>

```bash
# perintah
```

Hasil: <...>

![temuan](img/03-analisis.png)

### 3.3 <Eksploitasi / dekripsi / ekstraksi>

```bash
# perintah
```

Hasil: flag keluar.

![exploit](img/04-exploit.png)

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| <tool> | <versi> | <fungsinya di soal ini> |

Solver lengkap (`solve.py`):

```python
#!/usr/bin/env python3
# solver
```

---

## 5. Trial-and-Error / Langkah yang Gagal

Jujur catat yang dicoba tapi mentok, plus alasan gagalnya.

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | <...> | Gagal | <...> |
| 2 | <...> | Gagal | <...> |
| 3 | <...> | **Berhasil** | <...> |

---

## 6. Insight Utama & Teknik Unik

- **Kunci soal ini:** <satu kalimat inti kenapa soal ini bisa dipecahkan>
- **Teknik unik:** <trik / bypass / observasi yang tidak umum>
- **Pelajaran:** <yang dibawa ke soal berikutnya>

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
