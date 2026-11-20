# Video 3D «Rianimazione: come funziona»

Video di 2 minuti e 25 secondi in due formati: **orizzontale 16:9** per la LIM, il proiettore e il sito (pagina
`/servizi/formazione/slide/`, accanto alle slide del corso BLSD adulto `scripts/formazione/slide/blsd-adulto.html`) e
**verticale 9:16** per i social (news `rianimazione-come-funziona`, che lo pubblica da sola su Facebook e Instagram).
La stessa pagina fa i due formati: `?formato=verticale` (fotogrammi.py `--parametri formato=verticale`);
`?pulito=1` toglie le scritte (immagine per la grafica della news). Grafica nazionale in ogni fotogramma: fascia blu
con filo giallo e stemma, firma «Misericordia di Ariccia», nota «SCHEMA · NON IN SCALA», cornice di microtesto.
Mostra il cuore e la circolazione, l'arresto cardiaco, che cosa fanno le compressioni (sostituiscono la pompa del
cuore e fanno arrivare il sangue al cervello), il DAE e le conseguenze (fratture di costole e sterno).
Fatto il 20/11/2026 con la skill `video-3d` (schema `render(t)`, impaginazione comune `IMP`, ente `misericordia`).

## Anatomia vera
Corpo, cuore (camere, valvole, coronarie), arterie e vene, polmoni, gabbia toracica, colonna e cervello vengono
dall'atlante **BodyParts3D** (© The Database Center for Life Science, licenza CC BY 4.0, modelli ricavati da
risonanze di una persona vera): <https://dbarchive.biosciencedbc.jp/en/bodyparts3d/>.
`anatomia.py` scarica l'atlante (circa 200 MB, solo la prima volta), raggruppa le parti, toglie dai vasi i volumi
del fegato, divide la parete dei ventricoli fra destro e sinistro, completa con un tubo morbido i tratti del collo
che l'atlante non ha (carotide comune → carotide interna, succlavia → vertebrale), calcola per ogni punto dei vasi la
distanza lungo l'albero dal cuore (serve al sangue che scorre) e salva `anatomia.json` (circa 16 MB, non versionato).

## Come si rifà
```bash
W=/tmp/lavoro-rcp; mkdir -p $W/bp3d
python3 scripts/video-3d-rcp/anatomia.py --cartella $W/bp3d --uscita $W/bp3d/anatomia.json   # pip: numpy scipy fast-simplification
# voce: frasi in voce/frasi.txt, poi voce.py della skill colonna-sonora (tempi fissati in sottotitoli.json)
bash scripts/video-3d-rcp/costruisci.sh $W/bp3d/anatomia.json voce/sottotitoli.json $W/rianimazione-3d.html
python3 $SKILL/motion-pc-genzano/scripts/fotogrammi.py $W/rianimazione-3d.html --webgl --processi 3 \
        --uscita $W/fotogrammi --controlli --jpeg --video $W/muto.mp4
python3 $SKILL/colonna-sonora/scripts/mixa.py voce/colonna.json --uscita $W/mix.wav --rapporto $W/mix.json \
        --video $W/muto.mp4 --video-uscita $W/rianimazione-come-funziona.mp4
```
`voce/` contiene il testo (`frasi.txt`), i tempi delle frasi (`sottotitoli.json`, fatto da `tempi.py` dopo `voce.py scegli`)
e la colonna sonora (`colonna.json`): voce **Damien** (XTTS-v2, `assistente-personale/strumenti/voce-riserva/voce_riserva.py`,
scelta di Alessandro del 20/11/2026; la sigla DAE si scrive «dì a è» perché la legga lettera per lettera), musica
(Kevin MacLeod, «Touching Moments Two – Higher», CC BY 4.0) ed effetti fatti in codice.
Le scene sono scritte su una scaletta fissa (inizio delle 22 frasi) e la pagina le allinea da sola alla voce vera;
battito, compressioni (110 al minuto) e flusso del sangue vanno in tempo reale.

## Il sangue che scorre
`anatomia.py` calcola anche i **percorsi del sangue** nei vasi veri (dal cuore a testa, braccia, pancia e gambe;
il ritorno dal collo, dalle spalle e dal bacino; la piccola circolazione fino ai polmoni e ritorno): globuli rossi con
ossigeno e blu senza, che scorrono con il battito, si fermano nell'arresto e ripartono con le compressioni.
L'atlante non ha le vene di braccia e gambe: il ritorno del sangue si vede dal tronco in su.

## Fonti
Linee guida RCP 2025 di Italian Resuscitation Council: cap. 4 «BLS adulto» (compressioni 5-6 cm, 100-120 al minuto,
rilascio completo, p. 8; le compressioni mantengono la perfusione cerebrale e le pause portano al danno ischemico,
p. 19; ogni minuto di ritardo della scarica riduce del 3-6% la sopravvivenza, p. 26; posizione delle piastre,
p. 30) e cap. 12 «Primo soccorso» (lesioni da RCP frequenti in chi è in arresto, soprattutto fratture di costole e
sterno; meno dell'1% di lesioni in chi non era in arresto, p. 24).
