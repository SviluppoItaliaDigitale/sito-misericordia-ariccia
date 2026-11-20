# Slide per i corsi di primo soccorso, BLSD e P-BLSD

Presentazioni da proiettare in aula durante i corsi della Misericordia di Ariccia (BLSD adulto, P-BLSD, disostruzione delle vie aeree, primo soccorso), nate il 20/11/2026 su richiesta di Alessandro: «le slide per i nostri formatori / istruttori per quanto riguarda le manovre salvavita prendendo in stretta considerazione le linee guida aggiornate della IRC», «con grafica istituzionale», pubblicate per tutti.

- **Pagina del sito:** `content/slide-corsi.md` (`/servizi/formazione/slide/`), layout dei materiali per le scuole (`type: "scuole"`, campo `occhiello`).
- **Sorgenti:** `slide/*.html`, con lo stile di `../scuole/scuole.css` (kit nazionale: fascia blu, triangolo, Montserrat, firma e cornice). Immagini con licenza in `slide/img/`, crediti in `slide/img/CREDITI.md` e nell'ultima slide di ogni presentazione.
- **File pubblicati:** `static/documenti/formazione/` (PDF 16:9, 4K, 16:10, 4:3, PowerPoint 16:9 e 4:3 con le note per l'istruttore), anteprime in `static/img/formazione/`.
- **Come si rifanno:** `python3 scripts/scuole/rendi_pdf.py scripts/formazione/slide/NOME.html --anteprime CARTELLA`, poi si guardano le anteprime una per una; `python3 scripts/controlli/prova_scuole.py` controlla file, firma, anteprime e orfani.
- **Supporto, non sostituto:** la prima slide dice che accompagnano il materiale ufficiale del corso (ARES 118, Italian Resuscitation Council).
- **Fonti:** Linee guida RCP 2025 di Italian Resuscitation Council, con capitolo e pagina nelle note di ogni slide; dati uguali a quelli del sito (`data/dati_da_verificare.yaml`, dossier `primo-soccorso`). Si aggiornano quando IRC/ERC aggiornano le linee guida.
