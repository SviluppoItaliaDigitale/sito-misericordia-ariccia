---
name: grafiche-modelli-nazionali
description: Fa le grafiche della Misericordia di Ariccia con i modelli della Confederazione nazionale, identici agli originali (post 4:5 con foto e fascia, storie, testimonianze, caroselli, Save the date, assemblea dei soci, biglietto da visita, carta intestata). Riempie i campi, salva JPEG, PNG o PDF con la firma «Misericordia di Ariccia» e la cornice di microtesto, e controlla testi, loghi, caratteri e segnaposti. Usala per ogni grafica, post, storia, carosello, invito, ricordo di un defunto, biglietto o lettera della Misericordia di Ariccia, anche quando la richiesta non nomina i modelli nazionali, e per mettere firma e cornice a una grafica fatta in altro modo.
---

# Grafiche della Misericordia con i modelli nazionali

Cosa fa: compila i modelli grafici nazionali di `scripts/grafica-brand/modelli-nazionali/` e li salva alle misure giuste, fermandosi quando qualcosa non va.
Origine: skill scritta per Alessandro Cuollo il 21/10/2026 insieme ai modelli (sue istruzioni: «facciamole identiche», «le grafiche in automatico devono essere utilizzate sia da te che da altre AI»). Vale per Claude, ChatGPT e Gemini: Codex la trova in `.agents/skills/`.

## Prima di cominciare

1. **Un solo stile.** Dal 21/10/2026 tutte le grafiche della Misericordia seguono il marchio nazionale (`CLAUDE.md`, § «2. Grafica brand»). Se nessun modello va bene, parti dal più vicino e usa solo gli elementi del kit nazionale: colori, Montserrat, fascia, stemma e triangolo ufficiali. Mai la cornice dorata o le filigrane dello stile precedente.
2. **Scegli il modello** nel catalogo di `scripts/grafica-brand/modelli-nazionali/LEGGIMI.md`; i campi di ciascuno con `python3 .claude/skills/grafiche-modelli-nazionali/rendi.py --elenco`.
3. **Testi.** Brevi e nel tono della Misericordia: caldo, concreto, mai retorico. Il testo lungo va nell'articolo o nella didascalia, non nella grafica. Ogni dato ha una fonte: numeri, email e indirizzi da `hugo.toml` (`[params]`), date e luoghi dal documento o dalla persona che li ha dati. Niente frasi attribuite a qualcuno che non le ha dette.
4. **Foto.** Foto vere della Misericordia, con i permessi. Mai pazienti o persone assistite riconoscibili, mai dati sanitari, targhe, indirizzi o dettagli dei servizi; volontarie e volontari in primo piano solo con il loro consenso; minori mai riconoscibili senza il consenso dei genitori. Le foto di repertorio non devono sembrare attività della Misericordia.
5. **Firma e cornice, sempre.** Ogni grafica dice «Misericordia di Ariccia» e ha lungo i bordi una cornice di microtesto (Alessandro, 21/10/2026: «metti in ogni slide, documento grafico eccetera sempre Misericordia di Ariccia! Altrimenti ci rubano la grafica!!»). Con i modelli le mette `rendi.py`; per una grafica fatta in altro modo vedi «Grafiche fatte in altro modo» qui sotto.
6. **Lutto.** Le foto a colori restano a colori; quelle nate in bianco e nero, come quelle d'archivio, restano come sono. Solo quando la grafica ricorda una persona morta (consorelle e confratelli, volontari, benefattori, personaggi pubblici vicini alla Misericordia dal Papa in giù, anniversari della morte, vittime di una tragedia, 2 novembre) la foto va in bianco e nero: sui social il bianco e nero è il segno del lutto. La grafica resta istituzionale e a colori. Per un personaggio pubblico, foto con licenza libera e autore citato nel testo del post.

## Fare la grafica

1. Copia un esempio di `scripts/grafica-brand/modelli-nazionali/esempi/` nella cartella di lavoro e riempi i campi:

   ```json
   {
     "modello": "post-con-fascia",
     "campi": {
       "fascia": "Volontariato",
       "evidenziato": "C'è un posto",
       "titolo": "anche per te.",
       "sottotitolo": "Scegli tu come esserci: chiamaci o scrivici su WhatsApp al 348 4068657.",
       "foto": "foto-evento.jpg",
       "foto-posizione": "70% 50%",
       "foto-alt": "Volontari della Misericordia di Ariccia accanto all'ambulanza durante la festa"
     }
   }
   ```

   - Campi di testo: `\n` va a capo.
   - Campi HTML (`testo`, `frase`, `titolo-2`): solo `<p>`, `<br>`, `<strong>`, `<em>`, `<u>`, `<span class="evidenzia">` (fondo giallo), `<span class="finale">` (parola gialla sottolineata), `<p class="sottolinea">`. Lo script rifiuta il resto.
   - Elenchi (`voci`): una voce per riga.
   - Foto: percorso del file, relativo al file dei dati; `foto-posizione` sposta il ritaglio (due percentuali), `foto-zoom` da 1 a 2 taglia le bande bianche delle foto di WhatsApp, `foto-alt` descrive la foto.
   - Lutto: `"lutto": true` accanto a `"modello"` mette la foto in bianco e nero (esempio in `esempi/post-in-ricordo.json`); `"lutto": false` conferma che non è un ricordo. Se il testo sembra ricordare una persona morta e il dato manca, lo script si ferma.
2. Salva:

   ```
   python3 .claude/skills/grafiche-modelli-nazionali/rendi.py dati.json --uscita USCITA.jpg
   ```

   `.jpg` (qualità 88) per il sito e i social, `.pdf` per carta intestata e biglietto da visita, `.png` solo se richiesto. Serve Playwright per Python con Chromium: nell'ambiente di Claude c'è già; altrove `pip install playwright` e `python -m playwright install chromium` (lo fa anche `scripts/ambiente-codex.sh`).
3. Se lo script esce con PROBLEMI, correggi e rifai: accorcia i testi (il corpo dei caratteri resta quello del modello), sposta il ritaglio della foto, riempi i segnaposti. `--bozza` serve solo a vedere una versione incompleta: una bozza non si pubblica mai.
4. **Guarda l'immagine** prima di usarla: equilibrio, volti tagliati dal ritaglio, testo leggibile sulla foto, parole giuste, firma leggibile. Ingrandisci un bordo per vedere la cornice: da lontano non si nota, da vicino si legge «MISERICORDIA DI ARICCIA · www.misericordia-ariccia.it…». Il controllo automatico non giudica la foto.
5. **Non risalvare il file con un altro programma.** Il JPEG o il PNG porta in testa il segno della cornice, che i controlli del sito cercano nelle grafiche delle news e della Parola della domenica: un altro programma lo toglie. Se serve un ritaglio o un'altra misura, si rifà la grafica con `rendi.py`. `scripts/ottimizza-immagini.py` non ricomprime i file `-grafica.jpg` né quelli con il segno, e crea solo il `.webp` accanto.

## Grafiche fatte in altro modo

Per una grafica che non nasce dai modelli (copertina tratta da un video, design di Canva, grafica fatta da un'altra AI):

```
python3 .claude/skills/grafiche-modelli-nazionali/rendi.py --cornice GRAFICA.jpg [ALTRE.jpg …] [--uscita NUOVA.jpg]
python3 .claude/skills/grafiche-modelli-nazionali/rendi.py --cornice GRAFICA.jpg --firma basso-sinistra
```

- Senza `--uscita` aggiorna i file al loro posto; i file che hanno già il segno si saltano.
- Se la grafica non dice già «Misericordia di Ariccia» in modo leggibile, aggiungi `--firma basso-sinistra` (oppure `basso-centro`, `basso-destra`): la firma va su un fondo uniforme e lo script si ferma se sotto c'è un disegno o una scritta. Si sposta con `--firma-basso` e `--firma-margine` (px), si cambia con `--firma-corpo`, `--firma-carattere` (Montserrat o Jost) e `--firma-colore`; `--forza` solo dopo aver guardato che il fondo va bene così.
- Un design di Canva o di un altro programma si esporta in JPEG o PNG e poi passa da qui. Un PDF fatto altrove non riceve la cornice: per lettere e biglietti si usano i modelli da stampa, che ce l'hanno già.
- Se firma e cornice ci sono già nei pixel (per esempio il fotogramma di un video della rubrica, che le ha in ogni immagine) manca solo il segno: `rendi.py --segno FILE…` lo scrive senza toccare i pixel, solo dopo aver trovato la cornice su tutti e quattro i lati; se non la trova si ferma, e allora serve `--cornice`. Lo usa `scripts/video-rubrica/copia.sh` per le copertine dei video.

## Dove va il risultato

- **Grafica di una news**: `static/img/news/AAAA-MM-GG-<slug>-grafica.jpg`, con la data e lo slug della news (il nome in `-grafica.jpg` la protegge dalla ricompressione), poi `python3 scripts/ottimizza-immagini.py static/img/news`; nel front matter `immagine:` e come prima immagine dell'articolo (`CLAUDE.md`, § «1. Articolo sul sito»). Esce da sola sui social insieme alla news.
- **Caroselli e storie**: la pubblicazione automatica manda una sola immagine per news (il carosello automatico esiste solo per la Parola della domenica). I file si consegnano ad Alessandro, nella chat o nella cartella del lavoro.
- **Biglietti e lettere**: PDF consegnato ad Alessandro; non vanno sul sito.

## Controllo prima di consegnare

- [ ] Modello giusto e identico: niente cornici decorative, filigrane, altri loghi, colori o caratteri cambiati.
- [ ] «Misericordia di Ariccia» si legge e la cornice di microtesto c'è sui bordi (ingrandendo); il file non è stato risalvato con un altro programma.
- [ ] Ogni dato ha una fonte, i recapiti sono quelli di `hugo.toml`, niente inventato.
- [ ] Foto vera e con i permessi; nessuna persona assistita riconoscibile.
- [ ] Nessuna foto a colori portata in bianco e nero, salvo una grafica che ricorda una persona morta (`"lutto": true`).
- [ ] `rendi.py` ha scritto «ok» senza «BOZZA».
- [ ] L'immagine è stata aperta e guardata.
- [ ] C'è la descrizione della foto per l'articolo o la didascalia.

## Modificare i modelli

Come sono fatti, e che cosa rifare dopo una modifica (prova automatica e anteprima), lo spiega `LEGGIMI.md`, § «Come sono fatti». `python3 .claude/skills/grafiche-modelli-nazionali/rendi.py --autotest` prova lo script e i controlli.
