#!/usr/bin/env python3
"""Prova del calendario della «Parola» (domeniche e feste, dal 31/10/2026), sui controlli di ogni PR.

Controlla che scripts/parola-domenica/calendario.json copra almeno i prossimi 180 giorni (se no:
«calendario.py aggiorna»), che dia le date giuste in casi noti verificati su LitCal (spostamenti
compresi), che ogni scheda in .github/social/parola/ cada in un giorno della Parola con il titolo
giusto e che il testo dei post di una festa non parli di «domenica». Esce con 1 se un caso non va.
Solo libreria standard.
"""
import datetime as dt
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "scripts" / "parola-domenica"))
import calendario as cal  # noqa: E402
import pubblica_social as ps  # noqa: E402

falliti = []


def attesa(cond, messaggio):
    if not cond:
        falliti.append(messaggio)


c = cal.carica()
oggi = cal.oggi_roma()
attesa(cal.copertura(c) >= oggi + dt.timedelta(days=180),
       f"calendario.json copre solo fino al {cal.copertura(c)}: lanciare «calendario.py aggiorna»")

# casi verificati su LitCal (calendario italiano) il 31/10/2026
NOTI = {
    "2026-11-01": cal.DOMENICA,           # Tutti i Santi di domenica: resta la domenica
    "2026-11-02": cal.GIORNO,             # Commemorazione dei defunti
    "2026-12-08": cal.FESTA, "2026-12-25": cal.FESTA, "2026-12-26": cal.FESTA,
    "2027-01-06": cal.FESTA, "2027-02-10": cal.GIORNO, "2027-03-25": cal.GIORNO, "2027-03-26": cal.GIORNO,
    "2027-04-05": cal.FESTA,              # Annunciazione spostata dopo l'Ottava di Pasqua
    "2027-06-04": cal.FESTA,              # Sacro Cuore
    "2028-03-20": cal.FESTA,              # San Giuseppe spostato: il 19 è una domenica di Quaresima
}
for data, titolo in NOTI.items():
    if dt.date.fromisoformat(data) > cal.copertura(c):
        continue
    g = cal.giorno_della_parola(dt.date.fromisoformat(data), c)
    attesa(g and g["titolo"] == titolo, f"{data}: atteso «{titolo}», trovato {g}")
for data in ("2026-11-03", "2027-03-24", "2027-03-29", "2027-03-27"):  # feria, Settimana santa, Ottava, Veglia
    attesa(cal.giorno_della_parola(dt.date.fromisoformat(data), c) is None, f"{data}: non è un giorno della Parola")
attesa(all(dt.date.fromisoformat(d).isoweekday() != 7 for d in c["feste"]), "una festa di domenica in calendario.json")

for f in sorted((REPO / ".github/social/parola").glob("*.json")):
    s = json.loads(f.read_text(encoding="utf-8"))
    giorno = dt.date.fromisoformat(s["data"])
    attesa(f.stem == s["data"], f"{f.name}: la data della scheda è {s['data']}")
    if giorno.year < min(c["anni"]):
        continue
    g = cal.giorno_della_parola(giorno, c)
    attesa(g is not None, f"{f.name}: il {giorno} non è un giorno della Parola")
    if g:
        attesa(ps.titolo_parola(s) == g["titolo"], f"{f.name}: titolo «{ps.titolo_parola(s)}», in calendario «{g['titolo']}»")

festa = {"data": "2026-12-08", "titolo": cal.FESTA, "giorno_liturgico": "Immacolata Concezione della Beata Vergine Maria",
         "testo_social": "Prova.", "opera": None,
         "pagine": [{"lettura": "Vangelo", "riferimento": "Lc 1,28", "versetto": "Rallègrati, piena di grazia: il Signore è con te."}]}
for rete in ("facebook", "instagram"):
    t = ps.testo_parola(festa, rete)
    attesa(t.startswith("📖 La Parola della festa · Immacolata") and "letture di oggi" in t and "domenica" not in t.lower(),
           f"post {rete} di una festa: titolo, rimando o «domenica» sbagliati:\n{t}")
attesa(ps.testo_parola(festa, "instagram").endswith(ps.HASHTAG_PAROLA_FESTA), "festa senza #VangeloDelGiorno")
attesa(ps.alt_parola(festa)[-1].startswith("Vangelo, Lc 1,28"), "testo alternativo della festa sbagliato")

if falliti:
    print("Prova del calendario della Parola NON superata:")
    for x in falliti:
        print(" -", x)
    sys.exit(1)
print(f"Prova del calendario della Parola superata: copertura fino al {cal.copertura(c)}, {len(NOTI)} date note, schede coerenti, testo delle feste.")
