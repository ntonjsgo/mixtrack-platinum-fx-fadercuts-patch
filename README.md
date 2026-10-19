# Mixtrack Platinum FX — patch "Fader Cuts → pad MIDI semplici"

Patch non ufficiale per il firmware **1.10** del controller DJ **Numark Mixtrack Platinum FX**.
Fa sì che, in modalità pad **Fader Cuts**, gli 8 pad di ogni deck inviino **solo le loro note MIDI**
(Note On/Off), invece di generare dentro il controller dei movimenti automatici del crossfader.

> 🇬🇧 *English summary below.*

## Il problema

Nel firmware originale, quando i pad sono in modalità **Fader Cuts**, premere un pad non si limita a
mandare una nota: il controller avvia una **sequenza a tempo** (una delle 8, una per pad) che invia
messaggi `CC 8` del **crossfader** al computer, simulando i "tagli" di crossfader. Al rilascio rimanda
la posizione reale del crossfader.

Per chi usa il controller con un software diverso da quello previsto (Mixxx, una DAW, software VJ,
mapping MIDI personalizzati…) questo è un problema: in quella modalità gli 8 pad **non sono più dei
semplici pulsanti MIDI**, e ogni pressione muove il crossfader nel software, anche se tu vuoi usarli
per altro.

## La soluzione

La patch disattiva il motore delle sequenze di crossfader lasciando intatto tutto il resto:

| Indirizzo    | Funzione originale                                        | Patch   |
|--------------|-----------------------------------------------------------|---------|
| `0x08018AD2` | avvia la sequenza di crossfader del pad (Fader Cuts)      | `bx lr` |
| `0x08018DF2` | ferma la sequenza e rimanda la posizione del crossfader   | `bx lr` |

Più il ricalcolo della somma di controllo a 16 bit in fondo all'immagine. In tutto cambiano **4 byte**.
Le due funzioni sono chiamate solo dal gestore dei pad, quindi niente altro cambia:

- in Fader Cuts i pad mandano **Note On/Off**: note **20–27** (28–35 con SHIFT) sul canale pad del deck;
- tutte le altre modalità pad, i fader, le manopole e il crossfader fisico funzionano come prima;
- il **bootloader non viene toccato**: si può sempre tornare al firmware originale.

Testata su un controller reale con l'updater ufficiale per Windows.

## Cosa NON c'è in questa repo

Firmware, updater e codice decompilato sono proprietà di inMusic/Numark e **non vengono
ridistribuiti**. La repo contiene solo script e documentazione: il `.bin` originale lo estrai tu
dall'updater ufficiale scaricato dal sito Numark, e lo script lo modifica sul tuo computer.

## Come si usa

### 1. Procurati il firmware originale 1.10

Scarica "Mixtrack Platinum FX Firmware 1.10" (Windows o Mac) dal sito Numark, poi in uno di questi modi:

- **Windows, installando l'updater:** dopo l'installazione il file è in
  `C:\Program Files (x86)\Numark\MixTrack Platinum FX Firmware Updater\NKCH_ICYH108C02_Y1-10_C903.bin`
- **Windows, senza installare nulla:**
  ```powershell
  .\tools\extract_from_windows_installer.ps1 -Installer "Install MixTrack Platinum FX Firmware Updater For Firmware 1.10.exe" -Out NKCH_ICYH108C02_Y1-10_C903.bin
  ```
- **Dal DMG per Mac** (funziona su qualsiasi sistema con Python 3):
  ```bash
  python3 tools/extract_from_dmg.py "MixTrack Platinum FX Firmware Updater_For Firmware 1.10.dmg" NKCH_ICYH108C02_Y1-10_C903.bin
  ```

Il firmware è identico nelle versioni Windows e Mac
(SHA-256 `691c612d34fd4c3e275e52fd4735276f52a64fe6d5c4809cf58bac3b747ffb26`).

### 2. Applica la patch

```bash
python3 tools/patch_fadercuts.py NKCH_ICYH108C02_Y1-10_C903.bin NKCH_ICYH108C02_Y1-10_C903_nofadercuts.bin
```

Lo script rifiuta qualsiasi file che non sia l'originale 1.10 e controlla somma di controllo,
marcatore di validità e versione del bootloader prima di scrivere.
SHA-256 atteso del risultato: `7a90f823f25f8246576f9fcc8764e18794b2c762a48eb04ac82eabb05cc0d439`.

### 3. Caricala sul controller

1. Metti il controller in modalità aggiornamento: **tieni premuti i due CUE** al centro mentre colleghi il cavo USB.
2. Avvia l'updater ufficiale indicando il file modificato. Siccome la versione è la stessa (1.10), serve `-ALWAYS_UPDATE`.

**Windows (PowerShell):**
```powershell
& "C:\Program Files (x86)\Numark\MixTrack Platinum FX Firmware Updater\MixTrack Platinum FX Firmware Updater.exe" -ABSOLUTE_FIRMWARE_FILE_PATH=C:\percorso\NKCH_ICYH108C02_Y1-10_C903_nofadercuts.bin -ALWAYS_UPDATE
```

**macOS (Terminale)** — non modificare il `.bin` dentro l'app (romperesti la firma); passalo dall'esterno.
L'updater è solo Intel: sui Mac Apple Silicon serve Rosetta.
```bash
"/Applications/MixTrack Platinum FX Firmware Updater.app/Contents/MacOS/FirmwareUpdater" -ABSOLUTE_FIRMWARE_FILE_PATH="$HOME/Downloads/NKCH_ICYH108C02_Y1-10_C903_nofadercuts.bin" -ALWAYS_UPDATE
```

La modifica resta nel controller: una volta caricata funziona su qualsiasi computer.

### Tornare all'originale

Rientra in modalità aggiornamento (due CUE + USB) e carica il `.bin` originale con lo stesso comando,
oppure lancia l'updater ufficiale normalmente.

## ⚠️ Avvertenze

- Firmware **non ufficiale**: usalo a tuo rischio. Nessuna affiliazione con inMusic/Numark.
- Il bootloader resta intatto e l'applicazione viene avviata solo se l'immagine è completa (marcatore
  `55 AA` scritto alla fine), quindi un aggiornamento interrotto si recupera rientrando in modalità
  aggiornamento. Questo è dedotto dal codice del bootloader, non da test distruttivi.
- Vale solo per il firmware **1.10** (`NKCH_ICYH108C02_Y1-10_C903.bin`).

## Documentazione tecnica

Tutto quello che è stato ricostruito durante l'analisi:

- [`docs/fader-cuts.md`](docs/fader-cuts.md) — come funziona Fader Cuts nel firmware e perché la patch è sicura
- [`docs/firmware.md`](docs/firmware.md) — layout della flash, bootloader, marcatori, somma di controllo, dati compressi
- [`docs/protocollo-aggiornamento.md`](docs/protocollo-aggiornamento.md) — protocollo USB HID usato dall'updater
- [`docs/controlli-analogici.md`](docs/controlli-analogici.md) — mappa canale/CC di fader e manopole, soft takeover

## Strumenti

| File | A cosa serve |
|------|--------------|
| `tools/patch_fadercuts.py` | applica la patch al `.bin` originale |
| `tools/extract_from_windows_installer.ps1` | estrae il `.bin` dall'installer Windows senza installarlo |
| `tools/extract_from_dmg.py`, `tools/udif.py` | estraggono il `.bin` dal DMG per Mac senza montarlo |
| `tools/decompress_rw.py` | decomprime i dati iniziali della RAM (tabelle MIDI) dal firmware |
| `tools/ghidra/analyze_firmware.sh` + `DumpFw.java` | decompila tutto il firmware con Ghidra headless |
| `tools/ghidra/decompile_at.sh` + `DisAt.java` | decompila funzioni specifiche (es. per verificare la patch) |

Gli script Ghidra richiedono Ghidra 12.1 e un JDK 21 (`GHIDRA_INSTALL_DIR` impostata).

---

## English summary

Unofficial patch for **Numark Mixtrack Platinum FX firmware 1.10**. In **Fader Cuts** pad mode the
stock firmware runs a timed sequence that sends crossfader `CC 8` messages whenever a pad is pressed,
so the 8 pads can't be used as plain MIDI buttons in custom mappings (Mixxx, DAWs, VJ tools, …).
The patch turns the two functions that start/stop that sequence into `bx lr` (4 bytes changed incl. the
16-bit image checksum), so the pads only send their Note On/Off messages (notes 20–27, 28–35 with SHIFT).
The bootloader is untouched. No vendor binaries are included: extract the original `.bin` from Numark's
official updater with the provided scripts, patch it locally with `tools/patch_fadercuts.py`, and flash it
with the official updater (`-ABSOLUTE_FIRMWARE_FILE_PATH=<file> -ALWAYS_UPDATE`) after entering update
mode (hold both CUE buttons while plugging in USB). Use at your own risk.

## Licenza

Script e documentazione: [MIT](LICENSE). Firmware e software Numark restano dei rispettivi proprietari.
