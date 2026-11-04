#!/usr/bin/env python3
"""Lettore di pagine web in locale, al posto di Firecrawl: apre la pagina in un vero browser (Chromium con Playwright),
aspetta che il JavaScript la costruisca e restituisce il contenuto in Markdown, testo, HTML o elenco dei link; legge anche i PDF.
Gratis e senza limiti. Non aggira CAPTCHA né verifiche anti-bot: se il sito ne mostra una lo dice (uscita 3) e si passa al Chrome di Alessandro.

Skill: .claude/skills/leggi-web/SKILL.md.
Esempi:
  leggi.py https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32016R0679
  leggi.py URL --formato link                  # link della pagina (come «map»)
  leggi.py URL --tutta-la-pagina --uscita p.md  # senza togliere menu e piè di pagina
  leggi.py URL --screenshot pagina.png
  leggi.py URL1 URL2 URL3                       # più pagine in fila, una dopo l'altra
Uscita: 0 letta, 2 errore (rete, pagina inesistente), 3 bloccata da una verifica anti-bot.
"""

import argparse
import datetime
import re
import subprocess
import sys
import tempfile
import urllib.parse


def prepara():
    """Sessioni cloud o PC nuovo: installa da solo solo le librerie che mancano (Playwright non si tocca se c'è,
    perché una versione nuova vorrebbe un altro browser da 300 MB)."""
    import importlib.util
    pacchetti = {"bs4": "beautifulsoup4", "lxml": "lxml", "markdownify": "markdownify", "playwright": "playwright"}
    mancanti = [nome for modulo, nome in pacchetti.items() if importlib.util.find_spec(modulo) is None]
    if mancanti:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--user", "--break-system-packages", *mancanti],
                       check=False)


def avvia_browser(pw):
    """Il Chromium di Playwright; se manca la versione attesa, uno già presente sulla macchina; solo alla fine lo scarica."""
    try:
        return pw.chromium.launch()
    except ErrorePlaywright:
        pass
    import glob
    import os
    cartelle = [os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""), "/opt/pw-browsers", os.path.expanduser("~/.cache/ms-playwright")]
    for cartella in filter(None, cartelle):
        for eseguibile in sorted(glob.glob(f"{cartella}/chromium-*/chrome-linux*/chrome"), reverse=True):
            try:
                return pw.chromium.launch(executable_path=eseguibile)
            except ErrorePlaywright:
                continue
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
    return pw.chromium.launch()


prepara()
from bs4 import BeautifulSoup  # noqa: E402
from markdownify import markdownify  # noqa: E402
from playwright.sync_api import Error as ErrorePlaywright  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

# Segni di una pagina di verifica anti-bot: non si aggirano, si segnalano.
SEGNI_BLOCCO = re.compile(
    r"captcha|verify you are (a )?human|are you a robot|just a moment\.\.\.|checking your browser|"
    r"access denied|attention required|cf-challenge|ddos protection|unusual traffic|sei un robot|"
    r"enable javascript and cookies to continue|request unsuccessful\. incapsula",
    re.I,
)
DA_TOGLIERE = ["script", "style", "noscript", "template", "svg", "iframe", "form", "button"]
CORNICE = ["nav", "header", "footer", "aside"]
CORNICE_RUOLI = ["navigation", "banner", "contentinfo", "complementary", "search"]


class Bloccata(Exception):
    pass


def contenuto_principale(html, tutta):
    zuppa = BeautifulSoup(html, "lxml")
    for tag in zuppa(DA_TOGLIERE):
        tag.decompose()
    if tutta:
        return zuppa.body or zuppa
    for tag in zuppa(CORNICE):
        tag.decompose()
    for ruolo in CORNICE_RUOLI:
        for tag in zuppa.select(f'[role="{ruolo}"]'):
            tag.decompose()
    for tag in zuppa.select('[id*="cookie" i], [class*="cookie" i], [id*="consent" i], [class*="consent" i]'):
        tag.decompose()
    corpo = zuppa.body or zuppa
    lunghezza = len(corpo.get_text(" ", strip=True)) or 1
    # Il contenitore principale si usa solo se contiene buona parte del testo: certi siti mettono <main> attorno a poco.
    for selettore in ["main", "article", '[role="main"]', "#content", "#main", ".content"]:
        candidato = zuppa.select_one(selettore)
        if candidato and len(candidato.get_text(" ", strip=True)) > 0.4 * lunghezza:
            return candidato
    return corpo


def in_markdown(nodo, base):
    for a in nodo.find_all("a", href=True):
        a["href"] = urllib.parse.urljoin(base, a["href"])
    for img in nodo.find_all("img", src=True):
        img["src"] = urllib.parse.urljoin(base, img["src"])
    testo = markdownify(str(nodo), heading_style="ATX", bullets="-")
    return re.sub(r"\n{3,}", "\n\n", testo).strip()


def link(nodo, base):
    visti, elenco = set(), []
    for a in nodo.find_all("a", href=True):
        indirizzo = urllib.parse.urljoin(base, a["href"]).split("#")[0]
        if indirizzo.startswith("http") and indirizzo not in visti:
            visti.add(indirizzo)
            elenco.append(f"- [{a.get_text(' ', strip=True) or indirizzo}]({indirizzo})")
    return "\n".join(elenco)


def leggi_pdf(dati):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(dati)
        f.flush()
        esito = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True)
    if esito.returncode != 0:
        raise RuntimeError(f"pdftotext: {esito.stderr.strip()}")
    return esito.stdout


def leggi(contesto, url, args):
    pagina = contesto.new_page()
    try:
        # Un PDF il browser lo scaricherebbe: si chiede direttamente, con gli stessi cookie del browser.
        if url.lower().split("?")[0].endswith(".pdf"):
            risposta = contesto.request.get(url, timeout=args.attesa_massima * 1000)
            if not risposta.ok:
                raise RuntimeError(f"HTTP {risposta.status}")
            return "PDF", risposta.status, leggi_pdf(risposta.body())
        try:
            risposta = pagina.goto(url, wait_until="domcontentloaded", timeout=args.attesa_massima * 1000)
        except ErrorePlaywright as e:
            if "Download is starting" in str(e):
                risposta = contesto.request.get(url)
                return "PDF", risposta.status, leggi_pdf(risposta.body())
            raise
        tipo = (risposta.headers.get("content-type", "") if risposta else "").lower()
        if "application/pdf" in tipo:
            return "PDF", risposta.status, leggi_pdf(risposta.body())
        try:
            pagina.wait_for_load_state("networkidle", timeout=10_000)
        except ErrorePlaywright:
            pass  # pagine che non smettono mai di caricare (statistiche, chat): si va avanti con quello che c'è
        pagina.wait_for_timeout(args.attesa * 1000)
        if args.scorri:
            for _ in range(10):  # contenuti che compaiono scorrendo
                pagina.mouse.wheel(0, 4000)
                pagina.wait_for_timeout(500)
        stato = risposta.status if risposta else 0
        if len(pagina.inner_text("body").strip()) < 200:
            # Pagina quasi vuota: spesso è un PDF mostrato dal visore, o arrivato dopo una prima pagina di attesa
            # (EUR-Lex risponde 202 e poi carica il documento). Si richiede con i cookie ormai ottenuti dal browser.
            seconda = contesto.request.get(pagina.url, timeout=args.attesa_massima * 1000)
            if "application/pdf" in seconda.headers.get("content-type", "").lower():
                return "PDF", seconda.status, leggi_pdf(seconda.body())
        titolo = pagina.title()
        html = pagina.content()
        testo_visibile = pagina.inner_text("body")[:3000]
        if SEGNI_BLOCCO.search(titolo) or (len(testo_visibile) < 3000 and SEGNI_BLOCCO.search(testo_visibile)):
            raise Bloccata(f"{url}: il sito mostra una verifica anti-bot («{titolo}»).")
        if stato in (401, 403, 429):
            raise Bloccata(f"{url}: il sito rifiuta l'accesso automatico (HTTP {stato}).")
        if stato >= 400:
            raise RuntimeError(f"HTTP {stato}")
        if args.screenshot:
            pagina.screenshot(path=args.screenshot, full_page=True)
        return titolo, stato, formatta(html, pagina.url, args)
    finally:
        pagina.close()


def formatta(html, base, args):
    nodo = contenuto_principale(html, args.tutta_la_pagina)
    if args.formato == "html":
        return str(nodo)
    if args.formato == "testo":
        return nodo.get_text("\n", strip=True)
    if args.formato == "link":
        return link(BeautifulSoup(html, "lxml"), base)
    return in_markdown(nodo, base)


def leggi_semplice(url, args):
    """Ripiego senza browser: certi server rispondono male al browser automatico ma bene a una richiesta semplice
    (l'albo pretorio di Genzano dà 500 al browser e 200 così). I certificati si verificano sempre."""
    import urllib.request
    richiesta = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) leggi-web", "Accept-Language": args.lingua})
    with urllib.request.urlopen(richiesta, timeout=args.attesa_massima) as risposta:
        dati, tipo, stato = risposta.read(), risposta.headers.get("content-type", "").lower(), risposta.status
        codifica = risposta.headers.get_content_charset() or "utf-8"
    if "application/pdf" in tipo:
        return "PDF | senza browser", stato, leggi_pdf(dati)
    html = dati.decode(codifica, errors="replace")
    zuppa = BeautifulSoup(html, "lxml")
    titolo = zuppa.title.get_text(strip=True) if zuppa.title else ""
    if SEGNI_BLOCCO.search(titolo):
        raise Bloccata(f"{url}: il sito mostra una verifica anti-bot («{titolo}»).")
    return titolo + " | senza browser", stato, formatta(html, url, args)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url", nargs="+")
    p.add_argument("--formato", choices=["markdown", "testo", "html", "link"], default="markdown")
    p.add_argument("--tutta-la-pagina", action="store_true", help="non toglie menu, intestazione e piè di pagina")
    p.add_argument("--attesa", type=float, default=2, help="secondi in più dopo il caricamento (pagine lente)")
    p.add_argument("--attesa-massima", type=float, default=60)
    p.add_argument("--scorri", action="store_true", help="scorre la pagina per far comparire i contenuti caricati in seguito")
    p.add_argument("--screenshot", help="salva un'immagine della pagina intera (solo con un URL)")
    p.add_argument("--lingua", default="it-IT")
    p.add_argument("--uscita", help="scrive su file invece che a schermo")
    args = p.parse_args()

    esito, parti = 0, []
    with sync_playwright() as pw:
        browser = avvia_browser(pw)
        contesto = browser.new_context(locale=args.lingua, viewport={"width": 1366, "height": 900})
        for url in args.url:
            try:
                try:
                    titolo, stato, corpo = leggi(contesto, url, args)
                except Bloccata:
                    raise
                except Exception as primo:  # noqa: BLE001
                    try:
                        titolo, stato, corpo = leggi_semplice(url, args)
                    except Exception:  # noqa: BLE001 - si riporta l'errore del browser, più informativo
                        raise primo from None
                oggi = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                parti.append(f"<!-- {url} | {titolo} | HTTP {stato} | letta il {oggi} -->\n\n{corpo}\n")
            except Bloccata as e:
                print(f"BLOCCATA: {e} Aprila con il Chrome di Alessandro (strumenti claude-in-chrome), dove la verifica la supera lui.", file=sys.stderr)
                esito = max(esito, 3)
            except Exception as e:  # noqa: BLE001 - una pagina che non si legge non ferma le altre
                print(f"ERRORE: {url}: {e}", file=sys.stderr)
                esito = max(esito, 2) if esito != 3 else 3
        browser.close()
    testo = "\n\n".join(parti)
    if args.uscita:
        with open(args.uscita, "w") as f:
            f.write(testo)
        print(f"Scritto {args.uscita} ({len(testo)} caratteri)", file=sys.stderr)
    else:
        sys.stdout.write(testo)
    return esito


if __name__ == "__main__":
    sys.exit(main())
