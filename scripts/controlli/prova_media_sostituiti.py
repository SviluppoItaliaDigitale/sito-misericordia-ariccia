#!/usr/bin/env python3
"""Ferma una PR che sostituisce un video (o la sua copertina) tenendo lo stesso nome del file.

Perché: `.htaccess` lascia tenere i video e le immagini in cache per un mese (max-age=2592000). Un file rifatto con
lo stesso nome arriva sul server, ma chi lo ha già visto continua a vedere il vecchio fino a un mese. È successo il
22/11/2026 con il video del DAE rifatto per la pronuncia: online c'era il nuovo, Alessandro vedeva il vecchio.
Un video rifatto prende un nome nuovo (es. `-2`), e si aggiornano i riferimenti nella news.

Uso:  python3 scripts/controlli/prova_media_sostituiti.py --da-git RIF   (RIF = main, es. HEAD^1 nella PR)
      python3 scripts/controlli/prova_media_sostituiti.py --autotest
Esce con 1 se trova video o copertine modificati (stato M nel confronto con RIF); le altre immagini sostituite
sono solo un avviso.
"""
import re, subprocess, sys

BLOCCA = re.compile(r"^static/(video/.+\.(mp4|webm)|img/video/.+\.(jpe?g|png|webp))$", re.I)
AVVISA = re.compile(r"^static/.+\.(jpe?g|png|webp|gif|mp3|pdf)$", re.I)


def esamina(righe):
    blocca, avvisa = [], []
    for r in righe:
        parti = r.split("\t")
        if len(parti) < 2 or parti[0] != "M":
            continue
        f = parti[1]
        if BLOCCA.match(f):
            blocca.append(f)
        elif AVVISA.match(f):
            avvisa.append(f)
    return blocca, avvisa


def autotest():
    righe = ["M\tstatic/video/dae.mp4", "A\tstatic/video/dae-2.mp4", "M\tstatic/img/video/dae.jpg",
             "M\tstatic/img/news/x-grafica.jpg", "D\tstatic/video/vecchio.mp4", "M\tcontent/news/a.md"]
    b, a = esamina(righe)
    assert b == ["static/video/dae.mp4", "static/img/video/dae.jpg"], b
    assert a == ["static/img/news/x-grafica.jpg"], a
    print("autotest: ok")


def main():
    if "--autotest" in sys.argv:
        return autotest()
    rif = sys.argv[sys.argv.index("--da-git") + 1] if "--da-git" in sys.argv else "origin/main"
    out = subprocess.run(["git", "diff", "--name-status", rif, "HEAD"], capture_output=True, text=True, check=True).stdout
    blocca, avvisa = esamina(out.splitlines())
    for f in avvisa:
        print(f"::warning::{f} sostituito con lo stesso nome: chi lo ha in cache lo vede vecchio fino a un mese.")
    if blocca:
        for f in blocca:
            print(f"::error::{f} sostituito con lo stesso nome: i browser lo tengono in cache un mese e mostrano il vecchio. "
                  "Dai al file rifatto un nome nuovo (es. -2) e aggiorna i riferimenti.")
        sys.exit(1)
    print("Nessun video o copertina sostituiti con lo stesso nome.")


if __name__ == "__main__":
    main()
