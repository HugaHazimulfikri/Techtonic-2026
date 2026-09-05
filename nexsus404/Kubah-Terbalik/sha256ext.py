"""SHA-256 dengan state yang bisa di-set -> untuk length extension attack."""
import struct, hashlib

K = [
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2]

M = 0xffffffff
def _r(x, n): return ((x >> n) | (x << (32 - n))) & M

def compress(st, blk):
    w = list(struct.unpack(">16I", blk))
    for i in range(16, 64):
        s0 = _r(w[i-15],7) ^ _r(w[i-15],18) ^ (w[i-15] >> 3)
        s1 = _r(w[i-2],17) ^ _r(w[i-2],19) ^ (w[i-2] >> 10)
        w.append((w[i-16] + s0 + w[i-7] + s1) & M)
    a,b,c,d,e,f,g,h = st
    for i in range(64):
        t1 = (h + (_r(e,6)^_r(e,11)^_r(e,25)) + ((e&f)^(~e & g)) + K[i] + w[i]) & M
        t2 = ((_r(a,2)^_r(a,13)^_r(a,22)) + ((a&b)^(a&c)^(b&c))) & M
        h,g,f,e,d,c,b,a = g,f,e,(d+t1)&M,c,b,a,(t1+t2)&M
    return [(x+y)&M for x,y in zip(st,(a,b,c,d,e,f,g,h))]

def md_pad(n):
    """padding Merkle-Damgard untuk pesan sepanjang n byte"""
    return b"\x80" + b"\x00" * ((55 - n) % 64) + struct.pack(">Q", n * 8)

def sha256(msg, state=None, prelen=0):
    st = list(struct.unpack(">8I", state)) if state else [
        0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]
    data = msg + md_pad(prelen + len(msg))
    for i in range(0, len(data), 64):
        st = compress(st, data[i:i+64])
    return struct.pack(">8I", *st)

if __name__ == "__main__":
    # self-test: harus sama persis dengan hashlib
    for t in [b"", b"abc", b"halaman=utama", b"x"*200]:
        assert sha256(t).hex() == hashlib.sha256(t).hexdigest(), t
    print("[+] self-test SHA-256 LULUS (cocok dengan hashlib)")
