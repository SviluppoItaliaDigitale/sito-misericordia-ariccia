#!/usr/bin/env python3
"""Prova del testo alternativo nei post automatici (scripts/pubblica_social.py), sui controlli di ogni PR.

Al posto della Graph API di Meta c'è un sostituto finto di graph_post e graph_get che registra le chiamate. Si
controlla che il testo alternativo arrivi dove Meta lo accetta (alt_text sui contenitori Instagram delle immagini,
anche nel carosello; alt_text_custom sulle foto dell'album Facebook della Parola), che manchi dove non lo accetta
(Reel, post Facebook con link), che una news senza alt esca lo stesso e che, se Meta rifiuta il parametro, il post si
rifaccia una volta senza. Si provano anche i testi della Parola su tutte le schede e, se si passa il feed compilato da
Hugo (public/news/index.json), che ogni news vi abbia l'alt della sua immagine. Nasce il 21/10/2026 con il testo
alternativo nei post. Esce con 1 se un caso non va come deve. Solo libreria standard.
Uso: prova_testo_alternativo.py [public/news/index.json]
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import pubblica_social as ps  # noqa: E402

falliti = []


def attesa(cond, messaggio):
    if not cond:
        falliti.append(messaggio)


class GraphFinta:
    """Registra le chiamate; rifiuta, se richiesto, le richieste con un certo parametro, come farebbe Meta."""

    def __init__(self, rifiuta=None, errore=None, dettaglio=None):
        self.chiamate, self.rifiuta, self.errore, self.dettaglio, self.n = [], rifiuta, errore, dettaglio, 0

    def post(self, percorso, parametri):
        self.chiamate.append((percorso, dict(parametri)))
        if self.rifiuta and self.rifiuta in parametri:
            errore = {"message": f"(#100) {self.errore}", "type": "OAuthException", "code": 100, "fbtrace_id": "prova"}
            if self.dettaglio:
                errore["error_user_msg"] = self.dettaglio
            raise RuntimeError(f"HTTP 400 su {percorso}: {json.dumps({'error': errore})}")
        self.n += 1
        return {"id": f"{self.n}"}

    def get(self, percorso, parametri):
        return {"status_code": "FINISHED"}

    def su(self, fine):
        return [p for c, p in self.chiamate if c.endswith(fine)]


def prepara(graph, luogo=None):
    ps.PAGE_ID, ps.PAGE_TOKEN, ps.IG_USER_ID = "111", "prova", "222"
    ps.graph_post, ps.graph_get = graph.post, graph.get
    ps._luogo["id"] = luogo                 # niente ricerca del luogo su Meta
    ps._alt_rifiutati.clear()
    ps.time.sleep = lambda *_: None


NEWS = {"id": "2026-10-25-prova", "titolo": "Titolo di prova", "url": "https://www.misericordia-ariccia.it/news/prova/",
        "data": "2026-10-25", "sommario": "Sommario di prova.", "social_testo": "", "data_evento": "", "video": "",
        "video_copertina": "", "immagine": "https://www.misericordia-ariccia.it/img/news/prova-grafica.jpg",
        "immagine_alt": "Lo sapevi che… n. 2: Due rintocchi «a caso», tre «a morto»", "social_alt": ""}

# 1. news con immagine: alt_text = alt dell'immagine dell'articolo, sul contenitore dell'immagine
g = GraphFinta(); prepara(g)
attesa(ps.pubblica_instagram(dict(NEWS)) == "2", "news con immagine: pubblicazione non riuscita")
media = g.su("222/media")
attesa(len(media) == 1 and media[0].get("alt_text") == NEWS["immagine_alt"] and media[0]["image_url"] == NEWS["immagine"],
       f"news con immagine: alt_text sbagliato o mancante ({media})")
attesa(len(g.su("media_publish")) == 1, "news con immagine: media_publish non chiamato una volta")

# 2. social_alt del front matter prevale sull'alt dell'immagine
g = GraphFinta(); prepara(g)
ps.pubblica_instagram(dict(NEWS, social_alt="Testo alternativo  scritto\na mano."))
attesa(g.su("222/media")[0].get("alt_text") == "Testo alternativo scritto a mano.", f"social_alt non usato: {g.chiamate}")

# 3. news con video: Reel su Instagram, niente testo alternativo (Meta non lo accetta per i Reel)
g = GraphFinta(); prepara(g)
reel = dict(NEWS, video="https://www.misericordia-ariccia.it/video/prova.mp4")
ps.pubblica_instagram(reel)
media = g.su("222/media")
attesa(media and media[0].get("media_type") == "REELS" and "alt_text" not in media[0], f"Reel con testo alternativo: {media}")
attesa("Reel" in ps.riga_alt_instagram(reel), "riga del log del Reel sbagliata")

# 4. news senza alt: esce lo stesso, senza alt_text, e il log dice perché
g = GraphFinta(); prepara(g)
senza = dict(NEWS, immagine_alt="")
attesa(ps.pubblica_instagram(senza) == "2" and "alt_text" not in g.su("222/media")[0], f"news senza alt: {g.chiamate}")
attesa("social_alt" in ps.riga_alt_instagram(senza), "news senza alt: il log non dice come aggiungerlo")
attesa(ps.alt_news({k: v for k, v in NEWS.items() if k not in ("immagine_alt", "social_alt")})[0] == "",
       "feed senza i campi del testo alternativo: alt inventato")

# 5. Facebook, news: post con link, nessun testo alternativo
g = GraphFinta(); prepara(g)
ps.pubblica_facebook(dict(NEWS))
feed = g.su("111/feed")
attesa(len(feed) == 1 and not any(k.startswith("alt") for k in feed[0]), f"post Facebook con link e testo alternativo: {feed}")

# 6-7. Parola: album Facebook (alt_text_custom su ogni foto) e carosello Instagram (alt_text su ogni pagina)
scheda = json.loads((REPO / ".github/social/parola/2026-10-25.json").read_text(encoding="utf-8"))
immagini, alt = ps.immagini_parola(scheda), ps.alt_parola(scheda)
g = GraphFinta(); prepara(g)
ps.facebook_album(immagini, "testo", alt)
foto = g.su("111/photos")
attesa([f.get("alt_text_custom") for f in foto] == alt and all(f["published"] == "false" for f in foto),
       f"album Facebook: alt_text_custom sbagliati ({foto})")
attesa(len([k for k in g.su("111/feed")[0] if k.startswith("attached_media")]) == len(immagini), "album Facebook: foto non allegate")
g = GraphFinta(); prepara(g)
ps.instagram_carosello(immagini, "testo", alt)
media = g.su("222/media")
figli, contenitore = [m for m in media if m.get("is_carousel_item")], [m for m in media if m.get("media_type") == "CAROUSEL"]
attesa([m.get("alt_text") for m in figli] == alt, f"carosello Instagram: alt_text delle pagine sbagliati ({figli})")
attesa(len(contenitore) == 1 and "alt_text" not in contenitore[0], "carosello Instagram: alt_text sul contenitore del carosello")
g = GraphFinta(); prepara(g)
ps.instagram_carosello(immagini[:1], "testo", alt[:1])
attesa(g.su("222/media")[0].get("alt_text") == alt[0], "Parola di una pagina sola: alt_text mancante")

# 8. Meta rifiuta il parametro: una sola ripresa senza, poi in questo giro non lo si manda più
g = GraphFinta(rifiuta="alt_text", errore="Param alt_text is not valid"); prepara(g)
attesa(ps.pubblica_instagram(dict(NEWS)) == "2", "alt_text rifiutato: il post non è uscito")
media = g.su("222/media")
attesa(len(media) == 2 and "alt_text" in media[0] and "alt_text" not in media[1], f"alt_text rifiutato: riprese sbagliate ({media})")
ps.pubblica_instagram(dict(NEWS))
attesa(len(g.su("222/media")) == 3, "alt_text rifiutato: rimandato nello stesso giro")
g = GraphFinta(rifiuta="alt_text_custom", errore="Invalid parameter"); prepara(g)
ps.facebook_album(immagini, "testo", alt)
foto = g.su("111/photos")
attesa(len(foto) == len(immagini) + 1 and "alt_text_custom" in foto[0] and all("alt_text_custom" not in f for f in foto[1:]),
       f"alt_text_custom rifiutato: riprese sbagliate ({len(foto)} chiamate)")
# errore generico «(#100)» che non dipende dal testo alternativo: una ripresa senza, poi l'errore prosegue
# e il testo alternativo resta per i post seguenti
g = GraphFinta(rifiuta="image_url", errore="Invalid parameter"); prepara(g)
try:
    ps.pubblica_instagram(dict(NEWS))
    falliti.append("errore che non dipende dal testo alternativo: il post risulta uscito")
except RuntimeError:
    pass
attesa(len(g.su("222/media")) == 2 and "alt_text" not in ps._alt_rifiutati,
       f"errore che non dipende dal testo alternativo: riprese sbagliate o alt segnato come rifiutato ({g.su('222/media')})")
# un «(#100)» che nomina l'immagine, l'indirizzo o il luogo non dipende dal testo alternativo: nessuna ripresa senza
for errore, dettaglio in (("Invalid image URL", None), ("url should represent a valid URL", None),
                          ("Invalid parameter", "The image could not be downloaded."),
                          # titolo e messaggio per l'utente Meta li scrive nella lingua della richiesta
                          ("Invalid parameter", "Non è stato possibile scaricare l'immagine."),
                          # messaggio documentato per il codice 100 (sottocodice 2207040)
                          ("Invalid parameter", "Cannot use more than 20 tags per created media.")):
    g = GraphFinta(rifiuta="image_url", errore=errore, dettaglio=dettaglio); prepara(g)
    try:
        ps.pubblica_instagram(dict(NEWS))
        falliti.append(f"«(#100) {errore}»: il post risulta uscito")
    except RuntimeError:
        pass
    attesa(len(g.su("222/media")) == 1 and "alt_text" not in ps._alt_rifiutati,
           f"«(#100) {errore}» ({dettaglio}): ripresa senza testo alternativo ({len(g.su('222/media'))} chiamate)")
# un «(#100)» su un elemento del carosello che nomina is_carousel_item, un altro parametro della stessa richiesta:
# nessuna ripresa senza testo alternativo
g = GraphFinta(rifiuta="is_carousel_item", errore="Param is_carousel_item must be a boolean"); prepara(g)
try:
    ps.instagram_carosello(immagini, "testo", alt)
    falliti.append("«(#100) is_carousel_item»: il carosello risulta uscito")
except RuntimeError:
    pass
attesa(len(g.su("222/media")) == 1 and "alt_text" not in ps._alt_rifiutati,
       f"«(#100) is_carousel_item»: ripresa senza testo alternativo ({len(g.su('222/media'))} chiamate)")
# i nomi degli altri parametri della richiesta: un parametro che non è fra le parole fisse
errore_temporary = RuntimeError('HTTP 400 su 111/photos: {"error":{"message":"(#100) Param temporary must be a '
                                'boolean","code":100}}')
attesa(ps.alt_rifiutato(errore_temporary, "alt_text_custom") is True,
       "«(#100) temporary» senza i parametri della richiesta: dovrebbe riprovare")
attesa(ps.alt_rifiutato(errore_temporary, "alt_text_custom", {"url": "x", "temporary": "true"}) is False,
       "«(#100) temporary» con i parametri della richiesta: non dovrebbe riprovare")
# il testo alternativo nominato solo nel messaggio per l'utente, anche in italiano: si riprova senza
for dettaglio in ("Alt text is too long.", "Il testo alternativo dell'immagine è troppo lungo."):
    g = GraphFinta(rifiuta="alt_text", errore="Invalid parameter", dettaglio=dettaglio); prepara(g)
    attesa(ps.pubblica_instagram(dict(NEWS)) == "2", f"alt nominato nel messaggio per l'utente ({dettaglio}): il post non è uscito")
    attesa(len(g.su("222/media")) == 2 and "alt_text" in ps._alt_rifiutati,
           f"alt nominato nel messaggio per l'utente ({dettaglio}): riprese sbagliate ({g.su('222/media')})")
# il criterio sui testi degli errori: contano messaggio e messaggio per l'utente, non il percorso né le chiavi del JSON
for errore, atteso in (
        ('HTTP 400 su 222/media: {"error":{"message":"(#100) Invalid parameter","code":100}}', True),
        ('HTTP 400 su 111/photos: {"error":{"message":"Invalid parameter","code":100}}', True),
        ('HTTP 400 su 222/media: {"error":{"message":"Param alt_text is not valid","code":9004}}', True),
        ('HTTP 400 su 222/media: {"error":{"message":"(#100) Invalid image URL","code":100}}', False),
        ('HTTP 400 su 111/feed: {"error":{"message":"(#100) Invalid parameter","code":100,'
         '"error_user_msg":"Invalid place id"}}', False),
        ('HTTP 400 su 222/media: {"error":{"message":"Invalid parameter","code":100,'
         '"error_user_msg":"Il testo alternativo dell\'immagine \\u00e8 troppo lungo."}}', True),
        ('HTTP 400 su 222/media: {"error":{"message":"Invalid parameter","code":100,'
         '"error_user_msg":"Non \\u00e8 stato possibile scaricare l\'immagine."}}', False),
        ('HTTP 400 su 222/media: {"error":{"message":"Application request limit reached","code":4}}', False),
        ("HTTP 500 su 222/media: errore del server", False)):
    attesa(ps.alt_rifiutato(RuntimeError(errore), "alt_text") is atteso, f"alt_rifiutato({errore!r}) dovrebbe dare {atteso}")
# un errore che non c'entra non si riprova
g = GraphFinta(); prepara(g)
ps.graph_post = lambda p, q: (_ for _ in ()).throw(RuntimeError("HTTP 500 su 222/media: errore del server"))
try:
    ps.pubblica_instagram(dict(NEWS))
    falliti.append("errore 500: non si è fermato")
except RuntimeError:
    pass
# luogo rifiutato: lo gestisce con_luogo, il testo alternativo resta
g = GraphFinta(rifiuta="location_id", errore="Invalid parameter location_id"); prepara(g, luogo="999")
ps.pubblica_instagram(dict(NEWS))
media = g.su("222/media")
attesa(len(media) == 2 and media[1].get("alt_text") == NEWS["immagine_alt"] and "location_id" not in media[1],
       f"luogo rifiutato: il testo alternativo si è perso ({media})")

# 9. testi della Parola su tutte le schede: uno per pagina, entro 1000 caratteri, senza «immagine di»
for f in sorted((REPO / ".github/social/parola").glob("*.json")):
    s = json.loads(f.read_text(encoding="utf-8"))
    testi = ps.alt_parola(s)
    attesa(len(testi) == len(ps.immagini_parola(s)), f"{f.name}: i testi non sono uno per pagina")
    attesa(all(0 < ps.lunghezza_alt(t) <= ps.LIMITE_ALT for t in testi), f"{f.name}: testo vuoto o oltre {ps.LIMITE_ALT} caratteri")
    attesa(not any(re.search(r"\bimmagine\s+di\b", t, re.I) for t in testi), f"{f.name}: «immagine di» in un testo")
    attesa(testi[-1].endswith(" Tutte le letture di oggi sul nostro sito: misericordia-ariccia.it/liturgia-del-giorno."),
           f"{f.name}: l'ultima pagina non rimanda alle letture: «{testi[-1][-90:]}»")
    for v, t in zip(s["pagine"], testi[-len(s["pagine"]):]):
        attesa(t.startswith(f"{v['lettura']}, {v['riferimento']}: «{v['versetto'].strip()}»"), f"{f.name}: versetto non intero in «{t[:60]}»")
    if s.get("opera"):
        o = s["opera"]
        attesa(all(x in testi[0] for x in ("La Parola della domenica", s["giorno_liturgico"], o["titolo"], o["autore"])),
               f"{f.name}: copertina senza giorno, titolo o autore: «{testi[0]}»")
# 10. testo dei post della Parola: Instagram entro 2200 caratteri con link e hashtag; «Le parole dei Papi»
# (dal 30/10/2026) brevi, con la fonte, in tutti e due i post; se il testo è troppo lungo escono solo da Instagram
for f in sorted((REPO / ".github/social/parola").glob("*.json")):
    s = json.loads(f.read_text(encoding="utf-8"))
    ig, fb = ps.testo_parola(s, "instagram"), ps.testo_parola(s, "facebook")
    attesa(len(ig) <= 2200 and ig.endswith(ps.HASHTAG_PAROLA), f"{f.name}: post Instagram di {len(ig)} caratteri o senza hashtag")
    p = s.get("parole_papi")
    if p:
        attesa(len(p["testo"]) <= 500, f"{f.name}: «Le parole dei Papi» di {len(p['testo'])} caratteri (al massimo 500)")
        for testo in (ig, fb):
            attesa(f"«{p['testo'].strip()}»\n({p['fonte'].strip()}; fonte: Vatican News)" in testo,
                   f"{f.name}: «Le parole dei Papi» o la fonte mancano nel post")
lungo = dict(scheda, parole_papi={"testo": "parola " * 400, "fonte": "Papa Francesco, Angelus, 1° gennaio 2020"})
ig = ps.testo_parola(lungo, "instagram")
attesa(len(ig) <= 2200 and "Le parole dei Papi" not in ig and ig.endswith(ps.HASHTAG_PAROLA),
       "brano dei Papi troppo lungo: Instagram non l'ha lasciato fuori o ha perso gli hashtag")
attesa("Le parole dei Papi" in ps.testo_parola(lungo, "facebook"), "brano dei Papi tolto anche da Facebook")
attesa("Le parole dei Papi" not in ps.testo_parola(scheda, "facebook"), "brano dei Papi in una scheda che non lo ha")

copertina = ps.alt_parola(scheda)[0]
attesa("25 ottobre 2026" in copertina and "illustra il Vangelo, Mt 22,34-40" in copertina and "(1886-1894)" in copertina,
       f"copertina del 25/10/2026: data, lettura o anno mancanti: «{copertina}»")
for illustra, atteso in (("Prima lettura, Es 22,20-26", "la prima lettura, Es 22,20-26"),
                         ("Seconda lettura, 1Ts 1,5-10", "la seconda lettura, 1Ts 1,5-10"),
                         ("Lettera agli Ebrei, Eb 4,12", "il brano Lettera agli Ebrei, Eb 4,12")):
    attesa(ps.con_articolo(illustra) == atteso, f"«{illustra}» con l'articolo: {ps.con_articolo(illustra)}")

# 10. un testo troppo lungo si accorcia a frasi intere
lungo = " ".join(f"Frase numero {i} del testo alternativo, con qualche parola in più per allungarla." for i in range(40))
corto = ps.testo_alt(lungo)
attesa(ps.lunghezza_alt(corto) <= 1000 and corto.endswith("allungarla.") and lungo.startswith(corto), f"testo lungo accorciato male: {ps.lunghezza_alt(corto)}")

# 12. si conta in unità UTF-16 (22/10/2026): un'emoji vale 2, come nel generatore della Protezione Civile e in
# social-pc-genzano. 971 caratteri, 108 dei quali emoji, sono 1079 unità: il testo si accorcia a frasi intere.
attesa(ps.lunghezza_alt("a🙂b") == 4 and ps.lunghezza_alt("città") == 5, "conteggio UTF-16 sbagliato")
con_emoji = " ".join("Frase con emoji 🙂🙂🙂🙂 fra le parole." for _ in range(27))
attesa(len(con_emoji) <= 1000 < ps.lunghezza_alt(con_emoji), f"prova costruita male: {len(con_emoji)}, {ps.lunghezza_alt(con_emoji)}")
corto = ps.testo_alt(con_emoji)
attesa(ps.lunghezza_alt(corto) <= 1000 and corto.endswith("parole.") and con_emoji.startswith(corto),
       f"testo con emoji accorciato male: {ps.lunghezza_alt(corto)} unità")
una_frase = "Parola🙂 " * 200
corto = ps.testo_alt(una_frase)
attesa(ps.lunghezza_alt(corto) <= 1000 and corto.endswith("…") and not corto[:-1].endswith(" "),
       f"frase unica con emoji tagliata male: {ps.lunghezza_alt(corto)} unità, «{corto[-12:]}»")

# 11. feed compilato da Hugo: ogni news ha l'alt della sua immagine (partial news-immagine-alt.html)
if len(sys.argv) > 1:
    news = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["news"]
    norma = lambda t: re.sub(r"\s+", " ", t.replace("’", "'").replace("“", '"').replace("”", '"')).strip()
    controllate = 0
    for n in news:
        attesa("immagine_alt" in n and "social_alt" in n, f"feed: {n['id']} senza i campi immagine_alt e social_alt")
        sorgente = REPO / "content/news" / f"{n['id']}.md"
        if not n.get("immagine") or not sorgente.is_file():
            continue
        for alt_md, src in re.findall(r"!\[([^\]]*)\]\(([^)\s]+)", sorgente.read_text(encoding="utf-8")):
            if n["immagine"].endswith(src) and alt_md.strip():
                controllate += 1
                attesa(norma(n.get("immagine_alt", "")) == norma(alt_md), f"feed: {n['id']} ha l'alt «{n.get('immagine_alt')}» invece di «{alt_md}»")
                break
    attesa(controllate > 0, "feed: nessuna news controllata (feed vuoto o immagini senza alt)")
    print(f"Feed: {controllate} news con l'alt della loro immagine.")

if falliti:
    print("PROVA FALLITA:")
    for f in falliti:
        print(f"  - {f}")
    sys.exit(1)
print("Prova del testo alternativo superata: news con immagine, social_alt, Reel, news senza alt, post con link, "
      "album e carosello della Parola, parametro rifiutato, testi della Parola, testo lungo, conteggio UTF-16.")
