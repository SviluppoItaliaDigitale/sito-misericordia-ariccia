# Regola strumenti: si creano quando servono
Testo completo con storia: assistente-personale/memoria/regole-complete/strumenti.md

Vale in tutti i progetti per skill, comandi, hook, agenti, plugin, server MCP e pacchetti esterni.

## Quando
- Solo quando un lavoro reale ne ha bisogno (operazione che si ripete, procedura fissa che evita errori), mai in anticipo. Gli script usa-e-getta per il lavoro in corso non richiedono approvazione.
- Prima controlla che cosa esiste (`.claude/` del progetto, `~/.claude/`, plugin installati): riusa o estendi, niente doppioni.

## Come
- Su misura scrivi tu: procedure, regole del progetto, collegamenti, piccoli script. Per i «motori» (conversione documenti, generazione del sito, mappe, OCR, grafica) librerie collaudate dai canali ufficiali (npm, pip, apt, marketplace ufficiale Anthropic), mai riscritte.
- Da GitHub idee libere; codice altrui solo con licenza permissiva (MIT, Apache 2.0, BSD), citando autore e licenza. Senza licenza o copyleft (GPL, AGPL): chiedi prima.
- Pochi strumenti, semplici, ognuno con due righe di spiegazione in testa; i vincoli del progetto (CLAUDE.md, `.claude/rules/`) valgono anche per loro.

## Progetti esterni
- Prima di proporli verifica chi li mantiene, se sono attivi, la licenza e che cosa fa davvero il codice (script d'installazione, hook, accessi a rete e credenziali).
- Installali solo nel progetto che serve, senza aggiornamento automatico; provali con la sandbox attiva (`/sandbox`) quando c'è.

## Approvazione e registro
- Strumento che resta o pacchetto esterno: proposta in due righe (cosa, perché ora, dove va, rischi); si procede solo dopo il sì di Alessandro. Eccezione dal 13/10/2026 (`autonomia.md`): agenti e skill di supporto si creano da soli quando un lavoro reale ne ha bisogno. Per pacchetti esterni e server MCP la proposta resta.
- Ogni strumento va in `.claude/strumenti.md` del progetto (crealo al primo): nome, scopo, data, origine; per gli esterni anche fonte, licenza, versione. Agenti e skill creati da soli si citano anche nel resoconto.
- Uno strumento che non serve più: proponi di toglierlo.
