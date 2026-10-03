# Video dei servizi: accompagnamento nella vita quotidiana e «L'ultimo viaggio» (ottobre 2026).
from contenuti import S
TEL = 'tre quattro otto, quattro zero sei, otto sei cinque sette'
V3 = {
'accompagnamento-sociale': dict(nome='Accompagnamento sociale', num=0, serie='I nostri servizi · Accompagnamento sociale',
  card=dict(s='Prenota un accompagnamento', tel='348 4068657'), scene=[
  S('Accompagnamento', ['Le cose','di *ogni giorno*.'], 'La spesa, la posta, la banca. Per chi non può muoversi da solo, sono le cose più difficili.', 'auto-casa'),
  S('La spesa', ['Al','*supermercato*.'], 'Ti accompagniamo a fare la spesa. Il volontario spinge il carrello e porta le buste fino a casa.', 'supermercato', [['Il carrello', .45], ['Le buste fino a casa', .85]]),
  S('Posta e banca', ['Pensione','e *bollette*.'], 'Alla posta e in banca: per ritirare la pensione, pagare una bolletta, sbrigare una pratica.', 'posta-banca', [['Pensione', .4], ['Bollette', .6], ['Pratiche', .85]]),
  S('Farmacia e medico', ['Ricette','e *medicine*.'], 'Dal medico di famiglia per le ricette, e poi in farmacia a prendere le medicine.', 'farmacia', [['Medico di famiglia', .3], ['Farmacia', .75]]),
  S('Le piccole gioie', ['Anche','il *parrucchiere*.'], 'E anche le piccole cose che fanno stare bene: il parrucchiere, la messa della domenica, una visita al cimitero.', 'piccole-gioie', [['Parrucchiere', .45], ['La messa', .65], ['Il cimitero', .88]]),
  S('Gli affetti', ['Una visita','a chi *ami*.'], 'Una visita a un familiare o a un amico, a casa, in ospedale o in una residenza per anziani.', 'visita', [['Familiari', .3], ['Amici', .45], ['In residenza', .85]]),
  S('Porta a porta', ['Ti prendiamo,','ti *aspettiamo*.'], 'Ti veniamo a prendere a casa, ti aspettiamo, e ti riportiamo indietro. Anche in carrozzina, con i mezzi con la pedana.', 'porta-a-porta', [['Da casa', .2], ['Ti aspettiamo', .45], ['Mezzi con pedana', .85]]),
  S('Per chi', ['Nessuno','resta *solo*.'], 'Per gli anziani soli, per chi ha una disabilità, per chi non guida o non ha nessuno a cui chiedere un passaggio.', 'chi-serve', [['Anziani soli', .2], ['Disabilità', .4], ['Senza un passaggio', .85]]),
  S('Prenota', ['Chiamaci','con *anticipo*.'], 'Per prenotare chiamaci, o scrivici su WhatsApp, al '+TEL+', con qualche giorno di anticipo.', 'prenota', [['348 4068657', .6, 1], ['Qualche giorno prima', .9]],
    sub='Per prenotare chiamaci, o scrivici su WhatsApp, al 348 4068657, con qualche giorno di anticipo.'),
  dict(chip='Misericordia di Ariccia', title=['Accanto a te,','*ogni giorno*.'], voce='Misericordia di Ariccia: accanto a te, ogni giorno.', ill='fine', tags=[]),
  ]),
"ultimo-viaggio": dict(nome="L'ultimo viaggio", num=0, serie="I nostri servizi · L'ultimo viaggio", bpm=66, musica='dolce', voce_lenta=1.12,
  card=dict(s="L'ultimo viaggio · informazioni", tel='348 4068657'), scene=[
  S("L'ultimo viaggio", ['Quando il tempo','diventa *prezioso*.'], "C'è un momento in cui il tempo diventa prezioso. E un desiderio, l'ultimo, non può più aspettare.", 'mare'),
  S('Il mare', ['Rivedere','il *mare*.'], "Rivedere il mare, un'ultima volta. Sentire il vento sul viso, il rumore delle onde, e guardare l'orizzonte come da bambini.", 'mare-barella', [['Il vento sul viso', .4], ['Le onde', .6], ["L'orizzonte", .85]]),
  S('Le radici', ['Tornare','*a casa*.'], 'Tornare nel paese dove si è nati. Sentire di nuovo le campane della chiesa dove ci si è sposati.', 'paese', [['Il paese natale', .35], ['Le campane', .8]]),
  S('La casa', ['Il giardino','di una *vita*.'], "Rivedere la propria casa, il giardino curato per una vita, l'albero piantato quando è nato il primo figlio.", 'casa-giardino', [['La casa', .25], ['Il giardino', .5], ["L'albero", .85]]),
  S('La famiglia', ['Esserci,','*ancora* una volta.'], "Esserci, anche solo per un'ora, al matrimonio di un nipote. Vederlo felice, e sorridere insieme.", 'festa', [["Anche solo un'ora", .4], ['Sorridere insieme', .85]]),
  S('Le mani', ['Non portiamo','solo una *persona*.'], 'Non portiamo solo una persona. Portiamo i suoi ricordi, le sue emozioni, e le mani di chi le vuole bene.', 'mani', [['I ricordi', .45], ['Le emozioni', .6], ['Le mani di chi ama', .9]]),
  S('Come', ['Accanto,','*fino alla fine*.'], "Lo facciamo in ambulanza, con la barella, in sicurezza, e con i nostri volontari accanto, dal primo all'ultimo momento.", 'barella', [['Ambulanza e barella', .3], ['In sicurezza', .5], ["Fino all'ultimo momento", .9]]),
  S('Insieme', ['Con chi','gli *vuole bene*.'], 'Un familiare viene con noi. Organizziamo tutto insieme, con calma, con rispetto e con delicatezza.', 'famiglia', [['Un familiare con noi', .3], ['Con rispetto', .7], ['Con delicatezza', .9]]),
  S('Un sogno', ['Nessun desiderio','resti un *sogno*.'], 'Perché nessun desiderio resti soltanto un sogno.', 'tramonto-finale'),
  S('Chiamaci', ['Parliamone','*insieme*.'], 'Se una persona che ami ha un ultimo desiderio, chiamaci al '+TEL+'. Ne parliamo insieme, con il cuore.', 'prenota', [['348 4068657', .6, 1]],
    sub='Se una persona che ami ha un ultimo desiderio, chiamaci al 348 4068657. Ne parliamo insieme, con il cuore.'),
  dict(chip='Misericordia di Ariccia', title=['Ogni desiderio','*merita* un viaggio.'], voce='Ogni desiderio merita un viaggio.', ill='fine', tags=[]),
  ]),
}
