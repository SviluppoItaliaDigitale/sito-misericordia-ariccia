#!/usr/bin/env python3
"""Letture del giorno in traduzione CEI 2008 (quella letta a Messa) per la pagina
/liturgia-del-giorno/: le scarica dal sito ufficiale della CEI e le scrive in
data/liturgia_cei.json, che il template legge alla compilazione.

  liturgia_cei.py              → oggi (ora italiana), scrive data/liturgia_cei.json
  liturgia_cei.py 2026-10-11   → quel giorno, stampa il JSON senza scrivere

Se la pagina CEI non risponde o cambia forma non scrive nulla (o cancella il file
vecchio) e il template torna al testo Evangelizo. Uso consentito dalle note legali di
chiesacattolica.it: finalità formative, senza scopo di lucro, testo integrale e fonte
citata. Solo libreria standard.
"""

import datetime as dt
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://www.chiesacattolica.it/liturgia-del-giorno/?data-liturgia={d}"
USCITA = Path(__file__).resolve().parent.parent / "data" / "liturgia_cei.json"
# Titoli delle sezioni, confrontati in minuscolo (la Veglia pasquale li scrive in maiuscolo)
TITOLI = {f"{n} lettura": f"{n.capitalize()} lettura"
          for n in ("prima", "seconda", "terza", "quarta", "quinta", "sesta", "settima")}
TITOLI.update({"epistola": "Epistola", "salmo responsoriale": "Salmo responsoriale",
               "acclamazione al vangelo": "Acclamazione al Vangelo", "vangelo": "Vangelo"})
LETTURE = {v for v in TITOLI.values() if v.endswith("lettura")} | {"Epistola", "Vangelo"}
FINE_LETTURA = ("Parola di Dio", "Parola del Signore")
# formula d'annuncio: «Dal libro…», «Dalla lettera…», e per la Passione (Palme, Venerdì Santo)
# «Passione di nostro Signore Gesù Cristo secondo…»
ANNUNCIO = ("Dal ", "Dalla ", "Dagli ", "Dai ", "Passione di nostro Signore")


def righe_pagina(d):
    req = urllib.request.Request(URL.format(d=d), headers={"User-Agent": "MisericordiaAriccia-Liturgia/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        pagina = r.read().decode("utf-8", errors="replace")
    pagina = re.sub(r"<(script|style).*?</\1>", "", pagina, flags=re.S)
    return [r.strip() for r in html.unescape(re.sub(r"<[^>]+>", "\n", pagina)).splitlines() if r.strip()]


def letture(d):
    """Sezioni del giorno, ognuna con le sue righe. Le letture (anche le sette della Veglia
    pasquale e l'Epistola) e il Vangelo hanno titoletto, formula d'annuncio e riferimento."""
    righe = righe_pagina(d)
    inizio = next((i for i, r in enumerate(righe) if r.lower() == "prima lettura"), None)
    if inizio is None:
        return []
    teste = [i for i in range(inizio, len(righe)) if righe[i].lower() in TITOLI]
    esito = []
    for n, i in enumerate(teste):
        nome = TITOLI[righe[i].lower()]
        limite = teste[n + 1] if n + 1 < len(teste) else len(righe)
        blocco = righe[i + 1:limite]
        if nome in LETTURE:
            fine = next((j for j, r in enumerate(blocco) if r.startswith(FINE_LETTURA)), None)
            k = next((j for j, r in enumerate(blocco) if r.startswith(ANNUNCIO)), None)
            if fine is None:  # es. Veglia pasquale: dopo l'Esodo segue il cantico, senza «Parola di Dio»
                fine = len(blocco)
            if k is None or k + 1 >= fine:
                continue  # sezione illeggibile: si salta (prima lettura e Vangelo restano obbligatori)
            rif, corpo = blocco[k + 1], blocco[k + 2:fine]
            while corpo and re.fullmatch(r"[\d.,\-a-z ]+", corpo[0]):  # riferimento spezzato («.», «19-20»)
                rif += corpo.pop(0)
            esito.append({"sezione": nome, "titoletto": " ".join(blocco[:k]), "fonte_lettura": blocco[k],
                          "riferimento": rif, "righe": corpo, "chiusura": blocco[fine] if fine < len(blocco) else ""})
            if nome == "Vangelo":
                break
        else:
            unite = []
            for r in blocco:  # «(Cf.» «Ef 1,17-18» «)» arrivano su righe separate
                if unite and (r == ")" or unite[-1].endswith("(Cf.") or unite[-1].endswith("(")):
                    unite[-1] = unite[-1] + ("" if r == ")" else " ") + r
                else:
                    unite.append(r)
            esito.append({"sezione": nome, "riferimento": unite[0] if unite else "", "righe": unite[1:]})
    nomi = [x["sezione"] for x in esito]
    return esito if "Prima lettura" in nomi and "Vangelo" in nomi else []


def oggi_roma():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("Europe/Rome")).date()
    except Exception:  # noqa: BLE001
        return (dt.datetime.utcnow() + dt.timedelta(hours=1)).date()


def main():
    giorno = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else oggi_roma()
    try:
        sezioni = letture(giorno.strftime("%Y%m%d"))
    except Exception as e:  # noqa: BLE001
        print(f"::warning::Letture CEI non scaricate ({e}): la pagina userà Evangelizo")
        sezioni = []
    dati = {"data": giorno.isoformat(), "fonte": URL.format(d=giorno.strftime("%Y%m%d")), "letture": sezioni}
    if len(sys.argv) > 1:
        print(json.dumps(dati, ensure_ascii=False, indent=1))
        return 0
    if not sezioni:
        print("::warning::Letture CEI 2008 non trovate: la pagina userà Evangelizo")
        USCITA.unlink(missing_ok=True)
        return 0
    USCITA.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Letture CEI 2008 del {giorno}: {', '.join(x['sezione'] for x in sezioni)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
