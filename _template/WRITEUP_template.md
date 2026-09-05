<!-- category: <kategori> | points: <poin> -->
# <Nama Soal>

> Deskripsi soal dari panitia (tempel di sini).
>
> Author: <author> | Connection: <nc / url kalau ada>

## Reconnaissance

Langkah awal: cek file, jalankan, lihat perilakunya.

```bash
# contoh: file <soal> ; strings <soal> | grep ...
```

![recon](img/01-recon.png)

## Analisis

Jelaskan bug / mekanisme / celah yang ketemu.

## Exploitation

Langkah exploit + solver yang dipakai.

```python
# potongan solver / exploit
```

![flag](img/02-flag.png)

## Flag

```
FLAG{...}
```

<!--
  Cara pakai template ini:
  1. Salin ke folder soal kamu, rename jadi WRITEUP.md (nama file sebenarnya bebas):
       cp _template/WRITEUP_template.md <anggota>/<Nama-Soal>/WRITEUP.md
  2. Taruh screenshot di folder soal (mis. <anggota>/<Nama-Soal>/img/), path relatif.
  3. Isi metadata di baris paling atas (category & points) biar tabel Daftar Isi rapi.
     Kalau tidak diisi pun aman.
  4. Simpan: ./simpan.sh <anggota>/<Nama-Soal> "namasoal solved"
  Baris komentar ini boleh dihapus.
-->
