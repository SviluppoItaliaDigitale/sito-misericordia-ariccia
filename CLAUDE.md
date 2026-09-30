# Misericordia di Ariccia — Sito web

## Stato attuale del deploy (aggiornato 2026-07-07)

Il sito è **LIVE** su `https://www.misericordia-ariccia.it/` (radice del dominio).
La fase anteprima è terminata il **6 luglio 2026**.

## Monitoraggio automatico — Liturgia del giorno

Questo repo ha un agente di monitoraggio pianificato (Claude Code web routine).
I parametri corretti da usare sono:

| Parametro | Valore CORRETTO | Valore OBSOLETO (da ignorare) |
|---|---|---|
| Workflow da controllare | `Pubblica su Aruba (LIVE)` | ~~Pubblica su Aruba (anteprima)~~ |
| File workflow | `.github/workflows/deploy.yml` | — |
| Pagina liturgia live | `https://www.misericordia-ariccia.it/liturgia-del-giorno/` | ~~`/anteprima/liturgia-del-giorno/`~~ |
| Cron deploy | `5 22 * * *` + `5 23 * * *` UTC (≈ 00:05 italiane tutto l'anno, doppio cron per l'ora legale) | ~~`30 0 * * *`~~ |

Se il prompt del monitoraggio cita ancora "anteprima", **ignora quel riferimento** e usa i valori corretti in questa tabella.

Inoltre c'è una **rete di sicurezza automatica**: il workflow
`.github/workflows/guardiano-liturgia.yml` controlla ogni mezz'ora, di
notte, che la pagina della liturgia mostri la data di oggi; se il rebuild
notturno è fallito per qualsiasi motivo, rilancia il deploy da solo e
riprova ogni 30 minuti finché la pagina non risulta aggiornata.

## Infrastruttura

- **Generatore**: Hugo 0.154.5 (extended)
- **Hosting**: Aruba (FTPS)
- **Deploy**: GitHub Actions — `.github/workflows/deploy.yml`
  - Trigger: push su `main`, schedule giornaliero (00:30 UTC), workflow_dispatch
- **Server-dir FTP**: `www.misericordia-ariccia.it/` (radice)

## Fonti dati Liturgia del giorno

- **Letture** (Evangelizo): `https://feed.evangelizo.org/v2/reader.php?date=AAAAMMGG&type=all&lang=IT`
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
  `python3 scripts/ottimizza-immagini.py static/img/news` (crea i `.webp`).
- **Cache**: `.htaccess` mette CSS/JS/font in cache un anno (nomi con
  impronta), immagini un mese, HTML mai.
- **Da fare fuori dal repo** (l'utente): Google Search Console e Bing
  Webmaster (inviare `https://www.misericordia-ariccia.it/sitemap.xml`),
  scheda Google Business Profile aggiornata con il sito, richiedere link
  dai siti di Comune di Ariccia, Confederazione Misericordie, ASL Roma 6.

## Riferimenti della Confederazione

- **Giallo Ciano** (rivista nazionale): pagina `/giallo-ciano/`, dati in
  `data/giallo_ciano.yaml`. Solo link al sito nazionale, niente copie dei
  PDF. Nuovo numero su https://www.misericordie.it/giallo-ciano/ → una voce
  in cima al file YAML.
- **8xmille alla Chiesa cattolica**: riquadro in `/sostienici/` e nel footer,
  logo ufficiale in `static/img/loghi/8xmille-chiesa-cattolica*.svg`, link a
  https://5xmille.8xmille.it/ («Due firme che fanno bene»).

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

Ricetta consolidata (vedi gli esempi in questa sessione: lancio sito e
Velletri Moda):

- **Palette**: navy `#1b223f` (fondo), ciano `#00a5dc`, giallo `#f2e433`.
- **Font locali** (`static/fonts/`, via `@font-face` con `file://`):
  Playfair Display 600 per i titoli, Jost per il resto.
- **Struttura**: badge giallo a pillola con evento/data → titolo Playfair
  (parole chiave in giallo) → foto dentro cornice ciano arrotondata con
  `object-fit: cover` + `transform: scale(1.1-1.25)` per **tagliare le
  bande bianche** delle foto WhatsApp → cartiglio sfumato con didascalia →
  eventuale fascia di ringraziamento → piede bianco con logo
  (`static/img/loghi/mise-triangolo.png`) e `www.misericordia-ariccia.it`.
- **Render**: HTML nello scratchpad → screenshot con Playwright
  (`playwright-core` + Chromium in `/opt/pw-browsers/chromium-*/chrome-linux/chrome`,
  attendere `document.fonts.ready`). NON usare lo screenshot CLI di
  Chromium (scatta prima del caricamento font/immagini).
- **Export**: JPEG qualità ~88 in `static/img/news/` (deve essere JPEG:
  è l'immagine che va anche su Instagram).
- **Controllare sempre il render** (Read del PNG) prima di pubblicare:
  contenuto che trabocca, testi tagliati, contrasti.

### 3. Social: pubblicazione AUTOMATICA (dal 30/09/2026)

- Dopo il deploy, `scripts/pubblica_social.py` pubblica da solo ogni news
  nuova sulla pagina Facebook MiseAriccia e su Instagram
  @confraternitamisericordia (registro `.github/social/pubblicati.json`,
  guida `docs/pubblicazione-social.md`). Non serve più preparare testi
  social né la vecchia pagina `/grafiche-social/` (eliminata).
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
