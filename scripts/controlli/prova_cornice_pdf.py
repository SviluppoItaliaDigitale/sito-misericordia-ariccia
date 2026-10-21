#!/usr/bin/env python3
"""Prova della cornice di microtesto nei PDF: rendi.py --cornice FILE.pdf (cornice_pdf.py) e i modelli da stampa.

Costruisce PDF di prova con Chromium e pypdf, ci passa la cornice e guarda il risultato disegnato (pypdfium2): la
cornice cambia solo le quattro strisce del margine; il testo di ogni striscia è fatto di pezzi interi e nessuna lettera
esce dalla sua striscia (il difetto delle strisce verticali con «©», trovato il 21/10/2026, e il controllo del motore
che lo ferma); il tono sul bianco è quello dei modelli; il segno sta nel dizionario Info, letto con pypdf e cercato nei
byte come fa controlla_sito.py; il PDF di partenza non cambia. Prova i rifiuti (nome mancante, scritta o campo del
modulo nel margine, firma su un fondo non libero, PDF protetto o con una firma digitale) e i casi da accettare
(ornamento d'angolo, granello di polvere, pagina ruotata, rifilo, PDF con struttura, nome solo in un campo del modulo,
firma solo nelle pagine senza nome e chiara sul fondo scuro, linguetta al vivo, cornice già fatta). Infine i modelli da
stampa veri: carta intestata e biglietto.
Serve: Playwright con Chromium, pypdf, pypdfium2, numpy. Esce con 1 se un caso non va come deve.
Uso: prova_cornice_pdf.py [--tieni CARTELLA]   (con --tieni i PDF della prova restano lì, da guardare)
"""
import argparse
import contextlib
import datetime
import hashlib
import io
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / ".claude/skills/grafiche-modelli-nazionali"))
import cornice_pdf  # noqa: E402
import rendi  # noqa: E402

np, pypdf, pdfium = cornice_pdf.librerie()
from pypdf.generic import (ArrayObject, ByteStringObject, DecodedStreamObject, DictionaryObject, FloatObject,  # noqa: E402
                           NameObject, NumberObject, TextStringObject)

MM_PT = cornice_pdf.MM_PT
BASE_CSS = (REPO / "scripts/grafica-brand/modelli-nazionali/base.css").as_uri()
ANNO = datetime.date.today().year
PEZZI = {re.sub(r"\s+", "", p) for p in ("MISERICORDIA DI ARICCIA", "www.misericordia-ariccia.it",
                                         "grafica della Confraternita di Misericordia di Ariccia ODV", f"© {ANNO}")}
TONO_SUL_BIANCO = (182, 190, 203)        # il tono della cornice sul bianco nei modelli: 255 + (blu scuro - 255) × 0,3
S = 4                                    # pixel per punto nei disegni di controllo

falliti = []


def attesa(cond, messaggio):
    if not cond:
        falliti.append(messaggio)


def impronta(f: Path) -> str:
    return hashlib.sha256(f.read_bytes()).hexdigest()


# ---------------------------------------------------------------- PDF di prova

def pagina_html(corpo: str, sfondo: str = "#FFFFFF", colore: str = "#1A1A1A", w_mm: float = 210, h_mm: float = 297) -> str:
    return (f'<!doctype html><html lang="it"><head><meta charset="utf-8"><link rel="stylesheet" href="{BASE_CSS}">'
            f'<style>@page{{size:{w_mm}mm {h_mm}mm;margin:0}}html,body{{margin:0}}'
            f'.foglio{{position:relative;width:{w_mm}mm;height:{h_mm}mm;overflow:hidden;background:{sfondo};color:{colore};'
            f'font:10pt/1.45 Montserrat,sans-serif;break-after:page}}.testo{{position:absolute;left:25mm;right:25mm;top:30mm}}'
            f'</style></head><body>{corpo}</body></html>')


def foglio(nome: bool = True, extra: str = "", sfondo: str = "#FFFFFF", colore: str = "#1A1A1A") -> str:
    titolo = "Confraternita di Misericordia di Ariccia ODV" if nome else "Associazione di prova"
    return (f'<div class="foglio" style="background:{sfondo};color:{colore}"><div class="testo"><p><b>{titolo}</b></p>'
            '<p>Lettera di prova per la cornice di microtesto. Il testo sta dentro i margini della pagina, lontano dai '
            'bordi, come in una lettera vera.</p><p>Seconda riga di prova, con qualche parola in più per riempire.</p>'
            f'</div>{extra}</div>')


class Fabbrica:
    def __init__(self, browser, cartella: Path):
        self.browser, self.cartella = browser, cartella

    def pdf(self, nome: str, fogli: list, w_mm: float = 210, h_mm: float = 297, tagged: bool = False) -> Path:
        html = self.cartella / f"{nome}.html"
        html.write_text(pagina_html("".join(fogli), w_mm=w_mm, h_mm=h_mm), encoding="utf-8")
        pagina = self.browser.new_page()
        try:
            pagina.goto(html.as_uri(), wait_until="load")
            pagina.evaluate(rendi.ASPETTA_JS)
            uscita = self.cartella / f"{nome}.pdf"
            pagina.pdf(path=str(uscita), width=f"{w_mm}mm", height=f"{h_mm}mm", print_background=True,
                       margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}, tagged=tagged)
        finally:
            pagina.close()
        html.unlink()
        return uscita


def cornice(file: Path, uscita: Path | None = None, firma: dict | None = None, forza: bool = False, browser=None) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        esito = cornice_pdf.cornice_su_pdf(file, uscita, firma, forza, browser)
    return esito, buffer.getvalue()


# ---------------------------------------------------------------- controllo del risultato

def disegno(pdf: Path, i: int = 0):
    d = pdfium.PdfDocument(str(pdf))
    d.init_forms()
    p = d[i]
    img = p.render(scale=S, rev_byteorder=True).to_numpy().copy()
    tp = p.get_textpage()
    caratteri = [(tp.get_text_range(k, 1), *tp.get_charbox(k)) for k in range(tp.count_chars())]
    altezza = p.get_size()[1]
    tp.close(), p.close(), d.close()
    return img, caratteri, altezza


def strisce_px(img, margine_mm: float, s_mm: float, rifilo_mm: float = 0.0) -> dict:
    """Le quattro strisce della cornice in pixel (origine in alto a sinistra della pagina vista)."""
    mm = S * MM_PT
    h, w = img.shape[:2]
    x0 = y0 = rifilo_mm * mm
    x1, y1 = w - rifilo_mm * mm, h - rifilo_mm * mm
    m, s = margine_mm * mm, s_mm * mm
    return {"alto": (x0 + m + s, y0 + m, x1 - m - s, y0 + m + s), "basso": (x0 + m + s, y1 - m - s, x1 - m - s, y1 - m),
            "sinistra": (x0 + m, y0 + m + s, x0 + m + s, y1 - m - s), "destra": (x1 - m - s, y0 + m + s, x1 - m, y1 - m - s)}


def misure(nome_modello: str) -> tuple[float, float]:
    m = cornice_pdf.misure_modello(nome_modello)
    s_px = round(m["corpo_mm"] * m["px_mm"] + 4)
    return m["margine_mm"], s_px / m["px_mm"]


def confronta(nome: str, senza: Path, con: Path, pagina: int = 0, lati_attesi=cornice_pdf.LATI, rifilo_mm: float = 0.0,
              modello: str = "carta-intestata.html", testo: bool = True) -> None:
    """La cornice cambia solo le strisce dei lati attesi; ogni striscia scritta ha pezzi interi e caratteri dentro."""
    a, _, _ = disegno(senza, pagina)
    b, caratteri, altezza = disegno(con, pagina)
    if a.shape != b.shape:
        falliti.append(f"{nome}: la pagina con la cornice ha un'altra misura ({a.shape} invece di {b.shape})")
        return
    diff = np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2) > 6
    margine_mm, s_mm = misure(modello)
    strisce = strisce_px(b, margine_mm, s_mm, rifilo_mm)
    t = 0.3 * S                                                        # tolleranza: circa 0,1 mm
    dentro = np.zeros_like(diff)
    for lato, (x0, y0, x1, y1) in strisce.items():
        zona = (slice(max(0, int(y0 - t)), int(y1 + t) + 1), slice(max(0, int(x0 - t)), int(x1 + t) + 1))
        cambiata = bool(diff[zona].any())
        attesa(cambiata == (lato in lati_attesi), f"{nome}: striscia {lato} {'senza' if lato in lati_attesi else 'con'} la cornice")
        if lato in lati_attesi:
            dentro[zona] = True
    fuori = int((diff & ~dentro).sum())
    attesa(fuori == 0, f"{nome}: la cornice cambia {fuori} pixel fuori dalle strisce")
    if not testo:
        return
    for lato in lati_attesi:                                            # testo della striscia, letto dal PDF
        x0, y0, x1, y1 = strisce[lato]
        scritti, fuori_striscia = [], 0
        for c, l, bb, r, tt in caratteri:
            cx0, cy0, cx1, cy1 = l * S, (altezza - tt) * S, r * S, (altezza - bb) * S
            cx, cy = (cx0 + cx1) / 2, (cy0 + cy1) / 2
            if not (x0 - t <= cx <= x1 + t and y0 - t <= cy <= y1 + t):
                continue
            scritti.append(c)
            if c.strip() and (cx0 < x0 - 2 * t or cx1 > x1 + 2 * t or cy0 < y0 - 2 * t or cy1 > y1 + 2 * t):
                fuori_striscia += 1
        pezzi = [re.sub(r"\s+", "", p) for p in "".join(scritti).split("·") if p.strip()]
        attesa(bool(pezzi) and all(p in PEZZI for p in pezzi),
               f"{nome}: nella striscia {lato} c'è un pezzo non intero: {''.join(scritti)[:120]!r}")
        attesa(fuori_striscia == 0, f"{nome}: {fuori_striscia} lettere della striscia {lato} escono dalla striscia")


def versi_di_lettura(pdf: Path, pagina: int = 0, modello: str = "carta-intestata.html") -> dict:
    """Per ogni striscia, il verso in cui avanza il testo della cornice nella pagina come la si vede (dopo /Rotate):
    somma dei passi fra un carattere e il successivo, (du, dv) con v verso l'alto. Atteso: alto e basso da sinistra a
    destra (du > 0), destra dall'alto in basso (dv < 0), sinistra dal basso in alto (dv > 0), come nei modelli."""
    r = pypdf.PdfReader(str(pdf)).pages[pagina]
    rot = int(r["/Rotate"]) % 360 if "/Rotate" in r else 0
    crop = cornice_pdf.rettangolo(r["/CropBox"] if "/CropBox" in r else r["/MediaBox"])
    vw, vh = (crop[3] - crop[1], crop[2] - crop[0]) if rot in (90, 270) else (crop[2] - crop[0], crop[3] - crop[1])
    margine_mm, s_mm = misure(modello)
    m, s = margine_mm * MM_PT, s_mm * MM_PT
    d = pdfium.PdfDocument(str(pdf))
    p = d[pagina]
    tp = p.get_textpage()
    passi, ultimo = {x: [0.0, 0.0] for x in cornice_pdf.LATI}, {}
    for k in range(tp.count_chars()):
        if not tp.get_text_range(k, 1).strip():
            continue
        l, b_, r_, t_ = tp.get_charbox(k)
        u, v = cornice_pdf.schermo((l + r_) / 2, (b_ + t_) / 2, crop, rot)
        lato = ("alto" if vh - m - s <= v <= vh - m and m + s <= u <= vw - m - s else
                "basso" if m <= v <= m + s and m + s <= u <= vw - m - s else
                "sinistra" if m <= u <= m + s and m + s <= v <= vh - m - s else
                "destra" if vw - m - s <= u <= vw - m and m + s <= v <= vh - m - s else None)
        if lato:
            if lato in ultimo:
                passi[lato][0] += u - ultimo[lato][0]
                passi[lato][1] += v - ultimo[lato][1]
            ultimo[lato] = (u, v)
    tp.close(), p.close(), d.close()
    return passi


def verso_giusto(nome: str, pdf: Path, pagina: int = 0, lati=cornice_pdf.LATI) -> None:
    passi = versi_di_lettura(pdf, pagina)
    for lato in lati:
        du, dv = passi[lato]
        giusto = {"alto": du > abs(dv), "basso": du > abs(dv), "destra": -dv > abs(du), "sinistra": dv > abs(du)}[lato]
        attesa(giusto, f"{nome}: il testo della striscia {lato} va nel verso sbagliato (passi {du:.0f}, {dv:.0f})")


def toni_della_cornice(pdf: Path, pagina: int = 0) -> list[tuple[int, int, int]]:
    """I colori pieni (rg) dello strato della cornice nella pagina."""
    p = pypdf.PdfReader(str(pdf)).pages[pagina]
    toni = set()
    for nome, x in p["/Resources"]["/XObject"].items():
        if nome.startswith("/MisCornice"):
            for r, g, b in re.findall(rb"([\d.]+) ([\d.]+) ([\d.]+) rg", x.get_object().get_data()):
                toni.add(tuple(round(float(v) * 255) for v in (r, g, b)))
    return sorted(toni)


def ha_segno_nei_byte(pdf: Path) -> bool:
    """Come controlla_sito.py legge i segni, solo con la libreria standard: la chiave /FirmaECornice del dizionario Info
    nei byte del file, con la stringa letterale decodificata (pypdf scrive «-» e «.» come \\055 e \\056)."""
    m = re.search(rb"/FirmaECornice\s*\(((?:\\.|[^\\)])*)\)", pdf.read_bytes())
    if not m:
        return False
    valore = re.sub(rb"\\([0-7]{1,3})", lambda x: bytes([int(x.group(1), 8)]), m.group(1))
    return re.sub(rb"\\(.)", rb"\1", valore).decode("latin-1") == cornice_pdf.MARCATORE


def prova_esito(nome: str, sorgente: Path, esito: int, messaggio: str, atteso: int, frase: str | None = None,
                uscita: Path | None = None, prima: str | None = None) -> None:
    attesa(esito == atteso, f"{nome}: esito {esito} invece di {atteso} ({messaggio.strip()[:300]})")
    if frase:
        attesa(frase in messaggio, f"{nome}: nel messaggio manca «{frase}» ({messaggio.strip()[:300]})")
    if prima:
        attesa(impronta(sorgente) == prima, f"{nome}: il PDF di partenza è cambiato")
    if uscita is not None and atteso == 1:
        attesa(not uscita.exists(), f"{nome}: rifiutato ma il PDF di uscita è stato scritto lo stesso")


# ---------------------------------------------------------------- campi del modulo

def con_campo(sorgente: Path, uscita: Path, rect: list, valore: str, bordo: bool = False) -> Path:
    """Aggiunge alla prima pagina un campo di testo compilato (con il suo aspetto), come un modulo vero."""
    w = pypdf.PdfWriter(clone_from=str(sorgente))
    pagina = w.pages[0]
    helv = w._add_object(DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),
                                           NameObject("/BaseFont"): NameObject("/Helvetica"),
                                           NameObject("/Encoding"): NameObject("/WinAnsiEncoding")}))
    larghezza, altezza = rect[2] - rect[0], rect[3] - rect[1]
    disegno_campo = (f"q 0 0 0 RG 1 w 0.5 0.5 {larghezza - 1} {altezza - 1} re S Q " if bordo else "")
    aspetto = DecodedStreamObject()
    aspetto.set_data((disegno_campo + f"/Tx BMC q BT /Helv 9 Tf 0 g 3 {altezza / 2 - 3:.2f} Td ({valore}) Tj ET Q EMC").encode("latin-1"))
    aspetto.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Form"),
                    NameObject("/BBox"): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(larghezza), FloatObject(altezza)]),
                    NameObject("/Resources"): DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/Helv"): helv})})})
    campo = DictionaryObject({
        NameObject("/Type"): NameObject("/Annot"), NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/FT"): NameObject("/Tx"), NameObject("/T"): TextStringObject("denom"),
        NameObject("/V"): TextStringObject(valore), NameObject("/F"): NumberObject(4),
        NameObject("/Rect"): ArrayObject([FloatObject(x) for x in rect]),
        NameObject("/DA"): TextStringObject("/Helv 9 Tf 0 g"),
        NameObject("/AP"): DictionaryObject({NameObject("/N"): w._add_object(aspetto)})})
    if bordo:
        campo[NameObject("/MK")] = DictionaryObject({NameObject("/BC"): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(0)])})
    rif = w._add_object(campo)
    pagina[NameObject("/Annots")] = ArrayObject([rif])
    w._root_object[NameObject("/AcroForm")] = DictionaryObject({
        NameObject("/Fields"): ArrayObject([rif]), NameObject("/DA"): TextStringObject("/Helv 0 Tf 0 g"),
        NameObject("/DR"): DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/Helv"): helv})})})
    with open(uscita, "wb") as f:
        w.write(f)
    return uscita


# ---------------------------------------------------------------- casi

def casi_pdf(browser, t: Path) -> int:
    fab = Fabbrica(browser, t)
    n = 0

    # 1. lettera pulita col nome: quattro lati, solo le strisce, pezzi interi, tono dei modelli, segno, partenza intatta
    lettera = fab.pdf("lettera", [foglio()])
    prima = impronta(lettera)
    esito, msg = cornice(lettera, browser=browser)
    uscita = t / "lettera-cornice.pdf"
    prova_esito("lettera", lettera, esito, msg, 0, "ok:", prima=prima)
    if uscita.exists():
        confronta("lettera", lettera, uscita)
        verso_giusto("lettera", uscita)
        attesa(TONO_SUL_BIANCO in toni_della_cornice(uscita), f"lettera: tono della cornice sul bianco {toni_della_cornice(uscita)} invece di {TONO_SUL_BIANCO}")
        attesa(cornice_pdf.ha_segno(uscita) and ha_segno_nei_byte(uscita), "lettera: manca il segno nel dizionario Info")
        attesa(not cornice_pdf.ha_segno(lettera), "lettera: il segno è finito nel PDF di partenza")
        contenuto = b"".join(c.get_object().get_data() if hasattr(c.get_object(), "get_data") else b""
                             for c in pypdf.PdfReader(str(uscita)).pages[0]["/Contents"])
        attesa(cornice_pdf.ARTEFATTO in contenuto, "lettera: la cornice non è segnata come decorazione (/Artifact)")
        # 2. una seconda volta non si rifà: né sull'uscita, né sul suo PDF di partenza col segno
        uscita_prima = impronta(uscita)
        esito, msg = cornice(uscita, browser=browser)
        prova_esito("cornice già fatta", uscita, esito, msg, 0, "già fatta")
        attesa(not (t / "lettera-cornice-cornice.pdf").exists() and impronta(uscita) == uscita_prima,
               "cornice già fatta: rifatta lo stesso")
        # 3. stessa uscita del file di partenza: rifiutata
        esito, msg = cornice(lettera, uscita=lettera, browser=browser)
        prova_esito("uscita uguale alla partenza", lettera, esito, msg, 1, "non si cambia", prima=prima)
    n += 3

    # 4. attraverso rendi.py (cornice_su_file), come da riga di comando
    lettera_b = fab.pdf("lettera-b", [foglio()])
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        esito = rendi.cornice_su_file([lettera_b], t / "lettera-b-uscita.pdf", None, False, browser)
    attesa(esito == 0 and (t / "lettera-b-uscita.pdf").exists(), f"rendi.py --cornice su un PDF: {buffer.getvalue()[:300]}")
    n += 1

    # 5. senza il nome: rifiutata e niente uscita; con --firma la firma va dove il fondo è libero, scura sul bianco
    senza_nome = fab.pdf("senza-nome", [foglio(nome=False)])
    prima = impronta(senza_nome)
    esito, msg = cornice(senza_nome, browser=browser)
    prova_esito("senza il nome", senza_nome, esito, msg, 1, "Misericordia di Ariccia", uscita=t / "senza-nome-cornice.pdf", prima=prima)
    esito, msg = cornice(senza_nome, firma={"posizione": "basso-sinistra"}, browser=browser)
    prova_esito("senza il nome, con --firma", senza_nome, esito, msg, 0, "firma a pagina 1", prima=prima)
    if (t / "senza-nome-cornice.pdf").exists():
        img, caratteri, _ = disegno(t / "senza-nome-cornice.pdf")
        attesa(cornice_pdf.NOME in re.sub(r"\s+", " ", "".join(c[0] for c in caratteri)).casefold(),
               "--firma: la firma non si legge nel testo del PDF")
        zona = img[int(img.shape[0] * 0.92):int(img.shape[0] * 0.965), int(img.shape[1] * 0.05):int(img.shape[1] * 0.5)]
        attesa(zona.min() < 90, "--firma: la firma scura sul bianco non si vede in basso a sinistra")
    n += 2

    # 6. firma su un fondo non libero: rifiutata; due pagine, la seconda blu e senza nome: firma solo lì, chiara
    sporca = fab.pdf("firma-sporca", [foglio(nome=False, extra='<p style="position:absolute;left:12mm;bottom:12mm;margin:0;'
                                                         'font:9pt Montserrat">Testo proprio dove andrebbe la firma</p>')])
    esito, msg = cornice(sporca, firma={"posizione": "basso-sinistra"}, browser=browser)
    prova_esito("firma su un fondo con testo", sporca, esito, msg, 1, "fondo uniforme", uscita=t / "firma-sporca-cornice.pdf")
    due = fab.pdf("due-pagine", [foglio(), foglio(nome=False, sfondo="#003F85", colore="#FFFFFF")])
    esito, msg = cornice(due, firma={"posizione": "basso-sinistra"}, browser=browser)
    prova_esito("due pagine, firma solo nella seconda", due, esito, msg, 0, "firma a pagina 2")
    if (t / "due-pagine-cornice.pdf").exists():
        confronta("due pagine, pagina 1", due, t / "due-pagine-cornice.pdf", 0)
        img, _, _ = disegno(t / "due-pagine-cornice.pdf", 1)
        zona = img[int(img.shape[0] * 0.92):int(img.shape[0] * 0.965), int(img.shape[1] * 0.05):int(img.shape[1] * 0.5)]
        attesa(zona.max() > 200, "firma sul fondo blu: non è chiara")
        toni = toni_della_cornice(t / "due-pagine-cornice.pdf", 1)
        sul_blu = tuple(round(c + (255 - c) * 0.3) for c in (0, 63, 133))      # il tono chiaro sul blu #003F85
        attesa(any(max(abs(a - b) for a, b in zip(c, sul_blu)) <= 2 for c in toni), f"cornice sul fondo blu: toni {toni}, atteso {sul_blu}")
    n += 2

    # 7. scritta nel margine in basso (una nota troppo bassa): rifiutata; con --forza la cornice va sugli altri tre lati
    nota = '<p style="position:absolute;left:25mm;bottom:6.3mm;margin:0;font:8pt/1 Montserrat">Nota scritta troppo in basso, dentro il margine.</p>'
    con_nota = fab.pdf("nota", [foglio(extra=nota)])
    esito, msg = cornice(con_nota, browser=browser)
    prova_esito("scritta nel margine", con_nota, esito, msg, 1, "lato basso: nel margine c'è una scritta", uscita=t / "nota-cornice.pdf")
    esito, msg = cornice(con_nota, forza=True, browser=browser)
    prova_esito("scritta nel margine, --forza", con_nota, esito, msg, 0, "alto, sinistra, destra")
    if (t / "nota-cornice.pdf").exists():
        confronta("scritta nel margine, --forza", con_nota, t / "nota-cornice.pdf", lati_attesi=("alto", "sinistra", "destra"))
    n += 2

    # 8. ornamento d'angolo al vivo (triangolo giallo in basso a destra): accettato, strisce accorciate
    angolo = '<div style="position:absolute;right:0;bottom:0;width:0;height:0;border-left:28mm solid transparent;border-bottom:28mm solid #FCEB0C"></div>'
    con_angolo = fab.pdf("angolo", [foglio(extra=angolo)])
    esito, msg = cornice(con_angolo, browser=browser)
    prova_esito("ornamento d'angolo", con_angolo, esito, msg, 0, "alto, basso, sinistra, destra")
    if (t / "angolo-cornice.pdf").exists():
        confronta("ornamento d'angolo", con_angolo, t / "angolo-cornice.pdf")
        a, _, _ = disegno(con_angolo)
        b, _, _ = disegno(t / "angolo-cornice.pdf")
        lato = 28 * S * MM_PT                                             # il triangolo: lati di 28 mm sull'angolo
        yy, xx = np.mgrid[0:b.shape[0], 0:b.shape[1]]
        u, v = xx - (b.shape[1] - lato), b.shape[0] - yy                  # dal vertice in basso a sinistra del triangolo
        sopra = (u >= 0) & (v >= 0) & (v <= u)
        attesa(not ((np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2) > 6) & sopra).any(),
               "ornamento d'angolo: la cornice passa sopra il triangolo")
    n += 1

    # 8 bis. linguetta al vivo (un segno colorato che parte dal bordo ed entra a metà nel margine): accorcia la striscia
    linguetta = '<div style="position:absolute;left:100mm;bottom:0;width:4mm;height:7.3mm;background:#003F85"></div>'
    con_linguetta = fab.pdf("linguetta", [foglio(extra=linguetta)])
    esito, msg = cornice(con_linguetta, browser=browser)
    prova_esito("linguetta al vivo", con_linguetta, esito, msg, 0, "alto, basso, sinistra, destra")
    if (t / "linguetta-cornice.pdf").exists():
        confronta("linguetta al vivo", con_linguetta, t / "linguetta-cornice.pdf")
    n += 1

    # 9. granello di polvere chiaro nel margine: non conta
    granello = '<div style="position:absolute;left:100mm;top:7mm;width:0.7mm;height:0.7mm;border-radius:50%;background:#E4E4E4"></div>'
    con_granello = fab.pdf("granello", [foglio(extra=granello)])
    esito, msg = cornice(con_granello, browser=browser)
    prova_esito("granello di polvere", con_granello, esito, msg, 0, "alto, basso, sinistra, destra")
    n += 1

    # 10. campo del modulo nel margine sinistro (con il bordo): pdfium deve disegnarlo, e quel lato non si usa
    campo_margine = con_campo(lettera, t / "campo-margine.pdf", [15, 400, 60, 416], "prova", bordo=True)
    esito, msg = cornice(campo_margine, browser=browser)
    prova_esito("campo del modulo nel margine", campo_margine, esito, msg, 1, "lato sinistra", uscita=t / "campo-margine-cornice.pdf")
    # 11. il nome solo nel valore di un campo del modulo (come il rendiconto del 5×1000): basta
    campo_nome = con_campo(senza_nome, t / "campo-nome.pdf", [150, 600, 450, 616], "CONFRATERNITA DI MISERICORDIA DI ARICCIA ODV")
    esito, msg = cornice(campo_nome, browser=browser)
    prova_esito("nome in un campo del modulo", campo_nome, esito, msg, 0, "ok:")
    if (t / "campo-nome-cornice.pdf").exists():
        r = pypdf.PdfReader(str(t / "campo-nome-cornice.pdf"))
        attesa("/AcroForm" in r.trailer["/Root"] and "/Annots" in r.pages[0], "nome in un campo del modulo: il campo è sparito")
    n += 2

    # 12. pagina ruotata (/Rotate 90): la cornice segue la pagina come la si vede
    ruotata = t / "ruotata.pdf"
    w = pypdf.PdfWriter(clone_from=str(lettera))
    w.pages[0].rotate(90)
    with open(ruotata, "wb") as f:
        w.write(f)
    esito, msg = cornice(ruotata, browser=browser)
    prova_esito("pagina ruotata", ruotata, esito, msg, 0, "alto, basso, sinistra, destra")
    if (t / "ruotata-cornice.pdf").exists():
        confronta("pagina ruotata", ruotata, t / "ruotata-cornice.pdf", testo=False)
        verso_giusto("pagina ruotata", t / "ruotata-cornice.pdf")
    n += 1

    # 13. rifilo (TrimBox 3 mm dentro il foglio): la cornice si misura dal rifilo
    abbondanza = fab.pdf("abbondanza", [foglio()], w_mm=216, h_mm=303)
    w = pypdf.PdfWriter(clone_from=str(abbondanza))
    mb = [float(x) for x in w.pages[0].mediabox]
    w.pages[0][NameObject("/TrimBox")] = ArrayObject([FloatObject(mb[0] + 3 * MM_PT), FloatObject(mb[1] + 3 * MM_PT),
                                                     FloatObject(mb[2] - 3 * MM_PT), FloatObject(mb[3] - 3 * MM_PT)])
    rifilata = t / "rifilata.pdf"
    with open(rifilata, "wb") as f:
        w.write(f)
    esito, msg = cornice(rifilata, browser=browser)
    prova_esito("rifilo", rifilata, esito, msg, 0, "ok:")
    if (t / "rifilata-cornice.pdf").exists():
        confronta("rifilo", rifilata, t / "rifilata-cornice.pdf", rifilo_mm=3)
    n += 1

    # 14. PDF con struttura (tagged): la struttura resta e la cornice è una decorazione
    con_struttura = fab.pdf("struttura", [foglio()], tagged=True)
    attesa("/StructTreeRoot" in pypdf.PdfReader(str(con_struttura)).trailer["/Root"], "il PDF di prova non ha la struttura")
    esito, msg = cornice(con_struttura, browser=browser)
    prova_esito("PDF con struttura", con_struttura, esito, msg, 0, "ok:")
    if (t / "struttura-cornice.pdf").exists():
        radice = pypdf.PdfReader(str(t / "struttura-cornice.pdf")).trailer["/Root"]
        attesa("/StructTreeRoot" in radice and "/MarkInfo" in radice, "PDF con struttura: la struttura è sparita")
    n += 1

    # 15. PDF protetto: rifiutato
    protetto = t / "protetto.pdf"
    w = pypdf.PdfWriter(clone_from=str(lettera))
    w.encrypt("segreto")
    with open(protetto, "wb") as f:
        w.write(f)
    esito, msg = cornice(protetto, browser=browser)
    prova_esito("PDF protetto", protetto, esito, msg, 1, "protetto", uscita=t / "protetto-cornice.pdf")
    n += 1

    # 15-bis. PDF con una firma digitale (campo /Sig compilato): rifiutato, la cornice la renderebbe non più valida
    firmato = t / "firmato.pdf"
    w = pypdf.PdfWriter(clone_from=str(lettera))
    valore = w._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Sig"), NameObject("/Filter"): NameObject("/Adobe.PPKLite"),
        NameObject("/SubFilter"): NameObject("/adbe.pkcs7.detached"), NameObject("/Contents"): ByteStringObject(b"\0" * 16),
        NameObject("/ByteRange"): ArrayObject([NumberObject(0)] * 4)}))
    campo = w._add_object(DictionaryObject({
        NameObject("/FT"): NameObject("/Sig"), NameObject("/T"): TextStringObject("Firma"), NameObject("/V"): valore,
        NameObject("/Type"): NameObject("/Annot"), NameObject("/Subtype"): NameObject("/Widget"),
        NameObject("/Rect"): ArrayObject([NumberObject(0)] * 4), NameObject("/P"): w.pages[0].indirect_reference}))
    w.pages[0][NameObject("/Annots")] = ArrayObject([campo])
    w._root_object[NameObject("/AcroForm")] = DictionaryObject({NameObject("/Fields"): ArrayObject([campo]),
                                                               NameObject("/SigFlags"): NumberObject(3)})
    with open(firmato, "wb") as f:
        w.write(f)
    prima = impronta(firmato)
    esito, msg = cornice(firmato, browser=browser)
    prova_esito("PDF con firma digitale", firmato, esito, msg, 1, "firma digitale", uscita=t / "firmato-cornice.pdf", prima=prima)
    n += 1

    # 16. il controllo del motore: una riga che esce dalla sua striscia ferma il lavoro (lettere più larghe del previsto)
    originale = cornice_pdf.PREPARA_JS
    cornice_pdf.PREPARA_JS = originale.replace("return true;", "const st = document.createElement('style'); "
                                               "st.textContent = '[data-microtesto] div { letter-spacing: 3px !important }'; "
                                               "document.head.append(st); return true;")
    try:
        larga = fab.pdf("larga", [foglio()])
        esito, msg = cornice(larga, browser=browser)
        prova_esito("riga più lunga della striscia", larga, esito, msg, 1, "esce dalla sua striscia", uscita=t / "larga-cornice.pdf")
    finally:
        cornice_pdf.PREPARA_JS = originale
    n += 1
    return n


def casi_motore(browser) -> int:
    """Strisce verticali piene fino all'ultimo decimo di pixel, con «©»: devono stare intere (text-orientation:sideways);
    con l'impostazione predefinita di Chromium «©» resta dritto e il controllo del motore deve accorgersene."""
    pagina = browser.new_page()
    n = 0
    try:
        pagina.goto(cornice_pdf.MOTORE.as_uri(), wait_until="load")
        W = H = 1200
        pagina.set_viewport_size({"width": W, "height": H})
        for testo in ("© © © © © © © © © © © ©", f"MISERICORDIA DI ARICCIA · www.misericordia-ariccia.it · © {ANNO}"):
            for corpo, dritto in ((10, False), (15.12, False), (15.12, True)):
                pagina.evaluate(cornice_pdf.PREPARA_JS, [W, H])
                if dritto:
                    pagina.evaluate("() => { const st = document.createElement('style'); st.id = 'prova-dritto'; "
                                    "st.textContent = '[data-microtesto] div { text-orientation: mixed !important }'; document.head.append(st); }")
                larghezza = pagina.evaluate(cornice_pdf.MISURA_JS, [f"600 {corpo}px Montserrat", [testo]])[0]
                esito = pagina.evaluate("(o) => window.corniceVettoriale(o)", {
                    "corpo": corpo, "margine": 40, "larghezza": W, "altezza": H, "testo": testo,
                    "strisce": [{"lato": lato, "inizio": 0, "fine": larghezza + 0.5, "fondo": [255, 255, 255]} for lato in cornice_pdf.LATI]})
                if dritto:
                    pagina.evaluate("() => document.getElementById('prova-dritto').remove()")
                    attesa(set(esito["tagliate"]) == {"sinistra", "destra"},
                           f"motore, «{testo[:12]}…» con «©» dritto: il controllo non vede le strisce verticali tagliate ({esito['tagliate']})")
                else:
                    attesa(not esito["tagliate"] and all(s["testo"] == testo for s in esito["strisce"]) and len(esito["strisce"]) == 4,
                           f"motore, «{testo[:12]}…» corpo {corpo}: striscia piena segnata come tagliata ({esito['tagliate']})")
                n += 1
    finally:
        pagina.close()
    return n


def casi_modelli(browser, t: Path) -> int:
    """I modelli da stampa veri, disegnati con e senza la cornice: solo le strisce, pezzi interi, segno nel PDF."""
    n = 0
    for nome, modello in (("carta-intestata", "carta-intestata.html"), ("biglietto-fronte", "biglietto-fronte.html")):
        dati = rendi.leggi_dati(rendi.MODELLI / "esempi" / f"{nome}.json")
        info = rendi.leggi_modello(rendi.trova_modello(dati["modello"]))
        campi = rendi.prepara_campi(info, dati.get("campi", {}), rendi.MODELLI / "esempi")
        senza = rendi.disegna(browser, info, campi, t / f"{nome}-senza.pdf", bozza=True, cornice=False)
        con = rendi.disegna(browser, info, campi, t / f"{nome}.pdf", bozza=True)
        attesa(not con["problemi"] and con["microtesto"] > 0, f"modello {nome}: {con['problemi']}")
        attesa(cornice_pdf.ha_segno(Path(con["file"])) and ha_segno_nei_byte(Path(con["file"])), f"modello {nome}: manca il segno nel PDF")
        attesa(not cornice_pdf.ha_segno(Path(senza["file"])), f"modello {nome}: il segno c'è anche senza la cornice")
        lati = [x for x in cornice_pdf.LATI if x in (info["microtesto"]["lati"] or cornice_pdf.LATI)]
        confronta(f"modello {nome}", Path(senza["file"]), Path(con["file"]), lati_attesi=lati, modello=modello)
        esito, msg = cornice(Path(con["file"]), browser=browser)
        prova_esito(f"modello {nome} passato da --cornice", Path(con["file"]), esito, msg, 0, "già fatta")
        n += 2
    return n


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("--tieni", type=Path, metavar="CARTELLA", help="lascia lì i PDF della prova")
    x = a.parse_args()
    sync_playwright = rendi.importa_playwright()
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        t = x.tieni or Path(tmp)
        t.mkdir(parents=True, exist_ok=True)
        browser = rendi.avvia_browser(p)
        try:
            n = casi_pdf(browser, t) + casi_motore(browser) + casi_modelli(browser, t)
        finally:
            browser.close()
    if falliti:
        print("PROVA FALLITA:")
        for f in falliti:
            print(f"  - {f}")
        return 1
    print(f"Prova della cornice nei PDF superata: {n} casi (PDF costruiti, controllo del motore sulle strisce verticali, "
          "carta intestata e biglietto da visita).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
