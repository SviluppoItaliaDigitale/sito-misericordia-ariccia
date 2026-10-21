# La Parola della domenica (solo social)

Ogni domenica alle **4:47** esce su Facebook (album) e Instagram (carosello) un
**carosello**: in copertina **una sola opera d'arte, intera**, con scritto quale lettura
illustra; poi **una pagina per ogni versetto** scelto tra prima lettura, seconda lettura e
Vangelo, ognuna con il nome della lettura ben visibile. Sul sito non c'è una pagina: il
post e l'ultima pagina del carosello rimandano a leggere le letture complete sulla
[Liturgia del giorno](https://www.misericordia-ariccia.it/liturgia-del-giorno/) del nostro sito.

Indicazioni di Alessandro (9/10/2026): i versetti sono **quelli più belli e significativi**,
non per forza uno per lettura; l'opera va mostrata **per intero** (mai un dettaglio) e deve
essere chiaro **a quale lettura si riferisce**; basta **una sola opera**.

| Cosa | Dove |
|---|---|
| Scheda della domenica | `.github/social/parola/AAAA-MM-GG.json` |
| Pagine del carosello (online col deploy) | `static/img/parola/AAAA-MM-GG-1.jpg`, `-2.jpg`… |
| Grafica | **stile nazionale delle Misericordie, da domenica 25/10/2026** (approvato da Alessandro il 21/10/2026: «fai tutto uniformato»), costruito con gli elementi dei modelli del carosello della Confederazione (`scripts/grafica-brand/modelli-nazionali/`): **copertina** blu con la fascia bianca «LA PAROLA DELLA DOMENICA» e il triangolo, giorno liturgico e data, l'**opera intera** (mai ritagliata), l'etichetta gialla con la lettura che illustra, la scena e i crediti; **pagine dei versetti** chiare con la fascia blu, il nome della lettura grande e il libro, il versetto con l'evidenza gialla e il riferimento sottolineato; nell'**ultima pagina** il rimando a «misericordia-ariccia.it/liturgia-del-giorno» al posto delle frecce. Colori, Montserrat, fascia, triangolo, evidenziatore e frecce sono quelli del kit; niente cornici decorative, filigrane o altri loghi. Ogni pagina ha la firma «Misericordia di Ariccia» in basso a sinistra (elemento `data-firma`) e una **cornice di microtesto** lungo i bordi (nome, sito, «grafica della Confraternita di Misericordia di Ariccia ODV», anno), incisa da `rendi.js` con il motore `scripts/grafica-brand/firma-e-cornice.js`: invisibile da lontano, leggibile ingrandendo. Le scritte non toccano mai opera, triangolo e frecce, non si sovrappongono fra loro e non escono dalla pagina: `rendi.js` lo controlla da solo. Lo stile precedente (cornice dorata, gigli di Firenze, simbolo in filigrana a rotazione) resta solo nelle pagine già pubblicate fino al 18/10/2026 |
| Strumenti | `scripts/parola-domenica/` (`letture.py`, `opera.py`, `grafica-nazionale.html`, `rendi.js`); `grafica.html` è lo stile precedente e si usa solo per rifare una pagina già pubblicata (`GRAFICA=grafica.html`) |
| Pubblicazione | workflow «Parola della domenica (social)» → `pubblica_social.py --parola` |
| Registro dei post | `.github/social/pubblicati.json`, chiave `parola-AAAA-MM-GG` |

## Procedura settimanale (la routine del mercoledì, con recuperi)

Si prepara **la domenica che viene**. Se la scheda c'è già, non si fa nulla.

**Se mercoledì salta il lavoro si recupera da soli** (regola di Alessandro: il carosello deve
essere pronto entro domenica mattina presto):
- la routine «Parola della domenica» gira **da mercoledì a sabato alle 8:55**: se la scheda della
  domenica c'è già esce subito, altrimenti la prepara;
- la routine «Parola della domenica — recupero notturno» gira **domenica all'1:55**: se manca
  ancora, prepara la scheda di **oggi** e la mette online prima delle 4:47 (il deploy dura ~1 minuto);
- **dalla mezzanotte alle 4:47** il workflow controlla ogni mezz'ora che scheda e pagine siano online; dalle 4:00 una mancanza fa fallire il giro e GitHub avvisa Alessandro per email;
- **dalle 4:47 alle 7:00** pubblica, ogni mezz'ora, ciò che ancora manca nel registro (i giri successivi a quello riuscito non fanno nulla). Tanti giri perché GitHub non garantisce gli avvii a orario: il 18/10/2026 ha saltato i due delle 4:47;
- **dopo le 7:00 non si pubblica più** (regola di Alessandro del 18/10/2026: poi iniziano le Messe e non ha più senso): l'ultimo avvio utile è alle 6:50, anche a mano (l'avvio manuale rifiuta la pubblicazione vera fuori dalla finestra), e lo script ricontrolla l'ora prima di ogni social (`PAROLA_ENTRO`), così un giro lento non pubblica dopo le 7. A mano, entro le 7: Actions → «Parola della domenica (social)» → Run workflow con `prova` **tolta** (di default l'avvio manuale è solo una prova).

Di domenica `letture.py` senza data prende le letture di oggi.

1. **Letture**: `python3 scripts/parola-domenica/letture.py` (oppure `letture.py AAAA-MM-GG`).
   Dà il giorno liturgico e le letture riga per riga, con un numero di versetto
   **stimato** (tiene conto dei salti come «4,12-14.19-20»): controllarlo sempre.
2. **Versetti** (da 1 a 4, di solito 2-3): i più belli e significativi della domenica, da
   prima lettura, seconda lettura e Vangelo (il Salmo no). Non serve uno per lettura, ma il
   **Vangelo è obbligatorio**: almeno un versetto del Vangelo c'è sempre (`rendi.js` si
   rifiuta di creare il carosello senza).
   - Frasi che si capiscono **da sole**: da 6 a 35 parole circa; mai una minaccia o una
     condanna presa isolata.
   - Testo copiato **esatto** da `cei_2008` (traduzione CEI 2008, quella letta a Messa, dal
     sito ufficiale chiesacattolica.it), togliendo solo le virgolette del discorso diretto; se
     la frase comincia a metà versetto si mette la maiuscola. **Non** copiare dal testo
     Evangelizo (`letture`): è la vecchia CEI 1974 e a volte è diverso (es. «macellati» invece di
     «uccisi»); serve solo per contare i versetti. Se la pagina CEI non risponde si usa
     Evangelizo e si scrive `"traduzione": "CEI 1974 (Evangelizo)"` nella scheda.
   - `fonte_lettura`: la formula di `cei_2008` senza gli accenti di lettura (Isaìa → Isaia,
     Filippési → Filippesi).
   - Ordine: quello della Messa (prima lettura, seconda, Vangelo).
   - `evidenza`: 2-6 parole del versetto, copiate identiche, che vanno in giallo.
3. **Opera d'arte** (una sola, facoltativa), di solito sul **Vangelo**:
   - `python3 scripts/parola-domenica/opera.py cerca "parable of the prodigal son"`
     (meglio in inglese o col titolo del museo). Va bene solo `[PD]` (pubblico dominio o CC0).
     Commons limita le richieste: lo script aspetta e riprova da solo.
   - Deve essere l'**opera intera** (dipinto o incisione completi, non ritagli o dettagli
     fotografati), con la scena **riconoscibile** del brano. Preferire dipinti a colori; le
     incisioni vanno bene se la scena è chiara.
   - Scaricarla: `opera.py scarica "File:…" /scratchpad/opera.jpg` (o
     `https://commons.wikimedia.org/wiki/Special:FilePath/NOME?width=1600`) e **guardarla**:
     niente timbri o filigrane di gallerie, niente nudità.
   - **Autore**: su Commons il campo «Artist» a volte contiene il museo (es. «Rijksmuseum»):
     scrivere l'artista vero leggendo la descrizione o le firme incise.
   - Se non c'è un'opera adatta: `"opera": null` (niente copertina, il carosello parte dal
     primo versetto).
4. **Testo del post** (`testo_social`): 3-5 frasi semplici che legano i versetti e, se viene
   naturale, il servizio della Misericordia (prossimità, cura, gratuità). Niente prediche,
   frasi fatte o fatti inventati. Chiudere con «Buona domenica!». Versetti, crediti
   dell'opera, link e hashtag li aggiunge lo script.
5. **Scheda** `.github/social/parola/AAAA-MM-GG.json` (modello: quella del 2026-10-11):
   - `data`, `giorno_liturgico` (dal feed), `testo_social`, `traduzione` («CEI 2008 (chiesacattolica.it)»),
     `preparata_da` (esattamente «Alessandro Cuollo, AAAA-MM-GG», con la data di preparazione: i lavori
     sono sempre a sua firma, mai di uno strumento, e il controllo delle forme da non usare lo verifica);
   - `opera`: `autore`, `titolo` (in italiano), `anno`, `luogo` (museo), `licenza`, `fonte`
     (pagina Commons), `illustra` (es. «Vangelo, Mt 22,1-14»), `scena` (una frase su cosa
     si vede, legata al brano);
   - `pagine`: per ogni versetto `lettura` (Prima lettura / Seconda lettura / Vangelo),
     `fonte_lettura` (formula della Messa: «Dal libro del profeta Isaia», «Dalla lettera di
     san Paolo apostolo ai Filippesi», «Dal Vangelo secondo Matteo»…), `riferimento`
     (abbreviazioni CEI: Mt, Mc, Lc, Gv, Is, Fil…), `versetto`, `evidenza`.
6. **Grafica**: `cd scripts/parola-domenica && npm ci` (la prima volta), poi
   `node scripts/parola-domenica/rendi.js SCHEDA.json static/img/parola OPERA.jpg`
   (senza opera: senza l'ultimo argomento). **Aprire ogni JPEG e guardarlo**: opera intera
   e leggibile, testi non tagliati, lettura giusta su ogni pagina. Se un testo non entra o una
   scritta tocca opera, triangolo, frecce o un'altra scritta, lo script esce con errore: scegliere una
   frase più corta (non spostare gli elementi della grafica sopra il testo). Esce con errore anche se in
   una pagina manca la firma «Misericordia di Ariccia» o non si legge (meno di 24 px,
   trasparente, fuori pagina). La cornice di microtesto la mette lo script: ingrandendo un
   bordo del JPEG si legge «MISERICORDIA DI ARICCIA · www.misericordia-ariccia.it…». I JPEG
   non si risalvano con altri programmi: perderebbero il segno della cornice, che «Controlli
   del sito» cerca nelle pagine in uscita.
7. **Prova del testo**: `DRY_RUN=1 python3 scripts/pubblica_social.py --parola AAAA-MM-GG`.
8. **Pubblicazione**: commit di scheda e pagine, PR, merge su `main` (il deploy mette
   online le immagini). La domenica alle 4:47 il workflow pubblica da solo.

## Domeniche e feste particolari

- Se la domenica coincide con una solennità (es. Ognissanti, Natale), le letture del feed
  sono già quelle giuste: usare il `giorno_liturgico` che dà il feed.
- Le solennità infrasettimanali (Natale di mercoledì, Epifania…) non sono previste:
  solo le domeniche.

## Se qualcosa va storto

- Le fonti delle letture hanno errori passeggeri: il feed Evangelizo risponde a volte 403
  senza testo (circa una richiesta su dieci) e la pagina CEI a volte chiude la connessione.
  `letture.py` e `liturgia_cei.py` riprovano da soli fino a cinque volte, con attese di 3, 6, 12
  e 24 secondi (`scarica()` in `scripts/liturgia_cei.py`; la prova automatica è
  `scripts/controlli/prova_letture.py`, nei controlli di ogni PR). Il 21/10/2026 la preparazione
  del mercoledì non ha prodotto la scheda e lo script, provato subito dopo, si è fermato proprio
  su un 403 del feed. Se dopo i tentativi l'errore resta:
  - feed Evangelizo: `letture.py` si ferma con l'errore e non stampa nulla. Si riprova più tardi;
  - pagina CEI: `letture.py` non si ferma, avvisa «pagina CEI non raggiungibile» e dà solo il testo
    Evangelizo (CEI 1974): i versetti si prendono da lì e nella scheda si scrive
    `"traduzione": "CEI 1974 (Evangelizo)"`. Al deploy, `liturgia_cei.py` toglie il file delle letture
    CEI e la pagina Liturgia del giorno mostra il testo Evangelizo.

- La domenica senza scheda il workflow fallisce con l'avviso «Nessuna Parola della
  domenica»: si può preparare la scheda a mano e lanciare il workflow da Actions con
  `data` e `prova` tolta.
- Pagine non online (deploy non andato): il workflow si ferma senza pubblicare.
- Un post sbagliato si corregge o elimina con «🛠️ Gestione social».
