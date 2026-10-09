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
| Grafica | cornice dorata doppia, sobria, con il giglio di Firenze e due volute in ogni angolo (Alessandro: niente di pacchiano); filetto con alfa e omega ai lati della croce dello stemma FM, stemma storico (`static/img/loghi/mise-fregio.png`) come sigillo in copertina; nelle pagine dei versetti, in filigrana trasparentissima dietro il testo, **un solo simbolo per pagina** a rotazione settimanale (stemma, **pesce**, **rosario**, **buffa**, la veste storica dei confratelli, sagoma scura disegnata da ChatGPT nel compito 002 della bacheca); «Firenze · 1244» sotto lo stemma in copertina; niente motto né altre scritte in più (Alessandro: «troppe scritte»); il **giglio di Firenze** (dove nacque la prima Misericordia) solo negli angoli. Le filigrane possono stare dietro le scritte purché si leggano (decisione di Alessandro); per tutto il resto **mai scritte sopra la grafica**: `rendi.js` lo controlla da solo |
| Strumenti | `scripts/parola-domenica/` (`letture.py`, `opera.py`, `grafica.html`, `rendi.js`) |
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
- se alle 4:47 manca ancora, il workflow fallisce e GitHub avvisa Alessandro per email.

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
   - `data`, `giorno_liturgico` (dal feed), `testo_social`, `traduzione` («CEI 2008 (chiesacattolica.it)»), `preparata_da`;
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
   scritta tocca ornamenti, stemma, filetti o opera, lo script esce con errore: scegliere una
   frase più corta (non spostare gli ornamenti sopra il testo).
7. **Prova del testo**: `DRY_RUN=1 python3 scripts/pubblica_social.py --parola AAAA-MM-GG`.
8. **Pubblicazione**: commit di scheda e pagine, PR, merge su `main` (il deploy mette
   online le immagini). La domenica alle 4:47 il workflow pubblica da solo.

## Domeniche e feste particolari

- Se la domenica coincide con una solennità (es. Ognissanti, Natale), le letture del feed
  sono già quelle giuste: usare il `giorno_liturgico` che dà il feed.
- Le solennità infrasettimanali (Natale di mercoledì, Epifania…) non sono previste:
  solo le domeniche.

## Se qualcosa va storto

- La domenica senza scheda il workflow fallisce con l'avviso «Nessuna Parola della
  domenica»: si può preparare la scheda a mano e lanciare il workflow da Actions con
  `data` e `prova` tolta.
- Pagine non online (deploy non andato): il workflow si ferma senza pubblicare.
- Un post sbagliato si corregge o elimina con «🛠️ Gestione social».
