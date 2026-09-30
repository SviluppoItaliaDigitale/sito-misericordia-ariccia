#!/usr/bin/env python3
"""Ottimizzazione immagini del sito (static/img).

Uso:  python3 scripts/ottimizza-immagini.py                   (tutta static/img)
      python3 scripts/ottimizza-immagini.py static/img/news   (solo una cartella)
      aggiungere --prova per vedere cosa farebbe senza toccare nulla,
      --tutte per rifare anche le immagini già ottimizzate (sconsigliato).
Richiede Pillow (pip install pillow). Da rilanciare ogni volta che si
aggiungono foto o grafiche: crea la copia .webp che il sito usa in automatico
(render hook di Hugo e tag <picture>); senza .webp resta il JPEG, nessun errore.

Cosa fa, SOLO sulle immagini nuove, cioè senza il loro .webp accanto
(se sostituisci una foto tenendo lo stesso nome, cancella prima il suo .webp):
 - JPEG di foto: ricompressione progressiva q82 (max 1600 px di larghezza /
   2000 di altezza), sovrascritta solo se risparmia almeno il 10%;
 - le grafiche brand (*-grafica.jpg, vanno anche su Instagram a qualità ~88)
   e static/img/social/ restano intatte: ricevono solo la copia WebP;
 - WebP: copia .webp accanto a ogni jpg/png, scritta solo se più leggera
   dell'originale. Un .webp già esistente non viene MAI cancellato;
 - varianti ridotte dei loghi e favicon, solo se mancano.
Le immagini già ottimizzate non vengono ritoccate: ricomprimere a ogni giro
peggiora la qualità e cambia file che non c'era motivo di toccare.
"""
import os, sys, glob
from PIL import Image

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
PROVA = "--prova" in sys.argv
TUTTE = "--tutte" in sys.argv
ROOT = ARGS[0] if ARGS else "static/img"
MAX_W, MAX_H = 1600, 2000
# icone e anteprima social: devono restare PNG/JPEG così come sono
SENZA_WEBP = {"favicon.png", "favicon-32.png", "apple-touch-icon.png", "og-default.jpg"}
report = []

def salva_webp(im, dest, q=80):
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
    im.save(dest, "WEBP", quality=q, method=6)

def da_fare(src, derivato):
    """Vero se il derivato manca. Niente confronto di date: dopo un clone
    di git tutti i file hanno la data del clone e sarebbe un confronto a caso."""
    return TUTTE or not os.path.exists(derivato)

for f in sorted(glob.glob(os.path.join(ROOT, "**", "*.*"), recursive=True)):
    ext = f.lower().rsplit(".", 1)[-1]
    if ext not in ("jpg", "jpeg", "png"):
        continue
    if "-128." in f or "-84." in f or "-496." in f:
        continue
    if os.path.basename(f) in SENZA_WEBP:
        continue
    webp = f.rsplit(".", 1)[0] + ".webp"
    if not da_fare(f, webp):
        continue  # già ottimizzata: non si tocca
    if PROVA:
        print("da ottimizzare:", f)
        continue
    prima = os.path.getsize(f)
    im = Image.open(f)
    im.load()
    intoccabile = "/social/" in f or "-grafica." in os.path.basename(f)
    if ext in ("jpg", "jpeg") and not intoccabile:
        rgb = im.convert("RGB")
        w, h = rgb.size
        if w > MAX_W or h > MAX_H:
            rgb.thumbnail((MAX_W, MAX_H), Image.LANCZOS)
        tmp = f + ".tmp"
        rgb.save(tmp, "JPEG", quality=82, optimize=True, progressive=True)
        dopo = os.path.getsize(tmp)
        if dopo < prima * 0.9 or rgb.size != (w, h):
            os.replace(tmp, f)
            im = rgb
        else:
            os.remove(tmp)
            dopo = prima
        report.append((f, prima, dopo))
    # copia WebP accanto all'originale: scritta in un file temporaneo e tenuta
    # solo se conviene; un .webp preesistente non viene mai cancellato
    tmpw = webp + ".tmp"
    salva_webp(im, tmpw, q=80 if ext != "png" else 85)
    wsize = os.path.getsize(tmpw)
    if wsize < os.path.getsize(f):
        os.replace(tmpw, webp)
        report.append((webp, 0, wsize))
    else:
        os.remove(tmpw)
        print("WebP non conveniente, tenuto solo il JPEG:", f)

# ---- varianti dei loghi (dimensioni realmente usate in pagina, 2x retina) ----
loghi = os.path.join(ROOT, "loghi")
varianti = [
    ("mise-triangolo.png", "mise-triangolo-128.png", 136),   # navbar 64x56, footer 52x43
    ("mise-fregio.png", "mise-fregio-84.png", 84),           # navbar 42x42
    ("payoff-gente-al-servizio.png", "payoff-gente-al-servizio-496.png", 496),  # hero 248x144
]
for src, dst, w in varianti:
    p = os.path.join(loghi, src)
    if not os.path.exists(p) or not da_fare(p, os.path.join(loghi, dst)) or PROVA:
        continue
    im = Image.open(p).convert("RGBA")
    r = w / im.size[0]
    im = im.resize((w, round(im.size[1] * r)), Image.LANCZOS)
    out = os.path.join(loghi, dst)
    im.save(out, "PNG", optimize=True)
    salva_webp(im, out.rsplit(".", 1)[0] + ".webp", q=90)
    report.append((out, 0, os.path.getsize(out)))

# favicon: apple-touch-icon 180 e favicon 32
fav = os.path.join(ROOT, "favicon.png")
if os.path.exists(fav) and da_fare(fav, os.path.join(ROOT, "favicon-32.png")) and not PROVA:
    im = Image.open(fav).convert("RGBA")
    im.resize((180, 180), Image.LANCZOS).save(os.path.join(ROOT, "apple-touch-icon.png"), "PNG", optimize=True)
    im.resize((32, 32), Image.LANCZOS).save(os.path.join(ROOT, "favicon-32.png"), "PNG", optimize=True)

tot_prima = sum(p for _, p, _ in report if p)
tot_dopo = sum(d for _, p, d in report if p)
for f, p, d in report:
    if p:
        print(f"{p:>8} -> {d:>8}  {f}")
print(f"\nJPEG in loco: {tot_prima/1e6:.1f} MB -> {tot_dopo/1e6:.1f} MB")
print("WebP creati:", sum(1 for f, p, d in report if f.endswith('.webp') and d))
