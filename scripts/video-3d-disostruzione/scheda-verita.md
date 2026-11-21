# Scheda di verità: «Soffocamento: come si libera la gola»

Tutto ciò che deve essere vero in scena, con la fonte, la pagina e i secondi del video orizzontale
`disostruzione-come-funziona.mp4`, che dura 166,8 s nella versione 2 (il verticale ha gli stessi tempi). Controllato sui fotogrammi del
render finale, uno ogni 0,5 s, il 20/11/2026 (versione 2, voce con «boccóne», «tèsta», «toràce» e «mèdico» corretti). I fogli sono in `verita/` nella cartella di lavoro.

Fonti:
- **IRC 12**: Linee guida RCP 2025, Italian Resuscitation Council, cap. 12 «Primo soccorso» (PDF del 15/04/2026). Pagine ricontrollate sul PDF il 21/11/2026: il riepilogo «Soffocamento in un adulto» è a p. 11 (prima era scritto p. 13), la figura 5 a p. 12, colpi e compressioni addominali a p. 28, alternanza, rianimazione e dita alla cieca a p. 29, la valutazione del medico alle pp. 11 e 30.
- **IRC 9**: stesse linee guida, cap. 9 «BLS pediatrico» (PDF del 02/04/2026), letto il 20/11/2026: p. 25 (compressioni sulla metà inferiore dello sterno in tutte le età, due pollici nel lattante), p. 29 (soffocamento: lattante prono sull'avambraccio appoggiato alla gamba, testa più in basso, colpi tra le scapole; poi supino sulle ginocchia, due pollici, «comprimere lo sterno in modo più deciso»; bambino piegato in avanti, colpi tra le scapole e compressioni addominali come nell'adulto), p. 30 (figure 16 e 17).
- **ISS**: ISSalute, «Tumore della laringe», pubblicata il 7/9/2026.
- **Dossier**: schede «soffocamento» e «soffocamento-lattante» di `content/dossier/primo-soccorso.md`.
- **Atlante**: BodyParts3D, misure di `anatomia_disostruzione.py`.

| # | Che cosa deve essere vero in scena | Fonte | Secondi |
|---|---|---|---|
| 1 | Esofago **dietro**, trachea **davanti**: nello spaccato del collo, visto da sinistra con il viso a sinistra dello schermo, la trachea azzurra sta a sinistra e l'esofago arancione a destra. | Atlante: a 1,39 m da terra la trachea va da 9,6 a 11,0 cm in profondità, l'esofago da 8,9 a 9,8 cm. ISS: la laringe sta sopra la trachea, il cibo va verso l'esofago. | 3,0-17,5 |
| 2 | Il boccone della deglutizione normale scende nell'**esofago** (arancione), non nella trachea; l'aria scende nella trachea. | ISS («convogliandolo correttamente verso l'esofago»). | 3,8-11,3 e 12,0-17,6 |
| 3 | L'**epiglottide** si abbassa e chiude l'ingresso della trachea mentre il boccone passa. | ISS («durante la deglutizione, grazie all'epiglottide … impedisce al cibo di penetrare nelle vie respiratorie»). | 4,9-6,5 e 12,0-17,2 |
| 4 | Il boccone che sbaglia strada si ferma nella **trachea** e l'aria si ferma (avviso «L'aria non passa»). | IRC 12, p. 28 (ostruzione completa: l'aria non passa). | fermo da 20,3; avviso 20,3-24,2 |
| 5 | «Stai soffocando?»: mani alla gola, non parla, non tossisce. | IRC 12, p. 11. | 24,4-30,4 |
| 6 | **Passo 1**: se tossisce, incoraggiarla a tossire (la tosse spinge l'aria e muove il boccone). | IRC 12, p. 11 e p. 28 («la tosse genera elevate e prolungate pressioni nelle vie aeree»). | 30,4-37,1 |
| 7 | **Passo 2**: se non tossisce e non parla, 112 in vivavoce. | IRC 12, p. 11 («chiamare immediatamente il sistema di emergenza»); Dossier (vivavoce). | 37,1-44,2 |
| 8 | **Passo 3**: persona **piegata in avanti**; mano di chi soccorre **tra le scapole, al centro della schiena**; fino a **5 colpi** con **la base del palmo** (scritto nella scheda del passo e nell'etichetta 3D; contatore 1-5). | IRC 12, p. 28 («eminenza ipotenar … tra le scapole al centro della schiena») e fig. 5 p. 12 (descrizione della figura: persona piegata in avanti); Dossier («piegala in avanti»). | 44,1-52,3; colpi a 45,9 · 46,6 · 47,4 · 48,2 · 49,0 |
| 9 | **Passo 4**: chi soccorre sta **dietro**; **pugno tra l'ombelico e il margine delle costole**, l'altra mano sopra, spinta **in dentro e in su**; **persona inclinata in avanti** (scritto nella scheda e disegnata più piegata); fino a **5 compressioni** (contatore). | IRC 12, p. 28 (dietro, braccia intorno alla parte alta dell'addome, inclinare in avanti, pugno tra ombelico e margine costale, trazione decisa verso l'interno e verso l'alto). | 52,6-67,4; spinte a 61,8 · 62,6 · 63,4 · 64,2 · 65,1 |
| 10 | La spinta fa **salire il diaframma** e l'aria esce con forza, come un colpo di tosse. | IRC 12, p. 29 (le compressioni generano pressioni nelle vie aeree); descrizione schematica, nota «schema». | 67,6-72,3 (rallentate a 68,5 e 70,5) |
| 11 | **Passo 5**: alternare 5 colpi e 5 compressioni finché il boccone esce (il boccone esce dalla bocca). | IRC 12, p. 11 e p. 29. | 73,1-79,0; esce a 78,3 |
| 12 | **Passo 6**: se perde conoscenza, a terra e rianimazione; le compressioni sul torace spingono l'aria (il boccone esce a 90,0). | IRC 12, p. 11 e p. 29 («le compressioni toraciche generano pressioni nelle vie aeree … possono potenzialmente risolvere l'ostruzione»). | 79,3-91,1; compressioni 82,1-90,9 |
| 13 | Niente dita in bocca alla cieca. | IRC 12, p. 11 e p. 29. | 91,5-96,0 |
| 14 | Dopo le compressioni addominali, sempre dal medico. | IRC 12, p. 11. | 96,3-101,3 |
| 15 | Lattante, **passo 1**: non piange e non tossisce bene: fai chiamare il 112. | Dossier (soffocamento-lattante). | 104,6-110,2 |
| 16 | Lattante, **passo 2**: **a pancia in giù sull'avambraccio** appoggiato alla gamba di chi soccorre, **testa più in basso**, mento sostenuto dalla mano; **5 pacche tra le scapole** (contatore). | IRC 9, p. 29 e fig. 16a p. 30; Dossier (soffocamento-lattante). | 110,1-119,6; pacche a 111,7 · 112,5 · 113,3 · 114,1 · 114,9 |
| 17 | Lattante, **passo 3**: **a pancia in su sulle ginocchia** di chi soccorre, testa sostenuta, **due pollici al centro del torace, sulla metà inferiore dello sterno**, **più decise che nella rianimazione**; 5 compressioni (contatore). | IRC 9, p. 25 (metà inferiore dello sterno), p. 29 (ginocchia, due pollici, «in modo più deciso») e fig. 16b p. 30; Dossier. | 119,6-127,1; compressioni a 121,2 · 121,9 · 122,7 · 123,4 · 124,2 |
| 18 | Lattante, **passo 4**: alternare 5 e 5; se perde conoscenza 5 soffi su bocca e naso, poi rianimazione. | Dossier. | 127,1-135,3 |
| 19 | Uva, pomodorini e olive tagliati in pezzi piccoli, di circa mezzo centimetro (acino intero no, in quattro sì). | Dossier. | 135,3-142,0 |
| 19 bis | **Dall'anno in su si fa come nell'adulto**: piegato in avanti, 5 colpi tra le scapole e 5 compressioni addominali, alternati (scheda, solo a schermo). | IRC 9, p. 29 e fig. 17 p. 30; Dossier («Dall'anno in su si fa come nell'adulto»). | 141,9-145,1 |
| 20 | **Ordine dei passi** nel riepilogo finale: 1 tossisce? → 2 chiama il 112 → 3 5 colpi e 5 compressioni alternati; poi corsi (328 8105399, 06 933 3717) e 112. | IRC 12, p. 11; telefoni dal registro `tel-amministrazione`, `tel-fisso`. | 145,3-166,8 |

Non disegnato dall'atlante, e coperto dalla nota «SCHEMA · NON IN SCALA»: il boccone, la gola (faringe), l'aria, i
segni gialli sul corpo, le sagome dei gesti, le figure del lattante e i movimenti del diaframma e dell'epiglottide.
