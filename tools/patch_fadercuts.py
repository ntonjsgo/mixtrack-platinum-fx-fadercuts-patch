"""Patches Mixtrack Platinum FX fw 1.10 so Fader Cuts pads send only their notes (no simulated crossfader).

Each patched function gets `bx lr` (0x4770) at its entry, and the big-endian 16-bit sum in the last two bytes is recomputed.
"""
import struct, sys, hashlib

BASE = 0x08000000
ORIG_SHA256 = "691c612d34fd4c3e275e52fd4735276f52a64fe6d5c4809cf58bac3b747ffb26"
PATCHES = {
    0x08018AD2: "start of the Fader Cuts crossfader sequence",
    0x08018DF2: "stop of the sequence + resend of the real crossfader position",
}
BX_LR = b"\x70\x47"

src, dst = sys.argv[1], sys.argv[2]
fw = bytearray(open(src, "rb").read())
assert hashlib.sha256(fw).hexdigest() == ORIG_SHA256, "not the original 1.10 firmware"
assert len(fw) == 0x40000
assert sum(fw[:-2]) & 0xFFFF == struct.unpack_from(">H", fw, 0x3FFFE)[0], "original checksum mismatch"

for addr, what in PATCHES.items():
    off = addr - BASE
    print(f"{addr:#010x}  {fw[off:off+4].hex(' ')} -> {BX_LR.hex(' ')}  ({what})")
    fw[off:off+2] = BX_LR

assert fw[0x3FFEE:0x3FFF0] == b"\x55\xAA", "app-valid marker missing"
assert fw[0x3FFF] == 6, "bootloader version byte changed"
struct.pack_into(">H", fw, 0x3FFFE, sum(fw[:-2]) & 0xFFFF)
open(dst, "wb").write(fw)
print("new checksum", fw[0x3FFFE:].hex(" "), "sha256", hashlib.sha256(fw).hexdigest())
print("bytes changed:", sum(1 for a, b in zip(open(src, "rb").read(), fw) if a != b))
