#!/usr/bin/env python3
"""Prova delle forme da non usare (FORME_SBAGLIATE in controlla_sito.py), sui controlli di ogni PR.

Per ogni regola ci sono esempi che il controllo deve segnalare e forme giuste che deve lasciar
passare. Nasce dal rilievo sulla PR 207 del 21/10/2026: la prima versione del controllo sulla firma
delle schede della Parola della domenica guardava solo l'inizio del valore, così una firma con un
nome in più o senza data passava. Gli esempi sono scritti a pezzi (virgolette con chr(34), motto
spezzato) perché il controllo, che legge anche scripts/, non segnali questo file.
Esce con 1 se un caso non va come deve. Solo libreria standard. Uso: prova_forme.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from controlla_sito import FORME_SBAGLIATE  # noqa: E402

Q = chr(34)  # virgolette doppie
MOTTO = "renda merito"


def firma(valore):
    return f"{Q}preparata_da{Q}: {Q}{valore}{Q}"


CASI = [  # (testo, deve essere segnalato)
    ("Che " + "Dio ve ne " + MOTTO, True),
    ("che " + "dio te ne " + MOTTO, True),
    ("Che " + "Dio gliene " + MOTTO, True),
    ("Che Iddio ve ne " + MOTTO, False),
    ("Che Iddio gliene " + MOTTO, False),
    (firma("Assistente, 2026-10-09"), True),
    (firma("Alessandro Cuollo, Assistente"), True),
    (firma("Alessandro Cuollo"), True),
    (firma("Alessandro Cuollo, 2026-10-21, Assistente"), True),
    (firma("Alessandro Cuollo, 2026-13-01"), True),
    (firma("IU0QVW, 2026-10-21"), True),
    (firma(""), True),
    (firma("Alessandro Cuollo, 2026-10-21"), False),
    (f"{Q}preparata_da{Q}:{Q}Alessandro Cuollo, 2026-10-09{Q}", False),
    # anafilassi (21/10/2026): la seconda dose si usa se i sintomi persistono
    ("Se dopo 5 minuti non " + "migliora e ha una seconda dose, si può ripetere.", True),
    ("If they have not " + "improved after **5 minutes** and have a second dose, it can be repeated.", True),
    ("Se dopo 5 minuti ha ancora i sintomi, anche se va un po' meglio, e ha una seconda dose, usala.", False),
    ("If symptoms are still present after **5 minutes**, even if slightly better, and they have a second dose, use it.", False),
    # soffocamento (18/10/2026): il 112 si chiama subito, non solo quando perde conoscenza
    ("Se perde conoscenza, accompagnalo a terra, " + "chiama il 112 e inizia la rianimazione.", True),
    ("Se perde conoscenza, accompagnalo a terra, " + "chiama '+U12+' e inizia la rianimazione.", True),
    ("Se perde conoscenza, accompagnalo a terra e inizia la rianimazione. Se nessuno ha ancora chiamato il 112, chiamalo subito.", False),
    # rubrica, correzioni del 21/10/2026
    ("Aspetta 15 minuti. Se non migliora, dagli " + "altro zucchero.", True),
    ("Aspetta 15 minuti. Se ha ancora i sintomi, dagli altro zucchero. Se non migliora, chiama il 112.", False),
    ("Spingi per un terzo del torace, circa 4 cm " + "nel lattante, 5 nel bambino.", True),
    ("circa quattro centimetri " + "nel lattante", True),
    ("to one third of its depth (about 4 cm " + "in an infant, 5 cm in a child)", True),
    ("Spingi per almeno un terzo del torace, ma mai più di 6 cm.", False),
    ("gauge(-400,-260,c,'≈ 4 " + "cm')", True),
    ("gauge(-400,-260,c,'≥ 1/3')", False),
    ("mettigli un cuscino " + "sotto la testa, coprilo", True),
    ("a cushion " + "under the head, a blanket", True),
    ("Metti qualcosa di morbido sotto la testa, come una giacca piegata.", False),
    ("Di solito si riprende in meno " + "di un minuto.", True),
    ("Di solito si riprende in fretta. Se non si riprende, chiama il 112.", False),
    ("mettilo in un sacchetto pulito e chiuso, e il sacchetto " + "nel ghiaccio.", True),
    ("in a clean, sealed bag, and the bag " + "in ice.", True),
    ("in un sacchetto chiuso, dentro un altro sacchetto con acqua e ghiaccio.", False),
    ("Porta con te la confezione, o una batteria " + "uguale: aiuta i medici.", True),
    ("Bring the **packaging** or an identical " + "battery.", True),
    ("Apri porte e finestre " + "ed esci all'aria aperta.", True),
    ("Esci subito all'aria aperta. Se puoi farlo senza fermarti, apri le finestre.", False),
    ("vista annebbiata e un ronzio " + "nelle orecchie", True),
    ("blurred vision, ringing " + "in the ears", True),
    ("o se mano o piede " + "sono freddi e senza sensibilità", True),
    ("or a hand or foot " + "that is cold and numb", True),
    ("una luce notturna verso il bagno, pantofole chiuse", False),
    # colpo di calore (1/11/2026, Ministero della Salute luglio 2026): raffreddamento per evaporazione, niente immersione
    # né doccia fredda; restano libere le ustioni («non ghiacciata») e il divieto «Niente vasca, doccia fredda o ghiaccio»
    ("bagnala con acqua fredda su tutto " + "il corpo, testa esclusa", True),
    ("Il modo più veloce è l'acqua fredda su tutto " + "il\n\n00:00:41.000 --> 00:00:44.000\ncorpo, dal collo in giù", True),
    ("(meglio una doccia o una " + "vasca fredda)", True),
    ("in una vasca, o sotto una " + "doccia fredda.", True),
    ("S('Acqua fredda', ['Acqua','*fredda*.'], '…', 'vasca-" + "fredda', [['Dal collo in giù', .35], ['Vasca o " + "doccia', .75]]),", True),
    ("Immergila in acqua " + "fredda fino al collo.", True),
    ("cool the whole body except the head with cold " + "water (a cold " + "shower or bath is best)", True),
    ("Immerse them in cold " + "water up to the neck.", True),
    ("bagnala tutta con acqua fresca o avvolgila in teli bagnati e falle aria di continuo", False),
    ("Niente vasca, doccia fredda o ghiaccio.", False),
    ("No bath, cold shower or ice.", False),
    ("l'acqua fredda non è ottimale, è preferibile il raffreddamento per evaporazione", False),
    ("sotto acqua corrente fresca (non ghiacciata) per almeno 20 minuti", False),
    ("rinfrescala con acqua fresca (non gelata) e panni bagnati", False),
    # DAE (1/11/2026): la formula della legge 116/2021, non la frase senza condizioni
    ("Il defibrillatore: chiunque " + "può usarlo", True),
    ("Può usarlo " + "chiunque, e usarlo presto salva la vita.", True),
    ("Anyone can " + "use it, and using it early saves lives.", True),
    ("S('Chiunque', ['Chiunque'," + "'può *usarlo*.'],", True),
    ("Puoi usarlo anche tu: se non c'è personale formato, anche chi non è formato può usarlo.", False),
    ("Even someone without training can use it if no trained person is present.", False),
    # dente (1/11/2026): latte o fisiologica, niente pellicola
    ("oppure avvolgilo nella " + "pellicola trasparente per alimenti", True),
    ("dove conservarlo (latte o " + "pellicola)", True),
    ("Mettilo nel latte o nella soluzione fisiologica.", False),
    ("Copri senza stringere con pellicola trasparente per alimenti.", False),
    # occhi (1/11/2026): almeno 15 minuti
    ("Continua a lungo, dieci, " + "venti minuti.", True),
    ("a palpebre aperte, **per 10-20 " + "minuti**, senza far colare l'acqua", True),
    ("Continua per almeno 15 minuti, senza fermarti.", False),
    ("IRC 2021 (irrigare subito con abbondante acqua pulita per 10-20 minuti)", False),
    # antitetanica (1/11/2026): 5 anni per le ferite a rischio
    ("e l'ultimo richiamo dell'antitetanica è di più di " + "dieci anni fa", True),
    ("l'ultimo richiamo è di più di " + "10 anni fa", True),
    ("['Richiamo oltre " + "10 anni', .6]", True),
    ("e l'ultimo richiamo è di più di 5 anni fa, o non lo ricordi", False),
    ("ISSalute, Tetano (richiamo ogni dieci anni nella popolazione generale)", False),
    # ustioni (1/11/2026): niente pasta per i denti, niente «fumo» fra i motivi del 112
    ("Niente ghiaccio, burro, olio o " + "dentifri" + "cio. E non bucare le bolle.", True),
    ("Niente ghiaccio, " + "dentifri" + "cio, burro, olio o altri rimedi casalinghi.", True),
    ("No ice, " + "tooth" + "paste, butter, oil or other home remedies.", True),
    ("don't apply ice, " + "tooth" + "paste, butter or oil", True),
    ("Sulle ust" + "ioni non mettere mai il " + "dentifri" + "cio.", True),
    ("Niente ghiaccio, burro, olio o creme. E non bucare le bolle.", False),
    ("No ice, butter, oil, creams or other home remedies.", False),
    ("Lavati i denti con il " + "dentifri" + "cio al fluoro.", False),
    ("se è da fiamme, elettrica o chimica, se ha respirato " + "fumo, o se è un bambino.", True),
    ("se è da fiamme, elettrica o chimica, o se è un bambino.", False),
    # laccio (1/11/2026): per chi ne ha uno, non «solo se addestrato»
    ("non si ferma, chi è addestrato può " + "usare un laccio emostatico", True),
    ("se la pressione non basta, chi è addestrato può " + "applicare un **laccio emostatico**", True),
    ("someone who is trained can " + "apply a **tourniquet**", True),
    ("['Solo se " + "addestrato', .2]", True),
    ("se la pressione non basta e hai un **laccio emostatico**, mettilo il prima possibile", False),
    # trauma cranico (1/11/2026): «vede male o doppio»
    ("se le pupille sono " + "diverse, o se un braccio", True),
    ("['Pupille " + "diverse', .6]", True),
    ("se vede male o doppio, o se un braccio o una gamba sono deboli", False),
    # occhio colpito dai botti (1/11/2026)
    ("Coprilo senza " + "premere e chiama il 112.", True),
    ("Injured eye: cover it without " + "pressing and call **112**.", True),
    ("Occhio colpito: non toccarlo e chiama il **112**.", False),
    ("premi sulla ferita con una garza, senza premere sull'osso.", False),
    # cadute degli anziani (1/11/2026)
    ("Chiama il **112** se ha battuto la testa (ancora " + "di più se prende anticoagulanti)", True),
    ("Chiama il 112 se ha battuto la testa, ancora " + "di più se prende anticoagulanti,", True),
    ("Call **112** if they hit their head (all " + "the more if they take anticoagulants", True),
    ("Se ha battuto la testa e prende anticoagulanti, va visto subito in pronto soccorso.", False),
    # arresto cardiaco (1/11/2026): «non respira normalmente», non solo «non respira»
    ("Arresto cardiaco: la persona non risponde e non " + "respira", True),
    ("Cardiac arrest (no response, not " + "breathing):", True),
    ("la persona non risponde e non respira normalmente", False),
    ("Cardiac arrest (no response, not breathing normally):", False),
    # revisione sanitaria della rubrica (1/11/2026)
    ("Mantieni la pressione per almeno " + "10 minuti, senza sollevare la garza.", True),
    ("pressione diretta per almeno " + "dieci minuti", True),
    ("S('Non mollare', ['Almeno','*10 " + "minuti*.'], 'Mantieni", True),
    ("Continua a premere, senza mollare, finché arrivano i soccorsi.", False),
    ("Stringi la parte morbida del naso per 10-15 minuti di fila.", False),
    ("Se il dolore dura più di " + "qualche minuto, o va e viene, chiama subito il 112.", True),
    ("Dolore o peso al petto che non passa " + "dopo pochi minuti?", True),
    ("If the pain **does not go away " + "after a few minutes**, call 112.", True),
    ("Con questi segni chiama subito il 112, anche se il dolore dura da pochi minuti o va e viene.", False),
    ("Medicine solo se lo dice " + "l\\'operatore del '+U12[3:]+'.", True),
    ("['Farmaci: chiedi " + "al 112', .85]", True),
    ("['Chiedi al 112', .85, 1]", False),
    ("taglia per lungo in " + "quattro parti gli alimenti tondi", True),
    ("taglia uva, pomodorini e olive in " + "quattro, per lungo.", True),
    ("cut grapes into " + "quarters, lengthways", True),
    ("['Uva tagliata " + "in 4', .75]", True),
    ("taglia gli alimenti tondi in pezzi piccoli, di mezzo centimetro, senza semi né noccioli.", False),
    ("Soffocamento: se non riesce a " + "tossire,\n\n00:00:34.000 --> 00:00:37.000\ncinque colpi tra le scapole", True),
    ("Se perde conoscenza, " + "112 e rianimazione.", True),
    ("Se non ci riesce, chiama subito il **112** (o fallo chiamare), poi **5 colpi tra le scapole**", False),
    ("Se non si riprende, chiama il 112 e guarda se respira normalmente." + "\n\n00:00:36.909 --> 00:00:41.014\nSe non respira normalmente", True),
    ("Se **non si riprende** in fretta, chiama il **112** e guarda se respira normalmente: " + "se non respira normalmente, inizia", True),
    ("If they don't come round quickly, call **112** and check whether they are breathing normally: " + "if not, start **CPR**.", True),
    ("If they don't come round quickly, call 112 and check their breathing: " + "if it is not normal, start CPR.", True),
    ("Se non si riprende, chiama il 112 e guarda se respira normalmente. Se respira normalmente, e non ha battuto forte cadendo, mettilo su un fianco. Se non respira normalmente, inizia la rianimazione.", False),
    ("If they don't come round straight away, call 112 and check their breathing: if it is normal and they did not hit themselves hard when falling, put them on their side; if it is not normal, start CPR.", False),
    ("Se non risponde, chiama il 112 e guarda se respira normalmente. Se non respira normalmente, inizia la rianimazione.", False),
    ("Poi una breve perdita di coscienza, di solito meno " + "di un minuto.", True),
    ("Then a brief loss of consciousness, usually less " + "than a minute.", True),
    ("Poi una breve perdita di coscienza, di solito pochi secondi.", False),
    ("Se è confuso, sonnolento o non trema più, " + "chiama il 112 e tienilo " + "sdraiato.", True),
    ("If they are confused, drowsy or no longer shivering, " + "call **112**.", True),
    ("Se pensi che sia in ipotermia, chiama il 112. Se è confuso, sonnolento o non trema più, è grave: muovilo il meno possibile.", False),
    ("mai direttamente sulla pelle, per una " + "ventina di minuti.", True),
    ("**Ghiaccio avvolto in un panno**, per circa " + "20 minuti.", True),
    ("**Ice wrapped in a cloth**, for about " + "20 minutes.", True),
    ("**Ghiaccio avvolto in un panno**, per non più di 20 minuti alla volta.", False),
    ("Resta calmo e aiutalo a respirare " + "lentamente.", True),
    ("Chiama il 112 se lo spray non " + "funziona, se non riesce a parlare", True),
    ("Call **112** if the inhaler isn't " + "enough, they cannot speak", True),
    ("aiutalo a usarlo nella " + "coscia.", True),
    ("Chiama il 112 se non ha lo spray, se lo spray non basta, se non riesce a parlare.", False),
    ("aiutalo a usarlo nella parte esterna della coscia.", False),
    ("Se non risponde, chiama il 112 e guarda se respira normalmente." + "\n\n00:00:11.428 --> 00:00:15.561\nSe risponde, tranquillizzalo", True),
    (f"- {Q}Se non risponde, chiama il **112** e guarda se respira " + f"normalmente.{Q}", True),
    ("Se non risponde, chiama il 112 e guarda se respira normalmente: se non respira normalmente, inizia la rianimazione. Se risponde, tranquillizzalo.", False),
    ("A volte tosse, bava, dolore, vomito, o rifiuta di " + "mangiare.", True),
    ("sometimes coughing, drooling, pain, vomiting or refusing " + "food", True),
    ("A volte tosse, bava, vomito, o fatica a deglutire.", False),
    ("Le finestre " + "aprile solo se puoi farlo senza fermarti.", True),
    ("Apri le finestre solo se puoi farlo senza fermarti.", False),
    ("Chiama il 112 se l'ustione è più grande " + "del palmo della sua mano", True),
    ("Chiama il 112 se l'ustione è grande o profonda, se è sul viso, sulle mani, sui piedi o sui genitali.", False),
    ("finché l'oggetto non esce o " + "arrivano i soccorsi.", True),
    ("finché l'oggetto non esce. Non infilare le dita in bocca alla cieca.", False),
    ("non fermarti finché non arrivano i soccorsi o finché non si " + "sveglia. Se siete in due", True),
    ("o finché non si sveglia e respira normalmente.", False),
    ("Con il livello 2 o 3 evita il sole tra le 12 " + "e le 18.", True),
    ("il condizionatore va bene tra **25 e 27 " + "gradi**.", True),
    ("Con il livello 2 o 3 evita il sole tra le 11 e le 18; condizionatore intorno a 25-26 gradi.", False),
]

errori = 0
for testo, atteso in CASI:
    segnalato = any(rx.search(testo) for rx, _ in FORME_SBAGLIATE)
    if segnalato != atteso:
        errori += 1
        print(f"❌ {testo!r}: {'segnalato' if segnalato else 'non segnalato'}, atteso il contrario")
print(f"{len(CASI) - errori}/{len(CASI)} casi come previsto")
sys.exit(1 if errori else 0)
