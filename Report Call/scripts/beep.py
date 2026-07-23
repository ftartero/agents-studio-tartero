"""
beep.py
--------
Riproduce un breve segnale acustico dagli speaker di sistema. Non fa nessuna
valutazione: la decisione "serve avvisare?" la prende Cowork leggendo il
contesto (vedi cowork_task_prompt.txt). Questo script serve solo a fare
rumore quando Cowork lo richiama.

USO
---
    python beep.py
"""

import numpy as np
import soundcard as sc


def beep(frequency=880, duration=0.35, samplerate=16000):
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    tone = 0.3 * np.sin(2 * np.pi * frequency * t)
    sc.default_speaker().play(tone, samplerate=samplerate)


if __name__ == "__main__":
    beep()
