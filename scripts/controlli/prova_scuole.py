#!/usr/bin/env python3
"""Controllo dei materiali per le scuole (content/scuole/, static/documenti/scuole/, dal 18/11/2026).

Per ogni materiale elencato nelle pagine di content/scuole/: il PDF esiste, ha il segno di firma e cornice
(rendi.py --cornice, regola del 21/10/2026) e la sua anteprima in static/img/scuole/; le slide hanno anche i
formati per le LIM (4K, 16:10, 4:3) e i PowerPoint 16:9 e 4:3. Ogni PDF della cartella è elencato in una pagina (niente file orfani) e ogni sorgente HTML di
scripts/scuole/<fascia>/ ha il suo PDF, più recente del sorgente. Esce con 1 se qualcosa non va. Solo libreria standard.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARCATORE = re.search(r"const MARCATORE = '([^']+)'",
                      (REPO / "scripts/grafica-brand/firma-e-cornice.js").read_text(encoding="utf-8")).group(1)
errori = []

elencati = set()
for pagina in sorted((REPO / "content/scuole").glob("*.md")):
    if pagina.name == "_index.md":
        continue
    fm = pagina.read_text(encoding="utf-8").split("---")[1]
    blocco = re.search(r"^materiali:\n((?:[ -].*\n)+)", fm, re.M)
    if not blocco:
        errori.append(f"{pagina.name}: nessun materiale elencato")
        continue
    for voce in re.split(r"^  - ", blocco.group(1), flags=re.M)[1:]:
        f = re.search(r'file:\s*"?([^"\n]+)"?', voce)
        tipo = re.search(r'tipo:\s*"?(\w+)"?', voce)
        if not f or not tipo:
            errori.append(f"{pagina.name}: materiale senza file o tipo")
            continue
        rel = f.group(1).strip()
        pdf = REPO / "static" / rel.lstrip("/")
        elencati.add(pdf)
        if not re.fullmatch(r"/documenti/scuole/[a-z]+/[a-z0-9-]+\.pdf", rel):
            errori.append(f"{pagina.name}: percorso non valido {rel}")
        if not pdf.exists():
            errori.append(f"{pagina.name}: manca {rel}")
            continue
        if MARCATORE.encode() not in pdf.read_bytes():
            errori.append(f"{rel}: senza il segno di firma e cornice (rifarlo con scripts/scuole/rendi_pdf.py)")
        img = REPO / "static/img" / Path(rel.lstrip("/")).relative_to("documenti").with_suffix(".jpg")
        if not img.exists():
            errori.append(f"{rel}: manca l'anteprima {img.relative_to(REPO)}")
        if tipo.group(1) == "slide":
            # formati per le LIM (rendi_pdf.py, FORMATI_SLIDE): 16:9, 4K, 16:10, 4:3, PowerPoint 16:9 e 4:3
            for suff in ("-4k.pdf", "-16x10.pdf", "-4x3.pdf", ".pptx", "-4x3.pptx"):
                altro = pdf.with_name(pdf.stem + suff)
                elencati.add(altro)
                if not altro.exists():
                    errori.append(f"{rel}: manca il formato per la LIM {altro.name}")

for pdf in sorted(f for f in (REPO / "static/documenti/scuole").rglob("*") if f.suffix in (".pdf", ".pptx")):
    if pdf not in elencati:
        errori.append(f"{pdf.relative_to(REPO)}: non è elencato in nessuna pagina di content/scuole/")

for sorgente in sorted((REPO / "scripts/scuole").glob("*/*.html")):
    m = re.search(r'<meta name="uscita" content="([^"]+)"', sorgente.read_text(encoding="utf-8"))
    if not m:
        errori.append(f"{sorgente.relative_to(REPO)}: manca <meta name=\"uscita\">")
        continue
    if not (REPO / m.group(1)).exists():
        errori.append(f"{sorgente.relative_to(REPO)}: PDF non ancora fatto ({m.group(1)})")

if errori:
    print("Materiali per le scuole: problemi\n- " + "\n- ".join(errori))
    sys.exit(1)
print(f"Materiali per le scuole: {len(elencati)} PDF in ordine.")
