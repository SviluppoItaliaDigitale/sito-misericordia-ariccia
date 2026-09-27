# Regola strumenti: si creano quando servono

Vale in tutti i progetti per skill, comandi, hook, agenti, plugin, server MCP e pacchetti esterni.

## Quando
- Non creare strumenti in anticipo. Creali solo quando un lavoro reale ne ha bisogno: un'operazione che si ripete o una procedura fissa che evita errori.
- Gli script usa-e-getta per il lavoro in corso non richiedono approvazione.
- Prima di creare, controlla cosa esiste già (`.claude/` del progetto, `~/.claude/`, plugin installati): riusa o estendi, niente doppioni.

## Come
- La parte su misura la scrivi tu: procedure, regole del progetto, collegamenti, piccoli script.
- Per i "motori" (conversione documenti, generazione del sito, mappe, OCR, grafica) usa librerie collaudate dai canali ufficiali: npm, pip, apt, marketplace ufficiale Anthropic. Non riscriverle.
- GitHub è una biblioteca: prendi idee liberamente; usa codice altrui solo con licenza permissiva (MIT, Apache 2.0, BSD), citando autore e licenza. Senza licenza o con licenza copyleft (GPL, AGPL): chiedi prima.
- Pochi strumenti, semplici, ognuno con due righe di spiegazione in testa.
- I vincoli del progetto (CLAUDE.md, `.claude/rules/`) valgono anche per gli strumenti che crei.

## Progetti esterni
- Prima di proporli verifica chi li mantiene, se sono attivi, la licenza e cosa fa davvero il codice: script d'installazione, hook, accessi alla rete e alle credenziali.
- Installali solo nel progetto che serve, senza aggiornamento automatico, e provali con la sandbox attiva (`/sandbox`) quando è disponibile.

## Approvazione e registro
- Prima di creare uno strumento che resta o di installare qualcosa di esterno, proponi in due righe: cosa, perché ora, dove va, rischi. Procedi solo dopo il sì di Alessandro.
- Annota ogni strumento in `.claude/strumenti.md` del progetto: nome, scopo, data, origine (per gli esterni anche fonte, licenza e versione). Crea il file al primo strumento.
- Quando uno strumento non serve più, proponi di toglierlo.
