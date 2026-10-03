#!/usr/bin/env python3
"""Base musicale originale (giro di Do: Do - La min - Fa - Sol), generata in codice:
nessun campione esterno, nessun diritto d'autore di terzi. Uso: musica.py DURATA_S out.wav"""
import sys, wave, numpy as np
SR = 44100; DUR = float(sys.argv[1]); OUT = sys.argv[2]
BPM = float(sys.argv[3]) if len(sys.argv) > 3 else 88; beat = 60 / BPM; bar = 4 * beat
n = int(SR * DUR); t = np.arange(n) / SR
mix = np.zeros(n)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
# accordi in MIDI (voicing morbido) e basso
GIRO = [([60, 64, 67, 72], 48), ([57, 60, 64, 69], 45), ([53, 57, 60, 65], 41), ([55, 59, 62, 67], 43)]
def env(length, a, r):
    e = np.ones(length); ai = int(a * SR); ri = int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e
def add(start, length, sig):
    i = int(start * SR); j = min(n, i + len(sig))
    if i < n: mix[i:j] += sig[:j - i]
k = 0; s = 0.0
while s < DUR:
    notes, bass = GIRO[k % 4]
    L = int(bar * SR) + int(0.4 * SR); tt = np.arange(L) / SR
    # pad: sinusoidi leggermente scordate, attacco lento
    pad = sum(np.sin(2 * np.pi * hz(m) * tt) + 0.6 * np.sin(2 * np.pi * hz(m) * 1.003 * tt) for m in notes)
    add(s, L, 0.035 * pad * env(L, 0.9, 1.0))
    # basso: radice su 1 e 3
    for b in (0, 2):
        Lb = int(beat * 1.8 * SR); tb = np.arange(Lb) / SR
        add(s + b * beat, Lb, 0.16 * np.sin(2 * np.pi * hz(bass) * tb) * np.exp(-tb * 2.2) * env(Lb, 0.01, 0.2))
    # arpeggio pizzicato in ottavi (dal 3° giro in poi, così l'inizio è più calmo)
    if k >= 2:
        seq = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[3] + 12, notes[2] + 12, notes[1] + 12, notes[2] + 12, notes[3] + 12]
        for i, m in enumerate(seq):
            La = int(beat * 0.9 * SR); ta = np.arange(La) / SR
            tone = np.sin(2 * np.pi * hz(m) * ta) + 0.3 * np.sin(2 * np.pi * hz(m) * 2 * ta)
            add(s + i * beat / 2, La, 0.05 * tone * np.exp(-ta * 6) * env(La, 0.005, 0.05))
    # battito leggero (cassa morbida) sui quarti dal 3° giro
    if k >= 2:
        for b in range(4):
            Lk = int(0.25 * SR); tk = np.arange(Lk) / SR
            f = 90 * np.exp(-tk * 18) + 45
            add(s + b * beat, Lk, 0.09 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tk * 14))
    s += bar; k += 1
# dissolvenza in entrata/uscita e normalizzazione
mix *= env(n, 1.5, 3.0)
mix /= max(1e-9, np.max(np.abs(mix))) / 0.8
with wave.open(OUT, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', OUT, round(DUR, 2), 's')
