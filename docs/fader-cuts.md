# Fader Cuts nel firmware 1.10

Indirizzi riferiti all'immagine caricata a `0x08000000` (applicazione da `0x0800C000`).
Nomi `FUN_xxxxxxxx` = funzioni senza simboli, come le mostra Ghidra.

## Gestore dei pad — `FUN_0800DD24`

Per ogni pad (indice 0–7):

- **pressione** → `FUN_0800D9A0` scrive nel buffer USB‑MIDI un *Note On*:
  `[CIN 0x9, 0x90 | (deck + 4), nota, 0x7F]`.
  La nota viene da una tabella in RAM (`0x20000C6C` senza SHIFT, `0x20000CAC` con SHIFT):
  pad 1–8 → note `0x14–0x1B` (20–27), con SHIFT `0x1C–0x23` (28–35).
  Poi, **se la modalità pad del deck vale 2 (Fader Cuts)**, chiama `FUN_08018AD2(deck, pad)`.
- **rilascio** → `FUN_0800D91C` invia il *Note Off* corrispondente e, in Fader Cuts,
  chiama `FUN_08018DF2(deck)`.

Per i pad 5–8 la chiamata a Fader Cuts è subordinata anche a un flag (`0x20011CA5`).

## Il motore delle sequenze

- `FUN_08018AD2(deck, pad)` carica nella struttura del deck (`0x20...` puntata da `DAT_08018FD4`,
  32 byte per deck) uno degli 8 pattern, ne calcola la durata in funzione del tempo
  (`FUN_080189C6`) e azzera il contatore.
- `FUN_0800F192` → `FUN_08018E46(deck)` viene chiamata periodicamente per entrambi i deck: se la
  sequenza è attiva avanza di passo (`FUN_08018A0E`) e ad ogni passo chiama
  `FUN_0800F140(deck, valore)`, che invia `CC 8` (crossfader) sul canale `0xBF`
  (o sul canale del deck) con il valore del pattern.
- `FUN_08018DF2(deck)` azzera la struttura e chiama `FUN_0800EBC0(6)`, che rimanda la
  posizione **reale** del crossfader (controllo analogico 6, `0xBF CC 8`).

Le funzioni `FUN_08018AD2`, `FUN_08018DF2` e `FUN_08018F80` (stato "in esecuzione") sono chiamate
**solo** da `FUN_0800DD24`.

## La patch

```
0x08018AD2:  70 B5  (push {r4-r6,lr})  ->  70 47  (bx lr)
0x08018DF2:  10 B5  (push {r4,lr})     ->  70 47  (bx lr)
0x0803FFFE:  somma a 16 bit big-endian di 0x00000–0x3FFFD ricalcolata  (C7 9E -> C7 22)
```

Con l'avvio della sequenza disattivato, lo stato del deck resta 0: `FUN_08018E46` non fa nulla e
`FUN_08018F80` restituisce sempre "non attiva". Il rilascio non rimanda più il crossfader.
I Note On/Off dei pad sono generati prima e indipendentemente, quindi restano invariati.

Verifica: decompilando l'immagine patchata con `tools/ghidra/decompile_at.sh` le due funzioni
risultano `void FUN_...(void) { return; }` e il gestore dei pad conserva tutte le chiamate di invio note.
