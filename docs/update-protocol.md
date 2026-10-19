# Updater protocol (USB HID)

Reconstructed by decompiling the Windows updater (`MixTrack Platinum FX Firmware Updater.exe`
1.0.0.26078, class `LMixTrackHIDEngine`).

## Transport

- The device is found with `SetupDi*` and opened with `CreateFileW`.
- Every message is a **65-byte** HID report (Report ID 0 + 64 bytes) written with `WriteFile` and read
  with `ReadFile` in overlapped mode, 5 s timeout (`0x004095B0` send, `0x004096F0` send + reply).
- `HidD_SetOutputReport` and `HidD_GetAttributes` are loaded from `hid.dll` but never called.

## Two protocols in the binary

| | Binary file (`fopen "rb"`), `0x004035F0` | Text file (`fopen "r"`), `0x00407EF0` |
|---|---|---|
| Packet | `55 4F 01 <cmd>` | `01 <cmd> … <CRC> 17` |
| Commands | `C1` start, `C2` 16 data bytes, `C4` status/version (reply `F4`), `C3` finish | `38` version, `32` memory bounds, `37`/`39` data, `3A` close block, `3B` reboot |
| Check | 16-bit sum over the 16 bytes | CRC-16/X-25 (poly `0x8408`) or two's-complement sum |
| Data per packet | 16 | 53 |

The Mixtrack Platinum FX uses the first one (the `.bin` is opened with `"rb"`). The second one is
probably code shared with other inMusic products.

### Sequence for the `.bin`

1. `C1`
2. for every 16-byte block of the file: `C2` with offset (24 bits), data and sum
3. `C4` (reads the version), `C3` (finish and reboot)

`C2` packet (32 bytes):

```
00: 55 4F 01 C2
04: offset[23:16] offset[15:8] offset[7:0]
09..24: 16 data bytes
30..31: 16-bit sum (big-endian) of bytes 9..24
```

## Updater command-line options

`-ABSOLUTE_FIRMWARE_FILE_PATH=`, `-FIRMWARE_IMAGE_NAME=`, `-DEVICE_BOOTLOADER_PID=`, `-ALWAYS_UPDATE`,
`-START_UPDATE_AUTOMATICALLY`, `-SILENT_IF_UPDATE_NOT_NEEDED`, `-RETURN_UPDATE_MODE_STATUS`.
The same strings are present in the macOS updater (`FirmwareUpdater`, x86_64 only).

## Integrity

No cryptographic signature: only the per-block sum on the transport side, the `55 AA` marker and the
global sum at the end of the image (nothing was observed verifying the latter).
