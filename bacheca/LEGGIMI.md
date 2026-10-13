# Bacheca Claude ⇄ ChatGPT

> **Nota del 13/10/2026, aggiornata il 14/10.** Questa cartella resta per i compiti già aperti in `bacheca/compiti/`; i nuovi passaggi a ChatGPT li prepara e li chiude Claude con `scripts/passa-a.py` secondo il protocollo comune di `COORDINAMENTO.md` (§ «Passaggio a ChatGPT»): Alessandro li avvia in Codex Cloud con il testo di avvio e, a lavoro finito, preme «Create PR».
> Le immagini nuove le fa Claude con i propri strumenti (`CLAUDE.md` § «Bacheca Claude ⇄ ChatGPT»): Alessandro non deve più caricare nulla a mano. Il resto di questo file descrive il sistema a compiti e resta valido per quelli.

Spazio di lavoro comune tra **Claude** (Claude Code) e **ChatGPT** (chat e Codex)
per il sito della Misericordia di Ariccia. Ci si scrive a vicenda **dentro i file
dei compiti**: chi apre un compito scrive le istruzioni, l'altro lavora e
risponde nello stesso file, il primo controlla. Alessandro fa da arbitro.

> **ChatGPT, se stai leggendo per la prima volta:** il punto d'ingresso è
> `COORDINAMENTO.md` nella cartella principale (protocollo comune). Per i
> compiti con immagini leggi tutto questo file,
> poi `CLAUDE.md` nella radice del repo (regole del progetto, valgono anche per
> te), poi apri i compiti in `bacheca/compiti/` con `stato: da-fare` e
> `assegnato: chatgpt`.

## Come è fatta

```
bacheca/
  LEGGIMI.md        ← questo protocollo
  MODELLO.md        ← modello da copiare per un compito nuovo
  compiti/NNN-titolo.md   ← un file per compito (istruzioni, consegna, controllo)
  consegne/NNN-…    ← immagini e file consegnati (JPEG/PNG/SVG/HTML)
```

## Ciclo di un compito

| Stato | Chi lo imposta | Significato |
|---|---|---|
| `da-fare` | chi apre il compito | istruzioni pronte |
| `in-lavorazione` | chi lo esegue | ci sta lavorando |
| `consegnato` | chi lo esegue | consegna in `bacheca/consegne/`, risposta scritta nel file |
| `da-rifare` | chi controlla | le note del controllo dicono cosa cambiare |
| `approvato` | chi controlla | va bene; può essere usato nel sito |
| `pubblicato` | chi lo mette nel sito | indicare dove (file e URL) |
| `annullato` | chi l'ha aperto | non serve più: non lavorarci |

Ogni passaggio si annota in fondo al file, nella sezione **Registro**, con data e
nome (`Claude`, `ChatGPT`, `Codex`, `Alessandro`). Non si cancella mai quello che
ha scritto l'altro: si risponde sotto.

## Chi fa cosa

- **Claude**: scrive le istruzioni, controlla le consegne (apre l'immagine e la
  guarda davvero), le integra nel sito (articolo, `static/img/news/`, social).
- **ChatGPT in chat**: legge la bacheca con il connettore GitHub, crea le
  **immagini generate** (illustrazioni, sfondi, scene) e aggiorna da solo i file
  **di testo** dei compiti (verificato il 9/10/2026). Non può caricare file binari:
  il JPEG lo carica Alessandro in `bacheca/consegne/` (github.com → cartella →
  *Add file* → *Upload files*) oppure lo passa a Codex.
- **Codex**: scrive direttamente nel repo con una PR. Aggiorna i file dei compiti
  (stato, consegna, registro) e può creare le **grafiche brand** con la ricetta
  di `CLAUDE.md` (HTML + Playwright → JPEG). A controlli verdi unisce la PR da sé
  (protocollo comune di `COORDINAMENTO.md`); Claude, quando c'è, la ripassa.
- **Alessandro**: decide, approva le pubblicazioni sul sito, carica le immagini
  della chat.

## Regole fisse per ChatGPT e Codex

1. Dall'11/10/2026 ChatGPT e Codex possono lavorare anche sui file del sito e
   **portare il lavoro fino alla pubblicazione** (PR unita su `main` a controlli
   verdi), seguendo il protocollo comune di `COORDINAMENTO.md` nella cartella
   principale e le istruzioni di Alessandro o di Claude.
2. Le eccezioni in cui non si unisce (contenuti sanitari, privacy, costi, bandi)
   sono in `COORDINAMENTO.md` § «Questo repository». I social escono da soli dopo
   il deploy: nessuna pubblicazione social a mano.
3. Nome dei file consegnati: `bacheca/consegne/NNN-descrizione.jpg` (NNN = numero
   del compito; versioni successive `-v2`, `-v3`). JPEG qualità ~88, massimo ~1 MB.
4. **Niente fatti, persone, loghi o dati inventati.** Niente volti realistici di
   persone vere, niente divise o mezzi spacciati per foto reali: un'immagine
   generata deve sembrare un'illustrazione, non una foto di cronaca.
5. Contenuti sanitari (primo soccorso, RCP): solo se il compito lo chiede, seguendo
   le linee guida ERC/IRC, e restano da far rivedere a un istruttore.
6. Se qualcosa non è chiaro, scrivi la domanda nella sezione **Consegna**, metti
   `stato: da-rifare` con `assegnato: claude` e fermati.

## Identità visiva (sintesi, il dettaglio è in `CLAUDE.md`)

- **Colori**: navy `#1b223f` (fondo), ciano `#00a5dc`, giallo `#f2e433`, bianco.
- **Font** (in `static/fonts/`): Playfair Display 600 per i titoli, Jost per il resto.
- **Formati**: post e articoli **1080×1350** (4:5); storie/Reel **1080×1920**;
  anteprima social del sito **1200×630**.
- **Logo**: `static/img/loghi/mise-triangolo.png` — nelle immagini generate **non**
  ridisegnarlo né imitarlo: lo aggiunge la grafica brand.
- **Stile**: concreto e del territorio (Ariccia, Castelli Romani, volontariato).
  Evitare il "look da AI": niente blob sfocati, gradienti viola, neon, icone
  generiche (vedi `.claude/rules/grafica.md`).
- Testo dentro le immagini generate: **no**, salvo richiesta. Lo aggiunge la
  grafica brand, così resta corretto e modificabile.

## Come chiedere a ChatGPT di lavorare (da copiare)

- In chat: *«Leggi `bacheca/LEGGIMI.md` nel repo sito-misericordia-ariccia e fai
  il compito NNN.»*
- In Codex: *«Segui `bacheca/LEGGIMI.md` e lavora il compito NNN: aggiorna il
  file del compito e la voce in `COORDINAMENTO.md`, e apri una PR che tocca solo
  `bacheca/` e `COORDINAMENTO.md`.»*
- Per consegnare un'immagine fatta in chat via Codex: allegala al task e scrivi
  *«Salvala come `bacheca/consegne/NNN-….jpg` e segna il compito consegnato.»*
