#!/usr/bin/env python3
"""rendi-post.py — Grafica 4:5 di una puntata del podcast per Facebook e Instagram (dal 21/11/2026).

Riempie post-podcast.html con numero e titolo della puntata (dal front matter di
content/podcast/<file>.md), lo salva con Playwright in static/img/podcast/post/<file>.jpg
(1080×1350, JPEG qualità 88), lo passa da rendi.py --cornice e scrive `immagine:` nel front
matter, così la stessa grafica è anche l'anteprima della pagina. Il testo si adatta: il titolo
scende di misura finché sta nel suo spazio, e lo script si ferma se non ci sta.
Uso: python3 scripts/grafica-brand/podcast/rendi-post.py content/podcast/AAAA-MM-GG-id.md [...]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[2]
CARTELLA = RADICE / "static/img/podcast/post"


def campo(testo: str, nome: str) -> str:
    m = re.search(rf'^{nome}:\s*"?(.*?)"?\s*$', testo, re.M)
    if not m:
        sys.exit(f"manca «{nome}» nel front matter")
    return m.group(1).replace('\\"', '"')


def main() -> int:
    file = [Path(a) for a in sys.argv[1:]]
    if not file:
        print(__doc__)
        return 2
    CARTELLA.mkdir(parents=True, exist_ok=True)
    uscite = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for f in file:
            testo = f.read_text(encoding="utf-8")
            titolo, puntata = campo(testo, "title"), campo(testo, "episodio")
            uscita = CARTELLA / f"{f.stem}.jpg"
            uscita.unlink(missing_ok=True)  # rendi.py --cornice salta i file che hanno già il segno
            pagina = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
            pagina.goto((QUI / "post-podcast.html").as_uri())
            stato = pagina.evaluate(r"""async ([titolo, puntata]) => {
                document.querySelector('[data-campo=puntata]').textContent = 'PUNTATA ' + puntata;
                const t = document.querySelector('[data-campo=titolo]');
                // niente parole corte da sole a fine riga («il 112», «per le»): spazio unificatore dopo
                // ogni parola di una o tre lettere e prima dell'ultima parola corta
                t.textContent = titolo.replace(/(^|\s)(\S{1,3}) /g, '$1$2\u00a0').replace(/ (\S{1,4})$/, '\u00a0$1');
                await document.fonts.ready;
                const box = document.querySelector('.titolo');
                for (let px = 92; px >= 56; px -= 2) {
                  t.style.fontSize = px + 'px';
                  if (t.scrollHeight <= box.clientHeight && t.scrollWidth <= box.clientWidth) return px;
                }
                return 0;
            }""", [titolo, puntata])
            if not stato:
                sys.exit(f"{f.name}: il titolo non sta nello spazio neanche a 56 px")
            pagina.wait_for_load_state("networkidle")
            pagina.locator(".tavola").screenshot(path=str(uscita), type="jpeg", quality=88)
            pagina.close()
            uscite.append(uscita)
            via = "/" + uscita.relative_to(RADICE / "static").as_posix()
            if re.search(r"^immagine:", testo, re.M):
                testo = re.sub(r"^immagine:.*$", f'immagine: "{via}"', testo, count=1, flags=re.M)
            else:
                testo = re.sub(r"^(audio:.*)$", rf'\1\nimmagine: "{via}"', testo, count=1, flags=re.M)
            f.write_text(testo, encoding="utf-8")
            print(f"{uscita.relative_to(RADICE)} (titolo a {stato} px)")
        browser.close()
    return subprocess.run([sys.executable, str(RADICE / ".claude/skills/grafiche-modelli-nazionali/rendi.py"),
                           "--cornice", *map(str, uscite)]).returncode


if __name__ == "__main__":
    sys.exit(main())
