#!/usr/bin/env python3
"""rendi-copertina.py — Salva la copertina del podcast (JPEG) e le mette la cornice.

Disegna copertina-podcast.html (1000×1000) con Playwright e Chromium a 3000×3000 (feed
del podcast, come chiedono le app) e a 600×600 (pagina /podcast/ del sito), poi passa i
file da rendi.py --cornice della skill grafiche-modelli-nazionali (mai risalvarli dopo).
Uso: python3 scripts/grafica-brand/podcast/rendi-copertina.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[2]
CARTELLA = RADICE / "static/img/podcast"
USCITE = {CARTELLA / "copertina-podcast.jpg": 3, CARTELLA / "copertina-podcast-600.jpg": 0.6}


def main() -> int:
    CARTELLA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for uscita, scala in USCITE.items():
            uscita.unlink(missing_ok=True)  # rendi.py --cornice salta i file che hanno già il segno
            pagina = browser.new_page(viewport={"width": 1000, "height": 1000}, device_scale_factor=scala)
            pagina.goto((QUI / "copertina-podcast.html").as_uri())
            pagina.evaluate("document.fonts.ready")
            pagina.wait_for_load_state("networkidle")
            pagina.locator(".tavola").screenshot(path=str(uscita), type="jpeg", quality=88)
            pagina.close()
        browser.close()
    return subprocess.run([sys.executable, str(RADICE / ".claude/skills/grafiche-modelli-nazionali/rendi.py"),
                           "--cornice", *map(str, USCITE)]).returncode


if __name__ == "__main__":
    sys.exit(main())
