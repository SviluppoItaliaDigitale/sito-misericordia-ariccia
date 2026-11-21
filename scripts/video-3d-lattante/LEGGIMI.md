# Video 3D «Lattante: soffocamento e rianimazione»

Video per genitori, persone non sanitarie e volontari della Misericordia di Ariccia, nello stile dei video 3D già
pubblicati (rianimazione `scripts/video-3d-rcp/`, disostruzione `scripts/video-3d-disostruzione/`, infarto, ictus):
due formati dalla stessa pagina (orizzontale 16:9 e `?formato=verticale`), grafica nazionale in ogni fotogramma,
schede grandi per ogni azione. Iniziato il 20/11/2026 con la skill `video-3d`.

**Stato (21/11/2026):** modello, testi e scheda di verità approvati sanitariamente sui provini v3 (20/11/2026); voce
Damien registrata; pagina del video `lattante-3d.src.html` (quattro pose: in braccio con le vie dell'aria a schema, a
pancia in giù sull'avambraccio, a pancia in su sulle ginocchia, supino sul piano rigido con soffi, compressioni e DAE).

## File
- `lattante3d.js` — il lattante e le mani di chi soccorre, in three.js (vedi sotto).
- `provino-modello.src.html` — pagina dei provini: t 0-1 in piedi davanti, t 1-2 a pancia in giù sull'avambraccio,
  t 2-3 supino su un piano rigido con i due pollici sullo sterno; `?segno=1` mostra il segno giallo sullo sterno,
  `?vista=0..4` cambia la telecamera della terza posa (profilo, dall'alto, pollici da vicino, volto di fronte) e
  `?vista=1` della seconda (mano che sostiene il capo, da sotto).
- `lattante-3d.src.html` — la pagina del video (schema `render(t)`, impaginazione `IMP`, `?formato=verticale`,
  `?pulito=1`); `costruisci.sh SOTTOTITOLI.json MANI.json USCITA.html` la costruisce con `lattante3d.js` e le mani.
- `mani_makehuman.py` — scrive `mani.json` (avambracci e mani dell'adulto, mani e piedi del lattante) dai dati CC0 di
  MakeHuman: `python3 mani_makehuman.py CARTELLA_DATI mani.json` (scarica i tre file se mancano e controlla la licenza).
- `provino-mani.src.html` — provini delle mani (`?scena=pollici|aperta|pacche|capo|lattante`, `?vista=`, `?prova=dita`).
- `voce/frasi.txt` — le 18 frasi della voce (dopo `||` il testo a schermo, con le cifre); `voce/tempi.py` mette in fila le
  frasi (pause `DOPO`, le stesse della pagina) e scrive `sottotitoli.json` e `colonna.json` (voce, musica, effetti).
- `scheda-verita.md` — ciò che deve essere vero in scena, con fonte e pagina.

## Il modello: perché è fatto in codice
Ricerca del 20/11/2026 di un lattante libero scaricabile senza account:
- Sketchfab, «Baby» (darksoundlab) e «Baby (Fully Rigged)» (omermedia), CC BY 4.0: il download richiede un account
  (non creato, come da istruzione).
- Poly Pizza: la ricerca risponde 403 al lettore automatico; nessun modello verificabile.
- BodyParts3D: solo un adulto. MakeHuman: età minima circa 2 anni (`assistente-personale/memoria/risorse-3d.md`).
- GitHub (API di ricerca, «baby gltf», «infant 3d model», «baby obj model cc0»): nessun repository con un lattante in
  glTF/GLB/OBJ scaricabile; solo progetti di stima della posa e di immagini mediche.
Quindi il lattante è **costruito qui in three.js**, senza modelli di terzi (nessun credito da dare): forme morbide a
schema, articolate (collo, testa, spalle, gomiti, polsi, anche, ginocchia, caviglie), con le proporzioni di un
lattante di pochi mesi (testa grande, collo corto, arti corti), coperte dalla nota «SCHEMA · NON IN SCALA»; tutina azzurra come nelle figure IRC; occhi
aperti o chiusi (`espressione('sveglio'|'incosciente')`), mai il sorriso. Punti di riferimento per schede e gesti:
`giugulo`, `xifoide`, `sternoBasso` (centro della metà inferiore dello sterno), `scapole`, `mento`, `bocca`.
**Mani vere a cinque dita (21/11/2026, Alessandro: «Il corpo umano ha 5 dita per ogni mano»).** Avambracci e mani
dell'adulto, mani e piedi del lattante vengono dal corpo base di MakeHuman (repository ufficiale
makehumancommunity/makehuman, ramo master: `base.obj`, scheletro `default.mhskel` con le falangi, pesi
`default_weights.mhw`), tutti rilasciati **CC0** (pubblico dominio, nessun credito obbligatorio): solo i dati, nessun
codice di MakeHuman. `creaParteMH()` ne fa una SkinnedMesh con le ossa delle dita (`flessione`, `mira`); le pose sono in
`creaPoseMani()` (due pollici sulla metà inferiore dello sterno con le dita intorno al torace, mano delle pacche,
presa sulla mandibola). Il vecchio `creaMano` a forme non si usa più. Per trachea, polmoni, sterno e cuore nel video si userà BodyParts3D scalato e
dichiarato come schema (`scripts/video-3d-rcp/anatomia.py`), come negli altri video.

## Controllo automatico dello sterno
`controlloSterno(contatti)` di `lattante3d.js` (secondo parere del medico, 20/11/2026) restituisce un problema, nel formato
di `window.__controlli`, se il giallo non copre il 50% ± 2% del corpo dello sterno (dal punto medio 0,1465 alla fine
0,11) o se un punto di contatto dei pollici (`creaMano().contattoPollice()`) esce dalla metà inferiore; con
`fotogrammi.py --controlli` il render si ferma. Prova: `provino-modello.src.html?prova=fuori` sposta i pollici di 3 cm
verso i piedi e il controllo li segnala (contatto a y 0,090 invece di 0,120).

## Provini
```bash
SK=$(ls -d /root/.claude/skills/synced/*/video-3d | head -1); MP=$(ls -d /root/.claude/skills/synced/*/motion-pc-genzano | head -1)
python3 $SK/scripts/costruisci.py scripts/video-3d-lattante/provino-modello.src.html --uscita /tmp/provino.html \
        --ente misericordia --script scripts/video-3d-lattante/lattante3d.js
python3 $MP/scripts/fotogrammi.py /tmp/provino.html --webgl --tempi 0.5,1.5,2.5 --uscita /tmp/provini --jpeg
```

## Come si rifà il video
```bash
W=/tmp/lavoro-lattante; Q=scripts/video-3d-lattante; S=$(ls -d /root/.claude/skills/synced/*/motion-pc-genzano | head -1)
C=$(ls -d /root/.claude/skills/synced/*/colonna-sonora | head -1)
COQUI_TOS_AGREED=1 <venv>/bin/python assistente-personale/strumenti/voce-riserva/voce_riserva.py $Q/voce/frasi.txt $W/riprese
<venv>/bin/python $C/scripts/voce.py scegli $Q/voce/frasi.txt $W/riprese $W/voce
python3 scripts/video-3d-disostruzione/effetti.py $W/sfx          # stessi effetti fatti in codice della disostruzione
cp <musica.mp3 del video sulla disostruzione> $W/                  # Kevin MacLeod, «Touching Moments Two – Higher», CC BY 4.0
(cd $W && python3 $OLDPWD/$Q/voce/tempi.py)                       # sottotitoli.json e colonna.json
python3 $Q/mani_makehuman.py $W/mh-dati $W/mani.json
bash $Q/costruisci.sh $W/sottotitoli.json $W/mani.json $W/lattante-3d.html
python3 $S/scripts/fotogrammi.py $W/lattante-3d.html --webgl --processi 3 --uscita $W/f --controlli --jpeg --video $W/muto.mp4
python3 $C/scripts/mixa.py $W/colonna.json --uscita $W/mix.wav --video $W/muto.mp4 --video-uscita $W/lattante.mp4
```
Controlli automatici del render (`window.__controlli`): quelli dell'impaginazione, `controlloSterno()` (giallo, contatti di entrambi i
pollici dentro il giallo e polpastrelli a meno di 1 cm; prova `provino-mani?scena=pollici&prova=pollici`), `controlloDitaMH()` (cinque dita anatomiche in ogni mano e piede visibile: pollice con metacarpo e due
falangi, le altre con tre, medio il più lungo e mignolo il più corto; prova con `provino-mani?prova=dita`, che toglie
un dito e il controllo segnala «4 dita invece di 5»), `compenetrazione()` (nessuna nocca e nessun vertice della pelle di mano e avambraccio dentro il torace, tutti i vertici) e la mano
delle pacche mai sopra testa o collo (`posaProno`) e le due mani presenti durante le compressioni.

## Misure del torace (verificate il 21/11/2026)
All'altezza della metà inferiore dello sterno il modello misura: larghezza 13,2 cm, spessore 10,9 cm, circonferenza
circa 38 cm (`profiloTronco`, rx 0,066 e rz 0,055 m). Le misure reali sono:
- spessore antero-posteriore di circa 10,2 cm a 3,6 mesi di età media: Kao et al., Pediatrics 2009;124:49-55
  (PMID 19564282), dove un terzo dello spessore vale 3,4 cm;
- circonferenza alla linea dei capezzoli = 18,3735·ln(0,0012·peso_g + 2,1010), cioè 38,4 cm a 5 kg e 41,0 cm a 6 kg;
- rapporto spessore/larghezza di circa 0,6 a 0,4 anni, cioè una larghezza di circa 14-16 cm.
Le ultime due misure vengono da Seifnaraghi et al., BMC Res Notes 2022;15:206, licenza CC BY.
Il torace del modello è quindi nelle misure di un lattante di circa 5 kg. «10-11 cm» è lo spessore, non la larghezza.

## Soffi, DAE e pollici (21/11/2026, correzioni di medico, regista, formatore e Alessandro)
- **Soffi** (IRC 2025 cap. 9 p. 25, fig. 9): testa di chi soccorre dal corpo base MakeHuman CC0 (parte `testa` di
  `mani_makehuman.py`: viso, occhi, mascella, collo e spalle, colori per vertice; pelle più scura di quella del lattante;
  la maglia sotto il collo sfuma in pochi millimetri). `posaCapo()` la china sul lattante con la bocca aperta (larghezza
  lungo l'asse del viso del lattante) su bocca e naso e la fa scendere finché le labbra toccano senza entrare. Il torace si
  alza di 8 mm a ogni soffio (`uAlza`), con l'etichetta «Il torace si alza». Vista di lato, vicina.
  Controlli `soffi`: bocca e naso dentro l'apertura INTERNA delle labbra (parte centrale), apertura ≥ larghezza del naso,
  labbra a meno di 3 mm dal viso, nessun punto del volto dell'adulto dentro la testa del lattante. Prove:
  `?prova=soffi-lontano`, `?prova=soffi-dentro`; `?prova=fantasma` rende la testa trasparente per guardare le labbra.
- **DAE in due momenti** (p. 26, fig. 14), nell'ordine della voce: prima di fronte, sul piano, con la placca davanti
  (bordo a 2 mm a sinistra dello sterno, in basso sul torace, con un segno sottile sullo sterno); poi un solo giro lento
  (1,5 s, lattante sollevato, testa sempre a destra) e la placca dietro, al centro del dorso fra le scapole accennate.
  Una placca per volta, etichette solo a lattante fermo, braccia aperte; prima della scena seguente torna supino sul
  piano. Controlli `dae`: placca dietro sul dorso, sulla linea mediana (±4 mm), al centro fra le scapole, schiena verso
  la telecamera; placca davanti al suo posto e a più di 45 mm dall'asse del braccio. Prove `?prova=placca-fianco`,
  `?prova=placca-braccio`.
- **Pollici: mani 3D con la catena del pollice** (istruttore e coordinatore, 21/11/2026; sostituisce il disegno 2D,
  `disegnaMani2D` resta nel file ma non si usa). `posaDuePollici()` della pagina, prima la mano sinistra (la più stretta
  fra ascella e giallo), poi la destra con il polpastrello 7,5 mm più in là alla stessa altezza:
  1) palmo sul fianco (angolo 1,1-1,3 rad, mai sul davanti; altezza 0,075-0,08 sul bacino, fra il fondo della gabbia e
  la linea dei capezzoli); dita lunghe e appena curve lungo il fianco verso il dorso (`avvolgiDita`: nocca 15-30°,
  interfalangee 10-25°); polso entro ±70° perché l'avambraccio arrivi dai piedi;
  2) SOLO la catena del pollice (finger1-1, finger1-2, finger1-3) dentro gli angoli veri (CMC fino a 63-65°, MCP 0-60°,
  IP 0-79°): falange distale perpendicolare allo sterno; il **polpastrello vero** (`polpastrello()`, vertice più basso
  della falange distale) tocca la pelle verso la testa nel giallo (y 0,139), così la metà verso i piedi resta visibile;
  i pollici arrivano dai lati e convergono, punte affiancate a meno di 1 cm.
  Risultato (21/11/2026): polpastrelli a x −6,4 e +3,4 mm, y 136 e 135 mm (9,8 mm fra loro), da 0,5 mm nella pelle a
  0,7 mm sopra; falange distale a 12° dalla normale; CMC 62-63°, IP 74-75°; dita a 13 e 21 mm dal braccio del lattante.
  **Attenzione:** nelle ossa di MakeHuman la flessione verso il palmo è l'angolo **negativo** di `flessione()`; il vettore
  `p` di `vettoriMano()` è il **dorso** (prova del 21/11/2026). `ditaIntorno()` di `lattante3d.js` usa angoli positivi
  (dita in iperestensione) e non si usa più per i pollici; da correggere prima di riusarlo altrove.
  **Avambracci nudi** come nella fig. 11, niente maniche: la pelle sfuma nella trasparenza da 10 a 15 cm dal polso, così
  il taglio del modello non si vede mai. Telecamera dei due tratti: 3/4 dai piedi, 23° di lato verso chi soccorre,
  elevazione 53°, distanza 1,1 m (`POLLICI`; `?paz=`, `?pel=`, `?dpoll=`, `?yc=` solo per prove). La posa si calcola una
  volta per scena (circa 20 s per pagina) e si tiene in cache.
  Controlli in più: `controlloPolpastrelli()` (polpastrello al massimo 2 mm sopra la pelle; sul giallo con 5 mm di
  margine verso testa e piedi; proiettato dentro il contorno proiettato del giallo; punta del pollice non coperta da
  mani o torace; «cuore» = falangi distali a più di 30° fra loro; punte incrociate; **almeno il 30% del giallo visibile**,
  contato sui pixel della scena 3D su una griglia di 9 × 7 punti, **solo a torace fermo**: con un affondamento oltre il
  10% del massimo, 3,6 mm, non vale, perché i pollici affondano proprio lì), `controlloDitaAperte()` (flessione media
  delle quattro dita dentro i limiti, mai a pugno), dita a 12 mm almeno da ascella e braccio, fine dell'avambraccio
  sfumata o fuori quadro.
  Prove dei controlli, una per una (devono dare errore): `?prova=pollici-sdraiati`, `mani-ascelle`, `braccia-giu`
  (segnala le dita sul braccio; la distanza di 30 mm dalle manine non si attiva più con la posa attuale),
  `braccia-incrociate`, `manica-corta` (sfumatura oltre il taglio: «fine dell'avambraccio in vista e non sfumata»), `dita`
  («4 dita invece di 5»), `pugno`, `pollici-testa` (bersaglio 1,5 cm verso la testa), `cuore` (falangi distali 25° verso
  l'esterno: «34° fra loro»), `giallo-coperto` (mani spostate sopra il giallo a torace fermo: «giallo visibile solo al
  14%»). La posa della prima versione (v1) non era un «cuore» con questa definizione: falangi distali a 21,3° fra loro,
  punte a x +4,4 e −4,2 mm, non incrociate. Senza prova: nessun problema nei fotogrammi ogni 0,5 s di 55-72 s e 95-121 s.
- Schede dei passi 4-10 su due righe e più grandi; etichette con la linea di richiamo più grandi del 40%.
- Solo prove: `?cam={"c":[..],"p":[..]}`, `?capo={"a":..,"fc":..,"j":..}`, `?dbg=1`, `?paz=`, `?pel=`, `?dpoll=`, `?sd=`.

## Pose ricopiate dal vero (21/11/2026)
Pose confrontate con la skill `ricopia-dal-vero` (`confronta.py`, riferimento, render e sovrapposizione) alla stessa
angolazione di IRC 2025 cap. 9 fig. 11 (due pollici, `provino-mani?scena=pollici&vista=fig11`), della foto di riferimento
(`vista=alamy`) e di fig. 16a (pacche, `scena=pacche&vista=4`). Due pollici: avambracci che arrivano dai piedi e dall'alto,
palmi sui fianchi, dita intorno al torace, pollici obliqui verso la testa con le punte affiancate sulla metà inferiore
dello sterno. Pacche: per scelta del medico le dita vanno di traverso verso il fianco lontano (nella fig. 16a puntano
verso la testa), braccio di lato, mai sopra testa o collo. I riferimenti con diritti d'autore servono solo da guida.
Per provare varianti di posa: `provino-mani?...&pp={"rx":..,"h":[..],"p":[..],"t":[..]}` (solo prove).

## Voce
Damien con `assistente-personale/strumenti/voce-riserva/voce_riserva.py` (DiPI automatico, `pronuncia.tsv`); prima
della sintesi `controlla_pronuncia.py voce/frasi.txt` e l'agente `controllo-pronuncia`. Il 112 si legge «uno, uno, due»,
il 328 8105399 cifra per cifra. La voce si fa ascoltare ad Alessandro prima del render.

## Fonti
Linee guida RCP 2025 di Italian Resuscitation Council, cap. 9 «BLS pediatrico» (PDF del 02/04/2026):
<https://www.ircouncil.it/wp-content/uploads/2026/04/CAPITOLO_9-BLS_PEDIATRICO_02.04.2026.pdf>, pp. 6-7, 21-30, 63-64;
pagina per pagina in `scheda-verita.md`. Letto il 20/11/2026.

Note sulla voce (21/11/2026): rifatte con 4 riprese le frasi 2, 4, 5 e 13. Con «toràce» e «bène» scritti con l'accento
Damien aggiungeva una sillaba o storpiava la parola a fine periodo («toracei», «torash», «tossisce Wonderful»): nelle
riprese scelte «torace» e «bene» sono scritti senza accento (lettura piana corretta, trascrizione identica al testo) e
la frase 5, solo per la voce, ha la virgola al posto del punto («…del torace, con la mano…»).

## Revisione di regista e formatore (21/11/2026, voce nuova: 156-157 s, DOPO[15] da 2,6 a 3,6)
Le scene si indicano per frase della voce (`S[i]`, `E[i]`), non per secondi. In `lattante-3d.src.html`:
- **Pollici (frasi 8, 12-14):** polpastrelli di nuovo al centro del giallo (y 0,128, mai più in alto); telecamera più alta
  (62°) e più lontana (1,3 m), meno scorcio; due puntini rosati sulla tutina segnano la linea dei capezzoli (y 0,17).
  «giù di 1/3» è un riquadro 2D accanto al torace (freccia verticale, testo da 32-44 px), messo nel primo posto libero da
  corpo, braccia, mani e pannelli; controllo `marcatore`, prova `?prova=freccia-coperta`. Braccio sinistro del lattante
  abbassato a 1,75 rad nelle scene dei pollici, così la manina non finisce sotto scheda o contatore (controllo
  `pannelli`: nessuna scheda o contatore copre mani, piedi o testa del lattante). Avambracci senza sfumatura: oltre il
  taglio del modello continuano con un tronco di cono color pelle della stessa sezione, che si allarga verso il gomito ed
  esce dal quadro (controllo: fine dell'avambraccio fuori quadro; prova `manica-corta`). Dita: nocca 15-30°,
  interfalangee 10-25°, aperte di 0,11 rad fra un dito e l'altro. Grembo tolto (non si leggeva); mani via subito dopo
  l'ultima compressione (`RCP_B`, 0,45 s), prima del movimento verso il DAE (che parte a `S[15]` + 0,05 s).
  Non fatto: lattante inclinato di 10° a testa in giù sulle ginocchia (rischio per la posa calcolata).
- **Soffi (frase 11):** capelli corti castano scuro sul cuoio capelluto della testa MakeHuman (colori per vertice);
  telecamera più alta e lontana perché la testa non sia tagliata; il torace si alza di 11 mm con una luce tenue.
- **DAE (frase 15), sulle parole:** placca davanti da «se» di «se sei solo» fino a «e» di «e una sulla schiena»; giro di
  1,3 s da lì; placca dietro (fra le scapole, y 0,14) durante «sulla schiena» e la pausa; supino 0,25 s prima della
  frase 16. Il piano e l'ombra restano (lattante sollevato di 14 mm per girarlo). Placche più grandi (4,6 × 5,6 cm) con
  bordo giallo. Controllo `dae`: la placca detta dalla voce è nel quadro e non sotto un pannello.
- **Testi:** righe sotto delle schede e dei richiami almeno 30 px (la scheda si allarga se serve), testo del contatore
  30 px; parole dei sottotitoli non ancora dette con opacità almeno 0,74 (controllo `sottotitoli`); scheda 4: «compressioni
  forti e ben staccate». Bilanciamento delle due righe dei sottotitoli: non toccato (lo fa il motore dell'impaginazione).
- **Ultimo giro (21/11/2026):** telecamera dei pollici a 1,2 m (62°, spostata di 0,1); polpastrello 1 mm sopra la pelle a
  riposo; braccio destro del lattante a 1,75 rad nei soffi (la manina non va sotto la scheda 6); scheda 10 dopo il movimento
  della telecamera verso il DAE (S[15] + 1,15 s); DAE visto dall'alto (circa 74°) e vicino al torace, lattante spostato a
  sinistra delle schede. Placche: rettangolo bianco pieno ad angoli arrotondati (4,6 × 5,6 cm), bordo giallo, corto cavo.
  Etichette «Placca davanti» e «Placca dietro» in basso a destra, nello spazio libero. Testa di chi soffia: collo e maglia
  sotto il collo nascosti, telecamera più alta e lontana (testa intera).
  Controlli nuovi: `pannelli` (prova `?prova=pannelli`), `marcatore` (`?prova=freccia-coperta`), `dae` con l'area della
  placca detta dalla voce di almeno lo 0,4% del quadro (`?prova=placca-piccola`), `etichette` (etichette dei richiami mai
  sopra il corpo; prova con `?l1x=0&l1y=0`), `sottotitoli` (parole non ancora dette con opacità almeno 0,74).
- **Chiusura (21/11/2026):** la posa delle mani si calcola sempre con le braccia del lattante delle scene dei pollici
  (prima la cache dipendeva dal primo fotogramma reso: partendo dai soffi le dita della mano sinistra finivano a 11 mm dal
  braccio e il polpastrello destro fuori dal giallo, errore visto solo nelle prove a tratti); distanza dal braccio pesata
  di più nella scelta della presa (obiettivo 16,5 mm). Polpastrelli sul piano alla stessa distanza che sulle ginocchia:
  avvicinarli di 1 mm faceva le falangi a «cuore» (32°). DAE: telecamera un poco più lontana (`dd` 1,12, `dsh` 0,25) e
  piano ridotto al 62% dopo l'inizio della frase 15, così sotto la firma resta il fondo scuro. Controllo `firma`: sotto
  «Misericordia di Ariccia» al massimo il 3% di pixel chiari della scena 3D; prova `?prova=firma` (piano intero: 100%).
  Prove ogni 0,5 s: frasi 7-9 (50,5-75,4 s) nessun problema in 50 fotogrammi; frasi 10-16 (75,5-136,2 s) nessun
  problema in 121 fotogrammi.
- **Soffi, chiusura (21/11/2026):** testa di chi soccorre opaca, senza sfumature nella trasparenza (il collo finiva in un
  moncone sfocato); pelle, maglia e capelli fusi con pesi lisci sulla posizione a riposo: scollo a y 0,598, più alto
  dietro, sfumato su circa 8 mm; capelli sopra la fronte, sui lati sopra e davanti all'orecchio e dietro fino alla nuca,
  attaccatura sfumata su circa 1 cm, orecchie libere. Telecamera dei soffi vicina e bassa (`sax` 0,7, `say` 0,35, `saz`
  1,35, `sd` 0,48, `sy` 0): il profilo si legge (orecchio, guancia, naso, bocca su bocca e naso del lattante, capelli),
  la sommità della testa esce dal bordo in alto. Controllo `testa`: nessun vertice del bordo tagliato del pezzo (lati di
  un solo triangolo, sotto y 0,64) si vede davvero, cioè nel quadro e senza la testa, il lattante o il piano davanti
  (raggio dalla telecamera); prova d'errore `?sd=0.82&sy=0.12&sax=0.95&say=0.5&saz=1.25` (inquadratura larga: 79 punti).
  Prova ogni 0,5 s delle frasi 10-12 (75,5-100 s): nessun problema in 49 fotogrammi.
- **Braccia nelle altre scene (21/11/2026):** ogni braccio dell'adulto ha due aspetti, scelti per scena (`aspetto()`):
  «manica» (quello approvato: manica blu lunga e colore della manica sui vertici da 10 cm dal polso) in tutte le scene
  tranne i pollici, «nudo» (avambraccio nudo con la continuazione color pelle) solo sulle ginocchia e sul piano. La manica
  è lunga 1,8 m (prima 0,9): con i tempi della voce nuova la sua fine si vedeva a inizio frase 5. Gli angoli di riposo delle
  ossa si prendono alla costruzione (prima alla prima posa dei pollici: partendo dalle pacche la presa veniva sbagliata).
  Prova ogni 0,5 s di tutto il video (0-157,3 s): nessun problema in 315 fotogrammi.

