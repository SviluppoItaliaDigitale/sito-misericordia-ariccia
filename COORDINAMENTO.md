# Bacheca di coordinamento — sito della Misericordia di Ariccia

File interno: Hugo non lo pubblica. Lo usano Claude e ChatGPT per passarsi lavoro, istruzioni e avvisi. La prima parte è il protocollo comune a tutti i repository di Alessandro; la seconda riguarda solo questo sito.

<!-- PROTOCOLLO-COMUNE:INIZIO — testo identico in tutti i repository di Alessandro. Copia di riferimento: assistente-personale/COORDINAMENTO.md. Se lo cambi, cambialo in tutti e cinque i repository nello stesso lavoro. -->

## Protocollo comune Claude ⇄ ChatGPT ⇄ Gemini (uguale in tutti i repository)

Valido dall'11/10/2026 in tutti i repository di Alessandro: `sito-pc-genzano`, `social-pc-genzano`, `sito-misericordia-ariccia`, `cooprimavera`, `assistente-personale`. Il file si chiama sempre `COORDINAMENTO.md` e sta sempre nella cartella principale del repository. Questa prima parte è identica ovunque; la seconda parte, «Questo repository», cambia da repository a repository.

### A che cosa serve

Claude (Claude Code) e ChatGPT (chat con connettore GitHub, Codex) lavorano sugli stessi repository. La bacheca è il posto dove si passano lavoro, istruzioni e avvisi, così Alessandro non deve copiare testi da una chat all'altra e il lavoro continua anche quando una delle due non è disponibile (per esempio quando Claude ha finito i crediti).

**Anche Gemini (dall'11/10/2026).** Gemini lavora sui repository con **Jules** (jules.google, legge da solo `AGENTS.md`) o con Gemini CLI. Dove questo protocollo dice «ChatGPT», vale allo stesso modo per Gemini: stesse regole, stessa autonomia, stesse eccezioni. Differenze: i suoi rami si chiamano `gemini/<argomento>-AAAAMMGG`; una richiesta indirizzata a «ChatGPT» la prende solo ChatGPT, una indirizzata a «Gemini» solo Gemini, una indirizzata a «chi è disponibile» la prende la prima che apre la bacheca, che scrive subito accanto «presa da …» con una PR in bozza, così l'altra non la riprende. Le revisioni automatiche fatte da Codex o da Gemini sulle PR sono pareri da verificare, non ordini.

### Chi dà le istruzioni

- **Alessandro**: in chat o scrivendo una richiesta qui. Le sue istruzioni prevalgono su tutto il resto.
- **Claude o ChatGPT**: con una voce nella sezione «Richieste» di questo file, indirizzata all'altra.
- Le regole del repository (`CLAUDE.md`, `.claude/rules/`, `AGENTS.md`) valgono per entrambe: chi lavora le segue anche quando l'altra non c'è.

### Che cosa fa ChatGPT quando Alessandro scrive «guarda la bacheca» (o «continua il lavoro»)

ChatGPT lavora **in autonomia fino alla pubblicazione**, senza aspettare Claude:

1. **Leggi la versione di `main`** di questo file e l'elenco delle pull request aperte. Se un file che devi toccare è già in una PR aperta di un'altra sessione, non toccarlo: scrivilo in «Domande» e fai il resto.
2. **Prendi prima i lavori lasciati a metà** nella sezione «Lavori in corso», poi le richieste aperte indirizzate a ChatGPT (o a «chi è disponibile»), in ordine di data. Solo se entrambe le sezioni sono vuote rispondi in una riga: «Nessuna richiesta aperta per me in bacheca».
3. **Apri un ramo tuo** da `main` aggiornato: `chatgpt/<argomento>-AAAAMMGG` (o `codex/...`). Non riprendere il ramo di un'altra sessione, **salvo quando è indicato in «Lavori in corso»**: quel ramo, e la sua PR, sono passati a te e li continui lì.
4. **Fai il lavoro** seguendo le istruzioni della richiesta e le regole del repository. Leggi solo i file che servono a quel lavoro.
5. **Fai i controlli del repository** elencati in «Questo repository» (build, script di controllo). Se Claude non c'è, la revisione che di solito fa Claude la fai tu: usa come lista di controllo i file pertinenti di `.claude/agents/` se il repository li ha, altrimenti le regole di `CLAUDE.md`, `.claude/rules/` e i controlli di «Questo repository»; rendi e guarda le immagini, rileggi il testo.
6. **Apri la PR verso `main`** (anche in bozza), poi, **sullo stesso ramo**, aggiorna questa bacheca: accanto alla richiesta scrivi «fatta da ChatGPT, PR #N» con il numero appena assegnato e una riga su che cosa hai fatto; se una parte non si poteva fare, scrivi il motivo. Fai push: la PR si aggiorna da sola.
7. **Aspetta i controlli automatici e, se sono verdi, unisci tu la PR** (squash; se era in bozza, prima segnala che è pronta) e, dove il merge pubblica qualcosa (lo dice «Questo repository»), verifica che la pubblicazione parta e finisca (scheda Actions). Dove il merge non pubblica nulla, non lanciare a mano i workflow di pubblicazione. Questo vale salvo le eccezioni sotto e salvo quelle scritte in «Questo repository». Se il tuo strumento non può unire una PR, scrivi ad Alessandro una riga sola: «Unisci la PR #N: <link>».
8. **Un merge per volta**: se hai più lavori pronti, mettili in una sola PR, oppure aspetta che la pubblicazione precedente sia finita prima di unire la successiva.
9. **Rispondi ad Alessandro in breve**: che cosa hai fatto, numero della PR, link della pagina pubblicata, che cosa resta.

### Quando ChatGPT non unisce e si ferma

- I controlli automatici sono rossi e non sai correggerli: lascia la PR aperta e scrivi il problema in «Domande».
- Il lavoro richiede credenziali, spese, invii a persone o enti (email, messaggi), cancellazioni definitive o post sui social fuori dalle automazioni già previste.
- L'istruzione è ambigua su un fatto (dato, data, nome, norma): non indovinare, scrivi la domanda e fai il resto.
- Lo dice una regola di «Questo repository».

### Regole che valgono sempre

- **Mai commit diretti su `main`**: sempre ramo + PR, salvo che Alessandro lo chieda espressamente per quella modifica.
- **Mai dati inventati**: nomi, numeri, date, norme, recapiti si scrivono solo se verificati su una fonte. Se mancano, resta un campo «[da compilare]» o una domanda in bacheca.
- **Mai segreti nel repository** (password, token, chiavi).
- **Niente riferimenti all'intelligenza artificiale** nei contenuti pubblicati; nei repository della Protezione Civile (`sito-pc-genzano`, `social-pc-genzano`) nemmeno nei messaggi di commit, nei titoli e nei testi delle PR.
- **Italiano corretto e chiaro** in file, commit e PR.
- **Non cancellare quello che ha scritto l'altra**: si risponde sotto o si archivia con una riga di esito.

### Formato delle voci

- **Richiesta**: `- **AAAA-MM-GG — da <chi> a <chi> — <titolo>**` e sotto: che cosa serve, quali file, quali controlli, dove si pubblica. Chi la prende scrive accanto «presa da …, PR #N»; a lavoro pubblicato la sposta in «Archiviati» con l'esito.
- **Avviso**: `- **GG/MM/AAAA — <chi>.** testo`, in cima alla sezione «Avvisi». Serve quando un lavoro riguarda anche l'altra sessione (file rifatti, script cambiati, file generati da rigenerare).
- **Domanda**: in «Domande». Chi la legge risponde sotto, alla prima occasione.
- **Consegna di fine sessione**: chi chiude una sessione con lavoro a metà scrive in «Lavori in corso» che cosa resta, su quale ramo e in quale PR, così l'altra può riprenderlo: da quel momento il ramo passa all'altra sessione, e chi l'ha consegnato non ci fa più push finché non lo riceve indietro con una nuova consegna.

<!-- PROTOCOLLO-COMUNE:FINE -->

## Questo repository: sito-misericordia-ariccia

Il merge su `main` pubblica il sito LIVE su www.misericordia-ariccia.it in circa un minuto (workflow «Pubblica su Aruba (LIVE)»). Regole complete in `CLAUDE.md` (flusso editoriale, grafica brand, SEO, versione inglese, social) e in `.claude/rules/`.

### Compiti con immagini: cartella `bacheca/`

Per immagini generate e grafiche resta il sistema a file di `bacheca/` (protocollo in `bacheca/LEGGIMI.md`, modello in `bacheca/MODELLO.md`): un file per compito in `bacheca/compiti/`, consegne in `bacheca/consegne/`. Qui, in «Richieste», basta una riga che rimanda al compito.

### Controlli prima di unire una PR

- Build con Hugo 0.154.5 extended senza errori (`hugo --minify`).
- Il workflow «Controlli del sito» sulla PR verde (`scripts/controlli/controlla_sito.py`: link, immagini, video, CSP, registro dei dati, revisione sanitaria, news in uscita).
- Immagini nuove: `python3 scripts/ottimizza-immagini.py static/img/news` (crea i `.webp`); grafiche con cornice e filigrane come da `CLAUDE.md`, renderizzate e guardate prima di usarle.
- News: front matter completo (`description` specifica, `italianoSemplice`), fonti citate, link interni, data non futura se deve uscire subito.
- Dato aggiornabile nuovo (numeri, importi, leggi, contatti): aggiungilo a `data/dati_da_verificare.yaml`.
- Se cambi uno script inline, ricalcola gli hash della CSP (`hugo --minify` poi `python3 scripts/controlli/controlla_sito.py public --csp`).
- Dopo il deploy verifica la pagina live con `curl -L` (i 503 saltuari sono l'anti-bot di Aruba: riprova) e dai ad Alessandro il link.

### Quando qui ChatGPT non unisce

- Contenuti sanitari nuovi o cambiati (primo soccorso, rianimazione): PR pronta, unisce Alessandro dopo la revisione di un istruttore.
- Privacy, costi dei servizi, bandi: PR pronta, unisce Alessandro.
- I social escono da soli dopo il deploy (`scripts/pubblica_social.py`): una news con `social: false` non viene condivisa. Nessuna pubblicazione social a mano.

## Domande

- Nessuna domanda aperta.

## Lavori in corso

- Nessun lavoro a metà al 11/10/2026.

## Richieste

- Nessuna richiesta aperta. Compiti 001 (approvato) e 002 (pubblicato) chiusi in `bacheca/compiti/`.

## Avvisi

- **11/10/2026 — Claude.** Da oggi ChatGPT lavora fino alla pubblicazione anche sui file del sito, non solo in `bacheca/`, seguendo il protocollo comune qui sopra. `AGENTS.md`, `bacheca/LEGGIMI.md` e `CLAUDE.md` sono stati allineati.

## Archiviati

- Nessuna voce.
