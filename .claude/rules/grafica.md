# Regola grafica: niente "faccia da AI"
Testo completo con storia: assistente-personale/memoria/regole-complete/grafica.md

Vale in tutti i progetti per siti, landing, pagine, locandine e post: ogni lavoro deve sembrare fatto da uno studio per *quella* realtà.

## Segni tipici da evitare (il "look Claude")
Sfondo crema/avorio con terracotta, gradienti viola-indaco-blu, dark mode al neon; Inter o system-ui ovunque, serif di moda per fare «premium» (Fraunces, Instrument Serif, Playfair); hero centrato con pillola sopra il titolo, parola in gradiente e due pulsanti; tre card identiche con icona in quadratino arrotondato; occhiello in maiuscoletto spaziato su ogni sezione; emoji o icone Lucide al posto di immagini, blob sfocati, vetro smerigliato, ombre morbide e angoli molto arrotondati per tutto; fila di «numeri grandi» e testimonianze generiche; sezioni tutte uguali, alternanza meccanica testo/immagine; testi come «Scopri di più», «Il futuro di…», «non solo X, ma Y», terzine, trattini lunghi a raffica.

## Come dare personalità
- **Modelli ufficiali prima di tutto:** se la realtà ha modelli da usare identici, si usano quelli (Misericordia di Ariccia dal 21/10/2026: modelli nazionali, `comunicazione-social.md` § «Solo per la Misericordia di Ariccia»); il resto di questa sezione vale per ciò che i modelli non coprono.
- Parti dalla realtà vera (logo, colori istituzionali, foto, luoghi, mezzi, divise, documenti, storia); il dettaglio specifico vale più di ogni effetto.
- Dichiara prima del codice una direzione in una riga con un riferimento concreto, diversa da progetto a progetto.
- Tipografia scelta, non di default; se il brand impone i caratteri (Misericordia Montserrat, AGESCI Roboto) la personalità viene da composizione, scala, foto e colore. Colore ricavato dal brand o dal contesto, un accento inatteso usato poco, niente gradienti decorativi.
- Composizione asimmetrica, scale contrastanti, ritmo variato, almeno una sezione che non viene da un template; immagini vere prima dello stock (illustrazioni o immagini AI in stile coerente e dichiarato, mai icone + blob); un dettaglio d'autore della realtà ripreso con coerenza; microcopy con le parole della realtà.

## Strumenti: Adobe insieme a Canva (dal 17/10/2026)
- **Adobe for creativity** (account completo, `get_account_type` = `auth`, nessun limite da ospite): prima di ogni lavoro `adobe_mandatory_init`. Va sfruttato in pieno: foto Adobe Stock; ritocco, ritaglio e scontorno (Photoshop, Lightroom: `image_apply_auto_tone`, preset, HSL, esposizione, `image_auto_straighten`, `image_crop_and_resize`, selezione del soggetto, `image_generative_expand` unica funzione generativa, `image_vectorize` per i loghi); formati social; video e audio (`video_create_quick_cut`, `video_resize`, `media_enhance_speech`, `media_summarize`); PDF con Acrobat (creare, unire, dividere, comprimere, OCR, `pdf_redact`, esportare in Word/Excel/PowerPoint); InDesign da dati (attestati, tesserini, badge, `document_merge_data_layout`); Adobe Fonts in catalogo completo (`font_search` modalità `full`, `font_recommend`, `suggest_type_palettes`, `font_activate`; per i siti `get_fontkit_embed_url`/`font_create_kit`, solo con font tutti nell'abbonamento; prima fonte di caratteri se il brand non li impone); Express (modelli, HTML → Express, animazioni); archivio Creative Cloud e bacheche Firefly.
- **Canva** per i design che vivono già lì e i kit di marca su Canva; **Claude** per codice, testi e grafiche HTML/SVG. Si sceglie lo strumento migliore e si combinano.
- **Limiti Adobe, da non tentare:** generazione da testo e riempimento generativo; aumento di risoluzione, rimozione di oggetti o filigrane, sfondo sostituito da testo; modifiche generative a volti o corpi; taglio video a tempi precisi; oltre circa 20 file per lavoro.
- **Adobe Stock:** foto reali della realtà prima; Stock per ciò che manca o per immagini generiche. Ricerche in inglese, parole precise; il filtro `pricing` non è affidabile, si guarda il campo `pricing` di ogni risultato. Solo foto «Free» o incluse nel piano. 🔴 **Mai acquistare** né chiedere di farlo: se `asset_license_and_download_stock` risponde `confirmationRequired`, ci si ferma e **mai** lo si richiama con il `confirmationToken`; si sceglie un'altra foto. Il link di download dura un'ora: salvare subito. Una foto di repertorio non deve sembrare un'attività vera della realtà; per ognuna titolo, numero Adobe Stock e licenza nel registro dei materiali, e alt text che descrive l'immagine.

## Foto in bianco e nero: solo per il lutto (dal 21/10/2026)
- Le foto restano a colori. In bianco e nero solo nelle grafiche e nei post in ricordo di chi è morto (persone della realtà, personaggi pubblici vicini, dal Papa in giù; anniversari della morte, vittime di una tragedia, 2 novembre), e solo la foto: loghi, fasce, colori e testi restano a colori; se la grafica dell'ente è stampata sulla foto, il bianco e nero si applica prima, sulla sola foto.
- Restano come sono le immagini che documentano un evento (mappe, ShakeMap, satellitari, grafici, codici colore) e le foto nate in bianco e nero.
- Per un personaggio pubblico serve una foto con licenza d'uso (es. Wikimedia Commons), autore citato. Misericordia: `rendi.py` con `"lutto": true`, che si ferma se il testo sembra un ricordo e il dato manca.

## Nome dell'ente e cornice di microtesto (dal 21/10/2026)
Ogni grafica, slide o documento grafico porta il nome dell'ente ben leggibile e ai bordi una cornice di microtesto (nome, sito o in mancanza account social, anno), invisibile da lontano e leggibile ingrandendo. La firma non si toglie, la cornice non si copre; le grafiche già pubblicate restano come sono.
- **Misericordia di Ariccia:** modelli nazionali e `rendi.py` nel repository del sito; grafica fatta altrove: `rendi.py --cornice`.
- **Protezione Civile di Genzano:** `scripts/microtesto_cornice.py` (`sito-pc-genzano`) su copertine e immagini social, firma = fascia del Gruppo; grafica fatta altrove (dal 22/10/2026): `python3 scripts/microtesto_cornice.py GRAFICA.png` → `GRAFICA-cornice.png`, con la firma già presente.
- **Cooprimavera:** logo sulla fascia chiara in basso; cornice dai generatori `social/grafiche/genera.js` e `social/video/genera.js` (motore `social/grafiche/cornice.js`), controllata da `scripts/controlla-cornice.py`; grafica fatta altrove: `node social/grafiche/genera.js --cornice FILE.jpg`.
- **ARI Castelli Romani e AGESCI Genzano 2:** modelli in `associazioni/*/modelli/` di `assistente-personale`, motore `strumenti/firma-e-cornice.js`; grafica fatta altrove: `strumenti/cornice-su-immagine.py --ente ari|agesci`, con `--firma` se il nome manca.

## Limiti che restano
Accessibilità (contrasto, titoli, tastiera, `prefers-reduced-motion`), prestazioni e brand ufficiali vengono prima dell'originalità. Niente dati, foto o testimonianze inventati: segnaposto evidenti dove mancano.

## Controllo prima di consegnare
«Se tolgo logo e testi, si capisce di chi è? Sembra uscito da un generatore?». Due o più segni dell'elenco senza ragione di brand: correggi; indica in una riga la direzione scelta. Nessuna foto a colori portata in bianco e nero fuori dal lutto; nome dell'ente leggibile e cornice lungo i bordi.
