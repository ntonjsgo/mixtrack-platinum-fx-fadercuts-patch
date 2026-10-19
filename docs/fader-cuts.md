# Fader Cuts in firmware 1.10

Addresses refer to the image loaded at `0x08000000` (application from `0x0800C000`).
`FUN_xxxxxxxx` names = functions without symbols, as Ghidra shows them.

## Pad handler — `FUN_0800DD24`

For each pad (index 0–7):

- **press** → `FUN_0800D9A0` writes a *Note On* into the USB-MIDI buffer:
  `[CIN 0x9, 0x90 | (deck + 4), note, 0x7F]`.
  The note comes from a RAM table (`0x20000C6C` without SHIFT, `0x20000CAC` with SHIFT):
  pads 1–8 → notes `0x14–0x1B` (20–27), with SHIFT `0x1C–0x23` (28–35).
  Then, **if the deck's pad mode is 2 (Fader Cuts)**, it calls `FUN_08018AD2(deck, pad)`.
- **release** → `FUN_0800D91C` sends the matching *Note Off* and, in Fader Cuts,
  calls `FUN_08018DF2(deck)`.

For pads 5–8 the Fader Cuts call also depends on a flag (`0x20011CA5`).

## The sequence engine

- `FUN_08018AD2(deck, pad)` loads one of the 8 patterns into the deck's structure (pointed to by
  `DAT_08018FD4`, 32 bytes per deck), computes its duration from the tempo (`FUN_080189C6`) and
  resets the counter.
- `FUN_0800F192` → `FUN_08018E46(deck)` runs periodically for both decks: when the sequence is
  active it advances one step (`FUN_08018A0E`) and on every step calls `FUN_0800F140(deck, value)`,
  which sends `CC 8` (crossfader) on channel `0xBF` (or on the deck's channel) with the pattern value.
- `FUN_08018DF2(deck)` clears the structure and calls `FUN_0800EBC0(6)`, which re-sends the
  **real** crossfader position (analog control 6, `0xBF CC 8`).

`FUN_08018AD2`, `FUN_08018DF2` and `FUN_08018F80` ("running" state) are called **only** from
`FUN_0800DD24`.

## The patch

```
0x08018AD2:  70 B5  (push {r4-r6,lr})  ->  70 47  (bx lr)
0x08018DF2:  10 B5  (push {r4,lr})     ->  70 47  (bx lr)
0x0803FFFE:  big-endian 16-bit sum of 0x00000–0x3FFFD recomputed  (C7 9E -> C7 22)
```

With the sequence start disabled, the deck state stays 0: `FUN_08018E46` does nothing and
`FUN_08018F80` always returns "not running". The release no longer re-sends the crossfader.
The pads' Note On/Off messages are generated earlier and independently, so they are unchanged.

Verification: decompiling the patched image with `tools/ghidra/decompile_at.sh` shows both
functions as `void FUN_...(void) { return; }`, and the pad handler keeps all its note-sending calls.
