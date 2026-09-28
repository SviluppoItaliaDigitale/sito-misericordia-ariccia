---
name: landing-premium
description: >-
  Costruisce landing page e pagine narrative "premium" (stile studio da
  diecimila euro) per QUALSIASI realtà o progetto — quelle già seguite
  (Protezione Civile Genzano di Roma, Misericordia di Ariccia ODV,
  Cooprimavera Soc. Coop.) e ogni nuova realtà, cliente o idea futura —
  con cinque tecniche codificate (exploded view 3D scroll-driven,
  scrollytelling cinematografico con immagini AI, video scrubbato dallo
  scroll, sciame di cubi WebGL, vetrina scura premium). Usare questa skill
  OGNI VOLTA che l'utente chiede una landing, una pagina "wow", una pagina
  scroll-driven, un teardown, uno scrollytelling, una pagina di reclutamento
  o presentazione, una pagina educativa d'impatto, una vetrina servizi o
  pagina preventivo d'impatto, un sito/pagina spettacolare per un progetto
  nuovo, o mostra/cita un video TikTok di siti spettacolari da replicare —
  anche se non nomina esplicitamente una tecnica né una realtà conosciuta.
---

# Landing Premium — per ogni realtà, presente e futura

Pagine narrative ad alto impatto. Profili brand pronti per le realtà già
seguite (PC Genzano, Misericordia di Ariccia, Cooprimavera); per ogni nuova
realtà o progetto si ricava il brand con la procedura in `references/brand.md`
(sezione «Nuove realtà»).
Ogni pagina è un **file HTML autonomo** (CSS+JS inline, vanilla), pensato per
essere pubblicato come pagina statica accanto ai siti esistenti, senza toccare
tema o navbar.

## Flusso di lavoro

1. **Scegli la storia, poi la tecnica.** La tecnica serve il contenuto, mai il
   contrario. Mappa rapida:
   - oggetto fisico da spiegare (zaino, ambulanza, mezzo, DAE) → **exploded view 3D**
   - racconto emotivo a capitoli (un intervento, una giornata del volontario) → **scrollytelling foto AI**
   - viaggio continuo (dal cielo alla strada, IT-alert, discesa/percorso) → **video scrubbato**
   - concetto astratto/dati (rete, sistema, ciclo) → **sciame di cubi / 3D astratto**
   - presentazione servizi + contatti → **vetrina scura premium**
2. **Leggi `references/brand.md`** e applica i token dell'organizzazione giusta
   (palette, font, tono di voce). Mai mescolare i brand tra loro. Se la
   realtà non ha ancora un profilo, seguine la sezione «Nuove realtà»:
   ricava i token da sito/logo/materiali reali (Firecrawl), non inventarli;
   in mancanza di tutto dichiara una direzione visiva propria (mai una
   palette di ripiego generica) e proponila prima di costruire.
3. **Leggi la sezione pertinente di `references/tecniche.md`** e costruisci
   sull'impianto comune (scroll → progress → pesi capitolo). Non reinventare
   lo scaffold: è già collaudato.
4. Se servono immagini o video fotorealistici, **non generarli e non
   bloccarti**: consegna la pagina funzionante con la resa 3D/di fallback e
   allega i prompt da `references/prompt-pack.md` per Gemini (immagini "Nano
   Banana", video Veo) o indica stock gratuito (Pexels/Pixabay). La pagina
   deve prevedere lo slot (`PHOTOS`/`VIDEO_SRC` a inizio script) per il
   drop-in successivo.
5. **QA finale obbligatoria** (sezione sotto), poi consegna un solo file
   `.html` + eventuale nota di 3-5 righe su cosa manca (asset, testi da
   validare).

## Vincoli duri (non negoziabili)

Ereditati dal progetto pcgenzano; per coerenza si applicano a TUTTE le pagine
di questa skill, per qualunque realtà (note e future):

- **MAI** proporre o implementare PWA, Service Worker, offline-first, web app
  installabili — in nessuna forma, nemmeno come suggerimento futuro.
- **Vanilla JS only.** Niente framework (React/Vue/ecc.). Three.js è ammesso
  in quanto libreria.
- Pagine **autonome**: nessuna modifica al CSS della navbar Bootstrap Italia,
  nessuna dipendenza dal tema Hugo. Se la pagina entra nel repo Hugo, va come
  layout/pagina standalone.
- `localStorage` sempre e solo dentro `try/catch` (meglio: non usarlo affatto
  in queste pagine).
- Niente PDF ospitati su servizi terzi.
- Apostrofi dritti (') nel front matter YAML se la pagina entra in Hugo.
- Contenuti operativi (procedure, dotazioni, dati storici) vanno **validati
  dal responsabile della realtà prima della pubblicazione** (coordinatore,
  committente o cliente a seconda del caso): consegnare sempre come bozza e
  dirlo esplicitamente.

## Qualità minima (QA da eseguire sempre)

- `prefers-reduced-motion`: animazioni ambientali spente o attenuate; lo
  scroll-driven resta (è controllato dall'utente) ma con smoothing più diretto.
- Etichette ancorate al 3D: sfondo **opaco** scuro, testo bianco, clamp dentro
  il viewport (mai testo fuori schermo o sopra colori illeggibili), nascoste
  se il punto è dietro la camera (`v3.z>1`).
- Mobile: rail di navigazione nascosta, card ancorate in basso, `pixelRatio`
  massimo 2, tipografia con `clamp()`.
- Contrasto: testo lungo mai sotto AA su fondo scuro; le "parole fantasma" in
  outline sono decorative e restano sotto il 15% di opacità.
- Fallback: la pagina deve avere senso anche se WebGL fallisce (testo dei
  capitoli leggibile); `<noscript>` con il contenuto essenziale.
- Un solo file, nessun asset obbligatorio esterno oltre a Google Fonts e
  cdnjs (Three.js r128: unica CDN garantita anche negli artifact Claude).

## Riferimenti

- `references/tecniche.md` — implementazione delle 5 tecniche con gli snippet
  chiave collaudati (scaffold scroll, exploded view, scrub video, sciame
  InstancedMesh, foto Ken Burns, illuminazione premium r128).
- `references/brand.md` — profili brand pronti (PC Genzano, Misericordia di
  Ariccia, Cooprimavera: palette, font, tono, CTA, storie) + procedura
  «Nuove realtà» (direzione visiva propria, niente palette di ripiego).
- `references/prompt-pack.md` — prompt pronti per immagini (Gemini/Nano
  Banana) e video (Veo) per le scene ricorrenti, più fonti stock gratuite.
