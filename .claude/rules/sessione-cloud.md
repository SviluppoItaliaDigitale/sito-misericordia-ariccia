# Regola sessioni cloud e nuovi repository

Vale in tutti i progetti, presenti e futuri. Obiettivo: Alessandro lavora da PC, da cellulare o da un'altra postazione, anche con il PC spento, trovando sempre tutto disponibile.

## Parità cellulare–PC
- Il cellulare vale quanto il PC, specie in emergenza quando il PC non si può usare: niente deve esistere solo sul PC.
- La memoria si salva **solo** in `memoria/` del repo (versionata), mai nella memoria automatica locale di Claude Code, che il cloud non vede.
- Strumenti, script e configurazioni nuove vanno nel repo, non solo in `~/.claude` o sul desktop.

## Se sei in una sessione cloud (PC spento)
- Riconoscila così: non esistono `~/Scrivania`, gli altri progetti del PC e gli MCP locali (Firecrawl, Playwright).
- Per il web usa `WebSearch` e `WebFetch`. Gmail, Calendar, Drive e Canva funzionano (connettori di claude.ai).
- Regole, agenti, skill e memoria vengono dal repo: seguili come sul PC. I permessi li approva Alessandro dal cellulare.
- Qui un agente non ne avvia altri: la sessione parte con un solo livello di agenti. Per un lavoro grande e divisibile la sessione principale lo alza per sé, mai nelle routine, come spiega la regola `autonomia.md`, § «Dividere e velocizzare».
- I risultati vanno nel repo, su Drive o inviati ad Alessandro: non esiste un desktop.
- A fine lavoro fai **commit e push**, così il lavoro arriva al PC e alle altre postazioni. Nei repo dei siti, dove il merge su `main` avvia il deploy, segui le regole di pubblicazione del repo.
- Se ti serve un altro repo, dillo: va aggiunto quando si crea la sessione.

## Nuovo repository
Quando si crea un repository nuovo per una realtà o un progetto:
1. Copia in `.claude/rules/` tutte le regole trasversali di `assistente-personale/.claude/rules/`, e in `.claude/skills/` la skill `landing-premium` se il repo riguarda un sito. Copia anche il kit del passaggio a ChatGPT e dell'identità dei commit (dal 13/10/2026): `scripts/passa-a.py`, `scripts/imposta-identita-git.sh`, `.githooks/commit-msg` (tutti eseguibili), il workflow `.github/workflows/rimuovi-firma-strumento.yml` con `scripts/rimuovi-firma-strumento.py` (toglie dai testi su GitHub la firma che il canale delle sessioni aggiunge da solo) e, in `.claude/settings.json`, `"includeCoAuthoredBy": false` più l'hook `SessionStart` che esegue `bash scripts/imposta-identita-git.sh` (timeout 10); poi `.claude/strumenti.md` con la riga del kit. Verifica: `bash scripts/imposta-identita-git.sh`, `git config user.name` = `Alessandro Cuollo`, `git config core.hooksPath` = `.githooks`, `python3 scripts/passa-a.py stato` senza errori.
2. Aggiungi il repo alla routine cloud «Allineamento quotidiano regole, kit e passaggi automatici nei repository (dal 13/10/2026)» (`trig_01Kx6EVhaSiFnEdKHjDaCQzx`, ogni giorno alle 05:03 italiane): va sia nelle `sources` sia nell'elenco delle destinazioni del prompt. La routine precedente `trig_01P4p1hNKf9AUZ9WH3ur8Dkk` è disattivata dal 13/10/2026.
3. Copia in radice `COORDINAMENTO.md` (prima parte identica a quella di `assistente-personale/COORDINAMENTO.md`, poi la sezione «Questo repository») e crea `AGENTS.md` che rimanda alla bacheca, con il paragrafo «Passaggio preparato da Claude, avviato da Alessandro», la sezione «Qualità e guasti: regole per ogni intelligenza artificiale» e la sezione `## Code Review Rules` presi da `assistente-personale/AGENTS.md` (l'ultima la legge la revisione automatica delle pull request).
4. Aggiungi il repo in `memoria/` (voce della realtà) e in `CLAUDE.md` di `assistente-personale` se cambia il modo di lavorare.
5. Installa la sorveglianza dei guasti (regola `guasti.md`, dal 17/10/2026): sempre le label `automazione` e `fonte-rotta`. Se il repository pubblica un sito, copia anche i workflow `controllo-link.yml` e `salute-sito.yml` da `sito-misericordia-ariccia` o `cooprimavera` (il primo costruisce il sito con Hugo: adattalo al generatore e all'indirizzo del sito nuovo) e aggiungi il repo alla routine «Riparazione guasti dei siti» (`trig_01RBJ5MxdCUxjeq5UDGu5Lej`), sia nelle `sources` sia nell'elenco del prompt (il `job_config` si reinvia intero: un update parziale cancella il prompt). Un repository che non è un sito non riceve quei due workflow, che lì fallirebbero: la sua sorveglianza è quella adatta a ciò che fa (i run falliti delle sue automazioni, le fonti che legge), aggiunta quando ne ha.
