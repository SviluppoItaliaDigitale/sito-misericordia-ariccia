# Critica — giudicare la pagina sugli screenshot

Adattato dal riferimento `references/critique.md` di **taste-skill v2** (Leonxlnx, licenza MIT,
commit `6010f91`, letto il 23/10/2026). La skill originale non si installa: sceglie a caso palette e
caratteri e vieta componenti dei design system istituzionali. Qui resta solo il metodo per guardare
ciò che si è costruito. Il testo della licenza MIT dell'originale, che va sempre insieme a questo
file, è in `LICENZA-taste-skill.txt`.

Si giudica **sugli screenshot, mai sul codice**: chi ha scritto il codice ci legge le proprie
intenzioni, gli screenshot mostrano solo ciò che c'è. Finestre fisse, così due giri danno gli stessi
screenshot: **1280×800**, **768×1024** e **375×812** px. Per ognuna la prima schermata e poi la pagina
intera (con Playwright `full_page=True`).

Nelle tecniche guidate dallo scorrimento (esplosione 3D, video scrubbato, scrollytelling, cubi) la
pagina intera non basta, perché una scena bloccata cambia mentre si scorre: si fanno anche gli
screenshot a ogni scena e, dentro le scene bloccate, a circa il 25, il 50 e il 75 per cento
dell'avanzamento, più la pagina con il movimento ridotto (`reduced_motion="reduce"`). La passata 13
si fa su tutti questi.

## 1. Le passate

Una alla volta, prima desktop poi telefono.

1. **Un secondo, poi cinque.** Che cosa si vede per primo? Deve esserci una risposta sola: una
   parola, un'immagine, un oggetto. In cinque secondi uno sconosciuto deve capire che cosa è, per chi
   è e che cosa fare dopo.
2. **Occhi socchiusi.** La pagina si riduce a due o tre masse di dimensioni diverse? Tante masse
   piccole e simili vuol dire che niente guida.
3. **Copri il logo.** La prima schermata potrebbe essere di un'altra realtà o di un altro settore? Se
   cambiando nome e sostantivo nel titolo la pagina reggerebbe uguale, manca l'idea. Poi scorri: l'idea
   arriva fino ai contatti e al piè di pagina, o dopo la prima schermata diventa blocchi da modello?
4. **Bordi.** Segui il margine sinistro dei blocchi di testo: due o tre allineamenti ripetuti sono
   una composizione, sei sono elementi messi uno per volta.
5. **Spazio e cornice.** Le cose collegate sono vicine e quelle diverse lontane? Lo stacco fra sezioni
   è più grande di quelli interni? C'è un buco per caso (colonna corta, decorazione tolta)? Margini
   destro e sinistro uguali? Una sezione con il testo in metà schermo e l'altra metà vuota? Un vuoto più
   alto di mezzo schermo?
6. **Testo.** Salto netto fra corpo e titolo (tre volte o più)? Non più di cinque o sei dimensioni?
   Nessun titolo con una parola sola sull'ultima riga, righe non oltre circa 75 caratteri, niente testo
   centrato oltre tre righe.
7. **Colore.** Quale colore occupa più superficie, quale accompagna, dove sta l'accento? Un accento in
   dieci punti non dice più nulla; su un solo pulsante e un dettaglio dice «qui».
8. **Immagini.** Ognuna fa un lavoro (mostra la cosa, il luogo, la prova)? Tagli con proporzioni
   coerenti, stessa luce e stesso trattamento, nessuna foto stirata, nessun riquadro grigio, nessuna
   finta schermata fatta di barre grigie.
9. **Ripetizione.** Una parola per la disposizione di ogni sezione (divisa, elenco, a tutta larghezza,
   griglia, frase grande…): la stessa parola due volte di fila, o tre nella pagina, è il modello che
   si vede.
10. **Telefono.** La schermata a 375 è una composizione sua, con tagli e a capo suoi, o la pagina
    desktop schiacciata? La prima schermata resta una cosa sola e chiara?
11. **Pienezza.** Ogni schermata desktop è un manifesto composto, o una colonna stretta di testo piccolo
    con vuoto ai lati? Una pagina austera non è una pagina sobria: se sembra un bozzetto non finito, è
    costruita poco. Un solo motivo ingrandito a tutto schermo senza niente da leggere è un buco anche lui.
12. **Sostanza.** Ogni sezione richiesta dà la sua informazione intera e leggibile (orari, servizi,
    come diventare volontario, contatti)? Chi arriva esce sapendo ciò che cercava? L'azione principale
    è un pulsante vero nella prima schermata?
13. **Sovrapposizioni.** Qualcosa copre un titolo, una frase o un pulsante a qualche punto dello
    scorrimento? Qualcosa esce dal bordo del telefono? Una riga che scorre di lato si legge come tagliata.
14. **L'altra realtà e la cosa viva.** Metti sulla pagina il nome della realtà più simile: l'idea regge
    ancora? Poi nomina la cosa viva (che cosa può fare chi visita, o che cosa cambia a ogni visita). Se
    una delle due risposte è debole, è il primo problema del giro.

Nelle prove dell'autore originale una pagina ricca anche se piena di espedienti da modello ha sempre
battuto una pagina pulita ma povera: togliere le decorazioni è metà del lavoro, l'altra metà è la
sostanza (testo più grande, campi pieni di colore, foto vere, ogni sezione con il suo contenuto intero).

## 2. Il voto

Quattro voti da 1 a 10: **grafica 40%, usabilità 30%, idea 20%, contenuti 10%**.

- **Grafica:** 9-10 ogni schermata regge come un manifesto; 8 sicura e coerente con un paio di punti
  deboli; 7 pulita e professionale, poca tensione; 6 ordinata ma anonima, sembra un kit; 5 o meno
  gerarchia debole, spazi casuali, caratteri di default, immagini che non si accordano.
- **Usabilità:** 9-10 si capisce che cos'è, per chi è e che cosa fare senza scorrere, perfetta al
  telefono; 8 chiara con un attrito minore; 7 funziona con un problema vero; 6 o meno bisogna cercare.
- **Idea:** 9-10 un concetto di questa realtà, mai visto applicato così; 8 un'idea chiara con una mossa
  memorabile; 7 un approccio noto fatto con gusto; 6 o meno il default del settore.
- **Contenuti:** 9-10 ogni riga può parlare solo di questa realtà; 7-8 chiari con qualche frase
  generica; 6 o meno slogan, riempitivi, stock.

`totale = 0,4·grafica + 0,3·usabilità + 0,2·idea + 0,1·contenuti`. Un 8,5 onesto è raro: se il primo
voto al proprio lavoro è 9, si rifà come chi non l'ha costruito.

## 3. Tetti che prevalgono sul calcolo

- Due o più segni del «look da generatore» di `.claude/rules/grafica.md` senza una ragione di brand:
  totale al massimo **6,5**.
- La pagina potrebbe essere di chiunque (passata 3): idea al massimo **6**; l'idea regge anche per la
  realtà più simile (passata 14): idea al massimo **7**.
- Qualunque segnaposto (riquadro grigio, lorem, «immagine qui»): contenuti al massimo **5**.
- Una sezione richiesta mancante o ridotta a poche parole: contenuti al massimo **6**.
- Nessun pulsante vero per l'azione principale nella prima schermata: usabilità al massimo **7**.
- La prima schermata non dice che cos'è: usabilità al massimo **6**.
- Margini diversi, una sezione schiacciata da un lato, un vuoto più alto di mezzo schermo, o due
  schermate desktop quasi vuote: grafica al massimo **6,5**.
- Qualcosa copre un titolo: usabilità al massimo **6**; una fascia bianca dove un'animazione non è
  partita, o contenuto tagliato fuori schermo: usabilità al massimo **5**.
- Contrasto sotto AA o testo illeggibile con il movimento ridotto: la pagina non si consegna, prima
  si corregge.

## 4. Il rapporto di ogni giro

```
GIRO n
Visto in un secondo: …
Idea (una frase): …
Cosa viva: …
Disposizioni per sezione: apertura=… / …=… / …
Voti: grafica _ · usabilità _ · idea _ · contenuti _ → totale _,_
Tetti applicati: …
Tre problemi più visibili, ognuno con lo screenshot in cui si vede e la correzione:
1. …
2. …
3. …
```

I problemi si scrivono come un grafico a un collega: «il paragrafo parte 40 px a sinistra del titolo»,
«terza sezione divisa di fila», «al telefono l'ambulanza è tagliata fuori dall'inquadratura». «Potrebbe
essere più curata» non è un rilievo.

## 5. Che cosa correggere prima

1. **L'idea**, se la passata 3 fallisce: si cambia l'apertura, non i dettagli.
2. **La gerarchia**: una cosa dominante per schermata.
3. **La composizione**: allineamenti, spazi fra sezioni, varietà, buchi.
4. **Il testo**: scala, a capo, larghezza delle righe, interlinea.
5. **Le immagini**: sostituire le deboli, uniformare tagli e trattamento.
6. **Il colore**: proporzioni e disciplina dell'accento.
7. **I dettagli**: stati, fuoco, allineamenti piccoli, telefono.
8. **Il movimento**, per ultimo.

Se togliere un elemento lascia un buco, non riempirlo con una decorazione: chiudi lo spazio, ingrandisci
ciò che resta, o lascia il posto a una foto o a un campo di colore.

## 6. Quando fermarsi

Al massimo tre giri (critica → correzione dei tre problemi → nuovi screenshot → critica). Ci si ferma
prima quando un giro non trova più niente che uno sconosciuto noterebbe. Se dopo il terzo giro il totale
resta sotto 7,5, lo si scrive nella consegna con i problemi rimasti: non si arrotonda.

I modelli grafici ufficiali di una realtà (per esempio i modelli nazionali della Misericordia) si usano
come sono: la critica giudica come sono composti i contenuti dentro, non il modello.
