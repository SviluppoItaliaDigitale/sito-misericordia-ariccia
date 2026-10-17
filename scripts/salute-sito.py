#!/usr/bin/env python3
"""Controlla le automazioni del repository: segnala ogni workflow il cui ultimo run su main è fallito
(o annullato per tempo scaduto) e i run falliti delle ultime 24 ore, nella issue «Salute del sito».

Istruzione di Alessandro del 17/10/2026: un guasto non deve mai restare ignorato; ogni problema
emerge come issue (label automazione + fonte-rotta) che la routine giornaliera legge e ripara.
La issue si aggiorna in silenzio a ogni giro, riceve un commento solo quando l'elenco dei workflow
in errore cambia (firma in un commento HTML nel corpo) e si chiude da sola quando tutto è verde.

Uso:  python3 scripts/salute-sito.py [--prova]   (richiede gh autenticato e GITHUB_REPOSITORY)
Exit: 0 sempre se il controllo è riuscito; 1 se ci sono automazioni in errore; 2 se gh non risponde.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

TITOLO = "Salute del sito: automazioni in errore"
QUESTO = ".github/workflows/salute-sito.yml"
ROMA = ZoneInfo("Europe/Rome")
FALLITI = {"failure", "timed_out", "startup_failure"}


def gh(*args, dati=None):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, input=dati)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def api(percorso):
    return json.loads(gh("api", "-H", "Accept: application/vnd.github+json", percorso))


def ora_it(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ROMA).strftime("%d/%m/%Y %H:%M")


def tempo_scaduto(repo, run):
    """Un run annullato conta come guasto solo se un job ha superato il suo timeout."""
    for job in api(f"repos/{repo}/actions/runs/{run['id']}/jobs?per_page=50")["jobs"]:
        if job.get("conclusion") != "cancelled":
            continue
        for nota in api(f"repos/{repo}/check-runs/{job['id']}/annotations"):
            if "maximum execution time" in (nota.get("message") or ""):
                return True
    return False


def guasto(repo, run):
    c = run.get("conclusion")
    return c in FALLITI or (c == "cancelled" and tempo_scaduto(repo, run))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prova", action="store_true", help="stampa il corpo senza toccare la issue")
    a = ap.parse_args()
    repo = os.environ.get("GITHUB_REPOSITORY") or gh("repo", "view", "--json", "nameWithOwner",
                                                     "--jq", ".nameWithOwner").strip()
    try:
        flussi = [w for w in api(f"repos/{repo}/actions/workflows?per_page=100")["workflows"]
                  if w["state"] == "active" and w["path"] != QUESTO
                  and w["path"].startswith(".github/workflows/")]
        adesso = datetime.now(timezone.utc)
        limite = (adesso - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
        in_errore, recenti = [], []
        for w in flussi:
            ultimi = api(f"repos/{repo}/actions/workflows/{w['id']}/runs?branch=main&per_page=1"
                         "&exclude_pull_requests=true")["workflow_runs"]
            ultimo = next((r for r in ultimi if r["status"] == "completed"), None)
            if ultimo is None:
                # ultimo in corso: si guarda il precedente completato
                altri = api(f"repos/{repo}/actions/workflows/{w['id']}/runs?branch=main&per_page=5"
                            "&status=completed")["workflow_runs"]
                ultimo = altri[0] if altri else None
            rotto = bool(ultimo and guasto(repo, ultimo))
            if rotto:
                in_errore.append((w["name"], ultimo))
            for r in api(f"repos/{repo}/actions/workflows/{w['id']}/runs?branch=main&per_page=50"
                         f"&created=%3E%3D{limite}&status=completed")["workflow_runs"]:
                if guasto(repo, r):
                    recenti.append((w["name"], r, not rotto))
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 2

    firma_base = "|".join(sorted({n for n, _ in in_errore} |
                                 {n for n, _, rientrato in recenti if not rientrato}))
    firma = hashlib.sha256(firma_base.encode()).hexdigest()[:16] if firma_base else "verde"
    problemi = firma != "verde"

    righe = [f"<!-- firma-salute: {firma} -->",
             "Controllo giornaliero delle automazioni (`salute-sito.yml`). La issue si aggiorna a "
             "ogni giro, riceve un commento solo quando l'elenco cambia e si chiude da sola quando "
             "tutte le automazioni sono verdi.", ""]
    if in_errore:
        righe += [f"## Automazioni il cui ultimo run su main non è riuscito ({len(in_errore)})", "",
                  "| Workflow | Esito | Quando (ora italiana) | Log |", "|---|---|---|---|"]
        for nome, r in sorted(in_errore):
            esito = r["conclusion"] if r["conclusion"] != "cancelled" else "tempo scaduto"
            righe.append(f"| {nome} | {esito} | {ora_it(r['created_at'])} | [run {r['run_number']}]({r['html_url']}) |")
        righe.append("")
    if recenti:
        righe += [f"## Run non riusciti nelle ultime 24 ore ({len(recenti)})", ""]
        for nome, r, rientrato in sorted(recenti, key=lambda t: t[1]["created_at"], reverse=True):
            nota = " — poi rientrato (l'ultimo run è riuscito)" if rientrato else ""
            righe.append(f"- {nome}: {r['conclusion']}, {ora_it(r['created_at'])}, "
                         f"[run {r['run_number']}]({r['html_url']}){nota}")
        righe.append("")
    if not problemi:
        righe += ["Tutte le automazioni sono verdi.", ""]
    righe += ["Come si ripara: si apre il log, si trova la causa (fonte esterna cambiata, credenziale "
              "scaduta, errore nel codice) e la si corregge con una pull request; se la causa non è "
              "chiara o la correzione cambia qualcosa di sostanziale, si chiede ad Alessandro.",
              "", f"Ultimo controllo: {adesso.astimezone(ROMA).strftime('%d/%m/%Y %H:%M')} ora italiana."]
    corpo = "\n".join(righe)
    print(corpo)
    if a.prova:
        return 1 if problemi else 0

    aperte = json.loads(gh("issue", "list", "--state", "open", "--label", "fonte-rotta",
                           "--search", f'in:title "{TITOLO}"', "--json", "number,title,body"))
    issue = next((i for i in aperte if i["title"] == TITOLO), None)
    if problemi:
        if issue is None:
            gh("issue", "create", "--title", TITOLO, "--label", "automazione",
               "--label", "fonte-rotta", "--body-file", "-", dati=corpo)
        else:
            vecchia = (issue["body"] or "").split("-->", 1)[0]
            gh("issue", "edit", str(issue["number"]), "--body-file", "-", dati=corpo)
            if firma not in vecchia:
                nomi = ", ".join(sorted(set(firma_base.split("|"))))
                gh("issue", "comment", str(issue["number"]), "--body-file", "-",
                   dati=f"L'elenco delle automazioni in errore è cambiato: {nomi}.")
        return 1
    if issue is not None:
        gh("issue", "edit", str(issue["number"]), "--body-file", "-", dati=corpo)
        gh("issue", "close", str(issue["number"]), "--comment",
           "Tutte le automazioni sono di nuovo verdi: chiusa da sola.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
