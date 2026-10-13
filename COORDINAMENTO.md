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
- **Dubbi → domande** (istruzione di Alessandro del 13/10/2026: «se hai dubbi sei obbligato a fare domande a me per chiarimenti»). Quando una scelta cambia davvero l'esito e la risposta non è nei file, nelle regole o nelle fonti, non si indovina: si chiede ad Alessandro — in chat se c'è, altrimenti in «Domande» qui sotto — e intanto si fa il resto. Per le scelte ordinarie coperte dalle regole si procede e si riporta (regola `.claude/rules/autonomia.md`).

### Che cosa fa ChatGPT quando Alessandro scrive «guarda la bacheca» (o «continua il lavoro»)

ChatGPT lavora **in autonomia fino alla pubblicazione**, senza aspettare Claude:

1. **Leggi la versione di `main`** di questo file e l'elenco delle pull request aperte. Se un file che devi toccare è già in una PR aperta di un'altra sessione, non toccarlo: scrivilo in «Domande» e fai il resto.
2. **Prendi prima i lavori lasciati a metà** nella sezione «Lavori in corso», poi le richieste aperte indirizzate a ChatGPT (o a «chi è disponibile»), in ordine di data. Solo se entrambe le sezioni sono vuote rispondi in una riga: «Nessuna richiesta aperta per me in bacheca».
3. **Apri un ramo tuo** da `main` aggiornato: `chatgpt/<argomento>-AAAAMMGG` (o `codex/...`). Non riprendere il ramo di un'altra sessione, **salvo quando è indicato in «Lavori in corso»** o quando il lavoro ti arriva con un passaggio automatico (§ «Passaggio automatico a ChatGPT»): in quei casi il ramo, e la sua PR, sono passati a te e li continui lì.
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
- **Ogni lavoro è a firma di Alessandro Cuollo** — o del suo nominativo radioamatoriale **IU0QVW**, dove è d'uso — e in nessun caso deve apparire che sia stato fatto da un'intelligenza artificiale, «mai e poi mai» (istruzione del 13/10/2026, che estende a tutti i repository la regola nata in `sito-pc-genzano`). In pratica: identità git `Alessandro Cuollo <65465537+SviluppoItaliaDigitale@users.noreply.github.com>` su ogni commit (`bash scripts/imposta-identita-git.sh`, presente in ogni repository, la imposta e attiva l'hook `.githooks/commit-msg`, che toglie dal messaggio le righe `Co-authored-by` e quelle di sessione); nessun nome di strumenti nei messaggi di commit, nei titoli, nei testi e nei commenti delle PR, nei file pubblicati, nei metadati e nelle immagini; i commit arrivati su un ramo con un altro autore si riscrivono a nome di Alessandro prima di unire (`passa-a.py chiudi` lo fa da sé e toglie dalla PR i commenti di avvio e di risposta dello strumento); il merge è sempre squash con messaggio scritto a mano, così su `main` l'autore è Alessandro. Unica eccezione: i file di governo interni, non pubblicati (`CLAUDE.md`, `AGENTS.md`, `.claude/`, questa bacheca), che parlano necessariamente degli strumenti. Regola completa in `.claude/rules/firma-dei-lavori.md`, uguale in tutti i repository.
- **Italiano corretto e chiaro** in file, commit e PR.
- **Non cancellare quello che ha scritto l'altra**: si risponde sotto o si archivia con una riga di esito.

### Formato delle voci

- **Richiesta**: `- **AAAA-MM-GG — da <chi> a <chi> — <titolo>**` e sotto: che cosa serve, quali file, quali controlli, dove si pubblica. Chi la prende scrive accanto «presa da …, PR #N»; a lavoro pubblicato la sposta in «Archiviati» con l'esito.
- **Avviso**: `- **GG/MM/AAAA — <chi>.** testo`, in cima alla sezione «Avvisi». Serve quando un lavoro riguarda anche l'altra sessione (file rifatti, script cambiati, file generati da rigenerare).
- **Domanda**: in «Domande». Chi la legge risponde sotto, alla prima occasione.
- **Consegna di fine sessione**: chi chiude una sessione con lavoro a metà scrive in «Lavori in corso» che cosa resta, su quale ramo e in quale PR, così l'altra può riprenderlo: da quel momento il ramo passa all'altra sessione, e chi l'ha consegnato non ci fa più push finché non lo riceve indietro con una nuova consegna.

### Passaggio automatico a ChatGPT (dal 13/10/2026)

Claude non aspetta più che Alessandro scriva «guarda la bacheca»: quando decide che un lavoro va a ChatGPT, lo avvia da sola. Istruzione di Alessandro del 13/10/2026: «devi essere te in automatico a creare le istruzioni, aprire l'intelligenza artificiale idonea, fargli fare le cose e andare a pubblicare»; «valuta te i casi in cui deve essere utilizzato».

**Nessun passaggio a mano per Alessandro.** Istruzione del 13/10/2026: «io non devo fare nulla: devi fare tutto te in piena autonomia nel migliore dei modi»; «considera che hai un amico a disposizione a darti una mano, e tu gli devi dire esattamente cosa deve fare». Quindi: Claude decide, scrive la richiesta completa, la avvia, controlla il risultato, corregge o rifà da sola quando non va, e pubblica. Alessandro non copia testi, non apre chat, non incolla file. Se un lavoro non si può passare (sotto, «Che cosa non si passa») o non si può fare nel canale automatico (sotto, «Immagini»), lo fa Claude, se serve con più agenti in parallelo (regola `.claude/rules/autonomia.md`, uguale in tutti i repository: autonomia, lavoro diviso, agenti e skill creati quando servono, domande ad Alessandro nei dubbi).

**Come si avvia.** Claude scrive la richiesta in «Richieste» (formato di sempre, con la nota «passata in automatico»), apre un ramo `chatgpt/<argomento>-AAAAMMGG` da `main` aggiornato, apre una **pull request in bozza** con la stessa richiesta nella descrizione e lascia sulla PR il commento `@codex esegui la richiesta nella descrizione`. Codex, lo stesso che già rivede le pull request, parte da solo, lavora su quel ramo e fa push; il commento arriva dall'account di Alessandro, quindi vale come una sua istruzione. Chi lavora segue il protocollo di sempre (punti 4-6): controlli del repository, bacheca aggiornata sullo stesso ramo con «fatta da ChatGPT, PR #N», nessun'altra PR. Lo fa lo script `scripts/passa-a.py`, uguale in tutti i repository (`nuovo` avvia, `stato` controlla, `chiudi` unisce; `modello` stampa lo schema della richiesta). Se in un repository l'integrazione Codex non risponde, Claude fa il lavoro da sola e lo scrive in «Domande», una volta sola, perché Alessandro possa attivarla quando vuole.

**Prerequisito: un ambiente cloud per ciascun repository.** Il commento `@codex …` fa lavorare Codex solo se il repository ha il suo ambiente cloud (chatgpt.com/codex/cloud/settings/environments): altrimenti risponde «To use Codex here, create an environment for this repo» e non fa nulla. Gli ambienti li crea Alessandro, una volta per repository e solo da PC (dal cellulare non si può), con la configurazione automatica proposta da Codex, accesso a internet dell'agente attivo e pubblicazione finale; verificato il 13/10/2026: l'ambiente creato partendo da `social-pc-genzano` scaricava tutti e cinque i repository ma valeva per quello solo. `passa-a.py stato` riconosce quella risposta («AMBIENTE MANCANTE»); quando l'ambiente c'è, `passa-a.py riavvia --pr N` rimanda il commento di avvio sulla stessa PR. Fino ad allora il lavoro lo fa Claude da sola, come per i crediti finiti.

**Che cosa contiene la richiesta, sempre.** ChatGPT lavora bene solo con istruzioni esatte, e nel canale automatico non può fare domande: tutto ciò che gli serve sta nella richiesta, verificato prima da Claude. Sette parti, nell'ordine (`passa-a.py modello` le stampa): (1) **obiettivo** in una frase, e a che cosa serve; (2) **file** da creare o modificare, con il percorso esatto; (3) **che cosa fare**, passo per passo, con i dati già verificati (numeri, nomi, date, misure, testi): niente da cercare, niente da indovinare; (4) **vincoli** del repository che valgono per quel lavoro (regole, licenze, misure, accessibilità, niente riferimenti allo strumento nei file e nei commit); (5) **controlli** da eseguire prima del push, con i comandi esatti; (6) **consegna**: commit sul ramo della PR, bacheca aggiornata sullo stesso ramo, un commento breve sulla PR con fatto / non fatto / perché; (7) **che cosa non fare**: non unire, non segnare pronta, non aprire altre PR, non toccare altri file. Una richiesta a cui manca una parte non si manda.

**Quando Claude lo fa da sola.** Lo decide caso per caso, con parsimonia: il piano ChatGPT ha crediti a consumo e ogni passaggio li usa (li usa anche la revisione automatica che Codex fa su ogni PR non in bozza, quindi la PR resta in bozza finché il lavoro non è finito, e più lavori piccoli si mettono in una richiesta sola). Si passa un lavoro quando:

- **serve andare live prima su più fronti**, soprattutto in emergenza o quando lo stesso contenuto esce su più siti: Claude tiene per sé la parte che richiede i gate editoriali e la comunicazione di allerta ed emergenza, e passa a ChatGPT le parti autonome che si possono specificare per iscritto (script e dati, controlli, audit, materiali di supporto, adattamenti di cose già fatte), così lavorano in parallelo invece che in fila;
- **è un lavoro che ChatGPT sa fare bene e che non ha bisogno del giudizio della sessione**: l'aggiornamento degli interventi dall'export del gestionale, gli audit del sito, i controlli ripetitivi;
- **una sessione finisce con un lavoro urgente a metà** (emergenza, uscita programmata entro un giorno, Alessandro ha chiesto di andare live): oltre alla consegna in «Lavori in corso», Claude passa il ramo a ChatGPT con lo stesso meccanismo. Se non è urgente, scrive solo la consegna.

**Immagini.** Le illustrazioni **SVG** le fa Claude (istruzione di Alessandro del 13/10/2026): sono codice, le rende e le guarda prima di pubblicarle; le passa a ChatGPT solo per lavorare in parallelo, con la richiesta completa (misure, contenuto riquadro per riquadro, testi, vincoli). Le **immagini raster** (foto, locandine, grafiche PNG o JPG) non passano dal canale automatico, perché Codex non ha il generatore di immagini: le fa Claude con i propri strumenti — i generatori del repository (cover, immagini social, fascia blu), gli SVG resi in PNG, i connettori grafici disponibili nella sessione quando ci sono, le foto con licenza libera — e le controlla prima del commit come ogni immagine. Se un'immagine non si può fare in nessuno di questi modi, Claude sceglie l'alternativa migliore (per esempio un'illustrazione al posto di una foto) e lo scrive nella PR. Nessun passaggio a mano per Alessandro.

**Che cosa non si passa.** Allerte ed emergenze vere, articoli nuovi che devono passare dai gate editoriali, pagine legali, lavori che richiedono credenziali, spese o invii a persone: restano a Claude o ad Alessandro, come in «Quando ChatGPT non unisce e si ferma».

**Chi chiude.** Codex avviato da un commento non unisce la PR e non la segna pronta. Chiude Claude: la sessione che ha fatto il passaggio ne controlla l'esito (`passa-a.py stato`), guarda il risultato (immagini rese e guardate, controlli del repository, niente dati inventati né riferimenti allo strumento), poi `passa-a.py chiudi`: riscrive a nome di Alessandro i commit del ramo che avessero un altro autore, porta nel ramo le novità di `main` con un commit di merge (mai rebase; se c'è un conflitto si ferma e lo si risolve a mano), segna la PR pronta, aspetta i controlli verdi, unisce (squash con messaggio scritto, un merge per volta), toglie dalla PR il commento di avvio e le risposte dello strumento (i rapporti di `github-actions[bot]` restano) e, dove il repository ha `deploy.yml`, aspetta che il deploy del merge finisca bene: un deploy fallito ferma lo script, perché il sito non è aggiornato. Se la sessione è finita, lo fa la routine giornaliera. Se il risultato non va bene, Claude **continua direttamente** sullo stesso ramo e corregge o rifà, senza rimandare indietro (ogni giro costa crediti); se Codex risponde che i crediti sono finiti o non risponde entro un giorno, Claude fa il lavoro da sola e lo scrive in bacheca.

**Gemini.** Lo stesso schema varrà per Jules (etichetta `jules` su una issue) quando Alessandro avrà autorizzato l'app sui repository; fino ad allora i lavori che sarebbero andati a Gemini li fa Claude o passano a ChatGPT.

<!-- PROTOCOLLO-COMUNE:FINE -->

## Questo repository: sito-misericordia-ariccia

Il merge su `main` pubblica il sito LIVE su www.misericordia-ariccia.it in circa un minuto (workflow «Pubblica su Aruba (LIVE)»). Regole complete in `CLAUDE.md` (flusso editoriale, grafica brand, SEO, versione inglese, social) e in `.claude/rules/`.

### Compiti con immagini: cartella `bacheca/`

Per immagini generate e grafiche resta il sistema a file di `bacheca/` (protocollo in `bacheca/LEGGIMI.md`, modello in `bacheca/MODELLO.md`): un file per compito in `bacheca/compiti/`, consegne in `bacheca/consegne/`. Qui, in «Richieste», basta una riga che rimanda al compito.

Dal 13/10/2026 vale solo per i compiti già aperti in `bacheca/compiti/`: le immagini nuove (grafiche brand e immagini generate) le fa Claude con i propri strumenti e le controlla prima di pubblicarle (protocollo comune, § «Passaggio automatico a ChatGPT» → «Immagini»), e i nuovi passaggi a ChatGPT partono da `scripts/passa-a.py` (§ «Passaggi automatici in questo repository»). Nessun passaggio a mano per Alessandro.

### Controlli prima di unire una PR

- Build con Hugo 0.154.5 extended senza errori (`hugo --minify`).
- Il workflow «Controlli del sito» sulla PR verde (`scripts/controlli/controlla_sito.py`: link, immagini, video, CSP, registro dei dati, revisione sanitaria, news in uscita).
- Immagini nuove: `python3 scripts/ottimizza-immagini.py static/img/news` (crea i `.webp`); grafiche con cornice e filigrane come da `CLAUDE.md`, renderizzate e guardate prima di usarle.
- News: front matter completo (`description` specifica, `italianoSemplice`), fonti citate, link interni, data non futura se deve uscire subito.
- Dato aggiornabile nuovo (numeri, importi, leggi, contatti): aggiungilo a `data/dati_da_verificare.yaml`.
- Se cambi uno script inline, ricalcola gli hash della CSP (`hugo --minify` poi `python3 scripts/controlli/controlla_sito.py public --csp`).
- Dopo il deploy verifica la pagina live con `curl -L` (i 503 saltuari sono l'anti-bot di Aruba: riprova) e dai ad Alessandro il link.

### Passaggi automatici in questo repository

- Li avvia Claude con `python3 scripts/passa-a.py nuovo` (ramo `chatgpt/…`, voce in bacheca, PR in bozza, commento di avvio), li controlla con `passa-a.py stato` e li chiude con `passa-a.py chiudi --pr N` (commit riscritti a nome di Alessandro se serve, PR pronta, controlli verdi, squash merge, commenti dello strumento tolti dalla PR). Dettagli e criteri nel protocollo comune, § «Passaggio automatico a ChatGPT».
- Il commento `@codex …` è il solo riferimento allo strumento ammesso su GitHub, perché è il comando che avvia il lavoro, e `chiudi` lo toglie insieme alle risposte dello strumento. Titolo e descrizione della PR descrivono il lavoro senza nomi di strumenti (lo script si rifiuta di aprirla se ne trova uno); la richiesta per esteso sta in questa bacheca. Le revisioni automatiche di Codex sulle PR pronte restano visibili: dipendono da un'impostazione di Codex che solo Alessandro può cambiare, e per ora ha scelto di lasciarle (13/10/2026).
- Il merge su `main` pubblica il sito (`deploy.yml`): dopo `chiudi` si verifica che il deploy parta e finisca. Se la sessione che ha avviato il passaggio non lo chiude, lo chiude la prima sessione di Claude che apre questo repository, oppure la routine quotidiana di allineamento dei repository (`passa-a.py stato` → controllo del risultato → `chiudi`).

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

- **13/10/2026 — Claude.** Protocollo comune aggiornato con il § «Passaggio automatico a ChatGPT»: i passaggi li avvia Claude da sola con `scripts/passa-a.py` (ramo `chatgpt/…`, voce qui in «Richieste», PR in bozza, commento di avvio) e li chiude a nome di Alessandro. Nuove regole uguali in tutti i repository: `.claude/rules/firma-dei-lavori.md` (ogni lavoro a firma di Alessandro Cuollo o IU0QVW, identità git da `scripts/imposta-identita-git.sh`, hook `.githooks/commit-msg`) e `.claude/rules/autonomia.md`. Le immagini nuove le fa Claude; `bacheca/compiti/` resta per i compiti già aperti. Allineati `AGENTS.md`, `CLAUDE.md` e `bacheca/LEGGIMI.md`.
- **11/10/2026 — Claude.** Da oggi ChatGPT lavora fino alla pubblicazione anche sui file del sito, non solo in `bacheca/`, seguendo il protocollo comune qui sopra. `AGENTS.md`, `bacheca/LEGGIMI.md` e `CLAUDE.md` sono stati allineati.

## Archiviati

- Nessuna voce.
