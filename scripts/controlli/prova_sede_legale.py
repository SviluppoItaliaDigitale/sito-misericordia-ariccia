#!/usr/bin/env python3
"""Le tre sedi della Misericordia di Ariccia (Alessandro, 18/11/2026 e 21/11/2026, «una volta per tutte»):
- sede legale, via Beata Rosa Venerini 6: MAI sul sito né sui social; solo nella modulistica (carta intestata e moduli),
  sempre insieme alla sede amministrativa e a quella operativa. Altrove il controllo diventa rosso;
- sede amministrativa, viale Antonietta Chigi 46: iscrizioni, corsi, Servizio Civile, Banco alimentare, Centro di Ascolto;
- sede operativa, piazzale Aldo Moro 6: dove stanno i mezzi, per trasporti sanitari e servizi, con il cellulare 348 4068657;
  il fisso 06 933 3717 e il 328 8105399 sono della sede amministrativa. Non va negli inviti a
  iscriversi o a passare per diventare volontari (riga con «Aldo Moro» e «passa a trovarci» o «iscriv» senza «Chigi»).
Solo libreria standard."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AMMESSI = {"hugo.toml", "README.md", "data/dati_da_verificare.yaml",       # file interni, non pubblicati
           "scripts/controlli/prova_sede_legale.py", "scripts/controlli/controlla_fogli_kit.py"}  # la cercano
MODULISTICA = {"scripts/grafica-brand/modelli-nazionali/carta-intestata.html"}  # con le altre due sedi accanto
CARTELLE = ("content", "layouts", "static", "data", "scripts", "assets", "i18n")
import re
trovati, sedi = [], []
INVITO = re.compile(r"passa(?:te)? a trovarci|iscriv|iscrizion|Servizio Civile|Banco alimentare|Centro di Ascolto|corsi", re.I)
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
            if rel in MODULISTICA:
                if not ("Chigi" in t and "Aldo Moro" in t):
                    trovati.append(rel + " (modulistica: la sede legale va sempre con la sede amministrativa e l'operativa)")
            else:
                trovati.append(rel)
        for n, riga in enumerate(t.splitlines(), 1):
            if "Aldo Moro" in riga and INVITO.search(riga) and "Chigi" not in riga and "operativ" not in riga:
                sedi.append(f"{rel}:{n}")
            # il fisso 06 933 3717 è della sede amministrativa, non dell'operativa (Alessandro, 21/11/2026)
            if re.search(r"933 ?3717|069333717", riga) and re.search(r"[Ss]ede operativa|Operations base|Operational office", riga) \
                    and not re.search(r"amministrativ|Administrative", riga) and rel != "scripts/controlli/prova_sede_legale.py":
                sedi.append(f"{rel}:{n} (fisso accanto alla sede operativa)")
if sedi:
    print("La sede operativa (Aldo Moro, i mezzi) compare in un invito a iscriversi o ai corsi: lì va la sede "
          "amministrativa di viale Antonietta Chigi 46:\n- " + "\n- ".join(sedi))
    sys.exit(1)
if trovati:
    print("La sede legale compare fuori dalla modulistica (sul sito e sui social non va mai; usa viale Antonietta Chigi 46):\n- "
          + "\n- ".join(trovati))
    sys.exit(1)
print("Sedi: legale solo nella modulistica con le altre due sedi, mai su sito e social; nessun invito a iscriversi verso la sede operativa.")
