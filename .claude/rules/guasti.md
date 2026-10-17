# Regola guasti: niente errori ignorati, un agente ripara

Vale in tutti i repository di Alessandro, presenti e futuri: `sito-pc-genzano`, `sito-misericordia-ariccia`, `cooprimavera`, `social-pc-genzano`, `assistente-personale` e ogni sito o progetto nuovo. Nasce dalle istruzioni del 17/10/2026: *«gli errori 404 e simili non devono mai essere ignorati e devono essere risolti! deve esserci un agente che interviene!!»*, *«se c'è qualcosa che non va, in tutto il sito, deve esserci un agente che in maniera automatica interviene e risolve il problema! se ha dubbi, fa domande, ma deve risolvere!»*, *«questo vale per tutti i link del sito»*, *«idem per i siti attuali e futuri che gestiamo negli altri repository»*.

## Il caso da cui nasce

Il controllo settimanale dei video LIS di `sito-pc-genzano` leggeva una playlist che YouTube aveva eliminato. Ha ricevuto un 404 per almeno due mesi, lo ha scritto nel log e ha chiuso ogni volta in verde. Lo stesso censimento ha trovato controlli che, davanti a una fonte illeggibile, **cancellavano un avviso meteo in corso** o il bollettino incendi come se fossero cessati. Il problema non era la mancanza di agenti: era che i controlli non dicevano quando non avevano potuto controllare.

## Che cosa vale

1. **Un controllo che non riesce a leggere la sua fonte non chiude in verde.** Un 404, un 410, un 403 o un 5xx che persistono, un timeout ripetuto, uno schema cambiato, un feed o una playlist spariti sono un guasto. Lo script lo annota e il workflow apre o aggiorna **una sola issue in-place** con le label `automazione` + `fonte-rotta`, che si chiude da sola quando la fonte torna. Il run diventa rosso, a meno che giri tanto spesso da fare spam (allora basta la issue, aperta solo se il guasto persiste).
2. **Un errore di lettura non cambia mai i dati in vigore.** Un'allerta, un avviso, un catalogo o un elenco cessano solo quando la fonte, letta correttamente, dice che sono cessati, oppure quando la loro validità dichiarata è scaduta. Una fonte muta lascia i dati com'erano e lo dichiara.
3. **Tutti i link del sito sono controllati.** Interni, verso enti pubblici, verso terzi, verso documenti. Ogni link in 404 o 410, e ogni file mancante, rende rosso il controllo dei link e finisce nella issue «Link rotti». Un 403 o un 429 su un link esterno, quasi sempre un blocco anti-bot, si accetta e non entra nel rapporto. Un 5xx o un timeout, spesso un server lento, non rende rosso il controllo ma resta scritto nel rapporto di lychee, nel log del run: chi ripara lo ricontrolla con una richiesta reale e, se lo stesso link torna nei rapporti di più settimane, lo tratta come un link rotto. Si ripara cercando la pagina attuale sulla fonte e verificandola con una richiesta reale, mai con un URL indovinato. Se la pagina non esiste più, si punta alla sezione che la conteneva o si toglie il link lasciando il testo.
4. **Ogni repository ha la sua sorveglianza.** Ci sono tre pezzi:
   - un controllo dei link (lychee sul sito costruito), per i repository che pubblicano un sito;
   - un controllo giornaliero dei run falliti di tutte le automazioni, con una issue «Salute» che si chiude da sola;
   - l'età dei dati che dipendono da fonti esterne, dove ce ne sono.
5. **Un agente ripara, ogni giorno.** Una routine cloud legge le issue di guasto e i run rossi dell'ultimo giorno e li ripara. Per prima cosa riproduce l'errore, poi trova la causa, corregge tutti i file che ripetono la stessa cosa, rilancia il controllo e chiude solo dopo il run verde. Un errore si dichiara «transitorio» solo dopo averlo rieseguito e visto passare. Se una fonte è morta senza sostituti ufficiali, la toglie dal controllo e scrive che cosa non è più sorvegliato. Le routine sono:
   - per `sito-pc-genzano`, la «Lavorazione autonoma issue automatiche» (`trig_01EL97B5vF55j3JAWGiNiNCM`, punto 4-ter);
   - per gli altri siti, la «Riparazione guasti dei siti» (`trig_01RBJ5MxdCUxjeq5UDGu5Lej`);
   - per i repository che non pubblicano un sito, la «Riparazione guasti dei repository non-sito» (`trig_01HV9m4thNyBF317kLgZMNe4`) (per queste ultime due vedi `memoria/guasti-e-riparazioni.md` nel repository `assistente-personale`).
6. **Nei dubbi l'agente chiede, ma intanto ripara.** Se la soluzione dipende da una scelta che cambia davvero l'esito (quale fonte sostituisce quella morta, togliere un contenuto, confermare un dato) e la risposta non sta nei file, nelle regole o sulle fonti, l'agente fa una domanda precisa ad Alessandro con la sua raccomandazione. La domanda arriva come notifica sul telefono e come commento sulla issue. Intanto l'agente ripara tutto il resto. Una issue di guasto non si chiude mai senza averlo risolto o senza una domanda aperta.
7. **Se il guasto lo scopre Alessandro per primo, è il sistema a non aver funzionato.** Oltre al guasto si corregge il controllo che non l'ha visto.

## Repository nuovo

Insieme ai passi di `sessione-cloud.md` § «Nuovo repository» (passo 5), ogni repository nuovo nasce con:
- le label `automazione` e `fonte-rotta`;
- il workflow `salute-sito.yml` con `scripts/salute-sito.py`, che controlla ogni giorno i run falliti di tutte le automazioni;
- l'iscrizione all'elenco del prompt della routine che lo riguarda: «Riparazione guasti dei siti» (`trig_01RBJ5MxdCUxjeq5UDGu5Lej`) per un sito, «Riparazione guasti dei repository non-sito» (`trig_01HV9m4thNyBF317kLgZMNe4`) per un repository non-sito;
- se pubblica un sito, anche `controllo-link.yml` (da `sito-misericordia-ariccia` o `cooprimavera`).
