#!/usr/bin/env python3
"""Controlli di salute del sito (workflow «Controlli del sito», issue «Stato del sito»).

Legge la build di Hugo (cartella public/) e il repo, e scrive un rapporto in Markdown:
  1. link interni, immagini, video e sottotitoli che puntano a file inesistenti;
  2. script inline non coperti dagli hash della Content-Security-Policy in static/.htaccess;
  3. registro dei dati (data/dati_da_verificare.yaml): voci scadute e contenuti sanitari senza revisione;
  4. news programmate in uscita nei prossimi 14 giorni, con la data del controllo editoriale;
  5. forme già corrette che non devono tornare (FORME_SBAGLIATE), cercate nei sorgenti del sito
     e nei generatori di video, grafiche e post (CARTELLE_TESTI), così si vedono anche nelle news
     programmate e prima che un video o una grafica le renda in un file che nessuno rilegge;
  6. firma «Misericordia di Ariccia» e cornice di microtesto: il segno del motore nelle grafiche e nelle copertine
     dei video delle news e nelle pagine della Parola che escono dal 22/10/2026, la firma in ogni modello grafico;
  7. con --live: pagine principali online e build pubblicata uguale a quella attesa.
Solo libreria standard. Uso: controlla_sito.py public [--live] [--report out.md] [--csp]
  --csp: stampa gli hash degli script inline da copiare in static/.htaccess ed esce.
Esce con codice 1 se ci sono link interni rotti, script inline fuori dalla CSP, forme da non usare o grafiche
senza firma e cornice."""
import base64, datetime as dt, glob, hashlib, html, os, re, sys, time, urllib.request
from pathlib import Path
from urllib.parse import urlsplit, unquote, urljoin

REPO = Path(__file__).resolve().parents[2]
SITO = "https://www.misericordia-ariccia.it"
PAGINE_LIVE = ["/", "/richiedi-trasporto/", "/servizi/", "/contatti/", "/numeri-utili/",
               "/dossier/primo-soccorso/", "/sostienici/", "/diventa-volontario/", "/privacy/", "/en/"]
FREQ = {"giornaliera": 1, "settimanale": 7, "mensile": 30, "annuale": 365}
oggi = dt.datetime.now(dt.timezone(dt.timedelta(hours=1))).date()  # data italiana (± l'ora legale basta)
# Errori già corretti che non devono tornare (regola qualità, punto 5): espressione e forma giusta.
FORME_SBAGLIATE = [
    (re.compile(r"\bche\s+dio\s+(?:te\s+ne|ve\s+ne|gliene)\s+renda\s+merito", re.I),
     "il motto si scrive con «Iddio» («Che Iddio te ne renda merito»), come nello statuto tipo delle "
     "Misericordie («Che Iddio gliene renda merito») e nel glossario del sito (21/10/2026)"),
    # Il valore intero, non solo l'inizio: «Alessandro Cuollo, <altro>» o il nome senza data non passano.
    (re.compile(r'"preparata_da"\s*:\s*"(?!Alessandro Cuollo, 20\d\d-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])")[^"]*"'),
     "le schede della Parola della domenica si firmano esattamente «Alessandro Cuollo, AAAA-MM-GG» (la data "
     "di preparazione e nient'altro), mai con il nome di uno strumento: regola sulla firma dei lavori (21/10/2026)"),
    (re.compile(r"non\s+migliora\s+e\s+ha\s+una\s+seconda\s+dose|have\s+not\s+improved\s+after\s+\**5\s+minutes\**\s+and\s+have\s+a\s+second\s+dose", re.I),
     "anafilassi: la seconda dose si usa se i sintomi PERSISTONO dopo 5 minuti, non solo «se non migliora» "
     "(IRC 2025, cap. 12; corretto il 21/10/2026)"),
    (re.compile(r"perde\s+conoscenza,\s+accompagnalo\s+a\s+terra,\s+chiama\s+(?:il\s+112|'\+U12\+')\s+e\s+inizia", re.I),
     "soffocamento: il 112 si chiama subito, quando non riesce più a tossire o a parlare, non solo quando "
     "perde conoscenza (IRC 2025, cap. 12; corretto il 18/10/2026)"),
    # Correzioni della rubrica approvate il 21/10/2026 (issue #147), sui capitoli IRC 2025 4, 9 e 12.
    (re.compile(r"se\s+non\s+migliora,\s+dagli\s+altro\s+zucchero", re.I),
     "ipoglicemia: lo zucchero si ripete se dopo 15 minuti ha ANCORA I SINTOMI; se non migliora si chiama il 112 "
     "(IRC 2025, cap. 12)"),
    (re.compile(r"circa\s+(?:4|quattro)\s+(?:cm|centimetri)\s+nel\s+lattante|about\s+4\s+cm\s+in\s+an\s+infant|≈\s*4\s*cm", re.I),
     "rianimazione del bambino: almeno un terzo del torace, mai più di 6 cm; i «4-5 cm» sono del 2021 (IRC 2025, cap. 9)"),
    (re.compile(r"cuscino\s+sotto\s+la\s+testa|cushion\s+under\s+the\s+head", re.I),
     "cadute: la testa non si solleva con un cuscino, va tenuta ferma se ha battuto la testa o ha male al collo "
     "(IRC 2025, cap. 12)"),
    (re.compile(r"si\s+riprende\s+in\s+meno\s+di\s+un\s+minuto", re.I),
     "svenimento: se non si riprende si chiama il 112 e si guarda se respira; niente attesa di un minuto "
     "(IRC 2025, cap. 4 e 12)"),
    (re.compile(r"e\s+il\s+sacchetto\s+nel\s+ghiaccio|and\s+the\s+bag\s+in\s+ice", re.I),
     "parte amputata: garza bagnata, sacchetto chiuso dentro un altro sacchetto con acqua e ghiaccio, mai a contatto "
     "col ghiaccio, in ospedale con il ferito (IRC 2025, cap. 12)"),
    # Frasi della rubrica senza fonte o in contrasto con le fonti, tolte o corrette il 21/10/2026 (issue #147).
    (re.compile(r"porta\s+(?:con\s+te\s+)?la\s+\**confezione\**,?\s+o\s+una\s+batteria\s+uguale|bring\s+the\s+\**packaging\**\s+or\s+an\s+identical\s+battery", re.I),
     "batterie a bottone: niente cibo né bevande, sopra i 12 mesi il miele mentre si va al pronto soccorso "
     "(Ospedale Bambino Gesù); la confezione non è nella fonte"),
    (re.compile(r"apri\s+porte\s+e\s+finestre\s+ed\s+esci|open\s+doors\s+and\s+windows\s+and\s+get\s+out", re.I),
     "monossido: prima si esce all'aria aperta (NHS); le finestre si aprono solo se si può farlo senza fermarsi (Regione Toscana)"),
    (re.compile(r"ronzio\s+nelle\s+orecchie|ringing\s+in\s+the\s+ears", re.I),
     "svenimento: i segni prima sono sudore, nausea, capogiri, vista annebbiata (NHS) e pallore (Auxologico); "
     "il ronzio non è nelle fonti"),
    (re.compile(r"mano\s+o\s+piede\s+(?:sono\s+)?freddi|hand\s+or\s+foot\s+that\s+is\s+cold", re.I),
     "fratture: le estremità fredde non sono un motivo per il 112 nelle fonti (per l'NHS il formicolio è da 111); "
     "si chiama per frattura esposta, anca, femore, schiena, collo o dolore fortissimo"),
    # Colpo di calore: il Ministero della Salute (Linee di indirizzo caldo, luglio 2026, p. 14) scrive che l'acqua fredda
    # «non è ottimale» e preferisce il raffreddamento per evaporazione. Si bloccano l'immersione e la doccia fredda come
    # consiglio ai cittadini; restano libere le ustioni («acqua corrente fresca, non ghiacciata») e il divieto
    # «Niente vasca, doccia fredda o ghiaccio». Il gruppo (?:\s|\d|:|\.|-->)+ salta il passaggio fra due sottotitoli.
    (re.compile(r"acqua(?:\s|\d|:|\.|-->)+fredda(?:\s|\d|:|\.|-->)+su(?:\s|\d|:|\.|-->)+tutto(?:\s|\d|:|\.|-->)+il(?:\s|\d|:|\.|-->)+corpo"
                r"|(?:vasca|doccia),?(?:\s|\d|:|\.|-->)+o(?:\s|\d|:|\.|-->)+(?:sotto\s+)?(?:una\s+)?(?:vasca|doccia)\s+fredda"
                r"|immergil[oa]\s+(?:\w+\s+){0,2}in\s+acqua\s+fredda|\['Vasca\s+o\s+doccia'|'vasca-fredd[a]'"
                r"|cold\s+(?:shower|bath)\s+or\s+(?:shower|bath)|(?:with|in)\s+cold\s+water\s+\((?:a\s+)?cold"
                r"|whole\s+body\s+except\s+the\s+head\s+with\s+cold\s+water|immerse\s+(?:them|the\s+person)\s+in\s+cold\s+water", re.I),
     "colpo di calore: si raffredda per evaporazione, bagnando il corpo con acqua fresca o avvolgendolo in teli bagnati e "
     "facendo aria di continuo; niente vasca, doccia fredda o ghiaccio, perché l'acqua fredda «non è ottimale» (Ministero "
     "della Salute, Linee di indirizzo per la prevenzione degli effetti del caldo, luglio 2026, p. 14; corretto il 1/11/2026)"),
    # Altre correzioni della 3ª serie del 1/11/2026, sulle fonti statali più aggiornate.
    (re.compile(r"chiunque\s+può\s+usarlo|può\s+usarlo\s+chiunque|anyone\s+can\s+use\s+it|\['Chiunque',\s*'può", re.I),
     "DAE: la legge 116/2021 (art. 3) lo consente a chi non è formato se non c'è personale formato, in caso di sospetto "
     "arresto cardiaco; si scrive «Puoi usarlo anche tu» o la formula della legge, non la frase senza condizioni "
     "(formula approvata da Alessandro il 9/10/2026; corretto il 1/11/2026)"),
    (re.compile(r"avvolgilo\s+nella\s+pellicola|latte\s+o\s+pellicola|\['Pellicol[a]',|wrap\s+it\s+in\s+cling\s*film", re.I),
     "dente caduto: nel latte o nella soluzione fisiologica, se non c'è altro nella saliva; la pellicola non è nella fonte "
     "statale (Ministero della Salute, Linee guida traumi dentali 2018, pp. 13 e 17; corretto il 1/11/2026)"),
    (re.compile(r"Continua\s+a\s+lungo,\s+(?:dieci,\s+venti|10-20)\s+minuti|\['10-20\s+minuti',|per\s+\**10-20\s+minuti\**,\s+senza\s+far\s+colare", re.I),
     "occhi: si sciacqua per almeno 15 minuti (Centro Antiveleni dell'AOU Careggi, 24/02/2026; corretto il 1/11/2026)"),
    (re.compile(r"(?:richiamo|dose)[^.\n]{0,40}?di\s+più\s+di\s+(?:10|dieci)\s+anni\s+fa|Richiamo\s+oltre\s+10\s+anni", re.I),
     "antitetanica: per ferite profonde, sporche, punture e morsi si va dal medico se l'ultima dose è di più di 5 anni fa "
     "(Ministero della Salute, circolare del 3/7/2018; corretto il 1/11/2026)"),
    # Serie 1 e 2, seconda revisione del 1/11/2026 sulle fonti statali più aggiornate.
    (re.compile(r"(?:u[s]tion|scottatur|b[u]rn)[^\n]{0,150}?(?:d[e]ntifricio|t[o]othpaste)|(?:d[e]ntifricio|t[o]othpaste)[^\n]{0,150}?(?:u[s]tion|scottatur|b[u]rn)"
                r"|(?:ghiaccio|burro|olio),?\s+(?:o\s+)?d[e]ntifricio|d[e]ntifricio,\s+burro|(?:ice|butter|oil),?\s+(?:or\s+)?t[o]othpaste|t[o]othpaste,\s+butter", re.I),
     "ustioni: niente ghiaccio, burro, olio o creme; la pasta per i denti non è in nessuna fonte ufficiale (CRI, Ustioni; NHS, "
     "Burns and scalds, 31/03/2026; IFRC 2025, pp. 290 e 292; corretto il 1/11/2026)"),
    (re.compile(r"se\s+ha\s+respirato\s+fumo,\s+o\s+se\s+è\s+un\s+bambino|\['Fumo',\s*\.56\]", re.I),
     "ustioni: fra i motivi del 112 non c'è il fumo respirato, che non è nelle fonti (IFRC 2025, p. 290); i fumi hanno le schede "
     "avvelenamento e monossido (corretto il 1/11/2026)"),
    (re.compile(r"chi\s+è\s+addestrato\s+può\s+(?:usare|applicare)\s+un\s+\**laccio|someone\s+who\s+is\s+trained\s+can\s+apply\s+a\s+\**tourniquet"
                r"|\['Solo\s+se\s+addestrato'", re.I),
     "laccio emostatico: se la pressione non basta, lo mette chi ne ha uno, senza limiti di addestramento (IRC 2025, cap. 12, "
     "pp. 15 e 35; IFRC 2025, p. 256; corretto il 1/11/2026)"),
    (re.compile(r"le\s+pupille\s+sono\s+diverse|\['Pupille\s+diverse'|unequal\s+pupils|pupils\s+(?:are\s+)?(?:of\s+)?different\s+sizes?", re.I),
     "trauma cranico: il segno delle fonti è «vede male o doppio», non le pupille diverse (ISSalute, Commozione cerebrale; IFRC "
     "2025, p. 312; corretto il 1/11/2026)"),
    (re.compile(r"coprilo\s+senza\s+premere|cover\s+it\s+without\s+pressing|\['Copri\s+senza\s+premere'", re.I),
     "occhio colpito da un petardo: non toccarlo, non strofinarlo, non togliere frammenti e chiama il 112; «coprilo» non è in "
     "nessuna fonte (NHS, Eye injuries, 12/03/2026; corretto il 1/11/2026)"),
    (re.compile(r"Chiama\s+(?:il\s+\**112\**|'\+U12\+')\s+se\s+ha\s+battuto\s+la\s+testa,?\s+\(?ancora\s+di\s+più"
                r"|Call\s+\**112\**\s+if\s+they\s+hit\s+their\s+head\s+\(all\s+the\s+more", re.I),
     "cadute degli anziani: 112 per i segni d'allarme dopo il colpo alla testa, non per ogni colpo; chi prende anticoagulanti va "
     "subito in pronto soccorso (ISSalute, Commozione cerebrale; IFRC 2025, pp. 312-314; corretto il 1/11/2026)"),
    (re.compile(r"non\s+risponde\s+e\s+non\s+respira(?!\s+normalmente)|no\s+response,\s+not\s+breathing\b(?!\s+normally)", re.I),
     "arresto cardiaco: il criterio è «non risponde e non respira normalmente»; respiri rari, rumorosi o affannosi "
     "non sono un respiro normale (IRC 2025, cap. 4, pp. 5 e 14; guida rapida corretta il 1/11/2026)"),
    # Revisione sanitaria della rubrica del 1/11/2026 («anche gli altri video devono essere in linea con le linee guida
    # ufficiali»). Il gruppo (?:\s|\d|:|\.|-->)* salta il passaggio fra due sottotitoli di un .vtt (riga vuota e tempi),
    # dove una frase si spezza.
    (re.compile(r"(?:pressione|premere|premi)[^.\n]{0,40}?almeno\s+(?:10|dieci)\s+minuti|\['Almeno',\s*'\*10\s+minuti\*\.'\]"
                r"|pressure[^.\n]{0,40}?at\s+least\s+10\s+minutes", re.I),
     "emorragia grave: si preme senza mollare finché arrivano i soccorsi; nessuna fonte dà un tempo minimo, che fa credere "
     "di poter smettere prima (Croce Rossa Italiana, Emorragie; IRC 2025, cap. 12, p. 15; corretto il 1/11/2026)"),
    (re.compile(r"dura\s+più\s+di\s+qualche\s+minuto|non\s+passa\s+dopo\s+pochi\s+minuti|does\s+not\s+go\s+away\s+after\s+a\s+few\s+minutes", re.I),
     "infarto: con i segni si chiama SUBITO il 112, anche se il dolore dura da pochi minuti o va e viene (IFRC 2025, p. 358; "
     "corretto il 1/11/2026)"),
    (re.compile(r"Medicine\s+solo\s+se\s+lo\s+dice\s+l\\?'operatore|Farmaci:\s+chiedi\s+al\s+112", re.I),
     "infarto: se non è allergica e non l'ha già presa, si aiuta la persona a masticare un'aspirina da 150-500 mg, e a usare "
     "il suo spray se ha un'angina nota (IRC 2025, cap. 12, p. 12; corretto il 1/11/2026)"),
    (re.compile(r"in\s+quattro(?:\s+parti)?,?\s+per\s+lungo|per\s+lungo\s+in\s+quattro|into\s+quarters,?\s+lengthways|tagliata\s+in\s+4"
                r"|in\s+4,\s+per\s+lungo", re.I),
     "prevenzione del soffocamento nei bambini: gli alimenti tondi si tagliano in pezzi piccoli, di circa 5 mm, senza semi "
     "né noccioli (Ministero della Salute, Linee di indirizzo 2017, Tabella 1; corretto il 1/11/2026)"),
    (re.compile(r"se\s+non\s+riesce\s+a\s+tossire,(?:\s|\d|:|\.|-->)*(?:cinque|5)\s+colpi"
                r"|Se\s+perde\s+conoscenza,\s+\**112\**\s+e\s+rianimazione", re.I),
     "soffocamento: se non riesce più a tossire si chiama SUBITO il 112, poi colpi e compressioni; non solo quando perde "
     "conoscenza (IRC 2025, cap. 12, p. 11; news «10 cose» corretta il 1/11/2026)"),
    (re.compile(r"non\s+si\s+riprende[^.\n]{0,60}guarda\s+se\s+respira\s+normalmente[:.](?:\s|\d|:|\.|-->)*se\s+non\s+respira"
                r"|come\s+round[^.\n]{0,60}breathing\s+normally:\s+if\s+not,?\s+start"
                r"|come\s+round[^.\n]{0,60}check\s+their\s+breathing:\s+if\s+it\s+is\s+not\s+normal", re.I),
     "svenimento: se non si riprende ma respira normalmente (e non ha battuto forte cadendo) va messo su un fianco; "
     "se non respira normalmente, rianimazione (IRC 2025, cap. 12, p. 8; corretto il 1/11/2026)"),
    (re.compile(r"di\s+solito\s+meno\s+di\s+un\s+minuto|usually\s+less\s+than\s+a\s+minute", re.I),
     "svenimento: la perdita di coscienza dura di solito pochi secondi (IFRC 2025, p. 401; NHS); «meno di un minuto» "
     "invita ad aspettare (corretto il 1/11/2026)"),
    (re.compile(r"confus[oa],\s+sonnolent[oa]\s+o\s+non\s+trema\s+più,\s+chiama|tienilo\s+sdraiato"
                r"|confused,\s+drowsy\s+or\s+no\s+longer\s+shivering,\s+call", re.I),
     "ipotermia: il 112 si chiama per OGNI sospetta ipotermia, non solo quando è grave; se è grave si muove il meno "
     "possibile (IFRC 2025, pp. 461 e 463; Croce Rossa Italiana; corretto il 1/11/2026)"),
    (re.compile(r"per\s+una\s+ventina\s+di\s+minuti|(?:ghiaccio|ice)[^.\n]{0,70}?(?:circa\s+20\s+minuti|about\s+20\s+minutes)", re.I),
     "fratture: il ghiaccio si tiene per NON PIÙ di 20 minuti alla volta, oltre si danneggia la pelle (IFRC 2025, p. 301; "
     "Croce Rossa Italiana; corretto il 1/11/2026)"),
    (re.compile(r"aiutalo\s+a\s+respirare\s+lentamente|help\s+them\s+breathe\s+slowly"
                r"|Chiama\s+(?:il\s+\**112\**|'\+U12\+')\s+se\s+lo\s+spray\s+non\s+(?:funziona|basta)"
                r"|Call\s+\**112\**\s+if\s+the\s+inhaler\s+isn't\s+enough|usarlo\s+nella\s+coscia|use\s+it\s+in\s+the\s+thigh", re.I),
     "asma: 112 anche se non ha lo spray; calma e vestiti larghi, non «respiri lenti» (IFRC 2025, pp. 245-247); adrenalina "
     "nella parte esterna della coscia (IRC 2025, cap. 12, p. 11; corretto il 1/11/2026)"),
    (re.compile(r"guarda\s+se\s+respira\s+normalmente\.(?:\s|\d|:|\.|-->)*Se\s+risponde"
                r"|Se\s+non\s+risponde,\s+chiama\s+il\s+\*\*112\*\*\s+e\s+guarda\s+se\s+respira\s+normalmente\.\""
                r"|do\s+not\s+respond,\s+call\s+\*\*112\*\*\s+and\s+check\s+whether\s+they\s+are\s+breathing\s+normally\.\"", re.I),
     "cadute: dopo «guarda se respira normalmente» va detto che cosa fare: se non respira normalmente, rianimazione "
     "(IRC 2025, cap. 4, p. 15; corretto il 1/11/2026)"),
    (re.compile(r"rifiuta\s+di\s+mangiare|rifiuto\s+del\s+cibo|rifiuta\s+il\s+cibo|refusing\s+food", re.I),
     "batterie a bottone: i segni della fonte sono tosse, bava, vomito e fatica a deglutire (Ospedale Bambino Gesù, 2026; "
     "corretto il 1/11/2026)"),
    (re.compile(r"finestre\s+aprile", re.I),
     "avvelenamento: «aprile» si confonde con il mese; si scrive «Apri le finestre» (corretto il 1/11/2026)"),
    (re.compile(r"più\s+grande\s+del\s+palmo", re.I),
     "ustioni: si chiama il 112 per ustioni grandi o profonde, su viso, mani, piedi o genitali, da fiamme, elettriche o "
     "chimiche, o in un bambino; il «palmo» non è nelle fonti (IFRC 2025, p. 290; corretto il 1/11/2026)"),
    (re.compile(r"finché\s+l\\?'oggetto\s+non\s+esce\s+o\s+arrivano", re.I),
     "soffocamento del lattante: ci si ferma appena torna a piangere, tossire o respirare, anche se l'oggetto non si vede "
     "uscire (IRC 2025, cap. 9, p. 29; corretto il 1/11/2026)"),
    (re.compile(r"finché\s+non\s+si\s+sveglia\.", re.I),
     "rianimazione: si smette se si sveglia E respira normalmente (IFRC 2025, p. 162; corretto il 1/11/2026)"),
    (re.compile(r"sole\s+tra\s+le\s+12\s+e\s+le\s+18|tra\s+\**25\s+e\s+27\s+gradi", re.I),
     "caldo: ore più fresche fino alle 11 e dopo le 18, condizionatore intorno a 25-26 gradi (ISSalute, aggiornata il "
     "4/11/2025; corretto il 1/11/2026)"),
]
# La prova di queste regole (esempi da segnalare e forme giuste) è scripts/controlli/prova_forme.py.
# Dove si cercano: sorgenti del sito, sottotitoli e pagine in static/, generatori di video, grafiche e post
# (scripts/, schede social). Non i file di governo (CLAUDE.md, COORDINAMENTO.md…), che citano la forma per vietarla.
CARTELLE_TESTI = ("content", "layouts", "data", "assets", "archetypes", "static", "contenuti", "scripts", ".github/social")
FILE_TESTI = ("hugo.toml",)
ESTENSIONI_TESTI = (".md", ".html", ".yaml", ".yml", ".json", ".toml", ".py", ".js", ".vtt", ".srt", ".txt", ".svg")
# Firma «Misericordia di Ariccia» e cornice di microtesto (richiesta di Alessandro del 21/10/2026: «metti in ogni
# slide, documento grafico eccetera sempre Misericordia di Ariccia! Altrimenti ci rubano la grafica!!»). Il motore
# scripts/grafica-brand/firma-e-cornice.js scrive in testa al JPEG (commento) o al PNG (blocco tEXt) il suo segno:
# lo devono avere le grafiche delle news, le copertine dei loro video e le pagine della Parola che escono da DAL_FIRMA,
# e ogni modello grafico deve avere la firma (elemento data-firma). La prova di questo controllo è
# scripts/controlli/prova_cornice.py.
DAL_FIRMA = dt.date(2026, 10, 22)
MOTORE_FIRMA = REPO / "scripts/grafica-brand/firma-e-cornice.js"
MODELLI_FIRMA = ("scripts/grafica-brand/modelli-nazionali/*.html", "scripts/parola-domenica/grafica*.html")


def hash_inline(pub):
    """Hash sha256 (formato CSP) degli script inline eseguibili di tutte le pagine."""
    trovati = {}
    for f in glob.glob(f"{pub}/**/*.html", recursive=True):
        for s in re.findall(r"<script>(.*?)</script>", Path(f).read_text(encoding="utf-8"), re.S):
            h = "'sha256-" + base64.b64encode(hashlib.sha256(s.encode()).digest()).decode() + "'"
            trovati.setdefault(h, f.replace(pub, "").replace("index.html", ""))
    return trovati


def link_rotti(pub):
    rotti = {}
    for f in glob.glob(f"{pub}/**/*.html", recursive=True):
        testo = Path(f).read_text(encoding="utf-8")
        pagina = f[len(pub):].replace("index.html", "") or "/"
        # con --minify Hugo toglie le virgolette dove può: si leggono entrambe le forme
        attr = [a or b for a, b in re.findall(r'\s(?:href|src|poster)=(?:"([^"#?]*)|([^\s>"\'#?]+))', testo)]
        for ss in re.findall(r'srcset=(?:"([^"]+)"|([^\s>"]+))', testo):
            ss = ss[0] or ss[1]
            attr += [x.strip().split(" ")[0] for x in ss.split(",")]
        for u in attr:
            u = html.unescape(u)
            if not u: continue
            p = urlsplit(u)
            if p.scheme or u.startswith("//") or u.startswith("mailto:") or u.startswith("tel:"):
                if not u.startswith(SITO): continue
                u = urlsplit(u).path
            if not u.startswith("/"): u = urljoin(pagina, u)   # percorsi relativi (./css/…, ../img/…)
            loc = Path(pub + unquote(u))
            ok = (loc / "index.html").exists() if u.endswith("/") else (loc.exists() or (loc / "index.html").exists())
            if not ok: rotti.setdefault(u, pagina)
    return rotti


def leggi_registro():
    """Lettura minima del registro YAML (formato fisso: «- id:», chiavi a 2 spazi tra virgolette)."""
    voci, cur = [], None
    for riga in (REPO / "data/dati_da_verificare.yaml").read_text(encoding="utf-8").splitlines():
        m = re.match(r'- id: "(.+)"', riga)
        if m: cur = {"id": m.group(1)}; voci.append(cur); continue
        m = re.match(r'  (\w+): (.*)', riga)
        if cur is not None and m:
            v = m.group(2).strip()
            cur[m.group(1)] = v[1:-1] if v.startswith('"') else v
    return voci


def news_programmate(giorni=14):
    out = []
    for f in sorted((REPO / "content/news").glob("*.md")):
        fm = f.read_text(encoding="utf-8").split("---")[1]
        m = re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M)
        if not m: continue
        d = dt.date.fromisoformat(m.group(1))
        if oggi < d <= oggi + dt.timedelta(days=giorni):
            c = re.search(r'^controllo_editoriale:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M)
            t = re.search(r'^title:\s*"(.*)"', fm, re.M)
            out.append((d, f.name, t.group(1) if t else f.name, c.group(1) if c else ""))
    return out


def forme_sbagliate():
    file = [REPO / nome for nome in FILE_TESTI]
    for cartella in CARTELLE_TESTI:
        file += sorted((REPO / cartella).rglob("*"))
    trovate = []
    for f in file:
        if not f.is_file() or f.suffix not in ESTENSIONI_TESTI or "node_modules" in f.parts: continue
        testo = f.read_text(encoding="utf-8", errors="replace")
        for rx, regola in FORME_SBAGLIATE:
            for m in rx.finditer(testo):
                trovate.append((f"{f.relative_to(REPO)}:{testo.count(chr(10), 0, m.start()) + 1}", m.group(0), regola))
    return trovate


def segno_firma():
    """Il segno che il motore scrive nelle grafiche (MARCATORE di firma-e-cornice.js), in byte."""
    m = re.search(r"const MARCATORE = '([^']+)'", MOTORE_FIRMA.read_text(encoding="utf-8"))
    return m.group(1).encode() if m else None


def ha_segno(dati, segno):
    """Vero se il JPEG ha il segno in un commento (segmento COM) o il PNG in un blocco tEXt, prima dei dati
    dell'immagine: un segno sparso nei pixel compressi non vale."""
    if dati[:2] == b"\xff\xd8":
        i = 2
        while i + 4 <= len(dati) and dati[i] == 0xFF:
            tipo, lung = dati[i + 1], int.from_bytes(dati[i + 2:i + 4], "big")
            if tipo == 0xFE and segno in dati[i + 4:i + 2 + lung]: return True
            if tipo == 0xDA: break                          # inizio dei dati compressi
            i += 2 + lung
        return False
    if dati[:8] == b"\x89PNG\r\n\x1a\n":
        i = 8
        while i + 8 <= len(dati):
            lung, tipo = int.from_bytes(dati[i:i + 4], "big"), dati[i + 4:i + 8]
            if tipo == b"tEXt" and segno in dati[i + 8:i + 8 + lung]: return True
            if tipo == b"IDAT": break
            i += 12 + lung
        return False
    return False


def copertine_video(fm, corpo):
    """Copertine dei video di una news, come percorsi sotto static/: il fotogramma static/img/video/<nome>.jpg del
    social_video (lo crea scripts/video-rubrica/copia.sh), le locandine (poster="…") del corpo e social_video_copertina
    quando è un'immagine. Se è un numero, social_video_copertina è il secondo del video usato come copertina del Reel:
    un fotogramma del video, che nel file non si può controllare."""
    out = []
    sv = re.search(r'^social_video:\s*"?([^"\n]+?)"?\s*$', fm, re.M)
    if sv:
        out.append("img/video/" + Path(sv.group(1).strip()).stem + ".jpg")
    cop = re.search(r'^social_video_copertina:\s*"?([^"\n]+?)"?\s*$', fm, re.M)
    if cop and Path(cop.group(1).strip()).suffix.lower() in (".jpg", ".jpeg", ".png"):
        out.append(cop.group(1).strip().lstrip("/"))
    out += [p.lstrip("/") for p in re.findall(r'\sposter="([^"]+)"', corpo)]
    return list(dict.fromkeys(out))


def grafiche_senza_firma(radice=REPO):
    segno = segno_firma()
    if not segno:
        return ["scripts/grafica-brand/firma-e-cornice.js: non trovo il segno (const MARCATORE)"]
    mancano, senza = [], {}   # senza: immagine -> [tipo, news che la usano]
    for f in sorted((radice / "content/news").glob("*.md")):
        parti = f.read_text(encoding="utf-8").split("---", 2)
        fm, corpo = parti[1], parti[2] if len(parti) > 2 else ""
        d = re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M)
        if not d or dt.date.fromisoformat(d.group(1)) < DAL_FIRMA: continue
        im = re.search(r'^immagine:\s*"?([^"\n]+?)"?\s*$', fm, re.M)
        controllare = [(im.group(1).strip().lstrip("/"), "news")] if im else []
        controllare += [(c, "copertina del video, news") for c in copertine_video(fm, corpo)]
        for percorso, tipo in controllare:
            img = radice / "static" / percorso
            if img.suffix.lower() in (".jpg", ".jpeg", ".png") and img.is_file() and not ha_segno(img.read_bytes()[:65536], segno):
                senza.setdefault(img.relative_to(radice), [tipo, []])[1].append(f.name)
    for img, (tipo, news) in senza.items():
        mancano.append(f"`{img}` ({tipo} {', '.join(news[:3])}{f' e altre {len(news) - 3}' if len(news) > 3 else ''})")
    for img in sorted((radice / "static/img/parola").glob("*.jpg")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})-\d+\.jpg$", img.name)
        if m and dt.date.fromisoformat(m.group(1)) >= DAL_FIRMA and not ha_segno(img.read_bytes()[:65536], segno):
            mancano.append(f"`{img.relative_to(radice)}` (Parola della domenica)")
    for schema in MODELLI_FIRMA:
        for modello in sorted(radice.glob(schema)):
            if "data-firma" not in modello.read_text(encoding="utf-8"):
                mancano.append(f"`{modello.relative_to(radice)}`: modello senza la firma (elemento data-firma)")
    return mancano


def fonte_video_sbagliata():
    """News della rubrica in uscita che citano fonti diverse da IRC/ERC: il loro video non deve dire
    «Fonte: linee guida IRC 2025» nella scheda finale, ma rimandare all'articolo (campo fonte in
    scripts/video-rubrica/contenuti*.py). Errore trovato il 21/10/2026 (issue #147)."""
    sys.path.insert(0, str(REPO / "scripts/video-rubrica"))
    try:
        import contenuti
    except Exception as e:  # noqa: BLE001
        return [f"scripts/video-rubrica/contenuti.py non si legge: {e}"]
    mancano = []
    for f in sorted((REPO / "content/news").glob("*-primo-soccorso-*.md")):
        t = f.read_text(encoding="utf-8")
        d = re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', t, re.M)
        v = re.search(r'video/primo-soccorso-([a-z0-9-]+)\.mp4', t)
        if not d or not v or dt.date.fromisoformat(d.group(1)) < DAL_FIRMA: continue
        fonti = " ".join(re.findall(r"^\*Font[ei]:.*$", t, re.M))
        altre = [u for u in re.findall(r"\]\((https?://[^)]+)\)", fonti) if not re.search(r"ircouncil\.it|erc\.edu", u)]
        k = v.group(1)
        if altre and k in contenuti.V and not contenuti.V[k].get("fonte"):
            mancano.append(f"`{f.name}`: cita {altre[0]} ma il video «{k}» dice «linee guida IRC 2025» (manca fonte in contenuti*.py)")
    return mancano


def scarica(url, tentativi=4):
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (controlli sito Misericordia Ariccia)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code != 503 or i == tentativi - 1: return e.code, ""   # 503 intermittenti = anti-bot Aruba
        except Exception as e:
            if i == tentativi - 1: return str(e)[:60], ""
        time.sleep(5 * (i + 1))
    return "?", ""


def file_news_programmate():
    """File che le news con data futura citano (immagine, social_video, shortcode video e immagini Markdown) e che
    non esistono in static/: Hugo non costruisce le news future, quindi il controllo dei link non li vede finché la
    news non esce. Errore che avrebbe potuto sfuggire il 1/11/2026 (video della campagna volontari in montaggio)."""
    mancano = []
    for f in sorted((REPO / "content/news").glob("*.md")):
        t = f.read_text(encoding="utf-8")
        parti = t.split("---", 2)
        if len(parti) < 3: continue
        fm = parti[1]
        d = re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M)
        if not d or dt.date.fromisoformat(d.group(1)) <= oggi: continue
        if re.search(r'^draft:\s*true', fm, re.M): continue   # bozze (es. in attesa di revisione sanitaria): non escono
        rif = re.findall(r'^(?:immagine|social_video|social_video_copertina_file):\s*"?(/[^"\s]+)"?', fm, re.M)
        rif += ["/" + x for x in re.findall(r'\{\{<\s*video\s+src="([^"]+)"', t)]
        rif += ["/" + x for x in re.findall(r'\{\{<\s*video\b[^>]*\bposter="([^"]+)"', t)]
        rif += re.findall(r'!\[[^\]]*\]\((/[^)\s]+)\)', t)
        for r in dict.fromkeys(rif):
            if not (REPO / "static" / r.lstrip("/")).is_file():
                mancano.append(f"`{f.name}` ({d.group(1)}): manca `static{r}`")
        # Reel di Facebook: la Reels API accetta al massimo 90 s; un video più lungo va escluso con
        # social_reel_facebook: false, altrimenti la pubblicazione automatica fallisce il giorno dell'uscita (1/11/2026).
        sv = re.search(r'^social_video:\s*"?(/[^"\s]+\.mp4)"?', fm, re.M)
        if sv and not re.search(r'^social_reel_facebook:\s*false', fm, re.M):
            durata = durata_mp4(REPO / "static" / sv.group(1).lstrip("/"))
            if durata and durata > 90:
                mancano.append(f"`{f.name}` ({d.group(1)}): video di {durata:.0f} s, oltre i 90 s dei Reel di Facebook: "
                               "aggiungi `social_reel_facebook: false`")
    return mancano


def durata_mp4(f):
    """Durata in secondi di un MP4 letta dall'intestazione (box mvhd), senza ffmpeg; None se non si legge."""
    try:
        b = f.read_bytes()
    except OSError:
        return None
    i = b.find(b"mvhd")
    if i < 0: return None
    v = b[i + 4]
    if v == 1:
        scala, dur = int.from_bytes(b[i + 24:i + 28], "big"), int.from_bytes(b[i + 28:i + 36], "big")
    else:
        scala, dur = int.from_bytes(b[i + 16:i + 20], "big"), int.from_bytes(b[i + 20:i + 24], "big")
    return dur / scala if scala else None


def revisione_in_attesa(giorni=30):
    """Contenuti sanitari non ancora rivisti dal responsabile sanitario: news con revisione_sanitaria: "da fare"
    (in bozza, Hugo non le pubblica) e schede del dossier primo soccorso con revisione: "da fare" (nascoste dal layout).
    Restituisce (elenco, urgenti): urgenti quelli che escono entro `giorni` giorni o con la data già passata, che
    senza revisione non uscirebbero o uscirebbero in ritardo (3ª serie della rubrica, 1/11/2026)."""
    elenco, urgenti = [], []
    for f in sorted((REPO / "content/news").glob("*.md")):
        fm = f.read_text(encoding="utf-8").split("---")[1]
        if not re.search(r'^revisione_sanitaria:\s*"da fare"', fm, re.M): continue
        d = re.search(r'^date:\s*"?(\d{4}-\d{2}-\d{2})', fm, re.M)
        data = dt.date.fromisoformat(d.group(1)) if d else oggi
        voce = f"news `{f.name}` (esce il {data.strftime('%d/%m/%Y')})"
        elenco.append(voce)
        if (data - oggi).days <= giorni: urgenti.append(voce)
    ps = (REPO / "content/dossier/primo-soccorso.md").read_text(encoding="utf-8")
    for m in re.finditer(r'^  - id: "([^"]+)"\n((?:    .*\n)+)', ps, re.M):
        if re.search(r'^    revisione:\s*"da fare"', m.group(2), re.M):
            d = re.search(r'^    dal:\s*"(\d{4}-\d{2}-\d{2})"', m.group(2), re.M)
            data = dt.date.fromisoformat(d.group(1)) if d else oggi
            voce = f"scheda `{m.group(1)}` del dossier primo soccorso (video dal {data.strftime('%d/%m/%Y')})"
            elenco.append(voce)
            if (data - oggi).days <= giorni: urgenti.append(voce)
    return elenco, urgenti


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pub = (args[0] if args else "public").rstrip("/")
    if "--csp" in sys.argv:
        print(" ".join(hash_inline(pub))); return 0
    report = sys.argv[sys.argv.index("--report") + 1] if "--report" in sys.argv else None
    righe, errori = [f"_Controllo del {oggi.strftime('%d/%m/%Y')}_", ""], 0

    rotti = link_rotti(pub)
    righe.append(f"### 🔗 Link interni, immagini e video: {'✅ nessun file mancante' if not rotti else f'❌ {len(rotti)} mancanti'}")
    righe += [f"- `{u}` (in {p})" for u, p in list(rotti.items())[:30]]
    errori += bool(rotti)

    csp = re.search(r'Content-Security-Policy(?:-Report-Only)? "([^"]+)"', (REPO / "static/.htaccess").read_text())
    ammessi = set(re.findall(r"'sha256-[^']+'", csp.group(1))) if csp else set()
    fuori = {h: p for h, p in hash_inline(pub).items() if h not in ammessi}
    righe += ["", f"### 🛡️ Content Security Policy: {'✅ tutti gli script inline sono coperti' if not fuori else f'❌ {len(fuori)} script inline nuovi o cambiati'}"]
    righe += [f"- {h} (es. in {p}): ricalcola con `python3 scripts/controlli/controlla_sito.py public --csp`" for h, p in fuori.items()]
    errori += bool(fuori)

    voci = leggi_registro()
    scadute = [v["id"] for v in voci if not v.get("verificato") or
               (oggi - dt.date.fromisoformat(v["verificato"])).days > FREQ.get(v.get("frequenza"), 365)]
    sanitari = [v for v in voci if v.get("tipo") == "sanita"]
    ps = (REPO / "content/dossier/primo-soccorso.md").read_text(encoding="utf-8")
    rev = re.search(r'^verifica_sanitaria:\s*"(.+)"', ps, re.M)
    righe += ["", "### 📋 Registro dei dati",
              f"- Voci nel registro: {len(voci)} · scadute (oltre la loro frequenza): **{len(scadute)}**" + (f" ({', '.join(scadute[:12])}{'…' if len(scadute) > 12 else ''})" if scadute else ""),
              f"- Contenuti sanitari: {len(sanitari)} voci · verifica sanitaria del dossier primo soccorso: " + (f"✅ {rev.group(1)}" if rev else "⚠️ **non ancora registrata** (`verifica_sanitaria` in content/dossier/primo-soccorso.md)")]

    np_ = news_programmate()
    righe += ["", f"### 📅 News in uscita nei prossimi 14 giorni: {len(np_)}"]
    for d, nome, tit, c in np_:
        stato = f"controllata il {c}" if c else ("⚠️ **da controllare**" if (d - oggi).days <= 3 else "controllo 3 giorni prima")
        righe.append(f"- {d.strftime('%d/%m')} · {tit} — {stato}")

    sbagliate = forme_sbagliate()
    righe += ["", f"### ✍️ Forme da non usare: {'✅ nessuna' if not sbagliate else f'❌ {len(sbagliate)} da correggere'}"]
    righe += [f"- `{dove}`: «{trovato}» → {regola}" for dove, trovato, regola in sbagliate[:30]]
    errori += bool(sbagliate)

    senza = grafiche_senza_firma()
    righe += ["", "### 🖋️ Firma «Misericordia di Ariccia» e cornice di microtesto: "
              + ("✅ in tutte le grafiche in uscita e in tutti i modelli" if not senza else f"❌ {len(senza)} senza")]
    def rimedio(x):
        if x.endswith("(elemento data-firma)"): return f"- {x}"
        if "(copertina del video" in x:
            return (f"- {x}: se il video ha già firma e cornice, `python3 .claude/skills/grafiche-modelli-nazionali/rendi.py "
                    "--segno FILE` (lo fa `scripts/video-rubrica/copia.sh`), altrimenti `rendi.py --cornice FILE`")
        return (f"- {x}: rifarla con il modello, oppure `python3 .claude/skills/grafiche-modelli-nazionali/rendi.py --cornice FILE` "
                "(con `--firma basso-sinistra` se la grafica non mostra il nome)")
    righe += [rimedio(x) for x in senza[:30]]
    errori += bool(senza)

    ra, ru = revisione_in_attesa()
    righe += ["", "### 🩺 Revisione sanitaria in attesa: " + ("✅ nessun contenuto" if not ra else
              (f"❌ {len(ru)} in uscita entro 30 giorni senza revisione" if ru else f"⏳ {len(ra)} contenuti, nessuno in uscita nei prossimi 30 giorni"))]
    if ra: righe.append("- Li rivede il responsabile sanitario; poi si toglie `revisione_sanitaria` e `draft` dalle news e `revisione` dalle schede.")
    righe += [f"- {x}" for x in (ru or ra)[:30]]
    errori += bool(ru)

    fm_ = file_news_programmate()
    righe += ["", "### 🗓️ File delle news programmate: " + ("✅ immagini e video già nel sito" if not fm_ else f"❌ {len(fm_)} mancanti")]
    righe += [f"- {x}" for x in fm_[:30]]
    errori += bool(fm_)

    fv = fonte_video_sbagliata()
    righe += ["", "### 🎬 Fonte nella scheda finale dei video: " + ("✅ coerente con gli articoli" if not fv else f"❌ {len(fv)} da correggere")]
    righe += [f"- {x}" for x in fv[:30]]
    errori += bool(fv)

    if "--live" in sys.argv:
        righe += ["", "### 🌐 Sito online"]
        css_atteso = re.search(r'(css/sito\.min\.[0-9a-f]+\.css)', Path(f"{pub}/index.html").read_text())
        for p in PAGINE_LIVE:
            st, testo = scarica(SITO + p)
            nota = ""
            if p == "/" and css_atteso:
                nota = " · build aggiornata ✅" if css_atteso.group(1) in testo else " · ⚠️ la home online non usa il CSS di questa build (deploy non arrivato?)"
            righe.append(f"- {'✅' if st == 200 else '❌'} `{p}` → {st}{nota}")
            errori += st != 200

    testo = "\n".join(righe) + "\n"
    if report: Path(report).write_text(testo, encoding="utf-8")
    print(testo)
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())
