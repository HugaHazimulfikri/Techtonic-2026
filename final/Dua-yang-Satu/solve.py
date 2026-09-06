#!/usr/bin/env python3
"""Dua yang Satu - gabungkan dua berkas dengan XOR untuk memulihkan pesan.

Dua berkas berukuran sama yang masing-masing tampak acak = pola XOR berpasangan.
XOR bekerja per posisi, jadi bagian "di-urutkan ulang" pada deskripsi soal tidak
perlu dipulihkan: selama kedua berkas diacak dengan permutasi yang sama,
kiri[i] ^ kanan[i] tetap menghasilkan plain[i].
"""
import sys, zipfile

KIRI, KANAN, ARSIP = "kiri.bin", "kanan.bin", "identitas_utuh.zip"


def gabung(pa, pb):
    a, b = open(pa, "rb").read(), open(pb, "rb").read()
    if len(a) != len(b):
        sys.exit(f"[-] panjang beda ({len(a)} vs {len(b)}) - bukan pasangan XOR")
    return bytes(i ^ j for i, j in zip(a, b))


def main():
    pesan = gabung(KIRI, KANAN)
    print(f"[+] {KIRI} ^ {KANAN} = {pesan!r}")

    # Verifikasi: XOR dua blob acak nyaris mustahil menghasilkan ASCII penuh.
    # Peluang 10 byte acak semuanya printable ~ (95/256)^10 = 1 : 30.000.
    printable = sum(32 <= c < 127 for c in pesan)
    print(f"[+] byte printable: {printable}/{len(pesan)}")
    if printable != len(pesan):
        sys.exit("[-] hasil bukan teks bersih - operasi/pasangan salah")

    kunci = pesan.decode()
    print(f"[+] kunci     = {kunci}")
    print(f"[+] FLAG      = TechtonicExpoCTF{{{kunci}_66394FFC}}")

    # Konfirmasi kedua: pesan yang sama juga membuka arsip lanjutannya.
    try:
        with zipfile.ZipFile(ARSIP) as z:
            z.setpassword(kunci.encode())
            isi = z.namelist()
            z.read(isi[0])                      # lempar RuntimeError kalau salah
        print(f"[+] {ARSIP} terbuka dengan kunci yang sama: {', '.join(isi)}")
    except FileNotFoundError:
        print(f"[!] {ARSIP} tidak ada - lewati verifikasi arsip")
    except RuntimeError:
        print(f"[-] {ARSIP} menolak kunci - kunci mungkin salah")


if __name__ == "__main__":
    main()
