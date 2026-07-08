# Pulizia del vecchio sito sullo spazio Aruba

> Nota operativa (luglio 2026), a seguito dell'audit esterno sul sito live.

Il deploy via FTPS (`SamKirkland/FTP-Deploy-Action`) **carica** i file del sito
nuovo ma **non cancella** i file che non conosce: sullo spazio Aruba sono
quindi rimasti i file del vecchio sito (WordPress e sito 2016), tra cui
`contacts.php`, le cartelle `wp-content/`, `wp-admin/`, `wp-includes/` e le
vecchie pagine indicizzate dai motori di ricerca. L'audit li ha rilevati come
"pagine legacy" ancora raggiungibili, con vecchio cookie banner in inglese e
link al vecchio sito Altervista.

## Cosa è già stato fatto (nel repo)

In `static/.htaccess` sono stati aggiunti i **redirect 301** dalle vecchie
pagine alle nuove: gli slug WordPress censiti in
`docs/inventario-contenuti-sito-attuale.md` (`su-di-noi`, `portale-trasparenza`,
`i-nostri-progetti`, ecc.), `contacts.php` → `/contatti/` e un catch-all per
ogni altro `.php` residuo → home. Così, anche finché i vecchi file restano
fisicamente sul server, nessun visitatore o motore di ricerca li vede più.

## Cosa resta da fare (manualmente, via FTP)

Quando si è certi che non servano più backup:

1. scaricare in locale una copia di `wp-content/uploads/` (foto e documenti
   storici) se non già archiviata;
2. eliminare dallo spazio FTP le cartelle e i file del vecchio WordPress
   (`wp-admin/`, `wp-includes/`, `wp-content/`, `wp-*.php`, `xmlrpc.php`) e i
   `.php` del sito 2016;
3. lasciare intatti i file pubblicati dal workflow (tutto ciò che sta in
   `public/` dopo la build) e il file di stato `.ftp-deploy-sync-state.json`.

Vantaggi: meno superficie d'attacco (un WordPress non aggiornato è un rischio
di sicurezza), niente contenuti duplicati per la SEO, spazio disco libero.
