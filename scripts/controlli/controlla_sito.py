#!/usr/bin/env python3
"""Controlli di salute del sito (workflow «Controlli del sito», issue «Stato del sito»).

Legge la build di Hugo (cartella public/) e il repo, e scrive un rapporto in Markdown:
  1. link interni, immagini, video e sottotitoli che puntano a file inesistenti;
  2. script inline non coperti dagli hash della Content-Security-Policy in static/.htaccess;
  3. registro dei dati (data/dati_da_verificare.yaml): voci scadute e contenuti sanitari senza revisione;
  4. news programmate in uscita nei prossimi 14 giorni, con la data del controllo editoriale;
  5. con --live: pagine principali online e build pubblicata uguale a quella attesa.
Solo libreria standard. Uso: controlla_sito.py public [--live] [--report out.md] [--csp]
  --csp: stampa gli hash degli script inline da copiare in static/.htaccess ed esce.
Esce con codice 1 se ci sono link interni rotti o script inline fuori dalla CSP."""
import base64, datetime as dt, glob, hashlib, html, os, re, sys, time, urllib.request
from pathlib import Path
from urllib.parse import urlsplit, unquote, urljoin

REPO = Path(__file__).resolve().parents[2]
SITO = "https://www.misericordia-ariccia.it"
PAGINE_LIVE = ["/", "/richiedi-trasporto/", "/servizi/", "/contatti/", "/numeri-utili/",
               "/dossier/primo-soccorso/", "/sostienici/", "/diventa-volontario/", "/privacy/", "/en/"]
FREQ = {"giornaliera": 1, "settimanale": 7, "mensile": 30, "annuale": 365}
oggi = dt.datetime.now(dt.timezone(dt.timedelta(hours=1))).date()  # data italiana (± l'ora legale basta)


def hash_inline(pub):
    """Hash sha256 (formato CSP) degli script inline eseguibili di tutte le pagine."""
    trovati = {}
    for f in glob.glob(f"{pub}/**/*.html", recursive=True):
        for s in re.findall(r"<script>(.*?)</script>", Path(f).read_text(encoding="utf-8"), re.S):
            h = "'sha256-" + base64.b64encode(hashlib.sha256(s.encode()).digest()).decode() + "'"
            trovati.setdefault(h, f.replace(pub, "").replace("index.html", ""))
    return trovati


def link_rotti(pub):
    rotti = {}
    for f in glob.glob(f"{pub}/**/*.html", recursive=True):
        testo = Path(f).read_text(encoding="utf-8")
        pagina = f[len(pub):].replace("index.html", "") or "/"
        # con --minify Hugo toglie le virgolette dove può: si leggono entrambe le forme
        attr = [a or b for a, b in re.findall(r'\s(?:href|src|poster)=(?:"([^"#?]*)|([^\s>"\'#?]+))', testo)]
        for ss in re.findall(r'srcset=(?:"([^"]+)"|([^\s>"]+))', testo):
            ss = ss[0] or ss[1]
            attr += [x.strip().split(" ")[0] for x in ss.split(",")]
        for u in attr:
            u = html.unescape(u)
            if not u: continue
            p = urlsplit(u)
            if p.scheme or u.startswith("//") or u.startswith("mailto:") or u.startswith("tel:"):
                if not u.startswith(SITO): continue
                u = urlsplit(u).path
            if not u.startswith("/"): u = urljoin(pagina, u)   # percorsi relativi (./css/…, ../img/…)
            loc = Path(pub + unquote(u))
            ok = (loc / "index.html").exists() if u.endswith("/") else (loc.exists() or (loc / "index.html").exists())
            if not ok: rotti.setdefault(u, pagina)
    return rotti


def leggi_registro():
    """Lettura minima del registro YAML (formato fisso: «- id:», chiavi a 2 spazi tra virgolette)."""
    voci, cur = [], None
    for riga in (REPO / "data/dati_da_verificare.yaml").read_text(encoding="utf-8").splitlines():
        m = re.match(r'- id: "(.+)"', riga)
        if m: cur = {"id": m.group(1)}; voci.append(cur); continue
        m = re.match(r'  (\w+): (.*)', riga)
        if cur is not None and m:
            v = m.group(2).strip()
            cur[m.group(1)] = v[1:-1] if v.startswith('"') else v
    return voci


def news_programmate(giorni=14):
    out = []
    for f in sorted((REPO / "content/news").glob("*.md")):
        fm = f.read_text(encoding="utf-8").split("---")[1]
        m = re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M)
        if not m: continue
        d = dt.date.fromisoformat(m.group(1))
        if oggi < d <= oggi + dt.timedelta(days=giorni):
            c = re.search(r'^controllo_editoriale:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M)
            t = re.search(r'^title:\s*"(.*)"', fm, re.M)
            out.append((d, f.name, t.group(1) if t else f.name, c.group(1) if c else ""))
    return out


def scarica(url, tentativi=4):
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (controlli sito Misericordia Ariccia)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code != 503 or i == tentativi - 1: return e.code, ""   # 503 intermittenti = anti-bot Aruba
        except Exception as e:
            if i == tentativi - 1: return str(e)[:60], ""
        time.sleep(5 * (i + 1))
    return "?", ""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pub = (args[0] if args else "public").rstrip("/")
    if "--csp" in sys.argv:
        print(" ".join(hash_inline(pub))); return 0
    report = sys.argv[sys.argv.index("--report") + 1] if "--report" in sys.argv else None
    righe, errori = [f"_Controllo del {oggi.strftime('%d/%m/%Y')}_", ""], 0

    rotti = link_rotti(pub)
    righe.append(f"### 🔗 Link interni, immagini e video: {'✅ nessun file mancante' if not rotti else f'❌ {len(rotti)} mancanti'}")
    righe += [f"- `{u}` (in {p})" for u, p in list(rotti.items())[:30]]
    errori += bool(rotti)

    csp = re.search(r'Content-Security-Policy(?:-Report-Only)? "([^"]+)"', (REPO / "static/.htaccess").read_text())
    ammessi = set(re.findall(r"'sha256-[^']+'", csp.group(1))) if csp else set()
    fuori = {h: p for h, p in hash_inline(pub).items() if h not in ammessi}
    righe += ["", f"### 🛡️ Content Security Policy: {'✅ tutti gli script inline sono coperti' if not fuori else f'❌ {len(fuori)} script inline nuovi o cambiati'}"]
    righe += [f"- {h} (es. in {p}): ricalcola con `python3 scripts/controlli/controlla_sito.py public --csp`" for h, p in fuori.items()]
    errori += bool(fuori)

    voci = leggi_registro()
    scadute = [v["id"] for v in voci if not v.get("verificato") or
               (oggi - dt.date.fromisoformat(v["verificato"])).days > FREQ.get(v.get("frequenza"), 365)]
    sanitari = [v for v in voci if v.get("tipo") == "sanita"]
    ps = (REPO / "content/dossier/primo-soccorso.md").read_text(encoding="utf-8")
    rev = re.search(r'^revisione_istruttore:\s*"(.+)"', ps, re.M)
    righe += ["", "### 📋 Registro dei dati",
              f"- Voci nel registro: {len(voci)} · scadute (oltre la loro frequenza): **{len(scadute)}**" + (f" ({', '.join(scadute[:12])}{'…' if len(scadute) > 12 else ''})" if scadute else ""),
              f"- Contenuti sanitari: {len(sanitari)} voci · revisione di un istruttore sul dossier primo soccorso: " + (f"✅ {rev.group(1)}" if rev else "⚠️ **non ancora registrata** (`revisione_istruttore` in content/dossier/primo-soccorso.md)")]

    np_ = news_programmate()
    righe += ["", f"### 📅 News in uscita nei prossimi 14 giorni: {len(np_)}"]
    for d, nome, tit, c in np_:
        stato = f"controllata il {c}" if c else ("⚠️ **da controllare**" if (d - oggi).days <= 3 else "controllo 3 giorni prima")
        righe.append(f"- {d.strftime('%d/%m')} · {tit} — {stato}")

    if "--live" in sys.argv:
        righe += ["", "### 🌐 Sito online"]
        css_atteso = re.search(r'(css/sito\.min\.[0-9a-f]+\.css)', Path(f"{pub}/index.html").read_text())
        for p in PAGINE_LIVE:
            st, testo = scarica(SITO + p)
            nota = ""
            if p == "/" and css_atteso:
                nota = " · build aggiornata ✅" if css_atteso.group(1) in testo else " · ⚠️ la home online non usa il CSS di questa build (deploy non arrivato?)"
            righe.append(f"- {'✅' if st == 200 else '❌'} `{p}` → {st}{nota}")
            errori += st != 200

    testo = "\n".join(righe) + "\n"
    if report: Path(report).write_text(testo, encoding="utf-8")
    print(testo)
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())
