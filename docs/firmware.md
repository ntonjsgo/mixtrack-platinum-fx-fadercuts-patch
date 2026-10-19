# Firmware 1.10 — struttura

File: `NKCH_ICYH108C02_Y1-10_C903.bin`, 256 KB, SHA-256 `691c612d…f747ffb26`, identico in Windows e Mac.

## Microcontrollore

STM32F4 (Cortex‑M4F), dedotto da: controller della flash a `0x40023C00` con chiave `0x45670123`,
cancellazione per settori in stile Standard Peripheral Library (`FLASH_COMPLETE = 9`),
abilitazione FPU in `CPACR`, timer TIM9 a `0x40014000`, DMA1/DMA2 a `0x40026000/0x40026400`.

## Layout della flash

| Zona | Indirizzi | Contenuto |
|------|-----------|-----------|
| Bootloader | `0x08000000`–`0x08004327` (settori 0–1) | vector table SP `0x20006F68`, reset `0x08003D09`; versione bootloader al byte `0x08003FFF` (= 6); le routine di scrittura flash stanno nel settore 1 |
| Vuoto | `0x08004328`–`0x0800BFFF` | tutto a zero nel file (il settore 2 viene comunque cancellato da `C1`) |
| Applicazione | `0x0800C000`–`0x0803FFFF` | vector table SP `0x20013CD0`, reset `0x0801F865` |
| Coda | `0x0803FFEE` | marcatore `55 AA` (immagine valida) |
| | `0x0803FFF4` | byte di versione applicazione (`0x1A`), restituito dal comando `C4` |
| | `0x0803FFFE` | somma a 16 bit **big-endian** dei byte `0x00000`–`0x3FFFD` |

Le stringhe dei descrittori USB ("MixTrack Platinum FX", "Numark", "Audio Interface",
"Audio Config", "From PC", "To PC", anche "Akai Stage 88 MIDI-2") sono presenti in entrambe le immagini.

## Bootloader

`FUN_0800399C` (main del bootloader):

1. attende ~0,5 s;
2. se due bit di ingresso (i due CUE, dedotto) sono a 1 **e** il byte a `0x0803FFEF` vale `0xAA`,
   disattiva SPI1/SPI3 e i DMA e salta all'applicazione a `0x0800C000`;
3. altrimenti resta in modalità aggiornamento USB.

Comandi (`FUN_08002B38`), pacchetti da 32 byte `55 4F 01 <cmd> …`:

| Cmd | Azione |
|-----|--------|
| `C1` | cancella i settori 2–5 (`0x08008000`–`0x0803FFFF`), azzera i puntatori; base di scrittura `0xC000` |
| `C2` | verifica la somma a 16 bit dei 16 byte dati (offset 9–24) con quella a offset 30–31; offset file a 24 bit in 4–6. Offset < `0xC000`: i primi 16 KB vengono copiati in un buffer RAM, il resto ignorato; da `0xC000` in poi scrive 16 byte in flash in sequenza |
| `C4` | restituisce il byte di versione a `0x0803FFF4` |
| `C3` | confronta la versione del bootloader nel file (byte `0x3FFF` del buffer) con quella installata: se è maggiore, cancella e riscrive il settore 0 dal buffer RAM (autoaggiornamento del bootloader, solo i primi 16 KB); poi riavvia |

Risposte: `55 49 01 <cmd | 0x30>` se OK, `<cmd | 0x20>` se errore.

Nota: l'autoaggiornamento del bootloader è l'unico passaggio davvero rischioso (un'interruzione
durante la riscrittura del settore 0 potrebbe rendere il controller irrecuperabile). Con la patch di
questa repo non avviene, perché il byte di versione del bootloader resta 6.

## Dati iniziali della RAM (compressi)

L'applicazione è compilata con ARM Compiler: lo scatter-load (`FUN_0801F764`) legge una tabella a
`0x0801F7B0` con puntatori relativi:

1. azzeramento di `0x10DBC` byte da `0x20000F10` (`FUN_08010C12`);
2. decompressione LZ (`FUN_0801F65C`) da `0x0801FA2C` (0x6C7 byte compressi) verso `0x20000000`
   (0xF10 byte).

`tools/decompress_rw.py` reimplementa il decompressore; il risultato contiene le tabelle MIDI
(note dei pad, numeri di CC, inversioni) descritte in `controlli-analogici.md` e `fader-cuts.md`.
