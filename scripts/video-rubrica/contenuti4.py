# Campagna volontari «Esci dal post. Entra nella squadra» (novembre-dicembre 2026): quattro video da un minuto,
# uno per ogni uscita del giovedì. Fatti presi solo dal sito: Diventa volontario, Servizi sociali, Formazione,
# trasporti; Colletta Alimentare del 14/11/2026 da bancoalimentare.it/colletta-alimentare, con la Coop di Genzano di Roma
# (Via Emilia Romagna 102) nell'elenco ufficiale dei punti vendita (verificata il 1/11/2026; la Coop è la scelta della
# Misericordia, Alessandro 1/11/2026). Voce Luca (ElevenLabs) e effetti sonori, scelta di Alessandro del 1/11/2026.
from contenuti import S
TEL = 'tre quattro otto, quattro zero sei, otto sei cinque sette'
SER = 'Esci dal post · Entra nella squadra'
CARD = dict(s='Diventa volontario · WhatsApp', tel='348 4068657')
SCRIVI = S('Scrivici', ['Il primo passo:', 'un *messaggio*.'],
           'Il primo passo è un messaggio. Scrivi «volontario» su WhatsApp al ' + TEL + '.', 'prenota', [['348 4068657', .6, 1]],
           sub='Il primo passo è un messaggio. Scrivi VOLONTARIO su WhatsApp al 348\u00a04068657.')  # spazio che non va a capo
FINE = dict(chip='Esci dal post', title=['Entra nella', '*squadra*.'],
            voce='Esci dal post. Entra nella squadra della Misericordia di Ariccia.', ill='fine', tags=[])
CHI_PUO = S('Chi può', ['Dai 16', 'agli *80 anni*.'],
            'Possono entrare in squadra donne e uomini dai sedici agli ottant\'anni. Non servono capacità speciali: impari tutto con noi.',
            'persone', [['Dai 16 agli 80 anni', .3], ['Impari con noi', .8]],
            sub='Possono entrare in squadra donne e uomini dai 16 agli 80 anni. Non servono capacità speciali: impari tutto con noi.')
def C(nome, scene, **kw):
    return dict(nome=nome, num=0, serie=SER, brano='morning', voce='luca', effetti=True, card=CARD, scene=scene, **kw)

V4 = {
# 1 · giovedì 12/11/2026, prima della Colletta Alimentare di sabato 14/11
'squadra-ascolto': C('Anche ascoltare è un servizio', [
  S('Esci dal post', ['Anche ascoltare', 'è un *servizio*.'],
    'Non tutti hanno bisogno di un\'ambulanza. Qualcuno ha bisogno, prima di tutto, di essere ascoltato.', 'ascolto'),
  S('Centro di Ascolto', ['Un problema', 'alla *volta*.'],
    'Al Centro di Ascolto i nostri volontari accolgono chi è in difficoltà e lo aiutano a orientarsi: una bolletta, una questione legale, gli aiuti alimentari.',
    'sportello', [['Bollette', .45], ['Questioni legali', .65], ['Aiuti alimentari', .88]]),
  S('Non da soli', ['Anche uno', '*psicologo*.'],
    'Nelle giornate del Centro di Ascolto, in sede c\'è anche il sostegno di uno psicologo.', 'mani-cuore', [['Sostegno psicologico', .7]]),
  S('Banco Alimentare', ['La spesa per chi', '*non ce la fa*.'],
    'Con il Banco Alimentare distribuiamo beni di prima necessità alle persone in difficoltà.', 'spesa', [['Beni di prima necessità', .7]]),
  S('Colletta Alimentare', ['Sabato', '*14 novembre*.'],
    'Sabato quattordici novembre torna in tutta Italia la Colletta Alimentare. Noi saremo alla Coop di Genzano di Roma, in via Emilia Romagna: vieni a donare la spesa per chi è in difficoltà.',
    'supermercato', [['Colletta Alimentare', .2], ['Coop di Genzano di Roma', .55], ['Dona la spesa', .85]],
    sub='Sabato 14 novembre torna in tutta Italia la Colletta Alimentare. Noi saremo alla Coop di Genzano di Roma, in via Emilia Romagna: vieni a donare la spesa per chi è in difficoltà.'),
  S('Cosa serve', ['Tempo', 'e *cuore*.'],
    'Per dare una mano servono un po\' di tempo e la voglia di stare accanto agli altri. La formazione la facciamo insieme.',
    'tempo-cuore', [['Un po\' di tempo', .3], ['Formazione insieme', .85]]),
  SCRIVI, FINE]),
# 2 · giovedì 19/11/2026: tutte le attività, non solo l'ambulanza (webinar W4: presentare tutte le attività)
'squadra-non-solo-ambulanza': C('Non serve guidare l\'ambulanza', [
  S('Esci dal post', ['Non serve guidare', 'l\'*ambulanza*.'],
    'Molti pensano che fare il volontario voglia dire guidare l\'ambulanza. Non è così: ci sono tanti modi per esserci.', 'ambulanza'),
  S('Accompagnare', ['Accanto a chi', 'si *cura*.'],
    'Puoi accompagnare chi deve curarsi: in ambulanza, in auto o con i mezzi attrezzati per la carrozzina.', 'trasporti',
    [['In auto', .45], ['Mezzi attrezzati', .8]]),
  S('Ogni giorno', ['La spesa,', 'il *medico*.'],
    'Puoi accompagnare chi è solo nelle cose di ogni giorno: la spesa, la posta, il medico, la farmacia.', 'auto-casa',
    [['La spesa', .4], ['La posta', .55], ['Il medico', .75]]),
  S('Ascoltare', ['Accogliere', 'le *famiglie*.'],
    'Puoi accogliere le famiglie al Centro di Ascolto e dare una mano al Banco Alimentare.', 'spesa',
    [['Centro di Ascolto', .4], ['Banco Alimentare', .8]]),
  S('Eventi', ['Alle feste', 'del *paese*.'],
    'Puoi esserci alle gare, alle feste e alle sagre dei Castelli Romani, con la squadra dell\'assistenza sanitaria.', 'eventi',
    [['Gare', .25], ['Feste', .35], ['Sagre', .45]]),
  S('Imparare', ['Primo soccorso', 'e *defibrillatore*.'],
    'E con i nostri corsi impari il primo soccorso e l\'uso del defibrillatore.', 'corso', [['Primo soccorso', .4], ['Defibrillatore', .8]]),
  S('Su misura', ['Scegli', 'il *tuo* servizio.'],
    'Ognuno trova il servizio più adatto al proprio tempo e a quello che sa fare. Possono entrare in squadra donne e uomini dai sedici agli ottant\'anni.',
    'persone', [['Il tuo tempo', .3], ['Dai 16 agli 80 anni', .85]],
    sub='Ognuno trova il servizio più adatto al proprio tempo e a quello che sa fare. Possono entrare in squadra donne e uomini dai 16 agli 80 anni.'),
  SCRIVI, FINE]),
# 3 · giovedì 26/11/2026: i trasporti
'squadra-trasporti': C('Accompagnare chi deve curarsi', [
  S('Esci dal post', ['Tre volte', 'a *settimana*.'],
    'C\'è chi deve fare la dialisi tre volte a settimana. E da solo non ci può arrivare.', 'auto-casa', [['Dialisi', .4]]),
  S('Dopo il ricovero', ['Il ritorno', 'a *casa*.'],
    'C\'è chi torna a casa dopo un ricovero e non può viaggiare in auto.', 'barella', [['In ambulanza', .7]]),
  S('In carrozzina', ['Arrivare', '*dove serve*.'],
    'E c\'è chi usa la carrozzina e deve arrivare a una visita, a scuola o al lavoro.', 'porta-a-porta',
    [['Una visita', .4], ['La scuola', .55], ['Il lavoro', .75]]),
  S('Chi accompagna', ['Dietro ogni', '*viaggio*.'],
    'Dietro ogni viaggio ci sono i nostri volontari: in ambulanza, in auto o con i mezzi con la pedana.', 'trasporti',
    [['Ambulanza', .3], ['Auto', .45], ['Mezzi con pedana', .8]]),
  S('Non solo guidare', ['Ti prendiamo,', 'ti *aspettiamo*.'],
    'Non si tratta solo di guidare: si va a prendere la persona a casa, la si aspetta e la si riporta indietro, con calma.',
    'mani-strette', [['A casa', .3], ['Si aspetta', .55], ['Con calma', .9]]),
  S('Prima si impara', ['La formazione', '*prima*.'],
    'Prima del servizio c\'è la formazione: la facciamo insieme, passo dopo passo, fino a quando sei pronto.', 'passi3',
    [['Passo dopo passo', .5], ['Quando sei pronto', .85]]),
  CHI_PUO, SCRIVI, FINE]),
# 4 · giovedì 3/12/2026: formazione ed eventi, due giorni prima della Giornata del volontariato
'squadra-formazione': C('Impari tutto con noi', [
  S('Esci dal post', ['Non sai niente', 'di *primo soccorso*?'],
    'Non sai niente di primo soccorso? Va benissimo: si comincia tutti così.', 'corso'),
  S('Insieme', ['Passo', 'dopo *passo*.'],
    'Alla Misericordia di Ariccia la formazione viene prima del servizio, e la facciamo insieme, passo dopo passo.', 'passi3',
    [['Prima del servizio', .55], ['Insieme', .85]]),
  S('I corsi', ['Rianimazione e', '*defibrillatore*.'],
    'Ci sono i corsi di primo soccorso, quelli per usare il defibrillatore sull\'adulto e sul bambino, e il percorso da soccorritore.',
    'dae', [['Primo soccorso', .25], ['BLSD e P-BLSD', .6], ['Soccorritore', .88]]),
  S('In campo', ['Poi', '*in squadra*.'],
    'Poi si va in campo: alle gare, alle feste e alle manifestazioni dei Castelli Romani, sempre in squadra.', 'eventi',
    [['Gare', .3], ['Feste', .4], ['Sempre in squadra', .85]]),
  S('Per tutti', ['Corsi', '*aperti a tutti*.'],
    'I corsi di primo soccorso sono aperti a tutti. Anche se non diventi volontario, impari cosa fare nei primi minuti di un\'emergenza.',
    'rcp-mini', [['Aperti a tutti', .3], ['I primi minuti', .85]]),
  CHI_PUO, SCRIVI, FINE]),
}
