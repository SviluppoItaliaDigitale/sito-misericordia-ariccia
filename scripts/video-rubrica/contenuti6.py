# «Che cosa le ha insegnato la vita?» (novembre 2026): poco più di un minuto per invitare al volontariato dell'ascolto,
# accanto alle persone anziane o con disabilità. Richiesta di Alessandro del 12/11/2026: una breve intervista, simulata,
# fra un giovane volontario e una persona anziana, che commuova chi ascolta.
# È UNA STORIA IMMAGINATA e il video lo dice due volte: l'etichetta «Una storia immaginata» nella prima scena e la voce
# narrante alla fine («Maria è un personaggio di fantasia»). Maria e Matteo non esistono: niente testimonianze inventate
# presentate come vere (.claude/rules/grafica.md, § «Limiti che restano»). I fatti sul servizio vengono dal sito
# (Diventa volontario, Servizi sociali), come negli altri video della campagna (contenuti4.py).
# Tre voci ElevenLabs (voce_luca.py, tabella VOCI): Matteo = «andrea», Maria = «angelina», chiusura = «luca».
# «regia» è il testo mandato alla voce, con le indicazioni di recitazione fra parentesi quadre (modello eleven_v4);
# «pausa» aggiunge secondi di silenzio dopo la battuta. Niente fruscii ai cambi di scena: qui serve il silenzio.
from contenuti import S
from contenuti4 import TEL, SER, CARD

def M(title, voce, regia, **kw):   # Matteo, il giovane volontario: fa le domande
    return S('Matteo, volontario', title, voce, 'int-domanda', voce_di='andrea', regia=regia, **kw)
def A(title, voce, regia, ill, tags=None, **kw):   # Maria, 87 anni: risponde
    return S('Maria, 87 anni', title, voce, ill, tags, voce_di='angelina', regia=regia, **kw)

V6 = {
'ascoltami': dict(nome='Che cosa le ha insegnato la vita?', num=0, serie=SER, brano='touching-moments-two-higher', voce='luca',
  card=CARD, scene=[
  M(['Che cosa le ha', 'insegnato la *vita*?'], 'Maria, lei ha ottantasette anni. Che cosa le ha insegnato la vita?',
    '[softly] [curious] Maria, lei ha ottantasette anni. [short pause] Che cosa le ha insegnato la vita?',
    tags=[['Una storia immaginata', .02]], sub='Maria, lei ha 87 anni. Che cosa le ha insegnato la vita?'),
  A(['Le cose importanti', 'non fanno *rumore*.'],
    'Che le cose importanti non fanno rumore. Una mano sulla spalla. Qualcuno che ti chiede «come stai?», e poi aspetta la risposta.',
    '[elderly voice] [warmly] [slowly] Che le cose importanti non fanno rumore. [short pause] Una mano sulla spalla. [short pause] Qualcuno che ti chiede «come stai?»… e poi aspetta la risposta.',
    'cose-piccole', [['Una mano sulla spalla', .42]]),
  M(['E a noi', '*giovani*?'], 'E a noi giovani, che cosa vorrebbe lasciare?', '[softly] E a noi giovani, che cosa vorrebbe lasciare?'),
  A(['Non abbiate', '*fretta*.'],
    'Non abbiate fretta. Io ho corso tutta la vita. E adesso che il tempo ce l\'ho, non ho più nessuno a cui darlo.',
    '[elderly voice] [softly] [slowly] Non abbiate fretta. Io ho corso tutta la vita. [sad] E adesso che il tempo ce l\'ho… non ho più nessuno a cui darlo.',
    'tempo-vuoto', [['Nessuno a cui darlo', .8]]),
  M(['Il momento', 'più *difficile*?'], 'Qual è il momento più difficile della giornata?',
    '[softly] [cautiously] Qual è il momento più difficile della giornata?'),
  A(['Apparecchio ancora', 'per *due*.'], 'La sera. Apparecchio ancora per due. Poi mi ricordo, e tolgo un piatto.',
    '[elderly voice] [sad] [softly] [slowly] La sera. [pause] Apparecchio ancora per due. [pause] [trembling voice] Poi mi ricordo… e tolgo un piatto.',
    'tavola-due', pausa=1.0),
  M(['Di che cosa', 'ha *bisogno*?'], 'E oggi, di che cosa ha bisogno?', '[softly] [warmly] E oggi, di che cosa ha bisogno?'),
  A(['Mi hai dato', '*tutto*.'],
    'Di niente, figlio mio. Solo di qualcuno che si sieda qui, e mi ascolti. Tu oggi non mi hai portato niente. Eppure mi hai dato tutto.',
    '[elderly voice] [warmly] [slowly] Di niente, figlio mio. [short pause] Solo di qualcuno che si sieda qui, e mi ascolti. [pause] [trembling voice] Tu oggi non mi hai portato niente. [short pause] Eppure mi hai dato tutto.',
    'insieme', [['Qualcuno che ascolti', .4]], pausa=0.8),
  S('Una storia immaginata', ['La solitudine', 'è *vera*.'], 'Maria è un personaggio di fantasia. La sua solitudine, no.', 'finestra-accesa'),
  S('Scrivici', ['Il primo passo:', 'un *messaggio*.'],
    'Tante persone anziane, o con disabilità, aspettano solo qualcuno che le ascolti. Scrivi «volontario» su WhatsApp al ' + TEL + '.',
    'prenota', [['Persone anziane', .15], ['Persone con disabilità', .3], ['348 4068657', .75, 1]],
    sub='Tante persone anziane, o con disabilità, aspettano solo qualcuno che le ascolti. Scrivi VOLONTARIO su WhatsApp al 348\u00a04068657.'),
  dict(chip='Esci dal post', title=['Anche ascoltare', 'è un *servizio*.'], voce='Misericordia di Ariccia. Anche ascoltare è un servizio.', ill='fine', tags=[]),
  ]),
}
