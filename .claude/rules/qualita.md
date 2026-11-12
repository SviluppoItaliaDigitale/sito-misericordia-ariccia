# Regola qualità: lavori perfetti, a prova di errore e di confutazione
Testo completo con storia: assistente-personale/memoria/regole-complete/qualita.md

Vale in tutti i repository di Alessandro, per ogni sessione e strumento (decisione del 17/10/2026).

## Che cosa vale
1. **Ogni affermazione regge a una verifica esterna.** Fatti, numeri, date, norme, nomi e indicazioni di sicurezza hanno una fonte primaria verificata nella sessione (ente, norma vigente, dataset, documento originale), non la memoria né una fonte di seconda mano. Ciò che non si dimostra non si scrive, o si scrive come stima o ipotesi dichiarata.
2. **Lo stesso dato è uguale ovunque.** Prima di pubblicarlo si cerca come lo scrivono le altre pagine e gli altri file, codice compreso; se non coincide, si stabilisce sulla fonte quello giusto e si allineano tutte le copie nello stesso lavoro.
3. **Prima di consegnare si prova a confutare il lavoro**, come un revisore ostile: ogni affermazione, numero, link, comando. Finito solo quando quella lettura non trova più niente.
4. **Tutti i controlli si eseguono.** Uno strumento che manca si installa: `apt-get update` e poi `apt-get install`, poi `pip` o `npm`, poi download dalla fonte ufficiale, poi il browser già presente sulla macchina. «Qui non si installa» non è una ragione. Se tutte le strade falliscono, il controllo lo fa la CI della pull request **prima** di unire, e il resoconto dice che cosa è stato provato e con quale errore.
5. **Ogni errore trovato diventa un controllo**, chiunque lo trovi: si corregge in tutte le copie e si aggiunge ciò che l'avrebbe fermato (voce di registro, test, controllo bloccante sulle PR, passo nell'agente che doveva vederlo).
6. **Le fonti si ricontrollano:** ciò che si pubblica porta la data della verifica e si ricontrolla a scadenza o quando la fonte cambia.
7. **Onestà sui limiti:** mai dichiarare conformità, certificazioni o assenza di errori non misurate; ciò che non si è potuto verificare si dice, con il motivo.
8. **Nei dubbi si chiede** (`autonomia.md`), con la raccomandazione accanto, e intanto si fa il resto.
9. **Sempre una prova di funzionamento** (12/11/2026): dopo ogni modifica si prova la cosa vera, non solo i controlli del repository. Per un sito: pagine, risorse e moduli sul sito pubblicato dopo il deploy; per un workflow: un giro di prova (simulazione dove esiste); per uno script: un'esecuzione reale. Se la prova fallisce si torna indietro e lo si dice; ciò che non si è potuto provare si dichiara. Le prove non inviano mai email né altri messaggi veri (istruzione del 12/11/2026: «Non mandare nulla come email»): un modulo che spedisce si prova fino alla risposta di validazione, senza far partire l'invio, oppure in locale con la posta finta.

## Controllo prima di dichiarare chiuso un lavoro
Fonte primaria controllata in sessione per ogni affermazione verificabile; dati coincidenti con quelli del repository (o tutte le copie allineate); tutti i controlli eseguiti; prova di funzionamento fatta sulla cosa vera; lettura di confutazione senza esiti; un controllo per ogni errore trovato. Se un punto non regge, il lavoro non è finito.
