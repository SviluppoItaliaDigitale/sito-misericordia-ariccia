#!/usr/bin/env python3
"""Opere d'arte di pubblico dominio da Wikimedia Commons per la Parola della domenica.

  opera.py cerca "parable wedding feast"      → elenco di file con autore, data, licenza
  opera.py scarica "File:Nome.jpg" DEST.jpg   → scarica (max 1600 px) e stampa i crediti in JSON

Accetta solo file in pubblico dominio (licenza "Public domain"/PD-*/CC0): per gli altri
esce con errore. Solo libreria standard; rispetta i limiti di Commons (riprova se 429).
"""

import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "MisericordiaAriccia-ParolaDomenica/1.0 (https://www.misericordia-ariccia.it; info@misericordia-ariccia.it)"


def scarica_url(url, tentativi=6):
    for i in range(tentativi):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or i == tentativi - 1:
                raise
            attesa = int(e.headers.get("retry-after") or 0) + 5 * (i + 1)
            print(f"Commons: troppe richieste (HTTP {e.code}), riprovo tra {attesa} s", file=sys.stderr)
            time.sleep(attesa)
    raise RuntimeError("non raggiungibile")


def api(**parametri):
    return json.loads(scarica_url(API + "?" + urllib.parse.urlencode({**parametri, "format": "json"})))


def pulisci(testo):
    testo = html.unescape(re.sub(r"<[^>]+>", "", testo or ""))
    return re.sub(r"\s*(label|date) QS:.*", "", testo).strip()  # code di Wikidata


def info(titoli, larghezza=1600):
    r = api(action="query", prop="imageinfo", titles="|".join(titoli), iiprop="url|extmetadata|size",
            iiurlwidth=larghezza)
    for pagina in r["query"]["pages"].values():
        if "imageinfo" not in pagina:
            continue
        ii = pagina["imageinfo"][0]
        m = ii.get("extmetadata", {})
        licenza = pulisci(m.get("LicenseShortName", {}).get("value"))
        yield {
            "file": pagina["title"],
            "titolo": pulisci(m.get("ObjectName", {}).get("value")) or pagina["title"][5:].rsplit(".", 1)[0],
            "autore": pulisci(m.get("Artist", {}).get("value")),
            "data": pulisci(m.get("DateTimeOriginal", {}).get("value")),
            "licenza": licenza,
            "pubblico_dominio": bool(re.search(r"public domain|^pd|cc0", licenza, re.I)),
            "dimensioni": f"{ii.get('width')}x{ii.get('height')}",
            "url_immagine": ii.get("thumburl") or ii["url"],
            "pagina": ii.get("descriptionurl"),
        }


def cerca(testo):
    r = api(action="query", list="search", srnamespace=6, srlimit=15, srsearch=testo + " filetype:bitmap")
    titoli = [x["title"] for x in r["query"]["search"]]
    for o in (info(titoli) if titoli else []):
        segno = "PD" if o["pubblico_dominio"] else "--"
        print(f"[{segno}] {o['file']}\n      {o['autore'][:70]} · {o['data'][:40]} · {o['licenza']} · {o['dimensioni']}")


def scarica(titolo, destinazione):
    trovate = list(info([titolo]))
    if not trovate:
        sys.exit(f"File non trovato: {titolo}")
    o = trovate[0]
    if not o["pubblico_dominio"]:
        sys.exit(f"Non è di pubblico dominio ({o['licenza']}): scegline un'altra.")
    with open(destinazione, "wb") as f:
        f.write(scarica_url(o["url_immagine"]))
    print(json.dumps(o, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "cerca":
        cerca(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "scarica":
        scarica(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
