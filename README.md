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

**Tiap anggota** (setelah solve): taruh writeup di folder kamu, lalu simpan pakai **satu perintah**:

```bash
mkdir -p nexsus404/NamaSoal/img     # ganti nexsus404 dgn folder kamu; taruh writeup + gambar
./simpan.sh nexsus404/NamaSoal "NamaSoal solved"
```

`simpan.sh` otomatis `git add` -> `commit` -> `git pull --rebase` -> `git push` (retry kalau
origin barusan berubah), jadi **nggak perlu ngetik perintah git manual** dan nggak kena "fetch
first". Kalau mau simpan semua perubahan sekaligus: `./simpan.sh` (tanpa argumen).

<details><summary>Cara manual (kalau nggak mau pakai simpan.sh)</summary>

```bash
git add nexsus404/NamaSoal
git commit -m "add NamaSoal"
git pull --rebase && git push
```
</details>

**Gabung jadi satu** (siapa aja):

```bash
python3 build_writeup.py --pull --push
```

Itu bakal: `git pull` -> scan semua folder anggota -> rakit `WRITEUP.md` (daftar isi + semua
soal, path gambar dibetulin otomatis) -> `git commit` + `git push`.

## 😴 Cara paling enak (biar nggak nabrak)

Idenya: **cuma 1 orang jadi "perakit"** yang ngerakit `WRITEUP.md` otomatis TAPI **nggak push**.
Karena perakit nggak push, `origin` nggak pernah dapat commit `WRITEUP.md` -> **anggota lain
aman push seperti biasa, nggak kena "fetch first"**.

**Perakit** (1 orang) — jalanin sekali, biarin nongkrong:

```bash
python3 build_writeup.py --watch
```
Tiap ada anggota push writeup baru, dia otomatis `git pull` -> rakit ulang `WRITEUP.md`
**di lokal** (nggak di-push). Perakit selalu punya `WRITEUP.md` gabungan versi terbaru di
komputernya. Ganti interval: `--watch --interval 10`. Ctrl+C untuk berhenti.

**Anggota lain** — push writeup masing-masing seperti biasa (nggak jalanin tool apa pun):

```bash
git add namafolder/NamaSoal
git commit -m "NamaSoal"
git push
# atau singkat: ./simpan.sh namafolder/NamaSoal
```

**Publish `WRITEUP.md` final** — di AKHIR lomba, perakit push sekali:

```bash
python3 build_writeup.py --push
```

> `WRITEUP.md` sengaja di-`.gitignore` biar nggak kepush nggak sengaja selama lomba. Perakit
> pegang versi lokalnya; baru di-publish pas `--push` di akhir.

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
