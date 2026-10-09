# La Parola della domenica (solo social)

Ogni domenica alle **7:47** escono su Facebook e Instagram un versetto delle letture
della domenica e la sua grafica (1080×1350), con un'opera d'arte di pubblico dominio
quando ne esiste una adatta. Sul sito non c'è una pagina: il post rimanda alla
[Liturgia del giorno](https://www.misericordia-ariccia.it/liturgia-del-giorno/).

| Cosa | Dove |
|---|---|
| Scheda della domenica | `.github/social/parola/AAAA-MM-GG.json` |
| Grafica (online col deploy) | `static/img/parola/AAAA-MM-GG.jpg` → `/img/parola/AAAA-MM-GG.jpg` |
| Strumenti | `scripts/parola-domenica/` (`letture.py`, `opera.py`, `grafica.html`, `rendi.js`) |
| Pubblicazione | workflow «Parola della domenica (social)» → `pubblica_social.py --parola` |
| Registro dei post | `.github/social/pubblicati.json`, chiave `parola-AAAA-MM-GG` |

## Procedura settimanale (la routine del mercoledì)

Si prepara **la domenica successiva**. Se la scheda c'è già, non si fa nulla.

1. **Letture**: `python3 scripts/parola-domenica/letture.py` (oppure `letture.py AAAA-MM-GG`).
   Dà il giorno liturgico e le letture riga per riga, con un numero di versetto
   **stimato**: controllarlo (contare dal riferimento del brano; nei brani con salti,
   come «4,12-14.19-20», lo script ne tiene conto).
2. **Scelta del versetto**: è il cuore del messaggio della domenica.
   - Di norma dal **Vangelo**. La prima lettura o la seconda solo se il loro versetto
     dice la stessa cosa in modo più forte o più chiaro. Il Salmo no.
   - Una frase che si capisce **da sola**, senza il resto del brano: da 8 a 35 parole
     circa, mai un versetto di condanna o di minaccia preso isolato.
   - Il testo va copiato **esatto** dal feed (traduzione CEI), togliendo solo le
     virgolette di apertura o chiusura del discorso. Se la frase comincia a metà
     versetto, si parte con la maiuscola senza aggiungere parole.
   - `evidenza`: 2-5 parole del versetto, copiate identiche, da colorare in giallo.
3. **Opera d'arte** (se esiste per quella scena):
   - `python3 scripts/parola-domenica/opera.py cerca "parable of the prodigal son"`
     (meglio in inglese, provare anche il nome del pittore o la scena).
     Va bene solo `[PD]` (pubblico dominio o CC0).
   - Preferire **dipinti a colori** di grandi autori (Caravaggio, Rembrandt, Giotto,
     Beato Angelico, Tiziano, Murillo, Tissot…), già verticali o con un dettaglio
     verticale; incisioni in bianco e nero solo se non c'è altro.
   - Scaricarla nello scratchpad: `opera.py scarica "File:…" /percorso/opera.jpg` e
     **guardarla**: niente timbri o filigrane di gallerie in vista (vanno tagliate con
     `inquadratura`), niente nudità, scena giusta per il brano.
   - Se non c'è un'opera adatta: `"opera": null` → grafica solo tipografica.
4. **Testo del post** (`testo_social`): 2-4 frasi semplici. Cosa dice il versetto e,
   se viene naturale, un aggancio al servizio della Misericordia (prossimità, cura,
   gratuità). Niente prediche, niente frasi fatte, niente fatti inventati. Chiudere
   con «Buona domenica!». La riga dell'opera, il link e gli hashtag li aggiunge lo script.
5. **Scheda** `.github/social/parola/AAAA-MM-GG.json` (modello: quella del 2026-10-11):
   `data`, `giorno_liturgico`, `lettura` (Prima lettura / Seconda lettura / Vangelo),
   `riferimento` (abbreviazione CEI: Mt, Mc, Lc, Gv, Is, Fil…, es. «Mt 22,9»),
   `versetto`, `evidenza`, `testo_social`, `opera` (`autore`, `titolo` in italiano,
   `anno`, `luogo` se noto, `licenza`, `fonte` = pagina Commons, `inquadratura` =
   `object-position` CSS, `zoom` facoltativo), `immagine`, `preparata_da`.
6. **Grafica**: `cd scripts/parola-domenica && npm ci` (la prima volta), poi
   `node scripts/parola-domenica/rendi.js SCHEDA.json static/img/parola/AAAA-MM-GG.jpg OPERA.jpg`
   (senza OPERA.jpg viene la versione tipografica). **Aprire il JPEG e guardarlo**:
   versetto leggibile, opera inquadrata sul soggetto, niente filigrane, niente testo
   tagliato. Se il versetto non entra, lo script esce con errore: scegliere una frase
   più corta.
7. **Prova del testo**: `DRY_RUN=1 python3 scripts/pubblica_social.py --parola AAAA-MM-GG`.
8. **Pubblicazione**: commit di scheda + grafica, PR, merge su `main` (il deploy mette
   online la grafica). La domenica alle 7:47 il workflow pubblica da solo.

## Domeniche e feste particolari

- Se la domenica coincide con una solennità (es. Ognissanti, Natale), le letture del feed
  sono già quelle giuste: usare il `giorno_liturgico` che dà il feed.
- Le solennità infrasettimanali (Natale di mercoledì, Epifania…) non sono previste:
  solo le domeniche.

## Se qualcosa va storto

- La domenica senza scheda il workflow fallisce con l'avviso «Nessuna Parola della
  domenica»: si può preparare la scheda a mano e lanciare il workflow da Actions con
  `data` e `prova` tolta.
- Grafica non online (deploy non andato): il workflow si ferma senza pubblicare.
- Un post sbagliato si corregge o elimina con «🛠️ Gestione social».
