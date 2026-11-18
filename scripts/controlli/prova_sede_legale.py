#!/usr/bin/env python3
"""La sede legale (via Beata Rosa Venerini) non va mai nei contenuti operativi (Alessandro, 18/11/2026: «Quella è la
sede legale!! NON VA MAI MENZIONATA NELLE COSE OPERATIVE! LA SEDE STA IN VIA CHIGI»). Ammessa solo nelle pagine e
nei file per atti, privacy e trasparenza elencati qui; altrove il controllo diventa rosso. Solo libreria standard."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AMMESSI = {"content/contatti.md", "content/privacy.md", "content/trasparenza.md", "hugo.toml", "README.md",
           "layouts/_default/baseof.html", "data/dati_da_verificare.yaml", "scripts/controlli/prova_sede_legale.py"}
CARTELLE = ("content", "layouts", "static", "data", "scripts", "assets", "i18n")
trovati = []
for c in CARTELLE:
    for f in (REPO / c).rglob("*"):
        if not f.is_file() or f.suffix not in {".md", ".html", ".toml", ".yaml", ".yml", ".json", ".js", ".py", ".txt", ".css"}:
            continue
        rel = f.relative_to(REPO).as_posix()
        if rel in AMMESSI or "/out/" in rel:
            continue
        try:
            t = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "Venerini" in t:
            trovati.append(rel)
if trovati:
    print("La sede legale compare in contenuti operativi (usa viale Antonietta Chigi 46, site.Params.indirizzo):\n- "
          + "\n- ".join(trovati))
    sys.exit(1)
print("Sede legale: solo nelle pagine per atti, privacy e trasparenza.")
