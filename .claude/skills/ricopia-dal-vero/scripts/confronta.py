#!/usr/bin/env python3
"""Foglio di confronto fra un riferimento reale e il nostro render: affiancati e sovrapposti al 50%.
Skill ricopia-dal-vero (21/11/2026). Uso:
  python3 confronta.py RIFERIMENTO.jpg RENDER.jpg USCITA.jpg [--titolo "testo"]
Le due immagini si portano alla stessa altezza (sovrapposizione: il render adattato alla cornice del riferimento).
Il foglio serve solo a lavorare: i riferimenti con diritti d'autore non si pubblicano.
"""
import argparse
from PIL import Image, ImageDraw, ImageFont


def carattere(dim):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, dim)
        except OSError:
            pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("riferimento")
    ap.add_argument("render")
    ap.add_argument("uscita")
    ap.add_argument("--titolo", default="")
    ap.add_argument("--altezza", type=int, default=720)
    a = ap.parse_args()

    h = a.altezza
    rif = Image.open(a.riferimento).convert("RGB")
    ren = Image.open(a.render).convert("RGB")
    rif = rif.resize((round(rif.width * h / rif.height), h))
    ren = ren.resize((round(ren.width * h / ren.height), h))
    sovr = Image.blend(rif, ren.resize(rif.size), 0.5)

    fascia = 56
    larg = rif.width + ren.width + sovr.width
    foglio = Image.new("RGB", (larg, h + fascia), (0, 63, 133))
    x = 0
    d = ImageDraw.Draw(foglio)
    f = carattere(26)
    for img, etichetta in ((rif, "riferimento"), (ren, "nostro render"), (sovr, "sovrapposti 50%")):
        foglio.paste(img, (x, fascia))
        d.text((x + 12, 14), etichetta, fill=(252, 235, 12), font=f)
        x += img.width
    if a.titolo:
        w = d.textlength(a.titolo, font=f)
        d.text((larg - w - 12, 14), a.titolo, fill=(255, 255, 255), font=f)
    foglio.save(a.uscita, quality=90)
    print(a.uscita, foglio.size)


if __name__ == "__main__":
    main()
