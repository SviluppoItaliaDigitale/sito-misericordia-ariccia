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
online. GitHub però avvia i giri a orario molto meno spesso di quanto è scritto: in questo repository
«Sito raggiungibile», che ha un giro ogni ora, è partito 69 volte in venti giorni (5-25/11/2026), tre o
quattro al giorno; dal 15 al 24/11 almeno uno al giorno è caduto fra le 8:00 e le 21:59, e in otto giorni su dieci il
primo è partito fra le 12:40 e le 16:15. Senza una pubblicazione del sito al mattino, quindi, il post esce di solito nel primo pomeriggio; per farlo
uscire prima si avvia il giro a mano. **Avvio da fuori alle 8:35, 12:35 e 17:35 (dal 25/11/2026, deciso da Alessandro)**: tre volte al giorno l'operazione pianificata «Giornate: avvio delle 8:35, 12:35 e 17:35» (`trig_011mnrsAPp1mgqBguQbsoLaC`) chiede alla sessione cloud dedicata che avvia già la Parola (`session_011hTVxN3SGTswDA7EnR9XgP`) di avviare `giornate.yml` con `esterno=true` e `prova=false`. L'avvio esterno vale come un giro a orario: pubblica solo se oggi c'è una scheda e si è fra le 8:00 e le 21:59, altrimenti finisce subito in verde. Se la sessione dedicata viene archiviata l'avvio si ferma: restano i giri di GitHub e il controllo di mezzogiorno. Il registro è
`.github/social/pubblicati.json` (voce `giornata-AAAA-MM-GG`); i giri dopo quello riuscito non fanno nulla.
Scheda e grafica vanno su `main` almeno il giorno prima; se arrivano il giorno stesso, il post parte dopo il
deploy o, al più tardi, al giro dell'ora dopo. A mano: Actions → «Giornate e ricorrenze (social)» → Run workflow, con `prova` = sì per vedere che cosa
pubblicherebbe e con `prova` tolta per pubblicare (anche fuori orario, o un altro giorno con `data`).

**Secondo post nello stesso giorno.** Se Alessandro chiede un'altra grafica per la stessa giornata (25/11/2026:
il volto diviso a metà con la scritta «Perché?»), la scheda si chiama `AAAA-MM-GG-<nome>.json` e si pubblica a
mano: Run workflow con `data` = `AAAA-MM-GG-<nome>` e `prova` tolta. I giri automatici e il controllo guardano
solo la scheda `AAAA-MM-GG.json`. Quel giorno la metà in bianco e nero del volto è stata chiesta da Alessandro
come parte del messaggio: resta un'eccezione, le foto in bianco e nero sono solo per il lutto. Un'immagine che
non è una foto vera si indica come «immagine illustrativa», nell'articolo, nel post e nei crediti fotografici.

**Un post programmato deve uscire (regola di Alessandro del 25/11/2026: «Non deve mai più accadere! Se hai
programmato deve uscire! Riprova finché non lo vedi online»).** Un post delle giornate è uscito solo quando Meta
conferma che è online. Dopo la pubblicazione `pubblica_social.py` chiede a Meta il post appena creato (Facebook:
`is_published` e `permalink_url`; Instagram: `permalink`) e scrive l'indirizzo nel registro, voci
`facebook_online` e `instagram_online`. Se la pubblicazione o la conferma non riescono, lo stesso giro riprova
fino a 6 volte, ogni 5 minuti (`GIORNATA_TENTATIVI`, `GIORNATA_PAUSA` in `giornate.yml`), e poi finisce in rosso;
i giri successivi (ogni ora, dopo le pubblicazioni del sito, e i tre avvii da fuori) continuano da dove si è
arrivati. Ciò che è già nel registro non si pubblica una seconda volta: si chiede solo la conferma. Dal
26/11/2026 il controllo di mezzogiorno segnala anche un post «non confermato online». Limite: la conferma è
quella di Meta con le credenziali della pagina, non la vista di un visitatore anonimo (se l'app Meta tornasse in
modalità Sviluppo, Meta confermerebbe lo stesso: vedi `CLAUDE.md`, § «3. Social»). Prova senza rete:
`scripts/controlli/prova_giornate_online.py`, su ogni PR.

**Schede non uscite: restano come base (decisione di Alessandro del 25/11/2026).** I post del 15/11/2026
(Giornata mondiale dei poveri) e del 20/11/2026 (diritti dell'infanzia) non si pubblicano in ritardo: schede e
grafiche restano in `.github/social/giornate/` e in `static/img/giornate/` e si riusano l'anno prossimo e per
ricorrenze simili, aggiornando date, tema dell'anno e fonti.

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
| 15/11/2026 | X Giornata mondiale dei poveri («Il Signore è il rifugio del povero») | [Santa Sede, messaggio di Papa Leone XIV del 13/6/2026](https://www.vatican.va/content/leo-xiv/it/messages/poor/documents/20260613-messaggio-giornata-poveri.html) | non pubblicato: giro partito fuori orario (vedi «Controllo»); scheda e grafica restano come base per il prossimo anno |
| 20/11/2026 | Giornata internazionale per i diritti dell'infanzia e dell'adolescenza | [minori.gov.it, la Convenzione ONU](https://www.minori.gov.it/it/print/6972); [ONU, World Children's Day](https://www.un.org/en/observances/world-childrens-day) | non pubblicato: giro partito fuori orario (vedi «Controllo»); scheda e grafica restano come base per il prossimo anno |
| 25/11/2026 | Giornata internazionale per l'eliminazione della violenza contro le donne, con l'articolo [25 novembre, non sei sola](../content/news/2026-11-25-violenza-contro-le-donne.md) | [ONU](https://www.un.org/en/observances/ending-violence-against-women-day) | pubblicato alle 8:10, avviato a mano dopo il deploy; secondo post «Perché?» (scheda `2026-11-25-perche.json`), avviato a mano |
| 3/12/2026 | Giornata internazionale delle persone con disabilità (tema ONU 2026 non ancora pubblicato al 2/11/2026: non citato) | [ONU](https://www.un.org/en/observances/day-of-persons-with-disabilities) | pronto |
