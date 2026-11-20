# Video 3D «Ictus: il tempo è cervello»

Video di circa 2 minuti in due formati: **orizzontale 16:9** per la LIM, il proiettore e il sito, **verticale 9:16**
per i social. Stessa catena e stessa grafica del video sulla rianimazione (`scripts/video-3d-rcp/`): fascia blu con
filo giallo e stemma, firma «Misericordia di Ariccia», nota «SCHEMA · NON IN SCALA», cornice di microtesto in ogni
fotogramma. La stessa pagina fa i due formati (`?formato=verticale`); `?pulito=1` toglie le scritte.
Fatto il 20/11/2026 con la skill `video-3d`; testi approvati da Alessandro il 20/11/2026.

Pensato per chi **non è sanitario** e per i volontari soccorritori: azioni scritte grandi e in ordine (i tre
controlli viso-braccia-parola, il 112, l'ora, che cosa non fare), le parole tecniche spiegate a schermo (coagulo,
emorragia, TAC) e alla fine il riepilogo da leggere con calma.

## Scene
Il cervello e il sangue (dal cuore su per le carotidi fino alle arterie del cervello, con i globuli che scorrono) →
che cos'è l'ictus (coagulo nell'arteria cerebrale media sinistra, globuli fermi, accenno all'arteria che si rompe,
la parte del cervello a valle che si scurisce) → il cervello comanda il corpo (zona della parola, zona del movimento
del braccio, emisfero sinistro → lato destro del corpo) → i tre controlli → 112 → l'ora → che cosa non fare (cibo,
acqua, farmaci, nemmeno l'aspirina; coagulo o emorragia lo dice solo la TAC) → il tempo è cervello (il coagulo si
scioglie e il sangue torna) → riepilogo, 112 e corsi BLSD.

## Anatomia vera
Dall'atlante **BodyParts3D** (© The Database Center for Life Science, CC BY 4.0). `anatomia_ictus.py` parte
dall'anatomia della rianimazione (`../video-3d-rcp/anatomia.py`: pelle, cuore, arterie e vene con i percorsi del
sangue) e aggiunge i due emisferi, il resto dell'encefalo, le arterie del cervello (carotidi interne, poligono di
Willis, cerebrali anteriori, medie e posteriori, basilare, vertebrali) con i percorsi del sangue catena per catena, e
tre zone dell'emisfero sinistro (parola attorno all'insula, braccio sul giro precentrale, faccia laterale servita
dall'arteria cerebrale media).
**Limiti dell'atlante:** ha solo l'arteria cerebrale media **destra** e solo il tratto iniziale (sfenoidale) con i
rami centrali, non i rami sulla corteccia. La sinistra si ottiene specchiandola, come fa l'atlante per molte parti
sinistre (file «…M»). Coagulo, emorragia, zone del cervello e anello della TAC sono disegni schematici (nota a schermo).

## Come si rifà
```bash
W=/tmp/lavoro-ictus; B=/tmp/lavoro-rcp/bp3d          # atlante e anatomia.json della rianimazione (vedi ../video-3d-rcp)
python3 scripts/video-3d-ictus/anatomia_ictus.py --cartella $B --base $B/anatomia.json --uscita $W/anatomia-ictus.json
# voce Damien (una alla volta): voce_riserva.py voce/frasi.txt riprese --riprese 2, poi voce.py scegli (colonna-sonora)
cd $W && python3 scripts/video-3d-ictus/voce/tempi.py colonna.json sottotitoli.json
bash scripts/video-3d-ictus/costruisci.sh $W/anatomia-ictus.json $W/sottotitoli.json $W/ictus-3d.html
python3 $SKILL/motion-pc-genzano/scripts/fotogrammi.py $W/ictus-3d.html --webgl --processi 3 --uscita $W/fo \
        --controlli --jpeg --video $W/muto.mp4
python3 $SKILL/colonna-sonora/scripts/mixa.py colonna.json --uscita mix.wav --rapporto mix.json \
        --video muto.mp4 --video-uscita ictus-come-funziona.mp4
```
Le animazioni sono legate all'inizio delle frasi e delle parole della voce (`sottotitoli.json`): cambiando la voce
la pagina si riallinea da sola. Voce **Damien** (XTTS-v2, `assistente-personale/strumenti/voce-riserva/`): il 112 si
scrive «uno uno due», TAC si scrive come si legge; ogni ripresa è controllata dal riconoscitore vocale.

## Fonti (verificate il 20/11/2026)
- Scheda «Ictus» del dossier di primo soccorso del sito (viso, braccia, parola; 112; l'ora; niente farmaci).
- IRC, Linee guida RCP 2025, cap. 12 «Primo soccorso», p. 14: scala per riconoscere l'ictus e chiamata subito.
- ISSalute, «Ictus» (aggiornata il 17/12/2025): coagulo che chiude un'arteria (circa l'80%) o arteria che si rompe;
  in ospedale subito TAC o risonanza.
- ISSalute, «Afasia»: l'ictus danneggia le aree del cervello che controllano il linguaggio.
- Manuale MSD, edizione per i professionisti, «Panoramica sulla funzione cerebrale» (revisione set. 2025, agg. gen. 2026): corteccia motoria primaria nel giro precentrale, lato controlaterale; area di Broca nella corteccia frontale posteroinferiore sinistra.
- Ministero della Salute, «La presa in carico riabilitativa nell'assistenza a lungo termine» (dicembre 2025): deficit
  motorio «nell'emilato corporeo opposto al lato della lesione cerebrale».
- SNLG Regione Toscana, «Ictus cerebrale: linee guida» (2013): p. 25 ora di inizio dei sintomi raccolta dai
  soccorritori; p. 26 in attesa dei soccorsi nessuna terapia a domicilio; p. 33 ora di esordio (± 30 minuti) fra
  gli obiettivi del primo inquadramento; p. 38 trombolisi entro una finestra di ore dall'esordio; p. 42 aspirina in
  ospedale, non nei candidati alla trombolisi.
