# Regola grafica: niente "faccia da AI"

Vale in tutti i progetti per siti, landing, pagine, locandine e post. Obiettivo: ogni lavoro deve sembrare fatto da uno studio per *quella* realtà, non generato da un modello.

## Segni tipici da evitare (il "look Claude")
- Palette di default: sfondo crema/avorio con accento terracotta, gradienti viola-indaco-blu, dark mode con bagliori neon.
- Tipografia di default: Inter o system-ui ovunque; serif "eleganti" di moda per i titoli (Fraunces, Instrument Serif, Playfair) messi per fare "premium".
- Hero centrato con etichetta a pillola sopra il titolo, una parola del titolo in gradiente, due pulsanti affiancati.
- Griglia di tre card identiche: icona in un quadratino arrotondato, titoletto, due righe di testo.
- Occhiello in maiuscoletto spaziato sopra ogni titolo di sezione.
- Emoji o icone Lucide al posto di immagini; blob sfocati, vetro smerigliato, ombre morbide e angoli molto arrotondati uguali per tutto.
- Fila di "numeri grandi" (500+ volontari, 24/7…) e testimonianze generiche.
- Sezioni tutte uguali per altezza e spaziatura, alternanza meccanica testo/immagine.
- Testi: "Scopri di più", "Il futuro di…", "non solo X, ma Y", elenchi sempre in terzine, trattini lunghi a raffica.

## Come dare personalità
- **Parti dalla realtà vera**: logo, colori istituzionali, foto reali, luoghi, mezzi, divise, documenti, storia. Il dettaglio specifico (la sede, il territorio dei Castelli, il nominativo IQ0AP) vale più di qualsiasi effetto.
- **Dichiara una direzione** prima del codice, in una riga con un riferimento concreto (es. "manifesto tipografico svizzero", "giornale locale anni '60", "segnaletica d'emergenza", "quaderno di caccia scout", "rivista tecnica radioamatoriale"). Deve essere diversa da progetto a progetto.
- **Tipografia scelta, non di default**: abbinamenti meno battuti, gerarchie forti, titoli con carattere. Se il brand impone i font (es. Misericordia Jost/Inter, AGESCI Roboto), la personalità arriva da composizione, scala, foto e colore, non cambiando font.
- **Colore con intenzione**: palette ricavata dal brand o dal contesto (materiali, luoghi), con un accento inatteso usato poco. Niente gradienti decorativi senza motivo.
- **Composizione**: griglie asimmetriche, scale contrastanti, elementi che rompono la griglia, ritmo variato tra le sezioni; almeno una sezione che non si trova in un template.
- **Immagini vere** prima dello stock; se servono illustrazioni o immagini AI, stile coerente e dichiarato, mai il mix icone + blob.
- **Dettagli d'autore**: un elemento grafico proprio della realtà (texture, motivo, segno, tipo di cornice) ripreso con coerenza.
- **Microcopy su misura**: parole della realtà, non slogan da startup.

## Strumenti: Adobe insieme a Canva (dal 17/10/2026)
Istruzione di Alessandro del 17/10/2026: *«utilizza adobe e tutti i suoi strumenti per fare le nostre attività grafiche, video audio eccetera! oltre a canva e alle tue buone potenzialità di Claude. specialmente per la presa di foto da inserire nei nostri lavori»*.
- **Connettore Adobe** (`Adobe for creativity`, account Adobe completo): prima di ogni lavoro si chiama `adobe_mandatory_init`, che dice quale strumento usare. Si usa per le **foto da inserire nei lavori** (Adobe Stock); per il ritocco e il ritaglio delle foto e per lo sfondo da togliere (Photoshop, Lightroom); per i formati social; per video e audio (Premiere, Quick Cut); per i PDF (Acrobat: creare, unire, comprimere, OCR, convertire); per l'impaginazione da dati (InDesign) e per i caratteri (Adobe Fonts); per i modelli Express.
- **Canva** resta per i design che vivono già lì e per i kit di marca caricati su Canva. **Claude** scrive il codice, i testi e le grafiche HTML/SVG. Per ogni lavoro si sceglie lo strumento che dà il risultato migliore, e si possono combinare: per esempio una foto Adobe ritoccata e poi messa in una locandina Canva.
- **Sfruttare a pieno l'abbonamento** (istruzione del 17/10/2026: *«col mio abbonamento ho accesso a tante funzionalità che quegli utenti gratuiti non hanno modo di ottenere! quindi sfrutta a pieno ogni potenzialità!»*). L'account Adobe è completo (`get_account_type` = `auth`), quindi niente limiti giornalieri da ospite. Si usano senza risparmio:
  - **Adobe Fonts, catalogo completo:** `font_search` in modalità `full`, `font_recommend`, `suggest_type_palettes`, `font_activate`. Per i siti c'è `get_fontkit_embed_url` / `font_create_kit`, che funziona solo se tutti i font del kit sono nell'abbonamento. Se il brand non impone i caratteri, Adobe Fonts è la prima fonte, insieme alla regola sulla tipografia scelta.
  - **Foto:**
    - regolazioni stile Lightroom (`image_apply_auto_tone`, preset, HSL, esposizione);
    - raddrizzamento e ritaglio (`image_auto_straighten`, `image_crop_and_resize`);
    - selezione del soggetto e rimozione dello sfondo;
    - allargamento della tela con `image_generative_expand`, l'unica funzione generativa disponibile;
    - vettorializzazione dei loghi (`image_vectorize`).
  - **Video e audio:** `video_create_quick_cut` per i montaggi brevi, `video_resize` per i formati, `media_enhance_speech` per pulire la voce, `media_summarize`.
  - **PDF (Acrobat):** creare, unire, dividere, comprimere, OCR, oscurare i dati (`pdf_redact`), esportare in Word, Excel o PowerPoint.
  - **Impaginazione da dati (InDesign):** attestati, tesserini, badge; `document_merge_data_layout`.
  - **Express:** i modelli, l'esportazione da HTML a Express e l'animazione dei design.
  - **Archivio Creative Cloud e bacheche Firefly** per raccogliere e condividere materiali.
- **Limiti dichiarati da Adobe, da non tentare:**
  - niente generazione di immagini da testo e niente riempimento generativo;
  - niente aumento della risoluzione, niente rimozione di oggetti o filigrane, niente sfondo sostituito a partire da un testo;
  - niente modifiche generative a volti o corpi;
  - niente taglio video a tempi precisi;
  - al massimo circa 20 file per lavoro.
- **Foto Adobe Stock.** Le foto reali della realtà (sede, mezzi, persone, eventi) vengono prima; Stock serve dove mancano o per immagini generiche (paesaggi, oggetti, scene). Le ricerche si fanno **in inglese** e con parole precise: in italiano la ricerca dà pochi risultati. Il filtro `pricing` non è affidabile, quindi si guarda il campo `pricing` di ogni risultato.
  - Si usano le foto **«Free»** e quelle che il piano include senza spesa.
  - 🔴 **Mai acquistare.** Alessandro non comprerà mai foto, quindi non si chiede neppure. Se `asset_license_and_download_stock` risponde `confirmationRequired` con un preventivo, ci si ferma: **mai** richiamarlo con il `confirmationToken`. Si sceglie un'altra foto.
  - Il link di download dura un'ora: il file si salva subito nel lavoro.
  - Una foto di repertorio non deve mai sembrare un'attività vera della realtà (niente «i nostri volontari» sotto persone di Stock). Per ogni foto si annotano titolo, numero Adobe Stock e licenza nel registro dei materiali del lavoro, e nell'alt text si descrive l'immagine.

## Limiti che restano
- Accessibilità (contrasto, struttura titoli, tastiera, `prefers-reduced-motion`), prestazioni e brand ufficiali vengono prima dell'originalità.
- Niente dati, foto o testimonianze inventati: segnaposto evidenti dove mancano.

## Controllo prima di consegnare
Rileggi il lavoro con questa domanda: "se tolgo logo e testi, si capisce di chi è? Sembra uscito da un generatore?". Se trovi due o più segni dell'elenco sopra senza una ragione di brand, correggi prima di consegnare, e indica in una riga quale direzione hai scelto.
