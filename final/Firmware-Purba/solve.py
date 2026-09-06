#!/usr/bin/env python3
"""Firmware Purba - temukan kunci yang ditanam di dalam 1 MB data acak.

Strategi dua tahap:
  1. Peta entropi per blok 256-byte -> mempersempit 1 MB jadi satu alamat.
     (mengarahkan saja: selisihnya tipis, 6.928 vs rata-rata 7.176)
  2. Regex teks manusia -> membuktikan.
     [ -~] mencakup 95/256 nilai byte  -> 1.714 false positive.
     [a-z_ ] cuma 28/256               -> peluang 7 byte acak lolos ~1:800 juta.
"""
import collections, math, re, sys

BERKAS = sys.argv[1] if len(sys.argv) > 1 else "firmware_purba.bin"
BLOK = 256


def peta_entropi(d, n=5):
    """Entropi Shannon tiap blok; kembalikan n blok paling tidak acak."""
    skor = []
    for i in range(0, len(d) - BLOK + 1, BLOK):
        c = collections.Counter(d[i:i + BLOK])
        H = -sum(v / BLOK * math.log2(v / BLOK) for v in c.values())
        skor.append((H, i))
    skor.sort()
    return skor[:n], sum(H for H, _ in skor) / len(skor), len(skor)


def cari_teks(d):
    """Rentetan yang berpola teks manusia, bukan sekadar printable."""
    return [(m.start(), m.group().decode()) for m in re.finditer(rb"[a-z_ ]{7,}", d)]


def main():
    d = open(BERKAS, "rb").read()
    print(f"[+] {BERKAS}: {len(d)} byte ({hex(len(d))})")
    print(f"[+] kelebihan di luar 1 MiB: {d[0x100000:].hex()}")

    atas, rata, total = peta_entropi(d)
    print(f"\n[+] entropi {total} blok {BLOK}-byte (rata-rata {rata:.3f}):")
    for H, i in atas:
        tanda = "  <- titik tengah 1 MiB" if i == len(d) // 2 // BLOK * BLOK else ""
        print(f"      {i:#09x}  H={H:.3f}{tanda}")

    bising = len(re.findall(rb"[ -~]{6,}", d))
    temuan = cari_teks(d)
    print(f"\n[+] rentetan printable [ -~]{{6,}} : {bising}   <- terlalu bising")
    print(f"[+] setelah filter  [a-z_ ]{{7,}} : {len(temuan)}")
    for off, s in temuan:
        print(f"      {off:#09x}  {s!r}")

    if not temuan:
        sys.exit("[-] tidak ada teks ditemukan")

    kunci = temuan[0][1]
    print(f"\n[+] kunci = {kunci}")
    print(f"[+] FLAG  = TechtonicExpoCTF{{{kunci}_66394FFC}}")

    # Penanda di dekatnya yang mengonfirmasi ini memang sisipan sengaja,
    # bukan ASCII kebetulan: teksnya mengulang kalimat soal.
    if any("tidak pernah dipetakan" in s for _, s in temuan):
        print("[+] terkonfirmasi: ada penanda 'blok cadangan tidak pernah dipetakan'")


if __name__ == "__main__":
    main()
