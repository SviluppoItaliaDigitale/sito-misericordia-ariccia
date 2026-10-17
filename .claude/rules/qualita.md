# Regola qualità: lavori perfetti, a prova di errore e di confutazione

Vale in tutti i repository di Alessandro, presenti e futuri, per ogni sessione (PC, cellulare, cloud, routine) e per ogni strumento che vi lavora. Istruzione del 17/10/2026: *«tutti i lavori che vengono svolti in qualsiasi repository devono essere perfetti, a prova di errore e di ogni confutabile prova da parte di qualcuno. Noi dobbiamo essere la Bibbia di ogni argomento che trattiamo»*.

## Il caso da cui nasce

Il 17/10/2026 un audit esterno sul sito della Protezione Civile ha trovato errori che tutti i controlli interni avevano lasciato passare: l'orario del caldo scritto in cinque modi diversi in una trentina di file, il divieto parziale sui telefoni con la fuga di gas, i farmaci da tenere «per 3 giorni» invece di 7, PDF dichiarati accessibili senza esserlo. E un controllo non è stato eseguito perché «qui il correttore non si installa». Nessuno di questi errori era difficile da vedere: nessuno li aveva cercati come li cerca chi vuole confutarci.

## Che cosa vale

1. **Ogni affermazione regge a una verifica esterna.** Ogni fatto, numero, data, norma, nome o indicazione di sicurezza ha una fonte primaria verificata nella sessione (ente, norma vigente, dataset, documento originale), non la memoria e non una fonte di seconda mano. Ciò che non si può dimostrare non si scrive; se serve, si scrive come stima o ipotesi, dichiarandolo.
2. **Lo stesso dato è uguale ovunque.** Prima di pubblicare un dato si cerca come lo scrivono già le altre pagine e gli altri file del repository, compreso il codice. Se non coincide, si stabilisce sulla fonte qual è quello giusto e si allineano tutte le copie nello stesso lavoro, mai una sola.
3. **Prima di consegnare, si prova a confutare il proprio lavoro.** Lo si rilegge come lo leggerebbe un revisore ostile o un auditor esterno: ogni affermazione, ogni numero, ogni link, ogni comando. Si cerca attivamente l'errore, non la conferma. Un lavoro si dichiara finito solo quando quella lettura non trova più niente.
4. **Tutti i controlli si eseguono, nessuno si salta.** Uno strumento che manca si installa: `apt-get update` e poi `apt-get install`, poi `pip` o `npm`, poi il download dalla fonte ufficiale, poi il browser già presente sulla macchina. «Qui non si installa» non è una ragione per consegnare. Se tutte le strade falliscono, il controllo lo fa la CI della pull request **prima** di unire, e il resoconto dice che cosa è stato provato e con quale errore.
5. **Ogni errore trovato diventa un controllo.** Quando un errore lo trova qualcuno (Alessandro, un audit esterno, un revisore, un utente) o lo troviamo noi, si corregge in tutte le sue copie e si aggiunge il controllo che lo avrebbe fermato: una voce di registro, un test, un controllo bloccante sulle pull request, un passo nell'agente che doveva vederlo. Un errore corretto una volta e non sorvegliato ritorna.
6. **Le fonti si ricontrollano.** Norme, linee guida, recapiti e dati cambiano: ciò che si pubblica porta la data della verifica, e le fonti si ricontrollano a scadenza o quando cambiano. Un dato vero quando è stato scritto e falso oggi è un errore.
7. **Onestà sui limiti.** Non si dichiara mai una conformità, una certificazione o un'assenza di errori che non si è misurata. Ciò che non si è potuto verificare si dice, con il motivo.
8. **Nei dubbi si chiede** (regola `autonomia.md`): una scelta che cambia l'esito e non si risolve con le fonti si porta ad Alessandro con la raccomandazione accanto, e intanto si fa il resto.

## Controllo prima di dichiarare chiuso un lavoro

- Ogni affermazione verificabile ha una fonte primaria controllata in questa sessione.
- I dati che il lavoro pubblica coincidono con quelli già presenti nel repository; dove non coincidevano, sono state allineate tutte le copie.
- Tutti i controlli del repository sono stati eseguiti, nessuno saltato per uno strumento mancante.
- Il lavoro è stato riletto per confutarlo, e quella lettura non ha trovato altro.
- Ogni errore trovato strada facendo ha il suo controllo che lo ferma la volta dopo.

Se uno di questi punti non regge, il lavoro non è finito.
