#!/usr/bin/env python3
"""Motore di «Claude automatico» (scripts/lavoratore-ai.py): fa lavorare Claude nella cartella del repository con il
pacchetto Python ufficiale dell'Agent SDK (claude-agent-sdk), pagato dai crediti API del piano Ultra.

Perché l'Agent SDK e non il programma `claude`: la pagina «API credits for Max, Ultra, and Team plans»
(platform.claude.com/docs/en/about-claude/api-credits-for-subscribers, letta l'11/11/2026) dice che i crediti coprono
«Claude API, Claude Managed Agents, the Claude Agent SDK» e non «Claude Code».
La chiave arriva in CLAUDE_CREDITI_API_KEY; lo script la toglie dal proprio ambiente e la passa come ANTHROPIC_API_KEY
solo al processo dell'agente. I comandi che l'agente avvia non la trovano nel loro ambiente (prova con un servizio
finto dell'11/11/2026), ma un comando potrebbe leggerla dal processo dell'agente, come le chiavi degli altri motori: la
proteggono il job senza permessi di scrittura e il controllo del pacchetto (nessun valore della chiave nei file, nel
riassunto o in bacheca). Le richieste dell'agente si dichiarano «cc_entrypoint=sdk-py», cioè Agent SDK. CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1 non si usa: provato l'11/11/2026 con la 0.2.180, chiede un
recinto (bubblewrap e socat) che lascia nella cartella del repository file vuoti segnaposto (.env, package.json,
.gitmodules, node_modules/…), che finirebbero nel lavoro consegnato.
Uscita: 0 lavoro finito; 1 errore; 3 chiave assente; 76 crediti del mese finiti (riga «credit balance is too low»).

Uso: motore-agentsdk.py --modello sonnet|opus|claude-… --cartella DIR --riassunto-dir DIR [--turni N] [--budget USD] PROMPT
"""

import argparse
import asyncio
import json
import os
import re
import sys
import urllib.request

CREDITI_FINITI = re.compile(r"credit balance is too low|Credit balance too low", re.I)
CODICE_CREDITI = 76
STRUMENTI = ["Read", "Write", "Edit", "MultiEdit", "NotebookEdit", "Glob", "Grep", "Bash", "TodoWrite", "WebFetch",
             "WebSearch"]
API_MODELLI = os.environ.get("AGENTSDK_API_URL", "https://api.anthropic.com").rstrip("/") + "/v1/models?limit=100"


def stampa(testo):
    print(testo, flush=True)


def ultimo_modello(famiglia, chiave):
    """L'ultima versione della famiglia (claude-<famiglia>-…, senza data in fondo) nell'elenco ufficiale dei modelli,
    come strumenti/crediti-api/crediti.py; leggere l'elenco non costa crediti. Se l'elenco non si legge, il nome breve
    della famiglia, che il programma dell'agente risolve da sé."""
    if famiglia.startswith("claude-"):
        return famiglia
    try:
        richiesta = urllib.request.Request(API_MODELLI, headers={
            "x-api-key": chiave, "anthropic-version": "2023-06-01", "User-Agent": "lavoratore-ai"})
        with urllib.request.urlopen(richiesta, timeout=30) as r:
            dati = json.loads(r.read()).get("data") or []
        candidati = [m for m in dati if str(m.get("id", "")).startswith(f"claude-{famiglia}-")
                     and not re.search(r"-\d{8}$", m["id"])]
        if candidati:
            return max(candidati, key=lambda m: m.get("created_at", ""))["id"]
    except Exception as e:   # rete o chiave: il motivo vero lo dirà l'agente
        stampa(f"Elenco dei modelli non letto ({type(e).__name__}): uso il nome «{famiglia}».")
    return famiglia


async def lavora(a, chiave, modello):
    from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ClaudeSDKError, ResultMessage, TextBlock,
                                  ToolUseBlock, query)
    opzioni = ClaudeAgentOptions(
        cwd=a.cartella,
        add_dirs=[a.riassunto_dir],   # il riassunto (passo 7) va fuori dal repository
        permission_mode="bypassPermissions",   # nessuno risponde alle domande: lavora da sola, in un job senza scrittura
        # Gli strumenti del lavoro, elencati: se un'impostazione riporta i permessi al modo predefinito (lo fa
        # CLAUDE_CODE_SUBPROCESS_ENV_SCRUB, prova dell'11/11/2026), restano approvati.
        allowed_tools=STRUMENTI,
        max_turns=a.turni,
        max_budget_usd=a.budget,
        model=modello,
        system_prompt={"type": "preset", "preset": "claude_code"},
        setting_sources=[],   # niente ganci né impostazioni del repository: le regole le legge dal passo 1
        stderr=lambda riga: stampa(riga.rstrip()),
        env={"ANTHROPIC_API_KEY": chiave, "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "DISABLE_AUTOUPDATER": "1",
             "DISABLE_TELEMETRY": "1"},
    )
    esito, ultimo = None, ""
    try:
        async for m in query(prompt=a.prompt, options=opzioni):
            if isinstance(m, AssistantMessage):
                if m.error:
                    stampa(f"Errore del servizio: {m.error}")
                for b in m.content:
                    if isinstance(b, TextBlock) and b.text.strip():
                        ultimo = b.text
                        stampa(b.text.strip())
                    elif isinstance(b, ToolUseBlock):
                        stampa(f"[strumento] {b.name}")
            elif isinstance(m, ResultMessage):
                esito = m
    except ClaudeSDKError as e:
        stampa(f"Agente fermato: {e}")
        return CODICE_CREDITI if CREDITI_FINITI.search(str(e)) else 1
    if esito is None:
        stampa("Agente finito senza risultato.")
        return 1
    testo = " ".join(str(x) for x in (esito.result, esito.errors, esito.api_error_status) if x)
    costo = f"{esito.total_cost_usd:.2f} $" if esito.total_cost_usd is not None else "non indicato"
    stampa(f"Risultato: {esito.subtype}, {esito.num_turns} turni, costo {costo}." + (f" {testo}" if esito.is_error else ""))
    if esito.result or ultimo:
        percorso = os.path.join(a.riassunto_dir, "ultimo-messaggio.txt")
        with open(percorso, "w", encoding="utf-8") as f:
            f.write(esito.result or ultimo)
    if esito.is_error:
        return CODICE_CREDITI if CREDITI_FINITI.search(testo) else 1
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--modello", default="sonnet")
    p.add_argument("--cartella", default=".")
    p.add_argument("--riassunto-dir", required=True)
    p.add_argument("--turni", type=int, default=80)
    p.add_argument("--budget", type=float, default=float(os.environ.get("CLAUDE_AUTOMATICO_BUDGET_USD", "10")))
    p.add_argument("prompt")
    a = p.parse_args(argv)
    chiave = os.environ.pop("CLAUDE_CREDITI_API_KEY", "").strip()
    os.environ.pop("ANTHROPIC_API_KEY", None)   # la chiave entra solo dall'opzione env dell'agente
    if not chiave:
        stampa("Manca CLAUDE_CREDITI_API_KEY: la mette nei segreti dal PC scripts/collega-ai-automatiche.sh.")
        return 3
    modello = ultimo_modello(a.modello, chiave)
    stampa(f"Agent SDK, modello {modello}, al massimo {a.turni} turni e {a.budget:.2f} $.")
    return asyncio.run(lavora(a, chiave, modello))


if __name__ == "__main__":
    sys.exit(main())
