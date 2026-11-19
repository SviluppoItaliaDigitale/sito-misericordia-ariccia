#!/usr/bin/env python3
"""Controllo dei fogli dei kit per le emergenze: stampa davvero ogni scheda di static/kit/ con Chromium (A4, media
print, come «Stampa» del browser) e guarda struttura, immagini, carattere e fogli.
Lo usano gli agenti mis-print-card-qa, mis-didattica-reviewer, mis-verifica-visiva e mis-integrita-tecnica e il job
«fogli-kit» di «Controlli del sito» (.github/workflows/controlli.yml).

Nato il 19/11/2026 con gli agenti di controllo del kit (richiesta di Alessandro: copiarli prendendo spunto dal sito
della Protezione Civile di Genzano, da cui il kit è stato importato il 18/11/2026). L'idea viene da
scripts/check-fogli-stampa.py del sito PC (stesso autore): ciò che rompe la stampa (fogli bianchi, una riga di fonti o
il piè di pagina spinti da soli su un foglio in più) non si vede leggendo il codice, si vede solo stampando. Il codice
è scritto da zero con le librerie che questo repository usa già (Playwright, pypdfium2, numpy): niente PyMuPDF (AGPL).

Bloccante (exit 1), per ogni scheda:
  - struttura: DOCTYPE, lang="it", <title>, foglio di stile ../comune/print.css, link canonico uguale all'indirizzo
    vero, <article class="scheda"> con il piè di pagina, alt su ogni <img>;
  - residui dell'importazione dalla PC (recapiti, codici, percorsi) e la sede legale, che nei contenuti operativi non
    va mai (CLAUDE.md § «Sedi»);
  - errore JavaScript, risorsa del sito che non si carica (404), immagine rotta;
  - Montserrat (il carattere del kit nazionale, in comune/) non caricato;
  - foglio completamente bianco, in qualunque posizione;
  - foglio quasi vuoto (meno dell'8% dell'altezza con qualcosa stampato) quando i fogli sono più di uno;
  - foglio sotto il 20% seguito da un altro: di solito sul primo resta la sola intestazione e un riquadro che non si
    spezza passa tutto al foglio dopo (trovato il 19/11/2026 in tre schede).
Avviso (non blocca): un pezzo della scheda che chiede un carattere del computer (URW Gothic, Century Gothic, Arial…)
invece di Montserrat: si stampa diverso da computer a computer. Il monospace delle griglie dei giochi è voluto.
Exit 2: Playwright, Chromium o pypdfium2 mancanti.

Uso:
  python3 scripts/controlli/controlla_fogli_kit.py                         # tutte le schede
  python3 scripts/controlli/controlla_fogli_kit.py --da-git origin/main    # solo quelle che la PR tocca
  python3 scripts/controlli/controlla_fogli_kit.py --pagine bambini/06-labirinto-facile.html --png /tmp/fogli
  python3 scripts/controlli/controlla_fogli_kit.py --autotest              # prova il controllo su schede finte
Con --da-git: le schede cambiate, quelle del kit che nominano un'immagine cambiata, tutte se cambia comune/ o questo script.
"""
import argparse
import asyncio
import functools
import http.server
import re
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
STATIC = RADICE / "static"
KIT = STATIC / "kit"
SITO = "https://www.misericordia-ariccia.it"
SOGLIA_VUOTO = 0.08
SOGLIA_INTERMEDIO = 0.20   # un foglio con un altro dopo: sotto, il blocco seguente non ci stava ed è passato oltre
PARALLELE = 6
RESIDUI = {
    r"protezionecivilegenzano\.it": "indirizzo del sito o email della Protezione Civile",
    r"E10435833|Quality Label": "codice del Corpo europeo di solidarietà della Protezione Civile",
    r"Gruppo Comunale": "nome del Gruppo comunale della Protezione Civile",
    r"kit-calamita": "percorso dei kit della Protezione Civile",
    r"Rosa Venerini": "sede legale: nei contenuti operativi va Viale Antonietta Chigi, 46",
}
CARATTERE_DEL_COMPUTER = re.compile(r"font-family\s*:\s*([^;}\"]+)", re.I)
# Prima del PDF si aspettano tutte le immagini, anche quelle con loading="lazy", come quando si stampa dal browser.
ATTENDI = """async () => { await document.fonts.ready;
  const imgs = [...document.images]; imgs.forEach(i => { i.loading = 'eager'; });
  await Promise.all(imgs.map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
  return { montserrat: [...document.fonts].some(f => f.family.replace(/['"]/g, '') === 'Montserrat' && f.status === 'loaded'),
           rotte: imgs.filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src')) }; }"""


def schede() -> list[str]:
    return sorted(str(p.relative_to(KIT)) for p in KIT.rglob("*.html"))


def controlli_testo(rel: str, html: str) -> tuple[list[str], list[str]]:
    err, avv = [], []
    if not html.lstrip().lower().startswith("<!doctype html>"):
        err.append("manca <!DOCTYPE html>")
    if not re.search(r'<html[^>]*\blang="it"', html):
        err.append('manca lang="it" su <html>')
    if not re.search(r"<title>[^<]{5,}</title>", html):
        err.append("manca il <title>")
    if not re.search(r'href="(\.\./comune/|/kit/comune/)print\.css"', html):
        err.append("non usa il foglio di stile comune/print.css")
    can = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    atteso = f"{SITO}/kit/{rel}"
    if not can:
        err.append("manca il link canonico")
    elif can.group(1) != atteso:
        err.append(f"link canonico {can.group(1)} invece di {atteso}")
    if not re.search(r'<article class="scheda(-a4)?[ "]', html):   # scheda-a4: impaginazione propria a foglio fisso
        err.append('manca <article class="scheda">')
    if "scheda-footer" not in html:
        err.append("manca il piè di pagina (scheda-footer)")
    for img in re.findall(r"<img\b[^>]*>", html):
        if not re.search(r'\balt="', img) and 'aria-hidden="true"' not in img:
            err.append(f"immagine senza alt: {img[:90]}")
    for modello, cosa in RESIDUI.items():
        if re.search(modello, html):
            err.append(f"residuo dell'importazione: {cosa}")
    for pila in CARATTERE_DEL_COMPUTER.findall(html):
        primo = pila.split(",")[0].strip().strip("'\"")
        if primo.lower() not in ("montserrat", "monospace", "inherit"):
            avv.append(f"carattere del computer «{primo}» invece di Montserrat")
    return err, sorted(set(avv))


def riempimento(pdf: bytes) -> list[float]:
    import numpy as np
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(pdf)
    esiti = []
    for i in range(len(doc)):
        img = np.asarray(doc[i].render(scale=30 / 72, grayscale=True).to_pil().convert("L"))
        esiti.append(float((img.min(axis=1) < 235).sum()) / img.shape[0])
    doc.close()
    return esiti


def avvia_server(radice: Path) -> tuple[http.server.ThreadingHTTPServer, int]:
    class Silenzioso(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    gestore = functools.partial(Silenzioso, directory=str(radice))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestore)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


async def stampa(browser, porta: int, rel: str, png: Path | None, sem) -> tuple[list[str], list[float]]:
    async with sem:
        err: list[str] = []
        pagina = await browser.new_page()
        pagina.on("pageerror", lambda e: err.append(f"errore JavaScript: {e}"))
        pagina.on("response", lambda r: err.append(f"risorsa {r.status}: {r.url.split(str(porta), 1)[-1]}")
                  if r.status >= 400 and f"127.0.0.1:{porta}" in r.url else None)
        try:
            await pagina.goto(f"http://127.0.0.1:{porta}/kit/{rel}", wait_until="load", timeout=45000)
            stato = await pagina.evaluate(ATTENDI)
            if not stato["montserrat"]:
                err.append("Montserrat non caricato: la scheda si stampa con il carattere del computer")
            err += [f"immagine rotta: {s}" for s in stato["rotte"]]
            await pagina.emulate_media(media="print")
            pdf = await pagina.pdf(format="A4", prefer_css_page_size=True, print_background=True)
        finally:
            await pagina.close()
        fogli = riempimento(pdf)
        if png:
            import pypdfium2 as pdfium
            doc = pdfium.PdfDocument(pdf)
            for i in range(len(doc)):
                dest = png / f"{rel.replace('/', '__')}-{i + 1}.png"
                doc[i].render(scale=100 / 72).to_pil().save(dest)
            doc.close()
        for i, r in enumerate(fogli, 1):
            if r == 0:
                err.append(f"foglio {i} di {len(fogli)} bianco")
            elif len(fogli) > 1 and r < SOGLIA_VUOTO:
                err.append(f"foglio {i} di {len(fogli)} quasi vuoto ({r:.1%} dell'altezza stampata)")
            elif i < len(fogli) and r < SOGLIA_INTERMEDIO:
                err.append(f"foglio {i} di {len(fogli)} quasi vuoto ({r:.1%}): il blocco dopo è passato tutto al foglio seguente")
        return err, fogli


def da_git(base: str, tutte: list[str]) -> list[str]:
    nomi = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=RADICE,
                          capture_output=True, text=True, check=True).stdout.split()
    if any(n.startswith("static/kit/comune/") or n == "scripts/controlli/controlla_fogli_kit.py" for n in nomi):
        return tutte
    scelte = set()
    for n in nomi:
        if not n.startswith("static/kit/") or not (STATIC.parent / n).exists():
            continue
        rel = n.removeprefix("static/kit/")
        if rel.endswith(".html"):
            scelte.add(rel)
        else:   # un'immagine: le schede dello stesso kit che la nominano
            kit, nome = rel.split("/", 1)[0], Path(rel).name
            scelte.update(s for s in tutte if s.startswith(kit + "/") and nome in (KIT / s).read_text(encoding="utf-8"))
    return sorted(scelte)


async def controlla(radice: Path, elenco: list[str], png: Path | None) -> int:
    from playwright.async_api import async_playwright
    server, porta = avvia_server(radice)
    bloccanti = avvisi = 0
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            sem = asyncio.Semaphore(PARALLELE)
            esiti = await asyncio.gather(*(stampa(browser, porta, rel, png, sem) for rel in elenco))
            await browser.close()
    finally:
        server.shutdown()
    for rel, (err_stampa, fogli) in zip(elenco, esiti):
        err, avv = controlli_testo(rel, (radice / "kit" / rel).read_text(encoding="utf-8"))
        err += err_stampa
        bloccanti += bool(err)
        avvisi += bool(avv)
        if err or avv:
            print(f"\n{rel} ({len(fogli)} fogli: {', '.join(f'{r:.0%}' for r in fogli)})")
            for e in err:
                print(f"  ❌ {e}")
            for a in avv:
                print(f"  ⚠️  {a}")
    print(f"\nSchede controllate: {len(elenco)} · con errori bloccanti: {bloccanti} · con avvisi: {avvisi}")
    return 1 if bloccanti else 0


def autotest() -> int:
    """Schede finte: una giusta, una con il piè di pagina da solo sul secondo foglio, una con residui e senza alt."""
    testa = ('<!DOCTYPE html><html lang="it"><head><meta charset="utf-8"><title>Scheda di prova</title>'
             '<link rel="canonical" href="{sito}/kit/prova/{nome}"><link rel="stylesheet" href="../comune/print.css">'
             '</head><body><article class="scheda"><h1 class="scheda-title">Prova</h1>{corpo}'
             '<footer class="scheda-footer"><span>Prova</span></footer></article></body></html>')
    casi = {
        "giusta.html": ("<p>Testo breve.</p>", []),
        "sfora.html": ('<div style="height:270mm"></div>', ["quasi vuoto"]),
        "salta.html": ('<div style="height:45mm;border:1px solid #000"></div>'
                       '<div style="height:235mm;break-inside:avoid;border:1px solid #000"></div>', ["blocco dopo"]),
        "residui.html": ('<img src="../comune/triangolo-misericordie.png"><p>protezionecivilegenzano.it, '
                         'via Beata Rosa Venerini</p><img src="manca.png" alt="x">',
                         ["immagine senza alt", "residuo", "sede legale", "risorsa 404"]),
    }
    with tempfile.TemporaryDirectory() as t:
        radice = Path(t)
        (radice / "kit/prova").mkdir(parents=True)
        (radice / "kit/comune").symlink_to(KIT / "comune")
        for nome, (corpo, _) in casi.items():
            (radice / "kit/prova" / nome).write_text(testa.format(sito=SITO, nome=nome, corpo=corpo), encoding="utf-8")
        from io import StringIO
        import contextlib
        uscita = StringIO()
        with contextlib.redirect_stdout(uscita):
            asyncio.run(controlla(radice, [f"prova/{n}" for n in casi], None))
        testo = uscita.getvalue()
        blocchi = {m.group(1): m.group(2) for m in re.finditer(r"\nprova/(\S+) \(.*?\)\n((?:  .*\n?)*)", testo)}
        ok = True
        for nome, (_, attesi) in casi.items():
            trovato = blocchi.get(nome, "")
            for a in attesi:
                if a not in trovato:
                    ok = False
                    print(f"AUTOTEST: {nome} doveva segnalare «{a}»")
            if not attesi and trovato:
                ok = False
                print(f"AUTOTEST: {nome} doveva passare, invece:\n{trovato}")
    print("Autotest superato." if ok else "Autotest FALLITO.")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--da-git", metavar="BASE")
    ap.add_argument("--pagine", nargs="+", metavar="KIT/SCHEDA.html")
    ap.add_argument("--png", type=Path, metavar="CARTELLA", help="salva i fogli in PNG")
    ap.add_argument("--autotest", action="store_true")
    a = ap.parse_args()
    try:
        import numpy, pypdfium2, playwright  # noqa: F401
    except ImportError as e:
        print(f"Manca una libreria ({e.name}): pip install playwright==1.56.0 pypdfium2==5.13.0 numpy pillow, "
              "poi python -m playwright install chromium")
        return 2
    if a.autotest:
        return autotest()
    tutte = schede()
    elenco = a.pagine or (da_git(a.da_git, tutte) if a.da_git else tutte)
    mancanti = [s for s in elenco if s not in tutte]
    if mancanti:
        print("Schede inesistenti in static/kit/:", ", ".join(mancanti))
        return 2
    if not elenco:
        print("Nessuna scheda del kit toccata.")
        return 0
    if a.png:
        a.png.mkdir(parents=True, exist_ok=True)
    return asyncio.run(controlla(STATIC, elenco, a.png))


if __name__ == "__main__":
    sys.exit(main())
