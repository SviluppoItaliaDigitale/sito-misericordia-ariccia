#!/usr/bin/env python3
"""Scarica le letture di una domenica (o di un giorno).

Testo da usare: CEI 2008, quello letto a Messa, dal sito ufficiale della CEI
(chiesacattolica.it/liturgia-del-giorno). Evangelizo (la fonte della pagina Liturgia del
giorno del sito) usa ancora la traduzione CEI 1974: serve solo per i numeri dei versetti
e come riserva se la pagina CEI non risponde.

  letture.py                → il prossimo giorno della Parola, domenica o festa, oggi compreso
                              (calendario.py; di domenica o in una festa è oggi, per il recupero notturno)
  letture.py 2026-10-11     → quel giorno
  letture.py --controlla .github/social/parola/2026-11-01.json
                            → controlla che il brano «Le parole dei Papi» della scheda sia copiato
                              esatto da Vatican News, con la fonte giusta (esce con 1 se no)
  letture.py --fonte-papi [AAAA-MM-GG]
                            → controlla che Vatican News dia «Le Parole dei Papi» del prossimo
                              giorno della Parola (esce con 1 se no: lo usa il controllo settimanale
                              in controllo-link.yml, che apre la issue «fonte-rotta»)

Stampa un JSON: titolo liturgico; in "parole_dei_papi" il commento di un Papa alle letture
che Vatican News pubblica nella pagina del Vangelo del giorno (testo intero, fonte e indirizzo:
nella scheda va solo un brano breve, copiato esatto); in "cei_2008" le letture col testo da copiare; in
"letture" il testo Evangelizo riga per riga (una riga = un versetto). "versetto_stimato" numera le righe a partire dal
primo versetto del riferimento: è solo un aiuto, il riferimento esatto va controllato.
Solo libreria standard.
"""

import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from liturgia_cei import letture as letture_del_giorno, scarica  # noqa: E402  (stesso lettore della Liturgia del giorno)

VATICAN_NEWS = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno/{a}/{m:02d}/{g:02d}.html"
LIMITE_PAPI = 500  # caratteri del brano nella scheda: il post Instagram ha un limite di 2200
URL = "https://feed.evangelizo.org/v2/reader.php?date={d}&lang=IT&type={t}"
LETTURE = {"FR": "Prima lettura", "PS": "Salmo responsoriale", "SR": "Seconda lettura", "GSP": "Vangelo"}


def leggi(url):
    # il feed risponde a volte 403 senza corpo: scarica() riprova (21/10/2026, la routine si era fermata qui)
    return scarica(url, "MisericordiaAriccia-ParolaDomenica/1.0")


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
    """Prima lettura, seconda lettura e Vangelo in CEI 2008 (stesso lettore della pagina
    Liturgia del giorno, scripts/liturgia_cei.py), col testo su una riga sola."""
    return [{"lettura": x["sezione"], "titoletto": x["titoletto"], "fonte_lettura": x["fonte_lettura"],
             "riferimento": x["riferimento"], "testo": " ".join(x["righe"])}
            for x in letture_del_giorno(d) if x["sezione"] in ("Prima lettura", "Seconda lettura", "Vangelo")]


def parole_dei_papi(giorno):
    """Sezione «Le Parole dei Papi» della pagina Vatican News del giorno: testo, fonte (l'ultima
    parentesi, es. «Papa Leone XIV, Omelia, 1° novembre 2025») e indirizzo. None se la sezione manca."""
    url = VATICAN_NEWS.format(a=giorno.year, m=giorno.month, g=giorno.day)
    pagina = scarica(url, "Mozilla/5.0 (compatible; MisericordiaAriccia-ParolaDomenica/1.0)")
    m = re.search(r"<h2>\s*Le Parole dei Papi\s*</h2>(.*?)</section>", pagina, re.S | re.I)
    if not m:
        return None
    testo_intero = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).split())
    f = re.search(r"\(([^()]*\d{4})\)\s*$", testo_intero)
    if not f:
        return None
    return {"testo": testo_intero[:f.start()].strip(), "fonte": " ".join(f.group(1).split()), "url": url}


def normalizza(s):
    """Confronto del brano: spazi unici, apostrofi e virgolette uniformi."""
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return " ".join(s.split())


def controlla(file_scheda):
    """Errori del brano «Le parole dei Papi» della scheda rispetto a Vatican News (lista vuota: va bene)."""
    s = json.loads(Path(file_scheda).read_text(encoding="utf-8"))
    p = s.get("parole_papi")
    if not p:
        return []
    errori = []
    testo = (p.get("testo") or "").strip()
    if not testo or not (p.get("fonte") or "").strip():
        return ["parole_papi: servono «testo» e «fonte»"]
    if len(testo) > LIMITE_PAPI:
        errori.append(f"parole_papi: brano di {len(testo)} caratteri, al massimo {LIMITE_PAPI}")
    ufficiale = parole_dei_papi(dt.date.fromisoformat(s["data"]))
    if not ufficiale:
        return errori + ["Vatican News: sezione «Le Parole dei Papi» non trovata per questa data"]
    if normalizza(p["fonte"]) != normalizza(ufficiale["fonte"]):
        errori.append(f"parole_papi: fonte «{p['fonte']}», su Vatican News «{ufficiale['fonte']}»")
    intero = normalizza(ufficiale["testo"])
    # i tagli si segnano con «(…)», come fa Vatican News: ogni pezzo deve essere identico all'originale
    for pezzo in re.split(r"\s*\((?:…|\.\.\.)\)\s*", testo):
        if pezzo and normalizza(pezzo) not in intero:
            errori.append(f"parole_papi: questo pezzo non è identico a Vatican News: «{pezzo[:80]}…»")
    return errori


def prossimo_giorno():
    """Il prossimo giorno della Parola (domenica o festa del calendario), oggi compreso."""
    from calendario import giorno_della_parola, oggi_roma  # noqa: PLC0415 — stesso cartella
    oggi = oggi_roma()
    return next(oggi + dt.timedelta(days=k) for k in range(8) if giorno_della_parola(oggi + dt.timedelta(days=k)))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--fonte-papi":
        giorno = dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else prossimo_giorno()
        url = VATICAN_NEWS.format(a=giorno.year, m=giorno.month, g=giorno.day)
        try:
            p = parole_dei_papi(giorno)
        except Exception as e:  # noqa: BLE001 — dopo i tentativi di scarica(): guasto vero
            print(f"Vatican News non leggibile per il {giorno}: {e} ({url})")
            sys.exit(1)
        if not p or len(p["testo"]) < 100:
            print(f"Vatican News: sezione «Le Parole dei Papi» assente o cambiata per il {giorno} ({url})")
            sys.exit(1)
        print(f"Vatican News: «Le Parole dei Papi» del {giorno} ok ({p['fonte']}, {len(p['testo'])} caratteri)")
        return
    if len(sys.argv) > 2 and sys.argv[1] == "--controlla":
        errori = controlla(sys.argv[2])
        for e in errori:
            print("ERRORE:", e, file=sys.stderr)
        print("parole dei Papi: ok" if not errori else f"parole dei Papi: {len(errori)} errori")
        sys.exit(1 if errori else 0)
    if len(sys.argv) > 1:
        giorno = dt.date.fromisoformat(sys.argv[1])
    else:
        giorno = prossimo_giorno()
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
    try:
        esito["parole_dei_papi"] = parole_dei_papi(giorno)
        if not esito["parole_dei_papi"]:
            print("ATTENZIONE: sezione «Le Parole dei Papi» non trovata su Vatican News", file=sys.stderr)
    except Exception as e:  # noqa: BLE001 — facoltative: il carosello si fa lo stesso
        # il guasto persistente lo segnala il controllo settimanale (letture.py --fonte-papi in
        # controllo-link.yml), che fa diventare rosso il run e apre la issue «fonte-rotta»
        esito["parole_dei_papi"] = None
        print(f"GUASTO: Vatican News non raggiungibile ({e}): niente «Le parole dei Papi», "
              "da scrivere nel riepilogo", file=sys.stderr)
    print(json.dumps(esito, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
