#!/usr/bin/env python3
"""Fa il pacchetto ZIP di ogni fascia dei materiali per le scuole (come i «pacchetti offline» dei kit della
Protezione Civile di Genzano): static/documenti/scuole/<fascia>/pacchetto-<fascia>.zip con le schede, le guide,
le slide in PDF 16:9 e 4:3 e i PowerPoint 16:9, più un LEGGIMI.txt. Lascia fuori i materiali con
revisione: "da fare" (ancora in revisione sanitaria) e i PDF 4K, che si scaricano a parte.
Uso: python3 scripts/scuole/pacchetti.py   (dopo rendi_pdf.py, prima del commit)"""
import re
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
NOMI = {"infanzia": "scuola dell'infanzia", "primaria": "scuola primaria",
        "medie": "scuola secondaria di primo grado", "superiori": "scuola secondaria di secondo grado"}

for pagina in sorted((REPO / "content/scuole").glob("*.md")):
    fascia = pagina.stem
    if fascia not in NOMI:
        continue
    fm = pagina.read_text(encoding="utf-8").split("---")[1]
    blocco = re.search(r"^materiali:\n((?:[ -].*\n)+)", fm, re.M).group(1)
    file, righe = [], []
    for voce in re.split(r"^  - ", blocco, flags=re.M)[1:]:
        if re.search(r'revisione:\s*"da fare"', voce):
            continue
        rel = re.search(r'file:\s*"?([^"\n]+)"?', voce).group(1).strip()
        titolo = re.search(r'titolo:\s*"([^"]+)"', voce).group(1)
        pdf = REPO / "static" / rel.lstrip("/")
        altri = [pdf]
        if re.search(r'tipo:\s*"?slide', voce):
            altri += [pdf.with_suffix(".pptx"), pdf.with_name(pdf.stem + "-4x3.pdf")]
        for f in altri:
            if f.exists():
                file.append(f)
        righe.append(f"- {titolo}: {', '.join(f.name for f in altri if f.exists())}")
    dest = REPO / f"static/documenti/scuole/{fascia}/pacchetto-{fascia}.zip"
    leggimi = (f"Materiali per la {NOMI[fascia]} - Confraternita di Misericordia di Ariccia ODV\n"
               f"www.misericordia-ariccia.it/scuole/{fascia}/ - sede@misericordia-ariccia.it\n\n"
               "Gratuiti, da stampare e usare in classe così come sono.\n"
               "Le slide sono in PDF 16:9 (LIM e monitor di oggi) e 4:3 (LIM con proiettore); nel PowerPoint ci sono\n"
               "le note per chi presenta. Altri formati (4K, 16:10) e le istruzioni per la LIM: www.misericordia-ariccia.it/lim/\n\n"
               + "\n".join(righe) + "\n")
    # data fissa nei file dello ZIP: a contenuto uguale lo ZIP è identico, così la pubblicazione su Aruba
    # (che carica solo i file cambiati) non lo ricarica a ogni build
    def info(nome):
        zi = zipfile.ZipInfo(nome, date_time=(2026, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        return zi
    with zipfile.ZipFile(dest, "w") as z:
        z.writestr(info("LEGGIMI.txt"), leggimi)
        for f in file:
            z.writestr(info(f.name), f.read_bytes())
    print(f"{dest.relative_to(REPO)}: {len(file)} file, {dest.stat().st_size / 1e6:.1f} MB")
