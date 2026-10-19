# Mixtrack Platinum FX fw 1.10 — controlli analogici

Fonte: tabelle RW decompresse da 0x0801FA2C (vedi `tools/decompress_rw.py`) + funzioni
FUN_0800ebc0 / FUN_0800eafc / FUN_0800e970 / FUN_0800f2a4 / FUN_0801021c.

- Tabella numeri CC (1 byte per indice): RAM 0x20000CEC = offset 0xCEC nell'output di decompress_rw.py
- Tabella inversione (1 = valore invertito): RAM 0x20000EE4 = offset 0xEE4 nell'output di decompress_rw.py
- Stato: 0xB0 + canale. "Deck sx/dx" = canale del deck attivo (Deck Layer 1/3 e 2/4).
- Pickup = soft takeover (FUN_0801021c): dopo il cambio deck il controllo non invia finche'
  la posizione fisica non "aggancia" l'ultimo valore memorizzato per quel deck.

| Indice | Canale   | CC (hex/dec) | Bit | Invertito | Pickup | Controllo (dedotto dal CC) |
|-------:|----------|--------------|-----|-----------|--------|----------------------------|
| 0x00   | deck sx  | 0x17 / 23    | 7   | no        | si     | EQ alti sx                 |
| 0x01   | deck sx  | 0x18 / 24    | 7   | no        | si     | EQ medi sx                 |
| 0x02   | deck sx  | 0x19 / 25    | 7   | no        | si     | EQ bassi sx                |
| 0x03   | deck sx  | 0x16 / 22    | 7   | no        | si     | Gain sx                    |
| 0x04   | deck sx  | 0x1C / 28    | 7   | si        | si     | Fader volume sx            |
| 0x05   | deck sx  | 0x1A / 26    | 7   | no        | si     | Filtro sx                  |
| 0x06   | 0xBF     | 0x08 / 8     | 7   | no        | no     | Crossfader                 |
| 0x0C   | 0xBF     | 0x0C / 12    | 7   | no        | no     | Master / cue (globale)     |
| 0x0D   | 0xBF     | 0x0D / 13    | 7   | no        | no     | Master / cue (globale)     |
| 0x0E   | 0xBE     | 0x23 / 35    | 7   | no        | no     | Globale (cue mix?)         |
| 0x0F   | deck dx  | 0x1A / 26    | 7   | no        | si     | Filtro dx                  |
| 0x10   | deck dx  | 0x1C / 28    | 7   | si        | si     | Fader volume dx            |
| 0x11   | deck sx  | 0x09 + 0x29  | 14  | si        | no     | Pitch fader sx (MSB+LSB)   |
| 0x12   | deck dx  | 0x16 / 22    | 7   | no        | si     | Gain dx                    |
| 0x13   | deck dx  | 0x17 / 23    | 7   | no        | si     | EQ alti dx                 |
| 0x14   | 0xB8+0xB9| 0x04 / 4     | 7   | no        | no     | Controllo FX (inviato su 2 canali) |
| 0x15   | deck dx  | 0x09 + 0x29  | 14  | si        | no     | Pitch fader dx (MSB+LSB)   |
| 0x16   | deck dx  | 0x19 / 25    | 7   | no        | si     | EQ bassi dx                |
| 0x17   | deck dx  | 0x18 / 24    | 7   | no        | si     | EQ medi dx                 |

Indici 0x07-0x0B: CC 0x08 in tabella ma non inviati da FUN_0800ebc0 (non usati / altro percorso).
I nomi dei controlli sono dedotti da CC, simmetria sx/dx e flag di inversione: confermarli con un monitor MIDI.
