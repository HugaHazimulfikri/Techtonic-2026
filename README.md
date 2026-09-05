# Techtonic-2026

Repo kerja tim CTF **DOSCOM**. Tiap anggota menaruh writeup soal yang di-solve ke **folder
masing-masing**, lalu semuanya digabung otomatis jadi satu `WRITEUP.md` oleh
[`build_writeup.py`](build_writeup.py).

Folder anggota: `nexsus404/`, `sanzxcte/`, `x0r/`.

---

## 1. Struktur folder

```
<anggota>/<nama-soal>/<file .md>     writeup   (WAJIB: 1 file .md per folder soal)
<anggota>/<nama-soal>/<gambar>       screenshot (opsional)
<anggota>/<nama-soal>/<solver, dsb>  file lain  (opsional)
```

Contoh:

```
nexsus404/BMN/WRITEUP.md
nexsus404/BMN/img/01-soal.png
sanzxcte/Ecliprime/solve.md
sanzxcte/Ecliprime/output.png
```

Aturan yang wajib cuma dua:

1. **1 soal = 1 folder**, tepat 2 tingkat: `anggota/nama-soal/`. Jangan dinesting lebih dalam.
2. **1 file writeup `.md` per folder soal.** Nama bebas (`WRITEUP.md`, `writeup.md`, `bmn.md`, dst).
   Kalau ada beberapa `.md`, yang dipakai `WRITEUP.md`/`README.md` dulu, kalau tidak ada baru `.md`
   pertama (urut abjad).

**Gambar bebas** ditaruh di mana saja asal path-nya relatif ke folder soal. Semua otomatis
dibetulkan saat digabung:

```markdown
![x](img/01.png)     di subfolder img/
![x](01-soal.png)    langsung di folder soal
![x](ss/recon.png)   subfolder lain
![x](https://...)    URL (github dll) dibiarkan apa adanya
```

**Metadata opsional** di baris paling atas file writeup, biar tabel Daftar Isi rapi (kalau tidak
diisi, kategori/poin jadi `-`, judul diambil dari heading pertama atau nama folder):

```
<!-- category: web | points: 498 -->
# BMN
...isi writeup...
```

---

## 2. Alur pas lomba

### Anggota (tiap orang)

Biar cepat, salin template kosong ke folder soal kamu lalu isi:

```bash
mkdir -p nexsus404/NamaSoal/img
cp _template/WRITEUP_template.md nexsus404/NamaSoal/WRITEUP.md
```

Terus edit `WRITEUP.md`-nya (ada di [`_template/WRITEUP_template.md`](_template/WRITEUP_template.md)),
taruh screenshot di `img/`, lalu simpan. Cara paling gampang, satu perintah:

```bash
./simpan.sh nexsus404/NamaSoal "namasoal solved"
```

`simpan.sh` otomatis `git add` -> `commit` -> `git pull --rebase` -> `git push` (dengan retry),
jadi tidak perlu ngetik perintah git manual dan tidak kena error "fetch first". Argumen boleh
dikosongkan: `./simpan.sh` saja artinya simpan semua perubahan.

Kalau mau manual:

```bash
git add nexsus404/NamaSoal
git commit -m "namasoal"
git pull --rebase && git push
```

### Perakit (cukup 1 orang)

Jalankan sekali, biarkan nongkrong. Dia auto-rakit `WRITEUP.md` gabungan **di lokal, tanpa push**:

```bash
python3 build_writeup.py --watch
```

Tiap ada anggota push writeup baru, dia otomatis `git pull` + rakit ulang `WRITEUP.md` di komputer
perakit. Karena perakit **tidak push**, `origin` tidak pernah dapat commit `WRITEUP.md` dari
perakit, jadi **anggota lain aman push seperti biasa tanpa tabrakan**. Ctrl+C untuk berhenti.

### Publish `WRITEUP.md` final

Di akhir lomba, perakit publish sekali:

```bash
python3 build_writeup.py --push
```

> `WRITEUP.md` sengaja masuk `.gitignore` (yang di ROOT saja) biar tidak kepush tidak sengaja
> selama lomba. Baru muncul di GitHub saat `--push`.

---

## 3. Opsi tool

```bash
python3 build_writeup.py                 # rakit sekali -> WRITEUP.md (lokal)
python3 build_writeup.py --pull          # git pull dulu, baru rakit
python3 build_writeup.py --push          # rakit lalu commit + push (publish)
python3 build_writeup.py --watch         # nongkrong, auto rakit lokal tiap ada push baru
python3 build_writeup.py --watch --push  # nongkrong + auto publish tiap update
python3 build_writeup.py --watch --interval 10   # ganti interval cek (detik)
python3 build_writeup.py -o GABUNGAN.md  # nama output lain
python3 build_writeup.py --members sanzxcte nexsus404 x0r   # atur urutan anggota

# clone dari nol lalu rakit sekali jalan:
python3 build_writeup.py --repo https://github.com/HugaHazimulfikri/Techtonic-2026.git --into tech
```

Cuma butuh **Python 3** (tanpa dependensi luar) + **git**.

---

## 4. Template tampilan

Header dokumen gabungan (judul + banner + tabel Team) diambil dari
[`_template/header.md`](_template/header.md). Edit file itu tiap event:

- ganti judul `# Writeup Techtonic-2026`
- ganti banner `_template/banner.png` dengan banner event ini
- isi skor tiap anggota

Di bawah header, tool otomatis menambahkan **Daftar Isi Challenge** + semua writeup, dengan
pemisah page-break (buat rapi kalau di-export PDF). Matikan dengan `--no-pagebreak`.

---

## Ringkas

| Peran | Perintah |
| :---- | :------- |
| Anggota simpan writeup | `./simpan.sh <folder-soal> "pesan"` |
| Perakit gabung otomatis | `python3 build_writeup.py --watch` |
| Publish final | `python3 build_writeup.py --push` |
