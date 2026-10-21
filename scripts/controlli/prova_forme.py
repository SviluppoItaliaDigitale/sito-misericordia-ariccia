#!/usr/bin/env python3
"""Prova delle forme da non usare (FORME_SBAGLIATE in controlla_sito.py), sui controlli di ogni PR.

Per ogni regola ci sono esempi che il controllo deve segnalare e forme giuste che deve lasciar
passare. Nasce dal rilievo sulla PR 207 del 21/10/2026: la prima versione del controllo sulla firma
delle schede della Parola della domenica guardava solo l'inizio del valore, così una firma con un
nome in più o senza data passava. Gli esempi sono scritti a pezzi (virgolette con chr(34), motto
spezzato) perché il controllo, che legge anche scripts/, non segnali questo file.
Esce con 1 se un caso non va come deve. Solo libreria standard. Uso: prova_forme.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from controlla_sito import FORME_SBAGLIATE  # noqa: E402

Q = chr(34)  # virgolette doppie
MOTTO = "renda merito"


def firma(valore):
    return f"{Q}preparata_da{Q}: {Q}{valore}{Q}"


CASI = [  # (testo, deve essere segnalato)
    ("Che " + "Dio ve ne " + MOTTO, True),
    ("che " + "dio te ne " + MOTTO, True),
    ("Che " + "Dio gliene " + MOTTO, True),
    ("Che Iddio ve ne " + MOTTO, False),
    ("Che Iddio gliene " + MOTTO, False),
    (firma("Assistente, 2026-10-09"), True),
    (firma("Alessandro Cuollo, Assistente"), True),
    (firma("Alessandro Cuollo"), True),
    (firma("Alessandro Cuollo, 2026-10-21, Assistente"), True),
    (firma("Alessandro Cuollo, 2026-13-01"), True),
    (firma("IU0QVW, 2026-10-21"), True),
    (firma(""), True),
    (firma("Alessandro Cuollo, 2026-10-21"), False),
    (f"{Q}preparata_da{Q}:{Q}Alessandro Cuollo, 2026-10-09{Q}", False),
]

errori = 0
for testo, atteso in CASI:
    segnalato = any(rx.search(testo) for rx, _ in FORME_SBAGLIATE)
    if segnalato != atteso:
        errori += 1
        print(f"❌ {testo!r}: {'segnalato' if segnalato else 'non segnalato'}, atteso il contrario")
print(f"{len(CASI) - errori}/{len(CASI)} casi come previsto")
sys.exit(1 if errori else 0)
