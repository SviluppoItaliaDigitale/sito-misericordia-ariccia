# Testi delle routine di Claude — sito della Misericordia di Ariccia

Copia di riferimento dei testi delle routine di Claude che lavorano su questo repository. La fonte operativa resta la routine (https://claude.ai/code/routines/<id>); questa cartella versiona il testo e serve a chi lavora al posto di Claude quando è ferma: ChatGPT esegue le routine di oggi da questi file (`AGENTS.md`, § «Quando Claude è ferma, lavori tu al suo posto»). Quando cambi il testo di una routine, cambi anche il suo file nello stesso lavoro.

Orari in ora italiana. Le routine di Claude con l'orario fissato in UTC si spostano di un'ora con il cambio dell'ora: qui sono scritti tutti e due.

| Routine | Quando | Testo | Già fatta oggi se… |
|---|---|---|---|
| Parola della domenica e delle feste — preparazione (`trig_01DWXFsFoukfHxmHzWrkra7f`) | ogni giorno alle 08:55 italiane: prepara le domeniche e le feste dei prossimi 7 giorni senza scheda | [`parola-domenica-preparazione.md`](parola-domenica-preparazione.md) | ogni giorno di `calendario.py prossimi 7` ha già la sua scheda su `main` (vedi `docs/parola-della-domenica.md`) |
| Parola della domenica e delle feste — recupero notturno (`trig_01UcL5nUFwVLGN27GafGetjj`) | ogni notte alle 01:55 italiane, utile solo nei giorni della Parola (il carosello deve essere online prima delle 04:47) | [`parola-domenica-recupero.md`](parola-domenica-recupero.md) | oggi non è un giorno della Parola (`calendario.py oggi` esce con 1) o il carosello di oggi è già online |
| Verifica dati del sito (`trig_01QHuBqV7rS8PL2Ue3MDgtEk`) | ogni lunedì alle 05:54 italiane | [`verifica-dati.md`](verifica-dati.md) | date `verificato` di oggi in `data/dati_da_verificare.yaml` |
| Riparazione guasti dei siti (Misericordia Ariccia, Cooprimavera) (`trig_01RBJ5MxdCUxjeq5UDGu5Lej`) | ogni giorno alle 15:13 italiane con l'ora legale, alle 14:13 con l'ora solare | [`riparazione-guasti-siti.md`](riparazione-guasti-siti.md) | issue `fonte-rotta`, «Salute» e «Link rotti» dei due siti chiuse o commentate dall'account di Alessandro dopo le 15:13 (14:13 con l'ora solare); quando non c'è nulla da riparare non lascia segni, e rifarla comporta solo letture |
| Promemoria una tantum (10/11, 5/12, 10/12/2026) | alla data scritta nel file | [`promemoria-una-tantum.md`](promemoria-una-tantum.md) | resoconto o proposta già mandati ad Alessandro quel giorno; chi lavora al posto di Claude non li vede, quindi la rifà: i controlli sono letture, si corregge solo ciò che non va e la proposta chiede il via prima di produrre |

## Routine spente

- «Monitoraggio Liturgia del giorno» (`trig_01QHWD37UUth9jJ8YwPpEb6W`): spenta dal 21/10/2026. I suoi controlli li fa ogni notte il workflow `guardiano-liturgia.yml`, che non ha bisogno di nessuna intelligenza artificiale (`CLAUDE.md`, § «Controllo automatico — Liturgia del giorno»).
- Le due riserve della Parola della domenica nella chat di Claude (`trig_01YAwmyhUffYN1dAi14RvSnM`, dal mercoledì al sabato alle 14:55, e `trig_01VkyMRaGn8EuUmTk34cb5iF`, domenica alle 03:10): spente dal 21/10/2026, perché ripetevano la preparazione e il recupero notturno, che ripartono da soli dal giovedì al sabato e la domenica all'1:55.

Elenco di tutte le routine di Alessandro, anche degli altri repository, e che cosa vuol dire «fai le routine di oggi»: `ROUTINE.md` del repository `assistente-personale`.
