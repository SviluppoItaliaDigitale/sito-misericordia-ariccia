#!/usr/bin/env python3
"""
Passa un lavoro a ChatGPT (Codex) da solo e lo richiude a nome di Alessandro:
ramo `chatgpt/…`, voce in bacheca, PR in bozza con la richiesta, commento di avvio.

Protocollo: `COORDINAMENTO.md` § «Passaggio automatico a ChatGPT» (uguale in tutti i
repository di Alessandro) e regola `.claude/rules/firma-dei-lavori.md`.

Comandi
  modello                       stampa lo schema della richiesta (sette parti, da compilare)
  nuovo  --argomento SLUG --titolo "…" --brief FILE.md [--base main] [--prova]
                                ramo chatgpt/SLUG-AAAAMMGG da origin/BASE, voce in «Richieste»,
                                PR in bozza (titolo + brief), commento «@codex esegui la richiesta
                                nella descrizione», numero della PR scritto in bacheca
  stato  [--tutte]              le PR aperte sui rami chatgpt/*: bozza, commit dopo l'avvio,
                                risposte dello strumento, crediti esauriti, controlli
  chiudi --pr N [--attesa-minuti 40] [--senza-pulizia] [--senza-merge]
                                riscrive a nome di Alessandro i commit con un altro autore,
                                segna la PR pronta, aspetta i controlli, squash merge con
                                messaggio scritto, toglie dalla PR il commento di avvio e le
                                risposte dello strumento, cancella il ramo

Solo libreria standard; GitHub via `gh api` (REST: in sessione cloud GraphQL non c'è);
git solo con oggetti e riferimenti (commit-tree, update-ref): nessun checkout, la cartella
di lavoro resta com'è anche su repository con decine di migliaia di file.
Titolo e descrizione della PR non possono nominare strumenti: lo script si ferma se li trova.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# --- Costanti ------------------------------------------------------------------

NOME_OK = "Alessandro Cuollo"
EMAIL_OK = "65465537+SviluppoItaliaDigitale@users.noreply.github.com"
# Autori ammessi sui commit: Alessandro e il committer di GitHub (merge e squash dal server).
AUTORI_OK = {EMAIL_OK.lower(), "noreply@github.com"}
NOMI_OK = {NOME_OK.lower(), "github"}

BACHECA = "COORDINAMENTO.md"
PREFISSO_RAMO = "chatgpt/"
COMMENTO_AVVIO = "@codex esegui la richiesta nella descrizione"
COMMENTO_AVVIO_CODA = (
    "\n\nLavora su questo ramo e fai push qui: non aprire altre pull request, non unire e "
    "non segnare pronta questa. Segui la richiesta punto per punto, esegui i controlli "
    "indicati prima del push, aggiorna la bacheca `COORDINAMENTO.md` sullo stesso ramo e "
    "rispondi con un commento breve: che cosa hai fatto, che cosa resta e perché."
)

# Parole che non possono comparire in titolo e descrizione della PR (testi pubblici).
VIETATE = re.compile(
    r"\b(claude|chatgpt|chat gpt|codex|openai|anthropic|gemini|jules|copilot|llm|"
    r"intelligenza artificiale|artificial intelligence)\b",
    re.IGNORECASE,
)
# Le sigle vanno cercate rispettando le maiuscole: «ai» e «ia» minuscole sono parole italiane.
VIETATE_SIGLE = re.compile(r"\b(IA|AI|LLM)\b")

# Le sette parti della richiesta, nell'ordine, riconosciute dal numero e dalla prima parola.
PARTI = [
    (1, "obiettivo"),
    (2, "file"),
    (3, "che cosa fare"),
    (4, "vincoli"),
    (5, "controlli"),
    (6, "consegna"),
    (7, "che cosa non fare"),
]

MODELLO = """## 1. Obiettivo
<Una frase: che cosa deve esistere alla fine e a che cosa serve.>

## 2. File
<Percorsi esatti dei file da creare o modificare, uno per riga. Niente altro va toccato.>

## 3. Che cosa fare
<Passi numerati, con i dati già verificati: numeri, nomi, date, misure, testi da usare.
Niente da cercare, niente da indovinare. Dove serve un testo, il testo è qui.>

## 4. Vincoli
<Regole del repository che valgono per questo lavoro: misure, licenze, accessibilità,
stile, niente riferimenti a strumenti nei file e nei messaggi di commit, identità dei commit.>

## 5. Controlli
<Comandi esatti da eseguire prima del push, con il risultato atteso (es. `python3 scripts/…`,
`hugo --minify`). Se un controllo fallisce, si corregge prima di fare push.>

## 6. Consegna
<Commit sul ramo di questa pull request (messaggi in italiano, senza nomi di strumenti);
riga di esito accanto alla richiesta in `COORDINAMENTO.md` § «Richieste», sullo stesso ramo;
un commento breve sulla pull request: fatto / non fatto / perché.>

## 7. Che cosa non fare
<Non unire la pull request, non segnarla pronta, non aprirne altre, non toccare file fuori
dall'elenco del punto 2, non inventare dati mancanti: se manca qualcosa, scriverlo nel commento.>
"""


# --- Utilità -------------------------------------------------------------------

def die(msg: str, code: int = 2) -> None:
    print(f"[passa-a] ERRORE: {msg}", file=sys.stderr)
    sys.exit(code)


def info(msg: str) -> None:
    print(f"[passa-a] {msg}")


def run(cmd: list[str], cwd: str | None = None, check: bool = True, env: dict | None = None,
        quiet: bool = False, input: str | None = None) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, env=env, input=input)
    if check and r.returncode != 0:
        if not quiet:
            print(r.stdout, file=sys.stderr)
            print(r.stderr, file=sys.stderr)
        die(f"comando fallito ({r.returncode}): {' '.join(cmd)}")
    return r


def gh_api(percorso: str, metodo: str = "GET", dati: dict | None = None, ok_se: tuple = (),
           paginato: bool = False):
    """Chiama l'API REST di GitHub con `gh api`. Restituisce il JSON decodificato (o None)."""
    cmd = ["gh", "api", "-X", metodo, percorso, "-H", "Accept: application/vnd.github+json"]
    if paginato:
        cmd.append("--paginate")
    tmp = None
    if dati is not None:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(dati, tmp)
        tmp.close()
        cmd += ["--input", tmp.name]
    r = subprocess.run(cmd, text=True, capture_output=True)
    if tmp:
        os.unlink(tmp.name)
    if r.returncode != 0:
        testo = (r.stdout + r.stderr).strip()
        if any(s in testo for s in ok_se):
            return None
        die(f"GitHub ({metodo} {percorso}): {testo[:800]}")
    out = r.stdout.strip()
    if not out:
        return None
    if paginato:
        # --paginate concatena gli array: li riunisce.
        elementi = []
        dec = json.JSONDecoder()
        pos = 0
        while pos < len(out):
            while pos < len(out) and out[pos].isspace():
                pos += 1
            if pos >= len(out):
                break
            obj, fine = dec.raw_decode(out, pos)
            elementi.extend(obj if isinstance(obj, list) else [obj])
            pos = fine
        return elementi
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return out


def radice_repo() -> Path:
    r = run(["git", "rev-parse", "--show-toplevel"])
    return Path(r.stdout.strip())


def owner_repo(radice: Path) -> str:
    url = run(["git", "remote", "get-url", "origin"], cwd=str(radice)).stdout.strip()
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if not m:
        die(f"remote origin non riconosciuto come GitHub: {url}")
    return f"{m.group(1)}/{m.group(2)}"


def ramo_principale(radice: Path, richiesto: str | None) -> str:
    if richiesto:
        return richiesto
    r = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], cwd=str(radice), check=False)
    if r.returncode == 0:
        return r.stdout.strip().rsplit("/", 1)[-1]
    return "main"


def ambiente_commit(data_autore: str | None = None, data_committer: str | None = None) -> dict:
    """Variabili d'ambiente che firmano un commit a nome di Alessandro (regola firma-dei-lavori)."""
    env = dict(os.environ)
    env.update(GIT_AUTHOR_NAME=NOME_OK, GIT_AUTHOR_EMAIL=EMAIL_OK,
               GIT_COMMITTER_NAME=NOME_OK, GIT_COMMITTER_EMAIL=EMAIL_OK)
    if data_autore:
        env["GIT_AUTHOR_DATE"] = data_autore
    if data_committer:
        env["GIT_COMMITTER_DATE"] = data_committer
    return env


def commit_tree(radice: Path, albero: str, genitori: list[str], messaggio: str,
                data_autore: str | None = None, data_committer: str | None = None) -> str:
    """Crea un commit con `git commit-tree` (nessun checkout: funziona anche su repository enormi)."""
    cmd = ["git", "commit-tree", albero]
    for g in genitori:
        cmd += ["-p", g]
    cmd += ["-F", "-"]
    r = run(cmd, cwd=str(radice), env=ambiente_commit(data_autore, data_committer),
            input=messaggio.rstrip("\n") + "\n")
    return r.stdout.strip()


def albero_con_file(radice: Path, base_sha: str, percorso: str, contenuto: str) -> str:
    """Albero di `base_sha` con `percorso` sostituito da `contenuto` (indice temporaneo, niente checkout)."""
    blob = run(["git", "hash-object", "-w", "--stdin"], cwd=str(radice), input=contenuto).stdout.strip()
    idx = tempfile.NamedTemporaryFile(prefix="passa-a-idx-", delete=False)
    idx.close()
    os.unlink(idx.name)
    env = dict(os.environ, GIT_INDEX_FILE=idx.name)
    try:
        run(["git", "read-tree", base_sha], cwd=str(radice), env=env)
        run(["git", "update-index", "--add", "--cacheinfo", f"100644,{blob},{percorso}"], cwd=str(radice), env=env)
        return run(["git", "write-tree"], cwd=str(radice), env=env).stdout.strip()
    finally:
        if os.path.exists(idx.name):
            os.unlink(idx.name)


def oggi() -> dt.date:
    """Data di oggi in ora italiana (le voci di bacheca e i nomi dei rami la usano)."""
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("Europe/Rome")).date()
    except Exception:  # senza tzdata: l'ora locale della macchina
        return dt.date.today()


def controlla_vietate(testo: str, dove: str) -> None:
    trovate = sorted({m.group(0).strip() for m in VIETATE.finditer(testo)}
                     | {m.group(0) for m in VIETATE_SIGLE.finditer(testo)})
    if trovate:
        die(f"{dove} nomina strumenti o IA ({', '.join(trovate)}): "
            "titolo e descrizione della PR sono pubblici, vanno riscritti senza (regola firma-dei-lavori).")


def controlla_brief(testo: str) -> list[tuple[str, str]]:
    """Verifica le sette parti in ordine e che nessuna sia vuota. Restituisce [(titolo, corpo)]."""
    righe = testo.splitlines()
    indici = []
    for i, riga in enumerate(righe):
        m = re.match(r"^\s*#{1,3}\s*(\d)\.\s*(.+?)\s*$", riga)
        if m:
            indici.append((int(m.group(1)), m.group(2).strip().lower(), i))
    if [n for n, _, _ in indici] != [n for n, _ in PARTI]:
        die("la richiesta deve avere le sette parti nell'ordine `## 1. Obiettivo` … `## 7. Che cosa non fare` "
            "(`passa-a.py modello` stampa lo schema)")
    for (n, parola), (_, titolo, _) in zip(PARTI, indici):
        if not titolo.startswith(parola):
            die(f"la parte {n} deve chiamarsi «{parola.capitalize()}», trovato «{titolo}»")
    parti = []
    for k, (n, titolo, i) in enumerate(indici):
        fine = indici[k + 1][2] if k + 1 < len(indici) else len(righe)
        corpo = "\n".join(righe[i + 1:fine]).strip()
        if not corpo or corpo.startswith("<") and corpo.endswith(">"):
            die(f"la parte {n} ({titolo}) è vuota o ancora da compilare")
        parti.append((righe[i].strip().lstrip("#").strip(), corpo))
    return parti


def voce_bacheca(data: str, titolo: str, ramo: str, parti: list[tuple[str, str]], pr: int | None) -> str:
    """La voce per «Richieste»: una riga di testa e la richiesta indentata sotto."""
    nota = f"passata in automatico; PR #{pr}" if pr else "passata in automatico; PR in apertura"
    righe = [f"- **{data} — da Claude a ChatGPT — {titolo}** ({nota}; ramo `{ramo}`)"]
    for intestazione, corpo in parti:
        righe.append(f"  - **{intestazione}.**")
        for r in corpo.splitlines():
            righe.append(f"    {r}" if r.strip() else "")
    return "\n".join(righe).rstrip() + "\n"


def inserisci_in_richieste(testo: str, voce: str) -> str:
    """Mette la voce in cima all'elenco di «## Richieste», dopo il paragrafo introduttivo."""
    m = re.search(r"^## Richieste[^\n]*\n", testo, re.MULTILINE)
    if not m:
        die(f"sezione «## Richieste» non trovata in {BACHECA}")
    inizio = m.end()
    m2 = re.search(r"^## ", testo[inizio:], re.MULTILINE)
    fine = inizio + m2.start() if m2 else len(testo)
    sezione = testo[inizio:fine]
    m3 = re.search(r"^- \*\*", sezione, re.MULTILINE)
    if m3:
        punto = inizio + m3.start()
        return testo[:punto] + voce + "\n" + testo[punto:]
    return testo[:fine].rstrip("\n") + "\n\n" + voce + "\n" + testo[fine:]


# --- Comandi -------------------------------------------------------------------

def cmd_modello(args) -> None:
    if args.out:
        Path(args.out).write_text(MODELLO, encoding="utf-8")
        info(f"schema scritto in {args.out}")
    else:
        print(MODELLO, end="")


def cmd_nuovo(args) -> None:
    radice = radice_repo()
    repo = owner_repo(radice)
    base = ramo_principale(radice, args.base)
    slug = args.argomento.strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", slug):
        die("--argomento: solo minuscole, cifre e trattini (es. `illustrazione-temporale`)")
    titolo = args.titolo.strip()
    if not titolo:
        die("--titolo vuoto")
    brief_path = Path(args.brief)
    if not brief_path.exists():
        die(f"brief non trovato: {brief_path}")
    brief = brief_path.read_text(encoding="utf-8").strip() + "\n"
    parti = controlla_brief(brief)
    controlla_vietate(titolo, "il titolo")
    controlla_vietate(brief, "la richiesta")

    data = oggi()
    ramo = f"{PREFISSO_RAMO}{slug}-{data:%Y%m%d}"

    # Niente doppioni: una PR aperta sullo stesso ramo o sullo stesso argomento.
    aperte = gh_api(f"repos/{repo}/pulls?state=open&per_page=100", paginato=True) or []
    for pr in aperte:
        ref = pr["head"]["ref"]
        if ref == ramo or ref.startswith(f"{PREFISSO_RAMO}{slug}-"):
            die(f"esiste già la PR #{pr['number']} sul ramo {ref}: controllala con `stato`")

    info(f"repository {repo}, base {base}, ramo {ramo}")
    run(["git", "fetch", "-q", "origin", base], cwd=str(radice))
    if run(["git", "ls-remote", "--heads", "origin", ramo], cwd=str(radice)).stdout.strip():
        die(f"il ramo {ramo} esiste già su origin")
    base_sha = run(["git", "rev-parse", f"origin/{base}"], cwd=str(radice)).stdout.strip()
    r = run(["git", "show", f"{base_sha}:{BACHECA}"], cwd=str(radice), check=False)
    if r.returncode != 0:
        die(f"{BACHECA} non trovato sul ramo {base}")
    testo = r.stdout
    voce = voce_bacheca(f"{data:%Y-%m-%d}", titolo, ramo, parti, None)
    albero = albero_con_file(radice, base_sha, BACHECA, inserisci_in_richieste(testo, voce))
    commit1 = commit_tree(radice, albero, [base_sha], f"Bacheca: richiesta «{titolo}»")
    ref = f"refs/heads/{ramo}"
    run(["git", "update-ref", ref, commit1], cwd=str(radice))

    corpo_pr = (
        f"{brief.rstrip()}\n\n---\n"
        f"La richiesta per esteso, con la stessa data e lo stesso titolo, è nella bacheca "
        f"`{BACHECA}` § «Richieste», su questo ramo. Chi la prende lavora su questo ramo, "
        f"fa i controlli del repository e scrive lì l'esito."
    )
    if args.prova:
        info("PROVA: ramo e voce in bacheca creati solo in locale; niente push, PR o commento.")
        print(run(["git", "show", "--stat", "--format=%an <%ae>%n%s", commit1], cwd=str(radice)).stdout)
        print("---- descrizione della PR ----")
        print(corpo_pr)
        run(["git", "update-ref", "-d", ref], cwd=str(radice), check=False)
        return

    run(["git", "push", "-q", "origin", f"{ref}:{ref}"], cwd=str(radice))
    pr = gh_api(f"repos/{repo}/pulls", "POST", {
        "title": titolo, "head": ramo, "base": base, "body": corpo_pr, "draft": True,
    })
    numero = pr["number"]
    info(f"PR in bozza #{numero}: {pr['html_url']}")

    # Numero della PR nella voce di bacheca (secondo commit: lo squash li riunisce).
    testo2 = run(["git", "show", f"{commit1}:{BACHECA}"], cwd=str(radice)).stdout.replace(
        f"(passata in automatico; PR in apertura; ramo `{ramo}`)",
        f"(passata in automatico; PR #{numero}; ramo `{ramo}`)", 1)
    albero2 = albero_con_file(radice, commit1, BACHECA, testo2)
    commit2 = commit_tree(radice, albero2, [commit1], f"Bacheca: PR #{numero} per «{titolo}»")
    run(["git", "update-ref", ref, commit2, commit1], cwd=str(radice))
    run(["git", "push", "-q", "origin", f"{ref}:{ref}"], cwd=str(radice))

    if not args.senza_avvio:
        gh_api(f"repos/{repo}/issues/{numero}/comments", "POST",
               {"body": COMMENTO_AVVIO + COMMENTO_AVVIO_CODA})
        info("commento di avvio lasciato sulla PR")
    info(f"fatto. Prossimi passi: `passa-a.py stato` per seguire, `passa-a.py chiudi --pr {numero}` per unire.")


def _pr_chatgpt(repo: str, tutte: bool) -> list[dict]:
    aperte = gh_api(f"repos/{repo}/pulls?state=open&per_page=100", paginato=True) or []
    return [p for p in aperte if tutte or p["head"]["ref"].startswith(PREFISSO_RAMO)]


def _quando(iso: str) -> dt.datetime:
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))


def _e_bot(utente: dict) -> bool:
    return (utente or {}).get("type") == "Bot" or "[bot]" in (utente or {}).get("login", "")


def _controlli(repo: str, sha: str) -> tuple[list[dict], str]:
    """Check run sul commit: (elenco, riassunto)."""
    dati = gh_api(f"repos/{repo}/commits/{sha}/check-runs?per_page=100") or {}
    runs = dati.get("check_runs", []) if isinstance(dati, dict) else []
    if not runs:
        return [], "nessun controllo"
    esiti = {}
    for cr in runs:
        esiti[cr["name"]] = cr["conclusion"] or cr["status"]
    return runs, ", ".join(f"{k}: {v}" for k, v in sorted(esiti.items()))


def cmd_stato(args) -> None:
    radice = radice_repo()
    repo = owner_repo(radice)
    prs = _pr_chatgpt(repo, args.tutte)
    if not prs:
        info("nessuna PR aperta sui rami chatgpt/*")
        return
    io_login = (gh_api("user") or {}).get("login", "")
    adesso = dt.datetime.now(dt.timezone.utc)
    for pr in prs:
        n = pr["number"]
        commenti = gh_api(f"repos/{repo}/issues/{n}/comments?per_page=100", paginato=True) or []
        commits = gh_api(f"repos/{repo}/pulls/{n}/commits?per_page=100", paginato=True) or []
        avvio = next((c for c in commenti if c["user"]["login"] == io_login
                      and c["body"].strip().lower().startswith("@codex")), None)
        t_avvio = _quando(avvio["created_at"]) if avvio else None
        risposte = [c for c in commenti if _e_bot(c["user"])]
        crediti_finiti = any(re.search(r"usage limit|reached your .*limit|crediti", c["body"], re.I)
                             for c in risposte)
        dopo = [c for c in commits if t_avvio and _quando(c["commit"]["committer"]["date"]) > t_avvio]
        altri_autori = sorted({f"{c['commit']['author']['name']} <{c['commit']['author']['email']}>"
                               for c in commits
                               if c["commit"]["author"]["email"].lower() not in AUTORI_OK})
        _, riass = _controlli(repo, pr["head"]["sha"])
        print(f"\nPR #{n} {'[bozza]' if pr['draft'] else '[pronta]'} — {pr['title']}")
        print(f"  ramo {pr['head']['ref']} · {pr['html_url']}")
        if t_avvio:
            ore = (adesso - t_avvio).total_seconds() / 3600
            print(f"  avvio: {t_avvio.astimezone().strftime('%d/%m %H:%M')} ({ore:.1f} h fa)")
        else:
            print("  avvio: nessun commento di avvio trovato")
        print(f"  commit totali {len(commits)}, dopo l'avvio {len(dopo)}")
        if altri_autori:
            print(f"  autori da riscrivere prima di unire: {'; '.join(altri_autori)}")
        if risposte:
            ultima = risposte[-1]
            testo = re.sub(r"\s+", " ", ultima["body"]).strip()
            print(f"  ultima risposta dello strumento ({_quando(ultima['created_at']).astimezone().strftime('%d/%m %H:%M')}): {testo[:220]}")
        else:
            print("  risposte dello strumento: nessuna")
        print(f"  controlli: {riass}")
        if crediti_finiti:
            giudizio = "CREDITI FINITI: il lavoro lo fa Claude da sola e lo scrive in bacheca"
        elif dopo:
            giudizio = "HA FATTO PUSH: controllare il risultato, poi `chiudi --pr %d`" % n
        elif t_avvio and (adesso - t_avvio) > dt.timedelta(hours=24):
            giudizio = "NESSUNA RISPOSTA DA OLTRE 24 ORE: il lavoro lo fa Claude da sola e lo scrive in bacheca"
        elif risposte:
            giudizio = "in lavorazione (ha risposto, nessun push ancora)"
        else:
            giudizio = "in attesa"
        print(f"  => {giudizio}")


def _messaggio_pulito(body: str) -> str:
    righe = [r for r in body.splitlines()
             if not re.match(r"^\s*(co-authored-by|signed-off-by|claude-session|generated (with|by))", r, re.I)]
    testo = "\n".join(righe)
    testo = re.sub(r"\b(ChatGPT|Chat GPT|Codex|OpenAI|Claude|Anthropic|Copilot)\b", "lavoro", testo)
    testo = re.sub(r"\n{3,}", "\n\n", testo).strip()
    return testo or "Lavoro sul ramo"


def _riscrivi_autori(radice: Path, repo: str, ramo: str, base: str) -> bool:
    """Riscrive a nome di Alessandro i commit del ramo con un altro autore o con righe di strumento.
    Usa solo oggetti git (commit-tree): nessun checkout. Restituisce True se ha fatto push."""
    run(["git", "fetch", "-q", "origin", base, ramo], cwd=str(radice))
    vecchio_sha = run(["git", "rev-parse", f"origin/{ramo}"], cwd=str(radice)).stdout.strip()
    mb = run(["git", "merge-base", f"origin/{base}", f"origin/{ramo}"], cwd=str(radice)).stdout.strip()
    shas = run(["git", "rev-list", "--reverse", "--topo-order", f"{mb}..origin/{ramo}"],
               cwd=str(radice)).stdout.split()
    if not shas:
        info("nessun commit sul ramo oltre la base")
        return False
    nuovi: dict[str, str] = {}
    riscritti = 0
    for sha in shas:
        campi = run(["git", "log", "-1", "--format=%T%x1f%P%x1f%an%x1f%ae%x1f%cn%x1f%ce%x1f%aI%x1f%cI%x1f%B", sha],
                    cwd=str(radice)).stdout
        albero, genitori, an, ae, cn, ce, ad, cd, body = campi.split("\x1f", 8)
        genitori = genitori.split()
        msg = _messaggio_pulito(body)
        da_cambiare = (ae.lower() not in AUTORI_OK or ce.lower() not in AUTORI_OK
                       or an.lower() not in NOMI_OK or msg != body.strip())
        genitori_nuovi = [nuovi.get(g, g) for g in genitori]
        if not da_cambiare and genitori_nuovi == genitori:
            nuovi[sha] = sha
            continue
        nuovi[sha] = commit_tree(radice, albero, genitori_nuovi, msg, data_autore=ad, data_committer=cd)
        riscritti += 1
    nuovo_sha = nuovi[shas[-1]]
    if nuovo_sha == vecchio_sha:
        info("commit del ramo già a nome di Alessandro, nessuna riscrittura")
        return False
    run(["git", "push", "-q", f"--force-with-lease={ramo}:{vecchio_sha}", "origin",
         f"{nuovo_sha}:refs/heads/{ramo}"], cwd=str(radice))
    info(f"{riscritti} commit riscritti a nome di Alessandro; ramo {ramo} ripubblicato "
         f"({vecchio_sha[:7]} → {nuovo_sha[:7]})")
    return True


def _segna_pronta(repo: str, n: int) -> None:
    r = subprocess.run(["gh", "api", "-X", "POST", f"repos/{repo}/pulls/{n}/ccr/ready_for_review"],
                       text=True, capture_output=True)
    if r.returncode == 0:
        return
    r2 = subprocess.run(["gh", "pr", "ready", str(n), "-R", repo], text=True, capture_output=True)
    if r2.returncode != 0:
        die(f"non riesco a segnare pronta la PR #{n}: {(r.stderr + r2.stderr).strip()[:400]}")


def _aspetta_controlli(repo: str, n: int, minuti: int) -> str:
    """Aspetta che i check run dell'ultimo commit siano tutti conclusi. Restituisce lo sha."""
    scadenza = time.time() + minuti * 60
    visti_qualcosa = False
    inizio = time.time()
    while True:
        pr = gh_api(f"repos/{repo}/pulls/{n}")
        sha = pr["head"]["sha"]
        runs, riass = _controlli(repo, sha)
        if runs:
            visti_qualcosa = True
            pendenti = [r for r in runs if r["status"] != "completed"]
            falliti = [r for r in runs if r["status"] == "completed"
                       and r["conclusion"] not in ("success", "skipped", "neutral")]
            if not pendenti:
                if falliti:
                    die("controlli rossi, non unisco: " + "; ".join(
                        f"{r['name']} ({r['conclusion']}) {r.get('html_url', '')}" for r in falliti))
                info(f"controlli verdi: {riass}")
                return sha
            info(f"in attesa di {len(pendenti)} controlli… ({riass})")
        elif time.time() - inizio > 150:
            info("nessun controllo automatico su questa PR: procedo")
            return sha
        if time.time() > scadenza:
            die(f"i controlli non si sono conclusi entro {minuti} minuti")
        time.sleep(30)


def _pulisci_commenti(repo: str, n: int, io_login: str) -> None:
    commenti = gh_api(f"repos/{repo}/issues/{n}/comments?per_page=100", paginato=True) or []
    tolti = 0
    for c in commenti:
        mio_avvio = c["user"]["login"] == io_login and c["body"].strip().lower().startswith("@codex")
        if mio_avvio or _e_bot(c["user"]):
            gh_api(f"repos/{repo}/issues/comments/{c['id']}", "DELETE", ok_se=("404",))
            tolti += 1
    revisioni = gh_api(f"repos/{repo}/pulls/{n}/comments?per_page=100", paginato=True) or []
    for c in revisioni:
        if _e_bot(c["user"]):
            gh_api(f"repos/{repo}/pulls/comments/{c['id']}", "DELETE", ok_se=("404",))
            tolti += 1
    info(f"commenti tolti dalla PR: {tolti} (le revisioni del bot, se ci sono, non si possono cancellare)")


def cmd_chiudi(args) -> None:
    radice = radice_repo()
    repo = owner_repo(radice)
    n = args.pr
    pr = gh_api(f"repos/{repo}/pulls/{n}")
    if pr["state"] != "open":
        die(f"la PR #{n} non è aperta ({pr['state']})")
    ramo = pr["head"]["ref"]
    base = pr["base"]["ref"]
    if not ramo.startswith(PREFISSO_RAMO) and not args.qualsiasi:
        die(f"la PR #{n} non è su un ramo chatgpt/* ({ramo}); usa --qualsiasi se è voluto")
    titolo = args.titolo or pr["title"]
    controlla_vietate(titolo, "il titolo del merge")
    io_login = (gh_api("user") or {}).get("login", "")

    _riscrivi_autori(radice, repo, ramo, base)

    if pr["draft"]:
        _segna_pronta(repo, n)
        info(f"PR #{n} segnata pronta")
    sha = _aspetta_controlli(repo, n, args.attesa_minuti)

    if args.senza_merge:
        info("--senza-merge: mi fermo prima di unire")
        return
    messaggio = args.messaggio or f"Richiesta della bacheca di coordinamento: {titolo}."
    controlla_vietate(messaggio, "il messaggio del merge")
    esito = gh_api(f"repos/{repo}/pulls/{n}/merge", "PUT", {
        "merge_method": "squash", "commit_title": f"{titolo} (#{n})", "commit_message": messaggio, "sha": sha,
    })
    if not (esito and esito.get("merged")):
        die(f"merge non riuscito: {esito}")
    info(f"PR #{n} unita con squash: {esito.get('sha', '')[:7]}")
    gh_api(f"repos/{repo}/git/refs/heads/{ramo}", "DELETE", ok_se=("422", "404"))
    if not args.senza_pulizia:
        _pulisci_commenti(repo, n, io_login)
    if (radice / ".github" / "workflows" / "deploy.yml").exists():
        info(f"deploy: https://github.com/{repo}/actions/workflows/deploy.yml — verifica che parta e finisca")
    info("ricorda: la voce in bacheca va spostata in «Archiviati» con l'esito nella prossima PR")


# --- Main ----------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pm = sub.add_parser("modello", help="stampa lo schema della richiesta")
    pm.add_argument("--out", help="scrive lo schema in questo file invece che a schermo")
    pm.set_defaults(fn=cmd_modello)

    pn = sub.add_parser("nuovo", help="avvia un passaggio: ramo, bacheca, PR in bozza, commento")
    pn.add_argument("--argomento", required=True, help="slug del ramo chatgpt/<argomento>-AAAAMMGG")
    pn.add_argument("--titolo", required=True, help="titolo della PR e della voce in bacheca (senza nomi di strumenti)")
    pn.add_argument("--brief", required=True, help="file Markdown con le sette parti della richiesta")
    pn.add_argument("--base", help="ramo di partenza (predefinito: quello principale del repository)")
    pn.add_argument("--prova", action="store_true", help="solo in locale: niente push, PR, commento")
    pn.add_argument("--senza-avvio", action="store_true", help="apre la PR senza il commento di avvio")
    pn.set_defaults(fn=cmd_nuovo)

    ps = sub.add_parser("stato", help="stato delle PR sui rami chatgpt/*")
    ps.add_argument("--tutte", action="store_true", help="tutte le PR aperte, non solo chatgpt/*")
    ps.set_defaults(fn=cmd_stato)

    pc = sub.add_parser("chiudi", help="riscrive gli autori, segna pronta, aspetta i controlli, unisce")
    pc.add_argument("--pr", type=int, required=True)
    pc.add_argument("--titolo", help="titolo del commit di merge (predefinito: titolo della PR)")
    pc.add_argument("--messaggio", help="corpo del commit di merge (predefinito: riga sulla bacheca)")
    pc.add_argument("--attesa-minuti", type=int, default=40)
    pc.add_argument("--senza-pulizia", action="store_true", help="non toglie i commenti dalla PR")
    pc.add_argument("--senza-merge", action="store_true", help="si ferma dopo i controlli, senza unire")
    pc.add_argument("--qualsiasi", action="store_true", help="accetta anche rami non chatgpt/*")
    pc.set_defaults(fn=cmd_chiudi)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
