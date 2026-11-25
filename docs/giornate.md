# Giornate e ricorrenze sui social

Dal 2/11/2026 (richiesta di Alessandro): come la Confederazione, per ogni ricorrenza o giornata importante
esce un post dedicato, solo sui social (Facebook e Instagram), senza pagina sul sito.

## Come è fatto un post

- **Grafica**: modello nazionale `post-giornata.html` (fascia con il nome della giornata, titolo su due righe
  con la prima evidenziata e chiusa dai due punti, una frase), compilato con
  `python3 .claude/skills/grafiche-modelli-nazionali/rendi.py`. Dati della grafica in
  `.github/social/giornate/AAAA-MM-GG-grafica.json`, file in `static/img/giornate/AAAA-MM-GG-<tema>.jpg`.
- **Immagine**: prima una foto nostra adatta; poi un'opera a tema Misericordia
  (`scripts/grafica-brand/opere-misericordia/`, Sette opere del Maestro di Alkmaar); solo se manca tutto,
  un'immagine dei post nazionali (Alessandro, 2/11/2026). Nei ricordi dei defunti la foto va in bianco e nero
  (`"lutto": true`). Quando Alessandro chiede una foto e una nostra non c'è, si usa una foto di repertorio di Adobe
  Stock, gratuita o inclusa nel piano, che non sembri un nostro servizio: il numero va nei
  [crediti fotografici](../content/crediti-fotografici.md) e nel testo del post («Foto di repertorio»).
- **Testo**: `.github/social/giornate/AAAA-MM-GG.json` con `testo` (2-4 paragrafi brevi, tono della
  Misericordia, credito dell'immagine in fondo), `immagine`, `alt` e, facoltativi, `hashtag` (es.
  `#GiornataMondialeDeiPoveri`). Gli hashtag fissi li aggiunge lo script.
- **Riferimento**: i post nazionali si leggono con «Gestione social» → `osserva-ig`, ID `misericordieitalia`.
- **Giornata con articolo**: se per la giornata esce anche un articolo sul sito (25/11/2026, richiesta di Alessandro),
  la grafica è una sola, in `static/img/news/` come quella delle news, la scheda la indica in `immagine` e mette nel
  testo l'indirizzo dell'articolo; l'articolo ha `social: false`, così il post è uno solo.

## Pubblicazione

Il workflow `giornate.yml` pubblica la scheda di oggi, se c'è, con `scripts/pubblica_social.py --giornata`, al
primo giro utile fra le 8:00 e le 21:59 italiane: un giro ogni ora e uno alla fine di una pubblicazione del
sito («Pubblica su Aruba (LIVE)») partita da un'unione o avviata a mano, quando la grafica è appena andata
online. Il registro è
`.github/social/pubblicati.json` (voce `giornata-AAAA-MM-GG`); i giri dopo quello riuscito non fanno nulla.
Scheda e grafica vanno su `main` almeno il giorno prima; se arrivano il giorno stesso, il post parte dopo il
deploy o, al più tardi, al giro dell'ora dopo. A mano: Actions → «Giornate e ricorrenze (social)» → Run workflow, con `prova` = sì per vedere che cosa
pubblicherebbe e con `prova` tolta per pubblicare (anche fuori orario, o un altro giorno con `data`).

**Controllo (dal 25/11/2026).** `controllo-giornate.yml` gira dopo ogni giro delle giornate e alcune volte al
giorno, con `scripts/controlli/controlla_giornate.py`: da mezzogiorno il post di oggi deve essere nel registro
con Facebook e Instagram, e così quelli dei tre giorni prima. Se manca, apre o aggiorna la issue «Giornate e
ricorrenze: post non pubblicato» (`automazione` + `fonte-rotta`) e il run diventa rosso; la issue si chiude da
sola. Fa lo stesso se non riesce a leggere le schede o il registro (file mancante, JSON rotto, formato
cambiato): la issue dice che cosa non si legge, perché finché il controllo non legge non si sa se i post sono
usciti. Nasce dai post del 15/11 e del 20/11/2026, mai usciti: la finestra era 8:00-11:59, GitHub avviava un solo
giro al giorno, nel pomeriggio, e quel giro finiva in verde senza pubblicare. Un post di un giorno passato non
si recupera da solo: decide Alessandro se farlo uscire in ritardo.

## Calendario

Le date si verificano sulla fonte (ONU, Santa Sede, Ministeri) prima di preparare il post e si scrivono qui.

| Data | Giornata | Fonte | Stato |
|---|---|---|---|
| 2/11/2026 | Commemorazione dei defunti | calendario liturgico | pubblicato |
| 15/11/2026 | X Giornata mondiale dei poveri («Il Signore è il rifugio del povero») | [Santa Sede, messaggio di Papa Leone XIV del 13/6/2026](https://www.vatican.va/content/leo-xiv/it/messages/poor/documents/20260613-messaggio-giornata-poveri.html) | non pubblicato: giro partito fuori orario (vedi «Controllo») |
| 20/11/2026 | Giornata internazionale per i diritti dell'infanzia e dell'adolescenza | [minori.gov.it, la Convenzione ONU](https://www.minori.gov.it/it/print/6972); [ONU, World Children's Day](https://www.un.org/en/observances/world-childrens-day) | non pubblicato: giro partito fuori orario (vedi «Controllo») |
| 25/11/2026 | Giornata internazionale per l'eliminazione della violenza contro le donne, con l'articolo [25 novembre, non sei sola](../content/news/2026-11-25-violenza-contro-le-donne.md) | [ONU](https://www.un.org/en/observances/ending-violence-against-women-day) | pubblicato alle 8:10, avviato a mano dopo il deploy |
| 3/12/2026 | Giornata internazionale delle persone con disabilità (tema ONU 2026 non ancora pubblicato al 2/11/2026: non citato) | [ONU](https://www.un.org/en/observances/day-of-persons-with-disabilities) | pronto |
