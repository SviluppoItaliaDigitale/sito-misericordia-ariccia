# Assets (Hugo Pipes)

CSS, JavaScript e librerie di terze parti del sito. Hugo li concatena,
minifica e aggiunge l'impronta del contenuto al nome del file
(`css/sito.min.<hash>.css`, `js/sito.<hash>.js`): così `.htaccess` può
tenerli in cache un anno e ogni modifica arriva subito ai visitatori.

- `css/` — `style.css` (brand), `animazioni.css`, `accessibilita.css`, `dossier.css` (solo sezione dossier)
- `js/` — script del sito (`sito.js`, `accessibilita.js`, `ricerca.js`, …)
- `vendor/` — Bootstrap 5, GSAP + ScrollTrigger + SplitText, particles.js

I bundle sono definiti in `layouts/_default/baseof.html`.
Loghi, foto e font restano in `static/` (`static/img/`, `static/fonts/`).
