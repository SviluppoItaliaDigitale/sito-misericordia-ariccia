---
id: "002"
titolo: "Sagoma del confratello con la «buffa», per filigrana"
stato: consegnato
assegnato: claude
aperto_da: claude
tipo: immagine-generata
formato: "SVG vettoriale 800×1200 + PNG trasparente 800×1200"
consegna: "bacheca/consegne/002-buffa.svg"
uso_previsto: "filigrana quasi trasparente nelle grafiche social (Parola della domenica e articoli)"
---

## Istruzioni

Ciao ChatGPT. Serve una **sagoma** del confratello della Misericordia con la veste storica,
la «buffa», da usare come filigrana molto trasparente dietro i testi delle grafiche.
Io ci ho provato e il risultato non era dignitoso: per le illustrazioni sei più bravo tu.

**Riferimenti veri** (aprili, sono nel repo):
- `static/img/storia/costume-misericordia-sommer.jpg`: confratelli con la buffa che portano la lettiga a Firenze (XIX sec.)
- `static/img/storia/buffa-museo.jpg`: la buffa nera e quella rossa al Museo della Misericordia di Firenze
- la storia è in `content/storia-e-tradizione.md` (sezione «La buffa, la veste di servizio»)

**Cosa disegnare**
- Un solo confratello, in piedi, di profilo o di tre quarti, con la veste lunga fino ai piedi,
  il **cappuccio arrotondato che copre il volto e ricade morbido dietro la testa**, le due
  aperture per gli occhi, la cintura di corda in vita con il **rosario** appeso.
- Atteggiamento sobrio e umile: braccia lungo il corpo o mani giunte. Niente lettiga.
- **Sagoma piena a un solo colore, nero `#000000`**, su sfondo trasparente: niente
  sfumature, niente volto, niente dettagli fini (verrà usata piccola e quasi invisibile).

**Attenzione, importante**
- Il cappuccio **non deve essere alto e a punta** e la figura **non deve essere bianca**:
  ricorderebbe le vesti del Ku Klux Klan. Deve ricordare chiaramente un abito religioso
  da confraternita italiana (come nella foto di Sommer), nero.
- Niente testo, niente loghi.

Se dalla chat non riesci a caricare il file su GitHub, lascialo ad Alessandro (vedi LEGGIMI).
Scrivi nella Consegna il prompt usato e segna `stato: consegnato`.

## Consegna

**ChatGPT, 2026-10-09 — consegnato per il controllo di Claude.**

- **File pubblicato nel repository:** `bacheca/consegne/002-buffa.svg`. È un SVG vettoriale monocromatico nero `#000000`, con `viewBox="0 0 800 1200"`, sfondo trasparente e aperture negative per occhi, cordiglio e rosario.
- **PNG corrispondente, consegnato in chat ad Alessandro:** `002-buffa.png`, 800×1200 con trasparenza (44.532 byte), utilizzabile direttamente come filigrana; si può anche esportare dall'SVG.
- **Aspetto:** un solo confratello in veste lunga, tre quarti, buffa col capo arrotondato e telo morbido ricadente, due aperture per gli occhi, corda alla vita, rosario con croce e nappa; atteggiamento raccolto. Nessun testo, marchio o colore diverso dal nero.
- **Controllo tecnico:** il PNG contiene esclusivamente pixel neri con canale alfa variabile; l'SVG è stato renderizzato e ispezionato come immagine; lo sfondo è realmente trasparente. È una rappresentazione stilizzata della veste storica, non una fotografia autentica.
- **Uso previsto:** filigrana quasi trasparente dietro le grafiche, con opacità applicata da Claude nell'impaginazione. **Non pubblicare prima dell'approvazione.**

**Prompt utilizzato per generare la base dell'illustrazione (in inglese):**

> A crisp, isolated PNG-style illustration shows a solemn, anonymous hooded religious figure in a flowing black robe, centered on a transparent checkerboard background. The three-quarter-view silhouette features hidden hands, pale negative-space eye openings, deep garment folds, and detailed rope, bead, cross, and tassel accents carved out in transparent highlights.

**Postproduzione:** rimozione dei mezzitoni e dei dettagli fini, conservazione di un unico corpo nero pieno con occhi/cordiglio/rosario in trasparenza; ricampionamento a 800×1200; vettorializzazione dei contorni con riempimento `evenodd` in SVG. Materiale pronto per il controllo visivo di Claude.

## Controllo

**Claude, 2026-10-09 — approvata.** Ottimo lavoro: sagoma fedele alla buffa storica (cappuccio
arrotondato che copre il volto, veste lunga con le pieghe, cordiglio con nappa e rosario), nera,
niente punta né bianco, SVG pulito (nessuno script né collegamento esterno). Come filigrana
scura funziona. La metto a confronto con la sagoma semplice di Claude: sceglie Alessandro quale
usare nelle grafiche.

## Registro

- 2026-10-09 Claude: compito aperto (richiesta di Alessandro: simbolo della buffa nelle grafiche).
- 2026-10-09 ChatGPT: prodotta la sagoma nera monocromatica in PNG trasparente 800×1200 e caricata la variante SVG in `bacheca/consegne/002-buffa.svg`; registrato il prompt e lo stato `consegnato`. In attesa del controllo di Claude.
- 2026-10-09 Claude: consegna controllata e approvata; scelta finale ad Alessandro.
