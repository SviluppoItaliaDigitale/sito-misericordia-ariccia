# Regola autonomia: fare tutto, dividere il lavoro, chiedere nei dubbi

Vale in tutti i repository di Alessandro, per ogni sessione e per ogni strumento che vi lavora. Nasce dalle istruzioni del 13/10/2026.

## Piena autonomia, nessun passaggio a mano

- *«Io non devo fare nulla! Devi fare tutto te in piena autonomia nel migliore dei modi affinché i vari lavori e i vari siti web vengono perfetti.»* Claude decide, esegue, controlla e pubblica. Alessandro non copia testi, non apre chat, non incolla file, non lancia comandi: se un passaggio del lavoro richiederebbe una sua azione, Claude trova il modo di farlo da sola o sceglie l'alternativa migliore e lo scrive nel resoconto.
- Gli altri strumenti sono aiuti che Claude dirige: *«considera che hai un amico a disposizione a darti una mano, e tu gli devi dire esattamente cosa deve fare»*. Il passaggio automatico a ChatGPT (protocollo comune di `COORDINAMENTO.md`, § «Passaggio automatico a ChatGPT») è il canale; la richiesta è sempre completa, nelle sette parti di `scripts/passa-a.py modello`.
- Il risultato deve essere perfetto: ogni consegna passa dai controlli del repository prima di andare live, e ciò che non va bene si corregge o si rifà, senza rimandarlo ad Alessandro.

## Dividere e velocizzare

- *«Devi fare in maniera di ottimizzare ma velocizzare i lavori: crea, clona, oppure dai agli agenti che già sono attivi i lavori che ti saranno assegnati.»* Un lavoro divisibile in parti indipendenti (più file, più articoli, più controlli, più repository) si spezza e si distribuisce ad agenti in parallelo, avviati in una sola mossa; la sessione principale resta la regia, perché un agente non può avviarne altri; unire, verificare la coerenza e pubblicare restano in fila, un merge per volta.
- Un lavoro unico e indivisibile (un file, una pagina) non si dà a due agenti: non vanno più veloci e si pestano i piedi.
- Gli agenti consumano crediti del piano di Alessandro: si avviano quelli che servono, con un compito chiaro e un perimetro di file, non per abbondanza.

## Agenti e skill: si creano da soli, quando servono

- *«Hai piena autonomia nella creazione di nuovi agenti per supporto senza che io ti dia sempre l'autorizzazione»*; *«se necessario, inventati e scrivi nuove skills da adottare per migliorare le funzioni»*. Per agenti (`.claude/agents/`) e skill (`.claude/skills/`) **non serve la proposta preventiva** di `strumenti.md`: Claude li crea quando un lavoro reale ne ha bisogno, li registra in `.claude/strumenti.md` e lo dice nel resoconto.
- Restano valide le altre regole di `strumenti.md`: prima si controlla che cosa esiste già (niente doppioni), pochi strumenti semplici con due righe di spiegazione in testa, i vincoli del repository valgono anche per loro. Per i pacchetti esterni e i server MCP la proposta preventiva resta.

## Dubbi: domande obbligatorie

- *«Se hai dubbi sei obbligato a fare domande a me per chiarimenti.»* Autonomia non vuol dire indovinare: quando una scelta cambia davvero l'esito (un fatto, un dato, un nome, una norma, una decisione editoriale, una spesa) e la risposta non si trova nei file, nelle regole o nelle fonti, Claude **chiede ad Alessandro** prima di decidere — in chat se c'è, altrimenti in «Domande» di `COORDINAMENTO.md` — e intanto fa il resto del lavoro. Le domande sono precise, una alla volta quando possibile, con la raccomandazione di Claude accanto.
- Non si chiede per le scelte ordinarie già coperte dalle regole (formati, controlli, dove pubblicare, come dividere il lavoro): lì si procede e si riporta.
