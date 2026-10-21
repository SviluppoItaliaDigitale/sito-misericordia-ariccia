#!/usr/bin/env python3
"""Riempie un modello grafico nazionale della Misericordia di Ariccia e lo salva in JPEG, PNG o PDF, con i controlli.

Parte della skill grafiche-modelli-nazionali, scritta per Alessandro Cuollo il 21/10/2026. I modelli, i loghi ufficiali
e i caratteri sono in scripts/grafica-brand/modelli-nazionali/ (catalogo dei modelli e dei campi in LEGGIMI.md).

Uso:
  rendi.py DATI.json [--uscita FILE] [--bozza]           dai dati di un file (esempi in modelli-nazionali/esempi/)
  rendi.py --modello post-con-fascia.html --campo fascia=Volontariato --campo foto=foto.jpg ... --uscita FILE
  rendi.py DATI.json --lutto si|no                       la grafica ricorda una persona morta (sì) oppure no
  rendi.py --elenco                                      modelli, misure e campi
  rendi.py --esempi CARTELLA [--anteprima FILE.jpg]      disegna tutti gli esempi e, se chiesto, il foglio d'insieme
  rendi.py --autotest                                    prova lo script e i controlli

Il formato viene dall'estensione di --uscita: .jpg (qualità 88, per il sito e i social), .png, oppure .pdf per la
carta intestata (A4) e il biglietto da visita (85×55 mm), con i testi vettoriali. Le foto si indicano con il percorso
del file, relativo al file dei dati (o alla cartella corrente con --campo).

Foto in bianco e nero solo per il lutto: sui social il bianco e nero dice che si ricorda una persona morta. Con
"lutto": true nei dati (oppure --lutto si) la foto diventa in bianco e nero, mentre fascia, colori, loghi e testi
restano quelli istituzionali; senza, la foto resta a colori.

Esce con codice 1 se un testo non entra nel suo spazio o esce dalla tavola, se tocca loghi, fasce o altri testi,
se un'immagine o un carattere non si carica, se un campo non esiste nel modello, se un campo HTML contiene tag non
ammessi, se il testo ricorda una persona morta e i dati non dicono se è un lutto ("lutto": true o false), se
restano segnaposti tra parentesi quadre o la foto di prova (questi ultimi due sono ammessi solo nelle bozze:
"bozza": true nei dati, oppure --bozza). Il controllo automatico non giudica l'equilibrio: il risultato si guarda
sempre.
Richiede Playwright per Python con Chromium (pip install playwright, poi python -m playwright install chromium);
Pillow solo per --autotest.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

QUI = Path(__file__).resolve().parent
MODELLI = QUI.parents[2] / "scripts" / "grafica-brand" / "modelli-nazionali"   # .claude/skills/<skill> → radice
QUALITA_JPEG = 88
TAG_AMMESSI = {"p", "br", "strong", "b", "em", "i", "u", "span"}
CLASSI_AMMESSE = {"evidenzia", "sottolinea", "finale"}
SUFFISSI_FOTO = ("-posizione", "-alt", "-zoom")
FOTO_PROVA = MODELLI / "foto-prova"
# Frasi che di solito ricordano una persona morta: se compaiono e i dati non dicono se è un lutto, lo script si
# ferma. Solo frasi poco ambigue: «scomparsa» da sola no, perché nei testi della Misericordia è anche la persona
# scomparsa da cercare, e «morte» da sola no, perché torna nei testi di primo soccorso.
PAROLE_LUTTO = [
    r"\bci\s+ha(?:nno)?\s+lasciat[oaie]\b",
    r"\bvenut[oaie]\s+a\s+mancare\b",
    r"\bsi\s+(?:è|e')\s+spent[oaie]\b",
    r"\b(?:è|e')\s+mort[oa]\b",
    r"\bcasa\s+del\s+padre\b",
    r"\bsalit[oaie]\s+al\s+cielo\b",
    r"\bin\s+(?:memoria|ricordo)\s+d[ie]",
    r"\blutt[oi]\b",
    r"\bcordoglio\b",
    r"\bcondoglianz[ae]\b",
    r"\bripos[ai]\s+in\s+pace\b",
    r"\beterno\s+riposo\b",
    r"\bsuffragio\b",
    r"\bcommemora",
    r"\bdefunt[oaie]\b",
    r"\baddio\b",
    r"\banniversario\s+della\s+(?:morte|scomparsa)\b",
    r"\banni\s+dalla\s+(?:morte|scomparsa)\b",
    r"\bpiang\w*\s+(?:la\s+)?(?:morte|scomparsa)\b",
    r"\b(?:morte|scomparsa)\s+(?:di|del|della|dello)\s+(?:papa|santo\s+padre|pontefice|vescovo|cardinale|monsignor|don|padre|suor)\b",
]

RIEMPI_JS = r"""(campi) => {
  const errori = [];
  const tavola = document.querySelector('.tavola');
  for (const [nome, valore] of Object.entries(campi)) {
    if (/-(posizione|alt|zoom)$/.test(nome) && document.querySelector(`img[data-campo="${CSS.escape(nome.replace(/-(posizione|alt|zoom)$/, ''))}"]`)) continue;
    const elementi = document.querySelectorAll(`[data-campo="${CSS.escape(nome)}"]`);
    if (!elementi.length) { errori.push(`il campo «${nome}» non esiste in questo modello`); continue; }
    for (const el of elementi) {
      if (el.tagName === 'IMG') {
        el.src = valore;
        el.removeAttribute('hidden');
        // la foto di prova resta di prova anche quando si indica il suo file (lo segnala "#prova" in fondo)
        if (String(valore).endsWith('#prova')) el.setAttribute('data-prova', ''); else el.removeAttribute('data-prova');
        const pos = campi[nome + '-posizione'];
        if (pos) el.style.objectPosition = pos;
        const zoom = campi[nome + '-zoom'];
        if (zoom) { el.style.transform = `scale(${zoom})`; el.style.transformOrigin = pos || '50% 50%'; }
        el.alt = campi[nome + '-alt'] || '';
        document.querySelectorAll(`[data-segnaposto-di="${CSS.escape(nome)}"]`).forEach((s) => { s.hidden = true; });
      } else if (el.hasAttribute('data-elenco')) {
        const voci = String(valore).split('\n').map((v) => v.trim()).filter(Boolean);
        const primo = el.querySelector('li');
        el.querySelectorAll('li').forEach((li) => li.remove());
        for (const v of voci) {
          const li = primo.cloneNode(true);
          li.querySelector('[data-voce]').textContent = v;
          el.appendChild(li);
        }
      } else if (el.hasAttribute('data-html')) {
        el.innerHTML = valore;
      } else {
        el.textContent = '';
        String(valore).split('\n').forEach((riga, i) => {
          if (i) el.appendChild(document.createElement('br'));
          el.appendChild(document.createTextNode(riga));
        });
      }
    }
  }
  if (!tavola) errori.push('il modello non ha l\'elemento .tavola');
  return errori;
}"""

ASPETTA_JS = r"""async () => {
  document.body.getBoundingClientRect();
  const attese = [...document.images].filter((im) => im.getAttribute('src') && !im.hidden)
    .map((im) => im.complete ? null : new Promise((ok) => { im.onload = ok; im.onerror = ok; }));
  await Promise.all(attese);
  await document.fonts.ready;
  return true;
}"""

CONTROLLA_JS = r"""(area) => {
  const W = document.documentElement.clientWidth, H = document.documentElement.clientHeight;
  const problemi = [];
  const visibile = (el) => el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden';
  const nome = (el) => el.getAttribute('data-campo') || (el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 50);
  // Per i testi in linea il riquadro del browser comprende tutta l'altezza del carattere, più alta della riga
  // quando l'interlinea è stretta: lo si riduce alla riga, altrimenti due righe vicine sembrano sovrapposte.
  const rettangoli = (el) => {
    const cs = getComputedStyle(el);
    const riga = parseFloat(cs.lineHeight);
    return [...el.getClientRects()].filter((r) => r.width > 0.5 && r.height > 0.5).map((r) => {
      if (cs.display !== 'inline' || !(riga > 0) || r.height <= riga) return r;
      const d = (r.height - riga) / 2;
      return { left: r.left, right: r.right, top: r.top + d, bottom: r.bottom - d };
    });
  };
  // Il browser conta come sporgenza anche la parte del carattere che esce da una riga con interlinea stretta
  // (qualche pixel): si tollera fino a 0,3 volte il corpo più grande; una riga in più sporge molto di più.
  const corpoMassimo = (el) => [el, ...el.querySelectorAll('*')]
    .reduce((m, x) => Math.max(m, parseFloat(getComputedStyle(x).fontSize) || 0), 0);
  const tocca = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 2;

  // 1. testi che non entrano nel loro spazio
  for (const el of document.querySelectorAll('[data-riquadro], [data-campo]:not(img)')) {
    if (!visibile(el) || el.clientWidth === 0) continue;
    if (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + Math.max(2, 0.3 * corpoMassimo(el)))
      problemi.push(`il testo non entra nel suo spazio: «${nome(el)}»`);
  }
  const testi = [...document.querySelectorAll('[data-campo]:not(img)')].filter(visibile);
  // 2. testi fuori dalla tavola o, nelle storie, fuori dall'area sicura
  for (const el of testi) {
    const r = rettangoli(el);
    if (r.some((x) => x.left < -0.5 || x.top < -0.5 || x.right > W + 0.5 || x.bottom > H + 0.5))
      problemi.push(`esce dalla tavola: «${nome(el)}»`);
    else if (area > 0 && r.some((x) => x.top < area || x.bottom > H - area))
      problemi.push(`fuori dall'area sicura della storia (${area} px dall'alto e dal basso): «${nome(el)}»`);
  }
  // 3. testi che toccano loghi, fasce, parti fisse o altri testi
  const ostacoli = [...document.querySelectorAll('[data-logo], [data-ostacolo]')].filter(visibile);
  const viste = new Set();
  for (const t of testi) {
    const rt = rettangoli(t);
    for (const o of ostacoli) {
      if (o.contains(t) || t.contains(o)) continue;
      const ro = o.getBoundingClientRect();
      if (rt.some((r) => tocca(r, ro)))
        problemi.push(`«${nome(t)}» tocca ${o.hasAttribute('data-logo') ? 'il logo' : 'una parte fissa della grafica'}`);
    }
    for (const u of testi) {
      if (u === t || t.contains(u) || u.contains(t)) continue;
      const chiave = [nome(t), nome(u)].sort().join(' | ');
      if (viste.has(chiave)) continue;
      const ru = rettangoli(u);
      if (rt.some((a) => ru.some((b) => tocca(a, b)))) { viste.add(chiave); problemi.push(`«${nome(t)}» e «${nome(u)}» si sovrappongono`); }
    }
  }
  // 4. immagini e caratteri
  for (const im of document.images) {
    if (!visibile(im) || !im.getAttribute('src')) continue;
    if (!(im.complete && im.naturalWidth > 0)) problemi.push(`immagine non caricata: ${decodeURIComponent(im.getAttribute('src').split('/').pop())}`);
  }
  const famiglie = new Set();
  for (const el of document.querySelectorAll('.tavola, .tavola *')) {
    if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    famiglie.add(getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '').trim());
  }
  for (const f of famiglie) {
    const facce = [...document.fonts].filter((x) => x.family.replace(/["']/g, '') === f);
    if (!facce.length) problemi.push(`carattere «${f}» non dichiarato in base.css`);
    else if (facce.some((x) => x.status === 'error')) problemi.push(`carattere «${f}»: un file non si carica`);
    else if (!facce.some((x) => x.status === 'loaded')) problemi.push(`carattere «${f}» non caricato`);
  }
  // 5. segnaposti e foto di prova
  const tavola = document.querySelector('.tavola');
  const segnaposti = [...new Set((tavola ? tavola.innerText : '').match(/\[[^\[\]\n]{2,}\]/g) || [])];
  const prova = [...document.querySelectorAll('img[data-prova]')].some(visibile);
  return { problemi, segnaposti, prova };
}"""


class _ControlloHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.errori: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in TAG_AMMESSI:
            self.errori.append(f"tag <{tag}> non ammesso")
        for k, v in attrs:
            if k != "class" or not set((v or "").split()) <= CLASSI_AMMESSE:
                self.errori.append(f'attributo {k}="{v}" non ammesso in <{tag}>')

    handle_startendtag = handle_starttag


def controlla_html(valore: str) -> list[str]:
    c = _ControlloHTML()
    c.feed(valore)
    c.close()
    return c.errori


def leggi_modello(modello: Path) -> dict:
    testo = modello.read_text(encoding="utf-8")
    m = re.search(r'<meta name="formato" content="(\d+)x(\d+)"', testo)
    if not m:
        raise SystemExit(f"Errore: {modello.name} non dichiara il formato (<meta name=\"formato\">).")
    area = re.search(r'<meta name="area-sicura" content="(\d+)"', testo)
    stampa = re.search(r'<meta name="stampa" content="([\d.]+)x([\d.]+)mm"', testo)
    campi = re.search(r"Campi \(attributo data-campo\):\n(.*?)\nSi compila", testo, flags=re.S)
    return {
        "file": modello,
        "w": int(m.group(1)), "h": int(m.group(2)),
        "area": int(area.group(1)) if area else 0,
        "stampa": (float(stampa.group(1)), float(stampa.group(2))) if stampa else None,
        "foto": set(re.findall(r'<img data-campo="([\w-]+)"', testo)),
        "html": set(re.findall(r'data-campo="([\w-]+)"[^>]*\bdata-html\b', testo)),
        "elenco_campi": campi.group(1).rstrip() if campi else "",
    }


def trova_modello(nome: str) -> Path:
    p = Path(nome)
    if p.suffix != ".html":
        p = p.with_suffix(".html")
    for candidato in (p, MODELLI / p.name):
        if candidato.is_file():
            return candidato.resolve()
    disponibili = ", ".join(sorted(x.name for x in MODELLI.glob("*.html")))
    raise SystemExit(f"Errore: modello «{nome}» non trovato. Disponibili: {disponibili}")


def e_foto_di_prova(p: Path) -> bool:
    """Vero se il file è una delle foto di prova, anche copiato altrove o rinominato."""
    impronta = hashlib.sha256(p.read_bytes()).hexdigest()
    return any(hashlib.sha256(f.read_bytes()).hexdigest() == impronta for f in FOTO_PROVA.glob("*") if f.is_file())


def leggi_lutto(valore) -> bool | None:
    """Il dato «lutto»: true, false oppure assente (None)."""
    if valore is None or isinstance(valore, bool):
        return valore
    raise SystemExit("Errore: \"lutto\" vuole true (la grafica ricorda una persona morta) oppure false.")


def frase_di_lutto(info: dict, campi: dict) -> str | None:
    """La prima frase dei testi che di solito ricorda una persona morta, oppure None."""
    for k, v in campi.items():
        if k in info["foto"] or k.endswith(("-posizione", "-zoom")):
            continue
        testo = html.unescape(re.sub(r"<[^>]+>", " ", str(v)))
        for schema in PAROLE_LUTTO:
            m = re.search(schema, testo, flags=re.IGNORECASE)
            if m:
                return m.group(0)
    return None


def prepara_campi(info: dict, campi: dict, base: Path) -> dict:
    """Controlla i valori e trasforma i percorsi delle foto in indirizzi file://."""
    pronti = {}
    for k, v in campi.items():
        if not isinstance(v, (str, int, float)):
            raise SystemExit(f"Errore: il campo «{k}» deve essere un testo.")
        v = str(v)
        if k in info["foto"]:
            p = Path(v) if Path(v).is_absolute() else (base / v)
            if not p.is_file():
                raise SystemExit(f"Errore: la foto del campo «{k}» non esiste: {p}")
            v = p.resolve().as_uri() + ("#prova" if e_foto_di_prova(p) else "")
        elif k.endswith("-zoom"):
            try:
                z = float(v)
            except ValueError:
                raise SystemExit(f"Errore: «{k}» vuole un numero (per esempio 1.15).")
            if not 1 <= z <= 2:
                raise SystemExit(f"Errore: «{k}» deve stare tra 1 e 2.")
        elif k.endswith("-posizione") and not re.fullmatch(r"\s*-?\d+(\.\d+)?%\s+-?\d+(\.\d+)?%\s*", v):
            raise SystemExit(f"Errore: «{k}» vuole due percentuali, per esempio «70% 50%».")
        elif k in info["html"]:
            errori = controlla_html(v)
            if errori:
                raise SystemExit(f"Errore nel campo HTML «{k}»: " + "; ".join(sorted(set(errori))))
        pronti[k] = v
    return pronti


def disegna(browser, info: dict, campi: dict, uscita: Path, bozza: bool = False, scala: float = 1.0,
            lutto: bool | None = None) -> dict:
    """Disegna una grafica e la salva. Restituisce problemi (bloccanti) e avvisi (bozza).

    lutto: True mette in bianco e nero le foto (e solo le foto), False conferma che non è un lutto,
    None (non detto) ferma la grafica se i testi ricordano una persona morta."""
    formato = uscita.suffix.lower()
    if formato not in (".jpg", ".jpeg", ".png", ".pdf"):
        raise SystemExit("Errore: --uscita deve finire in .jpg, .png o .pdf.")
    if formato == ".pdf" and not info["stampa"]:
        raise SystemExit(f"Errore: {info['file'].name} non è un modello da stampa: salvalo in .jpg o .png.")
    pagina = browser.new_page(viewport={"width": info["w"], "height": info["h"]}, device_scale_factor=scala)
    try:
        pagina.goto(info["file"].as_uri(), wait_until="load")
        problemi = pagina.evaluate(RIEMPI_JS, campi)
        if info["foto"] and lutto is None:
            frase = frase_di_lutto(info, campi)
            if frase:
                problemi.append(f"il testo sembra ricordare una persona morta («{frase}»): se è così aggiungi "
                                "\"lutto\": true ai dati (la foto diventa in bianco e nero, la grafica resta a colori); "
                                "se non lo è, scrivi \"lutto\": false")
        if lutto:
            pagina.evaluate("() => document.body.classList.add('lutto')")
        pagina.evaluate(ASPETTA_JS)
        esito = pagina.evaluate(CONTROLLA_JS, info["area"])
        problemi += esito["problemi"]
        avvisi = []
        if esito["segnaposti"]:
            (avvisi if bozza else problemi).append("restano segnaposti da compilare: " + ", ".join(esito["segnaposti"]))
        if esito["prova"]:
            (avvisi if bozza else problemi).append("c'è ancora la foto di prova: indica una foto vera nel campo «foto»")
        uscita.parent.mkdir(parents=True, exist_ok=True)
        if formato == ".pdf":
            larghezza_mm, altezza_mm = info["stampa"]
            pagina.pdf(path=str(uscita), width=f"{larghezza_mm}mm", height=f"{altezza_mm}mm", print_background=True,
                       margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                       scale=round(larghezza_mm / 25.4 * 96 / info["w"], 5), page_ranges="1")
        else:
            pagina.screenshot(path=str(uscita), type="png" if formato == ".png" else "jpeg",
                              quality=None if formato == ".png" else QUALITA_JPEG,
                              clip={"x": 0, "y": 0, "width": info["w"], "height": info["h"]})
    finally:
        pagina.close()
    return {"file": str(uscita), "problemi": problemi, "avvisi": avvisi, "lutto": bool(lutto and info["foto"])}


def avvia_browser(p):
    try:
        return p.chromium.launch(args=["--allow-file-access-from-files", "--force-color-profile=srgb"])
    except Exception as e:  # browser non installato
        raise SystemExit(f"Errore: Chromium non parte ({e}). Installa con: python -m playwright install chromium")


def importa_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("Errore: serve Playwright per Python (pip install playwright, poi python -m playwright install chromium).")
    return sync_playwright


def leggi_dati(percorso: Path) -> dict:
    try:
        dati = json.loads(percorso.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"Errore: non riesco a leggere {percorso}: {e}")
    if not isinstance(dati, dict) or "modello" not in dati:
        raise SystemExit(f"Errore: {percorso} deve contenere almeno \"modello\" e \"campi\".")
    return dati


def stampa_esito(r: dict) -> bool:
    if r["problemi"]:
        print(f"PROBLEMI in {r['file']}:")
        for x in r["problemi"]:
            print(f"  - {x}")
        return False
    print(f"ok: {r['file']}" + (" (lutto: foto in bianco e nero)" if r.get("lutto") else "")
          + (" (BOZZA, non pubblicare: " + "; ".join(r["avvisi"]) + ")" if r["avvisi"] else ""))
    return True


def esempi(cartella: Path, anteprima: Path | None) -> int:
    sync_playwright = importa_playwright()
    ordine = ("post-", "storia-", "carosello-", "biglietto-", "carta-", "scheda-")
    file_esempi = sorted((MODELLI / "esempi").glob("*.json"),
                         key=lambda f: (next((i for i, x in enumerate(ordine) if f.stem.startswith(x)), 9), f.stem))
    tutto_bene = True
    risultati = []
    with sync_playwright() as p:
        b = avvia_browser(p)
        for f in file_esempi:
            dati = leggi_dati(f)
            info = leggi_modello(trova_modello(dati["modello"]))
            r = disegna(b, info, prepara_campi(info, dati.get("campi", {}), f.parent), cartella / f"{f.stem}.jpg",
                        bozza=bool(dati.get("bozza")), lutto=leggi_lutto(dati.get("lutto")))
            tutto_bene &= stampa_esito(r)
            risultati.append((f.stem, info, r))
        if anteprima:
            figure = "".join(
                f'<figure><img src="{Path(r["file"]).resolve().as_uri()}" style="height: {360 if i["h"] <= 1350 else 512}px">'
                f'<figcaption>{html.escape(nome)}</figcaption></figure>' for nome, i, r in risultati)
            pagina_html = cartella / "_anteprima.html"
            pagina_html.write_text(
                '<!doctype html><html lang="it"><head><meta charset="utf-8">'
                f'<link rel="stylesheet" href="{(MODELLI / "base.css").as_uri()}"><style>'
                'body{margin:0;background:#E9EDF4;font-family:Montserrat,sans-serif}'
                'main{display:flex;flex-wrap:wrap;gap:28px;padding:32px;width:2336px;align-items:flex-end}'
                'figure{margin:0;display:flex;flex-direction:column;gap:8px}'
                'img{display:block;width:auto;box-shadow:0 1px 3px rgba(0,0,0,.25)}'
                'figcaption{font-size:18px;font-weight:600;color:#233B74}</style></head>'
                f'<body><main>{figure}</main></body></html>', encoding="utf-8")
            pg = b.new_page(viewport={"width": 2400, "height": 800})
            pg.goto(pagina_html.as_uri(), wait_until="load")
            pg.evaluate(ASPETTA_JS)
            anteprima.parent.mkdir(parents=True, exist_ok=True)
            pg.screenshot(path=str(anteprima), type="jpeg", quality=80, full_page=True)
            pg.close()
            pagina_html.unlink()
            print(f"anteprima: {anteprima}")
        b.close()
    return 0 if tutto_bene else 1


def elenco() -> int:
    for f in sorted(MODELLI.glob("*.html")):
        info = leggi_modello(f)
        extra = f", stampa {info['stampa'][0]:g}×{info['stampa'][1]:g} mm" if info["stampa"] else ""
        print(f"{f.name} ({info['w']}×{info['h']} px{extra})")
        print(info["elenco_campi"] or "  nessun campo")
        print()
    print('Nei modelli con foto, "lutto": true nei dati (oppure --lutto si) mette la foto in bianco e nero: solo per '
          'ricordare una persona morta. Fascia, colori, loghi e testi restano quelli istituzionali.')
    return 0


def autotest() -> int:
    sync_playwright = importa_playwright()
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        print("AUTOTEST FALLITO: serve Pillow")
        return 1
    falliti = []

    def attesa(cond, messaggio):
        if not cond:
            falliti.append(messaggio)

    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        t = Path(tmp)
        b = avvia_browser(p)
        # 1. tutti gli esempi si disegnano senza problemi e alla misura giusta
        for f in sorted((MODELLI / "esempi").glob("*.json")):
            dati = leggi_dati(f)
            info = leggi_modello(trova_modello(dati["modello"]))
            r = disegna(b, info, prepara_campi(info, dati.get("campi", {}), f.parent), t / f"{f.stem}.jpg", bool(dati.get("bozza")),
                        lutto=leggi_lutto(dati.get("lutto")))
            attesa(not r["problemi"], f"esempio {f.name}: {r['problemi']}")
            attesa(Image.open(r["file"]).size == (info["w"], info["h"]), f"esempio {f.name}: misure sbagliate")
            attesa(bool(r["avvisi"]) == bool(dati.get("bozza")), f"esempio {f.name}: bozza segnata male ({r['avvisi']})")
        foto = MODELLI.parents[2] / "static" / "img" / "ambulanza.jpg"   # una foto vera della Misericordia
        post = leggi_modello(MODELLI / "post-con-fascia.html")
        buoni = {"fascia": "Volontariato", "evidenziato": "Prova", "titolo": "di un titolo.", "sottotitolo": "Una riga di prova.",
                 "foto": str(foto), "foto-posizione": "60% 50%", "foto-alt": "Ambulanza della Misericordia di Ariccia"}

        def prova(campi, info=post, bozza=False, nome="x.jpg", lutto=None):
            return disegna(b, info, prepara_campi(info, campi, t), t / nome, bozza, lutto=lutto)

        def colore_foto(file):
            """Quanto è colorata la zona della foto del post (x 100-700, y 300-600: niente fascia né sfumatura)."""
            r, g, bl = Image.open(file).convert("RGB").crop((100, 300, 700, 600)).split()
            croma = ImageChops.subtract(ImageChops.lighter(ImageChops.lighter(r, g), bl), ImageChops.darker(ImageChops.darker(r, g), bl))
            return ImageStat.Stat(croma).mean[0]

        def vicino(file, xy, esadecimale, tolleranza=14):
            p = Image.open(file).convert("RGB").getpixel(xy)
            atteso = tuple(int(esadecimale[i:i + 2], 16) for i in (1, 3, 5))
            return all(abs(a - b) <= tolleranza for a, b in zip(p, atteso))

        r = prova(buoni)
        attesa(not r["problemi"] and not r["avvisi"], f"post corretto con problemi: {r}")
        attesa(colore_foto(r["file"]) > 12, f"senza lutto la foto deve restare a colori ({colore_foto(r['file']):.1f})")
        # lutto: solo la foto in bianco e nero, la grafica istituzionale resta a colori
        r = prova(buoni, lutto=True, nome="lutto.jpg")
        attesa(not r["problemi"] and r["lutto"], f"post di lutto con problemi: {r}")
        attesa(colore_foto(r["file"]) < 3, f"con il lutto la foto deve essere in bianco e nero ({colore_foto(r['file']):.1f})")
        attesa(vicino(r["file"], (20, 185), "#003F85"), "con il lutto la fascia deve restare blu")
        attesa(vicino(r["file"], (20, 128), "#FCEB0C"), "con il lutto il filo deve restare giallo")
        lascia = dict(buoni, sottotitolo="Ci ha lasciati il nostro confratello Mario.")
        r = prova(lascia)
        attesa(any("persona morta" in x for x in r["problemi"]), f"testo di lutto senza \"lutto\" non segnalato: {r}")
        r = prova(lascia, lutto=False)
        attesa(not r["problemi"], f"\"lutto\": false non rispettato: {r}")
        r = prova(dict(buoni, sottotitolo="La Misericordia si unisce al dolore per la morte di Papa Francesco."))
        attesa(any("persona morta" in x for x in r["problemi"]), f"lutto per un personaggio pubblico non segnalato: {r}")
        for normale in ("Cerchiamo volontari per la ricerca di una persona scomparsa.",
                        "Il defibrillatore salva dalla morte cardiaca improvvisa."):
            r = prova(dict(buoni, sottotitolo=normale))
            attesa(not r["problemi"], f"testo normale scambiato per un lutto ({normale}): {r}")
        try:
            disegna(b, post, prepara_campi(post, buoni, t), t / "y.jpg", lutto=leggi_lutto("sì"))
            falliti.append("\"lutto\" accettato come testo")
        except SystemExit:
            pass
        # la foto di prova resta di prova anche se si indica il suo file, rinominato o no
        copia = t / "foto-evento.jpg"
        copia.write_bytes((FOTO_PROVA / "piazza-di-corte.jpg").read_bytes())
        for f in (FOTO_PROVA / "piazza-di-corte.jpg", copia):
            r = prova(dict(buoni, foto=str(f)))
            attesa(any("foto di prova" in x for x in r["problemi"]), f"foto di prova indicata col suo file non segnalata ({f.name}): {r}")
        r = prova(dict(buoni, fascia="Una fascia molto più lunga del suo spazio"))
        attesa(any("non entra" in x or "tocca il logo" in x for x in r["problemi"]), f"fascia lunga non segnalata: {r}")
        r = prova(dict(buoni, titolo="parola " * 60))
        attesa(any("non entra" in x for x in r["problemi"]), f"titolo lungo non segnalato: {r}")
        r = prova(dict(buoni, evidenziato="Un evidenziato decisamente troppo lungo per una riga"))
        attesa(any("non entra" in x for x in r["problemi"]), f"evidenziato lungo non segnalato: {r}")
        r = prova(dict(buoni, inventato="x"))
        attesa(any("non esiste" in x for x in r["problemi"]), f"campo inesistente non segnalato: {r}")
        senza_foto = {k: v for k, v in buoni.items() if not k.startswith("foto")}
        r = prova(senza_foto)
        attesa(any("foto di prova" in x for x in r["problemi"]), f"foto di prova non segnalata: {r}")
        r = prova(senza_foto, bozza=True)
        attesa(not r["problemi"] and r["avvisi"], f"bozza con foto di prova trattata male: {r}")
        r = prova(dict(buoni, sottotitolo="[da scrivere]"))
        attesa(any("segnaposti" in x for x in r["problemi"]), f"segnaposto non segnalato: {r}")
        for cattivo in ('<img src=x onerror="alert(1)">', '<p style="color:red">x</p>', "<script>x</script>"):
            try:
                prepara_campi(leggi_modello(MODELLI / "carosello-pagina.html"), {"testo": cattivo}, t)
                falliti.append(f"HTML non ammesso accettato: {cattivo}")
            except SystemExit:
                pass
        try:
            prepara_campi(post, dict(buoni, foto="non-esiste.jpg"), t)
            falliti.append("foto inesistente accettata")
        except SystemExit:
            pass
        assemblea = leggi_modello(MODELLI / "post-assemblea.html")
        r = prova({"data": "15 SETTEMBRE DUEMILAVENTISEI", "giorno": "SABATO", "ora": "18:00", "luogo": "SEDE OPERATIVA",
                   "convocazione": "SECONDA CONVOCAZIONE"}, info=assemblea)
        attesa(any("non entra" in x or "sovrappongono" in x or "tocca" in x for x in r["problemi"]), f"data lunga dell'assemblea non segnalata: {r}")
        storia = leggi_modello(MODELLI / "storia-con-fascia.html")
        attesa(storia["area"] > 0, "la storia non dichiara l'area sicura")
        r = prova(dict(buoni, sottotitolo="riga " * 120), info=storia)
        attesa(any("non entra" in x or "area sicura" in x for x in r["problemi"]), f"storia troppo piena non segnalata: {r}")
        carta = leggi_modello(MODELLI / "carta-intestata.html")
        r = disegna(b, carta, {}, t / "carta.pdf", bozza=True)
        testo_pdf = (t / "carta.pdf").read_bytes()
        mediabox = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]", testo_pdf)
        attesa(bool(mediabox) and abs(float(mediabox.group(1)) - 595.3) < 2 and abs(float(mediabox.group(2)) - 841.9) < 2,
               f"PDF della carta non in A4: {mediabox.group(0) if mediabox else 'MediaBox mancante'}")
        try:
            disegna(b, post, prepara_campi(post, buoni, t), t / "post.pdf")
            falliti.append("PDF di un post accettato")
        except SystemExit:
            pass
        b.close()
    if falliti:
        print("AUTOTEST FALLITO:")
        for f in falliti:
            print(f"  - {f}")
        return 1
    print("Autotest superato: esempi, misure, testi lunghi, campi inesistenti, foto di prova, lutto (foto in bianco e nero, "
          "grafica a colori, testi riconosciuti), segnaposti, HTML non ammesso, assemblea, area sicura della storia e PDF A4.")
    return 0


def main(argv=None) -> int:
    a = argparse.ArgumentParser(description="Riempie un modello grafico nazionale della Misericordia di Ariccia e lo salva, con i controlli.")
    a.add_argument("dati", nargs="?", type=Path, help="file JSON con \"modello\", \"campi\" ed eventualmente \"bozza\": true")
    a.add_argument("--modello", help="nome del modello (vedi --elenco), al posto del file di dati o per sostituire il suo")
    a.add_argument("--campo", action="append", default=[], help="CHIAVE=VALORE, ripetibile; \\n va a capo")
    a.add_argument("--uscita", type=Path, help="file da scrivere: .jpg, .png o .pdf (stampa)")
    a.add_argument("--bozza", action="store_true", help="ammette segnaposti e foto di prova (solo per vedere, mai per pubblicare)")
    a.add_argument("--lutto", choices=("si", "sì", "no"), help="si: la grafica ricorda una persona morta, foto in bianco e nero; "
                   "no: non è un lutto (sostituisce \"lutto\" dei dati)")
    a.add_argument("--scala", type=float, default=1.0, help="moltiplica i pixel di JPEG e PNG (es. 3 per stampare la carta in PNG)")
    a.add_argument("--elenco", action="store_true", help="elenca modelli, misure e campi")
    a.add_argument("--esempi", type=Path, metavar="CARTELLA", help="disegna tutti gli esempi in CARTELLA")
    a.add_argument("--anteprima", type=Path, metavar="FILE", help="con --esempi: foglio d'insieme in JPEG")
    a.add_argument("--autotest", action="store_true")
    x = a.parse_args(argv)
    if x.autotest:
        return autotest()
    if x.elenco:
        return elenco()
    if x.esempi:
        return esempi(x.esempi, x.anteprima)
    if not x.dati and not x.modello:
        a.error("indica un file di dati o --modello (oppure --elenco, --esempi, --autotest)")
    dati = leggi_dati(x.dati) if x.dati else {"campi": {}}
    info = leggi_modello(trova_modello(x.modello or dati["modello"]))
    da_riga = {}
    for c in x.campo:
        if "=" not in c:
            a.error(f"--campo vuole CHIAVE=VALORE, non «{c}»")
        k, v = c.split("=", 1)
        da_riga[k.strip()] = v.replace("\\n", "\n")
    # le foto dei dati sono relative al file dei dati, quelle passate con --campo alla cartella corrente
    campi = prepara_campi(info, {k: v for k, v in dati.get("campi", {}).items() if k not in da_riga},
                          x.dati.resolve().parent if x.dati else Path.cwd())
    campi.update(prepara_campi(info, da_riga, Path.cwd()))
    uscita = x.uscita or Path.cwd() / f"{(x.dati.stem if x.dati else info['file'].stem)}.jpg"
    lutto = (x.lutto != "no") if x.lutto else leggi_lutto(dati.get("lutto"))
    sync_playwright = importa_playwright()
    with sync_playwright() as p:
        b = avvia_browser(p)
        r = disegna(b, info, campi, uscita, bozza=x.bozza or bool(dati.get("bozza")), scala=x.scala, lutto=lutto)
        b.close()
    return 0 if stampa_esito(r) else 1


if __name__ == "__main__":
    sys.exit(main())
