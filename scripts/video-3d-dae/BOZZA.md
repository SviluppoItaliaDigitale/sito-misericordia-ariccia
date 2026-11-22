# Video 3D «Il DAE: com'è fatto» — bozza da approvare

Richiesta di Alessandro del 22/11/2026: il DAE scomposto in 3D, **sia Reel sia pagina del sito**, su un **DAE
generico** (semiautomatico, senza marca, dichiarato come illustrazione). Regola 1 della skill `video-3d`: testo e
scaletta vanno approvati prima della produzione.

Non ripete il video della rubrica del 12/1/2027 («Il defibrillatore (DAE)», `contenuti5.py`, che spiega **come si
usa**): questo mostra **com'è fatto** e perché funziona così, e rimanda a quello per i passi.

## Formati
- **Reel** verticale 1080×1920, circa 45 secondi, voce, musica bassa, sottotitoli; grafica nazionale in ogni
  fotogramma (fascia blu con filo giallo e stemma, firma «Misericordia di Ariccia», cornice di microtesto), nota
  «SCHEMA · NON IN SCALA» dall'inizio.
- **Pagina del sito** con lo stesso modello 3D: scorrendo, il DAE ruota e si apre nei suoi pezzi, con le
  spiegazioni accanto; animazioni dell'interfaccia con Motion; testo completo anche senza 3D.

## Scaletta e testo della voce

| # | Si vede | Voce (testo a schermo uguale) |
|---|---|---|
| 1 | Il DAE chiuso ruota piano, telecamera che si avvicina | Questo è un defibrillatore, il DAE. Vediamo com'è fatto dentro. |
| 2 | Si apre il coperchio; scheda «Accensione» sul pulsante | Alcuni si accendono da soli quando li apri, altri con un pulsante. |
| 3 | Vista esplosa: le due piastre escono dalla tasca, con il disegno di dove attaccarle e il cavo | Le due piastre adesive hanno dei sensori: leggono il ritmo del cuore. Il disegno ti dice dove attaccarle. |
| 4 | Si stacca l'altoparlante; onde sonore | L'altoparlante ti guida con la voce, passo dopo passo. |
| 5 | Si apre il guscio: la scheda elettronica si illumina, traccia del ritmo | Dentro, un piccolo computer analizza il ritmo e decide se serve una scarica. Mentre analizza, nessuno deve toccare la persona. |
| 6 | Si sfila la batteria | La batteria alimenta tutto: va controllata e cambiata quando serve. |
| 7 | Primo piano sul pulsante con il fulmine, che lampeggia | Se serve, il DAE ti chiede di premere il pulsante della scarica. Alcuni la danno da soli. |
| 8 | Le parti tornano al loro posto | La scarica ferma il tremito del cuore, così può ripartire con un battito efficace. Poi riprendi subito le compressioni. |
| 9 | DAE chiuso, invito | Impara a usarlo: corsi alla Misericordia di Ariccia. Chiama il 328 8105399. |

## Scheda di verità (regola qualità, punto 11)

| Voce | Che cosa deve essere vero in scena | Fonte |
|---|---|---|
| 1 | Il DAE è portatile, leggero e a batteria | NHLBI, «How Do Defibrillators Work», agg. 06/06/2023 |
| 2 | Accensione: alcuni all'apertura, altri con un pulsante | Video del DAE della rubrica, `contenuti5.py` (già verificato) |
| 3 | Le piastre sono **due**, adesive, con sensori che leggono il ritmo e poi portano la scarica; il disegno mostra la posizione: una sotto la clavicola destra accanto allo sterno, una sul fianco sinistro sotto l'ascella | NHLBI; IRC 2025, cap. 4, p. 30 |
| 4 | L'apparecchio dice a chi lo usa che cosa fare (istruzioni a voce) | NHLBI |
| 5 | Un computer interno analizza il ritmo e decide se serve la scarica; durante l'analisi nessuno tocca la persona | NHLBI; IRC 2025, cap. 4; `contenuti5.py` |
| 6 | La batteria alimenta il controllo del battito e la scarica; serve manutenzione, alcune batterie si cambiano ogni qualche anno | NHLBI |
| 7 | Nei semiautomatici si preme il pulsante della scarica, negli automatici la scarica parte da sola | `contenuti5.py` (già verificato) |
| 8 | La scarica ferma il tremito (fibrillazione) e il cuore può ripartire con un battito efficace; subito dopo si riprendono le compressioni | IRC 2025, cap. 4, p. 26 e p. 8 (forme corrette dal medico il 20/11/2026) |
| 9 | Numero dei corsi: 328 8105399 | `CLAUDE.md`, § «Telefoni» |

## Lasciato fuori, e perché
- **Condensatore** che accumula l'energia della scarica: per ora l'ho trovato solo su fonti commerciali, non su
  una fonte primaria. Si aggiunge solo se lo si verifica su una fonte primaria (norma tecnica, manuale ufficiale di
  un produttore, testo universitario).
- **Scadenza delle piastre**: non verificata su una fonte primaria in questa sessione.
- **Energia in joule, tensione, tempi di carica**: variano da modello a modello.

## Prossimi passi, dopo il sì di Alessandro
1. Modello 3D del DAE generico ricopiato dal vero (skill `ricopia-dal-vero`, foto di DAE con licenza libera su
   Wikimedia Commons come riferimento), con un controllo automatico che ferma il render se le piastre non sono due
   o se il disegno delle posizioni non coincide con IRC 2025, cap. 4, p. 30.
2. Provini con controlli, revisore video, agente `medico-emergenza` sulla scheda di verità.
3. Voce: Luca (ElevenLabs), con la pronuncia controllata sul DiPI («DAE» si legge «dì a è»), da far ascoltare ad
   Alessandro prima del render.
4. Render, mix, revisione finale; pagina del sito con lo stesso modello; news e post solo dopo l'approvazione.
