#!/usr/bin/env python3
"""Disegni al tratto della scuola dell'infanzia (ambulanza, telefono con l'1-1-2, mani del trucco dei pollici,
volontari, Flavio, la nonna, il papà) in SVG fatto a mano, e le pagine HTML che li usano.
Uso: python3 scripts/scuole/infanzia/disegni.py  →  riscrive disegni-da-colorare.html, storia-flavio-e-il-112.html
e filastrocca-del-112.html in questa cartella; poi si rendono con scripts/scuole/rendi_pdf.py.
Ogni disegno ha due versioni: da colorare (tutto bianco, linee spesse) e a colori (solo i colori del kit nazionale).
"""
from __future__ import annotations

import math
from pathlib import Path

QUI = Path(__file__).resolve().parent
L = "#233B74"  # colore delle linee: il testo del kit nazionale
BLU, GIALLO, AZZURRO, BIANCO = "#003F85", "#FCEB0C", "#009FE3", "#FFFFFF"
TENUE, CHIARO, LINEA, VERDE = "#EEF0F8", "#D9E3F4", "#C9D3E6", "#1E7B34"


class Tavolozza:
    """Colori di riempimento: con colore=False tutto bianco (pagina da colorare)."""

    def __init__(self, colore: bool):
        self.colore = colore

    def __call__(self, c: str) -> str:
        return c if self.colore else BIANCO


def f(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


def pts(p) -> str:
    return " ".join(f"{f(x)},{f(y)}" for x, y in p)


def tubo(d: str, w: float, fill: str, lw: float) -> str:
    """Un tubo con il contorno (braccia, gambe): tratto largo scuro e, sopra, tratto più stretto del colore."""
    return (f'<path d="{d}" fill="none" stroke="{L}" stroke-width="{f(w + 2 * lw)}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{f(w)}" stroke-linecap="round" stroke-linejoin="round"/>')


def forma(d: str, fill: str, lw: float, extra: str = "") -> str:
    return f'<path d="{d}" fill="{fill}" stroke="{L}" stroke-width="{f(lw)}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def linea(d: str, lw: float) -> str:
    return f'<path d="{d}" fill="none" stroke="{L}" stroke-width="{f(lw)}" stroke-linecap="round" stroke-linejoin="round"/>'


def cerchio(cx, cy, r, fill, lw) -> str:
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}" stroke="{L}" stroke-width="{f(lw)}"/>'


def punto(cx, cy, r) -> str:
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{L}"/>'


# ----------------------------------------------------------------------------------------------- ambulanza
def ambulanza(c: Tavolozza, lw: float = 6, scritta: bool = True) -> tuple[str, tuple]:
    """Ambulanza vista di fianco, muso a destra. viewBox 0 0 640 330."""
    s = []
    # carrozzeria del vano sanitario e della cabina, un solo contorno
    s.append(forma("M40 74 Q40 58 56 58 L404 58 Q416 58 416 70 L416 96 L480 96 Q500 96 512 114 L566 196 Q578 212 578 232 "
                   "L578 254 Q578 270 562 270 L56 270 Q40 270 40 254 Z", c(BIANCO), lw))
    # fascia lungo il fianco
    s.append(f'<path d="M40 196 L570 196 Q574 202 576 210 L578 222 L40 222 Z" fill="{c(GIALLO)}" stroke="{L}" stroke-width="{f(lw * .7)}" stroke-linejoin="round"/>')
    # finestrino della cabina
    s.append(forma("M430 112 L476 112 Q488 112 496 124 L534 182 L430 182 Z", c(CHIARO), lw))
    # porta della cabina e maniglia
    s.append(linea("M420 100 L420 266", lw * .7))
    s.append(linea("M436 238 L462 238", lw))
    # porte del vano: finestrino posteriore e porta laterale scorrevole
    s.append(linea("M60 238 L60 254", lw * .6))  # cerniere del portellone posteriore
    # lampeggianti blu sul tetto
    s.append(forma("M436 82 Q436 76 442 76 L486 76 Q492 76 492 82 L492 96 L436 96 Z", c(AZZURRO), lw))
    s.append(forma("M58 44 Q58 38 64 38 L104 38 Q110 38 110 44 L110 58 L58 58 Z", c(AZZURRO), lw))
    # faro e paraurti
    s.append(forma("M556 172 L570 172 Q578 182 578 196 L556 196 Z", c(GIALLO), lw * .8))
    s.append(forma("M560 254 L590 254 Q596 254 596 260 L596 268 Q596 274 590 274 L560 274 Z", c(LINEA), lw * .8))
    s.append(forma("M24 254 L48 254 L48 274 L30 274 Q24 274 24 268 Z", c(LINEA), lw * .8))
    # scritta sul fianco: lettere da colorare
    if scritta:
        s.append(f'<text x="228" y="150" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="40" '
                 f'letter-spacing="1" fill="{c(BLU)}" stroke="{L}" stroke-width="{f(lw * .45)}" paint-order="stroke">AMBULANZA</text>')
    # passaruota e ruote
    for cx in (148, 486):
        s.append(f'<path d="M{cx - 56} 270 A56 56 0 0 1 {cx + 56} 270 Z" fill="{c(TENUE)}" stroke="{L}" stroke-width="{f(lw)}" stroke-linejoin="round"/>')
        s.append(cerchio(cx, 272, 46, c(L) if c.colore else BIANCO, lw))
        s.append(cerchio(cx, 272, 20, c(LINEA), lw))
        s.append(punto(cx, 272, 5))
    s.append(linea("M6 322 L634 322", lw * .7))
    return "".join(s), (0, 0, 640, 330)


# ----------------------------------------------------------------------------------------------- telefono
def telefono(c: Tavolozza, lw: float = 6) -> tuple[str, tuple]:
    """Telefono con la tastiera e il numero 112 sullo schermo. viewBox 0 0 320 580."""
    s = [forma("M64 10 L256 10 Q300 10 300 54 L300 526 Q300 570 256 570 L64 570 Q20 570 20 526 L20 54 Q20 10 64 10 Z", c(BLU), lw)]
    s.append(forma("M52 70 L268 70 Q276 70 276 78 L276 168 Q276 176 268 176 L52 176 Q44 176 44 168 L44 78 Q44 70 52 70 Z", c(BIANCO), lw))
    s.append(forma("M130 34 L190 34 Q196 34 196 40 Q196 46 190 46 L130 46 Q124 46 124 40 Q124 34 130 34 Z", c(L) if c.colore else BIANCO, lw * .6))
    s.append(f'<text x="160" y="152" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="76" '
             f'letter-spacing="6" fill="{c(BLU)}" stroke="{L}" stroke-width="{f(lw * .5)}" paint-order="stroke">112</text>')
    tasti = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]
    for i, t in enumerate(tasti):
        cx, cy = 88 + (i % 3) * 72, 224 + (i // 3) * 70
        fuoco = t in ("1", "2")
        s.append(cerchio(cx, cy, 28, c(GIALLO) if fuoco else c(BIANCO), lw * (1 if fuoco else .75)))
        s.append(f'<text x="{cx}" y="{cy + 11}" text-anchor="middle" font-family="Montserrat" font-weight="{800 if fuoco else 600}" '
                 f'font-size="30" fill="{L}">{t}</text>')
    # tasto verde della chiamata, con la cornetta
    s.append(cerchio(160, 512, 32, c(VERDE), lw))
    s.append(f'<path d="M146 498 Q140 500 140 508 Q142 522 156 530 Q166 536 174 532 L178 526 L170 518 L164 522 Q156 518 152 510 L156 504 L150 496 Z" '
             f'fill="{BIANCO}" stroke="{L}" stroke-width="{f(lw * .45)}" stroke-linejoin="round"/>')
    return "".join(s), (0, 0, 320, 580)


# ----------------------------------------------------------------------------------------------- mani
def mano(c: Tavolozza, lw: float = 6, pelle: str = BIANCO, manica: str = AZZURRO) -> str:
    """Mano destra a pugno con il pollice in su, vista dal dorso delle dita: pollice in alto, quattro dita piegate
    davanti (cinque dita in tutto). Coordinate in un riquadro 0 0 200 330; la mano sinistra è la stessa specchiata."""
    s = []
    # manica
    s.append(forma("M44 264 L156 264 L162 326 L38 326 Z", c(manica), lw))
    # polso e palmo (dietro alle dita)
    s.append(forma("M62 124 Q60 116 72 116 L130 116 Q150 118 150 136 L150 250 Q150 272 128 272 L82 272 Q60 272 60 250 Z", c(pelle), lw))
    # pollice, dritto in su, con l'unghia
    s.append(forma("M66 132 L66 64 Q66 36 92 36 Q118 36 118 64 L118 132 Z", c(pelle), lw))
    s.append(linea("M80 70 Q80 50 92 50 Q104 50 104 70", lw * .6))
    s.append(linea("M74 100 Q92 107 110 100", lw * .6))  # piega del pollice
    # quattro dita piegate: indice, medio, anulare, mignolo (il mignolo più corto)
    dita = [(112, 176), (150, 180), (188, 176), (226, 166)]
    for i, (y, x2) in enumerate(dita):
        h = 38 if i < 3 else 34
        x0 = 118 if i == 0 else 100  # l'indice parte dal pollice
        s.append(forma(f"M{x0} {y} L{x2 - h / 2} {y} A{h / 2} {h / 2} 0 0 1 {x2 - h / 2} {y + h} L{x0} {y + h}", c(pelle), lw))
        s.append(linea(f"M{x2 - h / 2 - 22} {y + 8} Q{x2 - h / 2 - 16} {y + h / 2} {x2 - h / 2 - 22} {y + h - 8}", lw * .5))  # nocca
    return "".join(s)


def mani_trucco(c: Tavolozza, lw: float = 6) -> tuple[str, tuple]:
    """Tre momenti del trucco: pollice sinistro (1), pollice destro (1), tutti e due (2). viewBox 0 0 960 360.
    La mano disegnata va da x 24 a 226 (centro 125) e da y 10 a 330."""
    def m(cx, y, k, specchio):
        sx = -k if specchio else k
        return f'<g transform="translate({f(cx - sx * 125)} {f(y)}) scale({f(sx)} {f(k)})">{mano(c, lw / k)}</g>'
    s = [m(160, 10, 1, True), m(480, 10, 1, False), m(800 - 64, 52, .86, True), m(800 + 64, 52, .86, False)]
    return "".join(s), (0, 0, 960, 345)


# ----------------------------------------------------------------------------------------------- persone
def testa(cx, cy, r, c: Tavolozza, lw, capelli: str = "corti", colore_capelli: str = L, occhiali: bool = False,
          bocca: str = "sorriso", cappello: bool = False) -> str:
    s = []
    ch = c(colore_capelli)
    if capelli == "caschetto":   # caschetto con fiocco (non usato nella storia di Flavio)
        s.append(forma(f"M{cx - r * 1.12} {cy + r * .78} Q{cx - r * 1.3} {cy - r * 1.25} {cx} {cy - r * 1.14} "
                       f"Q{cx + r * 1.3} {cy - r * 1.25} {cx + r * 1.12} {cy + r * .78} Q{cx + r * .9} {cy + r * .9} {cx + r * .7} {cy + r * .78} "
                       f"L{cx - r * .7} {cy + r * .78} Q{cx - r * .9} {cy + r * .9} {cx - r * 1.12} {cy + r * .78} Z", ch, lw))
    if capelli == "crocchia":    # nonna: capelli raccolti
        s.append(cerchio(cx, cy - r * 1.05, r * .38, ch, lw))
        s.append(forma(f"M{cx - r * 1.04} {cy + r * .1} Q{cx - r * 1.1} {cy - r * 1.12} {cx} {cy - r * 1.06} "
                       f"Q{cx + r * 1.1} {cy - r * 1.12} {cx + r * 1.04} {cy + r * .1} Z", ch, lw))
    # orecchie e viso
    if capelli != "caschetto":
        s.append(cerchio(cx - r * .98, cy + r * .1, r * .2, c(BIANCO), lw * .8))
        s.append(cerchio(cx + r * .98, cy + r * .1, r * .2, c(BIANCO), lw * .8))
    s.append(cerchio(cx, cy, r, c(BIANCO), lw))
    if capelli == "caschetto":   # frangetta
        s.append(forma(f"M{cx - r * .92} {cy - r * .2} Q{cx - r * .9} {cy - r * 1.02} {cx} {cy - r} "
                       f"Q{cx + r * .9} {cy - r * 1.02} {cx + r * .92} {cy - r * .2} Q{cx + r * .4} {cy - r * .5} {cx} {cy - r * .48} "
                       f"Q{cx - r * .4} {cy - r * .5} {cx - r * .92} {cy - r * .2} Z", ch, lw))
        fx, fy = cx + r * .72, cy - r * .86  # fiocco
        s.append(forma(f"M{fx} {fy} L{fx - r * .42} {fy - r * .28} L{fx - r * .42} {fy + r * .28} Z M{fx} {fy} L{fx + r * .42} {fy - r * .28} L{fx + r * .42} {fy + r * .28} Z",
                       c(AZZURRO), lw * .7))
        s.append(cerchio(fx, fy, r * .12, c(AZZURRO), lw * .7))
    elif capelli == "crocchia":
        s.append(forma(f"M{cx - r * .96} {cy - r * .1} Q{cx - r * .9} {cy - r * 1.02} {cx} {cy - r} "
                       f"Q{cx + r * .9} {cy - r * 1.02} {cx + r * .96} {cy - r * .1} Q{cx + r * .5} {cy - r * .62} {cx} {cy - r * .62} "
                       f"Q{cx - r * .5} {cy - r * .62} {cx - r * .96} {cy - r * .1} Z", ch, lw))
    elif capelli == "corti":
        s.append(forma(f"M{cx - r * .97} {cy - r * .05} Q{cx - r * 1.02} {cy - r * 1.1} {cx} {cy - r * 1.06} "
                       f"Q{cx + r * 1.02} {cy - r * 1.1} {cx + r * .97} {cy - r * .05} Q{cx + r * .8} {cy - r * .55} {cx + r * .2} {cy - r * .6} "
                       f"Q{cx - r * .7} {cy - r * .6} {cx - r * .97} {cy - r * .05} Z", ch, lw))
    if cappello:                 # berretto dei volontari
        s.append(forma(f"M{cx - r * 1.02} {cy - r * .22} Q{cx - r} {cy - r * 1.18} {cx} {cy - r * 1.16} Q{cx + r} {cy - r * 1.18} {cx + r * 1.02} {cy - r * .22} Z",
                       c(BLU), lw))
        s.append(forma(f"M{cx - r * 1.1} {cy - r * .22} L{cx + r * 1.45} {cy - r * .22} Q{cx + r * 1.5} {cy - r * .02} {cx + r * 1.2} {cy - r * .02} L{cx - r * 1.1} {cy - r * .02} Z",
                       c(BLU), lw * .8))
    # occhi, guance, bocca
    s.append(punto(cx - r * .36, cy + r * .02, r * .1))
    s.append(punto(cx + r * .36, cy + r * .02, r * .1))
    if occhiali:
        s.append(f'<circle cx="{f(cx - r * .36)}" cy="{f(cy + r * .02)}" r="{f(r * .25)}" fill="none" stroke="{L}" stroke-width="{f(lw * .6)}"/>')
        s.append(f'<circle cx="{f(cx + r * .36)}" cy="{f(cy + r * .02)}" r="{f(r * .25)}" fill="none" stroke="{L}" stroke-width="{f(lw * .6)}"/>')
        s.append(linea(f"M{cx - r * .11} {cy + r * .02} L{cx + r * .11} {cy + r * .02}", lw * .6))
    if bocca == "sorriso":
        s.append(linea(f"M{cx - r * .3} {cy + r * .4} Q{cx} {cy + r * .68} {cx + r * .3} {cy + r * .4}", lw * .7))
    elif bocca == "o":
        s.append(f'<ellipse cx="{f(cx)}" cy="{f(cy + r * .5)}" rx="{f(r * .12)}" ry="{f(r * .15)}" fill="none" stroke="{L}" stroke-width="{f(lw * .6)}"/>')
    elif bocca == "dritta":
        s.append(linea(f"M{cx - r * .2} {cy + r * .5} Q{cx} {cy + r * .56} {cx + r * .2} {cy + r * .5}", lw * .7))
    return "".join(s)


def persona(x: float, y: float, tipo: str, c: Tavolozza, lw: float = 5, braccia=None, bocca="sorriso",
            gambe: str = "dritte", telefono_in_mano: bool = False, scala: float = 1.0) -> str:
    """Persona in piedi vista di fronte, piedi a (x, y). tipo: flavio, nonna, papa, volontaria, volontario.
    braccia: (sinistra, destra), ognuna una lista di punti relativi alla spalla (fino alla mano)."""
    k = scala
    adulti = {"nonna": 400, "papa": 440, "volontaria": 420, "volontario": 440}
    H = (260 if tipo == "flavio" else adulti[tipo]) * k
    r = (40 if tipo == "flavio" else 36) * k
    cy_t = y - H + r
    spalla_y = cy_t + r + 14 * k
    anca_y = y - H * (0.40 if tipo == "flavio" else 0.47)
    sw = (36 if tipo == "flavio" else 50) * k
    s = []
    # colori
    abito = {"flavio": GIALLO, "nonna": AZZURRO, "papa": CHIARO, "volontaria": BLU, "volontario": BLU}[tipo]
    calzoni = {"flavio": AZZURRO, "nonna": BIANCO, "papa": BLU, "volontaria": BLU, "volontario": BLU}[tipo]
    gw = (20 if tipo == "flavio" else 26) * k  # larghezza delle gambe
    # gambe e scarpe
    for sx in (-1, 1):
        gx = x + sx * sw * .42
        s.append(tubo(f"M{f(gx)} {f(anca_y)} L{f(gx)} {f(y - 10 * k)}", gw, c(calzoni), lw))
        if tipo in ("volontaria", "volontario"):  # bande riflettenti sui pantaloni
            yb = y - H * .14
            s.append(f'<rect x="{f(gx - gw / 2)}" y="{f(yb)}" width="{f(gw)}" height="{f(9 * k)}" fill="{c(GIALLO)}" stroke="{L}" stroke-width="{f(lw * .5)}"/>')
        s.append(f'<ellipse cx="{f(gx + sx * 8 * k)}" cy="{f(y - 6 * k)}" rx="{f(gw * .85)}" ry="{f(10 * k)}" fill="{c(L) if c.colore else BIANCO}" stroke="{L}" stroke-width="{f(lw)}"/>')
    # braccia (dietro al busto per l'attacco)
    if braccia is None:
        lb = H * .34
        braccia = ([(-lb * .17, lb * .5), (-lb * .2, lb)], [(lb * .17, lb * .5), (lb * .2, lb)])
    manica = c(abito)
    aw = (18 if tipo == "flavio" else 24) * k
    mani = []
    if telefono_in_mano:
        ox, oy = x + (sw - aw * .35), spalla_y + aw * .5
        braccia = (braccia[0], [(56 * k, 70 * k), (x + r * 1.05 - ox, cy_t + r * .45 - oy)])
    for sx, br in zip((-1, 1), braccia):
        ox, oy = x + sx * (sw - aw * .35), spalla_y + aw * .5
        p = [(ox, oy)] + [(ox + dx, oy + dy) for dx, dy in br]
        if len(p) == 3:
            d = f"M{f(p[0][0])} {f(p[0][1])} Q{f(p[1][0])} {f(p[1][1])} {f(p[2][0])} {f(p[2][1])}"
        else:
            d = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in p)
        s.append(tubo(d, aw, manica, lw))
        mani.append(p[-1])
    # busto
    if tipo in ("nonna", "volontaria"):
        orlo_y = y - H * (0.22 if tipo == "flavio" else 0.26)
        largo = sw * (1.35 if tipo != "volontaria" else 1.05)
        if tipo == "volontaria":  # giacca e pantaloni
            orlo_y = anca_y + 18 * k
            largo = sw * 1.02
        s.append(forma(f"M{f(x - sw)} {f(spalla_y + 8 * k)} Q{f(x - sw)} {f(spalla_y)} {f(x - sw + 14 * k)} {f(spalla_y)} "
                       f"L{f(x + sw - 14 * k)} {f(spalla_y)} Q{f(x + sw)} {f(spalla_y)} {f(x + sw)} {f(spalla_y + 8 * k)} "
                       f"L{f(x + largo)} {f(orlo_y)} L{f(x - largo)} {f(orlo_y)} Z", c(abito), lw))
    else:
        orlo_y = anca_y + 18 * k
        s.append(forma(f"M{f(x - sw)} {f(spalla_y + 10 * k)} Q{f(x - sw)} {f(spalla_y)} {f(x - sw + 14 * k)} {f(spalla_y)} "
                       f"L{f(x + sw - 14 * k)} {f(spalla_y)} Q{f(x + sw)} {f(spalla_y)} {f(x + sw)} {f(spalla_y + 10 * k)} "
                       f"L{f(x + sw)} {f(orlo_y)} L{f(x - sw)} {f(orlo_y)} Z", c(abito), lw))
    if tipo in ("volontaria", "volontario"):  # bande riflettenti e scritta sulla giacca
        yb = spalla_y + (orlo_y - spalla_y) * .62
        s.append(f'<rect x="{f(x - sw)}" y="{f(yb)}" width="{f(2 * sw)}" height="{f(12 * k)}" fill="{c(GIALLO)}" stroke="{L}" stroke-width="{f(lw * .5)}"/>')
        s.append(linea(f"M{f(x)} {f(spalla_y + 4 * k)} L{f(x)} {f(orlo_y)}", lw * .5))
    if tipo == "papa":  # colletto
        s.append(linea(f"M{f(x - 14 * k)} {f(spalla_y)} L{f(x)} {f(spalla_y + 18 * k)} L{f(x + 14 * k)} {f(spalla_y)}", lw * .6))
    if tipo == "nonna":  # bottoni del golfino
        for i in range(3):
            s.append(punto(x, spalla_y + 24 * k + i * 24 * k, 3.5 * k))
    # mani
    for mx, my in mani:
        s.append(cerchio(mx, my, aw * .62, c(BIANCO), lw))
    if telefono_in_mano:
        mx, my = mani[1]
        s.append(f'<rect x="{f(mx - 6 * k)}" y="{f(my - 48 * k)}" width="{f(22 * k)}" height="{f(50 * k)}" rx="{f(5 * k)}" fill="{c(BLU)}" stroke="{L}" stroke-width="{f(lw * .8)}"/>')
        s.append(cerchio(mx, my, aw * .62, c(BIANCO), lw))
    # collo e testa
    s.append(f'<rect x="{f(x - 9 * k)}" y="{f(cy_t + r * .8)}" width="{f(18 * k)}" height="{f(spalla_y - cy_t - r * .8 + 2)}" fill="{c(BIANCO)}" stroke="{L}" stroke-width="{f(lw * .8)}"/>')
    cap = {"flavio": ("corti", L), "nonna": ("crocchia", LINEA), "papa": ("corti", L),
           "volontaria": ("crocchia", GIALLO), "volontario": ("corti", L)}[tipo]
    s.append(testa(x, cy_t, r, c, lw, cap[0], cap[1], occhiali=(tipo == "nonna"), bocca=bocca,
                   cappello=False))
    return "".join(s)


def nonna_seduta(x: float, y: float, c: Tavolozza, lw: float = 5, bocca="dritta", k: float = 1.0, specchio: bool = False) -> str:
    if specchio:  # gambe verso sinistra
        return f'<g transform="translate({f(2 * x)} 0) scale(-1 1)">{nonna_seduta(x, y, c, lw, bocca, k)}</g>'
    """La nonna seduta per terra, gambe distese verso destra; piedi della seduta a quota y (pavimento)."""
    s = []
    r = 36 * k
    anca_x, anca_y = x, y - 26 * k
    # gambe distese
    for i, dy in enumerate((-6, 10)):
        s.append(tubo(f"M{f(anca_x)} {f(anca_y + dy * k)} L{f(anca_x + 170 * k)} {f(anca_y + dy * k + 6 * k)}", 26 * k, c(BIANCO), lw))
    for dy in (-6, 10):
        s.append(f'<ellipse cx="{f(anca_x + 182 * k)}" cy="{f(anca_y + dy * k)}" rx="{f(12 * k)}" ry="{f(20 * k)}" fill="{c(L) if c.colore else BIANCO}" stroke="{L}" stroke-width="{f(lw)}"/>')
    # gonna sulle ginocchia
    s.append(forma(f"M{f(x - 44 * k)} {f(y - 4 * k)} L{f(x + 110 * k)} {f(y - 4 * k)} Q{f(x + 118 * k)} {f(y - 30 * k)} {f(x + 100 * k)} {f(y - 52 * k)} "
                   f"L{f(x - 20 * k)} {f(y - 70 * k)} Z", c(AZZURRO), lw))
    # busto
    spalla_y = y - 190 * k
    sw = 48 * k
    s.append(tubo(f"M{f(x - sw + 10 * k)} {f(spalla_y + 14 * k)} Q{f(x - sw - 34 * k)} {f(spalla_y + 80 * k)} {f(x - sw - 30 * k)} {f(y - 14 * k)}", 24 * k, c(AZZURRO), lw))
    s.append(forma(f"M{f(x - sw)} {f(spalla_y + 8 * k)} Q{f(x - sw)} {f(spalla_y)} {f(x - sw + 14 * k)} {f(spalla_y)} L{f(x + sw - 14 * k)} {f(spalla_y)} "
                   f"Q{f(x + sw)} {f(spalla_y)} {f(x + sw)} {f(spalla_y + 8 * k)} L{f(x + sw + 6 * k)} {f(y - 50 * k)} L{f(x - sw - 6 * k)} {f(y - 50 * k)} Z", c(AZZURRO), lw))
    for i in range(3):
        s.append(punto(x, spalla_y + 24 * k + i * 26 * k, 3.5 * k))
    # braccio destro appoggiato sul ginocchio
    s.append(tubo(f"M{f(x + sw - 10 * k)} {f(spalla_y + 14 * k)} Q{f(x + sw + 24 * k)} {f(spalla_y + 70 * k)} {f(x + sw + 50 * k)} {f(y - 66 * k)}", 24 * k, c(AZZURRO), lw))
    s.append(cerchio(x - sw - 30 * k, y - 14 * k, 15 * k, c(BIANCO), lw))
    s.append(cerchio(x + sw + 50 * k, y - 66 * k, 15 * k, c(BIANCO), lw))
    cy_t = spalla_y - 14 * k - r
    s.append(f'<rect x="{f(x - 9 * k)}" y="{f(cy_t + r * .8)}" width="{f(18 * k)}" height="{f(spalla_y - cy_t - r * .8 + 2)}" fill="{c(BIANCO)}" stroke="{L}" stroke-width="{f(lw * .8)}"/>')
    s.append(testa(x, cy_t, r, c, lw, "crocchia", LINEA, occhiali=True, bocca=bocca))
    return "".join(s)


# ----------------------------------------------------------------------------------------------- scene
def stanza(c: Tavolozza, lw: float, w=900, h=560, finestra=True) -> str:
    """Fondo della casa: pavimento e finestra."""
    s = [f'<rect x="0" y="{h - 70}" width="{w}" height="70" fill="{c(TENUE)}"/>', linea(f"M0 {h - 70} L{w} {h - 70}", lw * .7)]
    if finestra:
        s.append(forma(f"M{w - 250} 40 L{w - 70} 40 L{w - 70} 250 L{w - 250} 250 Z", c(CHIARO), lw * .8))
        s.append(linea(f"M{w - 160} 40 L{w - 160} 250 M{w - 250} 145 L{w - 70} 145", lw * .6))
    return "".join(s)


def tavolo(x, y, c: Tavolozza, lw) -> str:
    return (forma(f"M{x} {y - 150} L{x + 220} {y - 150} L{x + 220} {y - 132} L{x} {y - 132} Z", c(LINEA), lw) +
            tubo(f"M{x + 20} {y - 132} L{x + 20} {y}", 12, c(LINEA), lw) + tubo(f"M{x + 200} {y - 132} L{x + 200} {y}", 12, c(LINEA), lw))


def vaso_fiori(x, y, c: Tavolozza, lw, k=1.0) -> str:
    """Vaso con tre fiori; base del vaso a (x, y)."""
    s = []
    for dx, h in ((-20, 70), (0, 92), (22, 74)):
        s.append(linea(f"M{x} {y - 40 * k} Q{x + dx * k * .5} {y - (40 + h * .6) * k} {x + dx * k} {y - (40 + h) * k}", lw * .7))
        s.append(cerchio(x + dx * k, y - (40 + h) * k, 11 * k, c(GIALLO), lw * .7))
    s.append(forma(f"M{x - 26 * k} {y - 50 * k} L{x + 26 * k} {y - 50 * k} L{x + 18 * k} {y} L{x - 18 * k} {y} Z", c(AZZURRO), lw * .8))
    return "".join(s)


def porta(x, y, c: Tavolozza, lw, w=170, h=400) -> str:
    """Porta aperta della stanza accanto; base a (x, y)."""
    return (forma(f"M{x} {y} L{x} {y - h} L{x + w} {y - h} L{x + w} {y} Z", c(LINEA), lw * .8) +
            forma(f"M{x + 14} {y} L{x + 14} {y - h + 14} L{x + w - 14} {y - h + 14} L{x + w - 14} {y} Z", c(TENUE), lw * .6))


def fumetto(x, y, w, h, testo: str, coda: tuple, c: Tavolozza, lw, corpo=44) -> str:
    """Nuvoletta con il testo, la coda punta a coda=(x, y)."""
    cx = x + w / 2
    tx, ty = coda
    base = min(max(tx, x + 40), x + w - 80)
    righe = testo.split("\n")
    t0 = y + h / 2 - (len(righe) - 1) * corpo * .6 + corpo * .35
    txt = "".join(f'<text x="{f(cx)}" y="{f(t0 + i * corpo * 1.2)}" text-anchor="middle" font-family="Montserrat" font-weight="700" '
                  f'font-size="{corpo}" fill="{L}">{r}</text>' for i, r in enumerate(righe))
    return (forma(f"M{x + 30} {y} L{x + w - 30} {y} Q{x + w} {y} {x + w} {y + 30} L{x + w} {y + h - 30} Q{x + w} {y + h} {x + w - 30} {y + h} "
                  f"L{base + 50} {y + h} L{tx} {ty} L{base + 14} {y + h} L{x + 30} {y + h} Q{x} {y + h} {x} {y + h - 30} L{x} {y + 30} Q{x} {y} {x + 30} {y} Z",
                  BIANCO, lw) + txt)


def svg(contenuto: str, vb: tuple, classe: str = "", stile: str = "") -> str:
    x, y, w, h = vb
    return (f'<svg class="{classe}" style="{stile}" viewBox="{x} {y} {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-hidden="true" preserveAspectRatio="xMidYMid meet">{contenuto}</svg>')


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(QUI))
    from pagine import scrivi_tutto  # noqa: E402
    scrivi_tutto()
