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
    # anafilassi (21/10/2026): la seconda dose si usa se i sintomi persistono
    ("Se dopo 5 minuti non " + "migliora e ha una seconda dose, si può ripetere.", True),
    ("If they have not " + "improved after **5 minutes** and have a second dose, it can be repeated.", True),
    ("Se dopo 5 minuti ha ancora i sintomi, anche se va un po' meglio, e ha una seconda dose, usala.", False),
    ("If symptoms are still present after **5 minutes**, even if slightly better, and they have a second dose, use it.", False),
    # soffocamento (18/10/2026): il 112 si chiama subito, non solo quando perde conoscenza
    ("Se perde conoscenza, accompagnalo a terra, " + "chiama il 112 e inizia la rianimazione.", True),
    ("Se perde conoscenza, accompagnalo a terra, " + "chiama '+U12+' e inizia la rianimazione.", True),
    ("Se perde conoscenza, accompagnalo a terra e inizia la rianimazione. Se nessuno ha ancora chiamato il 112, chiamalo subito.", False),
    # rubrica, correzioni del 21/10/2026
    ("Aspetta 15 minuti. Se non migliora, dagli " + "altro zucchero.", True),
    ("Aspetta 15 minuti. Se ha ancora i sintomi, dagli altro zucchero. Se non migliora, chiama il 112.", False),
    ("Spingi per un terzo del torace, circa 4 cm " + "nel lattante, 5 nel bambino.", True),
    ("circa quattro centimetri " + "nel lattante", True),
    ("to one third of its depth (about 4 cm " + "in an infant, 5 cm in a child)", True),
    ("Spingi per almeno un terzo del torace, ma mai più di 6 cm.", False),
    ("gauge(-400,-260,c,'≈ 4 " + "cm')", True),
    ("gauge(-400,-260,c,'≥ 1/3')", False),
    ("mettigli un cuscino " + "sotto la testa, coprilo", True),
    ("a cushion " + "under the head, a blanket", True),
    ("Metti qualcosa di morbido sotto la testa, come una giacca piegata.", False),
    ("Di solito si riprende in meno " + "di un minuto.", True),
    ("Di solito si riprende in fretta. Se non si riprende, chiama il 112.", False),
    ("mettilo in un sacchetto pulito e chiuso, e il sacchetto " + "nel ghiaccio.", True),
    ("in a clean, sealed bag, and the bag " + "in ice.", True),
    ("in un sacchetto chiuso, dentro un altro sacchetto con acqua e ghiaccio.", False),
    ("Porta con te la confezione, o una batteria " + "uguale: aiuta i medici.", True),
    ("Bring the **packaging** or an identical " + "battery.", True),
    ("Apri porte e finestre " + "ed esci all'aria aperta.", True),
    ("Esci subito all'aria aperta. Se puoi farlo senza fermarti, apri le finestre.", False),
    ("vista annebbiata e un ronzio " + "nelle orecchie", True),
    ("blurred vision, ringing " + "in the ears", True),
    ("o se mano o piede " + "sono freddi e senza sensibilità", True),
    ("or a hand or foot " + "that is cold and numb", True),
    ("una luce notturna verso il bagno, pantofole chiuse", False),
]

errori = 0
for testo, atteso in CASI:
    segnalato = any(rx.search(testo) for rx, _ in FORME_SBAGLIATE)
    if segnalato != atteso:
        errori += 1
        print(f"❌ {testo!r}: {'segnalato' if segnalato else 'non segnalato'}, atteso il contrario")
print(f"{len(CASI) - errori}/{len(CASI)} casi come previsto")
sys.exit(1 if errori else 0)
