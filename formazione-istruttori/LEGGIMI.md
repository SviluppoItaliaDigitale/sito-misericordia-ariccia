# Slide per i formatori della Misericordia di Ariccia

Presentazioni da proiettare in aula durante i corsi (BLSD adulto, P-BLSD, disostruzione delle vie aeree, primo soccorso), nate il 20/11/2026 su richiesta di Alessandro: «le slide per i nostri formatori / istruttori per quanto riguarda le manovre salvavita prendendo in stretta considerazione le linee guida aggiornate della IRC».

- **Interne:** questa cartella non è pubblicata sul sito (il deploy carica solo `public/`, costruito da Hugo con `content/` e `static/`).
- **Supporto, non sostituto:** le slide accompagnano il materiale ufficiale dei corsi (programma ARES 118, Italian Resuscitation Council) e lo dicono nella prima slide.
- **Fonti:** Linee guida RCP 2025 di Italian Resuscitation Council (traduzione delle linee guida ERC 2025), con capitolo e pagina nelle note per chi presenta; dati uguali a quelli del sito (`data/dati_da_verificare.yaml`, dossier `primo-soccorso`).
- **Formati:** per ogni presentazione PDF 16:9 Full HD, 4K, 16:10 e 4:3, PowerPoint 16:9 e 4:3 con le note per l'istruttore sotto ogni diapositiva.
- **Come si rifanno:** i sorgenti sono in `scripts/formazione/slide/*.html`; `python3 scripts/scuole/rendi_pdf.py scripts/formazione/slide/NOME.html --anteprime CARTELLA`, poi si guardano le anteprime una per una.
- **Quando si aggiornano:** quando IRC/ERC pubblicano aggiornamenti delle linee guida (registro: voce delle linee guida ERC/IRC 2025) e prima di ogni ciclo di corsi, con il responsabile della formazione.
