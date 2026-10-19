"""Extracts the original 1.10 firmware (.bin) from Numark's macOS updater DMG, without mounting it.

Usage: python extract_from_dmg.py "MixTrack Platinum FX Firmware Updater_For Firmware 1.10.dmg" out.bin

The DMG is decompressed in memory (see udif.py), then the firmware is located by its ARM vector table
and accepted only if its SHA-256 matches the official 1.10 image.
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from udif import decompress_udif  # noqa: E402

FW_SHA256 = "691c612d34fd4c3e275e52fd4735276f52a64fe6d5c4809cf58bac3b747ffb26"
FW_SIZE = 0x40000
FW_HEADER = bytes.fromhex("686f0020093d0008")  # initial SP 0x20006F68, reset 0x08003D09


def main():
    src, dst = sys.argv[1], sys.argv[2]
    img = decompress_udif(open(src, "rb").read())
    pos = img.find(FW_HEADER)
    while pos != -1:
        cand = img[pos:pos + FW_SIZE]
        if hashlib.sha256(cand).hexdigest() == FW_SHA256:
            open(dst, "wb").write(cand)
            print(f"firmware 1.10 found at image offset {pos:#x}, written to {dst}")
            return
        pos = img.find(FW_HEADER, pos + 1)
    sys.exit("official 1.10 firmware not found in this DMG")


if __name__ == "__main__":
    main()
