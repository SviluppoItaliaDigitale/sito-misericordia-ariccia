#!/usr/bin/env python3
"""controlla-magazzino.py — Quante puntate del podcast sono in calendario.

Adattato dal podcast della Protezione Civile di Genzano. Gira ogni giorno su
GitHub (controllo-podcast.yml), anche a PC spento.
Scrive il testo della segnalazione su --corpo e termina con:
0 = tutto bene (almeno --minimo puntate future e nessuna uscita mancata),
1 = magazzino basso o uscita mancata (aprire/aggiornare la issue).
Uso: controlla-magazzino.py [--minimo 2] [--corpo FILE]
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
PODCAST = RADICE / "content" / "podcast"
GIORNI_USCITA = (2, 5)  # mercoledì e sabato (la Protezione Civile esce martedì e venerdì)
NOMI = {2: "mercoledì", 5: "sabato"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minimo", type=int, default=2)
    ap.add_argument("--corpo", default="")
    a = ap.parse_args()
    oggi = date.today()
    date_attive = []
    for f in PODCAST.glob("*.md"):
        t = f.read_text(encoding="utf-8")
        if f.name == "_index.md" or "render: never" in t:
            continue
        m = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", t, re.M)
        if m:
            date_attive.append(date.fromisoformat(m.group(1)))
    future = sorted(d for d in date_attive if d > oggi)
    mancate = []
    if date_attive:  # le uscite mancate contano solo da quando il podcast è ripartito
        inizio = min(date_attive)
        d = inizio
        while d <= oggi:
            if d.weekday() in GIORNI_USCITA and d not in date_attive:
                mancate.append(d)
            d += timedelta(days=1)
    mancate = [d for d in mancate if d >= oggi - timedelta(days=14)]
    righe = [f"Controllo del {oggi.strftime('%d/%m/%Y')}.", ""]
    righe.append(f"- Puntate in calendario dopo oggi: **{len(future)}**"
                 + (f" (ultima: {future[-1].strftime('%d/%m/%Y')})" if future else ""))
    if mancate:
        righe.append("- Uscite mancate negli ultimi 14 giorni: "
                     + ", ".join(f"{NOMI[d.weekday()]} {d.strftime('%d/%m')}" for d in mancate))
    problema = len(future) < a.minimo or bool(mancate)
    righe += ["", "Il magazzino si riempie da solo quando il PC è acceso, con Chrome aperto e l'accesso a Google: "
              "ogni giorno, se ci sono meno di quattro settimane di puntate (8), se ne producono di nuove "
              "(scripts/podcast-auto/README.md). Se il PC resterà spento a lungo, basta riaccenderlo."]
    if a.corpo:
        Path(a.corpo).write_text("\n".join(righe) + "\n", encoding="utf-8")
    print("\n".join(righe))
    return 1 if problema else 0


if __name__ == "__main__":
    sys.exit(main())
