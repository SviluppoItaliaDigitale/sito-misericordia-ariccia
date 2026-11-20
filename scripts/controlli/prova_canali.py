#!/usr/bin/env python3
"""Ogni news di content/news/ dichiara il suo canale nel front matter (`canale:`), scelto leggendo l'articolo
(Alessandro, 20/11/2026: «dividere il sito come hai fatto per quello della pc di Genzano»). Valori ammessi:
misericordia (Dalla Misericordia), informazioni (Informazioni utili), approfondimenti (Approfondimenti); li usano
layouts/partials/canale-articolo.html, la home e l'archivio /news/. Esce con 1 se una news non ha un canale valido.
Con --autotest prova da sé che il controllo riconosce canale mancante, sbagliato e giusto. Solo libreria standard."""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AMMESSI = {"misericordia", "informazioni", "approfondimenti"}
SPIEGA = ("  misericordia    = vita della Confraternita: servizi, eventi, volontari, campagne, corsi, ringraziamenti\n"
          "  informazioni    = notizie di servizio per i cittadini: salute pubblica, guide, notizie da altri enti\n"
          "  approfondimenti = Primo soccorso passo passo, video 3D, «Lo sapevi che…», dossier, fede e divulgazione")


def canale(testo):
    if not testo.startswith("---"):
        return None
    fine = testo.find("\n---", 3)
    fm = testo[3:fine] if fine > 0 else ""
    m = re.search(r'^canale:\s*["\']?([^"\'\s#]+)', fm, re.M)
    return m.group(1).strip().lower() if m else None


def errori_in(file):
    err = []
    for f in file:
        if f.name == "_index.md":
            continue
        v = canale(f.read_text(encoding="utf-8"))
        if v is None:
            err.append(f"{f.relative_to(REPO) if f.is_relative_to(REPO) else f}: manca «canale:»")
        elif v not in AMMESSI:
            err.append(f"{f.relative_to(REPO) if f.is_relative_to(REPO) else f}: canale «{v}» non ammesso")
    return err


def autotest():
    assert canale('---\ntitle: "x"\ncanale: "misericordia"\n---\n') == "misericordia"
    assert canale("---\ncanale: approfondimenti # nota\n---\n") == "approfondimenti"
    assert canale('---\ntitle: "x"\n---\ncanale: "misericordia"\n') is None, "il canale nel testo non vale"
    assert canale('---\ncanale: "territorio"\n---\n') not in AMMESSI
    print("Autotest dei canali: OK")


if __name__ == "__main__":
    if "--autotest" in sys.argv:
        autotest()
        sys.exit(0)
    err = errori_in(sorted((REPO / "content" / "news").glob("*.md")))
    if err:
        print("\n".join(err))
        print(f"\n{len(err)} news senza canale valido. Scegli leggendo l'articolo:\n{SPIEGA}")
        sys.exit(1)
    print("Canale presente e valido in tutte le news.")
