---
name: leggi-web
description: Legge in locale, gratis e senza limiti, le pagine web che WebFetch non legge (siti costruiti con JavaScript come EUR-Lex, pagine con attese o caricamenti successivi, PDF serviti da pagine dinamiche) e le restituisce in Markdown, testo, HTML o elenco dei link, con screenshot se serve. È il gemello di Firecrawl senza crediti. Usala quando WebFetch dà una pagina vuota, monca o un errore, prima di Firecrawl, sul PC e nelle sessioni cloud dal cellulare. Non aggira CAPTCHA né verifiche anti-bot.
---

# Leggi web

Cosa fa: apre la pagina in un vero browser (Chromium con Playwright), aspetta che il JavaScript la costruisca, toglie menu, intestazione, piè di pagina e banner dei cookie, e restituisce il contenuto. I PDF, anche quelli che arrivano dopo una pagina d'attesa, li legge con `pdftotext`.
Origine: scritta per Alessandro Cuollo il 04/11/2026, per non consumare i 1.000 crediti mensili di Firecrawl. Usa solo librerie già installate (Playwright, BeautifulSoup, markdownify) e `pdftotext`; nelle sessioni cloud le installa da sola se mancano.

## Quando
Ordine di navigazione di `CLAUDE.md`: prima `WebSearch` e `WebFetch`, poi i canali gratuiti delle fonti (JSON, API, RSS), poi **questa skill**, e Firecrawl solo se anche questa non legge la pagina.

## Come
```
python3 .claude/skills/leggi-web/leggi.py URL                       # Markdown del contenuto principale
python3 .claude/skills/leggi-web/leggi.py URL --formato link        # link della pagina
python3 .claude/skills/leggi-web/leggi.py URL --formato testo
python3 .claude/skills/leggi-web/leggi.py URL --tutta-la-pagina     # con menu e piè di pagina
python3 .claude/skills/leggi-web/leggi.py URL --scorri --attesa 5   # contenuti che arrivano scorrendo o tardi
python3 .claude/skills/leggi-web/leggi.py URL --screenshot pagina.png
python3 .claude/skills/leggi-web/leggi.py URL1 URL2 --uscita pagine.md
```
Pagine lunghe: scrivere su file con `--uscita` e leggere solo le parti che servono.

Codici di uscita: 0 letta; 2 errore (rete, 404, 5xx); 3 **bloccata**, cioè il sito mostra una verifica anti-bot o risponde 401/403/429.

## Se la pagina è bloccata (uscita 3)
La skill non aggira CAPTCHA, verifiche «sei umano?» o blocchi dei siti, e non va modificata per farlo (niente finti browser, proxy a rotazione o risolutori di CAPTCHA). Le strade, in ordine:
1. Una fonte equivalente che si legge: il documento originale dell'ente, la Gazzetta Ufficiale, Normattiva, un open data.
2. Sul PC, il Chrome di Alessandro con gli strumenti `claude-in-chrome`: è il suo browser, con i suoi accessi; se compare una verifica la supera lui.
3. Firecrawl, se ci sono crediti.
Ciò che non si è potuto leggere si dichiara, con il motivo (regola `qualita.md`).

## Prove fatte il 04/11/2026 (25 fonti, tutte quelle per cui le regole indicavano Firecrawl e le fonti della rassegna normativa)
- **Si leggono (21):** EUR-Lex (pagina e PDF del Regolamento 2016/679, per intero), DG ECHO, UNDRR, Accademia della Crusca, Europeana, Library of Congress (lenta: `--attesa-massima 120`), Senato, Giustizia amministrativa, ENEA, INGV lista terremoti, Geoportale MASE (che Firecrawl non leggeva), Parco dei Castelli Romani, Treccani, albo pretorio di Genzano (`/web/trasparenza/papca-ap/-/papca/igrid/5986`, 20 atti, con il ripiego senza browser: al browser risponde 500), BURL (sicer e regione.lazio.it), Consiglio regionale del Lazio, Gazzetta Ufficiale, Normattiva, Dipartimento della Protezione Civile, EU Space. Anche in una sessione cloud (EUR-Lex, uscita 0).
- **Bloccate (3), uscita 3:** OCHA e Quirinale (403), Corte costituzionale (CAPTCHA Radware). Strade: per il Quirinale e la Corte gli atti stanno anche in Gazzetta Ufficiale e Normattiva; per OCHA, ReliefWeb (`reliefweb.int`, dello stesso ente); sul PC il Chrome di Alessandro; Firecrawl come ultima strada.
- **Errore (1):** Cassazione SentenzeWeb (`italgiure.giustizia.it`): il server non invia il certificato intermedio, e la verifica del certificato non si disattiva. Resta Firecrawl o il Chrome di Alessandro.
- **Nel Chrome di Alessandro (strumenti `claude-in-chrome`), stesso giorno:** Quirinale, OCHA, Corte costituzionale e Cassazione si aprono tutte e quattro, senza verifiche (alla Corte solo il banner dei cookie, da non accettare). Quindi sul PC, o dal cellulare con una sessione del PC comandata a distanza (Remote Control, PC acceso), si leggono **tutte le 25 fonti**. A PC spento queste quattro restano scoperte: fonti equivalenti, poi Firecrawl.
