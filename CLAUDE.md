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
- `assets/` — loghi e immagini
- `docs/` — documentazione di progetto

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
- **Export**: JPEG qualità ~88 in `static/img/news/` per il sito;
  PNG all'utente via SendUserFile per i social.
- **Controllare sempre il render** (Read del PNG) prima di pubblicare:
  contenuto che trabocca, testi tagliati, contrasti.

### 3. Testi social (scriverli in chat, non solo su file)

- **Facebook**: versione lunga con emoji, racconto, grazie, link
  all'articolo, CTA (assistenza eventi / volontariato / 5x1000).
- **Instagram**: versione corta, "link in bio".
- Hashtag standard: `#MisericordiaDiAriccia #Misericordie #CastelliRomani
  #Volontariato #GenteAlServizioDellaGente` + quelli dell'evento.
- 5x1000 quando pertinente: **C.F. 90031910582**.

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
