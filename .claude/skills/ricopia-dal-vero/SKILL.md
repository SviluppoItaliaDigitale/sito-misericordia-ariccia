---
name: ricopia-dal-vero
description: Ricopia fedelmente dal vero persone, mani, corpi, gesti, oggetti, mezzi e attrezzature nei video 3D, nelle animazioni e nelle grafiche di Alessandro, partendo da riferimenti reali (figure delle linee guida, foto, video, modelli con licenza) e confrontando ogni posa con il riferimento, affiancato e sovrapposto, prima del render. Usala ogni volta che in un lavoro compare una figura umana o un oggetto reale da rendere credibile: mani nelle manovre di primo soccorso, posizione di un corpo, un manichino, un DAE, un'ambulanza, una barella, un attrezzo. Usala anche quando Alessandro dice «ricopia», «fallo come nella foto», «non esiste una mano così», «guarda l'anatomia», «cerca delle foto e ricopia». Lavora insieme a video-3d, motion-pc-genzano, storie-illustrate e revisore-video, e non le sostituisce.
---

# Ricopia dal vero

Cosa fa: fa somigliare al vero ciò che mostriamo. Si parte dai riferimenti, non dalla fantasia; si misura, si confronta affiancato e sovrapposto, e un controllo automatico ferma il render quando la figura non torna.

Origine: skill scritta per Alessandro Cuollo il 21/11/2026, dopo il video 3D del lattante. Le mani dell'adulto erano state costruite con forme semplici, a manopola, con il solo pollice. Alessandro: «Non esiste una persona con braccia e la mano composta soltanto dal pollice», «cerca sul web delle foto o video e ricopia», «crea una skill che sappia ricopiare fedelmente gli oggetti e le persone».

Regole di riferimento: `.claude/rules/qualita.md`, punti 10 e 11 (dita contate, scheda di verità) e `.claude/rules/comunicazione-social.md` (persone nelle foto).

## 1. Riferimenti prima di tutto

Prima di modellare o mettere in posa, raccogli **almeno tre riferimenti** della stessa cosa, da angolazioni diverse.

1. **Fonte primaria del gesto**, se è un gesto sanitario o tecnico. Sono le figure della linea guida in vigore, per esempio IRC/ERC 2025, con capitolo, figura e pagina. La figura decide che cosa è giusto.
2. **Foto o video reali** di persone vere o di manichini da corso, da più lati. Vanno bene anche quelle che manda Alessandro.
3. **Modelli o atlanti**: misure, proporzioni, numero e forma delle parti.

Salva ogni riferimento in `<scratchpad>/<lavoro>/riferimento/` con un file `fonti.md` accanto: URL, autore, licenza, data.

**I riferimenti con diritti d'autore** (Alamy, Dreamstime, Getty, frame di video altrui) si usano **solo per guardare**. Non entrano mai nel video, nella grafica o nel sito, nemmeno ritagliati o ricalcati al tratto. Si riproduce la posa sul nostro modello.

Per leggere una pagina o scaricare un'immagine:
- WebSearch e WebFetch;
- la skill `leggi-web`;
- un link `share.google`, che si apre con `curl -sL` su `https://www.google.com/share.google?q=<codice>` e da cui si legge `imgurl`.

## 2. Modelli veri, mai forme inventate per mani, volti e corpi

Ordine di scelta per le figure umane:

1. **MakeHuman** (esportazione CC0): corpo adulto e bambino da circa 2 anni, mani a cinque dita con le ossa, scheletro per le pose.
2. **BodyParts3D** (CC BY 4.0): anatomia interna (ossa, organi, vasi). La pelle non c'è.
3. **Modelli con licenza libera già scaricati**, oppure Sketchfab con un account dell'ente (CC0 o CC BY, credito nella descrizione).
4. **Costruzione in codice** solo per ciò che non ha un modello, per esempio il corpo del lattante sotto l'anno. Anche lì mani e piedi si prendono da un modello vero, e le proporzioni si misurano sui riferimenti.

Per gli oggetti (DAE, barella, ambulanza, attrezzi), prima le foto dell'oggetto vero dell'ente o del fabbricante, poi un modello libero. L'elenco delle risorse è in `memoria/risorse-3d.md`.

Mani, dita, volti e piedi non si fanno mai con primitive (cilindri, capsule, sfere). Se manca un modello vero, ci si ferma e si cerca.

## 3. Misure e proporzioni

Dai riferimenti ricava i **rapporti**, non i pixel.

- **Mano adulta**:
  - cinque dita;
  - pollice con due falangi e metacarpo che parte dal lato del polso;
  - le altre dita con tre falangi;
  - il medio è il più lungo e il mignolo il più corto;
  - lunghezza della mano circa uguale all'altezza del viso.
- **Lattante** (sotto l'anno):
  - testa circa un quarto dell'altezza;
  - arti corti e paffuti;
  - mani piccole con dita corte, semiflesse;
  - il torace sta quasi tutto dentro le due mani di un adulto.
- **Contatti**: punto di appoggio (per esempio i polpastrelli sulla metà inferiore dello sterno), direzione delle dita, angolo del polso, lato del corpo.

Scrivi le misure nella scheda di verità del lavoro (`qualita.md`, punto 11), ognuna con il riferimento da cui viene.

## 4. Confronto affiancato e sovrapposto

Per ogni posa:

1. Metti la telecamera del modello alla **stessa angolazione** del riferimento.
2. Fai il render della posa.
3. Crea il foglio di confronto:

```
python3 .claude/skills/ricopia-dal-vero/scripts/confronta.py RIFERIMENTO.jpg RENDER.jpg USCITA.jpg [--titolo "due pollici, dall'alto"]
```

Il foglio ha tre riquadri: riferimento, render, e i due sovrapposti al 50%. Guardalo ingrandito e annota ogni differenza: dita, polso, distanze, lato, proporzioni. Correggi la posa e rifai il confronto finché le differenze sono solo di stile, mai di anatomia o di gesto.

## 5. Controlli automatici nel generatore

Ogni pagina 3D espone `window.__controlli`, che `fotogrammi.py --controlli` legge e che ferma il render. Per ogni figura e ogni oggetto aggiungi i controlli che servono:

- **dita**: cinque per mano e per piede; pollice con 2 falangi, le altre con 3;
- **compenetrazioni**: dita e mani non entrano nel corpo, nel piano o negli oggetti;
- **punti di contatto**: dentro la zona giusta (per esempio la metà inferiore dello sterno), dal lato giusto;
- **zone vietate**: per esempio la mano delle pacche mai sopra testa o collo;
- **proporzioni**: rapporti entro una tolleranza dichiarata.

Prova ogni controllo rompendo apposta la scena (`?prova=…`) e verifica che segnali l'errore.

## 6. Prima del render, e dopo

- **Prima del render**: manda ad Alessandro un foglio con le pose principali affiancate ai riferimenti.
  - Nei contenuti sanitari passa scheda di verità e fogli all'agente `medico-emergenza`.
  - Se c'è una voce, la regia convoca `controllo-pronuncia`.
- **Dopo il render**:
  - fotogrammi uno ogni 0,5 s nelle scene con figure e oggetti;
  - dita contate a occhio;
  - poi `revisore-video`.

## Consegna

- **Fogli di confronto**: uno per posa, con i percorsi.
- **Riferimenti**: elenco con fonte e licenza.
- **Esito dei controlli automatici**: anche le prove con errore voluto.
- **Riga finale**: «Ricopia dal vero: N pose confrontate con M riferimenti, controlli X/X verdi, differenze residue: …».
