#!/usr/bin/env python3
"""Scarica le letture di una domenica (o di un giorno).

Testo da usare: CEI 2008, quello letto a Messa, dal sito ufficiale della CEI
(chiesacattolica.it/liturgia-del-giorno). Evangelizo (la fonte della pagina Liturgia del
giorno del sito) usa ancora la traduzione CEI 1974: serve solo per i numeri dei versetti
e come riserva se la pagina CEI non risponde.

  letture.py                → prossima domenica
  letture.py 2026-10-11     → quel giorno

Stampa un JSON: titolo liturgico; in "cei_2008" le letture col testo da copiare; in
"letture" il testo Evangelizo riga per riga (una riga = un versetto). "versetto_stimato" numera le righe a partire dal
primo versetto del riferimento: è solo un aiuto, il riferimento esatto va controllato.
Solo libreria standard.
"""

import datetime as dt
import html
import json
import re
import sys
import urllib.request

CEI = "https://www.chiesacattolica.it/liturgia-del-giorno/?data-liturgia={d}"
SEZIONI_CEI = [("Prima Lettura", "Prima lettura"), ("Seconda Lettura", "Seconda lettura"), ("Vangelo", "Vangelo")]
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


def letture_cei(d):
    """Prima lettura, seconda lettura e Vangelo in CEI 2008: titoletto, formula d'annuncio
    («Dal libro del profeta Isaìa»), riferimento e testo, fino a «Parola di Dio/del Signore»."""
    pagina = leggi(CEI.format(d=d))
    pagina = re.sub(r"<(script|style).*?</\1>", "", pagina, flags=re.S)
    righe = [r.strip() for r in html.unescape(re.sub(r"<[^>]+>", "\n", pagina)).splitlines() if r.strip()]
    esito, pos = [], 0
    for titolo, nome in SEZIONI_CEI:
        try:
            i = righe.index(titolo, pos)
        except ValueError:
            continue
        fine = next((j for j in range(i + 1, len(righe)) if righe[j].startswith(("Parola di Dio", "Parola del Signore"))), None)
        if fine is None:
            continue
        blocco = righe[i + 1:fine]
        k = next((j for j, r in enumerate(blocco) if r.startswith(("Dal ", "Dalla ", "Dagli ", "Dai "))), None)
        if k is None or k + 1 >= len(blocco):
            continue
        rif, resto = blocco[k + 1], blocco[k + 2:]
        while resto and re.fullmatch(r"[\d.,\-a-z ]+", resto[0]):  # riferimenti spezzati su più righe («.», «19-20»)
            rif += resto.pop(0)
        esito.append({"lettura": nome, "titoletto": " ".join(blocco[:k]), "fonte_lettura": blocco[k],
                      "riferimento": rif, "testo": " ".join(resto)})
        pos = fine
    return esito


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
    try:
        esito["cei_2008"] = letture_cei(d)
    except Exception as e:  # noqa: BLE001
        esito["cei_2008"] = []
        print(f"ATTENZIONE: pagina CEI non raggiungibile ({e}): usare il testo Evangelizo e scriverlo nella scheda",
              file=sys.stderr)
    if not esito["cei_2008"]:
        print("ATTENZIONE: testo CEI 2008 non trovato", file=sys.stderr)
    print(json.dumps(esito, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
