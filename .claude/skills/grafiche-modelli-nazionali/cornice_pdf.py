#!/usr/bin/env python3
"""Cornice di microtesto (e, se chiesta, firma «Misericordia di Ariccia») sui PDF già fatti: rendi.py --cornice FILE.pdf.
Il PDF di partenza non cambia: esce FILE-cornice.pdf, con la cornice dei modelli da stampa in ogni pagina e il segno.

Parte della skill grafiche-modelli-nazionali, scritta per Alessandro Cuollo il 21/10/2026 (regola «Firma e cornice di
microtesto» di CLAUDE.md). La cornice è quella dei modelli da stampa, scritta dallo stesso motore
(scripts/grafica-brand/firma-e-cornice.js, corniceVettoriale): testo vettoriale in Montserrat, dentro il margine di
stampa di ogni pagina, con margine, corpo e misure della carta intestata (6 mm, 1,6 mm) o, sotto i 100 mm di lato,
del biglietto da visita (3 mm, 1 mm), letti dai due modelli. Ogni pagina si disegna (pypdfium2, campi del modulo
compresi) e su ogni lato si cerca il tratto più lungo dove il fondo è uniforme da un bordo all'altro della striscia: la
cornice corre solo lì, con il colore pieno calcolato su quel fondo. Ciò che arriva al bordo della pagina (un fondo al
vivo, un ornamento d'angolo) o cambia il fondo (una fascia, un riquadro) accorcia la striscia, come nei modelli; una
scritta, un numero di pagina o la coda di una firma entrati nel margine fermano invece quel lato, perché la cornice gli
starebbe accanto come se ne facesse parte: il lavoro si ferma, salvo --forza (cornice sugli altri lati). Le pagine di
prima restano intatte: il loro contenuto non si riscrive, si avvolge (q … Q) e la cornice si aggiunge sopra come
contenuto decorativo (/Artifact, che i lettori di schermo saltano). Le pagine che hanno già la cornice (di un modello
da stampa, o messa qui in un PDF poi unito ad altri) restano come sono e le altre la ricevono; se ce l'hanno tutte, il
lavoro è già fatto. Il segno sta nel dizionario Info, chiave
/FirmaECornice: lo legge ha_segno() qui sotto, e si trova anche nei byte del file, come i segni dei JPEG e dei PNG che
cerca scripts/controlli/controlla_sito.py. Se nel testo del PDF, compresi i campi del modulo compilati, non c'è
«Misericordia di Ariccia» il lavoro si ferma: il nome va aggiunto al documento, oppure --firma lo scrive in basso nelle
pagine che non l'hanno, solo dove il fondo è libero. Prova: scripts/controlli/prova_cornice_pdf.py.
Librerie: pypdf (BSD-3-Clause) per scrivere il PDF, pypdfium2 (Apache-2.0 o BSD-3-Clause) e numpy per disegnare le
pagine e leggerne il testo, Playwright con Chromium (lo stesso dei modelli) per il testo in Montserrat.
"""
from __future__ import annotations

import io
import math
import re
from pathlib import Path

QUI = Path(__file__).resolve().parent
GRAFICA = QUI.parents[2] / "scripts" / "grafica-brand"            # .claude/skills/<skill> → radice
MOTORE = GRAFICA / "firma-e-cornice.html"
MODELLI = GRAFICA / "modelli-nazionali"
MARCATORE = re.search(r"const MARCATORE = '([^']+)'", (GRAFICA / "firma-e-cornice.js").read_text(encoding="utf-8")).group(1)
CHIAVE = "/FirmaECornice"                       # dizionario Info del PDF
NOME = "misericordia di ariccia"
TESTO_CORNICE = "grafica della confraternita di misericordia di ariccia odv"   # già nella pagina: cornice già fatta
PRIMO_PEZZO = "MISERICORDIA DI ARICCIA"         # ogni lato della cornice lo porta almeno una volta, intero
ARTEFATTO = b"/Artifact <</Type /Pagination /Subtype /Watermark>> BDC"
LATO_PICCOLO_MM = 100                           # sotto: misure del biglietto da visita
UNIFORME = 8                                    # differenza massima (0-255) dei pixel di traverso nella striscia
DERIVA = 24                                     # differenza massima del fondo lungo un tratto (sfumature lente)
GRANELLO_MM = 2                                 # interruzione della striscia più corta di così, debole (scarto ≤
GRANELLO_SCARTO = 48                            # GRANELLO_SCARTO, meno del 20%) e senza segni più netti entro
GRANELLO_ARIA_MM = 3                            # GRANELLO_ARIA_MM: polvere di una scansione, che la cornice può coprire
FORMA_MM = 6                                    # interruzione più lunga e solitaria: il bordo di una forma, non testo
PIXEL_MASSIMI = 30_000_000                      # tetto dei pixel della pagina disegnata
FIRMA = "Misericordia di Ariccia"
FIRMA_MINIMA_PT = 5                             # come la firma dei modelli da stampa
LATI = ("alto", "basso", "sinistra", "destra")
MM_PT = 72 / 25.4


def librerie(solo_pypdf: bool = False):
    try:
        import pypdf
        if solo_pypdf:
            return pypdf
        import numpy
        import pypdfium2
    except ImportError as e:
        raise SystemExit(f"Errore: per la cornice nei PDF servono pypdf, pypdfium2 e numpy ({e.name} non c'è): "
                         "pip install pypdf pypdfium2 numpy")
    return numpy, pypdf, pypdfium2


def misure_modello(nome: str) -> dict:
    """Margine e corpo della cornice e pixel per millimetro di un modello da stampa (le sue <meta>)."""
    t = (MODELLI / nome).read_text(encoding="utf-8")
    larghezza_px = int(re.search(r'<meta name="formato" content="(\d+)x\d+"', t).group(1))
    larghezza_mm = float(re.search(r'<meta name="stampa" content="([\d.]+)x', t).group(1))
    m = dict(x.split("=", 1) for x in re.search(r'<meta name="microtesto" content="([^"]+)"', t).group(1).split())
    return {"modello": nome, "px_mm": larghezza_px / larghezza_mm,
            "margine_mm": float(m["margine"].removesuffix("mm")), "corpo_mm": float(m["corpo"].removesuffix("mm"))}


# ---------------------------------------------------------------- segno

def ha_segno(percorso: Path) -> bool:
    """Vero se il PDF porta il segno di firma e cornice nel dizionario Info."""
    pypdf = librerie(solo_pypdf=True)
    try:
        r = pypdf.PdfReader(str(percorso))
        if r.is_encrypted and not r.decrypt(""):
            return False
        return str((r.metadata or {}).get(CHIAVE, "")) == MARCATORE
    except Exception:
        return False


def marca(percorso: Path) -> None:
    """Scrive il segno nel dizionario Info di un PDF fatto dai modelli (rendi.py, carta intestata e biglietto)."""
    pypdf = librerie(solo_pypdf=True)
    w = pypdf.PdfWriter(clone_from=str(percorso))
    w.add_metadata({CHIAVE: MARCATORE})
    temporaneo = percorso.with_name(percorso.name + ".tmp")
    with open(temporaneo, "wb") as f:
        w.write(f)
    temporaneo.replace(percorso)


# ---------------------------------------------------------------- geometria

def rettangolo(r) -> tuple[float, float, float, float]:
    x = sorted((float(r[0]), float(r[2])))
    y = sorted((float(r[1]), float(r[3])))
    return x[0], y[0], x[1], y[1]


def schermo(x: float, y: float, crop, rot: int) -> tuple[float, float]:
    """Punto della pagina (spazio utente) → punto come lo si vede (ritaglio ruotato di /Rotate, origine in basso a sinistra)."""
    x0, y0, x1, y1 = crop
    return {0: (x - x0, y - y0), 90: (y - y0, x1 - x), 180: (x1 - x, y1 - y), 270: (y1 - y, x - x0)}[rot]


def da_schermo(crop, rot: int) -> tuple[float, ...]:
    """Matrice (a b c d e f) che riporta un punto visto (u, v) nello spazio utente della pagina."""
    x0, y0, x1, y1 = crop
    return {0: (1, 0, 0, 1, x0, y0), 90: (0, 1, -1, 0, x1, y0), 180: (-1, 0, 0, -1, x1, y1), 270: (0, -1, 1, 0, x0, y1)}[rot]


def numero(x: float) -> str:
    t = f"{x:.5f}".rstrip("0").rstrip(".")
    return "0" if t in ("", "-0") else t


# ---------------------------------------------------------------- analisi della pagina disegnata

def segmenti(maschera) -> list[tuple[int, int]]:
    """Tratti consecutivi veri di una sequenza di booleani: [(inizio, fine), ...]."""
    out, i, n = [], 0, len(maschera)
    while i < n:
        if not maschera[i]:
            i += 1
            continue
        j = i
        while j < n and maschera[j]:
            j += 1
        out.append((i, j))
        i = j
    return out


def tratto_libero(np, img, banda, esterno, orizzontale, px_mm):
    """Lungo una striscia della pagina disegnata, il tratto più lungo in cui il fondo è uniforme da un bordo all'altro
    della striscia (nessuna scritta, nessun disegno) e cambia poco. banda ed esterno sono (x0, x1, y0, y1) in pixel:
    la striscia e, alle stesse altezze (o larghezze), la metà esterna del margine, verso il bordo della pagina; px_mm
    sono i pixel per millimetro lungo la striscia. Restituisce (i0, i1, n, colore medio, contenuto) o None.
    Le interruzioni della striscia si guardano una per una:
    - un granello corto e debole, senza segni netti attorno (polvere o rumore di una scansione), non conta;
    - ciò che sta su un fondo diverso da quello principale del margine (dentro una fascia, un riquadro, un'intestazione
      colorata),
      il confine fra due fondi e ciò che arriva al bordo della pagina (un fondo al vivo, un ornamento d'angolo)
      accorciano solo la striscia, come nei modelli; così anche il bordo lungo e solitario di una forma (un riquadro,
      una riga, un cerchio);
    - il resto è contenuto della pagina entrato nel margine, sul suo fondo principale: una scritta, un numero di pagina,
      la coda di una firma. La cornice gli starebbe accanto come se ne facesse parte, e quel lato non si usa.
      contenuto: [(j0, j1), ...] in pixel lungo la striscia."""
    def lungo(x0, x1, y0, y1):
        z = img[y0:y1, x0:x1].astype(np.int16)
        return z.transpose(1, 0, 2) if orizzontale else z     # (lungo la striscia, di traverso, RGB)
    a = lungo(*banda)
    if a.shape[0] == 0 or a.shape[1] == 0:
        return None
    n, aria = a.shape[0], GRANELLO_ARIA_MM * px_mm
    mediana = np.median(a, axis=1)
    scarto = np.abs(a - mediana[:, None, :]).max(axis=(1, 2))
    uniforme = scarto <= UNIFORME

    def vicini(rotti, k):
        return (k > 0 and rotti[k][0] - rotti[k - 1][1] < aria) or (k + 1 < len(rotti) and rotti[k + 1][0] - rotti[k][1] < aria)

    forte = scarto > GRANELLO_SCARTO
    for s0, s1 in segmenti((~uniforme).tolist()):
        attorno = forte[max(0, s0 - int(aria)):s1 + int(aria)]
        if s1 - s0 <= GRANELLO_MM * px_mm and not attorno.any():
            uniforme[s0:s1] = True
            mediana[s0:s1] = mediana[s0 - 1] if s0 > 0 else mediana[s1] if s1 < n else mediana[s0]

    # il tratto più lungo, uniforme e con il fondo che cambia poco
    colori, lista = mediana.tolist(), uniforme.tolist()
    migliore, i = None, 0
    while i < n:
        if not lista[i]:
            i += 1
            continue
        rif, j = colori[i], i + 1
        while j < n and lista[j] and max(abs(c - r) for c, r in zip(colori[j], rif)) <= DERIVA:
            j += 1
        if migliore is None or j - i > migliore[1] - migliore[0]:
            migliore = (i, j)
        i = j
    if not migliore:
        return None
    i0, i1 = migliore
    colore = [int(round(sum(c[k] for c in colori[i0:i1]) / (i1 - i0))) for k in range(3)]

    # che cosa interrompe la striscia sul fondo principale del margine (il colore che vi occupa più spazio)
    contenuto = []
    rotti = segmenti((~uniforme).tolist())
    e = lungo(*esterno)
    e_letto = e.shape[0] == n and e.shape[1] > 0
    if e_letto:
        e_mediana = np.median(e, axis=1)
        e_pulito = np.abs(e - e_mediana[:, None, :]).max(axis=(1, 2)) <= UNIFORME
    rif = np.median(mediana[uniforme], axis=0)
    for k, (s0, s1) in enumerate(rotti):
        fondi = [mediana[x] for x in (s0 - 1, s1) if 0 <= x < n]
        if not fondi or any(np.abs(f - rif).max() > DERIVA for f in fondi):
            continue                                      # su un altro fondo, o al confine fra due fondi
        if e_letto:
            pulito = e_pulito[s0:s1] & (np.abs(e_mediana[s0:s1] - rif).max(axis=1) <= DERIVA)
            if pulito.mean() < 0.5:
                continue                                  # arriva al bordo della pagina
        if s1 - s0 > FORMA_MM * px_mm and not vicini(rotti, k):
            continue                                      # bordo lungo e solitario di una forma
        contenuto.append((s0, s1))
    return i0, i1, n, colore, contenuto


def zona_uniforme(np, img, x0, x1, y0, y1):
    """Luminanza media e scarto della zona (come la firma delle immagini nel motore): fondo libero se lo scarto è ≤ 6."""
    z = img[max(0, y0):max(0, y1), max(0, x0):max(0, x1)].astype(float)
    if z.size == 0:
        return 255.0, 0.0
    lum = 0.299 * z[..., 0] + 0.587 * z[..., 1] + 0.114 * z[..., 2]
    return float(lum.mean()), float(lum.std())


# ---------------------------------------------------------------- browser: misure e strato della cornice

# print-color-adjust:exact: senza, Chromium stampa senza sfondi in modalità «economica» e scurisce i testi chiari (la
# cornice sul bianco usciva grigio scuro invece del suo tono, la firma bianca sul blu non si sarebbe più vista).
PREPARA_JS = r"""async ([W, H]) => {
  await document.fonts.ready;
  document.documentElement.style.cssText = 'background:transparent;-webkit-print-color-adjust:exact;print-color-adjust:exact';
  document.body.innerHTML = '';
  document.body.style.cssText = 'margin:0;background:transparent';
  const t = document.createElement('div');
  t.className = 'tavola';
  t.style.cssText = `position:absolute;left:0;top:0;width:${W}px;height:${H}px;overflow:hidden`;
  document.body.append(t);
  return true;
}"""

MISURA_JS = r"""async ([font, testi]) => {
  await document.fonts.load(font, testi.join(' '));
  const c = document.createElement('canvas').getContext('2d');
  c.font = font;
  return testi.map((t) => c.measureText(t).width);
}"""

# La firma come le immagini (motore, scriviFirma): Montserrat 600, colore chiaro sul fondo scuro e scuro sul chiaro,
# linea di base a f.y; ha data-firma, così la cornice che la toccasse finisce fra i «tocchi».
FIRMA_JS = r"""async (f) => {
  const font = `${f.peso} ${f.corpo}px ${f.carattere}`;
  await document.fonts.load(font, f.testo);
  const el = document.createElement('div');
  el.setAttribute('data-firma', '');
  el.style.cssText = `position:absolute;left:${f.x}px;top:0;white-space:nowrap;font:${font};line-height:1;color:${f.colore}`;
  el.textContent = f.testo;
  const base = document.createElement('span');
  base.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
  el.append(base);
  document.querySelector('.tavola').append(el);
  el.style.top = `${f.y - (base.getBoundingClientRect().top - el.getBoundingClientRect().top)}px`;
  return true;
}"""


def strato_pdf(pagina, larghezza_mm: float, altezza_mm: float, px_mm: float) -> bytes:
    """La tavola del browser in PDF, alla misura della pagina: solo la cornice (e la firma), sfondo trasparente."""
    return pagina.pdf(width=f"{larghezza_mm:.4f}mm", height=f"{altezza_mm:.4f}mm", print_background=False,
                      margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                      scale=round(96 / (25.4 * px_mm), 6), page_ranges="1")


# ---------------------------------------------------------------- unione con la pagina

def impronta(o) -> str:
    """Impronta del contenuto di un oggetto PDF (dizionari, liste, flussi decompressi, riferimenti seguiti)."""
    import hashlib
    from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject, StreamObject
    h, visti = hashlib.sha256(), set()

    def scrivi(x):
        if isinstance(x, IndirectObject):
            if x.idnum in visti:
                h.update(b"R")
                return
            visti.add(x.idnum)
            x = x.get_object()
        if isinstance(x, StreamObject):
            h.update(b"S")
            scrivi(DictionaryObject({k: v for k, v in x.items() if k not in ("/Length", "/Filter", "/DecodeParms")}))
            h.update(x.get_data())
        elif isinstance(x, DictionaryObject):
            h.update(b"D")
            for k in sorted(x):
                h.update(k.encode())
                scrivi(x.raw_get(k))
            h.update(b"d")
        elif isinstance(x, ArrayObject):
            h.update(b"A")
            for y in x:
                scrivi(y)
            h.update(b"a")
        else:
            h.update(repr(x).encode())

    scrivi(o)
    return h.hexdigest()


def aggiungi_strato(pypdf, writer, pagina, strato, matrice, indice: int, caratteri: dict) -> None:
    """Disegna lo strato sopra la pagina senza riscriverne il contenuto: la pagina diventa [q] + contenuto di prima +
    [Q, strato come XObject dentro /Artifact]. I caratteri dello strato, uguali in ogni pagina, si copiano una volta
    sola (caratteri: impronta → riferimento già copiato)."""
    from pypdf.generic import (ArrayObject, DecodedStreamObject, DictionaryObject, IndirectObject, NameObject,
                               RectangleObject)

    def flusso(dati: bytes):
        s = DecodedStreamObject()
        s.set_data(dati)
        return writer._add_object(s)

    risorse_strato = DictionaryObject()
    for chiave in strato["/Resources"]:
        valore = strato["/Resources"].raw_get(chiave)
        if chiave != "/Font":
            risorse_strato[NameObject(chiave)] = valore.clone(writer)
            continue
        font = DictionaryObject()
        for nome in valore.get_object():
            rif = valore.get_object().raw_get(nome)
            k = impronta(rif)
            if k not in caratteri:
                caratteri[k] = rif.clone(writer) if isinstance(rif, IndirectObject) else writer._add_object(rif.clone(writer))
            font[NameObject(nome)] = caratteri[k]
        risorse_strato[NameObject(chiave)] = font
    xo = DecodedStreamObject()
    xo.set_data(strato.get_contents().get_data())
    xo[NameObject("/Type")] = NameObject("/XObject")
    xo[NameObject("/Subtype")] = NameObject("/Form")
    xo[NameObject("/BBox")] = RectangleObject(strato.mediabox)
    xo[NameObject("/Resources")] = risorse_strato
    rif = writer._add_object(xo.flate_encode())

    if "/Resources" not in pagina:
        pagina[NameObject("/Resources")] = DictionaryObject()
    risorse = pagina["/Resources"]
    if "/XObject" not in risorse:
        risorse[NameObject("/XObject")] = DictionaryObject()
    xobject = risorse["/XObject"]
    nome, k = f"/MisCornice{indice}", 0
    while nome in xobject:
        k += 1
        nome = f"/MisCornice{indice}_{k}"
    xobject[NameObject(nome)] = rif

    contenuti = ArrayObject([flusso(b"q\n")])
    if "/Contents" in pagina:
        prima = pagina.raw_get("/Contents")
        valore = prima.get_object()
        if isinstance(valore, ArrayObject):
            contenuti.extend(valore)
        else:
            contenuti.append(prima if isinstance(prima, IndirectObject) else writer._add_object(valore))
    cm = " ".join(numero(x) for x in matrice).encode()
    contenuti.append(flusso(b"\nQ\n" + ARTEFATTO + b"\nq " + cm + b" cm " + nome.encode() + b" Do Q\nEMC\n"))
    pagina[NameObject("/Contents")] = contenuti


# ---------------------------------------------------------------- lavoro su un PDF

def firmato(reader) -> bool:
    try:
        campi = reader.get_fields() or {}
    except Exception:
        campi = {}
    return any(str(c.get("/FT")) == "/Sig" and c.get("/V") for c in campi.values())


def valori_dei_campi(reader) -> list[str]:
    """Per ogni pagina, i valori scritti nei campi del modulo che vi compaiono: pdfium non li mette nel testo della
    pagina, e in un modulo compilato il nome dell'associazione può stare solo lì (rendiconto del 5×1000, campo «denom»)."""
    from pypdf.generic import ArrayObject

    def stringhe(v):
        if isinstance(v, str):
            return [str(v)]
        return [str(x) for x in v if isinstance(x, str)] if isinstance(v, ArrayObject) else []

    risultato = []
    for pagina in reader.pages:
        valori = []
        try:
            for a in (pagina["/Annots"] if "/Annots" in pagina else []):
                nodo = a.get_object()
                if nodo.get("/Subtype") != "/Widget":
                    continue
                for _ in range(20):                       # il valore può stare nel campo genitore
                    if "/V" in nodo:
                        valori += stringhe(nodo["/V"])
                        break
                    if "/Parent" not in nodo:
                        break
                    nodo = nodo["/Parent"].get_object()
        except Exception:
            pass
        risultato.append(" ".join(valori))
    return risultato


def ha_strato(pagina) -> bool:
    """Vero se la pagina porta già lo strato della cornice messo da qui (il blocco /Artifact in coda al contenuto):
    vale anche quando un altro programma ha unito o risalvato il PDF e il segno nel dizionario Info è andato perso."""
    try:
        c = pagina["/Contents"].get_object() if "/Contents" in pagina else []
        return any(ARTEFATTO in f.get_object().get_data() for f in (c if isinstance(c, list) else [c]))
    except Exception:
        return False


def elenco_pagine(numeri: list[int]) -> str:
    """«pagina 5», «pagine 6-17, 20 e 32»."""
    tratti: list[list[int]] = []
    for x in numeri:
        if tratti and x == tratti[-1][1] + 1:
            tratti[-1][1] = x
        else:
            tratti.append([x, x])
    parti = [str(a) if a == b else f"{a}-{b}" for a, b in tratti]
    if len(parti) == 1 and "-" not in parti[0]:
        return f"pagina {parti[0]}"
    return "pagine " + (parti[0] if len(parti) == 1 else ", ".join(parti[:-1]) + " e " + parti[-1])


def raggruppa(problemi: list[str]) -> list[str]:
    """Lo stesso problema su più pagine si scrive una volta sola («pagine 6-17 e 20: …»), nell'ordine in cui compare."""
    gruppi: dict[str, list[int]] = {}
    for x in problemi:
        r = re.match(r"pagina (\d+): (.*)", x, re.S)
        numeri = gruppi.setdefault(r.group(2) if r else x, [])
        if r:
            numeri.append(int(r.group(1)))
    return [f"{elenco_pagine(numeri)}: {testo}" if numeri else testo for testo, numeri in gruppi.items()]


def cornice_su_pdf(file: Path, uscita: Path | None, firma: dict | None, forza: bool, browser) -> int:
    """--cornice per un PDF: scrive FILE-cornice.pdf (o --uscita). Restituisce 0 se va bene (o se è già fatto), 1 se no."""
    np, pypdf, pdfium = librerie()
    dest = uscita or file.with_name(f"{file.stem}-cornice.pdf")
    if dest.resolve() == file.resolve():
        print(f"PROBLEMI in {file}: il PDF di partenza non si cambia: scegli un altro --uscita")
        return 1
    try:
        reader = pypdf.PdfReader(str(file))
    except Exception as e:
        print(f"PROBLEMI in {file}: il PDF non si legge ({e})")
        return 1
    if reader.is_encrypted:
        print(f"PROBLEMI in {file}: il PDF è protetto da password: salvalo senza protezione e riprova")
        return 1
    if firmato(reader):
        print(f"PROBLEMI in {file}: il PDF ha una firma digitale, che la cornice renderebbe non più valida: "
              "metti la cornice al documento prima di firmarlo")
        return 1
    if str((reader.metadata or {}).get(CHIAVE, "")) == MARCATORE:
        print(f"già fatta: {file} (ha già firma e cornice; per cambiarla si rifà dal documento originale)")
        return 0

    documento = pdfium.PdfDocument(str(file))
    documento.init_forms()      # senza, pdfium non disegna i campi del modulo e la cornice potrebbe finirci sotto
    campi = valori_dei_campi(reader)
    testi = []
    for i in range(len(documento)):
        tp = documento[i].get_textpage()
        testi.append(re.sub(r"\s+", " ", tp.get_text_range() + " " + (campi[i] if i < len(campi) else "")).casefold())
        tp.close()
    # pagine che hanno già la cornice (di un modello da stampa, o messa qui in un PDF poi unito ad altri): restano come
    # sono, due cornici una sopra l'altra non si leggono; le altre la ricevono
    gia = [TESTO_CORNICE in t or ha_strato(p) for t, p in zip(testi, reader.pages)]
    if all(gia):
        documento.close()
        print(f"già fatta: {file} (in tutte le pagine c'è già la cornice di microtesto)")
        return 0
    con_nome = [NOME in t for t in testi]
    if not any(con_nome) and not firma:
        documento.close()
        print(f"PROBLEMI in {file}: nel testo del PDF (né nei campi del modulo) non c'è «Misericordia di Ariccia»: "
              "aggiungilo al documento (per esempio nell'intestazione o in fondo) e rifai il PDF; se il nome c'è ma è "
              "un'immagine o una scritta in tracciati, scrivilo anche come testo. In alternativa --firma basso-sinistra (o "
              "basso-centro, basso-destra) lo scrive in basso nelle pagine che non l'hanno, solo dove il fondo è libero")
        return 1

    normale, piccolo = misure_modello("carta-intestata.html"), misure_modello("biglietto-fronte.html")
    writer = pypdf.PdfWriter(clone_from=reader)
    problemi, resoconto = [], []
    caratteri, strati = {}, []      # strati: i PDF dello strato restano aperti fino alla scrittura (pypdf copia per id)
    pagina_web = browser.new_page()
    try:
        pagina_web.goto(MOTORE.as_uri(), wait_until="load")
        for i, pagina in enumerate(writer.pages):
            n = i + 1
            if gia[i]:
                continue
            rot = int(pagina["/Rotate"]) % 360 if "/Rotate" in pagina else 0
            if rot not in (0, 90, 180, 270) or "/MediaBox" not in pagina:
                problemi.append(f"pagina {n}: " + ("manca la misura della pagina (MediaBox)" if rot in (0, 90, 180, 270)
                                                   else f"rotazione di {rot}° non gestita"))
                continue
            # misure lette senza gli accessori di pypdf, che scriverebbero nella pagina i riquadri mancanti
            crop = rettangolo(pagina["/CropBox"] if "/CropBox" in pagina else pagina["/MediaBox"])
            trim = rettangolo(pagina["/TrimBox"]) if "/TrimBox" in pagina else crop
            trim = (max(trim[0], crop[0]), max(trim[1], crop[1]), min(trim[2], crop[2]), min(trim[3], crop[3]))
            # pagina vista: misure del ritaglio ruotato e rifilo (TrimBox) in quel riferimento
            vista_w, vista_h = (crop[3] - crop[1], crop[2] - crop[0]) if rot in (90, 270) else (crop[2] - crop[0], crop[3] - crop[1])
            angoli = [schermo(x, y, crop, rot) for x in (trim[0], trim[2]) for y in (trim[1], trim[3])]
            tu0, tu1 = min(a[0] for a in angoli), max(a[0] for a in angoli)
            tv0, tv1 = min(a[1] for a in angoli), max(a[1] for a in angoli)
            w_mm, h_mm = (tu1 - tu0) / MM_PT, (tv1 - tv0) / MM_PT
            m = piccolo if min(w_mm, h_mm) < LATO_PICCOLO_MM else normale
            k = m["px_mm"]                                        # px della tavola per mm
            kpt = k / MM_PT                                       # px della tavola per punto
            W, H = w_mm * k, h_mm * k
            corpo, margine = m["corpo_mm"] * k, m["margine_mm"] * k
            s = round(corpo + 4)                                  # spessore della striscia, come nel motore
            # pagina disegnata (pypdfium2 applica ritaglio e rotazione): almeno 12 pixel di traverso nella striscia
            R = max(2.2, 12 * kpt / s)
            if vista_w * vista_h * R * R > PIXEL_MASSIMI:
                R = math.sqrt(PIXEL_MASSIMI / (vista_w * vista_h))
            img = documento[i].render(scale=R, rev_byteorder=True).to_numpy()
            sx, sy = img.shape[1] / vista_w, img.shape[0] / vista_h
            X = lambda xt: (tu0 + xt / kpt) * sx                  # px della tavola (dall'alto a sinistra del rifilo)
            Y = lambda yt: (vista_h - tv1 + yt / kpt) * sy        # → px della pagina disegnata
            def px(a, b, n_):
                return max(0, min(n_, int(math.floor(a)))), max(0, min(n_, int(math.ceil(b))))

            pagina_web.set_viewport_size({"width": int(math.ceil(W)) + 1, "height": int(math.ceil(H)) + 1})
            pagina_web.evaluate(PREPARA_JS, [W, H])
            larghezza_nome = pagina_web.evaluate(MISURA_JS, [f"600 {corpo}px Montserrat", [PRIMO_PEZZO]])[0]

            # firma, solo nelle pagine senza il nome, solo su fondo libero
            firma_pagina = None
            if firma and not con_nome[i]:
                fc = firma.get("corpo", None)
                corpo_f = fc * kpt if fc is not None else round(W * 0.03)
                margine_f = firma["margine"] * kpt if firma.get("margine") is not None else round(W * 0.06)
                basso_f = firma["basso"] * kpt if firma.get("basso") is not None else round(H * 0.05)
                carattere = firma.get("carattere", "Montserrat")
                larghezza = pagina_web.evaluate(MISURA_JS, [f"600 {corpo_f}px {carattere}", [FIRMA]])[0]
                pos = firma.get("posizione", "basso-sinistra")
                fx = W - margine_f - larghezza if pos == "basso-destra" else (W - larghezza) / 2 if pos == "basso-centro" else margine_f
                fy = H - basso_f
                zx0, zy0 = math.floor(fx - 12), math.floor(fy - corpo_f * 1.05 - 10)
                zx1, zy1 = math.ceil(fx + larghezza + 12), math.ceil(fy - corpo_f * 1.05 - 10 + corpo_f * 1.4 + 20)
                a, b = px(X(zx0), X(zx1), img.shape[1])
                c, d = px(Y(zy0), Y(zy1), img.shape[0])
                media, scarto = zona_uniforme(np, img, a, b, c, d)
                colore = firma.get("colore") or "auto"
                colore = colore if colore != "auto" else ("#FFFFFF" if media < 140 else "#0B2550")
                if corpo_f / kpt < FIRMA_MINIMA_PT:
                    problemi.append(f"pagina {n}: la firma è troppo piccola ({corpo_f / kpt:.1f} pt, ne servono almeno {FIRMA_MINIMA_PT})")
                elif zx0 < 0 or zx1 > W or zy0 < 0 or zy1 > H:
                    problemi.append(f"pagina {n}: la firma esce dalla pagina: spostala con --firma-margine o --firma-basso")
                elif scarto > 6 and not forza:
                    problemi.append(f"pagina {n}: sotto la firma non c'è un fondo uniforme (scarto {scarto:.1f}), coprirebbe un "
                                    "disegno o una scritta: spostala con --firma-basso, --firma-margine o --firma (--forza solo "
                                    "se il fondo va bene così)")
                else:
                    firma_pagina = {"testo": FIRMA, "x": fx, "y": fy, "corpo": corpo_f, "peso": 600, "carattere": carattere,
                                    "colore": colore}
                    pagina_web.evaluate(FIRMA_JS, firma_pagina)

            # tratti liberi sui quattro lati, come li cercherebbe corniceVettoriale sul fondo dei modelli; fra la striscia
            # e il bordo della pagina, la metà esterna del margine dice se ciò che interrompe la striscia arriva al bordo
            strisce, mancano = [], {}
            for lato in LATI:
                orizzontale = lato in ("alto", "basso")
                lunghezza = (W if orizzontale else H) - 2 * (margine + s)
                if lunghezza <= 0:
                    mancano[lato] = "la pagina è troppo piccola"
                    continue
                if orizzontale:
                    yt = margine if lato == "alto" else H - margine - s
                    a, b = px(X(margine + s), X(W - margine - s), img.shape[1])
                    c, d = px(Y(yt) - 1, Y(yt + s) + 1, img.shape[0])
                    ec, ed = px(*((Y(0), Y(margine / 2)) if lato == "alto" else (Y(H - margine / 2), Y(H))), img.shape[0])
                    banda, esterno = (a, b, c, d), (a, b, ec, ed)
                    inizio_px, scala, primo = X(margine + s), sx / kpt, a
                else:
                    xt = margine if lato == "sinistra" else W - margine - s
                    a, b = px(X(xt) - 1, X(xt + s) + 1, img.shape[1])
                    c, d = px(Y(margine + s), Y(H - margine - s), img.shape[0])
                    ea, eb = px(*((X(0), X(margine / 2)) if lato == "sinistra" else (X(W - margine / 2), X(W))), img.shape[1])
                    banda, esterno = (a, b, c, d), (ea, eb, c, d)
                    inizio_px, scala, primo = Y(margine + s), sy / kpt, c
                t = tratto_libero(np, img, banda, esterno, orizzontale, scala * k)
                if not t:
                    mancano[lato] = "il fondo del margine non è uniforme in nessun punto"
                    continue
                i0, i1, n_px, fondo, contenuto = t
                if contenuto:
                    mm = [((primo + j - inizio_px) / scala + margine + s) / k for c in contenuto for j in c]
                    mancano[lato] = (f"nel margine c'è una scritta o un disegno che non arriva al bordo della pagina "
                                     f"(da {min(mm):.0f} a {max(mm):.0f} mm dall'inizio del lato): la cornice gli "
                                     "starebbe accanto, come se ne facesse parte")
                    continue
                inizio = max(0.0, (primo + i0 - inizio_px) / scala)
                fine = min(lunghezza, (primo + i1 - inizio_px) / scala)
                if i0 > 0:
                    inizio += corpo                                # stacco da ciò che interrompe il fondo
                if i1 < n_px:
                    fine -= corpo
                if fine - inizio < larghezza_nome:
                    mancano[lato] = "il tratto libero del margine è troppo corto per il nome"
                    continue
                strisce.append({"lato": lato, "inizio": inizio, "fine": fine, "fondo": fondo})
            if mancano and (not forza or not strisce):
                problemi.append(f"pagina {n}: la cornice non trova posto (margine di {m['margine_mm']:g} mm, striscia di "
                                f"{s / k:.1f} mm): " + "; ".join(f"lato {x}: {y}" for x, y in mancano.items())
                                + ". Libera quel margine e rifai il PDF"
                                + (", oppure usa --forza per mettere la cornice solo sugli altri lati" if strisce else "")
                                + (". Per una grafica con una foto o una sfumatura a tutta pagina esporta un PNG o un "
                                   "JPEG e usa --cornice su quello: lì la cornice si adatta al fondo"
                                   if any("non è uniforme" in y for y in mancano.values()) else ""))
                continue
            esito = pagina_web.evaluate("(o) => window.corniceVettoriale(o)", {
                "corpo": corpo, "margine": margine, "larghezza": W, "altezza": H, "strisce": strisce})
            scritti = {x["lato"]: x["testo"] for x in esito["strisce"]}
            corti = [x["lato"] for x in strisce if PRIMO_PEZZO not in scritti.get(x["lato"], "")]
            if esito["tocchi"]:
                problemi.append(f"pagina {n}: la cornice di microtesto tocca la firma: alzala con --firma-basso")
                continue
            if esito.get("tagliate"):
                problemi.append(f"pagina {n}: la cornice di microtesto esce dalla sua striscia sul lato "
                                f"{', '.join(esito['tagliate'])}")
                continue
            if corti:
                problemi.append(f"pagina {n}: sul lato {', '.join(corti)} il nome non entra intero nella cornice")
                continue
            strati.append(pypdf.PdfReader(io.BytesIO(strato_pdf(pagina_web, w_mm, h_mm, k))))
            strato = strati[-1].pages[0]
            # strato (origine in basso a sinistra, alto a sinistra = alto a sinistra del rifilo) → pagina vista → pagina
            a_, b_, c_, d_, e_, f_ = da_schermo(crop, rot)
            du, dv = tu0, tv1 - float(strato.mediabox.top)
            matrice = (a_, b_, c_, d_, e_ + a_ * du + c_ * dv, f_ + b_ * du + d_ * dv)
            aggiungi_strato(pypdf, writer, pagina, strato, matrice, i, caratteri)
            resoconto.append((n, [x["lato"] for x in esito["strisce"]], esito["parole"], firma_pagina))
    finally:
        pagina_web.close()
        documento.close()

    if problemi:
        print(f"PROBLEMI in {file}:")
        for x in raggruppa(problemi):
            print(f"  - {x}")
        return 1
    writer.add_metadata({CHIAVE: MARCATORE})
    dest.parent.mkdir(parents=True, exist_ok=True)
    temporaneo = dest.with_name(dest.name + ".tmp")
    with open(temporaneo, "wb") as f:
        writer.write(f)
    temporaneo.replace(dest)
    lati = {tuple(r[1]) for r in resoconto}
    firme = [str(r[0]) for r in resoconto if r[3]]
    gia_fatte = [i + 1 for i, x in enumerate(gia) if x]
    print(f"ok: {dest} ({len(resoconto)} {'pagina' if len(resoconto) == 1 else 'pagine'}; cornice sui lati "
          + ("; ".join(", ".join(x) for x in sorted(lati)) if len(lati) > 1 else ", ".join(next(iter(lati), ())))
          + (f"; firma a pagina {', '.join(firme)}" if firme else "")
          + ((f"; {elenco_pagine(gia_fatte)} con la cornice già fatta, "
              + ("lasciata com'era" if len(gia_fatte) == 1 else "lasciate com'erano")) if gia_fatte else "") + ")")
    return 0
