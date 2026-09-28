# Regola sessioni cloud e nuovi repository

Vale in tutti i progetti, presenti e futuri. Obiettivo: Alessandro lavora da PC, da cellulare o da un'altra postazione, anche con il PC spento, trovando sempre tutto disponibile.

## Se sei in una sessione cloud (PC spento)
- Riconoscila così: non esistono `~/Scrivania`, gli altri progetti del PC e gli MCP locali (Firecrawl, Playwright).
- Per il web usa `WebSearch` e `WebFetch`. Gmail, Calendar, Drive e Canva funzionano (connettori di claude.ai).
- Regole, agenti, skill e memoria vengono dal repo: seguili come sul PC. I permessi li approva Alessandro dal cellulare.
- I risultati vanno nel repo, su Drive o inviati ad Alessandro: non esiste un desktop.
- A fine lavoro fai **commit e push**, così il lavoro arriva al PC e alle altre postazioni. Nei repo dei siti, dove il merge su `main` avvia il deploy, segui le regole di pubblicazione del repo.
- Se ti serve un altro repo, dillo: va aggiunto quando si crea la sessione.

## Nuovo repository
Quando si crea un repository nuovo per una realtà o un progetto:
1. Copia in `.claude/rules/` tutte le regole trasversali di `assistente-personale/.claude/rules/`, e in `.claude/skills/` la skill `landing-premium` se il repo riguarda un sito.
2. Aggiungi il repo alla routine cloud «Allineamento quotidiano regole e skill nei repo dei siti» (`trig_01P4p1hNKf9AUZ9WH3ur8Dkk`): va sia nelle `sources` sia nell'elenco delle destinazioni del prompt.
3. Aggiungi il repo in `memoria/` (voce della realtà) e in `CLAUDE.md` di `assistente-personale` se cambia il modo di lavorare.
