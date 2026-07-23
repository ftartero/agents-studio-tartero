"""
record_chunks.py (v2)
----------------------
Cattura DUE flussi audio in parallelo, a blocchi (chunk) di durata fissa:
  1. "loopback" = tutto cio' che il PC sta riproducendo in uscita (altri
     partecipanti della call, video YouTube, audio di una diretta, ecc.)
  2. "mic"      = il tuo microfono (la tua voce)

Ogni chunk viene salvato con un prefisso che ne indica la fonte:
    chunk_ALTRI_00001.wav   (loopback)
    chunk_IO_00001.wav      (microfono)

cosi' transcribe_watch.py puo' etichettare correttamente chi ha detto cosa
("Io" vs "Altri" — non e' vera diarization tra i singoli partecipanti remoti,
ma distingue almeno te dal resto).

NOTE PER PIATTAFORMA
---------------------
- Windows: 'soundcard' usa il loopback WASAPI in modo nativo per il flusso 1;
  il microfono di default viene usato per il flusso 2, non serve altro.
- macOS: per il flusso 1 (loopback) serve BlackHole (vedi README). Il
  microfono (flusso 2) funziona con il device standard, nessuna
  configurazione aggiuntiva.
- Linux: dipende dal setup PulseAudio/PipeWire per il loopback.

USO
---
    python record_chunks.py --outdir ./chunks --chunk-seconds 15

Lo script gira finche' non trovi un file "STOP" nella cartella indicata con
--stopfile (default: STOP nella cartella corrente), oppure premi Ctrl+C.
"""

import argparse
import threading
import wave
from pathlib import Path

import numpy as np
import soundcard as sc


def get_loopback_mic(device_name: str | None):
    """Ritorna il microfono 'loopback' per catturare l'audio di sistema in uscita."""
    if device_name:
        for mic in sc.all_microphones(include_loopback=True):
            if device_name.lower() in mic.name.lower():
                return mic
        raise SystemExit(f"Dispositivo loopback '{device_name}' non trovato. "
                          f"Disponibili: {[m.name for m in sc.all_microphones(include_loopback=True)]}")
    try:
        default_speaker = sc.default_speaker()
        return sc.get_microphone(default_speaker.name, include_loopback=True)
    except Exception as e:
        raise SystemExit(
            "Impossibile trovare automaticamente un dispositivo loopback.\n"
            "Su macOS: installa BlackHole e passa --loopback-device 'BlackHole'.\n"
            f"Disponibili: {[m.name for m in sc.all_microphones(include_loopback=True)]}\n"
            f"Errore originale: {e}"
        )


def get_input_mic(device_name: str | None):
    """Ritorna il microfono reale (la tua voce)."""
    if device_name:
        for mic in sc.all_microphones(include_loopback=False):
            if device_name.lower() in mic.name.lower():
                return mic
        raise SystemExit(f"Microfono '{device_name}' non trovato. "
                          f"Disponibili: {[m.name for m in sc.all_microphones(include_loopback=False)]}")
    return sc.default_microphone()


def write_wav(path: Path, data: np.ndarray, samplerate: int):
    data_int16 = np.clip(data * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(data_int16.shape[1] if data_int16.ndim > 1 else 1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(data_int16.tobytes())


def record_into(recorder, frames_needed, out_holder):
    out_holder["data"] = recorder.record(numframes=frames_needed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="./chunks", help="Cartella dove salvare i chunk audio")
    parser.add_argument("--chunk-seconds", type=int, default=15, help="Durata di ogni chunk in secondi")
    parser.add_argument("--samplerate", type=int, default=16000, help="Sample rate (16000 va bene per Whisper)")
    parser.add_argument("--loopback-device", default=None, help="Nome (parziale) del dispositivo loopback")
    parser.add_argument("--mic-device", default=None, help="Nome (parziale) del microfono da usare")
    parser.add_argument("--stopfile", default="./STOP", help="Se questo file compare, lo script si ferma")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stopfile = Path(args.stopfile)

    loop_mic = get_loopback_mic(args.loopback_device)
    my_mic = get_input_mic(args.mic_device)
    print(f"[record_chunks] Loopback (Altri): {loop_mic.name}")
    print(f"[record_chunks] Microfono (Io):   {my_mic.name}")
    print(f"[record_chunks] Chunk da {args.chunk_seconds}s in {outdir.resolve()}")
    print(f"[record_chunks] Per fermare: crea il file {stopfile.resolve()} oppure Ctrl+C")

    idx = 0
    frames_needed = args.samplerate * args.chunk_seconds

    with loop_mic.recorder(samplerate=args.samplerate) as loop_rec, \
         my_mic.recorder(samplerate=args.samplerate) as mic_rec:
        while True:
            if stopfile.exists():
                print("[record_chunks] STOP trovato, esco.")
                break
            idx += 1

            loop_holder, mic_holder = {}, {}
            t1 = threading.Thread(target=record_into, args=(loop_rec, frames_needed, loop_holder))
            t2 = threading.Thread(target=record_into, args=(mic_rec, frames_needed, mic_holder))
            t1.start(); t2.start()
            t1.join(); t2.join()

            write_wav(outdir / f"chunk_ALTRI_{idx:05d}.wav", loop_holder["data"], args.samplerate)
            write_wav(outdir / f"chunk_IO_{idx:05d}.wav", mic_holder["data"], args.samplerate)
            print(f"[record_chunks] Scritti chunk #{idx}")


if __name__ == "__main__":
    main()
