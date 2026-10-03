#!/usr/bin/env python3
"""Voce italiana Kokoro (Sara o Nicola) per i video: kokoro_voce.py VOCE VELOCITA PAUSA OUT.wav < testo
Gira nel venv kokoro/venv (kokoro-onnx 0.4.9) con il modello kokoro/kokoro-v1.0.onnx e le voci kokoro/voci-it.npz:
come prepararli è scritto nel README. Legge frase per frase e mette PAUSA secondi di silenzio tra una frase e l'altra."""
import re, sys, wave
from pathlib import Path
import numpy as np
from kokoro_onnx import Kokoro

K = Path(__file__).resolve().parent / 'kokoro'
SR = 24000
VOCI = {'sara': 'if_sara', 'nicola': 'im_nicola'}


class KokoroIt(Kokoro):
    # L'esportazione ONNX di onnx-community vuole la velocità in float32 (kokoro-onnx 0.4.9 la passa in int32).
    def _create_audio(self, phonemes, voice, speed):
        tokens = np.array(self.tokenizer.tokenize(phonemes[:510]), dtype=np.int64)
        style = np.array(voice[len(tokens)], dtype=np.float32)
        audio = self.sess.run(None, {'input_ids': [[0, *tokens, 0]], 'style': style,
                                     'speed': np.array([speed], dtype=np.float32)})[0]
        return audio, SR


def main():
    voce, vel, pausa, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    k = KokoroIt(str(K / 'kokoro-v1.0.onnx'), str(K / 'voci-it.npz'))
    frasi = [f for f in re.split(r'(?<=[.!?…])\s+', sys.stdin.read().strip()) if f]
    parti = []
    for i, f in enumerate(frasi):
        a, _ = k.create(f, voice=VOCI[voce], speed=vel, lang='it')
        parti.append(np.asarray(a, dtype=np.float32).reshape(-1))
        if i < len(frasi) - 1:
            parti.append(np.zeros(int(SR * pausa), dtype=np.float32))
    a = np.concatenate(parti) if parti else np.zeros(SR // 10, dtype=np.float32)
    with wave.open(out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == '__main__':
    main()
