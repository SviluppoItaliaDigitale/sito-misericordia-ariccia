#!/usr/bin/env python3
"""trova-fonti.py — Elenca le pagine pubblicate del sito su un tema della coda.

Adattato dal podcast della Protezione Civile di Genzano. Usa «fonti» (sempre
incluse) e «parole» di coda.yaml: cerca nelle pagine e nelle news già online
(data passata, niente bozze, pagine inglesi, spagnole, rumene, podcast, pagine
legali, news d'archivio più vecchie di un anno) quelle che hanno le parole nel
titolo (la descrizione conta solo per l'ordine), e stampa gli indirizzi da dare
a NotebookLM (al massimo --max). Scrive ~/podcast-lavoro-misericordia/<id>/fonti.txt
e fonte.md (testo delle pagine PUBBLICATE, per il controllo dei fatti).
Esce con 3 se una fonte fissa non è ancora pubblicata (data futura): la puntata
resta «da-fare» e si passa alla successiva.
Uso: trova-fonti.py ID [--max 12]
"""
from __future__ import annotations

import argparse
from html import unescape
import re
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import yaml

RADICE = Path(__file__).resolve().parents[2]
SITO = "https://www.misericordia-ariccia.it"
LAVORO = Path.home() / "podcast-lavoro-misericordia"
# Prime cartelle o pagine di content/ che non sono mai fonti.
ESCLUSE = ("en", "podcast", "privacy", "accessibilita", "mappa-del-sito", "liturgia-del-giorno",
           "crediti-fotografici", "espanol", "romana", "lim", "contatti-rapidi", "lo-sapevi-che")


def frontmatter(p: Path) -> dict:
    t = p.read_text(encoding="utf-8")
    m = re.match(r"\A---\n(.*?)\n---\n", t, re.S)
    try:
        return (yaml.safe_load(m.group(1)) or {}) if m else {}
    except yaml.YAMLError:
        return {}


def giorno(d) -> date | None:
    if not d:
        return None
    if hasattr(d, "date") and callable(d.date):
        return d.date()
    if isinstance(d, date):
        return d
    try:
        return date.fromisoformat(str(d)[:10])
    except ValueError:
        return None


def url(p: Path) -> str:
    """Indirizzo pubblico della pagina, come lo costruisce Hugo (url, slug, percorso)."""
    fm = frontmatter(p)
    if fm.get("url"):
        return SITO + "/" + str(fm["url"]).strip("/") + "/"
    rel = p.relative_to(RADICE / "content")
    if rel.name == "_index.md":
        parti = list(rel.parent.parts)
    else:
        parti = list(rel.with_suffix("").parts)
        if fm.get("slug"):
            parti[-1] = str(fm["slug"])
    return f"{SITO}/{'/'.join(parti)}/"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--max", type=int, default=12)
    a = ap.parse_args()
    coda = yaml.safe_load((Path(__file__).with_name("coda.yaml")).read_text(encoding="utf-8"))["puntate"]
    voce = next((v for v in coda if v["id"] == a.id), None)
    if not voce:
        print(f"ERRORE: {a.id} non è in coda", file=sys.stderr)
        return 1
    escludi = voce.get("escludi", [])
    parole = [re.compile(r"\b" + re.escape(w), re.I) for w in voce.get("parole", [])]
    oggi = date.today()
    fisse = [RADICE / f for f in voce["fonti"]]
    for p in fisse:
        if not p.exists():
            print(f"ERRORE: fonte mancante {p.relative_to(RADICE)}", file=sys.stderr)
            return 1
        fm = frontmatter(p)
        d = giorno(fm.get("date"))
        if fm.get("draft") or (d and d > oggi):
            print(f"NON ANCORA PUBBLICATA: {p.relative_to(RADICE)} (data {d}): la puntata resta da fare",
                  file=sys.stderr)
            return 3
    trovate = []
    for p in sorted((RADICE / "content").rglob("*.md")):
        rel = p.relative_to(RADICE / "content").as_posix()
        primo = rel.split("/")[0].removesuffix(".md")
        if p in fisse or primo in ESCLUSE or any(e in rel for e in escludi):
            continue
        fm = frontmatter(p)
        if fm.get("draft") or (fm.get("build") or {}).get("render") == "never":
            continue
        d = giorno(fm.get("date"))
        if d and d > oggi:
            continue
        if primo == "news" and d and d < oggi - timedelta(days=365):
            continue  # le news d'archivio parlano di corsi ed eventi conclusi
        titolo = str(fm.get("title", ""))
        descr = str(fm.get("description", ""))
        nel_titolo = sum(3 for r in parole if r.search(titolo))
        if not nel_titolo:
            continue  # la parola deve stare nel titolo: la sola descrizione porta pagine generiche
        punti = nel_titolo + sum(1 for r in parole if r.search(descr))
        if primo != "news":
            punti += 5  # pagine stabili prima degli articoli
        trovate.append((punti, str(d or ""), p))
    trovate.sort(key=lambda x: (-x[0], x[1]))
    scelte = fisse + [p for _, _, p in trovate[: max(0, a.max - len(fisse))]]
    indirizzi = [url(p) for p in scelte]
    dest = LAVORO / a.id
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "fonti.txt").write_text("\n".join(indirizzi) + "\n", encoding="utf-8")
    # Il testo per il controllo dei fatti è quello delle pagine PUBBLICATE, cioè
    # esattamente ciò che legge NotebookLM: i file .md non hanno i riquadri dei
    # layout (schede del dossier, numeri utili). Lezione del 15/11/2026 della PC.
    testo = []
    for u in indirizzi:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        html = ""
        for _ in range(3):  # i 503 intermittenti sono l'anti-bot di Aruba: si riprova
            try:
                html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
                break
            except OSError as e:
                errore = e
        if not html:
            print(f"ERRORE: fonte non raggiungibile {u}: {errore}", file=sys.stderr)
            return 1
        html = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", html)
        corpo = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()
        testo.append(f"===== {u}\n" + unescape(corpo).replace("\xa0", " "))
    (dest / "fonte.md").write_text("\n\n".join(testo) + "\n", encoding="utf-8")
    for u in indirizzi:
        print(u)
    print(f"# {len(scelte)} fonti ({len(trovate)} pagine pertinenti trovate)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
