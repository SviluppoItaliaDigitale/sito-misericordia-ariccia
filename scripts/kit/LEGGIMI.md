# Kit per le emergenze

Schede A4 da stampare della pagina [/kit/](https://www.misericordia-ariccia.it/kit/): una cartella per kit in `static/kit/<kit>/` (schede `NN-nome.html`), le risorse comuni in `static/kit/comune/` (`print.css`, Montserrat con la licenza `OFL-Montserrat.txt`, triangolo delle Misericordie) e le pagine indice in `content/kit/<kit>/_index.md`. Importate il 18/11/2026 dai Kit Calamità della Protezione Civile di Genzano di Roma, licenza CC BY-NC-SA 4.0 (Alessandro: «Crea anche i kit, puoi copiarli»).

## Importazione

`python3 scripts/kit/importa_da_pc.py PERCORSO_REPO_PC` copia pagine e schede dal sito della Protezione Civile e cambia percorsi, intestazione, colori, recapiti e firma.

⚠️ **Rilanciarlo sovrascrive tutto**, comprese le correzioni fatte qui dopo l'importazione: Montserrat e cornice di microtesto in `comune/print.css`, i caratteri delle singole schede e le correzioni di stampa del 19/11/2026 (commenti `controllo fogli di stampa` nelle schede). Dopo un'importazione si confronta con `git diff`, si rimettono le correzioni e si esegue il controllo qui sotto. Per una scheda sola conviene copiarla a mano.

Dopo l'importazione i testi si rileggono: recapiti e sede della Misericordia (la sede operativa di Viale Antonietta Chigi, 46; mai la sede legale, vedi `CLAUDE.md` § «Sedi»), l'attribuzione alla Protezione Civile nel piè di pagina (dovuta per la licenza), i riferimenti che valevano solo per il Gruppo comunale.

## Cornice di microtesto

Dal 19/11/2026 ogni foglio stampato ha la cornice di microtesto della regola grafica (nome, sito, «grafica della Confraternita di Misericordia di Ariccia ODV», anno), con lo stesso testo, corpo e tono delle grafiche. È tutta in fondo a `comune/print.css`, solo in stampa: in alto e in basso nei riquadri del margine di pagina (margine di 9 mm), sui lati con due strisce fisse. Firefox e Safari non stampano i riquadri del margine, quindi lì restano solo i due lati. Una scheda con `@page { margin: 0 }` deve disegnare alto e basso da sé, come `bambini/10-routine-lavarsi-mani.html`. Il **© 2026** va aggiornato quando le schede si rifanno in un altro anno.

## Controllo

```bash
python3 scripts/controlli/controlla_fogli_kit.py                         # tutte le schede, circa 25 secondi
python3 scripts/controlli/controlla_fogli_kit.py --da-git origin/main    # solo quelle che un lavoro tocca
python3 scripts/controlli/controlla_fogli_kit.py --pagine <kit>/<scheda>.html --png /tmp/fogli
```

Stampa davvero ogni scheda con Chromium in A4 e si ferma su: cornice di microtesto assente o toccata, struttura mancante, residui dell'importazione, sede legale, errori JavaScript, risorse 404, immagini rotte, Montserrat non caricato, un foglio bianco, un foglio quasi vuoto, un primo foglio con la sola intestazione. Gira su ogni pull request che tocca il kit (job `fogli-kit` di `.github/workflows/controlli.yml`). Servono `playwright==1.56.0`, `pypdfium2==5.13.0`, `numpy`, `pillow` e Chromium (`python3 -m playwright install chromium`).

Gli agenti che lo usano: `mis-print-card-qa` (qualità di stampa e giochi), `mis-didattica-reviewer` (sicurezza, età, fonti), `mis-verifica-visiva` (schermate lette davvero), `mis-integrita-tecnica` (file, pacchetti, link), in `.claude/agents/`.

## Correggere un foglio quasi vuoto

In quest'ordine, con il commento `/* controllo fogli di stampa, GG/MM/AAAA: motivo */` nella scheda:

1. scala di stampa della sola scheda, `@media print{.scheda{zoom:0.9x}}`, al massimo del 12% (0,88); se la scheda ha già un suo `zoom`, si cambia quel valore;
2. spazi della scheda (righe da scrivere, margini dei riquadri), senza togliere contenuto;
3. un foglio nuovo in un punto naturale (`.nuovo-foglio{break-before:page}`), quando il contenuto è davvero più lungo.

`comune/print.css` non si cambia per una scheda sola: vale per tutte e 142.
