# Misericordia di Ariccia — Sito web

## Stato attuale del deploy (aggiornato 2026-07-07)

Il sito è **LIVE** su `https://www.misericordia-ariccia.it/` (radice del dominio).
La fase anteprima è terminata il **6 luglio 2026**.

## Controllo automatico — Liturgia del giorno

Il controllo lo fa il workflow `.github/workflows/guardiano-liturgia.yml`,
senza intelligenza artificiale, quindi anche quando Claude è ferma. Ogni
mezz'ora, di notte (00:20-07:50 italiane con l'ora legale, 23:20-06:50 con
l'ora solare), verifica che la pagina
`https://www.misericordia-ariccia.it/liturgia-del-giorno/` sia di oggi e
completa: data di oggi, celebrazione del giorno (LitCal) e letture nel testo
CEI 2008. Se qualcosa manca rilancia il deploy («Pubblica su Aruba (LIVE)»,
`deploy.yml`) e riprova al giro dopo. Dalle 6 italiane, se la pagina non è
ancora completa, apre o aggiorna la issue «Liturgia del giorno: pagina
incompleta o non aggiornata» (label `automazione` + `fonte-rotta`), che si
chiude da sola quando la pagina torna completa.

La routine cloud «Monitoraggio Liturgia del giorno», che faceva gli stessi
controlli una volta al giorno con valori della fase di anteprima, è spenta
dal 21/10/2026.

## Verifica quotidiana dei dati (dal 9/10/2026)

Una routine cloud («Verifica dati sito Misericordia Ariccia», ogni mattina)
controlla sulle fonti ufficiali tutti i dati che possono cambiare (112 e
116117 nel Lazio, ASL Roma 6, leggi, importi, vaccini, statistiche, contatti),
elencati con file e fonte in `data/dati_da_verificare.yaml`. Corregge e
pubblica da sola i dati certi; quelli delicati o dubbi li mette nella issue
«Verifica dati: da controllare». Procedura: `docs/verifica-dati.md`.
**Quando aggiungi un dato aggiornabile al sito, aggiungilo anche al registro.**

## Controlli automatici del sito (dal 9/10/2026)

Dopo ogni deploy il workflow «Controlli del sito» (`.github/workflows/controlli.yml`,
script `scripts/controlli/controlla_sito.py`) ricompila il sito e aggiorna la issue
**«Stato del sito»**: link/immagini/video mancanti, CSP, registro dei dati, revisione
sanitaria, news in uscita (controllo editoriale `controllo_editoriale:` nel front matter
nei 3 giorni prima), pagine online e certificato FTPS. Gira anche su ogni PR.
Dal 21/10/2026 controlla anche la firma «Misericordia di Ariccia» e la cornice di
microtesto delle grafiche in uscita e dei modelli (§ «2. Grafica brand»; prova in
`scripts/controlli/prova_cornice.py`).
Blocca anche le **forme già corrette che non devono tornare** (`FORME_SBAGLIATE` nello
script, cercate nei sorgenti del sito e nei generatori di video, grafiche e post, cioè
`scripts/`, i sottotitoli in `static/` e le schede social, news programmate comprese): per esempio il motto si scrive
con «Iddio» («Che Iddio te ne renda merito»), come nello statuto tipo e nel glossario del
sito, mai «Che Dio…»; le schede della Parola della domenica hanno `preparata_da`
esattamente «Alessandro Cuollo, AAAA-MM-GG», mai il nome di uno strumento (21/10/2026). Quando si corregge un errore che potrebbe ripresentarsi, si
aggiunge la sua forma all'elenco, con i suoi esempi in `scripts/controlli/prova_forme.py`
(la prova del controllo, che gira con lui). Nello stesso workflow `scripts/controlli/prova_letture.py`
prova con un server locale i tentativi sulle fonti delle letture (`scarica()` in
`scripts/liturgia_cei.py`: 403, connessione chiusa, 404), usati da Liturgia del giorno e
Parola della domenica.
`.htaccess` ha una **CSP in sola osservazione** con gli hash degli script inline: se si
cambia uno script inline, ricalcolarli (`hugo --minify` poi `controlla_sito.py public --csp`).

## Guasti mai ignorati (dal 17/10/2026)

Istruzione di Alessandro: «gli errori 404 e simili non devono mai essere ignorati e devono
essere risolti». Due controlli aprono issue in-place con label `automazione` + `fonte-rotta`,
che si chiudono da sole al rientro: **«Link rotti sul sito»** (`controllo-link.yml`, ogni
mercoledì, lychee su tutti i link; run rosso per ogni 404/410 o file mancante) e **«Salute del
sito: automazioni in errore»** (`salute-sito.yml`, ogni giorno, workflow con l'ultimo run su
main fallito). Chi trova una di queste issue ripara la causa: URL nuovo solo se verificato con
una richiesta reale sulla fonte, altrimenti domanda ad Alessandro.

## Bacheca Claude ⇄ ChatGPT (dal 9/10/2026)

La bacheca è `COORDINAMENTO.md` nella cartella principale (protocollo comune,
uguale in tutti i repository; eccezioni e controlli di questo sito nella parte
«Questo repository»); istruzioni per Codex in `AGENTS.md`. Dall'11/10/2026
ChatGPT e Codex lavorano anche sui file del sito e uniscono da sé le PR a
controlli verdi, salvo le eccezioni scritte lì (contenuti sanitari, privacy,
costi, bandi). I push che toccano solo la bacheca (`bacheca/`, `AGENTS.md`,
`COORDINAMENTO.md`) non ripubblicano il sito.

- **Passaggi a ChatGPT: li prepara e li chiude Claude (dal 13/10/2026).**
  Niente più «guarda la bacheca» da aspettare: quando un lavoro va a ChatGPT,
  Claude lo prepara con `python3 scripts/passa-a.py nuovo` (ramo
  `chatgpt/<argomento>-AAAAMMGG`, voce in `COORDINAMENTO.md` § «Richieste» con
  la nota «preparata da Claude, da avviare a mano in Codex Cloud», PR in bozza
  con la richiesta nella descrizione) e riporta ad Alessandro il testo di
  avvio, con la richiesta intera. Ad Alessandro restano due gesti, perché il
  canale automatico `@codex` sulle PR per il suo account è muto e le vie a
  pagamento sono escluse: l'avvio in Codex Cloud (incolla il testo) e, a
  lavoro finito, «Create PR» nel task. La richiesta è sempre completa, nelle
  sette parti di `passa-a.py modello` (obiettivo, file, che cosa fare, vincoli,
  controlli, consegna, che cosa non fare): in Codex Cloud ChatGPT non può fare
  domande. Codex non unisce e non tocca la bacheca; Claude controlla il
  risultato (`passa-a.py stato`, immagini rese e guardate, controlli del
  repository) e chiude a nome di Alessandro con `passa-a.py chiudi --pr N
  --consegna M` (consegna portata nel ramo, commit riscritti se hanno un altro
  autore, voce di bacheca archiviata, PR pronta, controlli verdi, squash merge,
  commenti dello strumento tolti, deploy verificato). Criteri, costi e casi in
  cui non si passa nulla: `COORDINAMENTO.md` § «Passaggio a ChatGPT».
- **Immagini: le fa Claude.** Le grafiche raster (grafiche brand, locandine,
  immagini generate, JPEG per articoli e social) non passano più dalla chat di
  ChatGPT né da Alessandro: le fa Claude con i propri strumenti — la ricetta
  della grafica brand in questo file (§ «2. Grafica brand»), i blocchi di
  `scripts/grafica-brand/`, i connettori grafici della sessione quando ci sono,
  le opere e le foto con licenza libera — e le controlla aprendo davvero il
  render prima di pubblicarle. Alessandro non deve fare nulla a mano (sua
  istruzione del 13/10/2026: «io non devo fare nulla, devi fare tutto te in
  piena autonomia»). La cartella `bacheca/compiti/` (protocollo in
  `bacheca/LEGGIMI.md`, modello in `bacheca/MODELLO.md`) resta per i compiti
  già aperti; i nuovi passano da `passa-a.py`.
- **Regole comuni a tutti i repository**: `.claude/rules/autonomia.md` (piena
  autonomia, lavoro diviso fra agenti, domande ad Alessandro nei dubbi) e
  `.claude/rules/firma-dei-lavori.md` (ogni lavoro a firma di Alessandro Cuollo
  o del suo nominativo IU0QVW, mai di uno strumento: identità git impostata da
  `scripts/imposta-identita-git.sh`, hook `SessionStart` in
  `.claude/settings.json`, che attiva anche `.githooks/commit-msg`; nessun nome
  di strumenti in commit, PR, commenti e file pubblicati; squash merge con
  messaggio scritto).

## Parola della domenica sui social (dal 9/10/2026)

Ogni domenica alle 4:47 il workflow `parola-domenica.yml` pubblica su Facebook e
Instagram (solo social, nessuna pagina) un carosello (**sempre entro le 7:00**, poi iniziano
le Messe: dalla mezzanotte controlli ogni mezz'ora, dalle 4:47 alle 7 pubblicazione con giri
di riserva, dopo le 7 nulla, regola del 18/10/2026): copertina con una sola opera
d'arte di pubblico dominio **intera** (Wikimedia Commons) e una pagina per ognuno dei
versetti più significativi delle letture, con il nome della lettura ben visibile. Lo prepara il
mercoledì la routine cloud «Parola della domenica» (che riprova da giovedì a sabato e, se
serve, domenica all'1:55 con il «recupero notturno»): scheda in
`.github/social/parola/AAAA-MM-GG.json`, pagine in `static/img/parola/AAAA-MM-GG-N.jpg`, strumenti in
`scripts/parola-domenica/`. Procedura: `docs/parola-della-domenica.md`.

## Infrastruttura

- **Generatore**: Hugo 0.154.5 (extended)
- **Hosting**: Aruba (FTPS)
- **Deploy**: GitHub Actions — `.github/workflows/deploy.yml`
  - Trigger: push su `main`, schedule giornaliero (22:05 e 23:05 UTC: una delle due cade alle 00:05 italiane in ogni stagione), workflow_dispatch
- **Server-dir FTP**: `www.misericordia-ariccia.it/` (radice)

## Fonti dati Liturgia del giorno

- **Letture (testo principale, CEI 2008 letto a Messa)**: `https://www.chiesacattolica.it/liturgia-del-giorno/?data-liturgia=AAAAMMGG`,
  scaricate al deploy da `scripts/liturgia_cei.py` in `data/liturgia_cei.json` (non versionato).
  Uso consentito dalle note legali CEI (scopo formativo, non commerciale, testo integrale, fonte citata).
- **Letture (ripiego, CEI 1974)** (Evangelizo): `https://feed.evangelizo.org/v2/reader.php?date=AAAAMMGG&type=all&lang=IT`
  — usate solo se la CEI non risponde.
- **Calendario liturgico** (LitCal): `https://litcal.johnromanodorazio.com/api/dev/calendar/nation/IT/AAAA?year_type=CIVIL`

> Nota: questi feed sono bloccati dal proxy dell'ambiente di monitoraggio cloud.
> Il check dei feed va fatto con `curl` senza proxy oppure verificando i log del workflow GitHub Actions.

## Struttura contenuti Hugo

- `content/liturgia-del-giorno.md` — pagina della Liturgia del giorno
- `content/news/` — notizie
- `content/servizi/` — servizi offerti
- `assets/` — CSS, JS e librerie (Hugo Pipes: bundle unico minificato con
  impronta nel nome; vedi `assets/README.md` e `layouts/_default/baseof.html`)
- `static/img/` — loghi e foto (con copia `.webp` accanto a ogni jpg/png)
- `static/fonts/` — font auto-ospitati (woff2)
- `scripts/ottimizza-immagini.py` — ricompressione JPEG + creazione `.webp`
- `docs/` — documentazione di progetto

## SEO e performance (audit settembre 2026)

- **Titoli**: `titoloSeo` nel front matter = titolo per Google/social (con
  luogo e servizio), l'H1 in pagina resta `title`. `description` sempre
  presente e specifica. `immagine` nel front matter = anteprima social
  (default: `static/img/og-default.jpg` 1200×630).
- **Schema.org**: NGO+LocalBusiness e WebSite in home; BreadcrumbList
  ovunque; NewsArticle nelle news; Service nella sezione servizi e nelle
  pagine con `servizio: "Nome del servizio"` nel front matter; FAQPage.
- **Immagini**: le immagini Markdown passano dal render hook
  `layouts/_default/_markup/render-image.html` (WebP se esiste, width/height,
  lazy tranne la prima). Dopo aver aggiunto foto o grafiche nuove lanciare
  `python3 scripts/ottimizza-immagini.py static/img/news` (crea i `.webp`;
  lavora solo sulle immagini senza `.webp`, non ricomprime le `*-grafica.jpg`
  e non cancella nulla; `--prova` mostra cosa farebbe).
- **Cache**: `.htaccess` mette CSS/JS/font in cache un anno (nomi con
  impronta), immagini un mese, HTML mai.
- **Da fare fuori dal repo** (l'utente): Google Search Console e Bing
  Webmaster (inviare `https://www.misericordia-ariccia.it/sitemap.xml`),
  scheda Google Business Profile aggiornata con il sito, richiedere link
  dai siti di Comune di Ariccia, Confederazione Misericordie, ASL Roma 6.

## Versione inglese (`/en/`)

- Ogni pagina in `content/en/` dichiara la sua pagina italiana nel front matter
  con `traduzione: "/percorso"` (es. `en/formazione.md` → `"/servizi/formazione"`):
  da lì hreflang e selettore 🌐 collegano le due versioni (`partials/controparte.html`).
- Nelle pagine `/en/` menu (`[[menus.en]]` in `hugo.toml`), annunci (solo voci
  con `testo_en` in `data/annunci.yaml`), footer, briciole e strumenti JS
  (accessibilità, ricerca, lettura vocale, modulo trasporti) sono in inglese.
  La lingua si legge da `partials/lingua.html` (template) e da `<html lang>` (JS).
- Quando si cambia un testo importante in italiano (costi, privacy, bandi),
  aggiornare anche la pagina inglese corrispondente.
- Tradotte tutte le pagine tranne news, Liturgia del giorno e le pagine
  spagnola/rumena. I dossier inglesi stanno in `content/en/dossier/` con
  `type: "dossier"`; i servizi in `content/en/servizi-*.md` con `type: "servizi"`.
  I video restano in italiano (didascalie con «video in Italian»).

## Riferimenti della Confederazione

- **Giallo Ciano** (rivista nazionale): pagina `/giallo-ciano/`, dati in
  `data/giallo_ciano.json`. Solo link al sito nazionale, niente copie dei
  PDF. **Controllo automatico ogni sera** (`.github/workflows/controlla-giallo-ciano.yml`
  + `scripts/controlla_giallo_ciano.py`): i numeri nuovi vengono aggiunti da
  soli (online col rebuild notturno) e segnalati con una issue GitHub; i link
  rotti aprono la issue «Giallo Ciano: link da controllare».
- **Modelli grafici nazionali** (webinar sulla comunicazione del 2026): rifatti
  identici in `scripts/grafica-brand/modelli-nazionali/`; quando si usano lo dice
  § «2. Grafica brand».
- **8xmille alla Chiesa cattolica**: riquadro in `/sostienici/` e nel footer,
  logo ufficiale in `static/img/loghi/8xmille-chiesa-cattolica*.svg`, link a
  https://5xmille.8xmille.it/ («Due firme che fanno bene»).

## Rubrica «Primo soccorso passo passo» e contenuti a orario

- **Video**: generatore in `scripts/video-rubrica/` (guida nel suo `README.md`):
  testi in `contenuti*.py`, disegni in `ill*.js`, `./anteprima.sh`, `./render.sh`,
  `./copia.sh`. Serie 1 (10 video, 6/10–6/11), serie 2 (13 video, 10/11–22/12),
  speciale Giornata del volontariato (5/12). Contenuti sanitari sempre su linee guida
  ERC/IRC correnti e rivisti da un istruttore. Dal 21/10/2026 i video in uscita (dal 23/10)
  sono nello stile nazionale (fascia blu con filo giallo e stemma, Montserrat, colori del
  kit), con la firma «Misericordia di Ariccia» e la cornice di microtesto in ogni
  fotogramma: `prova_impaginazione.py` le controlla, `copia.sh` mette nella copertina il
  segno (`rendi.py --segno`) che «Controlli del sito» cerca nelle copertine dei video in
  uscita; per rifare solo le immagini di un video già montato, `pipeline.py <chiave>
  --audio-da <video.mp4>`. Restano come sono i video già pubblicati, quelli dei servizi e
  il 5×1000.
- **Dossier** `content/dossier/primo-soccorso.md` (23 schede): ogni scheda può avere
  `dal: "AAAA-MM-GG"` → il suo video (`static/video/primo-soccorso-<id>.mp4`) e il link
  all'articolo compaiono da quella data; prima c'è l'avviso «esce il …».
  `riconosci_tit` cambia il titolo «Come riconoscerlo».
- **Shortcode `video`**: parametro `dal="AAAA-MM-GG"` per mostrarlo solo da quella data.
- **News in evidenza**: `in_evidenza_fino: "AAAA-MM-GG"` nel front matter → riquadro
  grande in cima a `/news/` dal giorno di uscita fino a quella data compresa (intanto
  esce dalla griglia). Calendario attuale: soffocamento lattante 20–23/11,
  rianimazione bambino 24/11–4/12, speciale volontariato 5–31/12.
- **Home**: dal 5 al 31/12/2026 il callout volontari diventa lo speciale con il video
  (date in `layouts/home.html`, blocco «Callout: diventa volontario»).
- Tutte le date contano dalla **mezzanotte italiana** (`time.AsTime … "Europe/Rome"`):
  il cambio avviene col rebuild notturno, senza toccare nulla.
- **5x1000 ricorrente**: video `static/video/5x1000.mp4` (anche in `/sostienici/`) e
  news già programmate ogni anno l'11 maggio (inizio dichiarazioni) e il 15 settembre
  (ultimi giorni del 730), dal 2027 al **2030**, ognuna in evidenza fino a fine mese e
  pubblicata da sola sui social. Prima del 2031 crearne altre sullo stesso modello.
- **Musica dei video**: brani di Kevin MacLeod (CC BY 4.0) scelti da Alessandro, in `scripts/video-rubrica/musica/`; crediti in `data/musica_video.json` (mostrati sotto il video e nei post social). Solo i video della rianimazione a tempo usano la musica generata. Voce: Kokoro «Nicola» (maschile) in tutti i video; la femminile «Sara» è scartata (legge male, senza intonazione).
- **Video dei servizi**: accompagnamento sociale (`/servizi/servizi-sociali/`) e
  «L'ultimo viaggio» (`/trasporto-infermi/`), testi in `contenuti3.py`.
- Social: `social_video` + `social_video_copertina` nel front matter → Reel su
  Instagram e video su Facebook; `social_testo` per il testo su misura.

## FLUSSO EDITORIALE — foto + testi → articolo, grafica e social

Quando l'utente invia **una foto** (e/o un link di stampa, una locandina,
una descrizione di evento), il lavoro atteso è SEMPRE questo, senza che
debba rispiegarlo:

### 1. Articolo sul sito (`content/news/AAAA-MM-GG-slug.md`)

- Front matter: `title`, `date`, `slug`, `description` **unica e specifica**
  (mai quella di default del sito), `italianoSemplice` (frasi brevi, parole
  facili — c'è in ogni contenuto del sito).
- Se c'è un articolo di stampa: leggerlo (WebFetch), usare solo fatti
  verificati, **citare la fonte** con link in corsivo in fondo.
- Prima immagine dell'articolo = **la grafica brand** (mai la foto grezza:
  le foto WhatsApp hanno bande bianche): diventa automaticamente l'og:image.
- Alt text descrittivo su ogni immagine; link interni alle pagine correlate
  (`/assistenza-eventi/`, `/diventa-volontario/`, `/servizi/formazione/`…);
  CTA finale; quando si ringrazia qualcuno chiudere con il motto
  **«Che Iddio ve ne renda merito»**.
- Attenzione: Hugo **non pubblica** contenuti con data futura (escono col
  rebuild notturno, pochi minuti dopo la mezzanotte italiana).

### 2. Grafica brand (1080×1350, per articolo e social)

**Un solo stile, quello nazionale (dal 21/10/2026).** Istruzioni di Alessandro:
«facciamole identiche», «le grafiche in automatico devono essere utilizzate sia
da te che da altre AI», «deve essere tutto coerente». Lo stile della casa era
nato quando mancava un riferimento nazionale; ora c'è, con i webinar sulla
comunicazione della Confederazione pubblicati su YouTube.

- **Modelli**: i modelli grafici della Confederazione, rifatti identici per
  Ariccia in `scripts/grafica-brand/modelli-nazionali/` (catalogo in
  `LEGGIMI.md`): post con foto e fascia, anche come grafica delle news; storia;
  testimonianza; carosello; Save the date; assemblea dei soci; biglietto da
  visita; carta intestata. Si riempiono e si salvano con la skill
  `grafiche-modelli-nazionali` (`python3 .claude/skills/grafiche-modelli-nazionali/rendi.py`),
  che controlla testi, loghi, caratteri, segnaposti e foto di prova. Si usano
  identici: colori e caratteri del modello, niente cornici decorative, filigrane
  o altri loghi. L'unica aggiunta è la firma con la cornice di microtesto (punto
  qui sotto).
- **Firma «Misericordia di Ariccia» e cornice di microtesto in ogni grafica (dal
  21/10/2026).** Alessandro: «metti in ogni slide, documento grafico eccetera
  sempre Misericordia di Ariccia! Altrimenti ci rubano la grafica!! e se riesci
  anche un microtesto come filigrana ai bordi a mo' di cornice». Ogni modello ha
  la firma fissa (elemento `data-firma`): `rendi.py` si ferma se manca, se è
  troppo piccola (5 punti in stampa, 24 px nei formati social larghi 1080 px,
  16 px negli altri), se è trasparente o se una scritta la tocca. Ogni grafica
  esce con la cornice di microtesto lungo i bordi (nome, sito, «grafica della
  Confraternita di Misericordia di Ariccia ODV», anno): nei JPEG e PNG la incide
  il motore
  `scripts/grafica-brand/firma-e-cornice.js`, con il tono adattato al fondo,
  invisibile da lontano e leggibile ingrandendo; nei PDF da stampa è testo
  vettoriale dentro il margine (`<meta name="microtesto">` del modello). Il
  motore scrive nel file anche un segno che i controlli del sito cercano: lo
  devono avere le grafiche delle news e le pagine della Parola che escono dal
  22/10/2026. Per le grafiche fatte in altro modo (copertine dei video, Canva,
  altre AI) c'è `rendi.py --cornice FILE`, che aggiunge la cornice e, con
  `--firma basso-sinistra`, la firma su un fondo libero (si ferma se sotto c'è
  un disegno o una scritta). Le grafiche già pubblicate restano come sono.
- **Se nessun modello va bene**: si parte dal modello più vicino e si usano
  solo gli elementi del kit nazionale, cioè i colori (blu `#003F85`, giallo
  `#FCEB0C`, azzurro `#009FE3`, evidenziatore `#013C7C`), il carattere
  Montserrat, la fascia blu con il filo giallo e lo stemma, il triangolo nei
  caroselli e sulla carta, con i loghi ufficiali della cartella dei modelli.
- **Foto in bianco e nero solo per un lutto** (Alessandro, 21/10/2026: «quelle in
  bianco e nero sui social vengono utilizzate per commemorare la morte di
  qualcuno»). Le foto a colori restano a colori. In bianco e nero vanno solo
  nelle grafiche in ricordo di una persona morta: confratelli e consorelle,
  volontari, benefattori, chi ha fatto parte della vita della Misericordia e i
  personaggi pubblici che le sono stati vicini, dal Papa in giù; anche
  anniversari della morte, vittime di una tragedia, commemorazione dei defunti
  del 2 novembre. Si chiede con `"lutto": true` nei dati: diventa grigia solo
  la foto, mentre fascia, colori, stemma e testi restano istituzionali.
  `rendi.py` si ferma se il testo ricorda una persona morta e il dato manca.
  Le foto nate in bianco e nero, come quelle d'archivio, restano come sono.
- **5×1000**: le grafiche ufficiali della campagna nazionale, già compilate per
  Ariccia, così come sono. Quelle della campagna 2026 («Non servono superpoteri.
  Servi Tu.») sono `static/img/news/5x1000-ambulanza.jpg`, `-compagnia.jpg`,
  `-emporio.jpg` e `-spesa.jpg`. Per un anno nuovo si controlla prima se la
  Confederazione ha pubblicato la campagna di quell'anno e si usa quella,
  cambiando solo il codice fiscale. Non sono modelli ufficiali `5x1000-grafica.jpg`
  (una scena del video del 5×1000) e `5x1000-quadrato.jpg` (grafica fatta qui, con
  il vecchio dominio), entrambe nello stile precedente: restano nelle news che le
  usano già, ma non si prendono a modello.
- **Grafica di una news**: `static/img/news/AAAA-MM-GG-<slug>-grafica.jpg`, JPEG
  qualità 88 (deve essere JPEG: va anche su Instagram), poi
  `python3 scripts/ottimizza-immagini.py static/img/news`. È la prima immagine
  dell'articolo e l'anteprima sui social.
- **Render** solo con Playwright, dopo `document.fonts.ready` (lo fa `rendi.py`);
  mai lo screenshot da riga di comando di Chromium, che scatta prima che
  caratteri e immagini siano caricati.
- **Controllare sempre il render** aprendolo prima di pubblicare: testi
  tagliati, ritaglio della foto, contrasti.
- **Stile precedente**, fino al 20/10/2026: navy `#1b223f`, Playfair Display e
  Jost, cornice dorata e filigrane (blocchi in `scripts/grafica-brand/cornice.html`
  e `filigrane.html`). Resta nelle grafiche già pubblicate e, finché non passa
  allo stile nazionale, nella «Parola della domenica». Non si usa per grafiche
  nuove.

### 3. Social: pubblicazione AUTOMATICA (dal 30/09/2026)

- Dopo il deploy, `scripts/pubblica_social.py` pubblica da solo ogni news
  nuova sulla pagina Facebook MiseAriccia e su Instagram
  @confraternitamisericordia (registro `.github/social/pubblicati.json`,
  guida `docs/pubblicazione-social.md`). Non serve più preparare testi
  social né la vecchia pagina `/grafiche-social/` (eliminata).
- **L'app Meta «Sito Misericordia Ariccia» deve restare in modalità Live**
  (developers.facebook.com → app → Pubblicazione). In modalità Sviluppo tutto
  ciò che pubblica l'API risulta pubblicato ma lo vedono solo gli amministratori
  dell'app: è successo dal 30/9 al 4/10/2026 (post e Reel invisibili agli altri).
  Se «solo io lo vedo», controllare prima questo.
- **Facebook, news con video**: post con link all'articolo **più** un Reel
  caricato con la **Reels API** ufficiale (`/video_reels`, tre fasi; registro
  `facebook_reel`). Mai `/videos`: quei video diventavano Reel non distribuiti,
  visibili solo agli amministratori (4/10/2026). Limite Reel via API: 90 s.
- Tutti i post escono con il luogo **Ariccia** (Facebook `place`, Instagram
  `location_id`; vedi `docs/pubblicazione-social.md`).
- Il testo del post è `description`/sommario della news; per un testo
  su misura usare `social_testo:` nel front matter; `social: false` per
  non condividere. 5x1000 quando pertinente: **C.F. 90031910582**.

### 4. Pubblicazione

- Build di verifica con Hugo 0.154.5 (se manca: `CGO_ENABLED=0 go install
  github.com/gohugoio/hugo@v0.154.5` — le release GitHub sono bloccate dal
  proxy, il Go module proxy no).
- Commit sulla branch designata → push → **PR** → l'utente storicamente
  approva con "mergia / vai live"; per correzioni di problemi da lui
  segnalati si può mergiare direttamente.
- Dopo il deploy (workflow "Pubblica su Aruba (LIVE)", ~1 minuto):
  verificare la pagina live con `curl` (i 503 intermittenti sono
  l'anti-bot di Aruba: riprovare). **HTTPS è attivo dal 15/07/2026**
  (certificato dedicato, redirect http→https gestito dal proxy Aruba):
  usare `curl -L` o direttamente `https://`.
- **SEMPRE, nel messaggio finale all'utente**, indicare in modo ben
  visibile i link cliccabili:
  l'**URL dell'articolo live** appena pubblicato
  (`https://www.misericordia-ariccia.it/news/<slug>/`) e, se il deploy
  ha già girato, i post usciti su Facebook e Instagram.
