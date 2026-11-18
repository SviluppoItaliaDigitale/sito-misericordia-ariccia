#!/usr/bin/env python3
"""Rifà un .pptx dei materiali per le scuole con le immagini delle slide in JPEG (qualità 90) invece che in PNG:
stesso aspetto, un decimo del peso. Tiene dimensioni della diapositiva, note, titolo e autore.
Uso: python3 scripts/scuole/alleggerisci_pptx.py static/documenti/scuole/*/*.pptx"""
import io
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation


def alleggerisci(f: Path) -> None:
    vecchia = Presentation(str(f))
    nuova = Presentation()
    nuova.slide_width, nuova.slide_height = vecchia.slide_width, vecchia.slide_height
    for s in vecchia.slides:
        foto = [sh for sh in s.shapes if sh.shape_type == 13]
        if len(foto) != 1:
            sys.exit(f"{f}: mi aspettavo una sola immagine per slide")
        img = Image.open(io.BytesIO(foto[0].image.blob)).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=90, optimize=True, progressive=True)
        buf.seek(0)
        ns = nuova.slides.add_slide(nuova.slide_layouts[6])
        ns.shapes.add_picture(buf, 0, 0, width=nuova.slide_width, height=nuova.slide_height)
        if s.has_notes_slide:
            ns.notes_slide.notes_text_frame.text = s.notes_slide.notes_text_frame.text
    nuova.core_properties.title = vecchia.core_properties.title
    nuova.core_properties.author = vecchia.core_properties.author
    prima = f.stat().st_size
    nuova.save(str(f))
    print(f"{f}: {prima / 1e6:.1f} MB -> {f.stat().st_size / 1e6:.1f} MB")


for a in sys.argv[1:]:
    alleggerisci(Path(a))
