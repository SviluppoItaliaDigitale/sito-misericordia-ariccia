# Brand — token e tono

Ogni realtà ha la sua identità: mai mescolarle nella stessa pagina. Qui
sotto i profili pronti delle realtà già seguite; in fondo, la procedura per
qualsiasi realtà o progetto nuovo.

## Protezione Civile Genzano di Roma (Gruppo Comunale Volontari)

- **Contesto**: sito istituzionale protezionecivilegenzano.it, Hugo +
  Bootstrap Italia; le landing premium vivono come pagine autonome accanto.
- **Palette** (pagine scure): fondo `#0a1220` / `#070b14`; azzurro
  istituzionale `#2e90fa` (richiama il primary Bootstrap Italia `#0066CC`);
  arancio emergenza `#f59e0b`; per IT-alert accento allarme `#f04e3e`;
  testo `#eef2f7`, attenuato `#93a1b5`.
- **Font**: Titillium Web (coerente con Bootstrap Italia) per display e
  corpo; Roboto Mono per eyebrow, chip, etichette. Per il taglio
  cinematografico (stile TikTok) è ammesso Anton come display.
- **Tono**: istituzionale ma diretto, seconda persona singolare, zero
  allarmismo, dati verificabili. Numeri sensibili (quantità del kit, anni,
  procedure) SEMPRE da validare col coordinatore prima di pubblicare.
  Riferimenti corretti noti: acqua kit = 1,5 L/persona/giorno; fondazione
  gruppo 1991; modello del ciclo a 5 attività (le 4 di legge + "memoria",
  dal manuale interno).
- **Storie già approvate come prototipi**: zaino di emergenza 72h (exploded
  view, con sub-esplosione del kit primo soccorso); ciclo della protezione
  civile a 5 strati; viaggio di un messaggio IT-alert (sala operativa → rete
  → cella broadcast → città → telefono; accuratezza: cell broadcast su area,
  niente numeri, funziona a rete satura). CTA tipiche: checklist kit,
  approfondisci nel manuale, it-alert.gov.it.

## Confraternita di Misericordia di Ariccia ODV

- **Palette**: fondo blu notte `#0c1020`; oro `#f2c14e`; blu `#4a90d9`;
  rosso presidi `#d64545` / lampeggianti `#3d8bff`; avorio `#f2efe6`.
- **Font**: Playfair Display (display, corsivi d'accento) + Jost (corpo);
  Anton ammesso per lo stile cinematografico; mono per chip/etichette.
- **Livrea mezzo** (decal): base bianca `#e8e5db`, fascia arancio
  retroriflettente `#ff8a2a→#f07a18`, scritte blu `#163a7a`, emblema cerchio
  oro + croce blu, "AMBULANZA" bianco nella fascia.
- **Tono**: caldo, umano, orientato alla comunità e al reclutamento; la
  tecnica è al servizio dell'emozione. Chiusura ricorrente: "Manchi solo tu"
  + CTA "Diventa volontario" (formazione: corso base → affiancamento → primo
  turno).
- **Storie già approvate come prototipi**: ambulanza scomposta (guscio che si
  solleva; sub-esplosione zaino sanitario: pallone autoespandibile, collare,
  sfigmomanometro, garze); scrollytelling "L'intervento" (112 → chiamata →
  uscita → sul posto → rientro → volontari).
- Nessuna claim clinica su tempi/esiti; restare su fatti generici e
  verificabili (es. "ogni minuto conta" sì, percentuali no se non validate).

## Cooprimavera Società Cooperativa (Castelli Romani)

- **Contesto**: sito www.cooprimavera.com, Hugo, sito live dal 2026 (repo
  `SviluppoItaliaDigitale/cooprimavera`, clone in `~/cooprimavera/`); il sito
  è **chiaro** (fondo bianco, bottoni a pillola). Le landing premium scure
  vivono come pagine autonome accanto, senza toccare il tema.
- **Palette** — colori verificati dal logo/sito: verde `#9FC63D`
  (secondario/energia), verde scuro `#627C26` (primario), quasi-nero
  verdastro `#232A1C` (testo/CTA scure), crema `#F4F8E8`. Per le pagine
  scure premium (token derivati, coerenti col brand): fondo `#12160d` /
  `#0d100a`; accento principale il verde `#9FC63D` (ottimo contrasto su
  scuro); `#627C26` solo per superfici/forme grandi, mai per testo piccolo
  su fondo scuro; testo `#f2f5ec`, attenuato `#a7b096`.
- **Font**: il sito usa lo stack di sistema (system-ui/Roboto); per le
  landing premium usare Inter (corpo) — resa vicina al sito ma controllata —
  e Roboto Mono per eyebrow/chip; Anton ammesso come display per il taglio
  cinematografico. Bottoni a pillola (border-radius pieno) come sul sito.
- **Tono**: professionale B2B, diretto, seconda persona; claim «Il miglior
  partner per il tuo business». Sempre presente la doppia missione: servizi
  di qualità **+ inserimento lavorativo di persone svantaggiate**
  (cooperativa sociale, dal 2006). Niente promesse su prezzi/tempi non
  validate.
- **Fatti verificati utilizzabili**: dal 2006 (20 anni di esperienza);
  9 servizi a catalogo, 23 specialistici; opera a Roma e Castelli Romani
  (14 comuni elencati sul sito); servizi: pulizie professionali,
  giardinaggio, portierato, sanificazioni, disinfestazioni, allestimenti
  per eventi, noleggio sedie, moquette per eventi, forniture igieniche.
- **CTA tipiche**: «Richiedi un preventivo gratuito» → /preventivo/;
  WhatsApp 06 63 46 70; tel. 331 777 1888. Contatti sempre dal sito, mai
  inventati.
- **Storie candidate** (proposte, non ancora approvate dal committente):
  vetrina scura premium dei 9 servizi con CTA preventivo; exploded view del
  carrello pulizie professionale o dell'allestimento evento (palco/sedie/
  moquette che si compongono); scrollytelling "Una giornata in cooperativa"
  (alba → cantieri → persone, con la missione sociale come chiusura);
  sciame di cubi per la rete dei 14 comuni serviti.

## Nuove realtà e progetti futuri — procedura

Per qualsiasi realtà senza profilo qui sopra (nuova associazione, cliente,
progetto personale, idea da validare):

1. **Ricava i token da materiali reali, mai a memoria.** In ordine di
   preferenza: sito esistente (Firecrawl, formato `branding` + lettura del
   CSS), logo o materiale grafico fornito dall'utente, indicazioni esplicite
   dell'utente. Estrai: 2–3 colori di marca, font (o famiglia equivalente su
   Google Fonts), tono di voce, CTA principale.
2. **Adatta i colori al fondo scuro**: il colore di marca più saturo/chiaro
   diventa l'accento; le tinte scure del brand generano il fondo (mai nero
   puro: virare il fondo verso la tinta del brand). Verifica contrasto AA
   per il testo.
3. **Dati della realtà** (nome esatto, contatti, numeri, date): solo se
   forniti o verificati. I campi mancanti restano `[da compilare]` e vanno
   segnalati nella nota di consegna. Le storie proposte sono sempre
   **candidate** finché il committente non le approva.
4. **Niente palette di ripiego generica** (regola `.claude/rules/grafica.md`):
   se non esiste ancora alcun brand, non usare una base "neutra premium"
   uguale per tutti. Dichiara una **direzione visiva** con un riferimento
   concreto e proprio della realtà (luoghi, materiali, mestiere, storia) e
   ricava da lì palette e tipografia; proponila all'utente in due righe
   prima di costruire e dichiarala nella consegna. Se esiste
   `direzione-visiva.md` nella cartella della realtà, parti da quella.
5. **Rendi il profilo permanente**: se la realtà diventa ricorrente,
   aggiungi qui una sezione con i suoi token (stessa struttura delle
   precedenti) e rigenera il pacchetto `.skill` di backup.
