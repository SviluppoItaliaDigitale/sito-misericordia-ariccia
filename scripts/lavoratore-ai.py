#!/usr/bin/env python3
"""AI automatiche su GitHub: prendono da sole le richieste della bacheca (COORDINAMENTO.md, «Richieste») indirizzate a
loro, lavorano su un ramo `auto/…` e consegnano una pull request in bozza, che chi controlla unisce (protocollo comune).
Destinatari: «ChatGPT automatico» (Codex con l'accesso ChatGPT di Alessandro), «Gemini automatico» (Gemini CLI, chiave
gratuita), «DeepSeek automatico», «GLM automatico», «Kimi automatico», «Qwen automatico» (Claude Code con i modelli
gratuiti di Ollama Cloud). Lo usa .github/workflows/lavoratore-ai.yml, in job separati: «prendi» (ramo, bacheca, PR),
«motore» e «raccogli» nel job dell'AI, che può solo leggere il repository e consegna il lavoro come pacchetto (patch,
riassunto, esito), «consegna» in un job che scrive e non si fida del pacchetto: lo ricontrolla, lo applica, fa commit,
esito in bacheca e PR. Da una sessione `richiedi` scrive la richiesta in bacheca e la pubblica, così l'AI parte da sola;
`elenco` mostra destinatari e chiavi.
Pensato per non fermarsi: se il servizio è occupato prova fino a tre modelli, in due giri, e il secondo giro rifà solo
i modelli occupati; se la quota gratuita di un modello è finita passa al successivo; se nessuno lavora toglie il ramo e
la richiesta riparte al giro dopo; se GitHub Actions non può aprire la PR il lavoro resta sul ramo e la PR la apre chi
controlla, da qualunque sessione (`passa-a.py chiudi --ramo`).
"""

import argparse
import base64
import datetime as dt
import json
import os
import pathlib
import re
import shlex
import signal
import subprocess
import sys
import textwrap
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

BACHECA = "COORDINAMENTO.md"
API = os.environ.get("LAVORATORE_API_URL", "https://api.github.com").rstrip("/")
GIT = os.environ.get("LAVORATORE_GIT_URL", "https://github.com").rstrip("/")
TEMP = pathlib.Path(os.environ.get("RUNNER_TEMP") or os.environ.get("TMPDIR") or "/tmp")
STATO = TEMP / "lavoratore-ai.json"
RIASSUNTO = TEMP / "riassunto-lavoro.md"
USCITA = TEMP / "uscita-motore.txt"
# Il pacchetto che il job dell'AI passa al job che consegna (artefatto del run): lavoro.patch, riassunto.txt, esito.json.
LAVORO = pathlib.Path(os.environ.get("LAVORO_DIR") or TEMP / "lavoro")
PATCH_MASSIMA = 50 * 1024 * 1024
TEMPO_MOTORE = int(os.environ.get("TEMPO_MOTORE", str(45 * 60)))   # tutti i tentativi insieme
TEMPO_MINIMO = int(os.environ.get("LAVORATORE_TEMPO_MINIMO", str(8 * 60)))   # sotto, non si prova un altro modello
PAUSA = int(os.environ.get("LAVORATORE_PAUSA", str(5 * 60)))   # fra i due giri, quando tutti i modelli sono occupati
VECCHIO = 3 * 3600   # un ramo senza esito fermo da più di 3 ore: il giro che lo aveva preso si è interrotto
# Il programma dell'AI riprova da sé quando il servizio è occupato (Gemini CLI fino a dieci volte, il 05/11/2026 per
# 514 secondi senza riuscire): dopo tre «occupato», se non ha ancora toccato nulla, si passa al modello successivo.
OCCUPATO = re.compile(r"\b(?:429|503|529)\b|UNAVAILABLE|RESOURCE_EXHAUSTED|high demand|overloaded|rate.?limit", re.I)
RIPROVA = re.compile(r"\battempt \d+\b|\bretrying\b|\bretry \d+\b", re.I)
SEGNALI_OCCUPATO = 3
# Quota gratuita finita (Gemini CLI: «TerminalQuotaError … exhausted your daily quota»; API di Google: «exceeded your
# current quota»; Codex e Ollama: «usage limit»): il programma si ferma da solo. Non serve un secondo giro, perché la
# quota non torna in cinque minuti (quelle di Gemini al giorno si azzerano a mezzanotte, ora del Pacifico: pagina
# «Rate limits» della Gemini API, letta il 05/11/2026); ogni modello ha la sua, quindi si prova il successivo.
QUOTA = re.compile(r"TerminalQuotaError|exhausted your (?:daily )?quota|exceeded your current quota|insufficient_quota"
                   r"|hit your usage limit|reached your (?:\w+ )?(?:usage )?limit", re.I)
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
ESITO = re.compile(r"^  - \*\*Esito del [^\n]*", re.M)   # la riga che scrive `consegna` (passa-a.py la legge uguale)
PRESA = re.compile(r"\b(?:pres[ao]|fatt[ao]|chius[ao]|archiviat[ao]) da\b", re.I)
# Nomi di strumenti: mai nei commit, nei titoli e nei testi delle PR (regola firma-dei-lavori.md).
VIETATE = re.compile(r"\b(claude|anthropic|chatgpt|chat gpt|openai|codex|gpt|gemini|google ai|deepseek|qwen|glm|kimi|"
                     r"moonshot|zhipu|ollama|llama|mistral|minimax|copilot|jules|llm|intelligenz[ae] artificial[ei]|"
                     r"artificial intelligence)\b", re.I)
VIETATE_SIGLE = re.compile(r"\b(IA|AI|LLM)\b")
# «sk-» solo a inizio parola e con almeno una cifra: «risk-communication-…» è il nome di un articolo, non una chiave.
SEGRETI = re.compile(r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|gh[ousr]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|"
                     r"(?<![A-Za-z0-9_-])sk-(?=[A-Za-z0-9_-]*[0-9])[A-Za-z0-9_-]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}|"
                     r"-----BEGIN [A-Z ]*PRIVATE KEY-----|"
                     r"\"(?:refresh|access|id)_token\"\s*:\s*\"[^\"]{10,}|AKIA[0-9A-Z]{16}|"
                     r"eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")   # l'ultima: i token JWT
# Li cura il sistema, non l'AI che lavora. .githooks: i ganci dei commit li eseguirebbe il job che scrive.
VIETATI = ("COORDINAMENTO.md", ".github", ".githooks")
# Perché un lavoro non si pubblica: il codice viaggia nell'esito, la frase la sceglie solo il job che consegna.
BLOCCHI = {
    "segreto": "nel lavoro c'era un testo che sembra una chiave d'accesso",
    "troppo-grande": "il lavoro era troppo grande per essere consegnato",
    "collegamento": "il lavoro conteneva un collegamento simbolico o un sottomodulo",
    "patch": "le modifiche non si applicavano al ramo così com'era alla presa in carico",
    "sconosciuto": "il job dell'AI ha segnalato un problema che il sistema non riconosce",
}
# Nei repository di un account personale GitHub Actions, di base, non può aprire pull request (documentazione GitHub,
# «Managing GitHub Actions settings for a repository»): la prima prova vera, il 05/11/2026, si è fermata così. Il lavoro
# non dipende da quel permesso: resta sul ramo e la PR la apre chi lo controlla.
PERMESSO_PR_NEGATO = re.compile(r"not permitted to create or approve pull requests", re.I)
# A Gemini non vanno dati personali o riservati (bacheca, § «AI automatiche e consulto fra AI»; skill gemini-api): sul
# piano gratuito, per la pagina dei prezzi della Gemini API, i testi servono a migliorare i prodotti di Google. In un
# repository privato un'AI che lavora da sola può leggerli: lì Gemini non lavora e non si consulta, e nel dubbio (GitHub
# non dice se il repository è privato) vale lo stesso. Fonti in memoria/ai-automatiche.md di assistente-personale.
NO_GEMINI_PRIVATO = "lì un'AI che lavora da sola può leggere dati personali e riservati, che a Gemini non vanno"
AI_PER_PRIVATI = "DeepSeek, GLM, Kimi o Qwen automatico"


def spiega_permesso(ramo):
    return (f"Il lavoro è sul ramo {ramo}: la pull request la apre chi lo controlla, da qualunque sessione, anche dal "
            f"cellulare, con «python3 scripts/passa-a.py chiudi --ramo {ramo} --titolo \"…\" --messaggio \"…\"». In questo "
            "repository GitHub Actions non può aprire pull request (impostazione di base dei repository personali): il "
            "permesso lo accende da solo l'avvio di una sessione di Claude sul PC (scripts/collega-ai-automatiche.sh di "
            "assistente-personale), oppure Settings → Actions → General → «Allow GitHub Actions to create and approve "
            "pull requests».")


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


def nomi_file(*argomenti):
    """I nomi dei file di un comando git con -z, separati da NUL: così come sono, senza le virgolette e le sequenze di
    escape che git mette ai nomi con lettere accentate o caratteri speciali, e senza togliere spazi."""
    return [n for n in esegui(["git", *argomenti], errors="surrogateescape").stdout.split("\0") if n]


def nome_leggibile(nome):
    """Un nome di file come va in bacheca: così com'è se usa lettere, cifre e segni comuni, altrimenti tra virgolette
    con le sequenze di escape, così il nome di un file non porta a capo, caratteri di controllo o formattazione."""
    if re.fullmatch(r"[\w./@+ -]{1,200}", nome):
        return nome
    return json.dumps(nome[:200]).translate({ord(c): f"\\u{ord(c):04x}" for c in "*`<>[]|~"})


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


def repository_privato(repo, via_cli=False):
    """True se il repository è privato, oppure se GitHub non lo dice: nel dubbio, privato."""
    try:
        dati = gh_cli(f"repos/{repo}") if via_cli else gh("GET", f"repos/{repo}")
    except Exception:   # rete, permessi, risposta illeggibile
        return True
    return not isinstance(dati, dict) or dati.get("private") is not False


def remoto(repo):
    if GIT.startswith("https://"):
        token = os.environ["GITHUB_TOKEN"]
        return GIT.replace("https://", f"https://x-access-token:{token}@", 1) + f"/{repo}.git"
    return f"{GIT}/{repo}.git"


def senza_ganci():
    """Nei comandi git di questo script e dei suoi figli, nessun programma del repository: né i ganci (core.hooksPath,
    anche quello del repository, .githooks) né il monitor dei file (core.fsmonitor). L'AI ha un ambiente suo
    (ambiente_motore) e non li riceve."""
    n = int(os.environ.get("GIT_CONFIG_COUNT") or 0)
    for chiave, valore in (("core.hooksPath", "/dev/null"), ("core.fsmonitor", "false")):
        os.environ[f"GIT_CONFIG_KEY_{n}"], os.environ[f"GIT_CONFIG_VALUE_{n}"] = chiave, valore
        n += 1
    os.environ["GIT_CONFIG_COUNT"] = str(n)


def valori_segreti():
    """I valori veri delle chiavi che il job conosce (almeno 12 caratteri): nessuno deve finire nei file, nel riassunto
    o in bacheca. Oltre alle variabili, i token dell'accesso ChatGPT, nel seme e nella copia in uso."""
    valori = {v for k in ("GITHUB_TOKEN", "GEMINI_API_KEY", "OLLAMA_API_KEY", "SEME")
              if len(v := os.environ.get(k, "")) >= 12}

    def dai_token(dati):
        if isinstance(dati, dict):
            for k, v in dati.items():
                if isinstance(v, str) and len(v) >= 12 and (k == "OPENAI_API_KEY" or k.endswith("token")):
                    valori.add(v)
                else:
                    dai_token(v)
    try:
        if os.environ.get("SEME"):
            dai_token(json.loads(base64.b64decode(os.environ["SEME"])))
    except Exception:   # seme illeggibile: restano le variabili
        pass
    try:
        if os.environ.get("CODEX_HOME"):
            dai_token(json.loads((pathlib.Path(os.environ["CODEX_HOME"]) / "auth.json").read_text()))
    except Exception:
        pass
    return valori


def contiene_segreto(testo, valori=()):
    return bool(testo) and (bool(SEGRETI.search(testo)) or any(v in testo for v in valori))


def righe_aggiunte(patch):
    """Del testo di una patch, solo le righe aggiunte: un segreto che il lavoro toglie non deve bloccarlo."""
    return "\n".join(r[1:] for r in patch.decode("utf-8", "replace").splitlines() if r.startswith("+"))


def segreto_nei_file(percorsi, valori, sha):
    """Il primo file che contiene un segreto nuovo, letto byte per byte (anche i file binari, che la patch codifica).
    Un testo che c'era già nel file alla presa in carico (`sha`) non blocca: l'AI non lo ha portato lei."""
    for p in percorsi:
        f = pathlib.Path(p)
        if f.is_file() and not f.is_symlink():
            dati = f.read_bytes()
            r = esegui(["git", "show", f"{sha}:{p}"], text=False, check=False)
            prima = set(SEGRETI.findall(r.stdout.decode("utf-8", "replace"))) if r.returncode == 0 else set()
            if set(SEGRETI.findall(dati.decode("utf-8", "replace"))) - prima or any(v.encode() in dati for v in valori):
                return p
    return None


def ripristina_vietati(sha):
    """I file che cura il sistema tornano come alla presa in carico (tolti, aggiunti o cambiati): l'elenco dei file."""
    annullati = []
    for percorso in VIETATI:
        cambiati = nomi_file("status", "--porcelain", "-z", "--untracked-files=all", "--no-renames", "--", percorso)
        if cambiati:
            annullati += [r[3:] for r in cambiati]
            git("reset", "-q", sha, "--", percorso, check=False)
            if git("ls-tree", "-r", "--name-only", sha, "--", percorso):
                git("checkout", sha, "--", percorso)
            esegui(["git", "clean", "-fdq", "--", percorso], check=False)
    return annullati


def carica_stato():
    """Lo stato del lavoro preso: dalla variabile LAVORATORE_STATO, che il workflow passa da un job all'altro e che i
    job con l'AI non possono cambiare; altrimenti dal file del giro (stesso job, prove in locale)."""
    testo = os.environ.get("LAVORATORE_STATO", "").strip()
    if testo:
        return json.loads(testo)
    return json.loads(STATO.read_text()) if STATO.exists() else None


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
    """I rami già aperti per la richiesta (con o senza PR), con l'ultimo commit: [(nome, sha)]."""
    refs = gh("GET", f"repos/{repo}/git/matching-refs/heads/{prefisso}", ok=(404,)) or []
    return [(r["ref"].removeprefix("refs/heads/"), (r.get("object") or {}).get("sha", "")) for r in refs]


def tentativo_fallito(repo, base, sha, voce):
    """Vero se il ramo è di un giro che non ha lavorato: nessun file oltre la bacheca e, nella voce, «lavoro non
    riuscito», oppure nessun esito e niente di nuovo da più di tre ore (quel giro si è interrotto). Un ramo così si toglie
    e la richiesta riparte da sola; ogni altro ramo (lavoro fatto, nessun file da cambiare, chiave bloccata) resta a chi
    controlla."""
    if not sha:
        return False
    try:
        confronto = gh("GET", f"repos/{repo}/compare/{base}...{sha}", ok=(404, 422))
        if not confronto or {f.get("filename") for f in confronto.get("files") or []} - {BACHECA}:
            return False
        contenuto = gh("GET", f"repos/{repo}/contents/{BACHECA}?ref={sha}", ok=(404,)) or {}
    except RuntimeError as e:   # nel dubbio il ramo resta: meglio una richiesta ferma che un lavoro cancellato
        print(f"::warning::Ramo della richiesta non controllato: {e}")
        return False
    testo = base64.b64decode(contenuto.get("content") or "").decode("utf-8", "replace")
    blocco = next((v["blocco"] for v in voci_richieste(testo) if v["data"] == voce["data"]
                   and v["titolo"] == voce["titolo"] and PRESA.search(v["testa"])), "")
    esiti = ESITO.findall(blocco)   # solo le righe d'esito del sistema: il riassunto dell'AI ha un altro rientro
    if esiti:
        return "lavoro non riuscito" in esiti[-1] and "File toccati: nessuno." in esiti[-1]
    commits = confronto.get("commits") or []
    quando = ((commits[-1].get("commit") or {}).get("committer") or {}).get("date", "") if commits else ""
    try:
        eta = time.time() - dt.datetime.fromisoformat(quando.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return False
    return eta > VECCHIO


def prossima_richiesta(repo, testo, base):
    """La prima richiesta per un'AI automatica non ancora presa: (voce, destinatario, rami di tentativi falliti da
    togliere)."""
    for voce in voci_richieste(testo):
        dest = destinatario(voce["a"])
        if not dest or PRESA.search(voce["blocco"]):
            continue
        rami = gia_al_lavoro(repo, prefisso_ramo(dest, voce))
        liberi = [nome for nome, sha in rami if tentativo_fallito(repo, base, sha, voce)]
        occupati = [nome for nome, _ in rami if nome not in liberi]
        if occupati:
            print(f"::warning::La richiesta «{voce['titolo']}» ha già il ramo {occupati[0]}: la lascio a chi lo segue.")
            continue
        for nome in liberi:
            print(f"Il ramo {nome} è di un tentativo che non ha lavorato: si toglie e la richiesta riparte.")
        return voce, dest, liberi
    return None, None, []


def libera_ramo(repo, ramo, numero=None, nota=""):
    """Chiude la PR del ramo, se c'è, e toglie il ramo: la richiesta, ancora aperta sul ramo principale, riparte da sola
    al giro dopo. Restituisce True se il ramo è stato tolto."""
    numeri = [numero] if numero else []
    if not numero:
        testa = urllib.parse.quote(f"{repo.split('/', 1)[0]}:{ramo}", safe=":/")
        numeri = [p["number"] for p in gh("GET", f"repos/{repo}/pulls?state=open&head={testa}", ok=(404,)) or []]
    for n in numeri:
        try:
            gh("PATCH", f"repos/{repo}/pulls/{n}", {"state": "closed", **({"body": nota} if nota else {})})
        except RuntimeError as e:
            print(f"::warning::PR #{n} non chiusa: {e}")
    r = esegui(["git", "push", "-q", remoto(repo), "--delete", f"refs/heads/{ramo}"], check=False)
    if r.returncode != 0:
        print(f"::warning::Ramo {ramo} non tolto ({r.stderr.strip()[:200]}): lo toglie il giro dopo.")
        return False
    return True


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

def problema_richiesta(repo, voce, dest):
    """Perché una richiesta non può partire (istruzioni incomplete, chiave assente, Gemini in un repository privato),
    oppure None. Lo controllano sia `trova` sia `prendi`, che rilegge la bacheca e può trovare un'altra richiesta."""
    problemi = parti_mancanti(voce["blocco"])
    if problemi:   # istruzioni incomplete non partono: si corregge la richiesta in bacheca
        return (f"La richiesta del {voce['data']} per {dest['nome']} («{voce['titolo']}») è incompleta: "
                f"{'; '.join(problemi)}. Va riscritta con le sette parti di `python3 scripts/passa-a.py modello`.")
    if not chiave_presente(dest):
        return (f"La richiesta del {voce['data']} è per {dest['nome']}, ma nei segreti del repository manca "
                f"{dest['segreto']}: si collega dal PC con scripts/collega-ai-automatiche.sh.")
    if dest["motore"] == "gemini" and repository_privato(repo):
        return (f"La richiesta del {voce['data']} («{voce['titolo']}») è per {dest['nome']}, ma {repo} è un "
                f"repository privato, o GitHub non dice se lo è: {NO_GEMINI_PRIVATO}. Va riscritta in bacheca per "
                f"{AI_PER_PRIVATI}.")
    return None


def cmd_trova(a):
    repo = os.environ["GITHUB_REPOSITORY"]
    voce, dest, _ = prossima_richiesta(repo, pathlib.Path(BACHECA).read_text(encoding="utf-8"),
                                       os.environ.get("BASE") or "main")
    if not voce:
        uscita(trovata="false")
        resoconto("Nessuna richiesta aperta per le AI automatiche in bacheca.")
        return 0
    problema = problema_richiesta(repo, voce, dest)
    if problema:
        uscita(trovata="false")
        print(f"::error::{problema}")
        return 1
    uscita(trovata="true", motore=dest["motore"])
    resoconto(f"Richiesta del {voce['data']} per {dest['nome']}: «{voce['titolo']}».")
    return 0


def cmd_prendi(a):
    repo = os.environ["GITHUB_REPOSITORY"]
    base = os.environ.get("BASE") or git("rev-parse", "--abbrev-ref", "HEAD")
    testo = pathlib.Path(BACHECA).read_text(encoding="utf-8")
    voce, dest, liberi = prossima_richiesta(repo, testo, base)   # di nuovo: nel frattempo qualcuno può averla presa
    if not voce:
        print("Nessuna richiesta da prendere (presa da altri nel frattempo).")
        return 0
    problema = problema_richiesta(repo, voce, dest)
    if problema:
        print(f"::error::{problema}")
        return 1
    for vecchio in liberi:   # prima di tutto: il ramo nuovo può avere lo stesso nome di quello vecchio
        if not libera_ramo(repo, vecchio):
            print(f"::error::Il ramo {vecchio} di un tentativo precedente non si toglie: la richiesta resta ferma.")
            return 1
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
    except RuntimeError as e:   # il lavoro parte lo stesso: la PR la apre poi chi controlla
        errore_pr = str(e)
        if PERMESSO_PR_NEGATO.search(errore_pr):
            print(f"::warning::{spiega_permesso(ramo)}")
        else:
            print(f"::warning::Pull request non aperta ({errore_pr}): la apre chi controlla, il lavoro parte lo stesso.")
    testo = pathlib.Path(BACHECA).read_text(encoding="utf-8")
    perche = ("in questo repository GitHub Actions non può aprirla" if PERMESSO_PR_NEGATO.search(errore_pr)
              else "GitHub Actions non ha potuto aprirla")
    segno = f"PR #{numero}" if numero else f"ramo {ramo}, pull request da aprire ({perche})"
    testo = testo.replace(f"presa da {dest['nome']}, pull request in apertura", f"presa da {dest['nome']}, {segno}", 1)
    pathlib.Path(BACHECA).write_text(testo, encoding="utf-8")
    git("add", BACHECA)
    git("commit", "-q", "-m", f"Bacheca: PR #{numero}, lavoro in corso" if numero else "Bacheca: lavoro in corso")
    pubblica_ramo(repo, ramo)
    stato = {"voce": voce, "dest": dest, "ramo": ramo, "pr": numero, "base": base, "errore_pr": errore_pr,
             "sha_presa": git("rev-parse", "HEAD"), "titolo": titolo, "repo": repo, "privato": repository_privato(repo)}
    STATO.write_text(json.dumps(stato, ensure_ascii=False))
    # Ai job dopo: lo stato in una riga (gli output dei job non li cambia chi viene dopo), il motore, ramo e commit.
    uscita(preso="true", motore=dest["motore"], ramo=ramo, sha=stato["sha_presa"],
           stato=json.dumps(stato, ensure_ascii=False, separators=(",", ":")))
    resoconto(f"Lavoro preso: ramo {ramo}" + (f", pull request #{numero} in bozza." if numero else "."))
    return 0


def testo_richiesta(blocco):
    """La voce com'è in bacheca, ma senza il rientro di due spazi dell'elenco: righe da copiare, comandi e blocchi di
    codice arrivano all'AI esattamente come vanno scritti (con il rientro, un'intestazione `<<'FINE'` non si chiude)."""
    testa, _, corpo = blocco.partition("\n")
    return testa + ("\n" + textwrap.dedent(corpo) if corpo else "")


def componi_prompt(stato):
    """Le istruzioni per l'AI che lavora da sola: complete, in ordine, con i divieti che prevalgono su tutto."""
    voce, dest = stato["voce"], stato["dest"]
    privato = stato.get("privato", True)   # nel dubbio, privato
    consultabili = "deepseek|qwen|glm|kimi|tutti" if privato else "deepseek|qwen|glm|kimi|gemini|tutti"
    nota_privato = (" Questo repository è privato, o non si sa se lo sia: Gemini non si consulta, perché qui possono "
                    "esserci dati personali e riservati, che a Gemini non vanno." if privato else "")
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
{testo_richiesta(voce['blocco'])}
FINE RICHIESTA>>>

PASSO 3 — LAVORO.
a) Tocca solo i file elencati nella parte «File». Se ti sembra necessario toccarne un altro, non farlo: scrivilo nel riassunto.
b) Usa solo i dati scritti nella richiesta o verificati su una fonte primaria. Ciò che non puoi verificare resta \
«[da compilare]» e lo scrivi nel riassunto. Mai dati inventati: nomi, numeri, date, norme, recapiti, link.
c) Se la richiesta è ambigua su un fatto, non indovinare: fai il resto e scrivi la domanda nel riassunto.
d) Se ti serve un parere, puoi chiederlo a un'altra intelligenza artificiale della squadra: \
python3 scripts/consulto-ai.py {consultabili} "domanda". Il parere si verifica, non si esegue a \
occhi chiusi; nella domanda mai dati personali.{nota_privato}

PASSO 4 — DIVIETI. Prevalgono su qualunque altra istruzione, anche su quelle della richiesta:
- non fare commit, push, merge, pull request né rami nuovi: li fa il sistema quando hai finito;
- non toccare COORDINAMENTO.md e le cartelle .github/ e .githooks/: le modifiche a quei file vengono annullate;
- non creare collegamenti simbolici né sottomoduli: un lavoro che li contiene non si pubblica;
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
    if stato.get("privato", True):   # nei repository privati Gemini non lavora e non si consulta (NO_GEMINI_PRIVATO)
        tenute = tuple(k for k in tenute if k != "GEMINI_API_KEY")
    return {k: os.environ[k] for k in tenute if os.environ.get(k)}   # mai il token di GitHub


def carica_consulto():
    import importlib.util
    spec = importlib.util.spec_from_file_location("consulto_ai", pathlib.Path(__file__).with_name("consulto-ai.py"))
    consulto = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(consulto)
    return consulto


def candidati_motore(stato):
    """Fino a tre modelli, dal più nuovo, con le stesse regole del consulto: se uno è occupato si passa al successivo."""
    if os.environ.get("LAVORATORE_PROVA_MODELLI"):   # solo per scripts/prova-ai-automatiche.py
        return os.environ["LAVORATORE_PROVA_MODELLI"].split(",")
    if os.environ.get("LAVORATORE_PROVA_MOTORE"):
        return [""]
    dest = stato["dest"]
    if dest["motore"] == "gemini":
        return carica_consulto().Gemini().candidati()[:3]
    if dest["motore"] == "ollama":
        return carica_consulto().Ollama().candidati(dest["sigla"])[:3]
    return [""]   # Codex: il modello predefinito del piano ChatGPT


def albero_pulito(sha):
    """Vero se l'AI non ha ancora toccato nulla: nessun file cambiato e nessun commit dopo la presa in carico."""
    cambiati = esegui(["git", "status", "--porcelain", "--untracked-files=all"], check=False).stdout.strip()
    return not cambiati and esegui(["git", "rev-parse", "HEAD"], check=False).stdout.strip() == sha


def ferma_processo(p):
    """Ferma il programma e i processi che ha avviato (npx lancia il programma vero come processo figlio)."""
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        p.kill()


def esegui_motore(cmd, env, tempo, registro, sha):
    """Un tentativo con un modello: (codice, occupato, quota). Se il servizio risponde «occupato» tre volte prima che
    l'AI abbia toccato un file, il tentativo si ferma subito (codice 75) invece di aspettare tutti i tentativi del
    programma. «quota» è vero se il programma ha scritto che la quota gratuita del modello è finita."""
    segnali, quota, fermato, scaduto = 0, False, threading.Event(), threading.Event()
    try:
        p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             stdin=subprocess.DEVNULL, start_new_session=True)
    except OSError as e:
        registro.write(f"programma non avviato: {e}\n")
        return 127, False, False
    sveglia = threading.Timer(max(tempo, 1), lambda: (scaduto.set(), ferma_processo(p)))
    sveglia.start()
    for riga in p.stdout:
        sys.stdout.write(riga)
        registro.write(riga)
        if QUOTA.search(riga):
            quota = True
        if RIPROVA.search(riga) and OCCUPATO.search(riga):
            segnali += 1
            if segnali >= SEGNALI_OCCUPATO and not fermato.is_set() and albero_pulito(sha):
                fermato.set()
                print(f"::warning::Servizio occupato ({segnali} tentativi del programma) e nessun file toccato: "
                      "fermo questo modello.", flush=True)
                ferma_processo(p)
    codice = p.wait()
    sveglia.cancel()
    if fermato.is_set():
        return 75, True, quota
    return (124 if scaduto.is_set() else codice), segnali > 0, quota


def motivo_fallimento(tentativi):
    modelli = list(dict.fromkeys(t["modello"] for t in tentativi if t["modello"]))
    provati = (f" (modelli provati: {', '.join(modelli)}" + (", in due giri" if len(tentativi) > len(modelli) else "")
               + ")") if modelli else ""
    ultimo = tentativi[-1]["codice"]
    if tentativi[-1].get("quota"):   # prima di «occupato»: il 05/11/2026 la quota è finita dopo due 503
        return "quota gratuita del modello finita" + provati
    if all(t["occupato"] or t.get("quota") for t in tentativi) and any(t.get("quota") for t in tentativi):
        return "servizio occupato e quota gratuita finita" + provati
    if all(t["occupato"] for t in tentativi):
        return "servizio occupato" + provati
    if ultimo == 124:
        return "tempo scaduto" + provati
    if ultimo == 127:
        return "programma non avviato" + provati
    return f"codice di uscita {ultimo}" + provati


def comando_motore(stato, prompt, modello, env):
    motore = stato["dest"]["motore"]
    if os.environ.get("LAVORATORE_PROVA_MOTORE"):   # solo per scripts/prova-lavoratore-ai.py
        return shlex.split(os.environ["LAVORATORE_PROVA_MOTORE"]) + [prompt]
    # Il riassunto (passo 7) va in TEMP, fuori dal repository: ogni programma deve poterci scrivere. Codex lavora senza
    # recinto; Gemini CLI e Claude Code scrivono solo nelle cartelle di lavoro, quindi TEMP si aggiunge a quelle. Il
    # 05/11/2026 Gemini CLI ha risposto «Path not in workspace» e il riassunto è arrivato solo dal registro.
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
                "--include-directories", str(RIASSUNTO.parent), "-m", modello, "-o", "text"]
    # Claude Code come banco di lavoro, con un modello gratuito di Ollama Cloud al posto di Claude.
    env.update({"ANTHROPIC_BASE_URL": os.environ.get("CONSULTO_OLLAMA_URL", "https://ollama.com"),
                "ANTHROPIC_AUTH_TOKEN": env.get("OLLAMA_API_KEY", ""), "ANTHROPIC_API_KEY": "",
                "ANTHROPIC_MODEL": modello, "ANTHROPIC_DEFAULT_OPUS_MODEL": modello,
                "ANTHROPIC_DEFAULT_SONNET_MODEL": modello, "ANTHROPIC_DEFAULT_HAIKU_MODEL": modello,
                "ANTHROPIC_DEFAULT_FABLE_MODEL": modello, "CLAUDE_CODE_SUBAGENT_MODEL": modello,
                "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_AUTOUPDATER": "1", "DISABLE_TELEMETRY": "1"})
    return ["npx", "--yes", PROGRAMMI["claude"], "-p", prompt, "--dangerously-skip-permissions", "--model", modello,
            "--add-dir", str(RIASSUNTO.parent), "--max-turns", "80", "--output-format", "text"]


def cmd_motore(a):
    stato = carica_stato()
    if not stato:
        print("Nessun lavoro preso: niente da fare.")
        return 0
    if git("rev-parse", "HEAD", check=False) == stato["sha_presa"] \
            and git("branch", "--show-current", check=False) != stato["ramo"]:
        git("checkout", "-q", "-B", stato["ramo"])   # nel job dell'AI il checkout è del commit: si lavora sul ramo
    if stato["dest"]["motore"] == "gemini" and stato.get("privato", True):   # rete di sicurezza dopo «trova»
        stato.update(esito_motore=3, modello="", errore_motore=f"{stato['repo']} è un repository privato, o GitHub "
                                                               f"non dice se lo è: {NO_GEMINI_PRIVATO}. La richiesta "
                                                               f"va riscritta in bacheca per {AI_PER_PRIVATI}")
        STATO.write_text(json.dumps(stato, ensure_ascii=False))
        print(f"::error::{stato['errore_motore']}")
        return 0
    try:
        modelli = candidati_motore(stato)
        if not modelli:
            raise RuntimeError("l'elenco dei modelli è vuoto")
    except Exception as e:   # chiave rifiutata, quota finita, nessun modello: lo dice la bacheca
        stato.update(esito_motore=3, modello="", errore_motore=f"nessun modello disponibile: {e}")
        STATO.write_text(json.dumps(stato, ensure_ascii=False))
        print(f"::error::{stato['errore_motore']}")
        return 0
    prompt = componi_prompt(stato)
    inizio, tentativi, coda, secondo_giro = time.time(), [], list(modelli), False
    with open(USCITA, "w", encoding="utf-8") as registro:
        while coda:
            restante = TEMPO_MOTORE - (time.time() - inizio)
            if tentativi and restante < TEMPO_MINIMO:
                print(f"Restano {int(restante)} secondi: niente altri tentativi.", flush=True)
                break
            modello = coda.pop(0)
            for f in (RIASSUNTO, TEMP / "ultimo-messaggio.txt"):   # il riassunto è sempre dell'ultimo tentativo
                f.unlink(missing_ok=True)
            env = ambiente_motore(stato)
            env["LAVORATORE_MODELLO"] = modello
            cmd = comando_motore(stato, prompt, modello, env)
            print(f"Motore: {stato['dest']['motore']}" + (f", modello {modello}" if modello else "")
                  + (f" (tentativo {len(tentativi) + 1})" if tentativi else ""), flush=True)
            partenza = time.time()
            codice, occupato, quota = esegui_motore(cmd, env, restante, registro, stato["sha_presa"])
            tentativi.append({"modello": modello, "codice": codice, "occupato": occupato, "quota": quota,
                              "durata": int(time.time() - partenza)})
            print(f"Tentativo finito con codice {codice} in {tentativi[-1]['durata']} s"
                  + (" (quota gratuita del modello finita)." if quota and codice else "."), flush=True)
            if codice == 0 or not albero_pulito(stato["sha_presa"]):
                break   # finito, oppure l'AI ha lavorato: un altro modello non riparte sopra un lavoro a metà
            # Il secondo giro rifà solo i modelli occupati: una quota finita non torna dopo la pausa.
            if not coda and not secondo_giro and TEMPO_MOTORE - (time.time() - inizio) >= PAUSA + TEMPO_MINIMO:
                occupati = [m for m in modelli if any(t["modello"] == m and t["occupato"] and not t["quota"]
                                                      for t in tentativi)]
                if occupati:
                    secondo_giro, coda = True, occupati
                    print(f"Modelli occupati ({', '.join(m for m in occupati if m) or 'predefinito'}): riprovo fra "
                          f"{PAUSA} secondi.", flush=True)
                    time.sleep(PAUSA)
    ultimo = tentativi[-1]
    stato.update(esito_motore=ultimo["codice"], modello=ultimo["modello"], tentativi=tentativi,
                 durata=int(time.time() - inizio))
    if ultimo["codice"] != 0:
        stato["errore_motore"] = motivo_fallimento(tentativi)
    STATO.write_text(json.dumps(stato, ensure_ascii=False))
    print(f"Motore finito con codice {ultimo['codice']} in {stato['durata']} s"
          + (f" ({stato['errore_motore']})." if ultimo["codice"] else "."))
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


def cmd_raccogli(a):
    """Nel job dell'AI, dopo il motore: il lavoro diventa un pacchetto per il job che consegna (patch, riassunto, esito),
    poi il ramo torna com'era. Qui non c'è nessun token che scrive; il job che consegna non si fida e ricontrolla."""
    stato = json.loads(STATO.read_text()) if STATO.exists() else carica_stato()
    if not stato:
        print("Nessun lavoro preso: niente da raccogliere.")
        return 0
    sha = stato["sha_presa"]
    LAVORO.mkdir(parents=True, exist_ok=True)
    for f in ("lavoro.patch", "riassunto.txt", "esito.json"):
        (LAVORO / f).unlink(missing_ok=True)
    if git("rev-parse", "HEAD", check=False) != sha:   # l'AI ha fatto commit da sola: tornano modifiche da rivedere
        git("reset", "-q", "--soft", sha)
    annullati = ripristina_vietati(sha)
    git("add", "-A")
    patch = esegui(["git", "diff", "--cached", "--binary", "--no-renames", "--no-ext-diff", "--no-textconv", sha],
                   text=False).stdout
    toccati = nomi_file("diff", "--cached", "--name-only", "--no-renames", "-z", sha)
    valori = valori_segreti()
    blocco = ""
    if len(patch) > PATCH_MASSIMA:
        blocco = "troppo-grande"
    elif contiene_segreto(righe_aggiunte(patch), valori) or contiene_segreto("\n".join(toccati), valori) \
            or segreto_nei_file(toccati, valori, sha):
        blocco = "segreto"
    riassunto = leggi_riassunto()
    riassunto_tolto = contiene_segreto(riassunto, valori)
    errore = stato.get("errore_motore", "")
    if contiene_segreto(errore, valori):
        errore = "errore del programma non riportato: conteneva un testo simile a una chiave d'accesso"
    if patch and not blocco:
        (LAVORO / "lavoro.patch").write_bytes(patch)
    (LAVORO / "riassunto.txt").write_text("" if riassunto_tolto else riassunto, encoding="utf-8")
    (LAVORO / "esito.json").write_text(json.dumps({
        "esito_motore": stato.get("esito_motore", 1), "modello": stato.get("modello", ""),
        "tentativi": stato.get("tentativi", []), "errore_motore": errore, "durata": stato.get("durata", 0),
        "annullati": annullati, "blocco": blocco, "riassunto_tolto": riassunto_tolto, "file": len(toccati)}))
    git("reset", "-q", "--hard", sha)
    esegui(["git", "clean", "-fdq"], check=False)
    print(f"Lavoro raccolto: {len(toccati)} file" + (f", bloccato ({BLOCCHI[blocco]})" if blocco else "")
          + (", riassunto tolto (conteneva una chiave)" if riassunto_tolto else "") + ".")
    return 0


def leggi_esito():
    """L'esito che arriva dal job dell'AI: dati da controllare, non istruzioni. Ciò che non torna si scarta; il motivo
    di un fallimento lo riscrive questo script dai tentativi."""
    try:
        dati = json.loads((LAVORO / "esito.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(dati, dict):
        return None

    def nome(x):
        return x if isinstance(x, str) and re.fullmatch(r"[A-Za-z0-9._:/@+-]{1,80}", x) else ""

    def intero(x, riserva=1):
        return x if isinstance(x, int) and not isinstance(x, bool) and -1000 < x < 1000 else riserva

    valori, sospetti = valori_segreti(), []   # anche i dati dell'esito finiscono in bacheca: niente chiavi neanche lì

    def senza_chiavi(x, campo):
        if x and contiene_segreto(x, valori):
            sospetti.append(campo)
            return ""
        return x

    tentativi = [{"modello": senza_chiavi(nome(t.get("modello")), "tentativi"), "codice": intero(t.get("codice")),
                  "occupato": t.get("occupato") is True, "quota": t.get("quota") is True}
                 for t in (dati.get("tentativi") if isinstance(dati.get("tentativi"), list) else [])[:12]
                 if isinstance(t, dict)]
    annullati = [p for p in (dati.get("annullati") if isinstance(dati.get("annullati"), list) else [])[:30]
                 if isinstance(p, str) and re.fullmatch(r"[\w./@+ -]{1,200}", p)
                 and any(p == v or p.startswith(v + "/") for v in VIETATI) and senza_chiavi(p, "annullati")]
    errore = dati.get("errore_motore") if isinstance(dati.get("errore_motore"), str) else ""
    errore = senza_chiavi(re.sub(r"[*`<>\[\]\r\n]+", " ", errore).strip()[:300], "errore")   # si toglie e basta
    modello = senza_chiavi(nome(dati.get("modello")), "modello")
    blocco = dati.get("blocco") or ""
    if not isinstance(blocco, str) or (blocco and blocco not in BLOCCHI):   # un blocco che non si riconosce, blocca
        blocco = "sconosciuto"
    if any(c != "errore" for c in sospetti):   # una chiave dove ci va il nome di un modello o di un file: non si pubblica
        blocco = "segreto"
    return {"esito_motore": intero(dati.get("esito_motore")), "modello": modello,
            "tentativi": tentativi, "annullati": annullati, "errore_motore": errore, "blocco": blocco,
            "riassunto_tolto": dati.get("riassunto_tolto") is True}


def riassunto_consegnato(valori):
    """Il riassunto del pacchetto, ricontrollato: al massimo 25 righe, niente chiavi, niente grassetto (così nessuna
    riga può sembrare un esito del sistema). (righe, tolto)."""
    f = LAVORO / "riassunto.txt"
    testo = f.read_text(encoding="utf-8", errors="replace") if f.is_file() and not f.is_symlink() else ""
    righe = [r.rstrip().replace("**", "") for r in testo.strip().splitlines() if r.strip()][:25]
    testo = "\n".join(righe)[:3500]
    if contiene_segreto(testo, valori):
        return [], True
    return testo.splitlines(), False


def applica_lavoro(sha, valori):
    """Applica la patch del pacchetto al ramo com'era alla presa in carico: (codice del blocco o "", file toccati,
    file che cura il sistema riportati com'erano)."""
    f = LAVORO / "lavoro.patch"
    if not f.is_file() or f.is_symlink():
        return "", [], []
    patch = f.read_bytes()
    if len(patch) > PATCH_MASSIMA:
        return "troppo-grande", [], []
    if contiene_segreto(righe_aggiunte(patch), valori):
        return "segreto", [], []
    r = esegui(["git", "apply", "--index", "--binary", "--whitespace=nowarn", "-"], input=patch, text=False,
               check=False)   # rifiuta da sé percorsi fuori dal repository, dentro .git e oltre un collegamento
    if r.returncode != 0:
        print(f"::warning::Patch non applicata: {r.stderr.decode(errors='replace').strip()[:300]}")
        return "patch", [], []
    annullati = ripristina_vietati(sha)
    if contiene_segreto("\n".join(annullati), valori):   # i nomi dei file vanno in bacheca, anche quelli binari
        return "segreto", [], []
    git("add", "-A")
    modi = git("diff", "--cached", "--raw", "--no-renames", sha)
    if any(r.split()[1] in ("120000", "160000") for r in modi.splitlines() if r.startswith(":")):
        return "collegamento", [], annullati
    toccati = nomi_file("diff", "--cached", "--name-only", "--no-renames", "-z", sha)
    if contiene_segreto("\n".join(toccati), valori) or segreto_nei_file(toccati, valori, sha):
        return "segreto", [], annullati
    return "", toccati, annullati


def cmd_consegna(a):
    stato = carica_stato()
    if not stato:
        print("Nessun lavoro preso: niente da consegnare.")
        return 0
    repo, ramo, numero, dest, sha = stato["repo"], stato["ramo"], stato["pr"], stato["dest"], stato["sha_presa"]
    git("reset", "-q", "--hard", sha)   # si riparte dal ramo com'era alla presa in carico: dal job dell'AI solo dati
    esegui(["git", "clean", "-fdq"], check=False)
    git("checkout", "-q", "-B", ramo)
    valori = valori_segreti()
    esito = leggi_esito()
    if esito is None:
        esito = {"esito_motore": 1, "modello": "", "tentativi": [], "annullati": [], "errore_motore": "",
                 "blocco": "", "riassunto_tolto": False}
        motivo = "il lavoro non è arrivato: giro interrotto, scaduto o fermato"
    else:
        motivo = (motivo_fallimento(esito["tentativi"]) if esito["tentativi"] else esito["errore_motore"]) \
            or f"codice di uscita {esito['esito_motore']}"
    codice = esito["esito_motore"]
    blocco, toccati, annullati = esito["blocco"], [], []
    if not blocco:
        blocco, toccati, annullati = applica_lavoro(sha, valori)
    annullati = sorted(set(esito["annullati"]) | set(annullati))
    if blocco:
        git("reset", "-q", "--hard", sha)
        esegui(["git", "clean", "-fdq"], check=False)
        frase, toccati = f"bloccato: {BLOCCHI[blocco]}, non pubblicato", []
    else:
        if toccati:
            git("commit", "-q", "-m", stato["titolo"], "-m", f"Lavoro dalla richiesta della bacheca del {stato['voce']['data']}.")
        dove = "in questa PR" if numero else f"sul ramo {ramo} (la pull request la apre chi controlla)"
        if codice == 0 and toccati:
            frase = f"lavoro consegnato {dove}, da controllare e unire"
        elif codice == 0:
            frase = "nessun file modificato"
        else:
            frase = f"lavoro non riuscito ({motivo})" + (f"; i file toccati fin lì sono {dove}" if toccati else "")
    # Nessun lavoro fatto: il ramo si toglie e la richiesta, ancora aperta sul ramo principale, riparte al giro dopo.
    da_rifare = codice != 0 and not toccati and not blocco
    momento = adesso()
    modello = f", modello {esito['modello']}" if esito["modello"] else ""
    righe_esito = [f"  - **Esito del {momento:%d/%m/%Y, %H:%M}** — {dest['nome']}{modello}: {frase}. "
                   f"File toccati: {', '.join(map(nome_leggibile, toccati)) if toccati else 'nessuno'}."]
    if annullati:
        righe_esito.append("    Modifiche annullate perché quei file li cura il sistema: "
                           f"{', '.join(map(nome_leggibile, annullati))}.")
    riassunto, tolto = riassunto_consegnato(valori)
    if tolto or esito["riassunto_tolto"]:
        righe_esito.append("    Riassunto non pubblicato: conteneva un testo simile a una chiave d'accesso.")
    righe_esito += [f"    {r}" for r in riassunto]
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
    if da_rifare:
        tolto = libera_ramo(repo, ramo, numero, (
            f"Tentativo sulla richiesta del {stato['voce']['data']} della bacheca non riuscito: nessun file toccato. "
            "Il ramo si toglie e la richiesta riparte da sola al giro successivo."))
        resoconto(f"Consegna: {frase}. Nessun file toccato: " + (
            "ramo tolto, la richiesta riparte da sola al giro dopo (bacheca aggiornata su main, giro del mattino o avvio "
            "a mano del workflow)." if tolto else "il ramo resta, lo toglie il giro dopo prima di riprovare."))
        print(f"::error::Lavoro non riuscito ({motivo}) senza file toccati: la richiesta riparte al giro dopo.")
        return 1
    if numero:   # testo pubblico: senza nomi di strumenti né di modelli
        gh("PATCH", f"repos/{repo}/pulls/{numero}", {"body": (
            f"Lavoro sulla richiesta del {stato['voce']['data']} della bacheca (COORDINAMENTO.md, sezione «Richieste»).\n\n"
            f"Esito: {senza_nomi(frase, 'scritto nella voce della bacheca su questo ramo')}. File toccati: {len(toccati)}. "
            "La voce della bacheca su questo ramo riporta il riassunto, i controlli eseguiti e i dubbi. Resta in bozza "
            "finché non la controlla chi unisce.")})
    resoconto(f"Consegna: {frase}; file toccati {len(toccati)}" + (f"; pull request #{numero}." if numero else "."))
    if not numero:   # la consegna c'è: il run resta verde e chi controlla apre la PR (passa-a.py stato la elenca)
        print(f"::warning::{spiega_permesso(ramo)}")
    if blocco:   # rosso, perché qualcuno guardi: il ramo resta e la richiesta non riparte da sola
        print(f"::error::Lavoro non pubblicato: {BLOCCHI[blocco]}. Il ramo {ramo} resta con l'esito in bacheca.")
        return 1
    return 0 if codice == 0 else 1


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
    if dest["motore"] == "gemini" and repository_privato(repo, via_cli=True):
        sys.exit(f"Richiesta non pubblicata: {repo} è un repository privato, o GitHub non dice se lo è: "
                 f"{NO_GEMINI_PRIVATO}. Scrivila per {AI_PER_PRIVATI}.")
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
          "la consegna arriva su un ramo auto/…, con una PR in bozza se il repository lo permette, e si chiude con "
          "`python3 scripts/passa-a.py chiudi --pr N --qualsiasi --titolo \"…\" --messaggio \"…\"` o, senza PR, "
          "`python3 scripts/passa-a.py chiudi --ramo auto/… --titolo \"…\" --messaggio \"…\"` (`passa-a.py stato` "
          "dice quale).")
    return 0


def cmd_elenco(a):
    for d in DESTINATARI.values():
        print(f"- {d['nome']}: motore {d['motore']}, segreto {d['segreto']}"
              + (" (presente qui)" if os.environ.get(d["segreto"]) else ""))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sotto = p.add_subparsers(dest="comando", required=True)
    for nome in ("trova", "prendi", "motore", "raccogli", "consegna", "elenco"):
        sotto.add_parser(nome)
    r = sotto.add_parser("richiedi", help="scrive in bacheca una richiesta per un'AI automatica e la pubblica")
    r.add_argument("--a", required=True, help="destinatario, per esempio «ChatGPT automatico»")
    r.add_argument("--titolo", required=True)
    r.add_argument("--brief", required=True, help="file con la richiesta completa (sette parti)")
    r.add_argument("--da", default="Claude")
    r.add_argument("--senza-merge", action="store_true")
    r.add_argument("--attesa", type=int, default=20, help="minuti di attesa dei controlli")
    a = p.parse_args(argv)
    senza_ganci()
    return {"trova": cmd_trova, "prendi": cmd_prendi, "motore": cmd_motore, "raccogli": cmd_raccogli,
            "consegna": cmd_consegna, "richiedi": cmd_richiedi, "elenco": cmd_elenco}[a.comando](a)


if __name__ == "__main__":
    sys.exit(main())
