#!/usr/bin/env python3
"""Trasforma le pagine HTML dei materiali per le scuole in PDF (schede A4 o slide 16:9), con
firma e cornice di microtesto della Misericordia di Ariccia, e ne fa le anteprime per guardarle.
Le schede A4 escono in PDF vettoriale (testo selezionabile, stampa nitida). Le slide escono come
immagini 1920×1080 con la cornice incisa (rendi.py --cornice), raccolte in un PDF e in un .pptx
con lo stesso nome, da proiettare o aprire in PowerPoint e LibreOffice; il testo di ogni slide va
anche nelle note della diapositiva del .pptx, per chi usa un lettore di schermo.

Uso:  python3 scripts/scuole/rendi_pdf.py scripts/scuole/primaria/cartellino-112.html [ALTRI.html …] [--anteprime CARTELLA]
Ogni HTML dichiara nel <head>:  <meta name="formato" content="a4|slide">  e
<meta name="uscita" content="static/documenti/scuole/primaria/cartellino-112.pdf"> (percorso dalla radice del repository).
Il body ha la classe "a4" (pagine .pagina) o "slide" (pagine .diapo). Si ferma se un testo esce dalla pagina.
Servono playwright (Chromium), pypdf, pypdfium2, numpy.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
RENDI = RADICE / ".claude/skills/grafiche-modelli-nazionali/rendi.py"


def meta(html: str, nome: str) -> str:
    m = re.search(rf'<meta\s+name="{nome}"\s+content="([^"]+)"', html)
    if not m:
        sys.exit(f"manca <meta name=\"{nome}\" …>")
    return m.group(1)


def copertina(uscita: Path, prima) -> None:
    """Anteprima della prima pagina per la pagina del sito: static/img/scuole/<fascia>/<nome>.jpg, 640 px di lato lungo."""
    rel = uscita.relative_to(RADICE / "static/documenti/scuole")
    dest = RADICE / "static/img/scuole" / rel.with_suffix(".jpg")
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = prima.convert("RGB")
    im.thumbnail((640, 640))
    im.save(dest, quality=86, optimize=True, progressive=True)


# Formati delle slide per le LIM (lavagne interattive): (suffisso del file, altezza CSS a 1920 di larghezza,
# fattore di scala dei pixel, PowerPoint sì/no). Il file senza suffisso è il 16:9 Full HD.
FORMATI_SLIDE = [("", 1080, 1, True), ("-4k", 1080, 2, False), ("-16x10", 1200, 1, False), ("-4x3", 1440, 1, True)]


def rendi_slide(browser, sorgente: Path, html: str, uscita: Path, anteprime: Path | None) -> bool:
    """Slide in tutti i formati di FORMATI_SLIDE: immagini con la cornice incisa, PDF e, dove previsto, .pptx."""
    if uscita.suffix != ".pdf":
        sys.exit(f"{sorgente}: l'uscita delle slide deve finire in .pdf")
    from PIL import Image
    from pptx import Presentation
    from pptx.util import Emu
    sys.path.insert(0, str(RENDI.parent))
    import cornice_pdf  # segno di firma e cornice nel dizionario Info, come nei PDF dei modelli
    titolo = re.search(r"<title>([^<]+)</title>", html).group(1)
    for suff, alt, scala, con_pptx in FORMATI_SLIDE:
        dest = uscita.with_name(uscita.stem + suff + ".pdf")
        pagina = browser.new_page(viewport={"width": 1920, "height": alt}, device_scale_factor=scala)
        pagina.goto(sorgente.resolve().as_uri())
        pagina.evaluate(f"document.documentElement.style.setProperty('--h', '{alt}px')")
        pagina.evaluate("document.fonts.ready")
        pagina.wait_for_load_state("networkidle")
        fuori = pagina.evaluate("""() => { const out = [];
          document.querySelectorAll('.diapo').forEach((p, i) => { const b = p.getBoundingClientRect();
            p.querySelectorAll('*').forEach(e => { if (e.closest('.note-relatore')) return; const r = e.getBoundingClientRect();
              if (r.width && (r.bottom > b.bottom + 1 || r.right > b.right + 1)) out.push(`slide ${i + 1}: «${(e.textContent || '').trim().slice(0, 40)}» esce`); });
            const c = p.querySelector('.contenuto'); if (c && c.scrollHeight > c.clientHeight + 2) out.push(`slide ${i + 1}: il contenuto è più alto del suo spazio`); });
          return out.slice(0, 20); }""")
        if fuori:
            for f in fuori:
                print(f"PROBLEMA {sorgente.name} ({1920 * scala}×{alt * scala}): {f}")
            pagina.close()
            return False
        testi = pagina.evaluate("[...document.querySelectorAll('.diapo')].map(d => { const c = d.cloneNode(true); c.querySelectorAll('.note-relatore').forEach(n => n.remove()); document.body.appendChild(c); const t = c.innerText; c.remove(); return t; })")
        note = pagina.evaluate("[...document.querySelectorAll('.diapo')].map(d => { const n = d.querySelector('.note-relatore'); return n ? n.textContent.trim() : ''; })")
        with tempfile.TemporaryDirectory() as tmp:
            png = []
            for i, el in enumerate(pagina.query_selector_all(".diapo")):
                f = Path(tmp) / f"slide-{i + 1:02d}.png"
                el.screenshot(path=str(f))
                png.append(f)
            pagina.close()
            r = subprocess.run([sys.executable, str(RENDI), "--cornice", *map(str, png)], capture_output=True, text=True)
            if r.returncode:
                print(f"PROBLEMA {sorgente.name}: cornice non applicata\n{r.stdout.strip()}\n{r.stderr.strip()}")
                return False
            imm = [Image.open(f).convert("RGB") for f in png]
            imm[0].save(dest, save_all=True, append_images=imm[1:], resolution=72.0 * scala, quality=90,
                        title=titolo, author="Confraternita di Misericordia di Ariccia ODV")
            cornice_pdf.marca(dest)
            if con_pptx:
                pres = Presentation()
                pres.slide_width = Emu(12192000)
                pres.slide_height = Emu(round(12192000 * alt / 1920))
                for f, t, nr in zip(png, testi, note):
                    sl = pres.slides.add_slide(pres.slide_layouts[6])
                    sl.shapes.add_picture(str(f), 0, 0, width=pres.slide_width, height=pres.slide_height)
                    sl.notes_slide.notes_text_frame.text = (nr + "\n\n" if nr else "") + "Testo della slide: " + " ".join(t.split())
                pres.core_properties.author = "Confraternita di Misericordia di Ariccia ODV"
                pres.core_properties.title = titolo
                pres.save(dest.with_suffix(".pptx"))
            if suff == "":
                copertina(uscita, imm[0])
            if anteprime and scala == 1:
                anteprime.mkdir(parents=True, exist_ok=True)
                for i, im in enumerate(imm):
                    im.save(anteprime / f"{dest.stem}-{i + 1}.png")
        print(f"ok {dest.relative_to(RADICE)}{' e .pptx' if con_pptx else ''} ({len(imm)} slide, {1920 * scala}×{alt * scala})")
    return True


def rendi(browser, sorgente: Path, anteprime: Path | None) -> bool:
    html = sorgente.read_text(encoding="utf-8")
    formato, uscita = meta(html, "formato"), RADICE / meta(html, "uscita")
    if formato not in ("a4", "slide"):
        sys.exit(f"{sorgente}: formato «{formato}» sconosciuto (a4 o slide)")
    if "Misericordia di Ariccia" not in " ".join(re.sub(r"<[^>]+>", " ", html).split()):
        sys.exit(f"{sorgente}: manca la firma «Misericordia di Ariccia»")
    pagina = browser.new_page(viewport={"width": 1920, "height": 1080} if formato == "slide" else {"width": 794, "height": 1123})
    pagina.goto(sorgente.resolve().as_uri())
    pagina.evaluate("document.fonts.ready")
    pagina.wait_for_load_state("networkidle")
    sel = ".diapo" if formato == "slide" else ".pagina"
    # Contenuto che trabocca: un figlio che finisce oltre il bordo inferiore della sua pagina.
    fuori = pagina.evaluate("""sel => {
      const out = [];
      document.querySelectorAll(sel).forEach((p, i) => {
        const b = p.getBoundingClientRect();
        if (p.scrollHeight > p.clientHeight + 1) out.push(`pagina ${i + 1}: il contenuto è più alto della pagina`);
        p.querySelectorAll('*').forEach(e => { const r = e.getBoundingClientRect();
          if (r.width && (r.bottom > b.bottom + 1 || r.right > b.right + 1)) out.push(`pagina ${i + 1}: <${e.tagName.toLowerCase()}> «${(e.textContent || '').trim().slice(0, 40)}» esce dalla pagina`); });
      });
      return out.slice(0, 20); }""", sel)
    immagini_rotte = pagina.evaluate("[...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.src)")
    if fuori or immagini_rotte:
        for f in fuori + [f"immagine non caricata: {s}" for s in immagini_rotte]:
            print(f"PROBLEMA {sorgente.name}: {f}")
        pagina.close()
        return False
    n = pagina.evaluate(f"document.querySelectorAll('{sel}').length")
    uscita.parent.mkdir(parents=True, exist_ok=True)
    if formato == "slide":
        pagina.close()
        return rendi_slide(browser, sorgente, html, uscita, anteprime)
    with tempfile.TemporaryDirectory() as tmp:
        grezzo = Path(tmp) / "grezzo.pdf"
        pagina.pdf(path=str(grezzo), width="210mm", height="297mm", print_background=True, prefer_css_page_size=False)
        pagina.close()
        from pypdf import PdfReader
        pagine_pdf = len(PdfReader(str(grezzo)).pages)
        if pagine_pdf != n:
            print(f"PROBLEMA {sorgente.name}: {n} pagine nell'HTML ma {pagine_pdf} nel PDF (un contenuto va a capo su una pagina in più)")
            return False
        r = subprocess.run([sys.executable, str(RENDI), "--cornice", str(grezzo), "--uscita", str(uscita)],
                           capture_output=True, text=True)
        if r.returncode:
            print(f"PROBLEMA {sorgente.name}: cornice non applicata\n{r.stdout.strip()}\n{r.stderr.strip()}")
            return False
        from pypdf import PdfWriter
        w = PdfWriter(clone_from=str(uscita))
        titolo = re.search(r"<title>([^<]+)</title>", html).group(1)
        w.add_metadata({"/Title": titolo, "/Author": "Confraternita di Misericordia di Ariccia ODV"})
        w.write(str(uscita))
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(uscita))
    copertina(uscita, doc[0].render(scale=1.2).to_pil())
    doc.close()
    if anteprime:
        import pypdfium2 as pdfium
        anteprime.mkdir(parents=True, exist_ok=True)
        doc = pdfium.PdfDocument(str(uscita))
        for i in range(len(doc)):
            doc[i].render(scale=2.0).to_pil().save(anteprime / f"{uscita.stem}-{i + 1}.png")
        doc.close()
    print(f"ok {uscita.relative_to(RADICE)} ({n} pagine)")
    return True


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("html", nargs="+", type=Path)
    a.add_argument("--anteprime", type=Path, help="cartella dove salvare un PNG per pagina, da guardare prima di consegnare")
    arg = a.parse_args()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        esiti = [rendi(browser, h, arg.anteprime) for h in arg.html]
        browser.close()
    return 0 if all(esiti) else 1


if __name__ == "__main__":
    sys.exit(main())
