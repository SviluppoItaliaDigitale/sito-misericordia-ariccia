# Video 3D «Il DAE: com'è fatto» — testo approvato (22/11/2026)

Richiesta di Alessandro del 22/11/2026: il DAE scomposto in 3D, **sia Reel sia pagina del sito**, su un **DAE
generico** (semiautomatico, senza marca, dichiarato come illustrazione). Regola 1 della skill `video-3d`: testo e
scaletta vanno approvati prima della produzione.

Non ripete il video della rubrica del 12/1/2027 («Il defibrillatore (DAE)», `contenuti5.py`, che spiega **come si
usa**): questo mostra **com'è fatto** e perché funziona così, e rimanda a quello per i passi.

## Formati
- **Reel** verticale 1080×1920, circa 79 secondi (con la frase della memoria e l'avviso di sicurezza prima della scarica), voce, musica bassa, sottotitoli; grafica nazionale in ogni
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
| 5b | La scheda resta in vista; si illumina il chip della memoria | Alcuni registrano anche il ritmo del cuore e ciò che succede durante il soccorso, a volte pure l'audio. |
| 6 | Si sfila la batteria | La batteria alimenta tutto: va controllata e cambiata quando serve. |
| 7 | Primo piano sul pulsante con il fulmine; avviso «Nessuno tocchi la persona»; poi il pulsante si preme | Se serve, il DAE ti chiede di premere il pulsante della scarica. Prima controlla che nessuno tocchi la persona. Alcuni la danno da soli. |
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
| 5b | Alcuni DAE memorizzano ritmo ed eventi del soccorso; su alcuni modelli c'è anche la registrazione audio, opzionale e a tempo limitato (20 minuti AED Plus e AED Pro, 60 minuti AED 3). Si dice «alcuni», mai «molti» o «tutti»: le fonti sono di un solo fabbricante | Manuali ZOLL AED Plus, AED Pro, AED 3 (aggiunta chiesta da Alessandro il 22/11/2026) |
| 6 | La batteria alimenta il controllo del battito e la scarica; serve manutenzione, alcune batterie si cambiano ogni qualche anno | NHLBI |
| 7 | Nei semiautomatici si preme il pulsante della scarica, negli automatici la scarica parte da sola; prima della scarica nessuno tocca la persona (avviso a schermo mentre la voce lo dice, pulsante premuto dopo) | `contenuti5.py` (già verificato); IRC 2025, cap. 4; frase chiesta dal medico il 22/11/2026 |
| 8 | La scarica ferma il tremito (fibrillazione) e il cuore può ripartire con un battito efficace; subito dopo si riprendono le compressioni | IRC 2025, cap. 4, p. 26 e p. 8 (forme corrette dal medico il 20/11/2026) |
| 9 | Numero dei corsi: 328 8105399 | `CLAUDE.md`, § «Telefoni» |

## Lasciato fuori, e perché
- **Condensatore** che accumula l'energia della scarica: per ora l'ho trovato solo su fonti commerciali, non su
  una fonte primaria. Si aggiunge solo se lo si verifica su una fonte primaria (norma tecnica, manuale ufficiale di
  un produttore, testo universitario).
- **Scadenza delle piastre**: non verificata su una fonte primaria in questa sessione.
- **Energia in joule, tensione, tempi di carica**: variano da modello a modello.

## Voce
Luca (ElevenLabs) non disponibile il 22/11/2026: crediti dell'account a zero (le richieste rifiutate non costano). Voce di riserva Damien (XTTS-v2, licenza Coqui Public Model License, solo uso non commerciale; riga di licenza nella descrizione, mai nel video), approvata da Alessandro all'ascolto. Pronuncia controllata sul DiPI; «DAE» letto «dàe» (pronuncia.tsv); «Arìccia» con l'accento per la voce (sapere.it, De Agostini); numero letto a cifre.

## Revisione sanitaria (22/11/2026)
Prima lettura dell'agente `medico-emergenza`, tre correzioni, tutte fatte:
1. Il richiamo della seconda piastra puntava al riquadro vuoto del disegno: ora i richiami si calcolano dal disegno
   (`puntoDisegno`) e `problemiDisegno` ferma il render se un richiamo non punta al riquadro pieno giusto (prova:
   `?prova=scheda`).
2. Frase di sicurezza prima della scarica: riga 7 della scaletta e avviso «Nessuno tocchi la persona».
3. Tracciato della fibrillazione troppo regolare: ora irregolare, con ampiezza variabile.

## Pubblicazione (22/11/2026)
- Seconda lettura del medico: «APPROVATO SANITARIAMENTE» (piastra 2 spostata sul fianco sotto l'ascella, con il controllo
  anatomico `?prova=ascella`; tracciato irregolare).
- Revisore video: APPROVATO al secondo giro (fondo pieno dietro la firma; restano minori gli oggetti tagliati ai bordi
  nei primi piani). Controlli del render: nessun problema in 2424 fotogrammi; controllo `?prova=entro` sulle schede.
- Mix: musica «Morning» (Kevin MacLeod, CC BY 4.0), fruscio ai cambi di scena e colpo della scarica generati qui;
  -14 LUFS, voce sopra il fondo 23,7 dB.
- News `content/news/2026-11-22-dae-com-e-fatto.md`, video `static/video/dae-com-e-fatto-dentro.mp4` con `.vtt`.

## Voce rifatta (22/11/2026, dopo l'ascolto di Alessandro)
Dopo la pubblicazione Alessandro ha sentito «chesto», «scaricà» e il secondo «passo» con l'accento sbagliato. Frasi
1, 4, 5, 8 e 9 rifatte con le grafie scelte da lui all'ascolto fra più varianti: «Cuésto» (B), «skàrika» (B),
«pàsso dópo pàsso…» (C; va bene anche A, «pàsso dópo pàsso!»). Testo per la voce in `voce/frasi-voce.txt` (i
sottotitoli restano scritti normalmente). Video aggiornato solo sul sito, su sua richiesta; i post social restano quelli
del primo giorno. Il controllo della pronuncia (`controlla_pronuncia.py`) ora ferma le sdrucciole non risolte.

## Da fare
- Pagina del sito con lo stesso modello 3D, scorrendo (seconda parte della richiesta del 22/11/2026).
