# Pubblicazione automatica delle news sui social

Ogni **nuova news** pubblicata sul sito viene condivisa in automatico su:

- **Facebook** — pagina [MiseAriccia](https://www.facebook.com/MiseAriccia): post con testo e link all'articolo (l'anteprima usa titolo e immagine della news);
- **Instagram** — [@confraternitamisericordia](https://www.instagram.com/confraternitamisericordia): foto della news con didascalia e hashtag.

## Come funziona

1. Si aggiunge una news in `content/news/` e la si carica su `main`.
2. Il workflow *Pubblica su Aruba* compila e pubblica il sito.
3. Subito dopo, `scripts/pubblica_social.py` legge l'elenco delle news
   (`/news/index.json`, generato da Hugo) e pubblica quelle che non risultano
   nel registro `.github/social/pubblicati.json`.
4. Il registro viene aggiornato e salvato nel repository dal bot (commit
   "Social: registro post pubblicati").

Anche il rebuild notturno controlla le news: una news con **data futura**
esce sul sito e sui social il giorno della sua data.

### Regole di sicurezza

- Si pubblicano solo news con data **negli ultimi 10 giorni**: le vecchie non
  vengono mai ripescate.
- Al massimo **3 news per esecuzione** (le altre alla successiva).
- Una news non viene mai pubblicata due volte sulla stessa rete.
- Se i social danno errore, **il sito viene pubblicato comunque**; il post si
  ritenta al deploy successivo (o la notte seguente).

## Opzioni nella singola news (front matter)

```yaml
---
title: "Titolo della news"
date: 2026-10-01
slug: "titolo-della-news"
social: false                    # NON condividere sui social
immagine: "/img/news/foto.jpg"   # immagine per social/anteprima (altrimenti la prima del testo)
social_testo: "Testo personalizzato per il post, al posto del riassunto automatico."
---
```

- **Instagram richiede un'immagine JPEG** (`.jpg`): se la news non ha immagini,
  esce solo su Facebook.
- Formato consigliato per Instagram: quadrato (1080×1080) o verticale 4:5 (1080×1350).

## Provare senza pubblicare

GitHub → *Actions* → *Pubblica su Aruba (LIVE)* → *Run workflow* → spuntare
**"Social: solo prova"**. Il log dello step *Pubblica le nuove news sui social*
mostra i testi che verrebbero pubblicati.

In locale:

```bash
hugo && python3 scripts/pubblica_social.py   # senza credenziali è sempre una prova
```

## Configurazione iniziale (una volta sola)

Serve un amministratore della pagina Facebook.

1. **Collegare Instagram alla pagina Facebook**: l'account Instagram deve essere
   *professionale* (Business o Creator) e collegato alla pagina MiseAriccia
   (Meta Business Suite → Impostazioni → Account collegati).
2. **Creare un'app Meta** su <https://developers.facebook.com/apps> (tipo
   *Business*), aggiungendo i prodotti *Facebook Login for Business* e
   *Instagram*.
3. **Ottenere un token della pagina senza scadenza** — il modo più semplice è un
   *utente di sistema* in Meta Business Suite:
   Impostazioni business → Utenti → Utenti di sistema → Aggiungi (ruolo Admin) →
   Assegna risorse: la pagina MiseAriccia e l'account Instagram (controllo
   completo) → *Genera token* per l'app creata, con i permessi:
   `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`,
   `instagram_basic`, `instagram_content_publish`, `business_management`.
   Scegliere scadenza **"Mai"**.
4. **Ricavare gli ID** (sostituire `TOKEN`):
   ```bash
   curl "https://graph.facebook.com/v23.0/me/accounts?fields=id,name,access_token,instagram_business_account&access_token=TOKEN"
   ```
   - `id` della pagina MiseAriccia → **META_PAGE_ID**
   - `access_token` della pagina → **META_PAGE_TOKEN**
   - `instagram_business_account.id` → **META_IG_USER_ID**
5. **Inserire i secrets su GitHub**: repository → *Settings* → *Secrets and
   variables* → *Actions* → *New repository secret*: `META_PAGE_ID`,
   `META_PAGE_TOKEN`, `META_IG_USER_ID`.
6. Fare una prova con *"Social: solo prova"* (vedi sopra).

Finché i secrets non ci sono, lo script gira sempre in prova e non pubblica nulla.
Con solo `META_PAGE_ID` + `META_PAGE_TOKEN` pubblica solo su Facebook.

**Il token non va mai scritto nei file del repository**: solo nei secrets GitHub.

## Stato della configurazione (30/09/2026)

- Attiva dal 30/09/2026. Portfolio Meta «Misericordia di Ariccia ODV»
  (ID 1419956906942849), pagina MiseAriccia (ID 623665131108377) collegata a
  Instagram @confraternitamisericordia (ID 17841471518130375).
- App Meta «Sito Misericordia Ariccia» (ID 2286230255250372), ancora «Non
  pubblicata»: i post risultano comunque visibili al pubblico (verificato).
- Utente di sistema **sito-web**, con accesso completo alla pagina
  (Instagram incluso) e all'app. Ruolo nel portfolio: **Dipendente** (dal
  03/10/2026), così la gestione di amministratori e persone del portfolio
  resta solo ad Alessandro.
- Token rigenerato il **03/10/2026** con permessi di gestione completa dei
  contenuti (il token della pagina **non scade**):
  `pages_show_list`, `pages_read_engagement`, `pages_read_user_content`,
  `pages_manage_posts`, `pages_manage_engagement`, `pages_manage_metadata`,
  `read_insights`, `instagram_basic`, `instagram_content_publish`,
  `instagram_manage_contents`, `instagram_manage_comments`,
  `instagram_manage_insights`, `instagram_manage_messages`,
  `business_management` (imposto da Meta, non si può togliere).
  Esclusi di proposito i permessi pubblicitari (`ads_*`, `pages_manage_ads`)
  e quelli di negozio e contenuti sponsorizzati.
- Per rigenerare il token: Impostazioni business → Utenti di sistema →
  sito-web → *Genera token* (stessa app, scadenza «Mai», stessi permessi),
  poi ricavare il token della pagina (punto 4 sopra) e aggiornare il secret
  `META_PAGE_TOKEN`. Il token non va mai incollato in chat né nei file.
- Il 30/09/2026 il registro è stato allineato ai post reali: le news 2026
  mancanti sono state pubblicate (in ordine, senza doppioni). Le news dal
  2019 al 2024 restano segnate «preesistente» e non vanno ripubblicate.

## Parametri avanzati (variabili d'ambiente dello script)

| Variabile | Default | Significato |
|---|---|---|
| `SOCIAL_MAX_GIORNI` | 10 | età massima di una news per essere condivisa |
| `SOCIAL_MAX_PER_ESECUZIONE` | 3 | news massime per esecuzione |
| `META_GRAPH_VERSION` | v23.0 | versione della Graph API di Meta |
| `DRY_RUN` | — | `1` = solo prova |

Per ripubblicare una news già condivisa: togliere la sua voce da
`.github/social/pubblicati.json` (se è più vecchia di 10 giorni, lanciare lo
script con `SOCIAL_MAX_GIORNI` più alto).
