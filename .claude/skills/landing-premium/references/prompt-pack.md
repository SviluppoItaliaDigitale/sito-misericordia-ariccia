# Prompt pack — immagini e video AI

Gli asset fotorealistici non si generano nella skill: si consegnano la pagina
con lo slot (`PHOTOS` / `VIDEO_SRC`) e i prompt qui sotto, che l'utente lancia
gratuitamente da telefono (Gemini: immagini "Nano Banana", video Veo).

## Stile comune (accodare a ogni prompt immagine)

> fotografia cinematografica, illuminazione drammatica da set, leggero fumo,
> colori freddi con accento [colore brand], grana pellicola sottile, 16:9,
> fotorealistico, nessun testo, nessun logo

Per pagine notturne aggiungere: "notte, asfalto bagnato riflettente, accenti
blu dei lampeggianti". Generare tutte le immagini di una pagina nella stessa
sessione per coerenza di stile; formato 16:9 (desktop) o 4:5 se la pagina è
pensata mobile-first.

## Misericordia — "L'intervento" (6 scene)

1. HERO — ambulanza italiana bianca con fascia arancione ferma di notte sotto
   un lampione, lampeggianti blu accesi, vista 3/4 frontale dal basso
2. LA CHIAMATA — mano che stringe uno smartphone che illumina il volto al
   buio, chiamata in corso, atmosfera tesa
3. L'USCITA — ambulanza in movimento di notte sotto la pioggia, scia dei
   lampeggianti blu, leggero motion blur, strada urbana
4. SUL POSTO — zaino sanitario rosso aperto a terra illuminato da una torcia,
   defibrillatore giallo e barella accanto, notte
5. IL RIENTRO — ambulanza ferma davanti all'ingresso di un pronto soccorso,
   luci calde, atmosfera quieta
6. FINALE — gruppo di volontari soccorritori di spalle davanti all'ambulanza
   all'alba, luce dorata

## PC Genzano — kit 72h (scene tipo)

1. HERO — zaino da emergenza blu e arancione chiuso su pavimento di cemento,
   luce dall'alto a taglio, fondo scuro
2. APERTURA — lo stesso zaino aperto con il contenuto disposto ordinatamente
   in flat-lay: bottiglie d'acqua, torcia, radio, kit primo soccorso,
   documenti, coperta termica dorata
3. DETTAGLI — macro della coperta termica dorata spiegazzata che riflette la
   luce / macro della radio con mano che regola la manopola

## PC Genzano — IT-alert (video da scrubbare, prompt Veo)

> un'unica inquadratura continua in discesa: dalle nuvole sopra una cittadina
> italiana di notte, scendendo tra i tetti fino a una strada illuminata, e
> avvicinandosi alla finestra di una casa dove uno smartphone sullo schermo
> si illumina; cinematografico, realistico, nessun testo, 8 secondi

Poi ricodificare per lo scrub: `ffmpeg -i clip.mp4 -vf scale=1920:-2 -an
-c:v libx264 -g 1 -crf 23 dive.mp4`

## Cooprimavera — servizi e giornata (scene tipo)

Accento brand da usare nello stile comune: verde lime `#9FC63D`.

1. HERO — carrello pulizie professionale con secchi colorati e mocio in un
   atrio moderno vuoto illuminato dall'alba, pavimento lucido riflettente
2. PULIZIE — operatore in uniforme che pulisce una grande vetrata
   controluce, gocce e schiuma illuminate, ufficio moderno
3. GIARDINAGGIO — giardiniere che pota una siepe in un parco all'alba,
   luce dorata radente, particelle di verde in aria
4. EVENTI — fila di sedie bianche impilabili su moquette rossa in una sala
   eventi vuota, luci da palco calde, atmosfera di attesa
5. PORTIERATO — reception moderna con bancone illuminato di notte, monitor
   di videosorveglianza accesi sullo sfondo
6. FINALE — squadra di lavoratori in uniforme di spalle davanti a un
   furgone aziendale all'alba, luce dorata (missione sociale: volti e
   postura dignitosi, mai pietismo)

## Stock gratuito (senza account a pagamento)

- **Pexels / Pixabay**: video e foto CC-like libere (subacqueo, cieli, città,
  pioggia, drone). Ottimi per scrub e sfondi.
- **Poly.pizza, Quaternius, Kenney**: modelli 3D CC0/CC-BY (GLB) se serve
  sostituire la geometria procedurale.
- **Sketchfab**: account gratuito, filtrare "Downloadable" + licenza CC0/CC-BY
  (citare l'autore se CC-BY).
- Regola: verificare la licenza del singolo asset e annotare l'attribuzione
  nel footer quando richiesta.

## Nota qualità

Se l'utente può fotografare i mezzi/le persone reali, le foto vere battono
sempre l'AI su siti istituzionali: proporre prima quella strada, con l'AI
come riempitivo per le scene impossibili (viste aeree, notturne d'azione).
