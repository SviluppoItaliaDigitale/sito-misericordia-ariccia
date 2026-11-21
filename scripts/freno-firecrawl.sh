#!/usr/bin/env bash
# freno-firecrawl.sh — ferma ogni uso di Firecrawl finché non si sono provate le strade gratuite.
# Regola di Alessandro (21/10/2026 e 21/11/2026): prima ricerca e lettura web, poi il lettore locale «leggi-web»,
# Firecrawl solo per le pagine che gli altri non leggono (CLAUDE.md, § «Navigazione web»).
# Hook PreToolUse sugli strumenti mcp__Firecrawl__* e mcp__firecrawl__*. Lascia passare solo se nei 20 minuti prima è
# stato scritto il motivo: echo "URL: perché WebFetch e leggi-web non l'hanno letta" > "${TMPDIR:-/tmp}/firecrawl-motivo.txt"
F="${TMPDIR:-/tmp}/firecrawl-motivo.txt"
if [ -s "$F" ] && [ -n "$(find "$F" -mmin -20 2>/dev/null)" ]; then exit 0; fi
cat >&2 <<'MSG'
Firecrawl fermato: ha crediti contati. Ordine obbligatorio: 1) WebSearch e WebFetch; 2) lettore locale
`python3 .claude/skills/leggi-web/leggi.py URL` (gratis, senza limiti); 3) Firecrawl solo se i primi due non leggono la pagina.
Se li hai già provati, scrivi il motivo e riprova:
  echo "URL: che cosa hanno risposto WebFetch e leggi-web" > "${TMPDIR:-/tmp}/firecrawl-motivo.txt"
Nel resoconto scrivi che hai usato Firecrawl, perché e quanti crediti.
MSG
exit 2
