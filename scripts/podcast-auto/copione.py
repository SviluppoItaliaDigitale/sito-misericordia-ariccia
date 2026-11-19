#!/usr/bin/env python3
"""copione.py — Puntata a due voci da un copione scritto, quando NotebookLM sul PC non c'è (dal 19/11/2026).

Il copione sta in ~/podcast-lavoro-misericordia/<id>/copione.txt, una battuta per riga, «A: …» (Luca)
o «B: …» (Daniela), scritta solo con le frasi delle pagine del sito (fonte.md). Le due voci si generano
con il connettore ElevenLabs della sessione, una richiesta per voce con tutte le sue battute separate
da pause lunghe; qui si dividono sui silenzi e si rimontano nell'ordine del copione.

  copione.py testi ID               scrive voce-A.txt e voce-B.txt (battute con le pause) e stampa quante sono
  copione.py locale ID              (senza crediti ElevenLabs) genera le battute con le voci gratuite,
                                    Kokoro «Nicola» per A e Piper «Paola» per B (modelli in ~/voci), e monta
  copione.py monta ID A.mp3 B.mp3   divide le due registrazioni, controlla che le battute tornino,
                                    rimonta audio.m4a e scrive trascrizione.md (le battute del copione)
Serve ffmpeg. Esce con 1 se il numero dei pezzi non coincide con le battute.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

LAVORO = Path.home() / "podcast-lavoro-misericordia"
PAUSA = ' <break time="3.0s" /> '
VOCI = {"A": "Luca", "B": "Daniela"}
# Come si legge: il 112 si dice «uno, uno, due» (comunicazione-social.md), il sito per lettere.
PRONUNCIA = [(r"\b[Ii]l 112\b", "il numero uno, uno, due"), (r"\b112\b", "uno, uno, due"), (r"misericordia-ariccia\.it", "misericordia trattino ariccia punto it")]


def da_leggere(t: str) -> str:
    for a, b in PRONUNCIA:
        t = re.sub(a, b, t)
    return t


def battute(cartella: Path) -> list[tuple[str, str]]:
    righe = []
    for r in (cartella / "copione.txt").read_text(encoding="utf-8").splitlines():
        r = r.strip()
        if not r:
            continue
        m = re.match(r"^([AB]):\s*(.+)$", r)
        if not m:
            sys.exit(f"Riga non valida nel copione: {r}")
        righe.append((m.group(1), m.group(2)))
    return righe


def pezzi(mp3: Path, dest: Path, voce: str) -> list[Path]:
    """Divide una registrazione sui silenzi di almeno 1,6 s."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mp3), "-af",
                          "silencedetect=noise=-45dB:d=1.6", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    inizi = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    fini = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    durata = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                            "-of", "default=nw=1:nk=1", str(mp3)], text=True))
    tagli, t = [], 0.0
    for s, e in zip(inizi, fini + [durata] * (len(inizi) - len(fini))):
        if s - t > 0.3:
            tagli.append((t, s))
        t = e
    if durata - t > 0.3:
        tagli.append((t, durata))
    out = []
    for i, (a, b) in enumerate(tagli):
        f = dest / f"pezzo-{voce}-{i:02d}.wav"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp3), "-ss", f"{max(0, a - 0.05):.3f}",
                        "-to", f"{b + 0.15:.3f}", "-ac", "1", "-ar", "44100", str(f)], check=True)
        out.append(f)
    return out


VOCI_LOCALI = Path.home() / "voci"


def locale(cartella: Path, bt: list[tuple[str, str]]) -> dict[str, list[Path]]:
    """Una battuta per volta: Kokoro im_nicola (A) e Piper it_IT-paola-medium (B)."""
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(str(VOCI_LOCALI / "kokoro-v1.0.onnx"), str(VOCI_LOCALI / "voices-v1.0.bin"))
    pz: dict[str, list[Path]] = {"A": [], "B": []}
    for i, (v, t) in enumerate(bt):
        grezzo = cartella / f"grezzo-{i:02d}.wav"
        f = cartella / f"pezzo-{v}-{len(pz[v]):02d}.wav"
        if v == "A":
            audio, sr = k.create(da_leggere(t), voice="im_nicola", speed=1.0, lang="it")
            sf.write(grezzo, audio, sr)
        else:
            subprocess.run([sys.executable, "-m", "piper", "-m", str(VOCI_LOCALI / "it_IT-paola-medium.onnx"),
                            "--sentence-silence", "0.35", "-f", str(grezzo)], input=da_leggere(t), text=True,
                           capture_output=True, check=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(grezzo), "-af",
                        "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                        "-ac", "1", "-ar", "44100", str(f)], check=True)
        pz[v].append(f)
    return pz


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in ("testi", "monta", "locale"):
        print(__doc__)
        return 2
    cartella = LAVORO / sys.argv[2]
    bt = battute(cartella)
    if sys.argv[1] == "testi":
        for v in VOCI:
            righe = [da_leggere(t) for w, t in bt if w == v]
            (cartella / f"voce-{v}.txt").write_text(PAUSA.join(righe), encoding="utf-8")
            print(f"{VOCI[v]} ({v}): {len(righe)} battute, {sum(len(t) for t in righe)} caratteri")
        return 0
    if sys.argv[1] == "locale":
        pz = locale(cartella, bt)
    else:
        file = {"A": Path(sys.argv[3]), "B": Path(sys.argv[4])}
        pz = {v: pezzi(file[v], cartella, v) for v in VOCI}
    ok = True
    for v in VOCI:
        attese = sum(1 for w, _ in bt if w == v)
        if len(pz[v]) != attese:
            print(f"{VOCI[v]}: {len(pz[v])} pezzi, battute attese {attese}")
            ok = False
    if not ok:
        return 1
    pausa = cartella / "pausa.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                    "anullsrc=r=44100:cl=mono", "-t", "0.45", str(pausa)], check=True)
    idx = {"A": 0, "B": 0}
    elenco = []
    for v, _ in bt:
        elenco += [pz[v][idx[v]], pausa]
        idx[v] += 1
    lista = cartella / "elenco.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in elenco), encoding="utf-8")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "128k", str(cartella / "audio.m4a")],
                   check=True)
    (cartella / "trascrizione.md").write_text("\n\n".join(t for _, t in bt) + "\n", encoding="utf-8")
    print(f"Montata {cartella / 'audio.m4a'} con {len(bt)} battute.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
