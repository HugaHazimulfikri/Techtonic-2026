#!/usr/bin/env python3
"""Bongkar filter seccomp BPF milik kurungan.bin (43 instruksi di .rodata:0x2020)."""
import struct

SYS = {0:"read",1:"write",2:"open",3:"close",9:"mmap",10:"mprotect",11:"munmap",12:"brk",
 16:"ioctl",59:"execve",60:"exit",157:"prctl",158:"arch_prctl",202:"futex",218:"set_tid_address",
 231:"exit_group",257:"openat",273:"set_robust_list",334:"rseq",
 425:"io_uring_setup",426:"io_uring_enter",427:"io_uring_register"}
RET = {0x00000000:"KILL_THREAD", 0x7fff0000:"ALLOW"}

data = open("kurungan.bin","rb").read()[0x2020:0x2020+43*8]
izin = []
print(f"{'#':>3} {'code':>6} {'jt':>3} {'jf':>3} {'k':>12}   arti")
for i in range(43):
    code, jt, jf, k = struct.unpack("<HBBI", data[i*8:(i+1)*8])
    if   code == 0x20 and k == 4: s = "A = nomor syscall"
    elif code == 0x20 and k == 0: s = "A = arch"
    elif code == 0x15:
        nm = SYS.get(k, str(k)); s = f"if A == {k} ({nm}) -> +{jt} else +{jf}"
        if jf == 1: izin.append(nm)
    elif code == 0x06: s = "RET " + RET.get(k, hex(k))
    else: s = f"code={hex(code)} k={hex(k)}"
    print(f"{i:3} {hex(code):>6} {jt:3} {jf:3} {hex(k):>12}   {s}")

print("\nSYSCALL DIIZINKAN:", ", ".join(izin))
print("open / openat / execve TIDAK ADA -> jalan keluarnya io_uring")
