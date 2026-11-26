# Video 3D «Infarto: che cosa succede nel cuore»

Video di circa 2 minuti (122 s) in due formati: **orizzontale 16:9** per la LIM, il proiettore e il sito, **verticale
9:16** per i social. Va accanto al video «Rianimazione: come funziona» (`scripts/video-3d-rcp/`) e alle slide dei corsi
BLSD. È pensato per chi non è sanitario e per i nostri volontari: parole semplici, schede a schermo con le azioni
scritte grandi e in ordine. La stessa pagina fa i due formati: `?formato=verticale`; `?pulito=1` toglie le scritte;
`?zona=1` (solo per le prove) mostra sempre scura la zona del muscolo senza sangue.
Grafica nazionale in ogni fotogramma: fascia blu con filo giallo e stemma, firma «Misericordia di Ariccia», nota
«SCHEMA · NON IN SCALA», cornice di microtesto. Fatto il 20/11/2026 con la skill `video-3d`.

## Che cosa mostra
1. Il cuore è un muscolo: corpo intero, poi il cuore che batte.
2. Le coronarie vere dell'atlante (discendente anteriore, circonflessa, coronaria destra), con il sangue che le percorre.
3. Dentro la coronaria (tubo in scala, tagliato a metà): la placca che cresce nella parete.
4. La placca si rompe, il coagulo chiude l'arteria: i globuli si fermano davanti, oltre non arriva più sangue.
5. La parte del muscolo a valle del blocco (parete anteriore del ventricolo sinistro) si scurisce; orologio «il tempo è vita».
6. Come si riconosce: il centro del petto e le irradiazioni (braccio, spesso il sinistro, mandibola, schiena, stomaco),
   poi «spesso anche» (sudore freddo, nausea, fiato corto) e «segni più sfumati» (donne, anziani, diabete).
7. Che cosa fare, quattro schede grandi: 112 subito; seduta o sdraiata, restale accanto; aspirina da masticare se non
   è allergica e non l'ha già presa (a schermo, dopo la revisione del medico dell'emergenza del 20/11/2026: «150-500 mg,
   se non è allergica e non ha altre controindicazioni», IRC 2025 cap. 12 pp. 12 e 30); niente auto, l'ambulanza comincia le cure in viaggio.
8. In ospedale l'arteria si riapre (palloncino o farmaci) e il muscolo torna rosso.
9. Se il cuore si ferma: trema e non spinge, «non risponde e non respira normalmente? Compressioni e DAE».
10. Chiusura: riconosci, chiama il 112, resta con lei; corsi BLSD 328 8105399 oppure 06 933 3717.

## Anatomia vera e parti disegnate
Corpo, cuore e vasi vengono dall'atlante **BodyParts3D** (© The Database Center for Life Science, licenza CC BY 4.0):
<https://dbarchive.biosciencedbc.jp/en/bodyparts3d/desc.html>, preparato da `scripts/video-3d-rcp/anatomia.py`.
`anatomia_infarto.py` aggiunge le linee centrali delle tre coronarie (dall'origine sull'aorta), il punto del blocco
(al 30% della discendente anteriore) e, per ogni vertice delle pareti dei ventricoli, quanto dipende dal tratto a valle
(zona che si scurisce). **Placca, coagulo e globuli rossi nella coronaria non sono nell'atlante: sono disegnati** come
schema (nota «SCHEMA · NON IN SCALA»).

## Come si rifà
```bash
W=/tmp/lavoro-infarto; B=/tmp/lavoro-rcp/bp3d          # atlante e anatomia.json della rianimazione
python3 scripts/video-3d-infarto/anatomia_infarto.py --cartella $B --anatomia $B/anatomia.json --uscita $W/anatomia-infarto.json
# voce Damien: frasi lette (senza la parte dopo «||») con voce_riserva.py (assistente-personale/strumenti/voce-riserva),
# poi voce.py scegli della skill colonna-sonora (con faster-whisper) e, nella cartella di lavoro, voce/tempi.py
python3 scripts/video-3d-infarto/voce/tempi.py colonna.json sottotitoli.json
bash scripts/video-3d-infarto/costruisci.sh $W/anatomia-infarto.json $W/sottotitoli.json $W/infarto-3d.html
python3 $SKILL/motion-pc-genzano/scripts/fotogrammi.py $W/infarto-3d.html --webgl --processi 3 --uscita $W/f --controlli --jpeg --video $W/muto.mp4
python3 $SKILL/colonna-sonora/scripts/mixa.py colonna.json --uscita mix.wav --rapporto mix.json --video $W/muto.mp4 --video-uscita infarto-come-funziona.mp4
```
Le scene sono legate all'inizio delle 16 frasi della voce (`F(frase, frazione)`) e alle parole dette (`TP`: le schede
di braccio, mandibola, schiena e stomaco compaiono quando la voce le nomina).
Voce **Damien** (XTTS-v2, licenza Coqui Public Model License, solo uso non commerciale): il 112 si scrive «uno uno due»,
il DAE «dì a è»; la frase 11 è letta da «sdraiàre» (con l'accento grafico Damien diceva «sdragliare»), controllata con
Whisper medium. Musica: Kevin MacLeod, «Touching Moments Two – Higher», CC BY 4.0 (come la rianimazione). Effetti dalla
rianimazione (battito, passaggio, crepa, chiusura).

## Fonti (verificate il 20/11/2026)
- Istituto Superiore di Sanità, ISSalute, «Infarto del miocardio» (aggiornata il 17/12/2025):
  <https://www.issalute.it/index.php/la-salute-dalla-a-alla-z-menu/i/infarto-del-miocardio> — coronarie che portano il
  sangue al cuore; placche di grassi e colesterolo nella parete; la placca che si rompe forma un coagulo che blocca il
  flusso; sofferenza e morte di una parte del muscolo; intervento nel più breve tempo possibile; in ospedale
  angioplastica (catetere con «palloncino») o farmaci che sciolgono il coagulo.
- Linee guida RCP 2025 di Italian Resuscitation Council, cap. 12 «Primo soccorso», versione del 15/04/2026, p. 12 (dolore toracico: rassicurare,
  seduta o sdraiata in posizione comoda, acido acetilsalicilico masticabile 150-500 mg se non allergica, restare
  accanto) e p. 30 (sintomi diversi in un quarto delle donne; dolore epigastrico o fiato corto in chi ha il diabete).
- IFRC, International First Aid, Resuscitation and Education Guidelines 2025, «Chest pain», pp. 358-359 (112 subito
  anche se il dolore dura da pochi minuti; segni più sfumati anche negli anziani) e NHS, «Heart attack» (non andare in
  ospedale in auto), come nella news `content/news/*infarto*` del sito.
- Scheda «Infarto» del dossier del sito (`content/dossier/primo-soccorso.md`), verificata il 1/11/2026.
