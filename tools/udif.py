"""Decompresses an Apple UDIF (.dmg) image into a raw disk image (zlib, bzip2, raw and zero chunks).

Usage: python udif.py image.dmg raw.img
"""
import bz2
import plistlib
import struct
import sys
import zlib


def decompress_udif(d):
    k = d[-512:]
    if k[:4] != b"koly":
        raise ValueError("not a UDIF image (missing koly trailer)")
    xo, xl = struct.unpack(">QQ", k[0xD8:0xE8])
    pl = plistlib.loads(d[xo:xo + xl])
    out = bytearray()
    for blk in pl["resource-fork"]["blkx"]:
        m = blk["Data"]
        if m[:4] != b"mish":
            raise ValueError("unexpected blkx entry")
        sec0 = struct.unpack(">Q", m[8:16])[0]
        n = struct.unpack(">I", m[0xC8:0xCC])[0]
        for i in range(n):
            t, _, ss, sc, co, cl = struct.unpack(">IIQQQQ", m[0xCC + 40 * i:0xCC + 40 * i + 40])
            if t == 0xFFFFFFFF:
                break
            if t == 0x7FFFFFFE:
                continue
            off = (sec0 + ss) * 512
            if len(out) < off + sc * 512:
                out.extend(b"\0" * (off + sc * 512 - len(out)))
            c = d[co:co + cl]
            if t in (0, 2):
                data = b"\0" * (sc * 512)
            elif t == 1:
                data = c
            elif t == 0x80000005:
                data = zlib.decompress(c)
            elif t == 0x80000006:
                data = bz2.decompress(c)
            else:
                raise ValueError(f"unsupported chunk type {t:#x} (e.g. LZFSE/ADC)")
            out[off:off + len(data)] = data
    return bytes(out)


if __name__ == "__main__":
    raw = decompress_udif(open(sys.argv[1], "rb").read())
    open(sys.argv[2], "wb").write(raw)
    print(f"raw image: {len(raw)} bytes")
