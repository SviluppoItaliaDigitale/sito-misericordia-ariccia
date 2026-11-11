# Regola guasti: niente errori ignorati, un agente ripara
Testo completo con storia: assistente-personale/memoria/regole-complete/guasti.md

Vale in tutti i repository di Alessandro, presenti e futuri (decisioni del 17/10/2026).

## Che cosa vale
1. **Un controllo che non legge la sua fonte non chiude in verde.** 404, 410, 403 o 5xx persistenti, timeout ripetuti, schema cambiato, feed o playlist spariti sono un guasto: lo script lo annota e il workflow apre o aggiorna **una sola issue in-place** con le label `automazione` + `fonte-rotta`, che si chiude da sola al rientro. Il run diventa rosso, salvo controlli così frequenti da fare spam (allora basta la issue, aperta solo se il guasto persiste).
2. **Un errore di lettura non cambia mai i dati in vigore.** Allerte, avvisi, cataloghi ed elenchi cessano solo quando la fonte, letta correttamente, lo dice o quando scade la loro validità dichiarata. Una fonte muta lascia i dati com'erano e lo dichiara.
3. **Tutti i link del sito sono controllati** (interni, enti pubblici, terzi, documenti). Ogni 404/410 e ogni file mancante rende rosso il controllo e va nella issue «Link rotti». 403 e 429 su link esterni (anti-bot) si accettano e non entrano nel rapporto. 5xx e timeout non rendono rosso ma restano nel rapporto di lychee: chi ripara li ricontrolla con una richiesta reale e, se tornano per più settimane, li tratta come rotti. Si ripara trovando la pagina attuale sulla fonte e verificandola con una richiesta reale, mai con un URL indovinato; se non esiste più, si punta alla sezione che la conteneva o si toglie il link lasciando il testo.
4. **Ogni repository ha la sua sorveglianza:** controllo dei link (lychee sul sito costruito) se pubblica un sito; controllo giornaliero dei run falliti di tutte le automazioni, con una issue «Salute» che si chiude da sola; età dei dati che dipendono da fonti esterne, dove ci sono.
5. **Un agente ripara, ogni giorno.** Una routine cloud legge le issue di guasto e i run rossi dell'ultimo giorno: riproduce l'errore, trova la causa, corregge tutti i file che ripetono la stessa cosa, rilancia il controllo e chiude solo dopo il run verde. «Transitorio» solo dopo averlo rieseguito e visto passare. Una fonte morta senza sostituti ufficiali si toglie dal controllo, scrivendo che cosa non è più sorvegliato. Routine: per `sito-pc-genzano` la «Lavorazione autonoma issue automatiche» (`trig_01EL97B5vF55j3JAWGiNiNCM`, punto 4-ter); per gli altri siti la «Riparazione guasti dei siti» (`trig_01RBJ5MxdCUxjeq5UDGu5Lej`); per i repository senza sito la «Riparazione guasti dei repository non-sito» (`trig_01HV9m4thNyBF317kLgZMNe4`) (vedi `memoria/guasti-e-riparazioni.md` di `assistente-personale`).
6. **Nei dubbi l'agente chiede, ma intanto ripara.** Se la soluzione dipende da una scelta che cambia l'esito (fonte sostitutiva, togliere un contenuto, confermare un dato), domanda precisa ad Alessandro con raccomandazione, come notifica sul telefono e commento sulla issue. Una issue di guasto non si chiude mai senza averlo risolto o senza una domanda aperta.
7. **Se il guasto lo scopre Alessandro per primo, ha fallito il sistema:** oltre al guasto si corregge il controllo che non l'ha visto.

## Repository nuovo
Ogni repository nuovo (passo 5 di `sessione-cloud.md` § «Nuovo repository») nasce con:
- le label `automazione` e `fonte-rotta`;
- il workflow `salute-sito.yml` con `scripts/salute-sito.py` (run falliti ogni giorno; non dipende dal sito, si copia da `cooprimavera`, `social-pc-genzano` o `assistente-personale`);
- l'iscrizione all'elenco del prompt della routine di riparazione del punto 5 (sito o non-sito); il prompt si reinvia intero, perché un aggiornamento parziale lo cancella;
- se pubblica un sito, `controllo-link.yml` copiato da `sito-misericordia-ariccia` o `cooprimavera` (costruisce con Hugo: adattalo al generatore e all'indirizzo del sito nuovo);
- se legge fonti esterne, controlli conformi al punto 1.
