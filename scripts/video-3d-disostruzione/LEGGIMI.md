# Video 3D «Soffocamento: come si libera la gola»

Video per i corsi di primo soccorso e BLSD della Misericordia di Ariccia e per chi, senza essere sanitario, deve
aiutare in casa una persona che soffoca. Due formati dalla stessa pagina: **orizzontale 16:9** (LIM, proiettore,
sito) e **verticale 9:16** (`?formato=verticale`, social); `?pulito=1` toglie le scritte. Grafica nazionale in ogni
fotogramma (fascia blu con filo giallo e stemma, firma «Misericordia di Ariccia», nota «SCHEMA · NON IN SCALA»,
cornice di microtesto), come il video sulla rianimazione (`scripts/video-3d-rcp/`), di cui riusa schema e funzioni.
Fatto il 20/11/2026 con la skill `video-3d`.

## Che cosa mostra
1. Esofago (dietro) e trachea (davanti), l'epiglottide che chiude la trachea quando si deglutisce, il boccone che
   scende nell'esofago.
2. Il boccone che sbaglia strada e si ferma nella trachea: l'aria si ferma.
3. Adulto e bambino dall'anno in su: tosse, 112 in vivavoce, fino a 5 colpi tra le scapole (piegata in avanti),
   fino a 5 compressioni addominali (pugno fra ombelico e costole, in dentro e in su: il diaframma sale e l'aria
   spinge fuori il boccone), alternare 5 e 5, a terra e rianimazione se perde conoscenza, niente dita alla cieca,
   sempre dal medico dopo le compressioni addominali.
4. Lattante sotto l'anno: le vie aeree in 3D e i gesti disegnati a schema (5 pacche a pancia in giù sull'avambraccio
   con la testa più in basso; 5 compressioni con due pollici a pancia in su; alternare; 5 soffi e rianimazione se
   perde conoscenza); cibi tondi tagliati in pezzi piccoli.
Ogni azione ha la sua scheda numerata, grande, che resta a schermo per tutta la scena (indicazione di Alessandro: il
video serve a chi non è sanitario e ai volontari); i gesti dell'adulto sono anche disegnati di lato, con il conto
dei colpi e delle spinte.

## Anatomia
Pelle, trachea e bronchi, esofago, stomaco, lingua, palato molle, mandibola, osso ioide, polmoni, diaframma, gabbia
toracica, colonna, scapole, clavicole e cranio vengono dall'atlante **BodyParts3D** (© The Database Center for Life
Science, licenza CC BY 4.0): <https://dbarchive.biosciencedbc.jp/en/bodyparts3d/>. Epiglottide e cartilagini della
laringe (tiroide, cricoide) stanno solo nell'albero IS-A dell'atlante (file FJ2770, FJ2808, FJ2769).
Sono disegnati qui, e coperti dalla nota «schema»: il boccone, la gola (faringe, che l'atlante non ha: tubo
trasparente dietro la lingua), l'aria, i segni gialli sul corpo e i disegni a pittogramma dei gesti.
Nel modello l'esofago passa dietro la trachea (misurato da `anatomia_disostruzione.py`: a 1,39 m da terra la trachea
va da 9,6 a 11,0 cm in profondità, l'esofago da 8,9 a 9,8 cm).
Il corpo si piega in avanti nella pagina (rotazione del busto attorno alle anche; le braccia, staccate dal fianco
sotto il gomito nel modello, ruotano con il busto) e si sdraia per la rianimazione.

## Come si rifà
```bash
W=/tmp/lavoro-disostruzione; B=/tmp/lavoro-rcp/bp3d          # atlante già scaricato da scripts/video-3d-rcp/anatomia.py
# epiglottide e laringe dall'archivio IS-A (circa 140 MB): FJ2770, FJ2808, FJ2769 in $W/isa
python3 scripts/video-3d-disostruzione/anatomia_disostruzione.py --cartella $B --isa $W/isa --uscita $W/anatomia.json
# voce Damien (una alla volta), scelta delle riprese, tempi, effetti
COQUI_TOS_AGREED=1 <venv>/bin/python assistente-personale/strumenti/voce-riserva/voce_riserva.py voce/frasi.txt $W/riprese
python3 $SKILL/colonna-sonora/scripts/voce.py scegli voce/frasi.txt $W/riprese $W/voce
(cd $W && python3 .../voce/tempi.py)                     # sottotitoli.json e colonna.json
python3 scripts/video-3d-disostruzione/effetti.py $W/sfx
bash scripts/video-3d-disostruzione/costruisci.sh $W/anatomia.json $W/sottotitoli.json $W/disostruzione-3d.html
python3 $SKILL/motion-pc-genzano/scripts/fotogrammi.py $W/disostruzione-3d.html --webgl --processi 3 --uscita $W/f --controlli --jpeg --video $W/muto.mp4
python3 $SKILL/colonna-sonora/scripts/mixa.py $W/colonna.json --uscita $W/mix.wav --video $W/muto.mp4 --video-uscita $W/disostruzione-come-funziona.mp4
```
Voce **Damien** (XTTS-v2, licenza Coqui Public Model License, video non commerciale): il 112 si legge «uno uno due» e
i numeri di telefono cifra per cifra (`voce/frasi.txt`, dopo `||` il testo a schermo). Musica: «Touching Moments Two
– Higher» di Kevin MacLeod (incompetech.com), CC BY 4.0, come il video sulla rianimazione. Effetti fatti in codice
(`effetti.py`).

## Fonti
- Linee guida RCP 2025 di Italian Resuscitation Council, cap. 12 «Primo soccorso»
  (<https://www.ircouncil.it/wp-content/uploads/2026/04/CAPITOLO_12-PRIMO-SOCCORSO_15.04.2026.pdf>), p. 13
  (sequenza nell'adulto: «Sta soffocando?», incoraggiare la tosse, fino a 5 colpi interscapolari, fino a 5
  compressioni addominali, alternare, chiamare i soccorsi, niente esplorazioni alla cieca con le dita, RCP se non
  responsiva, valutazione medica dopo le compressioni addominali) e pp. 28-29 (la tosse genera pressioni elevate nelle
  vie aeree; colpi con il palmo tra le scapole; pugno tra ombelico e margine costale, trazione in dentro e in su,
  persona inclinata in avanti; le compressioni toraciche generano pressioni nelle vie aeree). Letto il 20/11/2026.
- ISSalute (Istituto Superiore di Sanità), «Tumore della laringe», pubblicata il 7/9/2026: la laringe sta sopra la
  trachea e, durante la deglutizione, l'epiglottide impedisce al cibo di entrare nelle vie respiratorie e lo
  convoglia verso l'esofago. Letta il 20/11/2026.
- Schede «Soffocamento» e «Soffocamento nel lattante» di `content/dossier/primo-soccorso.md` (lattante: pacche a
  pancia in giù sull'avambraccio con la testa più in basso, compressioni con due pollici, 5 soffi e rianimazione se
  perde conoscenza, cibi tondi in pezzi di circa mezzo centimetro).
- Linee guida RCP 2025 di Italian Resuscitation Council, cap. 9 «BLS pediatrico»
  (<https://www.ircouncil.it/wp-content/uploads/2026/04/CAPITOLO_9-BLS_PEDIATRICO_02.04.2026.pdf>), p. 25 (compressioni
  sulla metà inferiore dello sterno) e p. 29 (soffocamento nel lattante e nel bambino), figure 16 e 17 a p. 30. Letto il
  20/11/2026.

## Versione 2 (20/11/2026)
Solo ritocchi a schermo, voce invariata: «con la base del palmo» nei colpi; «persona inclinata in avanti» nelle
compressioni addominali, con la figura più piegata; nel lattante la gamba e le ginocchia di chi soccorre, «pancia in su
sulle tue ginocchia, più decise che nella rianimazione» e «metà inferiore dello sterno»; dopo il lattante la scheda
«Dall'anno in su si fa come nell'adulto» (pausa dopo la frase 19 portata a 4,6 s). Ogni voce e la sua fonte sono in
`scheda-verita.md`, da verificare sui fotogrammi ogni 0,5 s prima di pubblicare.
Voce: le pronunce sbagliate di Damien si correggono in `assistente-personale/strumenti/voce-riserva/pronuncia.tsv`
(qui: «boccóne», «tèsta», segnalate da Alessandro).
