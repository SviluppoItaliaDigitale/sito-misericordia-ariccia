# Migrazione dal vecchio dominio misericordiadiariccia.it

> Checklist operativa (11 luglio 2026), a seguito dell'audit esterno.
> Il vecchio sito WordPress è su un **dominio diverso** —
> `misericordiadiariccia.it` (senza trattino) — ancora online e indicizzato.
> Questi interventi vanno fatti **sull'hosting del vecchio dominio** e sui
> profili esterni: non sono realizzabili da questo repository.

## 1. Redirect 301 dal vecchio dominio (pagina per pagina)

Da configurare sull'hosting del vecchio sito (`.htaccess` se Apache).
Mappa completa, basata sull'inventario WordPress (`docs/inventario-contenuti-sito-attuale.md`):

| Vecchio URL (misericordiadiariccia.it) | Nuovo URL (www.misericordia-ariccia.it) |
|---|---|
| `/` | `/` |
| `/su-di-noi/` | `/chi-siamo/` |
| `/i-nostri-servizi/` | `/servizi/` |
| `/servizi/` | `/servizi/` |
| `/formazione/` | `/servizi/formazione/` |
| `/telesoccorso/` | `/progetti/` |
| `/servizio-civile-nazionale/` | `/servizio-civile/` |
| `/news/` | `/news/` |
| `/contatti/` | `/contatti/` |
| `/portale-trasparenza/` | `/trasparenza/` |
| `/i-nostri-progetti/` | `/progetti/` |
| `/informativa-sui-cookie/` | `/privacy/` |
| `/login/`, `/wp-login.php`, `/wp-admin/…` | `/` |
| `/contacts.php` (sito 2016) | `/contatti/` |
| articoli 2019-2024 (stesso slug) | `/news/<slug>/` — vedi sotto |
| archivi autore, categorie, tag, feed WP | `/news/` |
| tutto il resto | `/` |

Gli **articoli** del vecchio blog esistono quasi tutti sul nuovo sito con lo
stesso slug (es. `/2020/03/27/dona-un-respiro/` → `/news/dona-un-respiro/`):
regola consigliata `RedirectMatch 301 ^/\d{4}/\d{2}/\d{2}/(.+)/?$ https://www.misericordia-ariccia.it/news/$1/`
e poi verifica dei singoli slug.

Esempio di `.htaccess` completo per il vecchio dominio:

```apache
RewriteEngine On
# articoli del blog con data nel percorso
RedirectMatch 301 ^/\d{4}/\d{2}/\d{2}/(.+?)/?$ https://www.misericordia-ariccia.it/news/$1/
# pagine principali
Redirect 301 /su-di-noi https://www.misericordia-ariccia.it/chi-siamo/
Redirect 301 /i-nostri-servizi https://www.misericordia-ariccia.it/servizi/
Redirect 301 /formazione https://www.misericordia-ariccia.it/servizi/formazione/
Redirect 301 /telesoccorso https://www.misericordia-ariccia.it/progetti/
Redirect 301 /servizio-civile-nazionale https://www.misericordia-ariccia.it/servizio-civile/
Redirect 301 /portale-trasparenza https://www.misericordia-ariccia.it/trasparenza/
Redirect 301 /i-nostri-progetti https://www.misericordia-ariccia.it/progetti/
Redirect 301 /informativa-sui-cookie https://www.misericordia-ariccia.it/privacy/
Redirect 301 /contacts.php https://www.misericordia-ariccia.it/contatti/
# tutto il resto alla pagina corrispondente o alla home
RedirectMatch 301 ^/(.*)$ https://www.misericordia-ariccia.it/$1
```

> Nota: l'ultima regola prova a mantenere il percorso (`/news/` → `/news/`,
> `/contatti/` → `/contatti/`); il nuovo sito ha già i propri redirect interni
> per gli slug che non esistono più. **Mantenere i redirect per anni**, non
> mesi: Google e i link esterni si aggiornano lentamente.

Se l'hosting del vecchio dominio non permette redirect (es. hosting gratuito):
in alternativa fare **puntare il DNS del vecchio dominio allo stesso spazio
Aruba** del nuovo sito e gestire lì il redirect, oppure — ultima spiaggia —
sostituire il vecchio sito con una singola pagina "Ci siamo trasferiti" con
meta refresh e link.

## 2. Google Search Console

1. Registrare **entrambi** i domini come proprietà.
2. Verificare che la sitemap del nuovo dominio sia inviata
   (`https://www.misericordia-ariccia.it/sitemap.xml`).
3. Usare lo strumento **Cambio di indirizzo** dalla proprietà vecchia verso
   la nuova (richiede i redirect 301 del punto 1 già attivi).
4. Con "Controllo URL" verificare come Googlebot vede le pagine nuove
   (utile anche per il sospetto 502/anti-bot segnalato dall'audit).
5. Rimozione dall'indice di login, archivi autore e feed del vecchio sito.

## 3. Uniformare il dominio sui canali esterni

Tutti devono puntare a `https://www.misericordia-ariccia.it/`:

- [ ] Facebook (campo sito web + post fissati)
- [ ] Instagram (link in bio)
- [ ] Google Business Profile
- [ ] Scheda sul sito della Confederazione Nazionale delle Misericordie
- [ ] RUNTS e directory associative (CSV Lazio ecc.)
- [ ] Siti dei Comuni (Ariccia, Genzano, Velletri…) e della ASL Roma 6
- [ ] Firme email dei volontari e della segreteria
- [ ] QR code stampati (santini, volantini, adesivi sui mezzi)
- [ ] Profili/schede del Servizio Civile (DOL, scelgoilserviziocivile)
- [ ] Eventuali portali di donazione

## 4. Dopo la migrazione

- Spegnere il WordPress del vecchio dominio (i redirect non richiedono WP
  attivo): meno superficie d'attacco e niente pagina anti-bot "Please wait…".
- Rinnovare comunque il **dominio vecchio per almeno 3-5 anni**: i redirect
  funzionano solo finché il dominio è vostro.
- Monitorare in Search Console gli errori 404 provenienti dal vecchio
  dominio e aggiungere redirect mirati se emergono URL non previsti.

## Cosa è già a posto sul dominio nuovo (da questo repo)

- Redirect interni per gli slug legacy e i `.php` residui (`static/.htaccess`)
- `rel=canonical` autoreferenziale su tutte le pagine
- hreflang it/en sulle pagine con doppia versione
- Meta description uniche sulle pagine principali
- Sitemap XML e robots.txt
- Dati strutturati (NGO con contatti e area servita, NewsArticle,
  BreadcrumbList, Service, FAQPage)
