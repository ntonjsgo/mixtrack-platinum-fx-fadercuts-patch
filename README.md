# Mixtrack Platinum FX — "Fader Cuts → plain MIDI pads" patch

Unofficial patch for the **Numark Mixtrack Platinum FX** DJ controller, firmware **1.10**.
In **Fader Cuts** pad mode it makes the 8 pads of each deck send **only their MIDI notes**
(Note On/Off), instead of generating automatic crossfader movements inside the controller.

## The problem

With the stock firmware, when the pads are in **Fader Cuts** mode, pressing a pad does more than send
a note: the controller starts a **timed sequence** (one of 8, one per pad) that sends crossfader
`CC 8` messages to the computer, emulating crossfader cuts. On release it re-sends the real
crossfader position.

If you use the controller with software other than the one it was designed for (Mixxx, a DAW,
VJ software, custom MIDI mappings…) this gets in the way: in that mode the 8 pads are **no longer
plain MIDI buttons**, and every press moves the crossfader in your software even when you want to
use the pads for something else.

## The fix

The patch disables the crossfader sequence engine and leaves everything else untouched:

| Address      | Original function                                          | Patch   |
|--------------|------------------------------------------------------------|---------|
| `0x08018AD2` | starts the pad's crossfader sequence (Fader Cuts)          | `bx lr` |
| `0x08018DF2` | stops the sequence and re-sends the crossfader position    | `bx lr` |

Plus the recomputed 16-bit checksum at the end of the image: **4 bytes** change in total.
Both functions are called only by the pad handler, so nothing else is affected:

- in Fader Cuts the pads send **Note On/Off**: notes **20–27** (28–35 with SHIFT) on the deck's pad channel;
- all other pad modes, faders, knobs and the physical crossfader work as before;
- the **bootloader is not touched**: you can always go back to the original firmware.

Tested on a real controller with the official Windows updater.

## What is NOT in this repo

Firmware, updater and decompiled code belong to inMusic/Numark and are **not redistributed**.
This repo only contains scripts and documentation: you extract the original `.bin` from the official
updater downloaded from Numark's website, and the script patches it on your own machine.

## Usage

### 1. Get the original 1.10 firmware

Download "Mixtrack Platinum FX Firmware 1.10" (Windows or Mac) from Numark's website, then use one of these:

- **Windows, installing the updater:** after installation the file is at
  `C:\Program Files (x86)\Numark\MixTrack Platinum FX Firmware Updater\NKCH_ICYH108C02_Y1-10_C903.bin`
- **Windows, without installing anything:**
  ```powershell
  .\tools\extract_from_windows_installer.ps1 -Installer "Install MixTrack Platinum FX Firmware Updater For Firmware 1.10.exe" -Out NKCH_ICYH108C02_Y1-10_C903.bin
  ```
- **From the Mac DMG** (works on any system with Python 3):
  ```bash
  python3 tools/extract_from_dmg.py "MixTrack Platinum FX Firmware Updater_For Firmware 1.10.dmg" NKCH_ICYH108C02_Y1-10_C903.bin
  ```

The firmware is identical in the Windows and Mac packages
(SHA-256 `691c612d34fd4c3e275e52fd4735276f52a64fe6d5c4809cf58bac3b747ffb26`).

### 2. Apply the patch

```bash
python3 tools/patch_fadercuts.py NKCH_ICYH108C02_Y1-10_C903.bin NKCH_ICYH108C02_Y1-10_C903_nofadercuts.bin
```

The script rejects any file that is not the original 1.10 image and checks the checksum, the
validity marker and the bootloader version before writing.
Expected SHA-256 of the result: `7a90f823f25f8246576f9fcc8764e18794b2c762a48eb04ac82eabb05cc0d439`.

### 3. Flash it

1. Put the controller in update mode: **hold both CUE buttons** in the center while plugging in the USB cable.
2. Run the official updater pointing at the patched file. Since the version is the same (1.10), `-ALWAYS_UPDATE` is needed.

**Windows (PowerShell):**
```powershell
& "C:\Program Files (x86)\Numark\MixTrack Platinum FX Firmware Updater\MixTrack Platinum FX Firmware Updater.exe" -ABSOLUTE_FIRMWARE_FILE_PATH=C:\path\to\NKCH_ICYH108C02_Y1-10_C903_nofadercuts.bin -ALWAYS_UPDATE
```

**macOS (Terminal)** — don't replace the `.bin` inside the app (that breaks its code signature); pass it from outside.
The updater is Intel-only: Apple Silicon Macs need Rosetta.
```bash
"/Applications/MixTrack Platinum FX Firmware Updater.app/Contents/MacOS/FirmwareUpdater" -ABSOLUTE_FIRMWARE_FILE_PATH="$HOME/Downloads/NKCH_ICYH108C02_Y1-10_C903_nofadercuts.bin" -ALWAYS_UPDATE
```

The change lives in the controller: once flashed, it works with any computer.

### Going back to the original

Enter update mode again (both CUEs + USB) and flash the original `.bin` with the same command,
or just run the official updater normally.

## ⚠️ Warnings

- **Unofficial** firmware: use at your own risk. Not affiliated with inMusic/Numark.
- The bootloader stays intact and only boots the application when the image is complete (the `55 AA`
  marker is written at the end), so an interrupted update can be recovered by entering update mode
  again. This is inferred from the bootloader code, not from destructive testing.
- Only for firmware **1.10** (`NKCH_ICYH108C02_Y1-10_C903.bin`).

## Technical documentation

Everything reconstructed during the analysis:

- [`docs/fader-cuts.md`](docs/fader-cuts.md) — how Fader Cuts works in the firmware and why the patch is safe
- [`docs/firmware.md`](docs/firmware.md) — flash layout, bootloader, markers, checksum, compressed data
- [`docs/update-protocol.md`](docs/update-protocol.md) — USB HID protocol used by the updater
- [`docs/analog-controls.md`](docs/analog-controls.md) — channel/CC map of faders and knobs, soft takeover

## Tools

| File | Purpose |
|------|---------|
| `tools/patch_fadercuts.py` | applies the patch to the original `.bin` |
| `tools/extract_from_windows_installer.ps1` | extracts the `.bin` from the Windows installer without installing it |
| `tools/extract_from_dmg.py`, `tools/udif.py` | extract the `.bin` from the Mac DMG without mounting it |
| `tools/decompress_rw.py` | decompresses the firmware's initial RAM data (MIDI tables) |
| `tools/ghidra/analyze_firmware.sh` + `DumpFw.java` | decompiles the whole firmware with headless Ghidra |
| `tools/ghidra/decompile_at.sh` + `DisAt.java` | decompiles specific functions (e.g. to verify the patch) |

The Ghidra scripts need Ghidra 12.1 and JDK 21 (`GHIDRA_INSTALL_DIR` set).

## License

Scripts and documentation: [MIT](LICENSE). Numark firmware and software remain the property of their respective owners.
