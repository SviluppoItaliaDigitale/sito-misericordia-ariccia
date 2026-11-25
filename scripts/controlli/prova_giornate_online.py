#!/usr/bin/env python3
"""Prova della conferma online dei post delle giornate (scripts/pubblica_social.py --giornata), senza rete.

Dal 25/11/2026 un post delle giornate è «uscito» solo quando Meta conferma che è online: lo script scrive
l'indirizzo nel registro e, se pubblicazione o conferma non riescono, riprova nello stesso giro senza
pubblicare due volte. Qui Meta è finto: si controlla che cosa lo script pubblica, conferma e registra.
"""
import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
os.environ.pop("DRY_RUN", None)
import pubblica_social as ps  # noqa: E402

GIORNO = "2026-11-26"
casi = 0


class Risposta:
    headers = {"Content-Type": "image/jpeg"}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def giro(registro, leggi, tentativi="1", pubblica_ok=True):
    """Esegue un giro con Meta finto. `leggi(pid)` è la risposta alla richiesta di conferma (o solleva)."""
    pubblicati = []
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        (t / "giornate").mkdir()
        (t / "giornate" / f"{GIORNO}.json").write_text(
            json.dumps({"testo": "Prova.", "immagine": "/img/giornate/prova.jpg", "alt": "Prova"}), encoding="utf-8")
        reg = t / "pubblicati.json"
        reg.write_text(json.dumps(registro), encoding="utf-8")
        ps.GIORNATE_DIR, ps.REGISTRO = t / "giornate", reg
        ps.PAGE_ID, ps.PAGE_TOKEN, ps.IG_USER_ID, ps.DRY_RUN = "1", "x", "2", False
        ps.urllib.request.urlopen = lambda *a, **k: Risposta()

        def pubblica(rete):
            def f(*a, **k):
                if not pubblica_ok:
                    raise RuntimeError("Meta non risponde")
                pubblicati.append(rete)
                return f"id-{rete}"
            return f
        ps.facebook_album, ps.instagram_carosello = pubblica("facebook"), pubblica("instagram")
        ps.graph_get = lambda pid, par: leggi(pid)
        ps.time.sleep = lambda s: None
        os.environ["GIORNATA_TENTATIVI"] = tentativi
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            esito = ps.giornata_finche_online(GIORNO)
        return esito, pubblicati, json.loads(reg.read_text(encoding="utf-8")).get(f"giornata-{GIORNO}", {})


def attesa(cond, nome):
    global casi
    assert cond, nome
    casi += 1


def online(pid):
    return ({"id": pid, "is_published": True, "permalink_url": "https://www.facebook.com/p/1"} if "facebook" in pid
            else {"id": pid, "permalink": "https://www.instagram.com/p/1/"})


def rotto(pid):
    raise RuntimeError("HTTP 400: Unsupported get request")


# pubblicazione e conferma riuscite: tutto nel registro, esito 0
e, p, v = giro({}, online)
attesa(e == 0 and p == ["facebook", "instagram"] and v.get("facebook_online") and v.get("instagram_online"), "tutto riuscito")
# Meta non conferma: i post restano nel registro (niente doppioni), ma l'esito è 1
e, p, v = giro({}, rotto)
attesa(e == 1 and p == ["facebook", "instagram"] and "facebook" in v and "facebook_online" not in v, "non confermato")
# giro dopo: già nel registro, si chiede solo la conferma e non si ripubblica
e, p, v = giro({f"giornata-{GIORNO}": {"facebook": "id-facebook", "instagram": "id-instagram"}}, online)
attesa(e == 0 and p == [] and v.get("facebook_online") and v.get("instagram_online"), "conferma al giro dopo, senza ripubblicare")
# già confermato: non si chiede più nulla
e, p, v = giro({f"giornata-{GIORNO}": {"facebook": "a", "instagram": "b", "facebook_online": "https://f", "instagram_online": "https://i"}}, rotto)
attesa(e == 0 and p == [], "già confermato")
# Facebook dice «non pubblicato»: non è una conferma
e, p, v = giro({}, lambda pid: {"is_published": False, "permalink_url": "https://www.facebook.com/p/1"} if "facebook" in pid else online(pid))
attesa(e == 1 and "facebook_online" not in v and v.get("instagram_online"), "Facebook non pubblicato")
# indirizzo relativo di Facebook: diventa completo
e, p, v = giro({}, lambda pid: {"is_published": True, "permalink_url": "/1/posts/2"} if "facebook" in pid else online(pid))
attesa(e == 0 and v["facebook_online"] == "https://www.facebook.com/1/posts/2", "indirizzo relativo")
# la conferma fallisce due volte e poi riesce: più tentativi nello stesso giro, una sola pubblicazione
conta = {"n": 0}


def a_singhiozzo(pid):
    conta["n"] += 1
    if conta["n"] <= 2:
        raise RuntimeError("non ancora")
    return online(pid)


e, p, v = giro({}, a_singhiozzo, tentativi="4")
attesa(e == 0 and p == ["facebook", "instagram"] and v.get("facebook_online") and v.get("instagram_online"), "riprova nello stesso giro")
# la pubblicazione non riesce mai: esito 1 dopo i tentativi, registro vuoto
e, p, v = giro({}, online, tentativi="3", pubblica_ok=False)
attesa(e == 1 and v == {}, "pubblicazione mai riuscita")
print(f"Prova della conferma online delle giornate: {casi} casi su {casi} come atteso.")
