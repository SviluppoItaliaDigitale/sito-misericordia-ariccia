#!/usr/bin/env python3
"""Riscrive le 10 news della rubrica «Primo soccorso passo passo» dai contenuti dei video di approfondimento."""
import json, re, subprocess, sys
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).parent)); import contenuti
REPO = Path(__file__).resolve().parents[2]
from comune import FF, scrivi
CAL = [('ictus','2026-10-06'),('infarto','2026-10-09'),('emorragia','2026-10-13'),('rianimazione','2026-10-16'),
       ('soffocamento','2026-10-20'),('anafilassi','2026-10-23'),('ustioni','2026-10-27'),('ipoglicemia','2026-10-30'),
       ('avvelenamento','2026-11-03'),('trauma-cranico','2026-11-06')]
D = {a['id']: a for a in yaml.safe_load((REPO/'content/dossier/primo-soccorso.md').read_text().split('---')[1])['argomenti']}
EXTRA = {
 'ictus': ("Ictus: riconoscerlo e cosa fare", "Viso, braccia, parola e gli altri segni improvvisi: come riconoscere un ictus, perché chiamare subito il 112 e cosa non dare alla persona."),
 'infarto': ("Infarto: i segni e cosa fare", "Dolore o peso al centro del petto, i segni più sfumati in donne, anziani e diabetici, perché chiamare il 112 e non andare in ospedale in auto."),
 'emorragia': ("Emorragia grave: premi e non mollare", "Guanti, pressione diretta per almeno 10 minuti, garza sopra garza, oggetti conficcati, laccio emostatico e shock: cosa fare passo passo."),
 'rianimazione': ("Arresto cardiaco: la rianimazione passo passo", "Nella Giornata mondiale della rianimazione: sicurezza, coscienza, respiro, 112 e DAE, e la simulazione del massaggio cardiaco a tempo, 110 compressioni al minuto."),
 'soffocamento': ("Soffocamento: 5 colpi e 5 compressioni", "Tosse, ostruzione grave, 5 colpi tra le scapole e 5 compressioni addominali, mostrati con i disegni animati, e cosa fare se la persona perde conoscenza."),
 'anafilassi': ("Anafilassi: riconoscerla e usare l'adrenalina", "Le cause, i segni della reazione allergica grave, come usare l'autoiniettore di adrenalina e in che posizione mettere la persona."),
 'ustioni': ("Ustioni: cosa fare e cosa non fare", "Fermare il fuoco, 20 minuti di acqua corrente, togliere anelli, coprire con la pellicola, i rimedi da evitare e quando chiamare il 112."),
 'ipoglicemia': ("Ipoglicemia: serve zucchero", "Come riconoscere un calo di zuccheri in una persona con diabete, quanto zucchero dare, la regola dei 15 minuti e cosa fare se non risponde."),
 'avvelenamento': ("Avvelenamento: niente rimedi fai da te", "Perché non far vomitare né dare latte, i numeri dei Centri Antiveleni di Roma, pelle e occhi, gas e fumi, e come prevenire in casa."),
 'trauma-cranico': ("Colpo alla testa: i segnali d'allarme", "Dopo un colpo alla testa: cosa osservare, quando chiamare il 112, collo e schiena, il bernoccolo e le 24 ore successive."),
}
def durata(p):
    e = subprocess.run([FF,'-i',str(p)],capture_output=True,text=True).stderr
    h,m,s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', e).groups(); return int(h)*3600+int(m)*60+float(s)
def fmt(sec):
    sec = int(round(sec/5)*5); m, s = divmod(sec, 60)
    return f"{m} minuto" + (f" e {s} secondi" if s else "") if m == 1 else (f"{m} minuti" + (f" e {s} secondi" if s else "") if m else f"{s} secondi")
for i, (k, data) in enumerate(CAL, 1):
    a = D[k]; tit, desc = EXTRA[k]; v = contenuti.V[k]
    dur = fmt(durata(REPO/f'static/video/primo-soccorso-{k}.mp4'))
    passi = []
    for sc in v['scene'][1:-1]:
        h = re.sub(r'^\d+ · ', '', sc['chip'])
        passi.append(f"### {h}\n\n{sc.get('sub') or sc['voce']}")
    passi = '\n\n'.join(passi)
    extra_rcp = ("\n\n**Nel video c'è la simulazione del massaggio cardiaco a tempo:** le mani spingono al ritmo giusto, 110 compressioni al minuto, con il conteggio ad alta voce da 1 a 30. Anche la musica di sottofondo va a 110 battiti al minuto: puoi usarla per allenare l'orecchio al ritmo." if k == 'rianimazione' else '')
    social = f"🩺 Primo soccorso passo passo · {i}/10 — {a['titolo']}. {desc} 📞 In ogni emergenza chiama il 112. Tutte le schede nel nostro dossier sul sito; per imparare davvero, vieni ai corsi di primo soccorso e BLSD: 348 4068657."
    testo = f'''---
title: "{tit}"
titoloSeo: "{a['titolo']}: cosa fare passo passo (linee guida IRC 2025)"
date: {data}
slug: "primo-soccorso-{k}"
description: "{desc}"
immagine: "/img/news/primo-soccorso-{k}-grafica.jpg"
social_video: "/video/primo-soccorso-{k}.mp4"
social_video_copertina: 1
social_testo: {json.dumps(social, ensure_ascii=False)}
italianoSemplice: |
  **{a['titolo']}: un video con i disegni che spiega cosa fare, passo dopo passo.**

  È il numero {i} della nostra rubrica sul primo soccorso.

  In ogni emergenza chiama il **112**.

  Tutti i consigli sono nella pagina del dossier sul primo soccorso.
---

![{a['titolo']}: una scena del video «Primo soccorso passo passo» della Misericordia di Ariccia](/img/news/primo-soccorso-{k}-grafica.jpg)

**Primo soccorso passo passo** è la nostra rubrica: dieci video di approfondimento con disegni animati, uno per ogni emergenza tra le più comuni. Oggi il numero **{i} di 10**: **{a['titolo'].lower()}**. *{a['motto']}.*{extra_rcp}

{{{{< video src="video/primo-soccorso-{k}.mp4" poster="img/video/primo-soccorso-{k}.jpg" verticale="si" titolo="{a['titolo']}: primo soccorso passo passo" descrizione="{desc}" data="{data}" didascalia="Il video dura circa {dur}, con disegni animati, voce narrante e sottotitoli." >}}}}

## Passo passo

{passi}

## Da ricordare

{a['riconosci']}

Trovi la scheda, insieme alle altre, nel dossier **[Primo soccorso passo passo](/dossier/primo-soccorso/#{k})**.

## Impara con noi

Queste sono informazioni generali e **non sostituiscono un corso**: le manovre si imparano davvero provando, con un istruttore accanto. Organizziamo [corsi di primo soccorso, BLSD e P-BLSD](/servizi/formazione/) aperti a tutti. Chiama o scrivi su WhatsApp al **[348 4068657](tel:+393484068657)**.

**In ogni emergenza, chiama sempre il [112](tel:112).**

*Fonte: [Linee guida RCP 2025, Italian Resuscitation Council](https://www.ircouncil.it/linee-guida-rcp-2025/).*
'''
    scrivi(REPO/f'content/news/{data}-primo-soccorso-{k}.md', testo)
    print('ok', data, k, dur)
