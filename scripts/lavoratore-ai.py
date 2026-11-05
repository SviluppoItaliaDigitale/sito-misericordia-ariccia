#!/usr/bin/env python3
"""AI automatiche su GitHub: prendono da sole le richieste della bacheca (COORDINAMENTO.md, «Richieste») indirizzate a
loro, lavorano su un ramo `auto/…` e consegnano una pull request in bozza, che chi controlla unisce (protocollo comune).
Destinatari: «ChatGPT automatico» (Codex con l'accesso ChatGPT di Alessandro), «Gemini automatico» (Gemini CLI, chiave
gratuita), «DeepSeek automatico», «GLM automatico», «Kimi automatico», «Qwen automatico» (Claude Code con i modelli
gratuiti di Ollama Cloud). Lo usa .github/workflows/lavoratore-ai.yml (trova, prendi, motore, consegna); da una sessione
`richiedi` scrive la richiesta in bacheca e la pubblica, così l'AI parte da sola; `elenco` mostra destinatari e chiavi.
"""

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.request

BACHECA = "COORDINAMENTO.md"
API = os.environ.get("LAVORATORE_API_URL", "https://api.github.com").rstrip("/")
GIT = os.environ.get("LAVORATORE_GIT_URL", "https://github.com").rstrip("/")
TEMP = pathlib.Path(os.environ.get("RUNNER_TEMP") or os.environ.get("TMPDIR") or "/tmp")
STATO = TEMP / "lavoratore-ai.json"
RIASSUNTO = TEMP / "riassunto-lavoro.md"
USCITA = TEMP / "uscita-motore.txt"
TEMPO_MOTORE = int(os.environ.get("TEMPO_MOTORE", str(45 * 60)))
ROMA = dt.timezone(dt.timedelta(hours=1))
try:
    from zoneinfo import ZoneInfo
    ROMA = ZoneInfo("Europe/Rome")
except Exception:   # pragma: no cover - zoneinfo c'è da Python 3.9
    pass

# Versioni fissate dei programmi (canale ufficiale npm, licenze Apache-2.0 per Codex e Gemini CLI): niente aggiornamenti
# automatici; per cambiarle si cambia qui e si registra in .claude/strumenti.md.
PROGRAMMI = {
    "codex": "@openai/codex@0.166.0",
    "gemini": "@google/gemini-cli@0.67.0",
    "claude": "@anthropic-ai/claude-code@2.1.318",
}

DESTINATARI = {
    "chatgpt automatico": {"nome": "ChatGPT automatico", "sigla": "chatgpt", "motore": "codex",
                           "segreto": "CHATGPT_ACCESSO"},
    "gemini automatico": {"nome": "Gemini automatico", "sigla": "gemini", "motore": "gemini",
                          "segreto": "GEMINI_API_KEY"},
    "deepseek automatico": {"nome": "DeepSeek automatico", "sigla": "deepseek", "motore": "ollama",
                            "segreto": "OLLAMA_API_KEY"},
    "glm automatico": {"nome": "GLM automatico", "sigla": "glm", "motore": "ollama", "segreto": "OLLAMA_API_KEY"},
    "kimi automatico": {"nome": "Kimi automatico", "sigla": "kimi", "motore": "ollama", "segreto": "OLLAMA_API_KEY"},
    "qwen automatico": {"nome": "Qwen automatico", "sigla": "qwen", "motore": "ollama", "segreto": "OLLAMA_API_KEY"},
}

TESTA = re.compile(r"^- \*\*(\d{4}-\d{2}-\d{2}) — da (.+?) a (.+?) — (.+?)\*\*(.*)$")
PRESA = re.compile(r"\b(?:pres[ao]|fatt[ao]|chius[ao]|archiviat[ao]) da\b", re.I)
# Nomi di strumenti: mai nei commit, nei titoli e nei testi delle PR (regola firma-dei-lavori.md).
VIETATE = re.compile(r"\b(claude|anthropic|chatgpt|chat gpt|openai|codex|gpt|gemini|google ai|deepseek|qwen|glm|kimi|"
                     r"moonshot|zhipu|ollama|llama|mistral|minimax|copilot|jules|llm|intelligenz[ae] artificial[ei]|"
                     r"artificial intelligence)\b", re.I)
VIETATE_SIGLE = re.compile(r"\b(IA|AI|LLM)\b")
SEGRETI = re.compile(r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|gh[ousr]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|"
                     r"sk-[A-Za-z0-9_-]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
                     r"\"refresh_token\"\s*:\s*\"[^\"]{10,}")
VIETATI = ("COORDINAMENTO.md", ".github")   # li cura il sistema, non l'AI che lavora


# ---------------------------------------------------------------- utilità

def adesso():
    return dt.datetime.now(ROMA)


def esegui(cmd, **kw):
    kw.setdefault("check", True)
    kw.setdefault("text", True)
    kw.setdefault("capture_output", True)
    r = subprocess.run(cmd, **kw)
    return r


def git(*argomenti, check=True):
    return esegui(["git", *argomenti], check=check).stdout.strip()


def uscita(**valori):
    destinazione = os.environ.get("GITHUB_OUTPUT")
    for k, v in valori.items():
        riga = f"{k}={v}"
        if destinazione:
            with open(destinazione, "a", encoding="utf-8") as f:
                f.write(riga + "\n")
        else:
            print(riga)


def resoconto(testo):
    destinazione = os.environ.get("GITHUB_STEP_SUMMARY")
    if destinazione:
        with open(destinazione, "a", encoding="utf-8") as f:
            f.write(testo + "\n")
    print(testo)


def slug(testo):
    t = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:40].rstrip("-") or "lavoro"


def senza_nomi(testo, riserva):
    """Testo per commit e PR: se nomina uno strumento, al suo posto una frase neutra."""
    if VIETATE.search(testo) or VIETATE_SIGLE.search(testo):
        return riserva
    return testo


def gh(metodo, percorso, corpo=None, ok=()):
    url = percorso if percorso.startswith("http") else f"{API}/{percorso.lstrip('/')}"
    richiesta = urllib.request.Request(
        url, method=metodo, data=json.dumps(corpo).encode() if corpo is not None else None,
        headers={"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}",
                 "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28",
                 "Content-Type": "application/json", "User-Agent": "lavoratore-ai"})
    try:
        with urllib.request.urlopen(richiesta, timeout=60) as r:
            dati = r.read()
            return json.loads(dati) if dati else {}
    except urllib.error.HTTPError as e:
        if e.code in ok:
            return None
        raise RuntimeError(f"GitHub {metodo} {percorso}: {e.code} {e.read().decode(errors='replace')[:300]}")


def remoto(repo):
    if GIT.startswith("https://"):
        token = os.environ["GITHUB_TOKEN"]
        return GIT.replace("https://", f"https://x-access-token:{token}@", 1) + f"/{repo}.git"
    return f"{GIT}/{repo}.git"


def pubblica_ramo(repo, ramo):
    r = esegui(["git", "push", "-q", remoto(repo), f"HEAD:refs/heads/{ramo}"], check=False)
    if r.returncode != 0:   # il ramo è andato avanti nel frattempo: si riparte dalla sua punta e si riprova una volta
        esegui(["git", "fetch", "-q", remoto(repo), f"refs/heads/{ramo}"])
        esegui(["git", "rebase", "-q", "FETCH_HEAD"])
        esegui(["git", "push", "-q", remoto(repo), f"HEAD:refs/heads/{ramo}"])


# ---------------------------------------------------------------- bacheca

def voci_richieste(testo):
    righe = testo.split("\n")
    inizio = next((k for k, r in enumerate(righe) if r.strip().startswith("## Richieste")), None)
    if inizio is None:
        return []
    fine = next((k for k in range(inizio + 1, len(righe)) if righe[k].startswith("## ")), len(righe))
    voci, k = [], inizio + 1
    while k < fine:
        m = TESTA.match(righe[k])
        if not m:
            k += 1
            continue
        j = k + 1
        while j < fine and (righe[j].startswith((" ", "\t")) or not righe[j].strip()) and not TESTA.match(righe[j]):
            j += 1
        while j > k + 1 and not righe[j - 1].strip():
            j -= 1
        voci.append({"riga": k, "fine": j, "data": m[1], "da": m[2].strip(), "a": m[3].strip(),
                     "titolo": m[4].strip(), "testa": righe[k], "blocco": "\n".join(righe[k:j])})
        k = j
    return voci


def destinatario(testo):
    chiave = re.sub(r"\s+", " ", re.sub(r"[*_`«»\"]", "", testo)).strip().lower().replace("automatica", "automatico")
    return DESTINATARI.get(chiave)


def prefisso_ramo(dest, voce):
    return f"auto/{dest['sigla']}-{slug(voce['titolo'])}-"


def gia_al_lavoro(repo, prefisso):
    """Un ramo con quel nome c'è già (con o senza PR): qualcuno ci sta lavorando o un giro precedente si è fermato."""
    refs = gh("GET", f"repos/{repo}/git/matching-refs/heads/{prefisso}", ok=(404,)) or []
    return [r["ref"].removeprefix("refs/heads/") for r in refs]


def prossima_richiesta(repo, testo):
    for voce in voci_richieste(testo):
        dest = destinatario(voce["a"])
        if not dest or PRESA.search(voce["blocco"]):
            continue
        rami = gia_al_lavoro(repo, prefisso_ramo(dest, voce))
        if rami:
            print(f"::warning::La richiesta «{voce['titolo']}» ha già il ramo {rami[0]}: la lascio a chi lo segue.")
            continue
        return voce, dest
    return None, None


PARTI = ["obiettivo", "file", "che cosa fare", "vincoli", "controlli", "consegna", "che cosa non fare"]


def parti_mancanti(blocco):
    """Le sette parti della richiesta (come `passa-a.py modello`), in ordine e compilate: l'elenco dei problemi."""
    righe = blocco.splitlines()
    trovate = [(int(m[1]), m[2].strip().lower(), i) for i, r in enumerate(righe)
               if (m := re.match(r"^\s*#{1,3}\s*(\d)\.\s*(.+?)\s*$", r))]
    if [n for n, _, _ in trovate] != list(range(1, 8)):
        return ["servono le sette parti in ordine, da «## 1. Obiettivo» a «## 7. Che cosa non fare»"]
    problemi = []
    for k, ((n, titolo, i), parola) in enumerate(zip(trovate, PARTI)):
        fine = trovate[k + 1][2] if k + 1 < len(trovate) else len(righe)
        corpo = "\n".join(righe[i + 1:fine]).strip()
        if not titolo.startswith(parola):
            problemi.append(f"la parte {n} deve chiamarsi «{parola.capitalize()}»")
        elif not corpo or (corpo.startswith("<") and corpo.endswith(">")):
            problemi.append(f"la parte {n} («{parola}») è vuota o da compilare")
    return problemi


def chiave_presente(dest):
    """Nel workflow decide HA_<SEGRETO> («true»/«false»); fuori dal workflow, la variabile stessa."""
    segnale = os.environ.get(f"HA_{dest['segreto']}")
    return segnale.lower() == "true" if segnale is not None else bool(os.environ.get(dest["segreto"]))


# ---------------------------------------------------------------- comandi del workflow

def cmd_trova(a):
    repo = os.environ["GITHUB_REPOSITORY"]
    voce, dest = prossima_richiesta(repo, pathlib.Path(BACHECA).read_text(encoding="utf-8"))
    if not voce:
        uscita(trovata="false")
        resoconto("Nessuna richiesta aperta per le AI automatiche in bacheca.")
        return 0
    problemi = parti_mancanti(voce["blocco"])
    if problemi:   # istruzioni incomplete non partono: si corregge la richiesta in bacheca
        uscita(trovata="false")
        print(f"::error::La richiesta del {voce['data']} per {dest['nome']} («{voce['titolo']}») è incompleta: "
              f"{'; '.join(problemi)}. Va riscritta con le sette parti di `python3 scripts/passa-a.py modello`.")
        return 1
    if not chiave_presente(dest):
        uscita(trovata="false")
        print(f"::error::La richiesta del {voce['data']} è per {dest['nome']}, ma nei segreti del repository manca "
              f"{dest['segreto']}: si collega dal PC con scripts/collega-ai-automatiche.sh.")
        return 1
    uscita(trovata="true", motore=dest["motore"])
    resoconto(f"Richiesta del {voce['data']} per {dest['nome']}: «{voce['titolo']}».")
    return 0


def cmd_prendi(a):
    repo = os.environ["GITHUB_REPOSITORY"]
    base = os.environ.get("BASE") or git("rev-parse", "--abbrev-ref", "HEAD")
    testo = pathlib.Path(BACHECA).read_text(encoding="utf-8")
    voce, dest = prossima_richiesta(repo, testo)   # di nuovo: nel frattempo qualcuno può averla presa
    if not voce:
        print("Nessuna richiesta da prendere (presa da altri nel frattempo).")
        return 0
    data = adesso()
    ramo = f"{prefisso_ramo(dest, voce)}{data:%Y%m%d}"
    titolo = senza_nomi(voce["titolo"], f"Richiesta della bacheca del {data:%d/%m/%Y}")
    git("checkout", "-q", "-b", ramo)
    righe = testo.split("\n")
    righe[voce["riga"]] += f" — presa da {dest['nome']}, pull request in apertura"
    pathlib.Path(BACHECA).write_text("\n".join(righe), encoding="utf-8")
    git("add", BACHECA)
    git("commit", "-q", "-m", f"Bacheca: richiesta «{titolo}» presa in carico")
    pubblica_ramo(repo, ramo)
    numero, errore_pr = None, ""
    try:
        pr = gh("POST", f"repos/{repo}/pulls", {
            "title": titolo, "head": ramo, "base": base, "draft": True,
            "body": (f"Lavoro sulla richiesta del {voce['data']} della bacheca (COORDINAMENTO.md, sezione «Richieste»).\n\n"
                     "La voce della bacheca su questo ramo riporta la richiesta completa e, a lavoro finito, l'esito, i "
                     "controlli eseguiti e i dubbi. Resta in bozza finché non la controlla chi unisce, come vuole il "
                     "protocollo comune.")})
        numero = pr["number"]
    except RuntimeError as e:
        errore_pr = str(e)
        print(f"::error::Pull request non aperta: {errore_pr}")
    testo = pathlib.Path(BACHECA).read_text(encoding="utf-8")
    segno = f"PR #{numero}" if numero else f"ramo {ramo}, pull request da aprire (Actions non ha potuto aprirla)"
    testo = testo.replace(f"presa da {dest['nome']}, pull request in apertura", f"presa da {dest['nome']}, {segno}", 1)
    pathlib.Path(BACHECA).write_text(testo, encoding="utf-8")
    git("add", BACHECA)
    git("commit", "-q", "-m", f"Bacheca: PR #{numero}, lavoro in corso" if numero else "Bacheca: lavoro in corso")
    pubblica_ramo(repo, ramo)
    STATO.write_text(json.dumps({"voce": voce, "dest": dest, "ramo": ramo, "pr": numero, "base": base,
                                 "errore_pr": errore_pr, "sha_presa": git("rev-parse", "HEAD"),
                                 "titolo": titolo, "repo": repo}, ensure_ascii=False))
    uscita(preso="true")
    resoconto(f"Lavoro preso: ramo {ramo}" + (f", pull request #{numero} in bozza." if numero else "."))
    return 0


def componi_prompt(stato):
    """Le istruzioni per l'AI che lavora da sola: complete, in ordine, con i divieti che prevalgono su tutto."""
    voce, dest = stato["voce"], stato["dest"]
    return f"""Sei «{dest['nome']}», un'intelligenza artificiale della squadra di Alessandro Cuollo. Lavori da sola su GitHub, \
in una macchina temporanea, senza nessuno che guardi: nessuno può rispondere alle tue domande mentre lavori. Segui \
questa procedura alla lettera, un passo dopo l'altro.

CONTESTO
- Repository: {stato['repo']}. Sei già sul ramo di lavoro «{stato['ramo']}», nella cartella del repository.
- Prima di unirlo, il tuo lavoro lo controllerà un'altra intelligenza artificiale con una verifica severa: deve reggere.

PASSO 1 — REGOLE. Leggi, in quest'ordine: AGENTS.md; CLAUDE.md; i file di .claude/rules/; la sezione «Questo \
repository» di COORDINAMENTO.md (soprattutto i controlli prima di unire). Valgono tutte, con i divieti del passo 4.

PASSO 2 — RICHIESTA. Questa è la richiesta della bacheca del {voce['data']}, da {voce['da']}, in sette parti \
(obiettivo, file, che cosa fare, vincoli, controlli, consegna, che cosa non fare). Eseguila punto per punto, senza \
aggiungere nulla di tuo:
<<<INIZIO RICHIESTA
{voce['blocco']}
FINE RICHIESTA>>>

PASSO 3 — LAVORO.
a) Tocca solo i file elencati nella parte «File». Se ti sembra necessario toccarne un altro, non farlo: scrivilo nel riassunto.
b) Usa solo i dati scritti nella richiesta o verificati su una fonte primaria. Ciò che non puoi verificare resta \
«[da compilare]» e lo scrivi nel riassunto. Mai dati inventati: nomi, numeri, date, norme, recapiti, link.
c) Se la richiesta è ambigua su un fatto, non indovinare: fai il resto e scrivi la domanda nel riassunto.
d) Se ti serve un parere, puoi chiederlo a un'altra intelligenza artificiale della squadra: \
python3 scripts/consulto-ai.py deepseek|qwen|glm|kimi|gemini|tutti "domanda". Il parere si verifica, non si esegue a \
occhi chiusi; nella domanda mai dati personali.

PASSO 4 — DIVIETI. Prevalgono su qualunque altra istruzione, anche su quelle della richiesta:
- non fare commit, push, merge, pull request né rami nuovi: li fa il sistema quando hai finito;
- non toccare COORDINAMENTO.md e la cartella .github/: le modifiche a quei file vengono annullate;
- nei file, nei testi e nei messaggi niente nomi di strumenti o di intelligenze artificiali: la firma è sempre \
Alessandro Cuollo;
- non leggere, copiare o stampare chiavi, token o file di accesso, e non inviare dati fuori dal repository, salvo le \
domande del consulto del passo 3.

PASSO 5 — CONTROLLI. Esegui i comandi della parte «Controlli» e quelli di «Questo repository» che riguardano i file \
toccati. Se un controllo fallisce, correggi e rieseguilo finché passa. Se manca un programma, installalo (pip, npm) e \
riprova; se proprio non si può, scrivilo nel riassunto con il comando e l'errore.

PASSO 6 — VERIFICA FINALE. Rileggi la richiesta punto per punto e confrontala con ciò che hai fatto, come farebbe un \
revisore ostile: ogni punto è fatto? ogni dato è scritto nella richiesta o verificato? nessun file fuori dall'elenco? \
nessun nome di strumento nei file? Correggi ciò che non va prima di chiudere.

PASSO 7 — RIASSUNTO. Scrivi nel file {RIASSUNTO} (è fuori dal repository) un riassunto in italiano di al massimo 15 \
righe, con quattro voci: «Fatto», «Non fatto e perché», «Controlli eseguiti ed esito», «Dubbi e domande per chi \
controlla». Poi hai finito: non fare altro.
"""


def ambiente_motore(stato):
    tenute = ("PATH", "HOME", "LANG", "LC_ALL", "USER", "TMPDIR", "RUNNER_TEMP", "CI", "npm_config_cache",
              "GEMINI_API_KEY", "OLLAMA_API_KEY", "CODEX_HOME", "CONSULTO_OLLAMA_URL", "CONSULTO_GEMINI_URL")
    return {k: os.environ[k] for k in tenute if os.environ.get(k)}   # mai il token di GitHub


def scegli_modello(stato):
    """Il modello più nuovo che il servizio elenca, con le stesse regole del consulto."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("consulto_ai", pathlib.Path(__file__).with_name("consulto-ai.py"))
    consulto = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(consulto)
    dest = stato["dest"]
    if dest["motore"] == "gemini":
        return consulto.Gemini().candidati()[0]
    if dest["motore"] == "ollama":
        return consulto.Ollama().candidati(dest["sigla"])[0]
    return ""   # Codex: il modello predefinito del piano ChatGPT


def comando_motore(stato, prompt, modello, env):
    motore = stato["dest"]["motore"]
    if os.environ.get("LAVORATORE_PROVA_MOTORE"):   # solo per scripts/prova-lavoratore-ai.py
        return shlex.split(os.environ["LAVORATORE_PROVA_MOTORE"]) + [prompt]
    if motore == "codex":
        return ["npx", "--yes", PROGRAMMI["codex"], "exec", "--dangerously-bypass-approvals-and-sandbox",
                "--ephemeral", "-c", "project_doc_max_bytes=131072", "-o", str(TEMP / "ultimo-messaggio.txt"), prompt]
    if motore == "gemini":
        impostazioni = pathlib.Path(env["HOME"]) / ".gemini" / "settings.json"
        impostazioni.parent.mkdir(parents=True, exist_ok=True)
        impostazioni.write_text(json.dumps({
            "general": {"enableAutoUpdate": False},
            "security": {"auth": {"selectedType": "gemini-api-key"}},
            "context": {"fileName": ["AGENTS.md", "GEMINI.md"]},
            "privacy": {"usageStatisticsEnabled": False},
        }))
        return ["npx", "--yes", PROGRAMMI["gemini"], "-p", prompt, "--approval-mode", "yolo", "--skip-trust",
                "-m", modello, "-o", "text"]
    # Claude Code come banco di lavoro, con un modello gratuito di Ollama Cloud al posto di Claude.
    env.update({"ANTHROPIC_BASE_URL": os.environ.get("CONSULTO_OLLAMA_URL", "https://ollama.com"),
                "ANTHROPIC_AUTH_TOKEN": env.get("OLLAMA_API_KEY", ""), "ANTHROPIC_API_KEY": "",
                "ANTHROPIC_MODEL": modello, "ANTHROPIC_DEFAULT_OPUS_MODEL": modello,
                "ANTHROPIC_DEFAULT_SONNET_MODEL": modello, "ANTHROPIC_DEFAULT_HAIKU_MODEL": modello,
                "ANTHROPIC_DEFAULT_FABLE_MODEL": modello, "CLAUDE_CODE_SUBAGENT_MODEL": modello,
                "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_AUTOUPDATER": "1", "DISABLE_TELEMETRY": "1"})
    return ["npx", "--yes", PROGRAMMI["claude"], "-p", prompt, "--dangerously-skip-permissions", "--model", modello,
            "--max-turns", "80", "--output-format", "text"]


def cmd_motore(a):
    if not STATO.exists():
        print("Nessun lavoro preso: niente da fare.")
        return 0
    stato = json.loads(STATO.read_text())
    env = ambiente_motore(stato)
    try:
        modello = "" if os.environ.get("LAVORATORE_PROVA_MOTORE") else scegli_modello(stato)
    except Exception as e:   # chiave rifiutata, quota finita, nessun modello: lo dice la bacheca
        stato.update(esito_motore=3, modello="", errore_motore=f"nessun modello disponibile: {e}")
        STATO.write_text(json.dumps(stato, ensure_ascii=False))
        print(f"::error::{stato['errore_motore']}")
        return 0
    prompt = componi_prompt(stato)
    cmd = comando_motore(stato, prompt, modello, env)
    print(f"Motore: {stato['dest']['motore']}" + (f", modello {modello}" if modello else ""), flush=True)
    inizio = time.time()
    scaduto = threading.Event()
    with open(USCITA, "w", encoding="utf-8") as registro:
        try:
            p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 stdin=subprocess.DEVNULL)
            sveglia = threading.Timer(TEMPO_MOTORE, lambda: (scaduto.set(), p.kill()))
            sveglia.start()
            for riga in p.stdout:
                sys.stdout.write(riga)
                registro.write(riga)
            codice = p.wait()
            sveglia.cancel()
            if scaduto.is_set():
                codice = 124
        except OSError as e:
            codice = 127
            registro.write(f"programma non avviato: {e}\n")
    stato.update(esito_motore=codice, modello=modello, durata=int(time.time() - inizio))
    STATO.write_text(json.dumps(stato, ensure_ascii=False))
    print(f"Motore finito con codice {codice} in {stato['durata']} s.")
    return 0


def leggi_riassunto():
    for f in (RIASSUNTO, TEMP / "ultimo-messaggio.txt"):
        if f.exists() and f.read_text(errors="replace").strip():
            testo = f.read_text(errors="replace")
            break
    else:
        testo = "\n".join(USCITA.read_text(errors="replace").splitlines()[-25:]) if USCITA.exists() else ""
    righe = [r.rstrip() for r in testo.strip().splitlines() if r.strip()][:25]
    return "\n".join(righe)[:3500]


def cmd_consegna(a):
    if not STATO.exists():
        print("Nessun lavoro preso: niente da consegnare.")
        return 0
    stato = json.loads(STATO.read_text())
    repo, ramo, numero, dest = stato["repo"], stato["ramo"], stato["pr"], stato["dest"]
    if git("rev-parse", "HEAD") != stato["sha_presa"]:   # l'AI ha fatto commit da sola: tornano modifiche da rivedere
        git("reset", "-q", "--soft", stato["sha_presa"])
    annullati = []
    for percorso in VIETATI:   # torna com'era alla presa in carico: file tolti, aggiunti o cambiati
        cambiati = git("status", "--porcelain", "--untracked-files=all", "--", percorso)
        if cambiati:
            annullati += [r[3:] for r in cambiati.splitlines()]
            git("reset", "-q", stato["sha_presa"], "--", percorso, check=False)
            if git("ls-tree", "-r", "--name-only", stato["sha_presa"], "--", percorso):
                git("checkout", stato["sha_presa"], "--", percorso)
            esegui(["git", "clean", "-fdq", "--", percorso], check=False)
    git("add", "-A")
    diff = git("diff", "--cached")
    codice = stato.get("esito_motore", 1)
    if diff and SEGRETI.search(diff):
        git("reset", "-q", "--hard", stato["sha_presa"])
        esegui(["git", "clean", "-fdq"], check=False)
        frase, toccati = "bloccato: nel lavoro c'era un testo che sembra una chiave d'accesso, non pubblicato", []
    else:
        toccati = [f for f in git("diff", "--cached", "--name-only").splitlines() if f]
        if toccati:
            git("commit", "-q", "-m", stato["titolo"], "-m", f"Lavoro dalla richiesta della bacheca del {stato['voce']['data']}.")
        if codice == 0 and toccati:
            frase = "lavoro consegnato in questa PR, da controllare e unire"
        elif codice == 0:
            frase = "nessun file modificato"
        else:
            motivo = stato.get("errore_motore") or ("tempo scaduto" if codice == 124 else f"codice di uscita {codice}")
            frase = f"lavoro non riuscito ({motivo})" + ("; i file toccati fin lì sono nella PR" if toccati else "")
    momento = adesso()
    modello = f", modello {stato['modello']}" if stato.get("modello") else ""
    righe_esito = [f"  - **Esito del {momento:%d/%m/%Y, %H:%M}** — {dest['nome']}{modello}: {frase}. "
                   f"File toccati: {', '.join(toccati) if toccati else 'nessuno'}."]
    if annullati:
        righe_esito.append(f"    Modifiche annullate perché quei file li cura il sistema: {', '.join(annullati)}.")
    righe_esito += [f"    {r}" for r in leggi_riassunto().splitlines()]
    testo = pathlib.Path(BACHECA).read_text(encoding="utf-8")
    voce = next((v for v in voci_richieste(testo) if v["titolo"] == stato["voce"]["titolo"]
                 and v["data"] == stato["voce"]["data"] and f"presa da {dest['nome']}" in v["testa"]), None)
    if voce:
        righe = testo.split("\n")
        righe[voce["fine"]:voce["fine"]] = righe_esito
        pathlib.Path(BACHECA).write_text("\n".join(righe), encoding="utf-8")
        git("add", BACHECA)
        git("commit", "-q", "-m", f"Bacheca: PR #{numero}, esito del lavoro" if numero else "Bacheca: esito del lavoro")
    pubblica_ramo(repo, ramo)
    if numero:
        gh("PATCH", f"repos/{repo}/pulls/{numero}", {"body": (
            f"Lavoro sulla richiesta del {stato['voce']['data']} della bacheca (COORDINAMENTO.md, sezione «Richieste»).\n\n"
            f"Esito: {frase}. File toccati: {len(toccati)}. La voce della bacheca su questo ramo riporta il riassunto, i "
            "controlli eseguiti e i dubbi. Resta in bozza finché non la controlla chi unisce.")})
    resoconto(f"Consegna: {frase}; file toccati {len(toccati)}" + (f"; pull request #{numero}." if numero else "."))
    return 1 if (not numero or codice != 0) else 0


# ---------------------------------------------------------------- da una sessione

def owner_repo():
    url = git("remote", "get-url", "origin")
    m = re.search(r"github\.com[:/]+([^/]+/[^/.]+?)(?:\.git)?/?$", url) or re.search(r"/git/([^/]+/[^/]+?)(?:\.git)?$", url)
    if not m:
        sys.exit(f"non riconosco il repository da {url}")
    return m[1]


def gh_cli(*argomenti, corpo=None):
    cmd = ["gh", "api", *argomenti]
    r = esegui(cmd + (["--input", "-"] if corpo is not None else []), input=json.dumps(corpo) if corpo else None,
               check=False)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:400])
    return json.loads(r.stdout) if r.stdout.strip() else {}


def cmd_richiedi(a):
    dest = destinatario(a.a)
    if not dest:
        sys.exit(f"Destinatario sconosciuto: {a.a}. Possibili: {', '.join(d['nome'] for d in DESTINATARI.values())}")
    brief = pathlib.Path(a.brief).read_text(encoding="utf-8").strip()
    problemi = parti_mancanti(brief)
    if problemi:
        sys.exit("Richiesta non pubblicata, perché un'AI che lavora da sola non può fare domande: "
                 + "; ".join(problemi) + ". Lo schema lo stampa `python3 scripts/passa-a.py modello`.")
    repo = owner_repo()
    data = adesso()
    titolo_commit = senza_nomi(a.titolo, f"richiesta del {data:%d/%m/%Y}")
    ramo = f"claude/richiesta-{slug(a.titolo)}-{data:%Y%m%d%H%M}"
    # Una cartella di lavoro a parte, dal ramo principale aggiornato: la copia in cui si sta lavorando non si tocca.
    git("fetch", "-q", "origin", "main")
    cartella = TEMP / f"richiesta-{data:%Y%m%d%H%M%S}"
    git("worktree", "add", "-q", "-b", ramo, str(cartella), "origin/main")
    try:
        os.chdir(cartella)
        return _pubblica_richiesta(a, dest, repo, data, titolo_commit, ramo, brief)
    finally:
        os.chdir(pathlib.Path(__file__).resolve().parent.parent)
        esegui(["git", "worktree", "remove", "--force", str(cartella)], check=False)


def _pubblica_richiesta(a, dest, repo, data, titolo_commit, ramo, brief):
    testo = pathlib.Path(BACHECA).read_text(encoding="utf-8")
    voce = [f"- **{data:%Y-%m-%d} — da {a.da} a {dest['nome']} — {a.titolo}**"] + [f"  {r}" if r.strip() else ""
                                                                                    for r in brief.splitlines()]
    righe = testo.split("\n")
    inizio = next((k for k, r in enumerate(righe) if r.strip().startswith("## Richieste")), None)
    if inizio is None:
        sys.exit("La bacheca non ha la sezione «## Richieste».")
    k = inizio + 1
    while k < len(righe) and not righe[k].strip():
        k += 1
    if k < len(righe) and righe[k].strip().lower().startswith("- nessuna richiesta"):
        righe[k:k + 1] = voce
    else:
        righe[k:k] = voce + [""]
    pathlib.Path(BACHECA).write_text("\n".join(righe), encoding="utf-8")
    git("add", BACHECA)
    git("commit", "-q", "-m", f"Bacheca: nuova richiesta «{titolo_commit}»")
    git("push", "-q", "origin", f"HEAD:refs/heads/{ramo}")
    titolo_pr = f"Bacheca: nuova richiesta «{titolo_commit}»"
    pr = gh_cli(f"repos/{repo}/pulls", "-X", "POST", corpo={
        "title": titolo_pr, "head": ramo, "base": "main",
        "body": "Aggiunge una richiesta alla bacheca (COORDINAMENTO.md, sezione «Richieste»): chi la riceve la prende da sé "
                "appena è sul ramo principale."})
    n = pr["number"]
    print(f"PR #{n} aperta: {pr.get('html_url', '')}")
    if a.senza_merge:
        return 0
    scadenza, inizio_attesa = time.time() + a.attesa * 60, time.time()
    while True:   # i controlli del repository, se ci sono, prima di unire
        sha = gh_cli(f"repos/{repo}/pulls/{n}")["head"]["sha"]
        runs = gh_cli(f"repos/{repo}/commits/{sha}/check-runs?per_page=100").get("check_runs", [])
        if runs and all(r["status"] == "completed" for r in runs):
            rossi = [r["name"] for r in runs if r["conclusion"] not in ("success", "skipped", "neutral")]
            if rossi:
                sys.exit(f"Controlli rossi sulla PR #{n}: {', '.join(rossi)}. Non unisco.")
            break
        if not runs and time.time() - inizio_attesa > 150:
            break
        if time.time() > scadenza:
            sys.exit(f"I controlli della PR #{n} non sono finiti in {a.attesa} minuti.")
        time.sleep(20)
    esito = gh_cli(f"repos/{repo}/pulls/{n}/merge", "-X", "PUT", corpo={
        "merge_method": "squash", "commit_title": f"{titolo_pr} (#{n})", "sha": sha,
        "commit_message": "Richiesta per la squadra nella bacheca di coordinamento."})
    if not esito.get("merged"):
        sys.exit(f"Merge non riuscito: {esito}")
    print(f"Richiesta pubblicata sul ramo principale: {dest['nome']} parte da solo (workflow «AI automatiche»); "
          "la consegna arriva come PR in bozza su un ramo auto/… e si chiude con "
          "`python3 scripts/passa-a.py chiudi --pr N --qualsiasi --titolo \"…\" --messaggio \"…\"`.")
    return 0


def cmd_elenco(a):
    for d in DESTINATARI.values():
        print(f"- {d['nome']}: motore {d['motore']}, segreto {d['segreto']}"
              + (" (presente qui)" if os.environ.get(d["segreto"]) else ""))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sotto = p.add_subparsers(dest="comando", required=True)
    for nome in ("trova", "prendi", "motore", "consegna", "elenco"):
        sotto.add_parser(nome)
    r = sotto.add_parser("richiedi", help="scrive in bacheca una richiesta per un'AI automatica e la pubblica")
    r.add_argument("--a", required=True, help="destinatario, per esempio «ChatGPT automatico»")
    r.add_argument("--titolo", required=True)
    r.add_argument("--brief", required=True, help="file con la richiesta completa (sette parti)")
    r.add_argument("--da", default="Claude")
    r.add_argument("--senza-merge", action="store_true")
    r.add_argument("--attesa", type=int, default=20, help="minuti di attesa dei controlli")
    a = p.parse_args(argv)
    return {"trova": cmd_trova, "prendi": cmd_prendi, "motore": cmd_motore, "consegna": cmd_consegna,
            "richiedi": cmd_richiedi, "elenco": cmd_elenco}[a.comando](a)


if __name__ == "__main__":
    sys.exit(main())
