"""Re-implements the firmware's scatter-load LZ decompressor (0x0801F65C) and writes the initial RW RAM image."""
import struct, sys

BASE = 0x08000000
fw = open(sys.argv[1], 'rb').read()
out_path = sys.argv[2]

def rd(a):
    return struct.unpack_from('<I', fw, a - BASE)[0]

args = 0x0801F7C4                      # second scatter-table entry, after its handler offset
src = args + rd(args)                  # 0x0801FA2C
end = src + (rd(args + 4) >> 1)
dst = rd(args + 8)                     # 0x20000000

out = bytearray()
p = src
while p != end:
    tok = fw[p - BASE]; p += 1
    lit = tok & 3
    if lit == 0:
        lit = fw[p - BASE] + 3; p += 1
    mlen = tok >> 4
    if mlen == 0xF:
        mlen = fw[p - BASE] + 0xF; p += 1
    for _ in range(lit - 1):
        out.append(fw[p - BASE]); p += 1
    if mlen:
        off = fw[p - BASE]; p += 1
        hi = (tok >> 2) & 3
        if hi == 3:
            hi = fw[p - BASE]; p += 1
        back = len(out) - (off + (hi << 8))
        for i in range(mlen + 2):
            out.append(out[back + i])
open(out_path, 'wb').write(out)
print(f"src={src:#x} end={end:#x} dst={dst:#x} decompressed={len(out):#x} bytes")
