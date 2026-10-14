#!/usr/bin/env python3
"""
Passa un lavoro a ChatGPT (Codex) e lo richiude a nome di Alessandro — preparato da Claude,
avviato da Alessandro, chiuso da Claude: ramo `chatgpt/…`, voce in bacheca, PR in bozza con
la richiesta, testo di avvio da incollare in Codex Cloud.

Protocollo: `COORDINAMENTO.md` § «Passaggio a ChatGPT» (uguale in tutti i repository di
Alessandro) e regola `.claude/rules/firma-dei-lavori.md`. In Codex Cloud i gesti a mano sono
due, entrambi di Alessandro: l'avvio (incolla il testo di avvio) e, a lavoro finito, «Create PR»
dal task, che apre la pull request di consegna (la documentazione di Codex Cloud: «Review
changes and test results before committing or opening a pull request»). Il commento `@codex …`
sulla PR, che avvierebbe Codex da solo, per l'account di Alessandro non funziona (difetto aperto
del canale delle PR, verificato il 13/10/2026 con gli ambienti cloud pubblicati): si usa solo con
`--con-codex`, per riprovarlo senza spendere nulla.

Comandi
  modello                       stampa lo schema della richiesta (sette parti, da compilare)
  nuovo  --argomento SLUG --titolo "…" --brief FILE.md [--base main] [--prova] [--con-codex]
                                ramo chatgpt/SLUG-AAAAMMGG da origin/BASE, voce in «Richieste»,
                                PR in bozza (titolo + brief), numero della PR in bacheca; stampa
                                il testo di avvio (intestazione + richiesta completa) da incollare
                                in Codex Cloud. Con --con-codex lascia anche il commento
                                «@codex esegui la richiesta nella descrizione»
  stato  [--tutte]              le PR aperte sui rami chatgpt/*: bozza, pull request di consegna
                                (certe o possibili), commit arrivati dopo la preparazione,
                                risposte dello strumento, canale muto, crediti esauriti, controlli
  riavvia --pr N [--con-codex]  ristampa il testo di avvio di una PR già aperta (e, con
                                --con-codex, rimanda il commento di avvio)
  chiudi --pr N [--consegna M] [--attesa-minuti 40] [--attesa-deploy-minuti 30]
         [--senza-pulizia] [--senza-merge] [--senza-attesa-deploy]
                                con --consegna porta nel ramo il lavoro arrivato nella PR M
                                (aperta dal task con «Create PR»), le dà un titolo neutro (e la
                                descrizione, se è dell'account di Alessandro) e la chiude come
                                assorbita; poi riscrive a nome di Alessandro i commit con un
                                altro autore, porta nel ramo le novità della base (merge, mai
                                rebase), sposta in «Archiviati» la voce di bacheca con la riga
                                di esito, segna la PR pronta, aspetta i controlli, squash merge
                                con messaggio scritto, toglie dalle PR i commenti dello
                                strumento, cancella il ramo e, dove c'è `deploy.yml`, aspetta
                                che il deploy del merge finisca bene. Con --senza-merge si
                                ferma dopo aver portato dentro la consegna, riscritto gli
                                autori e allineato il ramo: la PR resta in bozza e la voce in
                                «Richieste»; aggiorna la copia locale del ramo (se non è quella
                                in uso) e stampa i passi per correggere sul ramo, poi si
                                rilancia `chiudi` (anche con lo stesso --consegna)

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
import shlex
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
    "indicati prima del push, non modificare `COORDINAMENTO.md` (l'esito lo scrive chi chiude) "
    "e rispondi con un commento breve: che cosa hai fatto, che cosa resta e perché."
)
# Nota nella riga di testa della voce di bacheca: chi prepara, chi avvia.
NOTA_PREPARATA = "preparata da Claude, da avviare a mano in Codex Cloud"
# Piede della descrizione della PR preparata: separa la richiesta (sopra) dal resto. `riavvia` lo
# usa per ricavare la richiesta dalla descrizione, quindi il suo inizio non va cambiato.
PIEDE_PR = (
    "\n\n---\nLa richiesta per esteso, con la stessa data e lo stesso titolo, è anche nella bacheca "
    f"`{BACHECA}` § «Richieste», su questo ramo. Il lavoro arriva su questo ramo o con una pull "
    "request di consegna; l'esito in bacheca lo scrive chi chiude."
)
INIZIO_PIEDE_PR = "\n\n---\nLa richiesta per esteso"
# Messaggi di commit di servizio dello script: non sono lavoro consegnato dallo strumento.
PREFISSI_SERVIZIO = ("Bacheca: richiesta «", "Bacheca: PR #", "Bacheca: archiviata ", "Allineamento con ",
                     "Consegna dalla pull request #")

# Parole che non possono comparire in titolo e descrizione della PR (testi pubblici).
VIETATE = re.compile(
    r"\b(claude|chatgpt|chat gpt|codex|openai|anthropic|gemini|jules|copilot|llm|"
    r"intelligenza artificiale|artificial intelligence)\b",
    re.IGNORECASE,
)
# Le sigle vanno cercate rispettando le maiuscole: «ai» e «ia» minuscole sono parole italiane.
VIETATE_SIGLE = re.compile(r"\b(IA|AI|LLM)\b")
# Account degli strumenti su GitHub (commenti e revisioni da togliere a lavoro unito).
# `github-actions[bot]` NON c'è: i suoi rapporti (accessibilità, controlli) restano sulla PR.
BOT_STRUMENTO = re.compile(r"codex|chatgpt|openai|claude|anthropic|gemini|jules|copilot", re.IGNORECASE)
# Righe di trailer da togliere dai messaggi di commit (qualunque strumento).
TRAILER_STRUMENTO = re.compile(
    r"^\s*(co-?authored-by\s*:|signed-off-by\s*:|claude-session\s*:|generated (with|by)\b|🤖|made with\b)",
    re.IGNORECASE,
)

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
<Comandi esatti da eseguire prima di consegnare, con il risultato atteso (es. `python3 scripts/…`,
`hugo --minify`). Se un controllo fallisce, si corregge prima di consegnare.>

## 6. Consegna
<Solo le modifiche ai file del punto 2, con messaggi di commit in italiano e senza nomi di
strumenti; alla fine un riassunto breve: fatto / non fatto / perché. `COORDINAMENTO.md` non
si tocca: l'esito in bacheca lo scrive chi chiude il lavoro.>

## 7. Che cosa non fare
<Non unire nulla, non segnare pronta nessuna pull request, non toccare file fuori dall'elenco
del punto 2, non inventare dati mancanti: se manca qualcosa, scriverlo nel riassunto finale.>
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
           paginato: bool = False, tollerante: bool = False):
    """Chiama l'API REST di GitHub con `gh api`. Restituisce il JSON decodificato (o None).
    Con `tollerante=True` un errore non ferma lo script: restituisce ("ERRORE", testo)."""
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
        if tollerante:
            return ("ERRORE", testo[:300])
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


def fetch_rami(radice: Path, *rami: str) -> None:
    """Aggiorna `origin/<ramo>` con refspec espliciti: i cloni delle sessioni cloud sono a ramo singolo
    (`fetch = +refs/heads/main:…`) e `git fetch origin <ramo>` lì non crea il riferimento remoto."""
    cmd = ["git", "fetch", "-q", "origin"] + [f"+refs/heads/{r}:refs/remotes/origin/{r}" for r in rami]
    run(cmd, cwd=str(radice))


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


def testo_avvio(repo: str, ramo: str, titolo: str, data: str, pr: int | str, brief: str) -> str:
    """Il testo che Alessandro incolla in Codex Cloud: un'intestazione breve e la richiesta completa.
    Il contenitore di Codex non legge la pull request e la sua rete può essere limitata, e il
    selettore del ramo può restare sul principale: per questo la richiesta viaggia intera nel testo
    e non rimanda né alla bacheca né a pagine esterne."""
    return (
        f"Richiesta «{titolo}» del {data} per il repository {repo} (pull request #{pr}, ramo {ramo}).\n"
        f"Lavora sul ramo {ramo} se è quello selezionato per questo task; altrimenti va bene il ramo "
        f"principale. Esegui la richiesta qui sotto punto per punto e i controlli che indica prima di "
        f"consegnare. Non modificare {BACHECA}: l'esito lo scrive chi chiude il lavoro. Messaggi di "
        f"commit in italiano, senza nomi di strumenti. Non unire nulla. Alla fine riassumi in poche "
        f"righe che cosa hai fatto, che cosa resta e perché.\n\n"
        f"{brief.strip()}\n"
    )


def stampa_avvio(repo: str, ramo: str, pr: int | str, testo: str) -> None:
    """Stampa il testo di avvio e i due gesti di Alessandro (gli unici passaggi a mano del protocollo)."""
    print("\n==== testo da incollare in Codex Cloud (chatgpt.com/codex) — inizio ====")
    print(testo.rstrip())
    print("==== testo da incollare in Codex Cloud — fine ====")
    print("---- per Alessandro ----")
    print(f"1. Avvio: chatgpt.com/codex → ambiente di {repo} → ramo «{ramo}» se il selettore lo "
          f"offre (altrimenti il principale) → incolla il testo qui sopra → avvia.")
    print("2. Consegna: quando Codex ha finito, «Create PR» dal task. Nient'altro: non unire.")
    print(f"3. Il resto lo fa la sessione: `passa-a.py stato` riconosce la pull request di consegna #M, "
          f"`passa-a.py chiudi --pr {pr} --consegna M` la porta nel ramo e unisce.")


def voce_bacheca(data: str, titolo: str, ramo: str, parti: list[tuple[str, str]], pr: int | None) -> str:
    """La voce per «Richieste»: una riga di testa, la nota sull'avvio a mano (quando la PR c'è) e la
    richiesta indentata sotto."""
    nota = f"{NOTA_PREPARATA}; PR #{pr}" if pr else f"{NOTA_PREPARATA}; PR in apertura"
    righe = [f"- **{data} — da Claude a ChatGPT — {titolo}** ({nota}; ramo `{ramo}`)"]
    if pr:
        righe.append(f"  - **Avvio a mano (Alessandro).** In Codex Cloud: ambiente del repository, ramo "
                     f"`{ramo}` se il selettore lo offre, poi il testo di avvio (intestazione più le sette "
                     f"parti qui sotto: lo stampa `passa-a.py nuovo`, lo ristampa `passa-a.py riavvia --pr {pr}`). "
                     f"A lavoro finito, «Create PR» dal task: la pull request di consegna la porta nel ramo "
                     f"e la chiude `passa-a.py chiudi --pr {pr} --consegna M`.")
    for intestazione, corpo in parti:
        righe.append(f"  - **{intestazione}.**")
        for r in corpo.splitlines():
            righe.append(f"    {r}" if r.strip() else "")
    return "\n".join(righe).rstrip() + "\n"


def _sezione(testo: str, nome: str) -> tuple[int, int]:
    """Inizio e fine del corpo della sezione `## <nome>` (senza la riga di titolo)."""
    m = re.search(rf"^## {re.escape(nome)}[^\n]*\n", testo, re.MULTILINE)
    if not m:
        die(f"sezione «## {nome}» non trovata in {BACHECA}")
    inizio = m.end()
    m2 = re.search(r"^## ", testo[inizio:], re.MULTILINE)
    return inizio, (inizio + m2.start() if m2 else len(testo))


def inserisci_in_sezione(testo: str, nome: str, voce: str, sentinella: str) -> str:
    """Mette la voce in cima all'elenco di `## <nome>`, dopo l'eventuale paragrafo introduttivo,
    togliendo la riga sentinella («Nessuna richiesta aperta», «Nessuna voce»)."""
    inizio, fine = _sezione(testo, nome)
    sezione = testo[inizio:fine]
    sezione = re.sub(rf"^- \*{{0,2}}{sentinella}\b[^\n]*\n?", "", sezione, flags=re.MULTILINE)
    m3 = re.search(r"^- \*\*", sezione, re.MULTILINE)
    if m3:
        punto = m3.start()
        sezione = sezione[:punto] + voce + "\n" + sezione[punto:]
    else:
        prima = sezione.rstrip("\n")
        sezione = (prima + "\n\n" if prima.strip() else "\n") + voce + "\n"
    return testo[:inizio] + sezione + testo[fine:]


def inserisci_in_richieste(testo: str, voce: str) -> str:
    return inserisci_in_sezione(testo, "Richieste", voce, "Nessuna richiesta aperta")


def archivia_voce(testo: str, n: int, base: str, data: str, esito: str | None = None) -> str | None:
    """Sposta la voce di «Richieste» che porta «PR #n» in cima ad «Archiviati», con la riga di esito.
    Restituisce il testo nuovo, o None se la voce non c'è."""
    esito = esito or f"Lavoro consegnato e unito in `{base}` con la pull request #{n}."
    inizio, fine = _sezione(testo, "Richieste")
    sezione = testo[inizio:fine]
    voci = list(re.finditer(r"^- \*\*.*$", sezione, re.MULTILINE))
    trovata = None
    for i, v in enumerate(voci):
        if re.search(rf"PR #{n}\b", v.group(0)):
            trovata = (v.start(), voci[i + 1].start() if i + 1 < len(voci) else len(sezione))
            break
    if not trovata:
        return None
    a, b = trovata
    voce = sezione[a:b].rstrip("\n") + "\n"
    resto = sezione[:a] + sezione[b:]
    resto = re.sub(r"^- \*{0,2}Nessuna richiesta aperta\b[^\n]*\n?", "", resto, flags=re.MULTILINE)
    if not re.search(r"^- \*\*", resto, re.MULTILINE):
        resto = resto.rstrip("\n") + "\n\n- Nessuna richiesta aperta."
    resto = "\n" + re.sub(r"\n{3,}", "\n\n", resto).strip("\n") + "\n\n"
    testo = testo[:inizio] + resto + testo[fine:]
    righe = voce.splitlines()
    righe.insert(1, f"  - **Esito ({data}).** {esito}")
    voce = "\n".join(righe) + "\n"
    if not re.search(r"^## Archiviati", testo, re.MULTILINE):
        testo = testo.rstrip("\n") + "\n\n## Archiviati\n\n"
    return inserisci_in_sezione(testo, "Archiviati", voce, "Nessuna voce")


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
    fetch_rami(radice, base)
    if run(["git", "ls-remote", "--heads", "origin", ramo], cwd=str(radice)).stdout.strip():
        die(f"il ramo {ramo} esiste già su origin")
    ref = f"refs/heads/{ramo}"
    if run(["git", "show-ref", "--verify", "--quiet", ref], cwd=str(radice), check=False).returncode == 0:
        die(f"il ramo {ramo} esiste già in locale: non lo sovrascrivo (cancellalo con "
            f"`git branch -D {ramo}` se è un residuo, o scegli un altro --argomento)")
    base_sha = run(["git", "rev-parse", f"origin/{base}"], cwd=str(radice)).stdout.strip()
    r = run(["git", "show", f"{base_sha}:{BACHECA}"], cwd=str(radice), check=False)
    if r.returncode != 0:
        die(f"{BACHECA} non trovato sul ramo {base}")
    testo = r.stdout
    data_str = f"{data:%Y-%m-%d}"
    voce1 = voce_bacheca(data_str, titolo, ramo, parti, None)
    albero = albero_con_file(radice, base_sha, BACHECA, inserisci_in_richieste(testo, voce1))
    commit1 = commit_tree(radice, albero, [base_sha], f"Bacheca: richiesta «{titolo}»")
    # Il vecchio valore «tutto zeri» chiede a git di creare il ramo solo se non esiste ancora.
    run(["git", "update-ref", ref, commit1, "0" * 40], cwd=str(radice))

    corpo_pr = f"{brief.rstrip()}{PIEDE_PR}"
    if args.prova:
        info("PROVA: ramo e voce in bacheca creati solo in locale; niente push, PR o commento.")
        print(run(["git", "show", "--stat", "--format=%an <%ae>%n%s", commit1], cwd=str(radice)).stdout)
        print("---- descrizione della PR ----")
        print(corpo_pr)
        print("---- voce in bacheca dopo l'apertura della PR (con N al posto del numero) ----")
        print(voce_bacheca(data_str, titolo, ramo, parti, "N"))
        stampa_avvio(repo, ramo, "N", testo_avvio(repo, ramo, titolo, data_str, "N", brief))
        run(["git", "update-ref", "-d", ref], cwd=str(radice), check=False)
        return

    run(["git", "push", "-q", "origin", f"{ref}:{ref}"], cwd=str(radice))
    pr = gh_api(f"repos/{repo}/pulls", "POST", {
        "title": titolo, "head": ramo, "base": base, "body": corpo_pr, "draft": True,
    })
    numero = pr["number"]
    info(f"PR in bozza #{numero}: {pr['html_url']}")

    # Numero della PR e nota sull'avvio a mano nella voce di bacheca (secondo commit: lo squash li riunisce).
    voce2 = voce_bacheca(data_str, titolo, ramo, parti, numero)
    testo1 = run(["git", "show", f"{commit1}:{BACHECA}"], cwd=str(radice)).stdout
    testo2 = testo1.replace(voce1, voce2, 1)
    if testo2 == testo1:
        die(f"voce di bacheca non ritrovata nel commit {commit1[:7]}: non aggiorno il ramo")
    albero2 = albero_con_file(radice, commit1, BACHECA, testo2)
    commit2 = commit_tree(radice, albero2, [commit1], f"Bacheca: PR #{numero} per «{titolo}»")
    run(["git", "update-ref", ref, commit2, commit1], cwd=str(radice))
    run(["git", "push", "-q", "origin", f"{ref}:{ref}"], cwd=str(radice))

    if args.con_codex:
        gh_api(f"repos/{repo}/issues/{numero}/comments", "POST",
               {"body": COMMENTO_AVVIO + COMMENTO_AVVIO_CODA})
        info("commento di avvio lasciato sulla PR (canale automatico, da riprovare: se lo strumento "
             "chiede un ambiente, si procede con il testo di avvio qui sotto)")
    stampa_avvio(repo, ramo, numero, testo_avvio(repo, ramo, titolo, data_str, numero, brief))
    info(f"fatto. Poi: `passa-a.py stato` per seguire, `passa-a.py chiudi --pr {numero} --consegna M` per unire.")


def _quando(iso: str) -> dt.datetime:
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))


def _ora_it(d: dt.datetime) -> str:
    """Data e ora in ora italiana (nelle sessioni cloud l'ora locale della macchina è UTC)."""
    try:
        from zoneinfo import ZoneInfo
        d = d.astimezone(ZoneInfo("Europe/Rome"))
    except Exception:
        d = d.astimezone()
    return d.strftime("%d/%m %H:%M")


def _di_servizio(messaggio: str) -> bool:
    """Commit fatti dallo script (bacheca, allineamento, consegna), non lavoro arrivato dallo strumento."""
    return messaggio.startswith(PREFISSI_SERVIZIO)


def _consegne(aperte: list[dict], n: int, ramo: str, titolo: str,
              t_prep: dt.datetime | None, t_pr: dt.datetime | None) -> tuple[list[dict], list[dict]]:
    """Le pull request aperte con cui il lavoro è stato consegnato (in Codex Cloud: «Create PR» dal
    task). Contano solo quelle aperte dopo la preparazione (o, se la sua ora non si ricava, dopo la PR
    preparata): una pull request più vecchia non può essere la consegna. Certe: base = il ramo
    preparato, oppure titolo o descrizione che citano quel ramo o la PR #n. Possibili, da riconoscere
    guardandole prima di assorbirle: quelle che riportano solo il titolo della richiesta (un titolo
    generico può coincidere per caso) e i rami `codex/…` senza altri segni, quando il task è partito
    dal ramo principale. Le pull request delle sessioni (`claude/…`, `chatgpt/…`) contano solo se
    puntano al ramo preparato."""
    certe, possibili = [], []
    soglia = t_prep or t_pr
    for p in aperte:
        if p["number"] == n or p["head"]["ref"] == ramo:
            continue
        if soglia is not None and _quando(p["created_at"]) <= soglia:
            continue
        testo = f"{p.get('title') or ''}\n{p.get('body') or ''}"
        nostra = p["head"]["ref"].startswith(("claude/", PREFISSO_RAMO))
        if p["base"]["ref"] == ramo:
            certe.append(p)
        elif nostra:
            continue
        elif ramo in testo or re.search(rf"#{n}\b", testo):
            certe.append(p)
        elif (titolo and titolo.lower() in testo.lower()) or p["head"]["ref"].startswith("codex/"):
            possibili.append(p)
    return certe, possibili


def _e_bot(utente: dict) -> bool:
    return (utente or {}).get("type") == "Bot" or "[bot]" in (utente or {}).get("login", "")


def _e_strumento(utente: dict) -> bool:
    """Vero per l'account di uno strumento (Codex e simili), falso per `github-actions[bot]`."""
    return _e_bot(utente) and bool(BOT_STRUMENTO.search((utente or {}).get("login", "")))


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
    aperte = gh_api(f"repos/{repo}/pulls?state=open&per_page=100", paginato=True) or []
    prs = [p for p in aperte if args.tutte or p["head"]["ref"].startswith(PREFISSO_RAMO)]
    if not prs:
        info("nessuna PR aperta sui rami chatgpt/*")
        return
    io_login = (gh_api("user") or {}).get("login", "")
    adesso = dt.datetime.now(dt.timezone.utc)
    for pr in prs:
        n = pr["number"]
        ramo = pr["head"]["ref"]
        commenti = gh_api(f"repos/{repo}/issues/{n}/comments?per_page=100", paginato=True) or []
        commits = gh_api(f"repos/{repo}/pulls/{n}/commits?per_page=100", paginato=True) or []
        avvio = next((c for c in commenti if c["user"]["login"] == io_login
                      and c["body"].strip().lower().startswith("@codex")), None)
        t_avvio = _quando(avvio["created_at"]) if avvio else None
        # La preparazione finisce con il commit «Bacheca: PR #N …»: ciò che arriva dopo è lavoro consegnato.
        prep = [c for c in commits if c["commit"]["message"].startswith("Bacheca: PR #")]
        t_prep = _quando(prep[-1]["commit"]["committer"]["date"]) if prep else None
        riferimenti = [t for t in (t_prep, t_avvio) if t]
        t_rif = max(riferimenti) if riferimenti else None
        risposte = [c for c in commenti if _e_strumento(c["user"])]
        crediti_finiti = any(re.search(r"usage limit|reached your .*limit|crediti", c["body"], re.I)
                             for c in risposte)
        ambiente_manca = any(re.search(r"create an environment|crea un ambiente", c["body"], re.I)
                             for c in risposte)
        dopo = [c for c in commits if not _di_servizio(c["commit"]["message"])
                and (t_rif is None or _quando(c["commit"]["committer"]["date"]) > t_rif)]
        certe, possibili = _consegne(aperte, n, ramo, pr["title"], t_prep, _quando(pr["created_at"]))
        altri_autori = sorted({f"{c['commit']['author']['name']} <{c['commit']['author']['email']}>"
                               for c in commits
                               if c["commit"]["author"]["email"].lower() not in AUTORI_OK})
        _, riass = _controlli(repo, pr["head"]["sha"])
        print(f"\nPR #{n} {'[bozza]' if pr['draft'] else '[pronta]'} — {pr['title']}")
        print(f"  ramo {ramo} · {pr['html_url']}")
        if t_prep:
            ore = (adesso - t_prep).total_seconds() / 3600
            print(f"  preparata: {_ora_it(t_prep)} ({ore:.1f} h fa)")
        else:
            print("  preparata: data non ricavabile (nessun commit «Bacheca: PR #…» sul ramo)")
        if t_avvio:
            print(f"  commento di avvio automatico: {_ora_it(t_avvio)}")
        print(f"  commit totali {len(commits)}, di lavoro arrivati dopo la preparazione {len(dopo)}")
        for c in certe:
            print(f"  consegna in pull request: #{c['number']} ({c['head']['ref']} → {c['base']['ref']}) · {c['html_url']}")
        for c in possibili:
            print(f"  possibile consegna (da riconoscere guardandola): #{c['number']} "
                  f"({c['head']['ref']} → {c['base']['ref']}) · {c['html_url']}")
        if altri_autori:
            print(f"  autori da riscrivere prima di unire: {'; '.join(altri_autori)}")
        if risposte:
            ultima = risposte[-1]
            testo = re.sub(r"\s+", " ", ultima["body"]).strip()
            print(f"  ultima risposta dello strumento ({_ora_it(_quando(ultima['created_at']))}): {testo[:220]}")
        print(f"  controlli: {riass}")
        if certe:
            m = certe[0]["number"]
            giudizio = (f"CONSEGNA NELLA PR #{m}: controllare il risultato, poi "
                        f"`chiudi --pr {n} --consegna {m}` (porta il lavoro nel ramo e chiude la #{m})")
        elif possibili:
            m = possibili[0]["number"]
            giudizio = (f"POSSIBILE CONSEGNA NELLA PR #{m}: guardarla; se è questo lavoro, controllare il "
                        f"risultato e `chiudi --pr {n} --consegna {m}`")
        elif dopo:
            giudizio = f"HA FATTO PUSH: controllare il risultato, poi `chiudi --pr {n}`"
        elif ambiente_manca:
            giudizio = ("CANALE AUTOMATICO MUTO: al commento di avvio lo strumento chiede un ambiente "
                        "(difetto del canale delle PR). Si avvia a mano in Codex Cloud: `riavvia --pr %d` "
                        "ristampa il testo di avvio; se urge, il lavoro lo fa Claude da sola" % n)
        elif crediti_finiti:
            giudizio = "CREDITI FINITI: il lavoro lo fa Claude da sola e lo scrive in bacheca"
        elif t_rif and (adesso - t_rif) > dt.timedelta(hours=24):
            giudizio = ("PREPARATA DA OLTRE 24 ORE SENZA CONSEGNA: chiedere ad Alessandro se l'ha avviata "
                        "e, se il task è finito, se manca solo «Create PR» (`riavvia --pr %d` ristampa il "
                        "testo di avvio); se l'ha avviata e non arriva nulla, il lavoro lo fa Claude da sola "
                        "e lo scrive in bacheca" % n)
        elif risposte:
            giudizio = "in lavorazione (lo strumento ha risposto, nessun push ancora)"
        else:
            giudizio = ("in attesa dell'avvio a mano in Codex Cloud o, a lavoro finito, di «Create PR» "
                        "(`riavvia --pr %d` ristampa il testo di avvio)" % n)
        print(f"  => {giudizio}")


def _messaggio_pulito(body: str) -> str:
    """Messaggio di commit senza trailer né nomi di strumenti (stesse liste dei testi pubblici)."""
    righe = [r for r in body.splitlines() if not TRAILER_STRUMENTO.match(r)]
    testo = "\n".join(righe)
    testo = VIETATE.sub("strumento", testo)
    testo = VIETATE_SIGLE.sub("strumento", testo)
    testo = re.sub(r"\n{3,}", "\n\n", testo).strip()
    return testo or "Lavoro sul ramo"


def _allinea_alla_base(radice: Path, repo: str, ramo: str, base: str) -> bool:
    """Porta nel ramo le novità della base con un commit di merge (mai rebase su un ramo condiviso),
    così i controlli girano sullo stato che verrà davvero unito. Solo oggetti git, nessun checkout.
    Restituisce True se ha fatto push; si ferma se il merge ha conflitti."""
    fetch_rami(radice, base, ramo)
    sha_base = run(["git", "rev-parse", f"origin/{base}"], cwd=str(radice)).stdout.strip()
    sha_ramo = run(["git", "rev-parse", f"origin/{ramo}"], cwd=str(radice)).stdout.strip()
    if run(["git", "merge-base", "--is-ancestor", sha_base, sha_ramo], cwd=str(radice),
           check=False).returncode == 0:
        info(f"il ramo contiene già tutto {base}")
        return False
    r = run(["git", "merge-tree", "--write-tree", "--messages", sha_ramo, sha_base], cwd=str(radice),
            check=False)
    if r.returncode != 0:
        if r.returncode == 1:
            die(f"il ramo {ramo} è in conflitto con {base}: va risolto a mano su una sessione con "
                f"checkout (merge di {base} nel ramo, mai rebase), poi `chiudi` di nuovo.\n" + r.stdout[:1500])
        die(f"git merge-tree non disponibile o fallito ({r.returncode}): serve git ≥ 2.38.\n{r.stderr[:500]}")
    albero = r.stdout.split("\n", 1)[0].strip()
    nuovo = commit_tree(radice, albero, [sha_ramo, sha_base], f"Allineamento con {base}")
    run(["git", "push", "-q", f"--force-with-lease={ramo}:{sha_ramo}", "origin",
         f"{nuovo}:refs/heads/{ramo}"], cwd=str(radice))
    info(f"ramo {ramo} allineato a {base} con un commit di merge ({nuovo[:7]}): i controlli ripartono")
    return True


def _glob_github(pattern: str, percorso: str) -> bool:
    """Confronto alla maniera dei filtri `paths` di GitHub Actions: `**` attraversa le cartelle, `*` no."""
    rx = ""
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**", i):
            rx += ".*"
            i += 2
            continue
        rx += {"*": "[^/]*", "?": "[^/]"}.get(c, re.escape(c))
        i += 1
    return re.fullmatch(rx, percorso) is not None


def _filtri_push(testo_workflow: str) -> dict[str, list[str]]:
    """Le liste `paths` e `paths-ignore` del trigger `push` di un workflow (lettura minima, senza PyYAML)."""
    filtri: dict[str, list[str]] = {}
    m = re.search(r"^on:\s*\n((?:[ \t]+.*\n|\s*#.*\n|\n)*)", testo_workflow, re.MULTILINE)
    blocco = m.group(1) if m else ""
    m2 = re.search(r"^  push:\s*\n((?:    .*\n|\s*#.*\n|\n)*)", blocco, re.MULTILINE)
    push = m2.group(1) if m2 else ""
    for chiave in ("paths", "paths-ignore"):
        m3 = re.search(rf"^    {chiave}:\s*\n((?:\s*-\s*.*\n|\s*#.*\n)*)", push, re.MULTILINE)
        if m3:
            voci = re.findall(r"^\s*-\s*['\"]?([^'\"\n#]+?)['\"]?\s*$", m3.group(1), re.MULTILINE)
            filtri[chiave] = [v.strip() for v in voci if v.strip()]
    return filtri


def _deploy_atteso(radice: Path, repo: str, base: str, sha: str) -> tuple[bool, str]:
    """Il commit unito farà partire `deploy.yml`? Guarda il workflow e i file del commit sul ramo
    di base appena aggiornato (mai la cartella di lavoro di chi lancia lo script), e rispetta i
    filtri `paths` / `paths-ignore` del trigger `push` (le bacheche non ripubblicano i siti)."""
    wf = gh_api(f"repos/{repo}/actions/workflows/deploy.yml", tollerante=True)
    if not isinstance(wf, dict):
        return False, "il repository non ha il workflow deploy.yml"
    if wf.get("state") not in (None, "active"):
        return False, f"deploy.yml è in stato «{wf.get('state')}»"
    fetch_rami(radice, base)
    r = run(["git", "show", f"{sha}:.github/workflows/deploy.yml"], cwd=str(radice), check=False)
    if r.returncode != 0:
        return True, "deploy.yml non leggibile dal commit: aspetto comunque"
    filtri = _filtri_push(r.stdout)
    if not filtri:
        return True, "ogni push su " + base + " ripubblica"
    toccati = run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
                  cwd=str(radice)).stdout.split()
    if "paths" in filtri:
        passa = [f for f in toccati if any(_glob_github(p, f) for p in filtri["paths"])]
        if not passa:
            return False, "nessun file del commit rientra nei `paths` del deploy"
    if "paths-ignore" in filtri:
        passa = [f for f in toccati if not any(_glob_github(p, f) for p in filtri["paths-ignore"])]
        if not passa:
            return False, "il commit tocca solo file esclusi dal deploy (`paths-ignore`)"
    return True, "il commit tocca file che ripubblicano il sito"


def _aspetta_deploy(radice: Path, repo: str, base: str, sha: str, minuti: int) -> None:
    """Aspetta il run di `deploy.yml` per il commit di merge e ne riferisce l'esito.
    Nessun run entro cinque minuti, un run fallito o un deploy mai concluso fermano lo script,
    perché il sito non risulta ripubblicato; un run annullato dalla coda (vince l'ultimo) si
    segue nel suo sostituto fino alla conclusione."""
    atteso, motivo = _deploy_atteso(radice, repo, base, sha)
    if not atteso:
        info(f"nessun deploy da aspettare: {motivo}")
        return
    info(f"deploy atteso: {motivo}")
    url_wf = f"https://github.com/{repo}/actions/workflows/deploy.yml"
    scadenza = time.time() + minuti * 60
    inizio = time.time()
    run_id = None
    run_dati: dict = {}
    while time.time() < scadenza:
        if run_id is None:
            dati = gh_api(f"repos/{repo}/actions/workflows/deploy.yml/runs?head_sha={sha}&per_page=5",
                          tollerante=True)
            runs = dati.get("workflow_runs", []) if isinstance(dati, dict) else []
            if runs:
                run_dati = runs[0]
                run_id = run_dati["id"]
            elif time.time() - inizio > 300:
                die(f"nessun run del deploy per {sha[:7]} dopo 5 minuti: il sito NON risulta ripubblicato "
                    f"(workflow non partito o non osservabile). Controlla {url_wf} e rilancialo a mano.")
            else:
                info("in attesa che parta il deploy…")
                time.sleep(30)
                continue
        else:
            letto = gh_api(f"repos/{repo}/actions/runs/{run_id}", tollerante=True)
            if isinstance(letto, dict):
                run_dati = letto
            else:
                info("lettura del run fallita, riprovo")
                time.sleep(30)
                continue
        stato, esito = run_dati["status"], run_dati.get("conclusion")
        if stato == "completed":
            if esito == "success":
                info(f"deploy del merge concluso bene: {run_dati['html_url']}")
                return
            if esito == "cancelled":
                # In coda vince l'ultimo deploy: si segue il sostituto fino in fondo.
                dopo = gh_api(f"repos/{repo}/actions/workflows/deploy.yml/runs?per_page=5", tollerante=True)
                recenti = dopo.get("workflow_runs", []) if isinstance(dopo, dict) else []
                sost = next((r for r in recenti if r["id"] != run_id
                             and _quando(r["created_at"]) >= _quando(run_dati["created_at"])), None)
                if not sost:
                    die(f"deploy del merge annullato e nessun deploy successivo lo sostituisce: "
                        f"{run_dati['html_url']} — rilancia il deploy a mano")
                info(f"deploy {run_id} annullato dalla coda: seguo il sostituto {sost['html_url']}")
                run_id, run_dati = sost["id"], sost
                continue
            die(f"deploy del merge FALLITO ({esito}): {run_dati['html_url']} — il sito non è aggiornato, "
                "va guardato il log e rilanciato il deploy")
        info(f"deploy in corso ({stato}): {run_dati['html_url']}")
        time.sleep(30)
    die(f"il deploy non si è concluso entro {minuti} minuti: {run_dati.get('html_url') or url_wf}")


def _riscrivi_autori(radice: Path, repo: str, ramo: str, base: str) -> bool:
    """Riscrive a nome di Alessandro i commit del ramo con un altro autore o con righe di strumento.
    Usa solo oggetti git (commit-tree): nessun checkout. Restituisce True se ha fatto push."""
    fetch_rami(radice, base, ramo)
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
    """Toglie dalla PR il commento di avvio e i commenti dell'account dello strumento.
    I rapporti di `github-actions[bot]` (accessibilità, controlli) restano: sono del repository."""
    commenti = gh_api(f"repos/{repo}/issues/{n}/comments?per_page=100", paginato=True) or []
    tolti, rimasti = 0, []
    for c in commenti:
        mio_avvio = c["user"]["login"] == io_login and c["body"].strip().lower().startswith("@codex")
        if mio_avvio or _e_strumento(c["user"]):
            esito = gh_api(f"repos/{repo}/issues/comments/{c['id']}", "DELETE", ok_se=("404",), tollerante=True)
            if isinstance(esito, tuple):
                rimasti.append(c["html_url"])
            else:
                tolti += 1
    revisioni = gh_api(f"repos/{repo}/pulls/{n}/comments?per_page=100", paginato=True) or []
    for c in revisioni:
        if _e_strumento(c["user"]):
            esito = gh_api(f"repos/{repo}/pulls/comments/{c['id']}", "DELETE", ok_se=("404",), tollerante=True)
            if isinstance(esito, tuple):
                rimasti.append(c["html_url"])
            else:
                tolti += 1
    info(f"commenti tolti dalla PR: {tolti} (le revisioni del bot, se ci sono, non si possono cancellare)")
    if rimasti:
        # Nelle sessioni cloud il proxy di GitHub vieta le cancellazioni (HTTP 403). Sulle PR dei passaggi
        # (rami chatgpt/* e codex/*) le fa il workflow «Togli la firma dello strumento» appena la PR si
        # chiude, con il giro di ogni notte come rete; qui si dice quali sono.
        info("commenti non cancellati da qui (il canale di questa sessione non lo permette): sulle pull "
             "request dei passaggi li toglie il workflow «Togli la firma dello strumento» alla chiusura, "
             "altrove vanno tolti dalla pagina della PR:\n  " + "\n  ".join(rimasti))


def cmd_riavvia(args) -> None:
    """Ristampa il testo di avvio di una PR chatgpt/* già aperta (e, con --con-codex, rimanda il
    commento di avvio): niente ramo nuovo, niente voce nuova in bacheca. La richiesta si ricava
    dalla descrizione della PR, dove `nuovo` l'ha scritta sopra il piede."""
    radice = radice_repo()
    repo = owner_repo(radice)
    n = args.pr
    pr = gh_api(f"repos/{repo}/pulls/{n}")
    if pr["state"] != "open":
        die(f"la PR #{n} non è aperta ({pr['state']})")
    ramo = pr["head"]["ref"]
    if not ramo.startswith(PREFISSO_RAMO):
        die(f"la PR #{n} non è su un ramo chatgpt/* ({ramo})")
    m = re.search(r"-(\d{4})(\d{2})(\d{2})$", ramo)
    if m:
        data = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    else:
        data = _quando(pr["created_at"]).strftime("%Y-%m-%d")
    corpo = (pr.get("body") or "").replace("\r\n", "\n")
    if INIZIO_PIEDE_PR in corpo:
        brief = corpo.split(INIZIO_PIEDE_PR, 1)[0]
    else:
        info("descrizione senza il piede di `nuovo`: uso la descrizione intera come richiesta")
        brief = corpo
    if not brief.strip():
        die(f"la descrizione della PR #{n} è vuota: non c'è una richiesta da ristampare")
    if args.con_codex:
        gh_api(f"repos/{repo}/issues/{n}/comments", "POST", {"body": COMMENTO_AVVIO + COMMENTO_AVVIO_CODA})
        info(f"commento di avvio rimandato sulla PR #{n}: {pr['html_url']}")
    stampa_avvio(repo, ramo, n, testo_avvio(repo, ramo, pr["title"], data, n, brief))
    info("segui con `stato`")


def _assorbi_consegna(radice: Path, repo: str, n: int, ramo: str, m: int, io_login: str) -> None:
    """Porta nel ramo della PR preparata (#n) il lavoro consegnato con una pull request propria (#m:
    in Codex Cloud la apre «Create PR» dal task), poi la chiude come assorbita con un titolo neutro.
    Solo oggetti git, nessun checkout; i commit arrivati si riscrivono dopo, come tutti gli altri."""
    if m == n:
        die("--consegna: è la stessa pull request")
    prm = gh_api(f"repos/{repo}/pulls/{m}")
    if prm["state"] != "open":
        # Già assorbita da un `chiudi` precedente (per esempio con --senza-merge). Il segno è il titolo
        # neutro che quel `chiudi` le ha dato: i commit consegnati, riscritti a nome di Alessandro, hanno
        # cambiato SHA, quindi la testa originale della #m può non risultare più nel ramo.
        if (prm.get("title") or "") == f"Consegna per la pull request #{n}":
            info(f"la PR #{m} è già stata assorbita dalla #{n} con un `chiudi` precedente")
            return
        fetch_rami(radice, ramo)
        sha_ramo = run(["git", "rev-parse", f"origin/{ramo}"], cwd=str(radice)).stdout.strip()
        if run(["git", "merge-base", "--is-ancestor", prm["head"]["sha"], sha_ramo], cwd=str(radice),
               check=False).returncode == 0:
            info(f"la PR #{m} è chiusa e il suo lavoro è già nel ramo {ramo}")
            return
        die(f"la PR #{m} non è aperta ({prm['state']}) e il suo lavoro non è nel ramo {ramo}")
    repo_m = (prm["head"].get("repo") or {}).get("full_name") or repo
    if repo_m.lower() != repo.lower():
        die(f"la PR #{m} viene da un altro repository ({repo_m}): il suo ramo va portato qui a mano")
    ramo_m = prm["head"]["ref"]
    if ramo_m == ramo:
        die(f"la PR #{m} è sullo stesso ramo {ramo}: non c'è nulla da assorbire")
    fetch_rami(radice, ramo, ramo_m)
    sha_ramo = run(["git", "rev-parse", f"origin/{ramo}"], cwd=str(radice)).stdout.strip()
    sha_m = run(["git", "rev-parse", f"origin/{ramo_m}"], cwd=str(radice)).stdout.strip()
    if run(["git", "merge-base", "--is-ancestor", sha_m, sha_ramo], cwd=str(radice),
           check=False).returncode == 0:
        info(f"il lavoro della PR #{m} è già nel ramo {ramo}")
    else:
        if run(["git", "merge-base", "--is-ancestor", sha_ramo, sha_m], cwd=str(radice),
               check=False).returncode == 0:
            nuovo = sha_m
            info(f"il ramo {ramo_m} prosegue {ramo}: lo porto avanti senza commit di merge")
        else:
            r = run(["git", "merge-tree", "--write-tree", "--messages", sha_ramo, sha_m], cwd=str(radice),
                    check=False)
            if r.returncode != 0:
                if r.returncode == 1:
                    die(f"il ramo {ramo_m} della PR #{m} è in conflitto con {ramo}: va risolto a mano su "
                        f"una sessione con checkout (merge di {ramo_m} in {ramo}), poi `chiudi` di nuovo.\n"
                        + r.stdout[:1500])
                die(f"git merge-tree non disponibile o fallito ({r.returncode}): serve git ≥ 2.38.\n{r.stderr[:500]}")
            albero = r.stdout.split("\n", 1)[0].strip()
            nuovo = commit_tree(radice, albero, [sha_ramo, sha_m], f"Consegna dalla pull request #{m}")
        run(["git", "push", "-q", f"--force-with-lease={ramo}:{sha_ramo}", "origin",
             f"{nuovo}:refs/heads/{ramo}"], cwd=str(radice))
        info(f"lavoro della PR #{m} portato nel ramo {ramo} ({nuovo[:7]})")
    neutro = (f"Lavoro portato nel ramo della pull request #{n}, che viene unita da lì: "
              f"questa si chiude come assorbita.")
    gh_api(f"repos/{repo}/issues/{m}/comments", "POST", {"body": neutro})
    # Titolo neutro sempre. La descrizione si riscrive solo se la PR è dell'account di Alessandro:
    # la riga che il canale delle sessioni aggiunge ai testi la toglie il workflow di pulizia, che
    # lavora solo sui testi dell'account; su una PR di un altro autore resterebbe.
    modifica = {"title": f"Consegna per la pull request #{n}", "state": "closed"}
    if (prm.get("user") or {}).get("login") == io_login:
        modifica["body"] = neutro
    else:
        info(f"la PR #{m} è di {(prm.get('user') or {}).get('login')}: descrizione lasciata com'è "
             "(se nomina lo strumento, si toglie dalla pagina della PR)")
    gh_api(f"repos/{repo}/pulls/{m}", "PATCH", modifica)
    info(f"PR #{m} chiusa come assorbita dalla #{n}, con titolo neutro")


def _e_antenato(radice: Path, a: str, b: str) -> bool:
    return run(["git", "merge-base", "--is-ancestor", a, b], cwd=str(radice), check=False).returncode == 0


def _cartella_del_ramo(radice: Path, ref: str) -> str | None:
    """La cartella di lavoro, fra tutte quelle collegate al repository (`git worktree`), che ha in uso
    il ramo; None se nessuna."""
    percorso = None
    for riga in run(["git", "worktree", "list", "--porcelain"], cwd=str(radice)).stdout.splitlines():
        if riga.startswith("worktree "):
            percorso = riga[len("worktree "):]
        elif riga == f"branch {ref}":
            return percorso
    return None


def _ramo_locale_per_correggere(radice: Path, ramo: str) -> list[str]:
    """Dopo --senza-merge il ramo remoto è andato avanti (consegna, autori riscritti, allineamento), mentre
    la copia locale lasciata da `nuovo` punta ancora alla preparazione: chi corregge partendo da lì
    lavorerebbe su una storia vecchia. Se il ramo non è in uso in nessuna cartella di lavoro collegata,
    la porta su origin/<ramo> con update-ref (file intatti, mai commit locali persi); altrimenti non tocca
    nulla e restituisce i comandi esatti. Restituisce i passi da fare prima delle correzioni."""
    fetch_rami(radice, ramo)
    remoto = run(["git", "rev-parse", f"origin/{ramo}"], cwd=str(radice)).stdout.strip()
    ref = f"refs/heads/{ramo}"
    cartella = _cartella_del_ramo(radice, ref)
    in_uso = cartella is not None
    # In uso in un'altra cartella collegata: lì `git switch` fallirebbe, si lavora in quella cartella.
    vai = [f"cd {shlex.quote(cartella)}"] if in_uso and Path(cartella).resolve() != radice.resolve() else []
    # Nomi quotati per la shell: i comandi si copiano così come sono (percorsi con spazi, rami con `;` o `$`).
    q, qo = shlex.quote(ramo), shlex.quote(f"origin/{ramo}")
    dove = f" (in uso nella cartella {cartella})" if vai else ""
    locale = run(["git", "rev-parse", "--verify", "--quiet", ref], cwd=str(radice), check=False).stdout.strip()
    if locale == remoto:
        info(f"copia locale del ramo {ramo}{dove} già uguale al remoto")
        return vai if in_uso else [f"git switch {q}"]
    if in_uso:
        # Il ramo è quello di una cartella di lavoro: aggiornarlo vuol dire toccare i file, lo fa chi corregge.
        if _e_antenato(radice, locale, remoto):
            info(f"il ramo {ramo}{dove} è indietro rispetto al remoto: va portato avanti prima di correggere")
            return vai + [f"git merge --ff-only {qo}"]
        info(f"il ramo {ramo}{dove} ha commit che non sono sul remoto: va unito al remoto (merge, mai rebase)")
        return vai + [f"git merge {qo}"]
    if not locale:
        run(["git", "update-ref", ref, remoto, "0" * 40], cwd=str(radice))
        info(f"copia locale del ramo {ramo} creata su origin/{ramo} ({remoto[:7]})")
        return [f"git switch {q}"]
    if _e_antenato(radice, locale, remoto):
        run(["git", "update-ref", ref, remoto, locale], cwd=str(radice))
        info(f"copia locale del ramo {ramo} portata sul remoto ({locale[:7]} → {remoto[:7]})")
        return [f"git switch {q}"]
    info(f"la copia locale del ramo {ramo} ha commit che non sono sul remoto: non la tocco")
    return [f"git switch {q}", f"git merge {qo}"]


def _archivia_voce(radice: Path, ramo: str, n: int, base: str) -> bool:
    """Sposta in «Archiviati» la voce di bacheca della PR #n, con la riga di esito, con un commit sul
    ramo prima dei controlli: così la bacheca unita è già in ordine. Restituisce True se ha fatto push."""
    fetch_rami(radice, ramo)
    sha = run(["git", "rev-parse", f"origin/{ramo}"], cwd=str(radice)).stdout.strip()
    r = run(["git", "show", f"{sha}:{BACHECA}"], cwd=str(radice), check=False)
    if r.returncode != 0:
        info(f"{BACHECA} assente sul ramo: niente da archiviare")
        return False
    nuovo_testo = archivia_voce(r.stdout, n, base, f"{oggi():%d/%m/%Y}")
    if nuovo_testo is None:
        info(f"nessuna voce con «PR #{n}» in «Richieste» della bacheca: niente da archiviare")
        return False
    albero = albero_con_file(radice, sha, BACHECA, nuovo_testo)
    nuovo = commit_tree(radice, albero, [sha], f"Bacheca: archiviata la richiesta della pull request #{n}")
    run(["git", "push", "-q", f"--force-with-lease={ramo}:{sha}", "origin", f"{nuovo}:refs/heads/{ramo}"],
        cwd=str(radice))
    info(f"voce della PR #{n} spostata in «Archiviati» con l'esito ({nuovo[:7]})")
    return True


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

    if args.senza_merge and not pr["draft"]:
        # Una PR del passaggio resta in bozza finché `chiudi` non unisce; se qualcuno l'ha già segnata
        # pronta, le correzioni arrivano su una PR pronta (da qui non si può rimettere in bozza: serve
        # GraphQL). La revisione automatica parte all'apertura, al passaggio a pronta o su richiesta.
        info(f"attenzione: la PR #{n} è già pronta, non in bozza; i commit di questo `chiudi` e le "
             "correzioni arriveranno su una PR pronta")
    if args.consegna:
        _assorbi_consegna(radice, repo, n, ramo, args.consegna, io_login)
    _riscrivi_autori(radice, repo, ramo, base)
    _allinea_alla_base(radice, repo, ramo, base)
    if args.senza_merge:
        # Serve a correggere sul ramo il lavoro arrivato: niente archivio della voce, la PR resta com'è
        # (in bozza: niente revisione automatica, che consuma crediti) e i controlli si aspettano dopo.
        passi = _ramo_locale_per_correggere(radice, ramo)
        passi += ["correzioni e `git commit` (messaggi in italiano, senza nomi di strumenti)",
                  f"git push origin {shlex.quote(ramo)}",
                  f"python3 scripts/passa-a.py chiudi --pr {n}"
                  + (f" --consegna {args.consegna}" if args.consegna else "")]
        info("--senza-merge: consegna nel ramo, autori riscritti, ramo allineato; la PR resta com'è e la "
             "voce di bacheca in «Richieste». Per correggere sul ramo:\n  "
             + "\n  ".join(f"{i}. {p if p.startswith('correzioni') else f'`{p}`'}"
                           for i, p in enumerate(passi, 1)))
        return
    _archivia_voce(radice, ramo, n, base)

    if pr["draft"]:
        _segna_pronta(repo, n)
        info(f"PR #{n} segnata pronta")
    sha = _aspetta_controlli(repo, n, args.attesa_minuti)
    messaggio = args.messaggio or f"Richiesta della bacheca di coordinamento: {titolo}."
    controlla_vietate(messaggio, "il messaggio del merge")
    esito = gh_api(f"repos/{repo}/pulls/{n}/merge", "PUT", {
        "merge_method": "squash", "commit_title": f"{titolo} (#{n})", "commit_message": messaggio, "sha": sha,
    })
    if not (esito and esito.get("merged")):
        die(f"merge non riuscito: {esito}")
    sha_merge = esito.get("sha", "")
    info(f"PR #{n} unita con squash: {sha_merge[:7]} "
         "(autore: il profilo GitHub di Alessandro, cioè Alessandro Cuollo o IU0QVW)")
    esito = gh_api(f"repos/{repo}/git/refs/heads/{ramo}", "DELETE", ok_se=("422", "404"), tollerante=True)
    if isinstance(esito, tuple):
        if ramo.startswith(("chatgpt/", "codex/", "claude/")):
            info(f"ramo {ramo} non cancellato da qui (il canale di questa sessione non lo permette): "
                 "lo toglie il workflow «Togli la firma dello strumento» alla chiusura della PR")
        else:
            info(f"ramo {ramo} non cancellato (il canale di questa sessione non lo permette): "
                 "si toglie dalla pagina della PR o da una sessione sul PC; è già unito, resta innocuo")
    else:
        info(f"ramo {ramo} cancellato")
    if not args.senza_pulizia:
        _pulisci_commenti(repo, n, io_login)
        if args.consegna:
            _pulisci_commenti(repo, args.consegna, io_login)
    if args.senza_attesa_deploy:
        info(f"--senza-attesa-deploy: se il repository pubblica un sito, verifica a mano "
             f"https://github.com/{repo}/actions/workflows/deploy.yml")
    elif sha_merge:
        _aspetta_deploy(radice, repo, base, sha_merge, args.attesa_deploy_minuti)


# --- Main ----------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pm = sub.add_parser("modello", help="stampa lo schema della richiesta")
    pm.add_argument("--out", help="scrive lo schema in questo file invece che a schermo")
    pm.set_defaults(fn=cmd_modello)

    pn = sub.add_parser("nuovo", help="prepara un passaggio: ramo, bacheca, PR in bozza, testo di avvio")
    pn.add_argument("--argomento", required=True, help="slug del ramo chatgpt/<argomento>-AAAAMMGG")
    pn.add_argument("--titolo", required=True, help="titolo della PR e della voce in bacheca (senza nomi di strumenti)")
    pn.add_argument("--brief", required=True, help="file Markdown con le sette parti della richiesta")
    pn.add_argument("--base", help="ramo di partenza (predefinito: quello principale del repository)")
    pn.add_argument("--prova", action="store_true", help="solo in locale: niente push, PR, commento")
    pn.add_argument("--con-codex", action="store_true",
                    help="lascia anche il commento di avvio sulla PR (canale automatico, da riprovare senza spese)")
    pn.set_defaults(fn=cmd_nuovo)

    ps = sub.add_parser("stato", help="stato delle PR sui rami chatgpt/*")
    ps.add_argument("--tutte", action="store_true", help="tutte le PR aperte, non solo chatgpt/*")
    ps.set_defaults(fn=cmd_stato)

    pr_ = sub.add_parser("riavvia", help="ristampa il testo di avvio di una PR chatgpt/* già aperta")
    pr_.add_argument("--pr", type=int, required=True)
    pr_.add_argument("--con-codex", action="store_true", help="rimanda anche il commento di avvio sulla PR")
    pr_.set_defaults(fn=cmd_riavvia)

    pc = sub.add_parser("chiudi", help="riscrive gli autori, archivia la voce, segna pronta, aspetta i controlli, unisce")
    pc.add_argument("--pr", type=int, required=True)
    pc.add_argument("--consegna", type=int, metavar="M",
                    help="pull request di consegna aperta dallo strumento dal suo ramo: la porta nel ramo e la chiude")
    pc.add_argument("--titolo", help="titolo del commit di merge (predefinito: titolo della PR)")
    pc.add_argument("--messaggio", help="corpo del commit di merge (predefinito: riga sulla bacheca)")
    pc.add_argument("--attesa-minuti", type=int, default=40, help="attesa massima dei controlli della PR")
    pc.add_argument("--attesa-deploy-minuti", type=int, default=30, help="attesa massima del deploy dopo il merge")
    pc.add_argument("--senza-pulizia", action="store_true", help="non toglie i commenti dalla PR")
    pc.add_argument("--senza-merge", action="store_true",
                    help="porta dentro la consegna, riscrive gli autori e allinea il ramo, poi si ferma: "
                         "la PR resta in bozza e la voce di bacheca in «Richieste»; aggiorna la copia locale "
                         "del ramo e stampa i passi per correggere")
    pc.add_argument("--senza-attesa-deploy", action="store_true", help="dopo il merge non aspetta il deploy")
    pc.add_argument("--qualsiasi", action="store_true", help="accetta anche rami non chatgpt/*")
    pc.set_defaults(fn=cmd_chiudi)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
