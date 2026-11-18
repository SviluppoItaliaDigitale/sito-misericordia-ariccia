#!/usr/bin/env python3
"""trascrivi.py — Trascrive in locale una puntata con faster-whisper.

Scrive accanto all'audio trascrizione-grezza.txt (un paragrafo per pausa),
da rileggere parola per parola e confrontare con fonte.md prima di pubblicare.
Uso: ~/.podcast-venv/bin/python trascrivi.py AUDIO [--modello medium]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import subprocess

import numpy as np
from faster_whisper import WhisperModel


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--modello", default="medium")
    a = ap.parse_args()
    audio = Path(a.audio)
    modello = WhisperModel(a.modello, device="cpu", compute_type="int8")
    # Decodifica con ffmpeg (16 kHz mono): la lettura interna di faster-whisper
    # passa da PyAV, e PyAV 19 non è più compatibile con faster-whisper 1.2.
    grezzo = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-f", "f32le", "-ac", "1",
                             "-ar", "16000", "-"], check=True, capture_output=True).stdout
    suono = np.frombuffer(grezzo, dtype=np.float32)
    segmenti, _ = modello.transcribe(suono, language="it", vad_filter=True)
    paragrafi, corrente, fine_prec = [], [], 0.0
    for s in segmenti:
        if corrente and s.start - fine_prec > 1.2:
            paragrafi.append(" ".join(corrente))
            corrente = []
        corrente.append(s.text.strip())
        fine_prec = s.end
    if corrente:
        paragrafi.append(" ".join(corrente))
    out = audio.with_name("trascrizione-grezza.txt")
    out.write_text("\n\n".join(paragrafi) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
