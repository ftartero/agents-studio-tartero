"""
enroll_voice.py
---------------
Arruola (registra) una voce nella rubrica vocale condivisa (voice_directory/),
a partire da un file audio pulito di UNA sola persona che parla. Calcola
l'impronta vocale con lo STESSO encoder usato dalla trascrizione (resemblyzer
VoiceEncoder, 16 kHz) e la aggiunge a embeddings.json + names.json, cosi' quella
persona verra' poi riconosciuta con lo stesso id in tutte le sessioni e da tutti
gli agenti che condividono questa cartella.

USO
---
    python enroll_voice.py "C:\\percorso\\mia_voce.m4a" --name "Flavio Tartero" \
        --confidence certa --voice-dir voice_directory

Accetta qualsiasi formato audio (wav/m4a/mp3/...): converte internamente in
WAV 16 kHz mono con ffmpeg. Se lo speaker esiste gia' (stessa voce sopra soglia),
di default AGGIORNA quel profilo invece di crearne un doppione; con --force-new
crea comunque un nuovo id.
"""

import argparse
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

SAMPLE_RATE = 16000


def to_wav_16k_mono(src: Path) -> Path:
    """Converte un audio qualsiasi in WAV 16k mono con ffmpeg, in un file temporaneo."""
    tmp = Path(tempfile.gettempdir()) / f"enroll_{src.stem}_16k.wav"
    cmd = ["ffmpeg", "-y", "-i", str(src), "-ar", str(SAMPLE_RATE), "-ac", "1", str(tmp)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not tmp.exists():
        raise SystemExit(f"Conversione ffmpeg fallita per {src}:\n{res.stderr[-800:]}")
    return tmp


def read_wav_float(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        n = wf.getnframes()
        raw = wf.readframes(n)
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def cosine(a, b):
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return 0.0 if d == 0 else float(np.dot(a, b) / d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", help="File audio della voce da arruolare")
    ap.add_argument("--name", required=True, help="Nome da associare alla voce")
    ap.add_argument("--confidence", default="certa", choices=["certa", "presunta"])
    ap.add_argument("--voice-dir", default="voice_directory")
    ap.add_argument("--match-threshold", type=float, default=0.75,
                    help="Se una voce nota supera questa similarita', la aggiorna invece di duplicarla")
    ap.add_argument("--force-new", action="store_true", help="Crea sempre un nuovo id")
    ap.add_argument("--date", default="", help="Data last_seen YYYY-MM-DD (default: oggi non disponibile -> vuoto)")
    args = ap.parse_args()

    src = Path(args.audio)
    if not src.exists():
        raise SystemExit(f"File non trovato: {src}")

    voice_dir = Path(args.voice_dir)
    voice_dir.mkdir(parents=True, exist_ok=True)
    emb_path = voice_dir / "embeddings.json"
    names_path = voice_dir / "names.json"

    print(f"[enroll] Converto e carico l'audio: {src.name}")
    wav_path = to_wav_16k_mono(src)
    wav = read_wav_float(wav_path)
    processed = preprocess_wav(wav, source_sr=SAMPLE_RATE)
    if len(processed) == 0:
        raise SystemExit("Dopo il preprocessing l'audio e' vuoto (troppo silenzio?). Riprova con una registrazione piu' chiara.")

    print("[enroll] Carico l'encoder (resemblyzer) e calcolo l'impronta...")
    encoder = VoiceEncoder()
    embedding = encoder.embed_utterance(processed)

    # carica registro esistente
    data = {"speakers": []}
    if emb_path.exists():
        data = json.loads(emb_path.read_text(encoding="utf-8"))
    speakers = data.setdefault("speakers", [])

    names = {}
    if names_path.exists():
        names = json.loads(names_path.read_text(encoding="utf-8"))

    # cerca una voce gia' simile
    best_id, best_sim = None, -1.0
    for s in speakers:
        sim = cosine(embedding, np.array(s["centroid"], dtype=np.float32))
        if sim > best_sim:
            best_sim, best_id = sim, s["id"]

    if (not args.force_new) and best_id is not None and best_sim >= args.match_threshold:
        # aggiorna il centroide esistente (media pesata) e il nome
        for s in speakers:
            if s["id"] == best_id:
                n = s.get("count", 1)
                c = np.array(s["centroid"], dtype=np.float32)
                s["centroid"] = ((c * n + embedding) / (n + 1)).tolist()
                s["count"] = n + 1
                break
        assigned = best_id
        action = f"AGGIORNATA voce esistente id {best_id} (similarita' {best_sim:.2f})"
    else:
        assigned = (max((s["id"] for s in speakers), default=0) + 1)
        speakers.append({"id": assigned, "centroid": embedding.tolist(), "count": 1})
        action = f"CREATA nuova voce id {assigned}" + (
            f" (voce piu' simile: id {best_id} a {best_sim:.2f}, sotto soglia)" if best_id is not None else "")

    names[str(assigned)] = {"name": args.name, "confidence": args.confidence, "last_seen": args.date}

    emb_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    names_path.write_text(json.dumps(names, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[enroll] {action}")
    print(f"[enroll] '{args.name}' -> Speaker {assigned}  (confidence={args.confidence})")
    print(f"[enroll] Rubrica ora: {len(speakers)} voci totali.")


if __name__ == "__main__":
    main()
