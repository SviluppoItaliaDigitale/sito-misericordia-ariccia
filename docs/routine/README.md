# Testi delle routine di Claude — sito della Misericordia di Ariccia

Copia di riferimento dei testi delle routine di Claude che lavorano su questo repository. La fonte operativa resta la routine (https://claude.ai/code/routines/<id>); questa cartella versiona il testo e serve a chi lavora al posto di Claude quando è ferma: ChatGPT esegue le routine di oggi da questi file (`AGENTS.md`, § «Quando Claude è fermo, lavori tu al suo posto»). Quando cambi il testo di una routine, cambi anche il suo file nello stesso lavoro.

Orari in ora italiana. Le routine di Claude con l'orario fissato in UTC si spostano di un'ora con il cambio dell'ora: qui sono scritti tutti e due.

| Routine | Quando | Testo | Già fatta oggi se… |
|---|---|---|---|
| Monitoraggio Liturgia del giorno (`trig_01QHWD37UUth9jJ8YwPpEb6W`) | ogni giorno alle 08:00 italiane con l'ora legale, alle 07:00 con l'ora solare | [`liturgia-del-giorno.md`](liturgia-del-giorno.md) | non lascia tracce se va tutto bene: i controlli sono solo letture, quindi rifalli sempre |
| Parola della domenica — preparazione (`trig_01DWXFsFoukfHxmHzWrkra7f`) | dal mercoledì al sabato alle 08:55 italiane (dopo il mercoledì solo come riserva) | [`parola-domenica-preparazione.md`](parola-domenica-preparazione.md) | la Parola della domenica che viene è già su `main` (vedi `docs/parola-della-domenica.md`) |
| Parola della domenica — recupero notturno (`trig_01UcL5nUFwVLGN27GafGetjj`) | ogni domenica alle 01:55 italiane (il carosello deve essere online prima delle 04:47) | [`parola-domenica-recupero.md`](parola-domenica-recupero.md) | il carosello di oggi è già online |
| Verifica dati del sito (`trig_01QHuBqV7rS8PL2Ue3MDgtEk`) | ogni giorno alle 05:54 italiane | [`verifica-dati.md`](verifica-dati.md) | date `verificato` di oggi in `data/dati_da_verificare.yaml` |
| Riparazione guasti dei siti (Misericordia Ariccia, Cooprimavera) (`trig_01RBJ5MxdCUxjeq5UDGu5Lej`) | ogni giorno alle 15:13 italiane con l'ora legale, alle 14:13 con l'ora solare | [`riparazione-guasti-siti.md`](riparazione-guasti-siti.md) | commenti di oggi sulle issue `fonte-rotta`, «Salute» e «Link rotti» dei due siti |
| Promemoria una tantum (10/11, 5/12, 10/12/2026) | alla data scritta nel file | [`promemoria-una-tantum.md`](promemoria-una-tantum.md) | resoconto già mandato ad Alessandro quel giorno |

Elenco di tutte le routine di Alessandro, anche degli altri repository, e che cosa vuol dire «fai le routine di oggi»: `ROUTINE.md` del repository `assistente-personale`.
