"""
transcribe_watch.py (v8 - faster-whisper)
-----------------------------------------
Fa SOLO trascrizione + diarization con rubrica vocale persistente. Nessuna
logica di allarme qui dentro: la valutazione "e' rilevante, serve avvisare?"
e' interamente compito di Cowork durante il ciclo di aggiornamento, cosi'
resta tutto dentro la stessa sessione, senza chiamate API separate.

MOTORE DI TRASCRIZIONE
----------------------
Usa faster-whisper (backend CTranslate2) con quantizzazione int8 su CPU:
sullo stesso modello 'small' e' ~25x realtime su una CPU desktop moderna
(contro ~1x di openai-whisper), quindi sta dietro al live con ampio margine
anche su call di un'ora e svuota la coda in fretta a fine sessione. Ha inoltre
un filtro VAD integrato che salta il silenzio: riduce sensibilmente le
allucinazioni di Whisper nei tratti muti (soprattutto sul flusso microfono).

E' possibile forzare la GPU con --device cuda (richiede le DLL CUDA/cuDNN),
ma su CPU int8 la velocita' e' gia' ampiamente sufficiente: il default e' cpu.

COSA FA
-------
Sorveglia la cartella dei chunk audio (scritta da record_chunks.py, che
produce chunk_ALTRI_*.wav per il loopback e chunk_IO_*.wav per il
microfono), trascrive ogni nuovo chunk, etichetta il flusso "Altri" con uno
"Speaker N" persistente (rubrica vocale in voice_directory/), scrive tutto in
transcript.txt, e cancella l'audio subito dopo la trascrizione.

USO
---
    python transcribe_watch.py --chunkdir ./chunks --transcript ./transcript.txt \
        --model small --language it \
        --silence-gap 1.0 --speaker-threshold 0.75 --voice-dir ./voice_directory
"""

import argparse
import json
import os
import time
import wave
from pathlib import Path

import numpy as np

from resemblyzer import VoiceEncoder, preprocess_wav

SAMPLE_RATE = 16000


def source_label(filename: str) -> str:
    if filename.startswith("chunk_IO_"):
        return "Io"
    if filename.startswith("chunk_ALTRI_"):
        return "Altri"
    return "?"


def chunk_index(filename: str) -> int:
    try:
        return int(filename.rsplit("_", 1)[-1].split(".")[0])
    except Exception:
        return 0


def format_clock(epoch_seconds: float) -> str:
    return time.strftime("%H:%M:%S", time.localtime(epoch_seconds))


def load_wav_16k_mono(path: Path) -> np.ndarray:
    """Legge un chunk WAV (16 kHz PCM int16, come lo scrive record_chunks.py) e
    lo restituisce come float32 mono normalizzato in [-1, 1], senza passare da
    ffmpeg. Se il file ha piu' canali, li media in mono."""
    with wave.open(str(path), "rb") as wf:
        n_channels = wf.getnchannels()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if n_channels > 1:
        audio = audio.reshape(-1, n_channels).mean(axis=1)
    return audio


class SpeakerRegistry:
    """Registro persistente di embedding vocali (impronte, non audio).
    Caricato/salvato su disco in embeddings.json cosi' la stessa persona
    viene riconosciuta anche in esecuzioni/call successive."""

    def __init__(self, similarity_threshold: float, path: Path):
        self.threshold = similarity_threshold
        self.path = path
        self.ids: list[int] = []
        self.centroids: list[np.ndarray] = []
        self.counts: list[int] = []
        self._next_id = 1
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                for entry in data.get("speakers", []):
                    self.ids.append(entry["id"])
                    self.centroids.append(np.array(entry["centroid"], dtype=np.float32))
                    self.counts.append(entry["count"])
                if self.ids:
                    self._next_id = max(self.ids) + 1
                print(f"[transcribe_watch] Rubrica vocale caricata: {len(self.ids)} persone gia' note.")
            except Exception as e:
                print(f"[transcribe_watch] Impossibile leggere la rubrica esistente ({e}), riparto vuota.")

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "speakers": [
                {"id": sid, "centroid": centroid.tolist(), "count": count}
                for sid, centroid, count in zip(self.ids, self.centroids, self.counts)
            ]
        }
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    def assign(self, embedding: np.ndarray) -> int:
        if not self.centroids:
            new_id = self._next_id
            self._next_id += 1
            self.ids.append(new_id)
            self.centroids.append(embedding)
            self.counts.append(1)
            self._save()
            return new_id

        sims = [self._cosine_sim(embedding, c) for c in self.centroids]
        best_idx = int(np.argmax(sims))
        best_sim = sims[best_idx]

        if best_sim >= self.threshold:
            n = self.counts[best_idx]
            self.centroids[best_idx] = (self.centroids[best_idx] * n + embedding) / (n + 1)
            self.counts[best_idx] += 1
            self._save()
            return self.ids[best_idx]
        else:
            new_id = self._next_id
            self._next_id += 1
            self.ids.append(new_id)
            self.centroids.append(embedding)
            self.counts.append(1)
            self._save()
            return new_id


class NameDirectory:
    """Mappa persistente id-speaker -> nome, curata da Cowork (o a mano)."""

    def __init__(self, path: Path):
        self.path = path
        self.names: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                self.names = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"[transcribe_watch] Impossibile leggere names.json ({e}), riparto vuoto.")
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("{}", encoding="utf-8")

    def lookup(self, speaker_id: int) -> str | None:
        entry = self.names.get(str(speaker_id))
        return entry["name"] if entry else None

    def refresh(self):
        self._load()


def _enable_cuda_dlls():
    """Se si usa --device cuda, aggancia le DLL fornite dai wheel nvidia-*-cu12
    (se installati) alla ricerca DLL di Windows."""
    import glob
    base = os.path.join(os.path.dirname(os.__file__), "..", "site-packages", "nvidia")
    base = os.path.abspath(base)
    for d in glob.glob(os.path.join(base, "*", "bin")):
        try:
            os.add_dll_directory(d)
        except Exception:
            pass


def load_model(model_name: str, device: str, compute_type: str):
    from faster_whisper import WhisperModel
    if device == "cuda":
        _enable_cuda_dlls()
    print(f"[transcribe_watch] Carico faster-whisper '{model_name}' (device={device}, compute_type={compute_type})...")
    return WhisperModel(model_name, device=device, compute_type=compute_type)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunkdir", default="./chunks")
    parser.add_argument("--transcript", default="./transcript.txt")
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", default="it")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--compute-type", default="int8",
                        help="int8 (cpu, default), int8_float16/float16 (gpu)")
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--stopfile", default="./STOP")
    parser.add_argument("--poll-seconds", type=float, default=1.0)
    parser.add_argument("--silence-gap", type=float, default=1.0)
    parser.add_argument("--min-segment-chars", type=int, default=2)
    parser.add_argument("--speaker-threshold", type=float, default=0.75)
    parser.add_argument("--min-diarization-seconds", type=float, default=0.5)
    parser.add_argument("--no-vad", action="store_true",
                        help="disattiva il filtro VAD (di default e' attivo, salta i silenzi)")
    parser.add_argument("--no-diarize-io", action="store_true",
                        help="NON riconoscere lo speaker sul flusso microfono [Io] (di default lo confronta con la rubrica come [Altri])")
    parser.add_argument("--voice-dir", default="./voice_directory")
    args = parser.parse_args()

    chunkdir = Path(args.chunkdir)
    chunkdir.mkdir(parents=True, exist_ok=True)
    transcript_path = Path(args.transcript)
    stopfile = Path(args.stopfile)

    voice_dir = Path(args.voice_dir)
    embeddings_path = voice_dir / "embeddings.json"
    names_path = voice_dir / "names.json"

    model = load_model(args.model, args.device, args.compute_type)
    print("[transcribe_watch] Carico il modello di speaker embedding (Resemblyzer)...")
    encoder = VoiceEncoder()
    speaker_registry = SpeakerRegistry(similarity_threshold=args.speaker_threshold, path=embeddings_path)
    name_directory = NameDirectory(path=names_path)
    use_vad = not args.no_vad
    # Etichette su cui fare diarization/riconoscimento vocale. Di default
    # entrambe: sul microfono [Io] possono parlare persone diverse, quindi anche
    # quel flusso va confrontato con la rubrica.
    diarize_labels = {"Altri"} if args.no_diarize_io else {"Altri", "Io"}
    print(f"[transcribe_watch] Modelli e rubrica caricati (VAD={'on' if use_vad else 'off'}, "
          f"diarization su: {', '.join(sorted(diarize_labels))}). In ascolto sui nuovi chunk...")

    processed = set()
    last_segment_end = {"Io": None, "Altri": None}
    chunks_since_name_refresh = 0

    while True:
        chunks = sorted(chunkdir.glob("chunk_*.wav"), key=lambda p: (chunk_index(p.name), p.name))
        new_chunks = [c for c in chunks if c.name not in processed]

        for chunk_path in new_chunks:
            label = source_label(chunk_path.name)
            chunk_mtime = chunk_path.stat().st_mtime

            try:
                seg_iter, _info = model.transcribe(
                    str(chunk_path),
                    language=args.language,
                    beam_size=args.beam_size,
                    vad_filter=use_vad,
                    condition_on_previous_text=False,
                )
                # faster-whisper e' lazy: materializzo qui i segmenti del chunk.
                segments = [
                    {"start": s.start, "end": s.end, "text": s.text}
                    for s in seg_iter
                ]
            except Exception as e:
                print(f"[transcribe_watch] Errore trascrivendo {chunk_path.name}: {e}")
                processed.add(chunk_path.name)
                chunk_path.unlink(missing_ok=True)
                continue

            if not segments:
                processed.add(chunk_path.name)
                chunk_path.unlink(missing_ok=True)
                continue

            raw_audio = None
            if label in diarize_labels:
                try:
                    raw_audio = load_wav_16k_mono(chunk_path)
                except Exception as e:
                    print(f"[transcribe_watch] Impossibile caricare l'audio per la diarization: {e}")

            chunk_duration_covered = segments[-1]["end"]
            chunk_start_epoch = chunk_mtime - chunk_duration_covered

            for seg in segments:
                text = seg["text"].strip()
                if len(text) < args.min_segment_chars:
                    continue

                seg_start_epoch = chunk_start_epoch + seg["start"]
                seg_end_epoch = chunk_start_epoch + seg["end"]
                seg_duration = seg["end"] - seg["start"]

                prev_end = last_segment_end.get(label)
                if label in diarize_labels and prev_end is not None:
                    gap = seg_start_epoch - prev_end
                    if gap >= args.silence_gap:
                        with open(transcript_path, "a", encoding="utf-8") as f:
                            f.write(f"[{format_clock(seg_start_epoch)}] --- possibile cambio di interlocutore (pausa {gap:.1f}s) ---\n")

                speaker_tag = ""
                if label in diarize_labels and raw_audio is not None and seg_duration >= args.min_diarization_seconds:
                    try:
                        start_sample = int(seg["start"] * SAMPLE_RATE)
                        end_sample = int(seg["end"] * SAMPLE_RATE)
                        seg_audio = raw_audio[start_sample:end_sample]
                        processed_wav = preprocess_wav(seg_audio, source_sr=SAMPLE_RATE)
                        if len(processed_wav) > 0:
                            embedding = encoder.embed_utterance(processed_wav)
                            speaker_id = speaker_registry.assign(embedding)
                            known_name = name_directory.lookup(speaker_id)
                            if known_name:
                                speaker_tag = f" [Speaker {speaker_id} - {known_name} (da rubrica)]"
                            else:
                                speaker_tag = f" [Speaker {speaker_id}]"
                    except Exception as e:
                        print(f"[transcribe_watch] Diarization fallita su un segmento: {e}")

                with open(transcript_path, "a", encoding="utf-8") as f:
                    f.write(f"[{format_clock(seg_start_epoch)}] [{label}]{speaker_tag} {text}\n")

                last_segment_end[label] = seg_end_epoch

            n_speakers_totali = len(speaker_registry.ids)
            print(f"[transcribe_watch] {chunk_path.name} ({label}) -> {len(segments)} segmenti aggiunti "
                  f"(persone in rubrica: {n_speakers_totali})")

            processed.add(chunk_path.name)
            chunk_path.unlink(missing_ok=True)

        chunks_since_name_refresh += len(new_chunks)
        if chunks_since_name_refresh >= 5:
            name_directory.refresh()
            chunks_since_name_refresh = 0

        if stopfile.exists() and not new_chunks:
            print("[transcribe_watch] STOP trovato e coda vuota, esco.")
            break

        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    main()
