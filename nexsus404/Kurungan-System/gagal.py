#!/usr/bin/env python3
"""Reproduksi percobaan yang GAGAL (lihat 'Yang gagal' di WRITEUP.md).
Memakai solve.py sebagai pembaca file arbitrer, jadi eksploitnya tidak ditulis ulang."""
import subprocess, sys, re

def probe(path):
    out = subprocess.run([sys.executable, "solve.py", path],
                         capture_output=True, text=True, timeout=60).stdout
    for l in out.splitlines():
        if l.startswith("[4]"):
            return l[4:].strip()
    return "(tidak ada respons)"

print("=== GAGAL 1: menebak path flag yang umum ===")
for p in ("/flag", "/flag.txt", "/app/flag.txt", "/home/ctf/flag", "/srv/flag.txt"):
    print(f"  {probe(p)}")
print("  -> semuanya ENOENT. Bypass io_uring sudah jalan (errno asli kembali,")
print("     prosesnya tidak dibunuh seccomp), cuma nama filenya yang salah.\n")

print("=== GAGAL 2: hint 'hanya baca yang diizinkan' saya baca sebagai fd terbuka ===")
print("  scan ioctl(FIONREAD) fd 0..39 -> cuma fd 0, 1, 2 yang valid")
print("  -> tidak ada fd flag yang sudah terbuka. Hipotesisnya salah;")
print("     'boleh_read' ternyata cuma ISI file rahasia.txt, bukan petunjuk teknik.\n")

print("=== GAGAL 3: /home/pwn EACCES, sempat dikira soalnya rusak ===")
for p in ("/home/x", "/home/tidakada/x", "/home/pwn/x", "/home/pwn/flag.txt"):
    print(f"  {probe(p)}")
print("  -> /home bisa ditelusuri (ENOENT), tapi /home/pwn EACCES.")
print("     Sebabnya uidmap nsjail 0 -> 65534: di dalam jail saya root, di luar nobody.\n")

print("=== ORACLE YANG MEMBANTAH SALAH BACA SAYA (ENOTDIR) ===")
for p in ("/srv/kurungan.bin/x", "/srv/tidakada/x", "/etc/hostname/x"):
    print(f"  {probe(p)}")
print("  -> ENOTDIR membuktikan file itu ADA. Ini yang membantah dugaan saya bahwa")
print("     jail punya /srv berbeda, yang muncul gara-gara output kepotong 'tail'.")
