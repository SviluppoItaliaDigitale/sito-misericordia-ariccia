#!/usr/bin/env python3
"""Pubblica automaticamente le nuove news del sito su Facebook e Instagram.

Viene eseguito dal workflow di deploy DOPO la pubblicazione su Aruba, così
link e immagini sono già raggiungibili da Meta. Legge l'elenco delle news
generato da Hugo (public/news/index.json), confronta con il registro
.github/social/pubblicati.json e pubblica solo quelle mai uscite sui social.

Regole di sicurezza:
  - si pubblicano solo news con data negli ultimi MAX_GIORNI giorni
    (le news vecchie non vengono mai "riesumate");
  - al massimo MAX_PER_ESECUZIONE news per esecuzione;
  - "social: false" nel front matter esclude la news;
  - senza credenziali (o con DRY_RUN=1) mostra solo cosa pubblicherebbe.

Credenziali (secrets GitHub): META_PAGE_ID, META_PAGE_TOKEN, META_IG_USER_ID.
Vedi docs/pubblicazione-social.md.

Solo libreria standard: nessuna dipendenza da installare.
"""

import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
FEED = Path(os.environ.get("SOCIAL_FEED", RADICE / "public/news/index.json"))
REGISTRO = Path(os.environ.get("SOCIAL_REGISTRO", RADICE / ".github/social/pubblicati.json"))

GRAPH = "https://graph.facebook.com/" + os.environ.get("META_GRAPH_VERSION", "v23.0")
PAGE_ID = os.environ.get("META_PAGE_ID", "").strip()
PAGE_TOKEN = os.environ.get("META_PAGE_TOKEN", "").strip()
IG_USER_ID = os.environ.get("META_IG_USER_ID", "").strip()

MAX_GIORNI = int(os.environ.get("SOCIAL_MAX_GIORNI", "10"))
MAX_PER_ESECUZIONE = int(os.environ.get("SOCIAL_MAX_PER_ESECUZIONE", "3"))
DRY_RUN = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "si", "yes")

HASHTAG = "#MisericordiaAriccia #Misericordie #Ariccia #CastelliRomani #Volontariato"


# ---------------------------------------------------------------- testi

def accorcia(testo, limite):
    testo = " ".join(testo.split())
    if len(testo) <= limite:
        return testo
    taglio = testo[:limite].rsplit(" ", 1)[0].rstrip(",;:—–-")
    return taglio + "…"


def testo_facebook(n):
    corpo = n.get("social_testo") or accorcia(n["sommario"], 400)
    return f"{n['titolo']}\n\n{corpo}\n\n👉 Leggi tutto: {n['url']}"


def testo_instagram(n):
    corpo = n.get("social_testo") or accorcia(n["sommario"], 1200)
    # Su Instagram i link nel testo non sono cliccabili: li scriviamo comunque
    # in forma breve, leggibile e ricopiabile.
    url_breve = n["url"].replace("https://", "").replace("www.", "").rstrip("/")
    testo = f"{n['titolo']}\n\n{corpo}\n\nL'articolo completo su {url_breve}\n\n{HASHTAG}"
    return testo[:2200]  # limite Instagram


# ---------------------------------------------------------------- Graph API

def graph_post(percorso, parametri):
    dati = urllib.parse.urlencode({**parametri, "access_token": PAGE_TOKEN}).encode()
    req = urllib.request.Request(f"{GRAPH}/{percorso}", data=dati, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        dettaglio = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code} su {percorso}: {dettaglio}") from None


def graph_get(percorso, parametri):
    q = urllib.parse.urlencode({**parametri, "access_token": PAGE_TOKEN})
    try:
        with urllib.request.urlopen(f"{GRAPH}/{percorso}?{q}", timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        dettaglio = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code} su {percorso}: {dettaglio}") from None


def pubblica_facebook(n):
    # Post con link: Facebook costruisce l'anteprima da og:title/og:image.
    r = graph_post(f"{PAGE_ID}/feed", {"message": testo_facebook(n), "link": n["url"]})
    return r["id"]


def pubblica_instagram(n):
    # 1) contenitore con l'immagine (URL pubblico, JPEG)  2) attesa elaborazione  3) pubblicazione
    c = graph_post(f"{IG_USER_ID}/media", {"image_url": n["immagine"], "caption": testo_instagram(n)})
    cid = c["id"]
    for _ in range(20):
        stato = graph_get(cid, {"fields": "status_code"}).get("status_code")
        if stato == "FINISHED":
            break
        if stato in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram ha rifiutato l'immagine {n['immagine']} (stato {stato})")
        time.sleep(3)
    r = graph_post(f"{IG_USER_ID}/media_publish", {"creation_id": cid})
    return r["id"]


# ---------------------------------------------------------------- registro

def carica_registro():
    if REGISTRO.exists():
        return json.loads(REGISTRO.read_text(encoding="utf-8"))
    return {}


def salva_registro(reg):
    REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    REGISTRO.write_text(json.dumps(reg, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- main

def main():
    if not FEED.exists():
        sys.exit(f"Feed non trovato: {FEED} (compilare prima il sito con hugo)")
    news = json.loads(FEED.read_text(encoding="utf-8"))["news"]
    reg = carica_registro()

    # --inizializza: segna tutte le news attuali come già pubblicate (primo avvio)
    if "--inizializza" in sys.argv:
        oggi = dt.date.today().isoformat()
        for n in news:
            voce = reg.setdefault(n["id"], {})
            voce.setdefault("facebook", f"preesistente {oggi}")
            voce.setdefault("instagram", f"preesistente {oggi}")
        salva_registro(reg)
        print(f"Registro inizializzato con {len(news)} news.")
        return 0

    reti = {}
    if PAGE_ID and PAGE_TOKEN:
        reti["facebook"] = pubblica_facebook
    if IG_USER_ID and PAGE_TOKEN:
        reti["instagram"] = pubblica_instagram
    prova = DRY_RUN or not reti
    if prova:
        print("MODALITÀ PROVA: nessuna pubblicazione reale" + ("" if reti else " (credenziali Meta assenti)"))
        reti = {"facebook": None, "instagram": None}

    limite = dt.date.today() - dt.timedelta(days=MAX_GIORNI)
    fatte, errori = 0, 0
    # dalla più vecchia alla più recente, così sui social escono in ordine
    for n in sorted(news, key=lambda x: (x["data"], x["id"])):
        voce = reg.get(n["id"], {})
        mancanti = [r for r in reti if r not in voce]
        if not mancanti:
            continue
        if not n.get("social", True):
            continue
        if dt.date.fromisoformat(n["data"]) < limite:
            continue
        if fatte >= MAX_PER_ESECUZIONE:
            print(f"Raggiunto il limite di {MAX_PER_ESECUZIONE} news: le altre alla prossima esecuzione.")
            break
        fatte += 1
        print(f"\n== {n['titolo']}\n   {n['url']}")
        for rete in mancanti:
            if rete == "instagram" and not n["immagine"].lower().endswith((".jpg", ".jpeg")):
                print("   instagram: saltato (serve un'immagine JPEG nella news o 'immagine:' nel front matter)")
                if not prova:
                    reg.setdefault(n["id"], {})[rete] = "saltato: nessuna immagine JPEG"
                    salva_registro(reg)
                continue
            if prova:
                testo = testo_facebook(n) if rete == "facebook" else testo_instagram(n)
                print(f"   {rete}: pubblicherebbe →\n" + "\n".join("      " + r for r in testo.splitlines()))
                continue
            try:
                pid = reti[rete](n)
                reg.setdefault(n["id"], {})[rete] = pid
                salva_registro(reg)  # subito: se qualcosa dopo fallisce non si ripubblica
                print(f"   {rete}: pubblicato (id {pid})")
            except Exception as e:  # noqa: BLE001 — si riprova alla prossima esecuzione
                errori += 1
                print(f"   {rete}: ERRORE — {e}", file=sys.stderr)

    if fatte == 0:
        print("Nessuna nuova news da pubblicare sui social.")
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())
