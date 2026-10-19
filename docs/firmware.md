# Firmware 1.10 — structure

File: `NKCH_ICYH108C02_Y1-10_C903.bin`, 256 KB, SHA-256 `691c612d…f747ffb26`, identical on Windows and Mac.

## Microcontroller

STM32F4 (Cortex-M4F), inferred from: flash controller at `0x40023C00` with key `0x45670123`,
sector erase in Standard Peripheral Library style (`FLASH_COMPLETE = 9`), FPU enabled in `CPACR`,
TIM9 at `0x40014000`, DMA1/DMA2 at `0x40026000/0x40026400`.

## Flash layout

| Region | Addresses | Contents |
|--------|-----------|----------|
| Bootloader | `0x08000000`–`0x08004327` (sectors 0–1) | vector table SP `0x20006F68`, reset `0x08003D09`; bootloader version at byte `0x08003FFF` (= 6); the flash write routines live in sector 1 |
| Empty | `0x08004328`–`0x0800BFFF` | all zeros in the file (sector 2 is still erased by `C1`) |
| Application | `0x0800C000`–`0x0803FFFF` | vector table SP `0x20013CD0`, reset `0x0801F865` |
| Tail | `0x0803FFEE` | `55 AA` marker (valid image) |
| | `0x0803FFF4` | application version byte (`0x1A`), returned by command `C4` |
| | `0x0803FFFE` | **big-endian** 16-bit sum of bytes `0x00000`–`0x3FFFD` |

The USB descriptor strings ("MixTrack Platinum FX", "Numark", "Audio Interface", "Audio Config",
"From PC", "To PC", and also "Akai Stage 88 MIDI-2") appear in both images.

## Bootloader

`FUN_0800399C` (bootloader main):

1. waits ~0.5 s;
2. if two input bits (the two CUE buttons, inferred) read 1 **and** the byte at `0x0803FFEF` is `0xAA`,
   it shuts down SPI1/SPI3 and the DMAs and jumps to the application at `0x0800C000`;
3. otherwise it stays in USB update mode.

Commands (`FUN_08002B38`), 32-byte packets `55 4F 01 <cmd> …`:

| Cmd | Action |
|-----|--------|
| `C1` | erases sectors 2–5 (`0x08008000`–`0x0803FFFF`) and resets the pointers; write base `0xC000` |
| `C2` | checks the 16-bit sum of the 16 data bytes (offsets 9–24) against the one at offsets 30–31; 24-bit file offset in 4–6. Offsets < `0xC000`: the first 16 KB are copied into a RAM buffer, the rest is ignored; from `0xC000` on it writes 16 bytes to flash sequentially |
| `C4` | returns the version byte at `0x0803FFF4` |
| `C3` | compares the bootloader version in the file (byte `0x3FFF` of the buffer) with the installed one: if higher, it erases and rewrites sector 0 from the RAM buffer (bootloader self-update, first 16 KB only); then it reboots |

Replies: `55 49 01 <cmd | 0x30>` on success, `<cmd | 0x20>` on error.

Note: the bootloader self-update is the only really risky step (an interruption while sector 0 is
being rewritten could leave the controller unrecoverable). It does not happen with the patch in this
repo, because the bootloader version byte stays 6.

## Initial RAM data (compressed)

The application is built with ARM Compiler: the scatter-load routine (`FUN_0801F764`) reads a table
at `0x0801F7B0` with relative pointers:

1. zero-fill of `0x10DBC` bytes from `0x20000F10` (`FUN_08010C12`);
2. LZ decompression (`FUN_0801F65C`) from `0x0801FA2C` (0x6C7 compressed bytes) to `0x20000000`
   (0xF10 bytes).

`tools/decompress_rw.py` reimplements the decompressor; the output contains the MIDI tables
(pad notes, CC numbers, inversions) described in `analog-controls.md` and `fader-cuts.md`.
