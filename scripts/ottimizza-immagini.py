#!/usr/bin/env python3
"""Ottimizzazione immagini del sito (static/img).

Uso:  python3 scripts/ottimizza-immagini.py            (tutta static/img)
      python3 scripts/ottimizza-immagini.py static/img/news   (solo una cartella)
Richiede Pillow (pip install pillow). Da rilanciare ogni volta che si
aggiungono foto o grafiche: crea la copia .webp che il sito usa in automatico
(render hook di Hugo e tag <picture>); senza .webp resta il JPEG, nessun errore.

Cosa fa:
 - JPEG: ricompressione progressiva q82 (max 1600 px di larghezza / 2000 di altezza),
   sovrascritta solo se risparmia almeno il 10%;
 - WebP: copia .webp accanto a ogni jpg/png (usata dal render hook e dal carosello);
 - static/img/social/: i JPEG restano intatti (sono i file che l'utente scarica),
   ma ricevono comunque la copia WebP;
 - varianti ridotte dei loghi usati in navbar/footer/hero.
"""
import os, sys, glob
from PIL import Image

ROOT = sys.argv[1] if len(sys.argv) > 1 else "static/img"
MAX_W, MAX_H = 1600, 2000
report = []

def salva_webp(im, dest, q=80):
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
    im.save(dest, "WEBP", quality=q, method=6)

for f in sorted(glob.glob(os.path.join(ROOT, "**", "*.*"), recursive=True)):
    ext = f.lower().rsplit(".", 1)[-1]
    if ext not in ("jpg", "jpeg", "png"):
        continue
    if "-128." in f or "-84." in f or "-496." in f:
        continue
    prima = os.path.getsize(f)
    im = Image.open(f)
    im.load()
    intoccabile = "/social/" in f
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
    # copia WebP accanto all'originale
    webp = f.rsplit(".", 1)[0] + ".webp"
    salva_webp(im, webp, q=80 if ext != "png" else 85)
    wsize = os.path.getsize(webp)
    # se il WebP non conviene (raro per i PNG piccoli), non tenerlo
    if wsize >= os.path.getsize(f):
        os.remove(webp)
        wsize = 0
    report.append((webp, 0, wsize))

# ---- varianti dei loghi (dimensioni realmente usate in pagina, 2x retina) ----
loghi = os.path.join(ROOT, "loghi")
varianti = [
    ("mise-triangolo.png", "mise-triangolo-128.png", 136),   # navbar 64x56, footer 52x43
    ("mise-fregio.png", "mise-fregio-84.png", 84),           # navbar 42x42
    ("payoff-gente-al-servizio.png", "payoff-gente-al-servizio-496.png", 496),  # hero 248x144
]
for src, dst, w in varianti:
    p = os.path.join(loghi, src)
    if not os.path.exists(p):
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
if os.path.exists(fav):
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
