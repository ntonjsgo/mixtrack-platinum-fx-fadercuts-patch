# Protocollo dell'updater (USB HID)

Ricavato decompilando l'updater per Windows (`MixTrack Platinum FX Firmware Updater.exe` 1.0.0.26078,
classe `LMixTrackHIDEngine`).

## Trasporto

- Individuazione del dispositivo con `SetupDi*`, apertura con `CreateFileW`.
- Ogni messaggio è un report HID da **65 byte** (Report ID 0 + 64 byte) scritto con `WriteFile` e letto
  con `ReadFile` in modalità overlapped, timeout 5 s (`0x004095B0` invio, `0x004096F0` invio + risposta).
- `HidD_SetOutputReport` e `HidD_GetAttributes` vengono caricate da `hid.dll` ma mai chiamate.

## Due protocolli nel binario

| | File binario (`fopen "rb"`), `0x004035F0` | File di testo (`fopen "r"`), `0x00407EF0` |
|---|---|---|
| Pacchetto | `55 4F 01 <cmd>` | `01 <cmd> … <CRC> 17` |
| Comandi | `C1` avvio, `C2` 16 byte dati, `C4` stato/versione (risposta `F4`), `C3` fine | `38` versione, `32` limiti memoria, `37`/`39` dati, `3A` chiude blocco, `3B` riavvio |
| Controllo | somma a 16 bit sui 16 byte | CRC‑16/X‑25 (poly `0x8408`) o somma in complemento a due |
| Dati/pacchetto | 16 | 53 |

Il Mixtrack Platinum FX usa il primo (il `.bin` viene aperto in `"rb"`). Il secondo è probabilmente
codice condiviso con altri prodotti inMusic.

### Sequenza per il `.bin`

1. `C1`
2. per ogni blocco da 16 byte del file: `C2` con offset (24 bit), dati e somma
3. `C4` (legge la versione), `C3` (fine e riavvio)

Pacchetto `C2` (32 byte):

```
00: 55 4F 01 C2
04: offset[23:16] offset[15:8] offset[7:0]
09..24: 16 byte di dati
30..31: somma a 16 bit (big-endian) dei byte 9..24
```

## Opzioni da riga di comando dell'updater

`-ABSOLUTE_FIRMWARE_FILE_PATH=`, `-FIRMWARE_IMAGE_NAME=`, `-DEVICE_BOOTLOADER_PID=`, `-ALWAYS_UPDATE`,
`-START_UPDATE_AUTOMATICALLY`, `-SILENT_IF_UPDATE_NOT_NEEDED`, `-RETURN_UPDATE_MODE_STATUS`.
Le stesse stringhe sono presenti nell'updater per macOS (`FirmwareUpdater`, solo x86_64).

## Integrità

Nessuna firma crittografica: solo la somma per blocco lato trasporto, il marcatore `55 AA` e la somma
globale in coda all'immagine (non è stato osservato chi la verifichi).
