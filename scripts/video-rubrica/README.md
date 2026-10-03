# Generatore dei video «Primo soccorso passo passo»

Crea i video verticali della rubrica (1080×1920, 30 fps, H.264 + AAC):
disegni animati in canvas, voce italiana sintetica (Piper), sottotitoli,
musica originale generata in codice (giro di Do, nessun diritto di terzi)
e, dove serve, la **simulazione a tempo delle compressioni** (110/min,
conteggio a voce da 1 a 30, musica allo stesso BPM).

## Come è fatto

| File | Cosa fa |
|---|---|
| `contenuti.py` | testi della 1ª serie (10 video): per ogni scena chip, titolo, voce, sottotitolo, etichette, disegno |
| `contenuti2.py` | 2ª serie (13 video) + speciale Giornata del volontariato |
| `contenuti3.py` | video dei servizi: accompagnamento sociale e «L'ultimo viaggio» (voce più lenta con `voce_lenta`, musica `dolce`) |
| `ill.js`, `ill2.js`, `ill3.js` | libreria dei disegni animati (`ILL[nome]({u, p, D, A})`) |
| `appro.src.html` | modello della pagina animata (impaginazione, sottotitoli, chiusura con la scheda contatti) |
| `musica.py` | base musicale originale: `musica.py DURATA out.wav [BPM] [base\|dolce]` (`dolce`: La min, senza percussioni) |
| `pipeline.py` | regia: voce → tempi → HTML → fotogrammi → mix audio → MP4 |
| `frames.js`, `anteprima.js`, `shot.js` | cattura con Chromium (video completo, foglio di anteprima, singoli fotogrammi) |
| `anteprima.sh`, `render.sh`, `copia.sh` | scorciatoie: anteprime, montaggio, copia nel sito |
| `articoli.py`, `articoli2.py` | generano le news programmate dai testi dei video (non sovrascrivono quelle esistenti) |
| `comune.py` | ffmpeg e scrittura prudente delle news |

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

Chromium: nelle sessioni cloud è già in `/opt/pw-browsers/chromium-1194/…`;
altrove indicare il percorso con `CHROME=/percorso/chrome`. Si possono
forzare anche `FF=/percorso/ffmpeg` e `PIPER_MODEL=/percorso/voce.onnx`.

## Uso

```bash
./anteprima.sh ictus infarto        # foglio con un fotogramma per scena: out/<chiave>/foglio.png
./render.sh ictus                   # video completo: out/primo-soccorso-ictus.mp4 (~6 min per video)
./copia.sh ictus                    # copia in static/video + copertina + grafica + .webp
```

Le chiavi sono quelle di `contenuti.py`/`contenuti2.py` (es. `rianimazione`,
`soffocamento-lattante`, `giornata-volontariato`).

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
`illN.js` (aggiungerlo in `pipeline.py` accanto a `ill2.js`) e le news con uno script
come `articoli2.py`. Contenuti sanitari: sempre verificati su linee guida ERC/IRC
correnti, e fatti rivedere da un istruttore prima dell'uscita.
