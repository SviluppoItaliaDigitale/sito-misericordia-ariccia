#!/usr/bin/env python3
"""Le tre sedi della Misericordia di Ariccia (Alessandro, 18/11/2026 e 21/11/2026, «una volta per tutte»):
- sede legale, via Beata Rosa Venerini 6: solo carta intestata e fiscalità (con le pagine di atti, privacy e trasparenza
  elencate qui); altrove il controllo diventa rosso;
- sede amministrativa, viale Antonietta Chigi 46: iscrizioni, corsi, Servizio Civile, Banco alimentare, Centro di Ascolto;
- sede operativa, piazzale Aldo Moro 6: dove stanno i mezzi, per trasporti sanitari e servizi. Non va negli inviti a
  iscriversi o a passare per diventare volontari (riga con «Aldo Moro» e «passa a trovarci» o «iscriv» senza «Chigi»).
Solo libreria standard."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AMMESSI = {"content/contatti.md", "content/privacy.md", "content/trasparenza.md", "hugo.toml", "README.md",
           "layouts/_default/baseof.html", "data/dati_da_verificare.yaml", "scripts/controlli/prova_sede_legale.py",
           "scripts/controlli/controlla_fogli_kit.py",
           "scripts/grafica-brand/modelli-nazionali/carta-intestata.html"}   # carta intestata: sede legale (21/11/2026)   # i due controlli devono nominarla per cercarla
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
            trovati.append(rel)
        for n, riga in enumerate(t.splitlines(), 1):
            if "Aldo Moro" in riga and INVITO.search(riga) and "Chigi" not in riga and "operativ" not in riga:
                sedi.append(f"{rel}:{n}")
if sedi:
    print("La sede operativa (Aldo Moro, i mezzi) compare in un invito a iscriversi o ai corsi: lì va la sede "
          "amministrativa di viale Antonietta Chigi 46:\n- " + "\n- ".join(sedi))
    sys.exit(1)
if trovati:
    print("La sede legale compare in contenuti operativi (usa viale Antonietta Chigi 46, site.Params.indirizzo):\n- "
          + "\n- ".join(trovati))
    sys.exit(1)
print("Sedi: legale solo in carta intestata, fiscalità, atti, privacy e trasparenza; nessun invito a iscriversi verso la sede operativa.")
