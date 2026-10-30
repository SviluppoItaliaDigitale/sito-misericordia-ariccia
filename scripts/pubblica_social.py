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

Con --parola pubblica invece la «Parola della domenica» di oggi (solo social,
nessuna pagina sul sito): scheda in .github/social/parola/AAAA-MM-GG.json e
grafica già online in /img/parola/AAAA-MM-GG.jpg. Vedi docs/parola-della-domenica.md.

Testo alternativo (dal 21/10/2026): le immagini di Instagram (news e carosello
della Parola) e le foto dell'album Facebook della Parola escono con il loro
testo alternativo; i Reel e i post Facebook con link non lo accettano. Vedi
docs/pubblicazione-social.md.

Solo libreria standard: nessuna dipendenza da installare.
"""

import datetime as dt
import json
import os
import re
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

# news (id separati da virgola) il cui post Instagram va cancellato e rifatto
RIPUBBLICA_IG = [x.strip() for x in os.environ.get("RIPUBBLICA_INSTAGRAM", "").split(",") if x.strip()]

# "elenco" = mostra gli ultimi post della pagina Facebook (sola lettura);
# id di news separati da virgola = riscrive il testo di quei post Facebook
AGGIORNA_FB = os.environ.get("AGGIORNA_FACEBOOK", "").strip()

MAX_GIORNI = int(os.environ.get("SOCIAL_MAX_GIORNI", "10"))
MAX_PER_ESECUZIONE = int(os.environ.get("SOCIAL_MAX_PER_ESECUZIONE", "3"))
DRY_RUN = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "si", "yes")

# Luogo dei post (Facebook «place», Instagram «location_id»): la pagina-luogo
# «Ariccia». Se SOCIAL_LUOGO_ID non è impostato lo script la cerca da solo con
# la Graph API (vedi luogo_post); se non la trova i post escono senza luogo.
LUOGO_ID = os.environ.get("SOCIAL_LUOGO_ID", "").strip()
LUOGO_NOME = "Ariccia"

HASHTAG = "#MisericordiaAriccia #Misericordie #Ariccia #CastelliRomani #Volontariato"


# ---------------------------------------------------------------- testi

def accorcia(testo, limite):
    testo = " ".join(testo.split())
    if len(testo) <= limite:
        return testo
    taglio = testo[:limite].rsplit(" ", 1)[0].rstrip(",;:—–-")
    return taglio + "…"


GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def riga_data(n):
    """Se il post esce DOPO la data della news, apre il testo con la data
    dell'evento, così "stamattina" o "sabato" non sembrano riferiti a oggi.
    La data è `data_evento:` del front matter (se c'è) o la data della news.
    Con `social_testo:` scritto a mano la data la mette chi scrive."""
    if n.get("social_testo") or dt.date.fromisoformat(n["data"]) >= dt.date.today():
        return ""
    g = dt.date.fromisoformat((n.get("data_evento") or n["data"])[:10])
    return f"📅 {GIORNI[g.weekday()].capitalize()} {g.day} {MESI[g.month - 1]} {g.year}\n\n"


def credito_musica(n):
    """Riga di credito per i video con musica di terzi (data/musica_video.json, licenza CC BY: va citato l'autore)."""
    video = n.get("video") or n.get("social_video")  # nel feed di Hugo (layouts/news/list.json) il campo si chiama "video"
    if not video:
        return ""
    try:
        dati = json.loads((Path(__file__).resolve().parent.parent / "data" / "musica_video.json").read_text())
    except (OSError, ValueError):
        return ""
    brano = dati.get("video", {}).get(Path(video).name)
    return f"\n\n🎵 {brano} – {dati['autore']} (incompetech.com) CC BY 4.0" if brano else ""


def testo_facebook(n):
    corpo = n.get("social_testo") or accorcia(n["sommario"], 400)
    return f"{n['titolo']}\n\n{riga_data(n)}{corpo}{credito_musica(n)}\n\n👉 Leggi tutto: {n['url']}"


def testo_instagram(n):
    corpo = n.get("social_testo") or accorcia(n["sommario"], 1200)
    # Su Instagram i link nel testo non sono cliccabili: li scriviamo comunque
    # in forma breve, leggibile e ricopiabile.
    url_breve = n["url"].replace("https://", "").replace("www.", "").rstrip("/")
    testo = f"{n['titolo']}\n\n{riga_data(n)}{corpo}{credito_musica(n)}\n\nL'articolo completo su {url_breve}\n\n{HASHTAG}"
    return testo[:2200]  # limite Instagram


# ---------------------------------------------------------------- testo alternativo
#
# Ogni immagine ha il suo testo alternativo (regola .claude/rules/comunicazione-social.md, dal webinar
# su disabilità e fragilità). Instagram: «alt_text» sul contenitore di un'immagine singola o di
# un'immagine del carosello, fino a 1000 caratteri; Meta lo ha introdotto il 24/03/2025 e non lo accetta
# per Reel e storie. Facebook: «alt_text_custom» sulle foto caricate con /{page-id}/photos (l'album della
# Parola). I post Facebook delle news sono post con link: non c'è una foto a cui darlo.

LIMITE_ALT = 1000
_alt_rifiutati = set()  # parametri che Meta ha rifiutato in questo giro: non si mandano più


def lunghezza_alt(testo):
    """Lunghezza del testo alternativo in unità UTF-16 (22/10/2026), come la contano il generatore delle grafiche
    della Protezione Civile e la pubblicazione di social-pc-genzano: è il conteggio più severo, perché un
    carattere fuori dal piano di base (un'emoji, un simbolo musicale) vale 2. Meta non dice in che unità conta i
    1000 caratteri; così il limite non si supera in nessun modo di contare."""
    return len(str(testo).encode("utf-16-le")) // 2


def _entro(testo, limite):
    """La parte iniziale di `testo` che sta in `limite` unità UTF-16."""
    usate = 0
    for i, c in enumerate(testo):
        usate += 2 if ord(c) > 0xFFFF else 1
        if usate > limite:
            return testo[:i]
    return testo


def testo_alt(testo, limite=LIMITE_ALT):
    """Testo alternativo su una riga e dentro il limite di Meta: se è più lungo si tengono le frasi intere."""
    testo = re.sub(r"\s+", " ", str(testo or "")).strip()
    if lunghezza_alt(testo) <= limite:
        return testo
    tenute = ""
    for frase in re.split(r"(?:(?<=[.!?…])|(?<=[.!?…]»))\s+", testo):
        prova = f"{tenute} {frase}".strip()
        if lunghezza_alt(prova) > limite:
            break
        tenute = prova
    # una sola frase più lunga del limite (non succede con i testi di oggi): si taglia all'ultima parola intera
    return tenute or _entro(testo, limite - 1).rsplit(" ", 1)[0].rstrip(",;:—–-") + "…"


def alt_news(n):
    """Testo alternativo dell'immagine di una news e da dove viene: «social_alt:» del front matter, altrimenti
    l'alt dell'immagine dell'articolo che diventa l'immagine del post (di solito la grafica brand). Il feed di
    Hugo lo dà in «immagine_alt» solo per l'immagine pubblicata, cioè n["immagine"] (partial
    news-immagine-alt.html). Testo vuoto se l'immagine pubblicata non ha un alt nel testo."""
    if (n.get("social_alt") or "").strip():
        return testo_alt(n["social_alt"]), "social_alt del front matter"
    if (n.get("immagine_alt") or "").strip():
        return testo_alt(n["immagine_alt"]), "alt dell'immagine nell'articolo"
    return "", ("l'immagine pubblicata non ha un alt nel testo: aggiungilo all'immagine nell'articolo "
                "o scrivi social_alt: nel front matter")


def riga_alt_instagram(n):
    """Riga per il log: che testo alternativo riceve il post Instagram di una news."""
    if n.get("video"):
        return "testo alternativo: no, è un Reel (Instagram non lo accetta per i Reel)"
    alt, fonte = alt_news(n)
    return f"testo alternativo ({fonte}): {alt}" if alt else f"testo alternativo: nessuno, {fonte}"


# Il testo alternativo nominato nel rifiuto di Meta, in qualunque grafia: alt_text, alt_text_custom, «Alt text».
# Anche in italiano: titolo e messaggio per l'utente (error_user_title, error_user_msg) Meta li scrive nella lingua
# della richiesta (guida «Handling Errors» della Graph API).
ALT_NOMINATO = re.compile(r"alt[ _-]?text|testo alternativo", re.I)
# Parametri e cause diversi dal testo alternativo, in inglese e in italiano: indirizzo o immagine, luogo, didascalia,
# programmazione, carosello, tag. Un «(#100)» che ne nomina uno riguarda quello, non il testo alternativo. Si
# aggiungono i nomi degli altri parametri della stessa richiesta (argomento `altri` di alt_rifiutato).
# Il codice 100 copre problemi diversi, e nei casi documentati il messaggio dice quale (tipo di contenuto, carosello
# con meno di 2 o più di 10 elementi, tag: riferimento dei codici di errore della Graph API di Instagram); un rifiuto
# del testo alternativo non è documentato, quindi riprovare quando il 100 non nomina nulla è una regola prudente nostra.
ALTRA_CAUSA = re.compile(r"url|image|photo|video|media|place|location|caption|message|children|link|publish|schedul"
                         r"|carousel|\btag"
                         r"|immagin|foto|indirizz|luogo|posizion|didascal|messagg|programm|carosell",
                         re.I)


def errore_meta(errore):
    """Testo e codice dell'errore di Meta dentro un errore di graph_post («HTTP 400 su <percorso>: <JSON>»): il
    messaggio, il titolo e il messaggio per l'utente, senza il percorso della richiesta né le chiavi del JSON, che
    contengono parole come «media» e «message». Se la risposta non è un JSON leggibile, i campi si cercano nel testo."""
    t = re.sub(r"^HTTP \d+ su \S+: ", "", str(errore))
    try:
        e = json.JSONDecoder().raw_decode(t[t.index("{"):])[0].get("error") or {}
    except (ValueError, AttributeError):
        e = {}
    if isinstance(e, dict) and e:
        testo = " ".join(str(e[k]) for k in ("message", "error_user_title", "error_user_msg") if e.get(k))
        return testo, e.get("code")
    campi = re.findall(r'"(?:message|error_user_title|error_user_msg)"\s*:\s*"((?:[^"\\]|\\.)*)"', t)
    codice = re.search(r'"code"\s*:\s*(\d+)', t)
    return (" ".join(campi) if campi else t), (int(codice.group(1)) if codice else None)


def alt_rifiutato(errore, chiave, altri=()):
    """Vero se il rifiuto di Meta dipende o può dipendere dal testo alternativo: lo nomina, oppure è un
    «(#100) Invalid parameter» che non nomina un altro parametro. `altri` sono i nomi degli altri parametri della
    stessa richiesta (image_url, is_carousel_item, caption…): un «(#100)» che ne nomina uno riguarda quello.
    Un «(#100)» che nomina il luogo lo gestisce con_luogo; uno che nomina l'immagine o l'indirizzo, e gli altri errori,
    col testo alternativo non c'entrano. Stesso criterio della Protezione Civile (scripts/pubblica-social-auto.py del
    repository dei social) e di Cooprimavera (scripts/gestione_social.py)."""
    testo, codice = errore_meta(errore)
    if chiave in testo or ALT_NOMINATO.search(testo):
        return True
    if not (codice == 100 or "(#100)" in testo) or ALTRA_CAUSA.search(testo):
        return False
    basso = testo.lower()
    return not any(k.lower() in basso or k.lower().replace("_", " ") in basso for k in altri if k and k != chiave)


def con_alt(pubblica, parametri, chiave):
    """Pubblica col testo alternativo (parametri[chiave]); se Meta rifiuta la richiesta per un parametro, riprova
    una volta senza e lo scrive nel log: il post non deve mai saltare per il testo alternativo. Se senza testo
    alternativo la richiesta riesce, era quello il problema e in questo giro non si manda più; se fallisce
    ancora, il problema era un altro e l'errore prosegue come prima."""
    senza = {k: v for k, v in parametri.items() if k != chiave}
    if not parametri.get(chiave) or chiave in _alt_rifiutati:
        return pubblica(senza)
    try:
        return pubblica(parametri)
    except RuntimeError as e:
        if not alt_rifiutato(e, chiave, senza):
            raise
        print(f"   Meta ha rifiutato la richiesta con il testo alternativo ({chiave}): si riprova una volta senza ({e})")
        risultato = pubblica(senza)
        _alt_rifiutati.add(chiave)
        print(f"   riuscita senza testo alternativo: in questo giro {chiave} non si manda più")
        return risultato


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


def graph_delete(percorso):
    q = urllib.parse.urlencode({"access_token": PAGE_TOKEN})
    req = urllib.request.Request(f"{GRAPH}/{percorso}?{q}", method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        dettaglio = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code} su {percorso}: {dettaglio}") from None


def cancella_instagram(reg, prova):
    """Cancella i post Instagram delle news in RIPUBBLICA_INSTAGRAM e le toglie
    dal registro, così il giro normale le ripubblica col testo aggiornato.
    Al primo errore si ferma: si ripubblicano solo quelle già cancellate,
    mai un doppione."""
    for nid in RIPUBBLICA_IG:
        if nid in reg and "instagram" not in reg[nid]:
            print(f"   {nid}: già tolto dal registro (post cancellato a mano), si ripubblica")
            continue
        mid = reg.get(nid, {}).get("instagram", "")
        if not mid.isdigit():
            raise RuntimeError(f"{nid}: nessun post Instagram cancellabile nel registro ({mid!r})")
        if prova:
            print(f"   {nid}: cancellerebbe il post Instagram {mid} e lo ripubblicherebbe")
            continue
        graph_delete(mid)
        del reg[nid]["instagram"]
        salva_registro(reg)
        print(f"   {nid}: cancellato il post Instagram {mid}")


def elenca_facebook():
    r = graph_get(f"{PAGE_ID}/posts", {"fields": "id,created_time,message", "limit": 40})
    for p in r.get("data", []):
        print(f"\n-- {p['created_time'][:10]}  {p['id']}")
        print("\n".join("   " + riga for riga in (p.get("message") or "(senza testo)").splitlines()))


def aggiorna_facebook(news, reg, prova):
    """Riscrive il testo dei post Facebook già pubblicati (l'API lo consente)."""
    per_id = {n["id"]: n for n in news}
    for nid in [x.strip() for x in AGGIORNA_FB.split(",") if x.strip()]:
        pid = reg.get(nid, {}).get("facebook", "")
        if nid not in per_id or "_" not in pid:
            print(f"   {nid}: nessun post Facebook modificabile nel registro ({pid!r})")
            continue
        testo = testo_facebook(per_id[nid])
        if prova:
            print(f"   {nid}: riscriverebbe il post {pid} →\n" + "\n".join("      " + r for r in testo.splitlines()))
            continue
        graph_post(pid, {"message": testo})
        print(f"   {nid}: aggiornato il post Facebook {pid}")


_luogo = {}


def luogo_post():
    """Id della pagina-luogo «Ariccia» da usare come luogo dei post, o None.
    1) SOCIAL_LUOGO_ID; 2) ricerca delle pagine con dati di posizione
    (city = Ariccia); 3) la nostra pagina, se il suo indirizzo è ad Ariccia.
    Il risultato si calcola una volta per esecuzione e si scrive nel log."""
    if "id" in _luogo:
        return _luogo["id"]
    trovato, come = None, ""
    if LUOGO_ID:
        trovato, come = LUOGO_ID, "SOCIAL_LUOGO_ID"
    else:
        try:
            r = graph_get("pages/search", {"q": LUOGO_NOME, "fields": "id,name,location"})
            for p in r.get("data", []):
                loc = p.get("location") or {}
                if p.get("name") == LUOGO_NOME and loc.get("city") == LUOGO_NOME and not loc.get("street"):
                    trovato, come = p["id"], "ricerca pagine"
                    break
        except Exception as e:  # noqa: BLE001
            print(f"Luogo: ricerca della pagina «{LUOGO_NOME}» non riuscita ({e})")
        if not trovato and PAGE_ID:
            try:
                loc = graph_get(PAGE_ID, {"fields": "location"}).get("location") or {}
                if loc.get("city") == LUOGO_NOME:
                    trovato, come = PAGE_ID, "indirizzo della nostra pagina"
            except Exception as e:  # noqa: BLE001
                print(f"Luogo: lettura dell'indirizzo della pagina non riuscita ({e})")
    print(f"Luogo dei post: {trovato} ({come})" if trovato else "Luogo dei post: nessuno, si pubblica senza luogo")
    _luogo["id"] = trovato
    return trovato


def con_luogo(pubblica, parametri, chiave):
    """Prova a pubblicare col luogo; se Meta rifiuta proprio il luogo, riprova senza."""
    luogo = luogo_post()
    if luogo:
        try:
            return pubblica({**parametri, chiave: luogo})
        except RuntimeError as e:
            if "place" not in str(e).lower() and "location" not in str(e).lower():
                raise
            print(f"   luogo rifiutato da Meta, si pubblica senza ({e})")
    return pubblica(parametri)


def pubblica_facebook(n):
    # Sempre un post con link: Facebook costruisce l'anteprima da og:title/og:image
    # e il video si guarda nell'articolo. I video caricati con l'API (/videos)
    # venivano trasformati in Reel e Facebook non li distribuiva a nessuno
    # (visibili solo agli amministratori, 4 ottobre 2026): niente più Reel su FB.
    testo = testo_facebook(n)
    if n.get("video"):
        testo = testo.replace("\n\n👉 Leggi tutto:", "\n\n▶️ Guarda il video e leggi tutto:")
    r = con_luogo(lambda par: graph_post(f"{PAGE_ID}/feed", par),
                  {"message": testo, "link": n["url"]}, "place")
    return r["id"]


def pubblica_facebook_reel(n):
    """Reel sulla pagina Facebook con la Reels API ufficiale (tre fasi: start,
    upload del file da URL, finish). È la stessa via di Meta Business Suite:
    i video caricati con /videos venivano convertiti in Reel ma non distribuiti.
    Limiti Meta: verticale 9:16, da 3 a 90 secondi."""
    avvio = graph_post(f"{PAGE_ID}/video_reels", {"upload_phase": "start"})
    vid = avvio["video_id"]
    # Fase 2: Facebook scarica il file dall'URL pubblico del sito.
    req = urllib.request.Request(f"https://rupload.facebook.com/video-upload/{GRAPH.rsplit('/', 1)[1]}/{vid}",
                                 data=b"", method="POST",
                                 headers={"Authorization": f"OAuth {PAGE_TOKEN}", "file_url": n["video"]})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            esito = json.load(resp)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} nel caricamento del Reel: {e.read().decode(errors='replace')}") from None
    if not esito.get("success"):
        raise RuntimeError(f"caricamento del Reel non riuscito: {esito}")
    graph_post(f"{PAGE_ID}/video_reels", {"upload_phase": "finish", "video_id": vid,
                                          "video_state": "PUBLISHED", "description": testo_facebook(n)})
    # Attesa dell'elaborazione (di solito 1–3 minuti); se fallisce lo dice qui.
    for _ in range(100):
        stato = graph_get(vid, {"fields": "status"}).get("status", {})
        fase = stato.get("publishing_phase", {})
        if fase.get("status") == "complete" or stato.get("video_status") == "ready":
            return vid
        if stato.get("video_status") == "error" or fase.get("status") == "error":
            raise RuntimeError(f"Facebook ha rifiutato il Reel {n['video']}: {stato}")
        time.sleep(3)
    print(f"   facebook_reel: ancora in elaborazione (id {vid}), si considera pubblicato")
    return vid


def pubblica_instagram(n):
    # 1) contenitore con l'immagine (URL pubblico, JPEG) o col video (Reel)
    # 2) attesa elaborazione  3) pubblicazione
    if n.get("video"):
        # niente testo alternativo: Instagram non lo accetta per i Reel
        parametri = {"media_type": "REELS", "video_url": n["video"], "caption": testo_instagram(n),
                     "share_to_feed": "true"}
        if n.get("video_copertina"):  # secondo del video da usare come copertina del Reel
            parametri["thumb_offset"] = str(int(float(n["video_copertina"]) * 1000))
        attese = 100  # un video può richiedere qualche minuto (~5)
    else:
        parametri = {"image_url": n["immagine"], "caption": n.get("_testo") or testo_instagram(n)}
        alt = n["_alt"] if "_alt" in n else alt_news(n)[0]  # _alt: pagina unica della Parola
        if alt:
            parametri["alt_text"] = alt
        attese = 40  # fino a ~2 minuti: con più post di fila Instagram rallenta
    c = con_luogo(lambda par: con_alt(lambda q: graph_post(f"{IG_USER_ID}/media", q), par, "alt_text"),
                  parametri, "location_id")
    cid = c["id"]
    for _ in range(attese):
        stato = graph_get(cid, {"fields": "status_code"}).get("status_code")
        if stato == "FINISHED":
            break
        if stato in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram ha rifiutato l'immagine {n['immagine']} (stato {stato})")
        time.sleep(3)
    else:
        raise RuntimeError(f"Instagram non ha finito di elaborare l'immagine (stato {stato}): si riprova al prossimo giro")
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


# ---------------------------------------------------------------- Parola della domenica

SITO = "https://www.misericordia-ariccia.it"
PAROLA_DIR = RADICE / ".github/social/parola"
LITURGIA = SITO + "/liturgia-del-giorno/"
HASHTAG_PAROLA = "#ParolaDiDio #VangeloDellaDomenica #MisericordiaAriccia #Misericordie #Ariccia"


def oggi_roma():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("Europe/Rome"))
    except Exception:  # noqa: BLE001 — senza tzdata: UTC+1 basta per la data
        return dt.datetime.utcnow() + dt.timedelta(hours=1)


def immagini_parola(s):
    """URL delle pagine del carosello: copertina (se c'è l'opera) e una per versetto."""
    n = len(s["pagine"]) + (1 if s.get("opera") else 0)
    return [f"{SITO}/img/parola/{s['data']}-{k}.jpg" for k in range(1, n + 1)]


# il campo «illustra» della scheda comincia con il nome della lettura (es. «Vangelo, Mt 22,34-40»)
LETTURE_CON_ARTICOLO = (("Vangelo", "il Vangelo"), ("Prima lettura", "la prima lettura"),
                        ("Seconda lettura", "la seconda lettura"), ("Salmo", "il Salmo"))


def con_articolo(illustra):
    for nome, articolato in LETTURE_CON_ARTICOLO:
        if illustra.startswith(nome):
            return articolato + illustra[len(nome):]
    return f"il brano {illustra}"


def alt_parola(s):
    """Testi alternativi delle pagine del carosello, nello stesso ordine di immagini_parola: la copertina
    (se c'è l'opera) e una pagina per versetto; l'ultima rimanda alle letture complete sul sito. Si ricavano
    solo dai dati della scheda, quindi valgono con la grafica nazionale (dal 25/10/2026) come con la precedente."""
    testi = []
    o = s.get("opera")
    if o:
        g = dt.date.fromisoformat(s["data"])
        opera = f"L'opera «{o['titolo']}» di {o['autore']}" + (f" ({o['anno']})" if o.get("anno") else "")
        if (o.get("illustra") or "").strip():
            opera += f" illustra {con_articolo(o['illustra'].strip())}"
        scena = (o.get("scena") or "").strip()
        opera += f": {scena}" if scena else ""
        opera += "" if opera[-1] in ".!?…" else "."
        testi.append(testo_alt(f"La Parola della domenica: {s['giorno_liturgico']}, "
                               f"{g.day} {MESI[g.month - 1]} {g.year}. {opera}"))
    for i, v in enumerate(s["pagine"]):
        t = f"{v['lettura']}, {v['riferimento']}: «{v['versetto'].strip()}»"
        if i == len(s["pagine"]) - 1:
            t += " Tutte le letture di oggi sul nostro sito: misericordia-ariccia.it/liturgia-del-giorno."
        testi.append(testo_alt(t))
    return testi


def blocco_papi(s):
    """«Le parole dei Papi» (dal 30/10/2026, facoltative): un brano breve del commento alle letture che Vatican News
    pubblica nella pagina del Vangelo del giorno, copiato esatto e con la fonte. Solo testo, nessuna pagina in più."""
    p = s.get("parole_papi") or {}
    if not (p.get("testo") or "").strip() or not (p.get("fonte") or "").strip():
        return ""
    return f"🕊️ Le parole dei Papi\n«{p['testo'].strip()}»\n({p['fonte'].strip()}; fonte: Vatican News)"


def testo_parola(s, rete, con_papi=True):
    righe = [f"📖 La Parola della domenica · {s['giorno_liturgico']}"]
    righe += [f"«{v['versetto']}»\n({v['lettura']}, {v['riferimento']})" for v in s["pagine"]]
    if con_papi and blocco_papi(s):
        righe.append(blocco_papi(s))
    if s.get("testo_social"):
        righe.append(s["testo_social"])
    o = s.get("opera")
    if o:
        righe.append(f"🎨 In copertina: {o['autore']}, {o['titolo']}" + (f" ({o['anno']})" if o.get("anno") else "")
                     + (f", {o['luogo']}" if o.get("luogo") else "") + f" · illustra {o['illustra']} · pubblico dominio")
    if rete == "instagram":
        righe.append("📖 Tutte le letture della domenica sul nostro sito: misericordia-ariccia.it/liturgia-del-giorno")
        righe.append(HASHTAG_PAROLA)
        testo = "\n\n".join(righe)
        if len(testo) > 2200 and con_papi and blocco_papi(s):
            # oltre il limite di Instagram il brano dei Papi si lascia fuori, mai link e hashtag
            # (letture.py --controlla e la prova dei controlli lo segnalano già in preparazione)
            print("instagram: testo oltre 2200 caratteri, esce senza «Le parole dei Papi»", file=sys.stderr)
            return testo_parola(s, rete, con_papi=False)
        return testo[:2200]
    righe.append(f"📖 Leggi tutte le letture della domenica sul nostro sito:\n👉 {LITURGIA}")
    return "\n\n".join(righe)


def attendi_contenitore(cid, attese=40):
    for _ in range(attese):
        stato = graph_get(cid, {"fields": "status_code"}).get("status_code")
        if stato == "FINISHED":
            return
        if stato in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram ha rifiutato il contenitore {cid} (stato {stato})")
        time.sleep(3)
    raise RuntimeError(f"Instagram non ha finito di elaborare {cid}: si riprova al prossimo giro")


def facebook_album(immagini, testo, alt=None):
    """Un solo post con più foto: si caricano non pubblicate, ognuna col suo testo alternativo
    (alt_text_custom), poi si allegano al post."""
    alt = alt or [""] * len(immagini)
    foto = [con_alt(lambda q: graph_post(f"{PAGE_ID}/photos", q),
                    {"url": u, "published": "false", "alt_text_custom": a}, "alt_text_custom")["id"]
            for u, a in zip(immagini, alt)]
    parametri = {"message": testo}
    for i, fid in enumerate(foto):
        parametri[f"attached_media[{i}]"] = json.dumps({"media_fbid": fid})
    return con_luogo(lambda par: graph_post(f"{PAGE_ID}/feed", par), parametri, "place")["id"]


def instagram_carosello(immagini, testo, alt=None):
    """Carosello Instagram: un contenitore per pagina, ognuno col suo testo alternativo (alt_text)."""
    alt = alt or [""] * len(immagini)
    if len(immagini) == 1:
        return pubblica_instagram({"immagine": immagini[0], "_testo": testo, "_alt": alt[0]})
    figli = []
    for u, a in zip(immagini, alt):
        cid = con_alt(lambda q: graph_post(f"{IG_USER_ID}/media", q),
                      {"image_url": u, "is_carousel_item": "true", "alt_text": a}, "alt_text")["id"]
        attendi_contenitore(cid)
        figli.append(cid)
    c = con_luogo(lambda par: graph_post(f"{IG_USER_ID}/media", par),
                  {"media_type": "CAROUSEL", "children": ",".join(figli), "caption": testo}, "location_id")
    attendi_contenitore(c["id"])
    return graph_post(f"{IG_USER_ID}/media_publish", {"creation_id": c["id"]})["id"]


def pubblica_parola(giorno=None):
    """Pubblica il carosello del giorno: album su Facebook, carosello su Instagram, una volta sola."""
    giorno = giorno or oggi_roma().date().isoformat()
    file = PAROLA_DIR / f"{giorno}.json"
    if not file.exists():
        print(f"::warning::Nessuna Parola della domenica per il {giorno} ({file.relative_to(RADICE)} manca)")
        return 1
    s = json.loads(file.read_text(encoding="utf-8"))
    immagini = immagini_parola(s)
    alt = alt_parola(s)
    for u in immagini:
        try:
            with urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=30) as r:
                if not r.headers.get("Content-Type", "").startswith("image/jpeg"):
                    raise RuntimeError(f"tipo {r.headers.get('Content-Type')}")
        except Exception as e:  # noqa: BLE001
            if not DRY_RUN:
                print(f"ERRORE: la pagina {u} non è online ({e}): serve il deploy", file=sys.stderr)
                return 1
            print(f"(prova) non ancora online: {u}")
    chiave = f"parola-{giorno}"
    reg = carica_registro()
    voce = reg.get(chiave, {})
    prova = DRY_RUN or not (PAGE_ID and PAGE_TOKEN)
    errori = 0
    for rete in ("facebook", "instagram"):
        if rete in voce:
            print(f"{rete}: già pubblicata ({voce[rete]})")
            continue
        testo = testo_parola(s, rete)
        chiave_alt = "alt_text" if rete == "instagram" else "alt_text_custom"
        if prova:
            print(f"{rete}: pubblicherebbe {len(immagini)} immagini con il testo →\n"
                  + "\n".join("   " + r for r in testo.splitlines()))
            print(f"{rete}: testo alternativo di ogni pagina ({chiave_alt}) →")
            for u, a in zip(immagini, alt):
                print(f"   {u.rsplit('/', 1)[1]}: {a}")
            continue
        if rete == "instagram" and not IG_USER_ID:
            continue
        entro = os.environ.get("PAROLA_ENTRO", "")  # es. "07:00": dopo, la Parola non esce più (Messe)
        if entro and oggi_roma().strftime("%H:%M") >= entro:
            errori += 1
            print(f"{rete}: NON pubblicata, sono passate le {entro} (regola del 18/10/2026)", file=sys.stderr)
            continue
        try:
            print(f"{rete}: testo alternativo ({chiave_alt}) su {sum(1 for a in alt if a)} pagine su {len(immagini)}")
            pid = (facebook_album(immagini, testo, alt) if rete == "facebook"
                   else instagram_carosello(immagini, testo, alt))
            reg.setdefault(chiave, {})[rete] = pid
            salva_registro(reg)
            print(f"{rete}: pubblicata (id {pid})")
        except Exception as e:  # noqa: BLE001
            errori += 1
            print(f"{rete}: ERRORE — {e}", file=sys.stderr)
    return 1 if errori else 0


# ---------------------------------------------------------------- main

def main():
    if "--parola" in sys.argv:
        resto = [a for a in sys.argv[1:] if a != "--parola"]
        return pubblica_parola(resto[0] if resto else None)
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
        reti["facebook_reel"] = pubblica_facebook_reel  # solo per le news con video
    if IG_USER_ID and PAGE_TOKEN:
        reti["instagram"] = pubblica_instagram
    prova = DRY_RUN or not reti
    if prova:
        print("MODALITÀ PROVA: nessuna pubblicazione reale" + ("" if reti else " (credenziali Meta assenti)"))
        reti = {"facebook": None, "facebook_reel": None, "instagram": None}

    fatte, errori = 0, 0
    if not prova:
        luogo_post()  # sempre nel log, anche quando non c'è niente da pubblicare
    if AGGIORNA_FB and PAGE_ID and PAGE_TOKEN:
        try:
            if AGGIORNA_FB == "elenco":
                elenca_facebook()
            else:
                aggiorna_facebook(news, reg, prova)
        except Exception as e:  # noqa: BLE001
            errori += 1
            print(f"ERRORE su Facebook: {e}", file=sys.stderr)
    if RIPUBBLICA_IG:
        print(f"Ripubblicazione Instagram di {len(RIPUBBLICA_IG)} news")
        try:
            cancella_instagram(reg, prova)
        except Exception as e:  # noqa: BLE001
            errori += 1
            print(f"ERRORE nella cancellazione: {e}", file=sys.stderr)

    limite = dt.date.today() - dt.timedelta(days=MAX_GIORNI)
    # dalla più vecchia alla più recente, così sui social escono in ordine
    for n in sorted(news, key=lambda x: (x["data"], x["id"])):
        voce = reg.get(n["id"], {})
        # Reel di Facebook solo per le news con video che non lo escludono: la Reels API accetta
        # da 3 a 90 secondi, e per i video più lunghi resta il post con il link (social_reel_facebook: false)
        mancanti = [r for r in reti if r not in voce
                    and (r != "facebook_reel" or (n.get("video") and n.get("reel_facebook", True)))]
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
            if rete == "instagram" and not n.get("video") and not n["immagine"].lower().endswith((".jpg", ".jpeg")):
                print("   instagram: saltato (serve un'immagine JPEG nella news o 'immagine:' nel front matter)")
                if not prova:
                    reg.setdefault(n["id"], {})[rete] = "saltato: nessuna immagine JPEG"
                    salva_registro(reg)
                continue
            if prova:
                testo = testo_instagram(n) if rete == "instagram" else testo_facebook(n)
                formato = " come Reel" if (rete == "facebook_reel" or (rete == "instagram" and n.get("video"))) else ""
                print(f"   {rete}: pubblicherebbe{formato} →\n" + "\n".join("      " + r for r in testo.splitlines()))
                if rete == "instagram":
                    print(f"   {rete}: {riga_alt_instagram(n)}")
                continue
            try:
                if rete == "instagram":
                    print(f"   {rete}: {riga_alt_instagram(n)}")
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
