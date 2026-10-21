# Generatore dei video «Primo soccorso passo passo»

Crea i video verticali della rubrica (1080×1920, 30 fps, H.264 + AAC):
disegni animati in canvas, voce italiana sintetica (Kokoro, «Nicola»), sottotitoli,
musica (brani di Kevin MacLeod scelti da Alessandro, oppure la base originale
generata in codice) e, dove serve, la **simulazione a tempo delle compressioni**
(110/min, conteggio a voce da 1 a 30, musica allo stesso BPM).

Dal 21/10/2026 i video sono nello **stile nazionale** della Confederazione, con in
ogni fotogramma la firma «Misericordia di Ariccia» e la cornice di microtesto
(vedi «Stile nazionale, firma e cornice» qui sotto).

## Come è fatto

| File | Cosa fa |
|---|---|
| `contenuti.py` | testi della 1ª serie (10 video): per ogni scena chip, titolo, voce, sottotitolo, etichette, disegno |
| `contenuti2.py` | 2ª serie (13 video) + speciale Giornata del volontariato |
| `contenuti3.py` | video dei servizi: accompagnamento sociale e «L'ultimo viaggio» (voce più lenta con `voce_lenta`, musica `dolce`) |
| `ill.js`, `ill2.js`, `ill3.js` | libreria dei disegni animati (`ILL[nome]({u, p, D, A})`) |
| `riferimenti/livrea-ambulanza-facsimile.jpg` | fac-simile della livrea delle nostre ambulanze: `miseAmbulanza` in `ill3.js` è ricalcata da qui (non inventare livree) |
| `riferimenti/volontari-divisa.png` | riferimento per i volontari: SOLO la divisa giallo-ciano (blu, quella sanitaria; l'arancione è della protezione civile, settore non attivo: non usarla) con colletto e fasce giallo fluo, filetti argento, triangolo e bandiera (`volunteer()` in `ill3.js`, `bust(…,{divisa:true})` in `ill.js`) |
| `appro.src.html` | modello della pagina animata nello stile nazionale (fascia blu con filo giallo e stemma, firma, titolo con evidenziatore, sottotitoli, chiusura con la scheda contatti, cornice di microtesto) |
| `musica.py` | base musicale originale: `musica.py DURATA out.wav [BPM] [base\|dolce]` (`dolce`: La min, senza percussioni) |
| `musica/` | brani scelti da Alessandro (Kevin MacLeod, incompetech.com, CC BY 4.0): campo `brano` del video (`morning`, `touching-moments-two-higher`); di default `heartwarming`; i video con `bpm=110` (compressioni a tempo) usano `musica.py`. Ogni nuovo video va aggiunto a `data/musica_video.json` per il credito sotto il video e nei post |
| `kokoro_voce.py` | voce Kokoro scelta da Alessandro: **Nicola** (maschile) in tutti i video. «Sara» è scartata (legge male, senza intonazione); `voce='paola'` torna a Piper |
| `pipeline.py` | regia: voce → tempi → HTML → fotogrammi → mix audio → MP4 (con `--audio-da` rifà solo le immagini) |
| `frames.js`, `anteprima.js`, `shot.js` | cattura con Chromium (video completo, foglio di anteprima, singoli fotogrammi) |
| `anteprima.sh`, `render.sh`, `copia.sh` | scorciatoie: anteprime, montaggio, copia nel sito (con il segno di firma e cornice nella copertina) |
| `prova_impaginazione.py` (+ `.js`) | prova senza voce: un fotogramma intero per scena con in rosso la zona coperta dai comandi di Instagram e in verde la firma, in `out/<chiave>/prova.png`; si ferma (codice 1) se la firma manca, è sotto i 24 px, è coperta da una scritta o da un disegno, finisce nella zona di Instagram, se manca la cornice su un lato o se un'email o un sito va a capo a metà. Da usare quando si tocca `appro.src.html` o si scrive un video nuovo: titoli, etichette e sottotitoli devono restare fuori dalla zona rossa |
| `articoli.py`, `articoli2.py` | generano le news programmate dai testi dei video (non sovrascrivono quelle esistenti) |
| `comune.py` | ffmpeg, pagina animata (caratteri, loghi ufficiali dei modelli nazionali, motore di firma e cornice) e scrittura prudente delle news |

Prodotti e dipendenze locali finiscono in `out/`, `voce/` e `node_modules/` (esclusi da git).

## Prerequisiti (una volta per sessione)

```bash
cd scripts/video-rubrica
pip install piper-tts imageio-ffmpeg numpy        # voce, ffmpeg, audio
npm install                                        # playwright-core (versione fissata)
mkdir -p voce && cd voce                           # voce italiana «paola» (Piper)
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/it_IT-paola-medium.onnx
curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/it_IT-paola-medium.onnx.json
cd ..
```

Voci Kokoro (una volta per sessione; ~320 MB, in `kokoro/`, escluso da git):

```bash
python3 -m venv kokoro/venv && kokoro/venv/bin/pip install kokoro-onnx==0.4.9
H=https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main
curl -L -o kokoro/kokoro-v1.0.onnx $H/onnx/model.onnx
curl -L -o /tmp/if_sara.bin $H/voices/if_sara.bin && curl -L -o /tmp/im_nicola.bin $H/voices/im_nicola.bin
python3 -c "import numpy as n; n.savez('kokoro/voci-it.npz', **{k: n.fromfile(f'/tmp/{k}.bin', n.float32).reshape(-1,1,256) for k in ['if_sara','im_nicola']})"
```

Se la voce si ferma con «Error processing file '…/phontab'», la cartella dei dati di
espeak ha un percorso troppo lungo per espeak (succede nelle copie di lavoro con
percorsi lunghi): si crea un collegamento corto e lo si indica a espeak.

```bash
ln -sfn "$(kokoro/venv/bin/python -c 'import espeakng_loader as e; print(e.get_data_path())')" /tmp/esd
export ESPEAK_DATA_PATH=/tmp/esd
```

Chromium: nelle sessioni cloud è già in `/opt/pw-browsers/chromium-1194/…`;
altrove indicare il percorso con `CHROME=/percorso/chrome`. Si possono
forzare anche `FF=/percorso/ffmpeg` e `PIPER_MODEL=/percorso/voce.onnx`.

## Uso

```bash
./anteprima.sh ictus infarto        # foglio con un fotogramma per scena: out/<chiave>/foglio.png
./render.sh ictus                   # video completo: out/primo-soccorso-ictus.mp4 (~6 min per video)
./copia.sh ictus                    # copia in static/video + sottotitoli + copertina con il segno di firma e cornice + .webp (la grafica della news si fa col modello nazionale)
```

Le chiavi sono quelle di `contenuti.py`/`contenuti2.py` (es. `rianimazione`,
`soffocamento-lattante`, `giornata-volontariato`).

Per rifare **solo le immagini** di un video già montato (un cambio di stile o di
impaginazione), lasciando voce, musica e tempi come sono:

```bash
python3 pipeline.py anafilassi --audio-da ../../static/video/primo-soccorso-anafilassi.mp4
```

Prima di montare controlla che i tempi siano gli stessi (sottotitoli calcolati uguali al
`.vtt` accanto al video, durata entro 0,2 s), poi copia l'audio del video così com'è,
senza ricodificarlo. Un video per volta.

Per un singolo fotogramma di controllo (dopo un'anteprima o un render):
`cd out && KEY=ictus T=2:0.6,5:0.9 node ../shot.js` → `out/ictus/s0.png`, `s1.png`.

## Correggere un video

1. Modificare il testo in `contenuti*.py` (voce: numeri in lettere, «il uno uno due»;
   `sub`: il testo a schermo) o il disegno in `ill*.js`.
2. `./anteprima.sh <chiave>` e controllare `out/<chiave>/foglio.png`.
3. `./render.sh <chiave>`, guardare il video, poi `./copia.sh <chiave>`.
4. Se cambia la durata, aggiornare a mano la didascalia «Il video dura circa…» nella news.
5. Build Hugo, commit, PR (regole in `CLAUDE.md`).

Attenzione: se la news è **già uscita sui social**, il video pubblicato su
Facebook/Instagram resta quello vecchio (il sito si aggiorna, i post no).

## Una nuova serie

Aggiungere un `contenutiN.py` sul modello di `contenuti2.py` (campi `serie`, `num`,
`tot`; `bpm=110` e `conta=30` per una simulazione a tempo; `card` per cambiare la
scheda finale), importarlo in fondo a `contenuti.py`, creare i disegni mancanti in un
`illN.js` (entra da solo nella pagina, dopo `ill.js` e in ordine di numero: lo carica
`pagina()` di `comune.py`) e le news con uno script come `articoli2.py`. Se una scena chiede
un disegno che non c'è, `prova_impaginazione.py` e il montaggio si fermano con l'errore
«disegno mancante». Contenuti sanitari: sempre verificati su linee guida ERC/IRC
correnti, e fatti rivedere da un istruttore prima dell'uscita.

## Impaginazione per Instagram (dal 17/10/2026)

Nei Reels Instagram copre la fascia bassa (circa 380 px) e una colonna a destra (circa
150 px) con descrizione e pulsanti. I sottotitoli partono da 1300 px e sono larghi 820 px,
così anche con tre righe restano fuori; nello stile nazionale sono a 35 px e le etichette
a 30 px (Montserrat è più larga di Jost: con queste misure nessuna scena va a capo più di
prima). Prima di un video nuovo: `python3 prova_impaginazione.py <chiave>`.

## Stile nazionale, firma e cornice (dal 21/10/2026)

Regola di Alessandro del 21/10/2026: un solo stile, quello dei modelli nazionali, e in
ogni grafica la firma «Misericordia di Ariccia» con la cornice di microtesto (CLAUDE.md,
§ «2. Grafica brand»). La pagina animata parte dal modello «storia» 9:16 e usa solo il kit
nazionale, con i file di `scripts/grafica-brand/modelli-nazionali/`:

- fondo blu (`#003F85`, sfumato verso il blu notte ai bordi); in alto la **fascia blu con il
  filo giallo** e lo **stemma**, con la serie e il numero del video in Montserrat;
- sotto la fascia la **firma «Misericordia di Ariccia»** (30 px, bianca), sempre visibile;
- titolo bianco con la parola chiave nell'**evidenziatore** (`#013C7C`, testo `#FCF10C`),
  chip giallo (`#FCEB0C`), etichette blu con bordo giallo, sottotitoli su fondo blu notte;
- chiusura con la scheda contatti bianca (triangolo ufficiale, filo giallo in basso);
- **cornice di microtesto** lungo i quattro bordi, sopra a tutto: la incide il motore
  `scripts/grafica-brand/firma-e-cornice.js` (`corniceSovrapposta`), con lo stesso testo
  delle grafiche (nome, sito, «grafica della Confraternita di Misericordia di Ariccia ODV»,
  anno); si legge ingrandendo anche dopo la compressione del video.

I disegni (`ill*.js`) non cambiano: forme, posizioni, scritte e colori restano quelli
dei video già pubblicati. `prova_impaginazione.py` controlla firma e cornice in ogni
scena; `copia.sh` scrive nella copertina il segno che i controlli del sito cercano
(`rendi.py --segno`, solo se trova la cornice nei pixel). Restano nello stile di prima i
video già pubblicati, quelli dei servizi (`contenuti3.py`) e il video del 5×1000; la sua
copertina (`static/img/video/5x1000.jpg`, che compare anche nelle news del 5×1000 dal 2027)
ha firma e cornice aggiunte con `rendi.py --cornice`, come la grafica di quelle news.
