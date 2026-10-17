#!/usr/bin/env python3
"""Legge il rapporto markdown di lychee e fallisce se un link del sito risponde 404/410
o punta a un file che nel sito compilato non esiste; scrive il corpo della issue «Link rotti sul sito».

Istruzione di Alessandro del 17/10/2026: «gli errori 404 e simili non devono mai essere
ignorati e devono essere risolti... vale per tutti i link del sito». Lychee gira con
`fail: false` perché timeout, errori 5xx e blocchi anti-bot sono quasi sempre passeggeri:
quelli restano nella sezione informativa della issue. Un 404/410, o un file interno
mancante, invece è una pagina spostata o un errore nostro, e rende rosso il run.
Adattato da scripts/check-404-istituzionali.py del sito della Protezione Civile di Genzano.

Uso:  python3 scripts/controlla-link-rotti.py lychee-report.md [--corpo corpo-issue.md]
Exit: 0 se nessun link rotto, 1 altrimenti (elenco su stdout e nel corpo della issue).
"""
import argparse
import re
import sys
from urllib.parse import unquote, urlparse

# Domini di enti pubblici, elencati per primi: sono le fonti ufficiali promesse ai lettori.
SCHEMI_PUBBLICI = re.compile(
    r"(\.gov\.it|\.europa\.eu|\.gov|\.int|\.edu\.it"
    r"|(^|\.)regione\.[a-z-]+\.it|(^|\.)comune\.[a-z-]+\.[a-z.]+"
    r"|(^|\.)(sanita|salute)\.[a-z-]+\.it|(^|\.)(asl|ausl|aou|arpa|ares)[a-z0-9-]*\.[a-z.]*it)$"
)
ENTI_PUBBLICI = {
    "normattiva.it", "gazzettaufficiale.it", "camera.it", "senato.it", "quirinale.it",
    "garanteprivacy.it", "protezionecivile.it", "iss.it", "istat.it", "inps.it", "inail.it",
    "aslroma6.it", "salutelazio.it", "112lazio.it", "areslazio.it",
}

SEZIONE = re.compile(r"^### Errors in (.+)$")
RIGA = re.compile(r"^\* \[([^\]]+)\] <([^>]+)>[^|]*\|\s*(.*)$")


def pubblico(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    return bool(SCHEMI_PUBBLICI.search(host)) or any(
        host == d or host.endswith("." + d) for d in ENTI_PUBBLICI)


def pagina(sorgente: str) -> str:
    """public/news/x/index.html -> /news/x/"""
    p = sorgente.strip().removeprefix("public/").removeprefix("./public/")
    p = re.sub(r"(^|/)index\.html$", r"\1", p)
    return "/" + p


def leggi(testo: str):
    rotti, passeggeri = [], []
    sorgente = "?"
    for riga in testo.splitlines():
        m = SEZIONE.match(riga)
        if m:
            sorgente = pagina(m.group(1))
            continue
        m = RIGA.match(riga)
        if not m:
            continue
        stato, url, motivo = m.groups()
        if stato in ("404", "410"):
            rotti.append((stato, url, sorgente))
        elif url.startswith("file://") and "not found" in motivo.lower():
            # file mancante nel sito compilato: è un 404 del nostro sito
            percorso = unquote(urlparse(url).path)
            percorso = "/" + percorso.split("/public/", 1)[-1] if "/public/" in percorso else percorso
            rotti.append(("404", "(interno) " + percorso, sorgente))
        else:
            passeggeri.append((stato, url, sorgente, motivo.strip()))
    return rotti, passeggeri


def corpo_issue(rotti, passeggeri) -> str:
    righe = [
        "Controllo settimanale di tutti i link del sito (interni ed esterni), workflow "
        "`controllo-link.yml`. Questa issue si aggiorna a ogni controllo e si chiude da sola "
        "quando non ci sono più link rotti.",
        "",
    ]
    if rotti:
        righe += [f"## Link rotti da correggere ({len(rotti)})", "",
                  "| Esito | Link | Pagina del sito |", "|---|---|---|"]
        ordinati = sorted(rotti, key=lambda r: (not pubblico(r[1]), r[1], r[2]))
        for stato, url, src in ordinati:
            righe.append(f"| {stato} | {url} | `{src}` |")
        righe += ["",
                  "Come si corregge: si cerca la pagina attuale sulla fonte, la si verifica con una "
                  "richiesta reale e si sostituisce l'URL in tutti i file sorgente (`content/`, "
                  "`data/`, `layouts/`, `static/`). Se la pagina non esiste più si punta alla "
                  "sezione che la conteneva, a una copia d'archivio, oppure si toglie il link "
                  "lasciando il testo. Mai un indirizzo ricostruito a indovinare.", ""]
    else:
        righe += ["Nessun link rotto: tutti i link rispondono.", ""]
    if passeggeri:
        righe += [f"## Errori di rete, da ricontrollare al prossimo giro ({len(passeggeri)})", "",
                  "Timeout, errori del server e blocchi dei sistemi anti-robot: di norma "
                  "passeggeri, non fanno fallire il controllo. Se lo stesso link resta qui per "
                  "più settimane va verificato a mano.", ""]
        visti = set()
        for stato, url, src, motivo in sorted(passeggeri, key=lambda r: r[1]):
            if url in visti:
                continue
            visti.add(url)
            righe.append(f"- `{stato}` {url} — `{src}` — {motivo[:120]}")
        righe.append("")
    return "\n".join(righe)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rapporto", nargs="?", default="lychee-report.md")
    ap.add_argument("--corpo", help="file dove scrivere il corpo della issue")
    a = ap.parse_args()
    try:
        testo = open(a.rapporto, encoding="utf-8").read()
    except FileNotFoundError:
        print(f"Rapporto {a.rapporto} assente: il controllo non è stato eseguito.")
        return 2
    rotti, passeggeri = leggi(testo)
    rotti = sorted(set(rotti))
    if a.corpo:
        with open(a.corpo, "w", encoding="utf-8") as f:
            f.write(corpo_issue(rotti, passeggeri))
    if not rotti:
        print(f"Nessun link rotto ({len(passeggeri)} errori di rete passeggeri).")
        return 0
    print(f"{len(rotti)} link rotti (404/410 o file mancanti):")
    for stato, url, src in rotti:
        print(f"  {stato}  {url}  <- {src}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
