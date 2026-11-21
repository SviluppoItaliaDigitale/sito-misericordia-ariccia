#!/usr/bin/env python3
"""pubblica-puntata.py — Pubblica una puntata che ha superato il controllo e la mette nel calendario dei social.

Adattato dal podcast della Protezione Civile di Genzano. Ricodifica l'audio
(AAC 64 kbps mono, senza metadati né firma dell'encoder), scrive
content/podcast/<oggi>-<id>.md con la trascrizione verificata come corpo e le pagine fonte
in fondo, e segna la voce «programmata» in coda.yaml. Dal 21/11/2026 (scelta di Alessandro:
«i podcast già pronti me li devi già pubblicare immediatamente sul sito, mentre sui social
rimane il calendario») la puntata esce sul sito subito, al primo deploy, e sui social il
primo mercoledì o sabato libero, scritto in «social_data:» (scripts/pubblica_social.py).
Fa anche la grafica dei social (scripts/grafica-brand/podcast/rendi-post.py).
Uso: pubblica-puntata.py ID AUDIO TRASCRIZIONE_VERIFICATA.md [--descrizione "…"]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

import yaml

RADICE = Path(__file__).resolve().parents[2]
CODA = Path(__file__).with_name("coda.yaml")
PODCAST = RADICE / "content" / "podcast"
EPISODI = RADICE / "static" / "podcast" / "episodi"


def secondi(file: Path) -> int:
    return int(round(float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(file)], text=True).strip())))


def durata(sec: int) -> str:
    """Durata da leggere in pagina; il feed usa i secondi (durata_secondi)."""
    return f"{sec // 60} min {sec % 60:02d} s"


def prossimo_episodio() -> int:
    numeri = []
    for f in PODCAST.glob("*.md"):
        testo = f.read_text(encoding="utf-8")
        if "render: never" in testo or f.name == "_index.md":
            continue
        m = re.search(r"^episodio:\s*(\d+)", testo, re.M)
        if m:
            numeri.append(int(m.group(1)))
    return max(numeri, default=0) + 1


def frontmatter(rel: str) -> dict:
    testo = (RADICE / rel).read_text(encoding="utf-8")
    m = re.match(r"\A---\n(.*?)\n---\n", testo, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def titolo_pagina(rel: str) -> str:
    return str(frontmatter(rel).get("title", Path(rel).stem)).replace("[", "(").replace("]", ")")


def percorso_pagina(rel: str) -> str:
    """Percorso pubblico della pagina, come lo costruisce Hugo (url, slug, file)."""
    fm = frontmatter(rel)
    if fm.get("url"):
        return "/" + str(fm["url"]).strip("/") + "/"
    p = Path(rel).relative_to("content")
    parti = list(p.parent.parts) if p.name == "_index.md" else list(p.with_suffix("").parts)
    if fm.get("slug") and p.name != "_index.md":
        parti[-1] = str(fm["slug"])
    return "/" + "/".join(parti) + "/"


GIORNI_USCITA = (2, 5)  # mercoledì e sabato


def date_programmate() -> list[date]:
    """Date del calendario dei social delle puntate attive («social_data:», altrimenti la data)."""
    out = []
    for f in PODCAST.glob("*.md"):
        testo = f.read_text(encoding="utf-8")
        if f.name == "_index.md" or "render: never" in testo:
            continue
        m = (re.search(r'^social_data:\s*"?(\d{4}-\d{2}-\d{2})', testo, re.M)
             or re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", testo, re.M))
        if m:
            out.append(date.fromisoformat(m.group(1)))
    return out


def prossima_uscita() -> date:
    """Primo mercoledì o sabato libero dopo oggi e dopo l'ultima in calendario."""
    giorno = max([date.today()] + date_programmate()) + timedelta(days=1)
    while giorno.weekday() not in GIORNI_USCITA:
        giorno += timedelta(days=1)
    return giorno


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("audio")
    ap.add_argument("trascrizione")
    ap.add_argument("--descrizione", required=True)
    ap.add_argument("--oggi", action="store_true", help="anche sui social oggi, invece che al primo mercoledì o sabato libero")
    a = ap.parse_args()

    dati = yaml.safe_load(CODA.read_text(encoding="utf-8"))
    voce = next((v for v in dati["puntate"] if v["id"] == a.id), None)
    if not voce:
        print(f"ERRORE: {a.id} non è in coda.yaml", file=sys.stderr)
        return 1
    adesso = datetime.now(ZoneInfo("Europe/Rome")).replace(microsecond=0)
    oggi = adesso.date().isoformat()
    social = (adesso.date() if a.oggi else prossima_uscita()).isoformat()
    slug = f"{oggi}-{a.id}"
    if (PODCAST / f"{slug}.md").exists():
        print(f"ERRORE: esiste già content/podcast/{slug}.md", file=sys.stderr)
        return 1
    EPISODI.mkdir(parents=True, exist_ok=True)
    audio_out = EPISODI / f"{slug}-podcast.m4a"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", a.audio, "-vn", "-ac", "1",
         "-c:a", "aac", "-b:a", "64k", "-map_metadata", "-1", "-fflags", "+bitexact",
         "-flags:a", "+bitexact", "-movflags", "+faststart", str(audio_out)],
        check=True)

    corpo = Path(a.trascrizione).read_text(encoding="utf-8").strip()
    if re.search(r"(?i)notebook|intelligenza artificiale|\bgenerat[oa] (con|da)\b", corpo):
        print("ERRORE: la trascrizione nomina uno strumento o l'intelligenza artificiale", file=sys.stderr)
        return 1
    fonti = "\n".join(f"- [{titolo_pagina(f)}]({percorso_pagina(f)})" for f in voce["fonti"])
    episodio = prossimo_episodio()
    titolo = voce["titolo"].replace('"', "'")
    descr = a.descrizione.replace('"', "'")
    testo = f"""---
title: "{titolo}"
date: {(adesso - timedelta(minutes=5)).isoformat()}
social_data: "{social}"
description: "{descr}"
episodio: {episodio}
audio: "/podcast/episodi/{audio_out.name}"
durata: "{durata(secondi(audio_out))}"
durata_secondi: {secondi(audio_out)}
italianoSemplice: |
  **Questa è una puntata del podcast della Misericordia di Ariccia.**

  Puoi ascoltarla. Sotto c'è tutto il testo della puntata.

  In fondo trovi le pagine del sito da leggere.

  In emergenza chiama il **112**.
draft: false
---

{corpo}

## Per approfondire sul nostro sito

{fonti}

In emergenza chiama il **112**. La Misericordia di Ariccia fa trasporti programmati, non soccorso d'emergenza.
"""
    (PODCAST / f"{slug}.md").write_text(testo, encoding="utf-8")

    voce["stato"] = "programmata"
    voce["file"] = f"content/podcast/{slug}.md"
    voce["data"] = oggi
    voce["social_data"] = social
    CODA.write_text(
        CODA.read_text(encoding="utf-8").split("puntate:")[0]
        + yaml.safe_dump({"puntate": dati["puntate"]}, allow_unicode=True, sort_keys=False),
        encoding="utf-8")

    grafica = subprocess.run(["python3", str(RADICE / "scripts/grafica-brand/podcast/rendi-post.py"),
                              str(PODCAST / f"{slug}.md")])
    if grafica.returncode:
        print("ERRORE: grafica dei social non riuscita (rendi-post.py): senza grafica Instagram non pubblica",
              file=sys.stderr)
        return 1
    print(f"PROGRAMMATA content/podcast/{slug}.md episodio {episodio}: sul sito da oggi, sui social il {social}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
