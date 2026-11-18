#!/usr/bin/env python3
"""Importa i «kit calamità» del sito della Protezione Civile di Genzano di Roma (stesso autore, contenuti
CC BY-NC-SA 4.0) nella sezione /kit/ del sito della Misericordia di Ariccia (18/11/2026, Alessandro: «Crea anche
i kit, puoi copiarli»). Copia pagine e schede stampabili, cambia percorsi, intestazione, colori, recapiti e firma;
i testi poi si rileggono a mano (vedi scripts/kit/LEGGIMI.md). Uso: python3 scripts/kit/importa_da_pc.py PERCORSO_REPO_PC"""
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PC = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/iu0qvw/sito-pc-genzano")
DST_S, DST_C = REPO / "static/kit", REPO / "content/kit"


def nome(d: str) -> str:
    if d == "kit-calamita":
        return ""
    if d == "kit-calamita-shared":
        return "comune"
    return d.removeprefix("kit-calamita-").removeprefix("kit-")


def percorsi(t: str) -> str:
    t = re.sub(r"/formazione/(kit-calamita[a-z-]*|kit-fragilita-vulnerabilita)/",
               lambda m: "/kit/" + (nome(m.group(1)) + "/" if nome(m.group(1)) else ""), t)
    t = t.replace("../kit-calamita-shared/", "../comune/")
    t = re.sub(r"\.\./(kit-calamita-[a-z-]+|kit-fragilita-vulnerabilita)/", lambda m: "../" + nome(m.group(1)) + "/", t)
    t = t.replace("https://www.protezionecivilegenzano.it/kit/", "https://www.misericordia-ariccia.it/kit/")
    t = t.replace("segreteria@protezionecivilegenzano.it", "sede@misericordia-ariccia.it")
    return t


LOGO = ('<img class="logo" src="/kit/comune/triangolo-misericordie.png" alt="Logo delle Misericordie">'
        '<div class="brand">Misericordia di Ariccia<small>Confraternita di Misericordia di Ariccia ODV</small></div>')


def scheda(t: str) -> str:
    t = percorsi(t)
    t = re.sub(r'<link rel="canonical" href="https://www\.protezionecivilegenzano\.it/formazione/',
               '<link rel="canonical" href="https://www.misericordia-ariccia.it/formazione/', t)
    t = re.sub(r'<svg class="logo".*?</svg>\s*<div class="brand">.*?</div>', LOGO, t, flags=re.S)
    t = t.replace("www.protezionecivilegenzano.it</span>", "www.misericordia-ariccia.it · adattato da materiali della Protezione Civile di Genzano di Roma, CC BY-NC-SA 4.0</span>")
    return t


DST_S.mkdir(parents=True, exist_ok=True)
DST_C.mkdir(parents=True, exist_ok=True)
for d in sorted(list((PC / "static/formazione").glob("kit-calamita*")) + [PC / "static/formazione/kit-fragilita-vulnerabilita"]):
    if not d.is_dir():
        continue
    dest = DST_S / nome(d.name) if nome(d.name) else DST_S / "calamita"
    for f in d.rglob("*"):
        if f.is_dir():
            continue
        out = dest / f.relative_to(d)
        out.parent.mkdir(parents=True, exist_ok=True)
        if f.suffix == ".html":
            out.write_text(scheda(f.read_text(encoding="utf-8")), encoding="utf-8")
        elif f.suffix == ".css":
            out.write_text(f.read_text(encoding="utf-8").replace("#003366", "#003F85").replace("#001a33", "#002f63"), encoding="utf-8")
        else:
            shutil.copy2(f, out)
for d in sorted(list((PC / "content/formazione").glob("kit-calamita*")) + [PC / "content/formazione/kit-fragilita-vulnerabilita"]):
    src = d / "_index.md"
    if not src.exists():
        continue
    n = nome(d.name)
    out = DST_C / ("_index.md" if not n else f"{n}/_index.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(percorsi(src.read_text(encoding="utf-8")), encoding="utf-8")
shutil.copy2(REPO / "scripts/grafica-brand/modelli-nazionali/loghi/triangolo-misericordie.png", DST_S / "comune/triangolo-misericordie.png")
print("importati:", sorted(p.name for p in DST_S.iterdir()))
