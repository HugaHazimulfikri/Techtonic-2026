#!/usr/bin/env python3
"""Regenerasi bagian 4 tiap WRITEUP.md dengan full source code dari disk.

Kode di writeup dibaca langsung dari berkasnya, jadi tidak mungkin melenceng
dari kode yang sebenarnya dijalankan. Jalankan ulang setiap kali script berubah.
"""
import re, pathlib

ROOT = pathlib.Path(__file__).parent
BERKAS = {
    "final/Jerat-Peladen":  ["params.py", "solve.py", "uji_pembulatan.py", "screenshot.py", "_shot.py"],
    "final/Dua-yang-Satu":  ["solve.py", "screenshot.py", "_shot.py"],
    "final/Timah-Hitam":    ["solve.py", "screenshot.py", "_shot.py"],
    "final/Firmware-Purba": ["solve.py", "screenshot.py"],
}
KET = {
    "params.py":         "parameter soal, dipisah supaya bisa langsung di-import solver",
    "solve.py":          "solver utama",
    "uji_pembulatan.py": "uji lokal Fraction vs integer // (lihat bagian 5)",
    "screenshot.py":     "render screenshot tiap langkah dari keluaran perintah sungguhan",
    "_shot.py":          "helper render bersama, ada di root repo",
}

for folder, daftar in BERKAS.items():
    wu = ROOT / folder / "WRITEUP.md"
    teks = wu.read_text()

    # ambil tabel tools yang sudah ada supaya tidak hilang
    bag4 = teks.split("## 4. Tools & Script yang Digunakan")[1].split("\n---\n")[0]
    baris = bag4.split("\n")
    tabel = [b for b in baris if b.startswith("|")]
    catatan = [b for b in baris if b.startswith("Catatan tooling:")]

    blok = ["## 4. Tools & Script yang Digunakan", ""] + tabel + [""]
    if catatan:
        blok += catatan + [""]
    blok += ["Seluruh kode di bawah ini disalin langsung dari berkas yang ada di folder "
             "soal ini, jadi bisa dijalankan apa adanya.", ""]

    for nama in daftar:
        p = (ROOT if nama == "_shot.py" else ROOT / folder) / nama
        if not p.exists():
            print(f"  ! lewat {folder}/{nama} (tidak ada)")
            continue
        blok += [f"### `{nama}`", "", f"> {KET.get(nama,'')}", "",
                 "```python", p.read_text().rstrip(), "```", ""]

    baru = teks.split("## 4. Tools & Script yang Digunakan")[0] + "\n".join(blok) + \
           "\n---\n" + teks.split("## 4. Tools & Script yang Digunakan")[1].split("\n---\n", 1)[1]
    wu.write_text(baru)
    print(f"  {folder}/WRITEUP.md  <- {len(daftar)} berkas kode  ({len(baru)//1024} KB)")

print("selesai")
