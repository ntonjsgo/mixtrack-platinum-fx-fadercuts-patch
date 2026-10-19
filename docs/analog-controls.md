# Mixtrack Platinum FX fw 1.10 — analog controls

Source: RW tables decompressed from `0x0801FA2C` (see `tools/decompress_rw.py`) plus functions
`FUN_0800EBC0` / `FUN_0800EAFC` / `FUN_0800E970` / `FUN_0800F2A4` / `FUN_0801021C`.

- CC number table (1 byte per index): RAM `0x20000CEC` = offset `0xCEC` in the output of `decompress_rw.py`
- Invert table (1 = value inverted): RAM `0x20000EE4` = offset `0xEE4` in the output of `decompress_rw.py`
- Status byte: `0xB0` + channel. "Left/right deck" = channel of the active deck (Deck Layer 1/3 and 2/4).
- Pickup = soft takeover (`FUN_0801021C`): after a deck switch the control sends nothing until its
  physical position "catches" the last value stored for that deck.

| Index | Channel   | CC (hex/dec) | Bits | Inverted | Pickup | Control (inferred from the CC) |
|------:|-----------|--------------|------|----------|--------|--------------------------------|
| 0x00  | left deck | 0x17 / 23    | 7    | no       | yes    | Left EQ high                   |
| 0x01  | left deck | 0x18 / 24    | 7    | no       | yes    | Left EQ mid                    |
| 0x02  | left deck | 0x19 / 25    | 7    | no       | yes    | Left EQ low                    |
| 0x03  | left deck | 0x16 / 22    | 7    | no       | yes    | Left gain                      |
| 0x04  | left deck | 0x1C / 28    | 7    | yes      | yes    | Left volume fader              |
| 0x05  | left deck | 0x1A / 26    | 7    | no       | yes    | Left filter                    |
| 0x06  | 0xBF      | 0x08 / 8     | 7    | no       | no     | Crossfader                     |
| 0x0C  | 0xBF      | 0x0C / 12    | 7    | no       | no     | Master / cue (global)          |
| 0x0D  | 0xBF      | 0x0D / 13    | 7    | no       | no     | Master / cue (global)          |
| 0x0E  | 0xBE      | 0x23 / 35    | 7    | no       | no     | Global (cue mix?)              |
| 0x0F  | right deck| 0x1A / 26    | 7    | no       | yes    | Right filter                   |
| 0x10  | right deck| 0x1C / 28    | 7    | yes      | yes    | Right volume fader             |
| 0x11  | left deck | 0x09 + 0x29  | 14   | yes      | no     | Left pitch fader (MSB+LSB)     |
| 0x12  | right deck| 0x16 / 22    | 7    | no       | yes    | Right gain                     |
| 0x13  | right deck| 0x17 / 23    | 7    | no       | yes    | Right EQ high                  |
| 0x14  | 0xB8+0xB9 | 0x04 / 4     | 7    | no       | no     | FX control (sent on 2 channels)|
| 0x15  | right deck| 0x09 + 0x29  | 14   | yes      | no     | Right pitch fader (MSB+LSB)    |
| 0x16  | right deck| 0x19 / 25    | 7    | no       | yes    | Right EQ low                   |
| 0x17  | right deck| 0x18 / 24    | 7    | no       | yes    | Right EQ mid                   |

Indices 0x07–0x0B: CC 0x08 in the table but not sent by `FUN_0800EBC0` (unused / other path).
Control names are inferred from the CC numbers, left/right symmetry and invert flags: confirm them with a MIDI monitor.
