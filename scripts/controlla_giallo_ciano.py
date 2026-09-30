#!/usr/bin/env python3
"""Controllo giornaliero di Giallo Ciano, la rivista delle Misericordie d'Italia.

Legge https://www.misericordie.it/giallo-ciano/ e lo confronta con
data/giallo_ciano.json (la nostra pagina /giallo-ciano/):
  - numero nuovo sul sito nazionale  -> lo aggiunge in cima al JSON;
  - link cambiato dal nazionale      -> aggiorna il nostro link;
  - nostri link che non rispondono   -> li segnala.
Scrive gli avvisi in giallo_ciano_avvisi.md (li trasforma in segnalazioni
GitHub il workflow .github/workflows/controlla-giallo-ciano.yml).
Solo libreria standard.
"""

import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "data/giallo_ciano.json"
AVVISI = RADICE / "giallo_ciano_avvisi.md"
PAGINA = "https://www.misericordie.it/giallo-ciano/"
UA = {"User-Agent": "Mozilla/5.0 (controllo link sito Misericordia di Ariccia)"}
MESI = "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()


def scarica(url, tentativi=3):
    for i in range(tentativi):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code < 500 and e.code != 429:
                return e.code, b""
            errore = e.code
        except Exception as e:  # noqa: BLE001 — rete: si riprova
            errore = type(e).__name__
        time.sleep(10 * (i + 1))
    return errore, b""


def testo(frammento):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", frammento)).split())


def numeri_nazionali(pagina):
    """[(uscita 'Mese AAAA', numero 'n/AAAA' o None, link)] nell'ordine della pagina."""
    trovati = []
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', pagina, re.S):
        t, link = testo(m.group(2)), urllib.parse.urljoin(PAGINA, html.unescape(m.group(1)))
        u = re.fullmatch(r"(?:GialloCiano\s*-\s*n\.\s*(\d+)\s+)?(\w+)\s+(20\d\d)", t, re.I)
        if u and u.group(2).lower() in MESI:
            numero = f"{u.group(1)}/{u.group(3)}" if u.group(1) else None
            trovati.append((f"{u.group(2).capitalize()} {u.group(3)}", numero, link))
    return trovati


def main():
    dati = json.loads(DATI.read_text(encoding="utf-8"))
    avvisi, modificato = [], False

    stato, corpo = scarica(PAGINA)
    nazionali = numeri_nazionali(corpo.decode("utf-8", "replace")) if stato == 200 else []
    if not nazionali:
        avvisi.append(f"- ⚠️ Non riesco a leggere l'elenco dei numeri da {PAGINA} (risposta: {stato}). "
                      "Forse la pagina è cambiata: va controllata a mano.")

    nostri = {n["uscita"]: n for n in dati["numeri"]}
    usati = {}
    for _, _, link in nazionali:
        usati[link] = usati.get(link, 0) + 1
    for uscita, numero, link in reversed(nazionali):  # dal più vecchio, così i nuovi finiscono in cima
        if uscita in nostri:
            n = nostri[uscita]
            # link cambiato dal nazionale (solo se non è un link condiviso con un altro numero: errore loro)
            if link != n["link"] and usati[link] == 1:
                avvisi.append(f"- 🔗 **{uscita}**: il sito nazionale ha cambiato il link, aggiornato → {link}")
                n["link"], n["formato"] = link, "PDF" if link.lower().endswith(".pdf") else "sfogliabile"
                n.pop("nota", None)
                modificato = True
            continue
        anno = uscita.split()[1]
        if not numero:  # l'ultimo numero in evidenza non ha il numero: lo ricavo dal precedente dello stesso anno
            stesso_anno = [int(x["numero"].split("/")[0]) for x in dati["numeri"] if x["numero"].endswith("/" + anno)]
            numero = f"{max(stesso_anno, default=0) + 1}/{anno}"
        nuovo = {"numero": numero, "uscita": uscita, "link": link,
                 "formato": "PDF" if link.lower().endswith(".pdf") else "sfogliabile"}
        dati["numeri"].insert(0, nuovo)
        nostri[uscita] = nuovo
        modificato = True
        avvisi.append(f"- 🆕 **È uscito Giallo Ciano di {uscita.lower()}** (n. {numero}): aggiunto alla pagina "
                      f"https://www.misericordia-ariccia.it/giallo-ciano/ (online dopo il rebuild notturno). "
                      f"Link: {link}")

    # ordine: dal più recente (anno, mese)
    dati["numeri"].sort(key=lambda x: (int(x["uscita"].split()[1]), MESI.index(x["uscita"].split()[0].lower())), reverse=True)

    for n in dati["numeri"]:
        stato, _ = scarica(n["link"])
        if stato != 200:
            avvisi.append(f"- ❌ **{n['uscita']}**: il link non funziona (risposta {stato}) → {n['link']}")

    if modificato:
        DATI.write_text(json.dumps(dati, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    AVVISI.write_text("\n".join(avvisi) + ("\n" if avvisi else ""), encoding="utf-8")
    print("\n".join(avvisi) or "Tutto in ordine: nessun numero nuovo, tutti i link funzionano.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
