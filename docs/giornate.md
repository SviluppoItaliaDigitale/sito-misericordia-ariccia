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
  (`"lutto": true`).
- **Testo**: `.github/social/giornate/AAAA-MM-GG.json` con `testo` (2-4 paragrafi brevi, tono della
  Misericordia, credito dell'immagine in fondo), `immagine`, `alt` e, facoltativi, `hashtag` (es.
  `#GiornataMondialeDeiPoveri`). Gli hashtag fissi li aggiunge lo script.
- **Riferimento**: i post nazionali si leggono con «Gestione social» → `osserva-ig`, ID `misericordieitalia`.

## Pubblicazione

Il workflow `giornate.yml` pubblica ogni mattina alle 8:31 italiane (riserva 9:31 e 10:31) la scheda di oggi,
se c'è, con `scripts/pubblica_social.py --giornata`; il registro è `.github/social/pubblicati.json`
(voce `giornata-AAAA-MM-GG`). Scheda e grafica vanno su `main` almeno il giorno prima, così il deploy mette
online l'immagine. Prova a mano: Actions → «Giornate e ricorrenze (social)» → `prova` = sì.

## Calendario

Le date si verificano sulla fonte (ONU, Santa Sede, Ministeri) prima di preparare il post e si scrivono qui.

| Data | Giornata | Fonte | Stato |
|---|---|---|---|
| 2/11/2026 | Commemorazione dei defunti | calendario liturgico | pubblicato |
