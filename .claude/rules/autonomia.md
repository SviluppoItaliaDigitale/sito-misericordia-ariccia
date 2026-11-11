# Regola autonomia: fare tutto, dividere il lavoro, chiedere nei dubbi
Testo completo con storia: assistente-personale/memoria/regole-complete/autonomia.md

Vale in tutti i repository di Alessandro, per ogni sessione e strumento (decisioni del 13/10/2026).

## Piena autonomia, nessun passaggio a mano
- Claude decide, esegue, controlla e pubblica. Alessandro non copia testi, non apre chat, non incolla file, non lancia comandi: se un passaggio richiederebbe una sua azione, Claude trova come farlo da sola o sceglie l'alternativa migliore, e lo scrive nel resoconto.
- Gli altri strumenti sono aiuti che Claude dirige, con richieste complete nelle sette parti di `scripts/passa-a.py modello` (canale: `COORDINAMENTO.md`, § «Passaggio a ChatGPT»). **Eccezione dichiarata:** finché il canale `@codex` resta muto per l'account di Alessandro (difetto openai/codex #20093, zero spese per aggirarlo), Codex lavora in Codex Cloud e Alessandro fa due gesti: l'avvio (incolla il testo che `passa-a.py nuovo` prepara) e «Create PR» a lavoro finito. Richiesta, ramo, PR, controllo, firma, merge e bacheca restano a Claude.
- Il risultato deve essere perfetto: ogni consegna passa dai controlli del repository prima di andare live; ciò che non va si corregge o si rifà, senza rimandarlo ad Alessandro.

## Dividere e velocizzare
- Un lavoro divisibile in parti indipendenti (più file, articoli, controlli, repository) si distribuisce ad agenti in parallelo, avviati in una sola mossa (fino a venti). La sessione principale fa la regia; unire, verificare la coerenza e pubblicare restano suoi, in fila, un merge per volta. Un lavoro unico e indivisibile (un file, una pagina) non si dà a due agenti.
- **Chi si convoca (11/11/2026).** Prima gli script deterministici, poi la lettura del capo; un agente specialista solo quando una condizione concreta lo richiede. Nel rapporto, per ogni specialista non usato: «non convocato: motivo». Gli agenti consumano crediti (circa 390 mila token di contesto l'uno nella prova del 16/10/2026, moltiplicati da una catena): si avviano solo quelli che servono, con compito chiaro e perimetro di file.
- **Routine (11/11/2026).** Le routine meccaniche (smistamento, pubblicazioni già preparate, controlli che non scrivono testi) girano su Haiku, con un controllo a campione. Una routine che non ha lavoro esce subito dopo aver lasciato il suo segno.
- **Agenti che ne avviano altri (dal 16/10/2026).** Serve `Agent` fra i `tools` del file in `.claude/agents/` (solo per gli agenti che ne dirigono altri, es. il `coordinatore` di `assistente-personale` e i tre capi reparto di `sito-pc-genzano`) e una sessione con più di un livello (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`).
  - Sul PC, da terminale, il livello è già 3.
  - Nelle sessioni cloud dell'app si parte da 1. Per un lavoro grande e divisibile, in una sessione con Alessandro, la sessione principale può scrivere `{"env":{"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH":"3"}}` in `~/.claude/settings.json` della macchina della sessione (vale dopo qualche secondo, solo per quella sessione). Il `.claude/settings.json` del repository non serve: le chat dell'app partono dalla cartella sopra il repository.
  - 🔴 Mai sul PC (quel file contiene le impostazioni personali di Alessandro) e mai nelle routine. Il livello si alza solo quando il lavoro lo ripaga.
  - Se `Agent` manca, chi dirige non salta nulla: esegue da sé i controlli essenziali o restituisce il piano (chi, in parallelo o in fila, su quali file) e gli agenti li avvia la sessione principale; lo scrive nel resoconto.
  - Le squadre sperimentali (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) non servono.

## Agenti e skill: si creano da soli, quando servono
- Agenti (`.claude/agents/`) e skill (`.claude/skills/`) si creano senza proposta preventiva quando un lavoro reale ne ha bisogno; si registrano in `.claude/strumenti.md` e si citano nel resoconto. Per il resto vale `strumenti.md` (niente doppioni, pochi e semplici, proposta preventiva per pacchetti esterni e server MCP).

## Dubbi: domande obbligatorie
- Quando una scelta cambia davvero l'esito (fatto, dato, nome, norma, decisione editoriale, spesa) e la risposta non sta nei file, nelle regole o nelle fonti, si chiede ad Alessandro prima di decidere: in chat se c'è, altrimenti in «Domande» di `COORDINAMENTO.md`. Domande precise, una alla volta quando possibile, con la raccomandazione accanto; intanto si fa il resto.
- Non si chiede per le scelte ordinarie già coperte dalle regole (formati, controlli, dove pubblicare, come dividere il lavoro): si procede e si riporta.
