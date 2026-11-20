#!/usr/bin/env python3
"""effetti.py — effetti sonori del video sulla disostruzione, fatti in codice (nessun file di terzi):
colpo sordo (colpi tra le scapole e pacche), soffio d'aria (tosse e compressioni addominali), passaggio e chiusura.
Uso: python3 effetti.py CARTELLA  → colpo.wav, soffio.wav, passaggio.wav, chiusura.wav (48 kHz, mono)
Scritto per Alessandro Cuollo il 20/11/2026.
"""
import sys, wave
from pathlib import Path
import numpy as np

FR = 48000
rng = np.random.default_rng(7)

def salva(p, x):
    x = np.clip(x / (np.abs(x).max() + 1e-9) * 0.8, -1, 1)
    with wave.open(str(p), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(FR); w.writeframes((x * 32767).astype('<i2').tobytes())

def passa_basso(x, a):
    y = np.zeros_like(x); s = 0.0
    a = np.broadcast_to(np.asarray(a, dtype=float), x.shape)
    for i, v in enumerate(x): s += a[i] * (v - s); y[i] = s
    return y

def colpo():
    t = np.arange(int(0.32 * FR)) / FR
    corpo = np.sin(2 * np.pi * (95 - 40 * t) * t) * np.exp(-t / 0.06)
    tocco = passa_basso(rng.standard_normal(len(t)), 0.25) * np.exp(-t / 0.012)
    return corpo + 0.5 * tocco

def soffio():
    t = np.arange(int(0.6 * FR)) / FR
    inv = np.minimum(t / 0.05, 1) * np.exp(-np.maximum(t - 0.05, 0) / 0.16)
    return passa_basso(rng.standard_normal(len(t)), 0.08) * inv

def passaggio():
    t = np.arange(int(0.7 * FR)) / FR
    inv = np.sin(np.pi * np.clip(t / 0.7, 0, 1)) ** 2
    return passa_basso(rng.standard_normal(len(t)), 0.03 + 0.1 * t) * inv

def chiusura():
    t = np.arange(int(1.6 * FR)) / FR
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t / 0.7) * g for f, g in [(523.25, 1), (659.25, 0.7), (783.99, 0.5)])

if __name__ == '__main__':
    d = Path(sys.argv[1]); d.mkdir(parents=True, exist_ok=True)
    for nome, f in [('colpo', colpo), ('soffio', soffio), ('passaggio', passaggio), ('chiusura', chiusura)]:
        salva(d / f'{nome}.wav', f()); print(nome)
