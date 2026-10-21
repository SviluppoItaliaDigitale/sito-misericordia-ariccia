# Routine «Monitoraggio Liturgia del giorno»

- **Quando gira:** ogni giorno alle 08:00 italiane con l'ora legale, alle 07:00 con l'ora solare.
- **Routine di Claude:** `trig_01QHWD37UUth9jJ8YwPpEb6W`, testo aggiornato il 28/08/2026. Sotto la riga c'è lo stesso testo della routine, salvo l'indirizzo email di Alessandro, tolto perché il repository è pubblico: se cambi l'uno, cambia anche l'altro.
- **Se Claude è ferma:** la esegue ChatGPT quando Alessandro chiede «fai le routine di oggi» (`AGENTS.md`, § «Quando Claude è fermo, lavori tu al suo posto»). Dove il testo chiede una notifica push o un'email ad Alessandro, l'esito va nel riassunto finale e, se il lavoro nasce da una issue, in un commento sulla issue; dove chiede di avviare un agente, applichi tu la lista di controllo del suo file in `.claude/agents/`.
- **Come capire se oggi è già stata fatta:** non lascia tracce se va tutto bene: i controlli sono solo letture, quindi rifalli sempre.
- **Valori superati nel testo:** la routine è stata scritta nella fase di anteprima, finita il 6 luglio 2026, e alcuni valori non valgono più. Valgono questi, come dice anche `CLAUDE.md`:
  - pagina da controllare: https://www.misericordia-ariccia.it/liturgia-del-giorno/ (l'indirizzo `/anteprima/liturgia-del-giorno/` rimanda lì con un 301);
  - workflow: «Pubblica su Aruba (LIVE)», cioè `deploy.yml`, al posto di «Pubblica su Aruba (anteprima)»;
  - ricostruzione notturna: alle 22:05 e alle 23:05 UTC, così una delle due cade alle 00:05 italiane in ogni stagione; al punto 4 «di oggi» vuol dire l'esecuzione della notte appena passata, che `gh` data al giorno prima;
  - letture: quelle principali sono della CEI (chiesacattolica.it), Evangelizo è solo il ripiego; se un feed non risponde dall'ambiente cloud, che può bloccarli, guarda i log dell'ultimo deploy;
  - rilancio: `gh workflow run deploy.yml` senza input, come fa il guardiano notturno (`guardiano-liturgia.yml`): gli input servono solo per i social, e `ripubblica_instagram` cancella e ripubblica dei post.
  Il testo della routine lo può correggere solo Alessandro, dalla pagina della routine; finché resta così, il corpo qui sotto resta uguale alla routine.

---
Sei l'agente di monitoraggio della funzione "Liturgia del giorno" del sito della Misericordia di Ariccia (anteprima animata su Aruba). Parti da zero contesto: esegui questi passi e agisci.

Contesto: la pagina live è https://www.misericordia-ariccia.it/anteprima/liturgia-del-giorno/ ; usa le letture da Evangelizo e la celebrazione/santo dal calendario liturgico italiano (litcal). Il sito è ricostruito ogni notte dal workflow GitHub Actions "Pubblica su Aruba (anteprima)" del repo SviluppoItaliaDigitale/sito-misericordia-ariccia.

1) Data di oggi: esegui `date -u +%Y%m%d` (es. 20260620) e `date -u +%Y-%m-%d`.
2) Verifica le FONTI esterne per OGGI:
   - Letture: `curl -s 'https://feed.evangelizo.org/v2/reader.php?date=AAAAMMGG&type=all&lang=IT'` deve restituire testo NON vuoto contenente 'Vangelo' e una citazione biblica.
   - Calendario: `curl -s 'https://litcal.johnromanodorazio.com/api/dev/calendar/nation/IT/AAAA?year_type=CIVIL'` deve essere JSON con almeno un evento per la data di oggi.
3) Verifica la PAGINA LIVE: `curl -sk 'https://www.misericordia-ariccia.it/anteprima/liturgia-del-giorno/'`. Deve contenere 'messale' con il testo del Vangelo e NON il messaggio di fallback 'non sono momentaneamente disponibili'. Verifica anche che la data mostrata sia quella di OGGI (se è vecchia, il rebuild notturno non è avvenuto).
4) Verifica l'ultimo deploy notturno: `gh run list --repo SviluppoItaliaDigitale/sito-misericordia-ariccia --workflow 'Pubblica su Aruba (anteprima)' --limit 3` — l'ultimo run deve essere 'success' e di oggi.

SE TUTTO È OK: termina con un resoconto breve 'OK — Liturgia del giorno aggiornata e funzionante' e NON inviare email.

SE QUALCOSA È ROTTO (feed irraggiungibile, pagina con fallback, data vecchia, deploy fallito):
 a) Prova a RISOLVERE: ri-lancia il deploy con `gh workflow run 'Pubblica su Aruba (anteprima)' --repo SviluppoItaliaDigitale/sito-misericordia-ariccia`, attendi ~3 minuti (`sleep 180`), poi ricontrolla la pagina live.
 b) Se il problema è il feed Evangelizo irraggiungibile o vuoto, annotalo: potrebbe servire una fonte alternativa per le letture.
 c) INVIA UNA EMAIL via Gmail a l'indirizzo Gmail di Alessandro con oggetto 'Liturgia del giorno — problema rilevato' e un corpo che spiega in italiano: cosa è rotto, cosa hai provato, se si è risolto, e l'azione consigliata.

Concludi SEMPRE con un resoconto chiaro di cosa hai verificato, dell'esito e delle azioni svolte.

AVVISO IN CASO DI BLOCCO OPERATIVO: se qualcosa impedisce a TE di eseguire i controlli o le azioni previste (clone o accesso al repo negato, gh non autenticato o senza permessi, Gmail non disponibile per inviare l'email, strumenti mancanti, errori ripetuti dell'ambiente), NON chiudere in silenzio: avvisa l'utente (PushNotification, e email se Gmail funziona) con (a) il passo in cui ti sei bloccata, (b) l'errore ESATTO e verbatim, (c) cosa serve per sbloccare, (d) quali controlli hai comunque completato e con che esito. Includi l'id di questa routine: trig_01QHWD37UUth9jJ8YwPpEb6W. L'assistente dell'utente sul PC (workspace assistente-personale) ha un runbook per sbloccarti (memoria/runbook-sblocco-routine-cloud.md): scrivi l'avviso in modo che possa agire subito senza farti altre domande.
