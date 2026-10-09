#!/usr/bin/env python3
"""Scarica le letture di una domenica (o di un giorno) da Evangelizo, la stessa fonte
della pagina Liturgia del giorno del sito.

  letture.py                → prossima domenica
  letture.py 2026-10-11     → quel giorno

Stampa un JSON: titolo liturgico e, per prima lettura, salmo, seconda lettura e Vangelo,
il riferimento e le righe del testo. "versetto_stimato" numera le righe a partire dal
primo versetto del riferimento: è solo un aiuto, il riferimento esatto va controllato.
Solo libreria standard.
"""

import datetime as dt
import html
import json
import re
import sys
import urllib.request

URL = "https://feed.evangelizo.org/v2/reader.php?date={d}&lang=IT&type={t}"
LETTURE = {"FR": "Prima lettura", "PS": "Salmo responsoriale", "SR": "Seconda lettura", "GSP": "Vangelo"}


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MisericordiaAriccia-ParolaDomenica/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def testo(grezzo):
    grezzo = grezzo.split("Copyright", 1)[0]
    righe = [html.unescape(re.sub(r"<[^>]+>", "", r)).strip() for r in re.split(r"<br\s*/?>", grezzo)]
    return [r for r in righe if r]


def versetti(titolo):
    """«Filippesi 4,12-14.19-20.» → ['4,12', '4,13', '4,14', '4,19', '4,20'] (una riga = un versetto)."""
    m = re.search(r"(\d+)(?:\(\d+\))?,([\d\-.a-z]+)", titolo)
    if not m:
        return []
    numeri = []
    for pezzo in m.group(2).strip(".").split("."):
        estremi = [int(re.sub(r"\D", "", x)) for x in pezzo.split("-") if re.sub(r"\D", "", x)]
        if estremi:
            numeri += [f"{m.group(1)},{v}" for v in range(estremi[0], estremi[-1] + 1)]
    return numeri


def main():
    if len(sys.argv) > 1:
        giorno = dt.date.fromisoformat(sys.argv[1])
    else:
        oggi = dt.date.today()
        giorno = oggi + dt.timedelta(days=(6 - oggi.weekday()) or 7)
    d = giorno.strftime("%Y%m%d")
    esito = {"data": giorno.isoformat(), "giorno_liturgico": leggi(URL.format(d=d, t="liturgic_t")).strip(),
             "letture": []}
    for codice, nome in LETTURE.items():
        titolo = html.unescape(re.sub(r"<[^>]+>", "", leggi(URL.format(d=d, t="reading_lt") + f"&content={codice}"))).strip()
        if not titolo:
            continue  # nei giorni feriali manca la seconda lettura
        righe = testo(leggi(URL.format(d=d, t="reading") + f"&content={codice}"))
        numeri = versetti(titolo) if codice != "PS" else []
        esito["letture"].append({
            "lettura": nome, "codice": codice, "titolo": titolo,
            "righe": [{"versetto_stimato": numeri[i] if i < len(numeri) else "", "testo": r}
                      for i, r in enumerate(righe)],
        })
    print(json.dumps(esito, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
