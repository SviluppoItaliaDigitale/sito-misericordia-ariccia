# Podcast automatico della Misericordia di Ariccia (dal 18/11/2026)

Due puntate a settimana (mercoledì e sabato), fatte con NotebookLM («Overview audio», due voci)
nel Chrome del PC e pubblicate solo dopo la trascrizione e il controllo dei fatti. Nessun
passaggio a mano. È lo stesso metodo del podcast della Protezione Civile di Genzano
(`sito-pc-genzano/scripts/podcast-auto/`), adattato a questo sito.

Decisione di Alessandro del 18/11/2026: *«Vogliamo creare podcast come facciamo per la protezione
civile?»*; metodo «Due voci, come la Protezione Civile»; temi: Primo soccorso passo passo, I dossier
della Misericordia, Kit e prevenzione, Chi siamo e i servizi.

## Dove gira

Sul PC, senza nessuno davanti: la crontab dell'utente lancia `scripts/podcast-auto/giro-automatico.sh`
ogni ora dalle 8:11 alle 21:11. Il lanciatore parte davvero una volta al giorno e solo se in
calendario ci sono meno di 8 puntate (controllo gratuito su `origin/main`); avvia Claude Code
senza finestra con Chrome (`claude -p --chrome --permission-mode auto`) in una copia di lavoro
separata (`~/podcast-lavoro-misericordia/copia-sito`) e scrive i log in `~/podcast-lavoro-misericordia/log/`.
Tutto il materiale di lavoro sta in `~/podcast-lavoro-misericordia/`, separato da `~/podcast-lavoro/`
della Protezione Civile.

**Riga da aggiungere alla crontab** (`crontab -e`; non è stata aggiunta da sola):

```
11 8-21 * * * $HOME/sito-misericordia-ariccia/scripts/podcast-auto/giro-automatico.sh
```

Il minuto 11 è sfalsato rispetto al giro della Protezione Civile (`31 8-21 * * *`).

Servono sul PC:
- PC acceso e non in sospensione;
- Chrome aperto con l'estensione di Claude collegata e l'accesso a Google in NotebookLM
  (`notebook.google.com`), lo stesso account della Protezione Civile;
- `~/.podcast-venv` (già creato per la Protezione Civile) con `faster-whisper`, `numpy` e `pyyaml`;
  `ffmpeg` e `ffprobe` nel PATH;
- `claude` in `~/.local/bin`.

Prova del collegamento: `giro-automatico.sh --prova` (risponde «CHROME OK» o «CHROME NO»; non
genera nulla).

Le puntate già in calendario escono da sole anche a PC spento: Hugo non pubblica le date future e
il sito si ricostruisce ogni notte poco dopo mezzanotte (`deploy.yml`). Se il magazzino scende
sotto una settimana o un'uscita salta, `controllo-podcast.yml` apre la issue «Podcast: poche
puntate in calendario» (label `automazione` e `podcast`), che arriva per email; dal cloud non si
ripara, serve il PC.

## Blocco comune con la Protezione Civile

Chrome e l'account di NotebookLM sono gli stessi dei due podcast: due giri insieme si pestano i
piedi (schede, generazioni, ricevitore). Questo giro prende con `flock` il blocco comune
`~/.cache/podcast-chrome.lock` e lo tiene per tutto il giro; se è occupato esce e riprova all'ora
successiva.

**Da fare nel repository della Protezione Civile** (non toccato da qui): il suo
`scripts/podcast-auto/giro-automatico.sh` usa solo il proprio blocco `~/podcast-lavoro/.giro.lock`.
Va aggiunto, subito dopo, lo stesso blocco comune:

```bash
mkdir -p "$HOME/.cache"
exec 8>"$HOME/.cache/podcast-chrome.lock"
flock -n 8 || { echo "Chrome è occupato da un altro giro del podcast." >>"$LOG"; exit 0; }
```

Finché non c'è, i due giri si evitano solo per l'orario sfalsato (minuto 11 e minuto 31) e perché
ognuno parte una volta al giorno: un giro della Misericordia ancora in corso al minuto 31 non
ferma quello della Protezione Civile.

## Il giro, passo per passo

Una puntata alla volta: si chiude fino alla messa in calendario prima di cominciare la successiva.

1. **Prossima puntata**: prima voce `da-fare` di `coda.yaml`.
   `python3 scripts/podcast-auto/trova-fonti.py <id>` prende le fonti della voce, aggiunge le altre
   pagine pubblicate con le `parole` nel titolo e scrive `~/podcast-lavoro-misericordia/<id>/fonti.txt`
   (indirizzi per NotebookLM) e `fonte.md` (testo delle pagine pubblicate, per il controllo dei
   fatti). Se esce con 3, una fonte non è ancora uscita sul sito (data futura): la voce resta
   `da-fare` e si passa alla successiva.
   `~/.podcast-venv/bin/python scripts/podcast-auto/prepara-fonte.py <id>` scrive `istruzioni.txt`
   (con le regole in più per le voci `tema: primo-soccorso`). Mai fonti esterne al sito: se le
   fonti sono poche, la puntata si fa sulle pagine che ci sono; se ce ne sono di fuori tema, si
   mettono in `escludi`.
2. **NotebookLM** (Chrome, scheda nuova): «Nuovo notebook» → «Aggiungi fonte» → «Siti web»
   → tutti gli indirizzi di `fonti.txt` separati da uno spazio → «Inserisci». Poi «Overview audio»
   → formato **Approfondimento**, lingua **Italiano**, lunghezza **Breve** (con la predefinita le voci
   riempiono il tempo con spiegazioni che le fonti non contengono: lezione della Protezione Civile
   del 15/11/2026) → nel campo «Su cosa dovrebbero concentrarsi…» il testo di `istruzioni.txt`
   → «Genera ora». Se il campo taglia il testo, si accorcia `istruzioni.txt` togliendo la parte sul
   tono, mai le regole. Attendere (5-20 minuti). Cercare i pulsanti per nome (strumento `find`),
   non per coordinate.
   **Scaricare senza «Scarica»** (Chrome chiede dove salvare e quella finestra non si comanda): si
   avvia `~/.podcast-venv/bin/python scripts/podcast-auto/ricevitore.py <id>` (in background, ascolta
   su 127.0.0.1:8798, porta diversa da quella della Protezione Civile), si preme «Riproduci»
   sull'audio pronto e nella pagina si esegue:
   ```js
   performance.setResourceTimingBufferSize(5000);
   document.querySelectorAll('audio,video').forEach(x => x.pause());
   const u = performance.getEntriesByType('resource').map(e => e.name)
     .filter(n => n.includes('googlevideo.com/videoplayback')).pop();
   const b = await (await fetch(u.replace(/&range=[^&]*/, ''))).blob();
   (await fetch('http://127.0.0.1:8798/', {method: 'POST', body: b})).status
   ```
   Se `u` è vuoto, si ricarica la pagina e si preme di nuovo «Riproduci». Il file arriva in
   `~/podcast-lavoro-misericordia/<id>/audio.m4a`.
3. **Trascrizione**: `~/.podcast-venv/bin/python scripts/podcast-auto/trascrivi.py ~/podcast-lavoro-misericordia/<id>/audio.m4a`.
4. **Filtro automatico**: `python3 scripts/podcast-auto/controlla-trascrizione.py <id>`. Se esce con 1
   (numeri assenti dalle fonti, **qualunque numero di telefono diverso dal 112, anche se sta nelle
   fonti**, «i documenti», «i manuali», parole assolute o intensificazioni, nomi di strumenti), la
   puntata non passa: si rigenera o si scarta come al passo 5. Le righe con «!» (si chiama la
   Misericordia, si nomina il 118) non bloccano, ma vanno guardate una per una al passo 5.
5. **Controllo dei fatti** (agente `pc-materiali-publisher` del sito della Protezione Civile,
   § «Niente si pubblica senza verifica», applicato qui): leggere tutta la trascrizione e
   confrontarla frase per frase con `fonte.md`. Al posto dei «dati canonici» della Protezione Civile
   (che questo sito non ha) si usa `data/dati_da_verificare.yaml`: ogni dato della puntata che sta
   nel registro (112, 116117, ASL, importi, norme, recapiti) deve coincidere con il suo `valore`.
   Errore = un'affermazione che le fonti non contengono o contraddicono, un numero diverso, un
   «sempre/mai/fondamentale» non nelle fonti, un nome di strumento o di intelligenza artificiale, la
   Misericordia indicata come da chiamare in emergenza (in emergenza si chiama il 112: la
   Misericordia fa trasporti programmati, `content/dossier/chiamare-il-112.md`), un numero di
   telefono diverso dal 112, le spiegazioni del «perché» e le conclusioni che le fonti non danno.
   Per il primo soccorso è errore anche una manovra spiegata oltre ciò che dicono le schede (dosi,
   tempi, ritmi, posizioni non scritti) e la mancanza dell'invito a imparare le manovre con un
   istruttore. Se c'è anche un solo errore la puntata **non si pubblica**: si rigenera una volta
   (stesse fonti, istruzioni rafforzate sul punto sbagliato); al secondo errore la voce va in
   `stato: scartata` con il motivo e si passa alla successiva al giro dopo.
6. **Trascrizione pulita**: correggere solo gli errori di riconoscimento (non il contenuto), dare
   paragrafi leggibili, in `~/podcast-lavoro-misericordia/<id>/trascrizione.md`. Il 112 si scrive «112».
7. **Pubblicazione**: `~/.podcast-venv/bin/python scripts/podcast-auto/pubblica-puntata.py <id> AUDIO TRASCRIZIONE --descrizione "…"`
   (≤160 caratteri, dice di che cosa parla, niente «verificato» o «interviste»). Ricodifica l'audio
   (AAC 64 kbps mono, senza metadati) in `static/podcast/episodi/`, scrive `content/podcast/<data>-<id>.md`
   con la data del primo mercoledì o sabato libero e segna la voce `programmata`. Poi
   `hugo --minify`, `python3 scripts/controlli/controlla_sito.py public`,
   `python3 scripts/controlli/prova_sede_legale.py`, ramo `claude/podcast-<id>`, PR, squash merge
   a controlli verdi, verifica del deploy e, il giorno dell'uscita, ascolto della pagina pubblicata
   (il player carica l'audio) e controllo del feed `/podcast/index.xml`.
8. **Resoconto** ad Alessandro con notifica: puntata in calendario (link e data) o scartata (motivo).

## Senza il PC (riserva, dal 19/11/2026)

`copione.py` fa una puntata da un copione scritto a mano (`copione.txt`, righe «A:» e «B:») solo con le frasi di `fonte.md`: `copione.py testi ID` prepara i testi per le voci ElevenLabs Luca e Daniela, `copione.py monta ID A.mp3 B.mp3` li divide e li rimonta; senza crediti `copione.py locale ID` usa le voci gratuite Kokoro «Nicola» e Piper «Paola». Poi i passi 3-8 come sopra. Il metodo principale resta NotebookLM.

## La coda

`coda.yaml`: 20 puntate, i quattro temi alternati (primo soccorso, chi siamo e servizi, kit e
prevenzione, dossier). Le schede del primo soccorso che escono più avanti nel dossier (soffocamento
del lattante, rianimazione nel bambino, fratture e le successive) si aggiungono quando la loro news è
uscita; prima `trova-fonti.py` le rifiuta.

## Il sito

- `content/podcast/_index.md`: pagina `/podcast/`, voce «Podcast» nel menu principale (peso 57,
  fra «Dossier» e «Trasparenza»), dati del canale per il feed. Finché non c'è nessuna puntata dice
  «Le prime puntate arrivano a breve».
- `layouts/podcast/list.html` (elenco), `single.html` (player, testo completo, pagine fonte),
  `list.rss.xml` (feed per Apple Podcasts, Spotify e le altre app: copertina, categoria, lingua,
  autore «Confraternita di Misericordia di Ariccia ODV», durata in secondi, peso del file).
- Copertina: `static/img/podcast/copertina-podcast.jpg` (3000×3000, per il feed) e
  `copertina-podcast-600.jpg` (pagina), fatte con `scripts/grafica-brand/podcast/rendi-copertina.py`
  dagli elementi del kit nazionale, con firma e cornice di microtesto. Non si risalvano con altri
  programmi.
- Stile: sezione `/* ---- Podcast ---- */` in fondo a `assets/css/style.css`.
- Spotify e Apple Podcasts: dopo l'iscrizione del feed (la fa Alessandro con i suoi account) gli
  indirizzi vanno in `podcast_spotify` e `podcast_apple` di `content/podcast/_index.md`.

## Regole fisse

- Fonti solo pagine del sito già pubblicate e verificate; mai siti esterni come fonte.
- Nessun riferimento a strumenti o all'intelligenza artificiale nella pagina, nel file audio
  (metadati tolti dalla ricodifica), nei testi, nelle issue e nelle PR (`firma-dei-lavori.md`).
- Non si dichiara nulla che non è vero per quel file.
- L'unico numero da dire è il 112 («uno, uno, due»).
- Il notebook di NotebookLM resta nell'account; non si condivide.
