"""Pagine HTML della scuola dell'infanzia che usano i disegni di disegni.py (da colorare, storia, filastrocca).
Si lanciano con: python3 scripts/scuole/infanzia/disegni.py  (riscrive i tre HTML in questa cartella).
"""
from __future__ import annotations

from disegni import (QUI, Tavolozza, ambulanza, telefono, mani_trucco, persona, nonna_seduta, stanza, tavolo,
                     vaso_fiori, porta, fumetto, svg, linea, f, L)

LOGO = '<img class="logo" src="../../grafica-brand/modelli-nazionali/loghi/triangolo-misericordie.png" alt="Logo delle Misericordie">'
TEMA_A4 = "<div class=\"tema\">Per la <b>scuola dell'infanzia</b></div>"
PIEDE = ('<div class="piede"><div class="p1"><span>Confraternita di Misericordia</span><span>di Ariccia ODV</span></div>'
         '<div class="p2"><span>Viale Antonietta Chigi 46 - 00072 Ariccia (RM)</span><span>Cell. +39 328 8105399 - C.F. 90031910582</span></div>'
         '<div class="p3"><span>www.misericordia-ariccia.it</span><span>sede@misericordia-ariccia.it</span></div></div>')
FRECCIA = ('<svg class="freccia" aria-hidden="true" width="94" height="86" viewBox="0 0 94 86" fill="none" stroke="{c}" stroke-width="15" '
           'stroke-linejoin="miter" stroke-miterlimit="10"><path d="M8 8l34 35-34 35"></path><path d="M48 8l34 35-34 35"></path></svg>')
AVVISO = "<!-- Pagina generata da disegni.py: per cambiarla si modifica pagine.py e si rilancia disegni.py. -->"


def testa_html(titolo: str, formato: str, uscita: str, stile: str = "") -> str:
    return (f'<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n<meta name="formato" content="{formato}">\n'
            f'<meta name="uscita" content="static/documenti/scuole/infanzia/{uscita}.pdf">\n<title>{titolo}</title>\n'
            f'<link rel="stylesheet" href="../scuole.css">\n<style>{stile}</style>\n</head>\n')


def pagina_a4(contenuto: str) -> str:
    return f'<section class="pagina">{LOGO}{TEMA_A4}<div class="contenuto">{contenuto}</div>{PIEDE}</section>\n'


# ============================================================================================ disegni da colorare
STILE_COLORA = """
.colora h1 { text-align: center; }
.colora .nome { font-size: 15px; color: #233B74; display: flex; gap: 10px; align-items: flex-end; }
.colora .nome span { flex: 1; border-bottom: 1.5px solid #5A6686; height: 20px; }
.colora .disegno { flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center; }
.colora .disegno svg { width: 100%; height: 100%; }
.colora .frase { font-size: 26px; line-height: 34px; font-weight: 800; color: #233B74; text-align: center; }
.colora .nota-adulti { text-align: center; }
"""


def numeri_mani(riempi: str = "#FFFFFF") -> str:
    """I numeri 1, 1, 2 sotto i tre momenti del trucco dei pollici (viewBox di mani_trucco allungato a 450)."""
    return "".join(f'<text x="{x}" y="420" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="78" '
                   f'fill="{riempi}" stroke="{L}" stroke-width="4" paint-order="stroke">{n}</text>' for x, n in ((160, "1"), (480, "1"), (800, "2")))


def colorare() -> str:
    c = Tavolozza(False)
    lw = 6
    pag = []

    def una(titolo, disegno, frase, nota):
        return pagina_a4(f'<div class="colora" style="display:contents">'
                         f'<div class="nome">Mi chiamo<span></span></div>'
                         f'<h1>{titolo}</h1><div class="disegno">{disegno}</div>'
                         f'<p class="frase">{frase}</p><p class="nota-adulti">{nota}</p></div>')

    a, vb = ambulanza(c, lw)
    pag.append(una("L'ambulanza", svg(a, (vb[0] - 10, vb[1] - 10, vb[2] + 20, vb[3] + 20)),
                   "L'ambulanza porta aiuto a chi sta male.",
                   "Per l'adulto: l'ambulanza la manda il 112, quando c'è un'emergenza."))
    t, vb = telefono(c, lw)
    pag.append(una("Il telefono e il 112", svg(t, (vb[0] - 10, vb[1] - 10, vb[2] + 20, vb[3] + 20)),
                   "Per un pericolo vero si chiama il 112.",
                   "Per l'adulto: il 112 è gratuito e si chiama anche dal cellulare senza credito. Si gioca con un telefono finto, mai con quello vero."))
    m, vb = mani_trucco(c, lw)
    pag.append(una("Pollice, pollice, due pollici", svg(m + numeri_mani(), (0, 0, 960, 450)),
                   "Pollice, pollice, due pollici: 1-1-2!",
                   "Per l'adulto: alza il pollice sinistro (1), poi il destro (1), poi tutti e due insieme (2). È il trucco della Commissione europea."))
    sc = (linea("M10 500 L890 500", lw * .7) + nonna_seduta(400, 500, c, lw, bocca="sorriso", specchio=True) +
          persona(590, 500, "volontaria", c, lw, braccia=([(-46, 70), (-84, 126)], [(26, 72), (30, 146)])) +
          persona(770, 500, "volontario", c, lw))
    pag.append(una("I volontari aiutano", svg(sc, (0, 40, 900, 480)),
                   "La volontaria e il volontario aiutano la nonna.",
                   "Per l'adulto: i volontari e le volontarie della Misericordia indossano la divisa con le strisce che si vedono bene."))
    html = testa_html("Disegni da colorare: il 112 e l'ambulanza", "a4", "disegni-da-colorare", STILE_COLORA)
    return html + f'<body class="a4">\n{AVVISO}\n' + "".join(pag) + "</body>\n</html>\n"


# ============================================================================================ storia (slide)
STILE_STORIA = """
.storia { flex-direction: row !important; align-items: center; gap: 60px !important; }
.storia .testo { width: 700px; flex: none; display: flex; flex-direction: column; gap: 34px; font-size: 54px; line-height: 70px; font-weight: 600; }
.storia .testo strong { font-weight: 800; }
.storia .scena { flex: 1; height: 100%; min-width: 0; display: flex; align-items: center; justify-content: center; }
.storia .scena svg { width: 100%; height: 100%; }
.ricorda ol { font-size: 52px; line-height: 66px; font-weight: 700; gap: 26px !important; }
.ricorda .n { display: inline-flex; width: 74px; height: 74px; border-radius: 50%; background: #FCEB0C; color: #233B74; font-weight: 800;
  align-items: center; justify-content: center; margin-right: 22px; font-size: 46px; }
.ricorda ol { list-style: none; padding-left: 0 !important; }
"""

TEMA_SLIDE = '<div class="tema">Una storia&nbsp;<b>per la scuola dell\'infanzia</b></div>'


def diapo(*parti: str, copertina: bool = False, classe: str = "storia") -> str:
    """parti: i pezzi del contenuto (testo, scena…) e, per ultima, la nota per chi presenta."""
    contenuto, note = "".join(parti[:-1]), parti[-1]
    cl = "diapo copertina" if copertina else "diapo"
    freccia = FRECCIA.format(c="var(--giallo)" if copertina else "#233B74")
    return (f'<section class="{cl}"><div class="banda"></div>{TEMA_SLIDE}{LOGO}'
            f'<div class="contenuto{"" if copertina else " " + classe}">{contenuto}</div>'
            f'<div class="firma-slide">Misericordia di Ariccia</div>{freccia}'
            f'<div class="note-relatore">{note}</div></section>\n')


def storia() -> str:
    c = Tavolozza(True)
    lw = 5
    W, H = 900, 600

    def scena(*parti, vb=(0, 0, W, H)):
        return f'<div class="scena">{svg("".join(parti), vb)}</div>'

    def testo(*p):
        return '<div class="testo">' + "".join(f"<p>{x}</p>" for x in p) + "</div>"

    base = 560  # quota del pavimento
    casa = stanza(c, lw, W, 630)
    d = []
    # 1 copertina
    d.append(diapo('<h1>Flavio e il 112</h1><p class="sotto">Una storia da leggere insieme, per imparare a chiedere aiuto.</p>',
                   "Prima di cominciare: «Chi sa che cos'è un'ambulanza? Chi l'ha vista passare?». Leggete piano, una slide alla volta, "
                   "e lasciate tempo ai bambini per guardare i disegni.", copertina=True))
    # 2
    d.append(diapo(testo("Questo è <strong>Flavio</strong>.", "Oggi è a casa della <strong>nonna</strong>. Il papà è nell'altra stanza."),
                   scena(casa, tavolo(60, base, c, lw), vaso_fiori(170, base - 150, c, lw), persona(420, base, "flavio", c, lw),
                         persona(600, base, "nonna", c, lw), vb=(0, 30, W, 600)),
                   "Domande: «Chi c'è nel disegno? Voi andate a trovare i nonni? Che cosa fate insieme?»"))
    # 3
    d.append(diapo(testo("Oh! La nonna <strong>scivola</strong> e si siede per terra.", "«Non riesco ad alzarmi», dice."),
                   scena(casa, persona(680, base, "flavio", c, lw, bocca="o"),
                         nonna_seduta(250, base, c, lw, bocca="o"), vb=(0, 30, W, 600)),
                   "Domande: «Che cosa è successo alla nonna? Come si sente Flavio, secondo voi?». Rassicurate: la nonna è sveglia e parla, "
                   "ma da sola non riesce ad alzarsi."))
    # 4
    d.append(diapo(testo("Flavio fa un bel respiro.", "Poi <strong>chiama un adulto</strong>: «Papà, vieni!»"),
                   scena(casa, porta(640, base, c, lw), persona(725, base, "papa", c, lw, scala=.92),
                         persona(430, base, "flavio", c, lw, braccia=([(-14, 40), (-20, 88)], [(40, -10), (58, -50)])),
                         nonna_seduta(110, base, c, lw, k=.85),
                         fumetto(300, 60, 300, 110, "Papà, vieni!", (420, 270), c, lw), vb=(0, 30, W, 600)),
                   "Domande: «Che cosa fa Flavio per prima cosa? Chi potete chiamare voi, se a casa o a scuola qualcuno sta male?». "
                   "Messaggio: prima si chiama un adulto vicino, se c'è."))
    # 5
    d.append(diapo(testo("Il papà dice: «Bravo, Flavio!", "Adesso chiamiamo insieme il <strong>112</strong>.»"),
                   scena(casa, nonna_seduta(110, base, c, lw, k=.85), persona(470, base, "flavio", c, lw),
                         persona(640, base, "papa", c, lw, telefono_in_mano=True), vb=(0, 30, W, 600)),
                   "Domande: «Qual è il numero da chiamare quando c'è un pericolo vero?». Fate ripetere tutti insieme: «uno, uno, due»."))
    # 6
    m, vbm = mani_trucco(c, lw)
    t, vbt = telefono(c, lw)
    d.append(diapo(testo("Per ricordare il numero c'è un trucco:", "<strong>pollice, pollice, due pollici</strong>. 1-1-2!"),
                   scena(m, numeri_mani("#FCEB0C"), vb=(0, 0, 960, 450)),
                   "Fate il gesto tutti insieme: pollice sinistro in su (uno), pollice destro in su (uno), tutti e due insieme (due). "
                   "Ripetetelo tre volte. È il trucco suggerito dalla Commissione europea."))
    # 7
    d.append(diapo(testo("Risponde una <strong>voce gentile</strong>.", "Il papà dice <strong>che cosa è successo</strong> e <strong>dove sono</strong>."),
                   scena(casa, persona(470, base, "flavio", c, lw), persona(640, base, "papa", c, lw, telefono_in_mano=True),
                         fumetto(40, 50, 420, 150, "La nonna è caduta\ne non si alza.", (560, 240), c, lw, corpo=36), vb=(0, 30, W, 600)),
                   "Domande: «Che cosa bisogna dire al telefono?». Risposta: che cosa è successo e dove si è. "
                   "Spiegate che chi risponde fa delle domande per aiutare, non bisogna avere paura."))
    # 8
    d.append(diapo(testo("Flavio sa <strong>l'indirizzo</strong> a memoria:", "la via, il numero di casa e il paese.", "Il papà <strong>non riattacca</strong>: ascolta e risponde."),
                   scena(casa, persona(470, base, "flavio", c, lw, braccia=([(-14, 40), (-20, 88)], [(40, -10), (58, -50)])),
                         persona(640, base, "papa", c, lw, telefono_in_mano=True),
                         fumetto(60, 50, 380, 150, "Via…, numero…,\nAriccia!", (450, 280), c, lw, corpo=40), vb=(0, 30, W, 600)),
                   "Domande: «Voi sapete il vostro indirizzo? La via, il numero, il paese?». Compito per casa: impararlo con mamma o papà. "
                   "Spiegate che al telefono del 112 non si chiude finché non lo dice chi risponde."))
    # 9
    a, vba = ambulanza(c, lw)
    d.append(diapo(testo("Ecco l'<strong>ambulanza</strong>!", "Scendono due <strong>soccorritori</strong>, con la divisa."),
                   scena(f'<g transform="translate(10 150) scale(.82)">{a}</g>', persona(640, 420, "volontaria", c, lw, scala=.78),
                         persona(790, 420, "volontario", c, lw, scala=.78), vb=(0, 50, 900, 400)),
                   "Domande: «Avete mai visto un'ambulanza? Di che colore era? Che cosa porta?». L'ambulanza è gratuita e la manda il 112."))
    # 10
    d.append(diapo(testo("I soccorritori aiutano la nonna, con calma e gentilezza.", "La nonna sorride: «<strong>Grazie, Flavio!</strong>»"),
                   scena(casa, nonna_seduta(330, base, c, lw, bocca="sorriso", specchio=True),
                         persona(520, base, "volontaria", c, lw, braccia=([(-46, 70), (-84, 126)], [(26, 72), (30, 146)])),
                         persona(680, base, "volontario", c, lw), persona(830, base, "flavio", c, lw), vb=(0, 30, W, 600)),
                   "Domande: «Come si sente adesso la nonna? E Flavio?». Chiudete con un applauso per Flavio, che ha chiesto aiuto nel modo giusto."))
    # 11
    d.append(diapo('<h2>Ricordi?</h2><ol>'
                   '<li><span class="n">1</span>Chiama un adulto.</li>'
                   '<li><span class="n">2</span>Insieme chiamate il 112.</li>'
                   '<li><span class="n">3</span>Di\' che cosa è successo e dove sei.</li></ol>'
                   '<p><span class="evidenzia">Il 112 non è un gioco.</span></p>',
                   "Ripassate i tre passi. Poi fate il gioco del telefono finto (è nella guida per l'insegnante): mai con un telefono vero, "
                   "perché anche un vecchio telefono senza scheda chiama davvero il 112.", classe="ricorda"))
    html = testa_html("Flavio e il 112: una storia per la scuola dell'infanzia", "slide", "storia-flavio-e-il-112", STILE_STORIA)
    return html + f'<body class="slide">\n{AVVISO}\n' + "".join(d) + "</body>\n</html>\n"


# ============================================================================================ filastrocca
STILE_FILA = """
.fila h1 { text-align: left; }
.fila .versi { font-size: 21px; line-height: 31px; font-weight: 600; color: #233B74; display: flex; flex-direction: column; gap: 14px; }
.fila .versi p:first-child, .fila .versi p:last-child { font-weight: 800; }
.fila .alto { display: flex; gap: 22px; align-items: center; }
.fila .alto svg { width: 210px; flex: none; }
.fila .spazio { flex: 1; border: 2px dashed #5A6686; display: flex; align-items: flex-start; padding: 12px 16px; font-size: 15px; color: #233B74; font-weight: 600; }
"""


def filastrocca() -> str:
    c = Tavolozza(False)
    m, vb = mani_trucco(c, 7)
    versi = ["Pollice, pollice, due pollici in su:<br>uno, uno, due, lo ricordi anche tu!",
             "Se qualcuno sta male, se c'è un pericolo vero,<br>chiama un adulto e non stare in pensiero.",
             "Al telefono parla con voce sicura:<br>di' che cosa è successo, e niente paura.",
             "Di' dove sei: la via, il numero, la città,<br>e resta in linea: l'aiuto arriverà.",
             "Il 112 non è per scherzare:<br>è un numero vero, che serve ad aiutare."]
    corpo = ('<div class="fila" style="display:contents">'
             '<div class="alto"><div><h1>La filastrocca del 112</h1><p class="sotto">Da leggere ad alta voce, tutti insieme, facendo il gesto dei pollici.</p></div>'
             f'{svg(m, (0, 0, 960, 345))}</div>'
             '<div class="versi">' + "".join(f"<p>{v}</p>" for v in versi) + '</div>'
             '<div class="spazio">Disegna qui chi ti può aiutare.</div>'
             '<p class="nota-adulti">Per l\'adulto: prima si chiama un adulto vicino, se c\'è; poi il 112, gratuito, anche dal cellulare senza credito. '
             'Al telefono si dice che cosa è successo e dove, si risponde alle domande e non si riattacca finché non lo dice l\'operatore.</p></div>')
    html = testa_html("La filastrocca del 112", "a4", "filastrocca-del-112", STILE_FILA)
    return html + f'<body class="a4">\n{AVVISO}\n' + pagina_a4(corpo) + "</body>\n</html>\n"


def scrivi_tutto() -> None:
    for nome, fn in (("disegni-da-colorare", colorare), ("storia-flavio-e-il-112", storia), ("filastrocca-del-112", filastrocca)):
        (QUI / f"{nome}.html").write_text(fn(), encoding="utf-8")
        print("scritto", nome + ".html")
