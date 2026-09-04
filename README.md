# Techtonic-2026

Repo kerja tim CTF. Tiap anggota nge-push writeup soal yang di-solve ke **folder masing-masing**,
lalu digabung otomatis jadi satu `WRITEUP.md` pakai [`build_writeup.py`](build_writeup.py).

## 📁 Struktur folder

```
<anggota>/<challenge>/<file .md>      <- writeup (wajib, 1 per folder soal)
<anggota>/<challenge>/<gambar>        <- screenshot (opsional)
<anggota>/<challenge>/<solver, soal>  <- opsional
```

Folder anggota: `sanzxcte/`, `nexsus404/`, `x0r/`.

**Nama file writeup bebas** — nggak harus `WRITEUP.md`. Boleh `writeup.md`, `README.md`, atau
`.md` apa pun (mis. `bmn.md`, `catatan.md`). Kalau ada beberapa `.md`, yang dipakai `WRITEUP.md`/
`README.md` dulu, kalau nggak ada baru `.md` pertama (urut abjad).

**Gambar bebas ditaruh di mana aja** asal path-nya **relatif ke folder soal**. Semua path relatif
otomatis dibetulin saat digabung. Contoh yang semua valid:

```markdown
![x](img/01.png)        -> di subfolder img/
![x](01-soal.png)       -> langsung di folder soal
![x](ss/recon.png)      -> subfolder lain
![x](https://...)       -> URL (github dll) dibiarkan apa adanya
```

Contoh struktur:

```
nexsus404/BMN/WRITEUP.md      +  nexsus404/BMN/img/01-soal.png
sanzxcte/Ecliprime/solve.md   +  sanzxcte/Ecliprime/output.png
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

## 🔁 Mode watch (jalan sekali, auto terus)

Nggak mau jalanin manual tiap kali? Cukup **satu orang** jalanin ini sekali, biarin nongkrong:

```bash
python3 build_writeup.py --watch
```

Dia bakal cek repo tiap 20 detik. **Tiap ada anggota push writeup baru**, dia otomatis
`git pull` -> rakit ulang `WRITEUP.md` -> `git push`. Ctrl+C untuk berhenti.
Ganti interval kalau perlu: `--watch --interval 10` (cek tiap 10 detik).

> Cukup **satu orang** yang jalanin `--watch` (si "perakit"). Anggota lain tinggal push
> folder writeup masing-masing seperti biasa — `WRITEUP.md` diurus si perakit.

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
