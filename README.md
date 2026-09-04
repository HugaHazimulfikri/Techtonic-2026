# Techtonic-2026

Repo kerja tim CTF. Tiap anggota nge-push writeup soal yang di-solve ke **folder masing-masing**,
lalu digabung otomatis jadi satu `WRITEUP.md` pakai [`build_writeup.py`](build_writeup.py).

## 📁 Struktur folder

```
<anggota>/<challenge>/WRITEUP.md      <- writeup (wajib)
<anggota>/<challenge>/img/*.png       <- screenshot (opsional, ditulis "img/xxx.png" di writeup)
<anggota>/<challenge>/<solver, soal>  <- opsional
```

Folder anggota: `sanzxcte/`, `nexsus404/`, `x0r/`.

Contoh:

```
nexsus404/BMN/WRITEUP.md
nexsus404/BMN/img/01-soal.png
sanzxcte/Ecliprime/WRITEUP.md
```

### Metadata opsional

Baris paling atas `WRITEUP.md` boleh diisi metadata biar tabel daftar isi rapi:

```
<!-- category: web | points: 498 -->
# BMN
...
```

Kalau nggak diisi pun aman: kategori/poin diisi `-`, judul diambil dari heading pertama.

## ⚡ Alur pas lomba

**Tiap anggota** (setelah solve):

```bash
git pull                                  # ambil update terbaru
mkdir -p nexsus404/NamaSoal/img           # ganti nexsus404 dgn folder kamu
# taruh WRITEUP.md + screenshot di situ
git add nexsus404/NamaSoal
git commit -m "add NamaSoal"
git push
```

**Gabung jadi satu** (siapa aja):

```bash
python3 build_writeup.py --pull --push
```

Itu bakal: `git pull` -> scan semua folder anggota -> rakit `WRITEUP.md` (daftar isi + semua
soal, path gambar dibetulin otomatis) -> `git commit` + `git push`.

## 🛠️ Opsi tool

```bash
python3 build_writeup.py                 # rakit folder saat ini -> WRITEUP.md
python3 build_writeup.py --pull          # git pull dulu, baru rakit
python3 build_writeup.py --push          # rakit lalu commit + push
python3 build_writeup.py -o GABUNGAN.md  # nama output lain
python3 build_writeup.py --members sanzxcte nexsus404 x0r   # atur urutan anggota

# clone dari nol lalu rakit sekali jalan:
python3 build_writeup.py --repo https://github.com/HugaHazimulfikri/Techtonic-2026.git --into techtonic
```

Cuma butuh **Python 3** (tanpa dependensi luar) + **git**.

## 🎨 Template & tampilan

Header dokumen hasil gabungan (judul + banner + tabel Team) diambil dari
[`_template/header.md`](_template/header.md). Edit file itu tiap event:

- ganti judul `# Writeup Techtonic-2026`
- ganti banner `_template/banner.png` dengan banner event
- isi skor tiap anggota setelah lomba selesai

Di bawah header, tool otomatis menambahkan **Daftar Isi Challenge** + semua writeup, dengan
page-break (`<div>`) di antara bagian biar rapi kalau di-export ke PDF (pakai `--no-pagebreak`
untuk mematikannya).
