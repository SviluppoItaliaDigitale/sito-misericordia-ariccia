#!/usr/bin/env python3
"""Scrive le news programmate della 2ª serie «Primo soccorso passo passo» e lo speciale Giornata del volontariato."""
import json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import contenuti
REPO = Path(__file__).resolve().parents[2]
from comune import FF, scrivi
def durata(p):
    e = subprocess.run([FF,'-i',str(p)],capture_output=True,text=True).stderr
    h,m,s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', e).groups(); return int(h)*3600+int(m)*60+float(s)
def fmt(sec):
    sec = int(round(sec/5)*5); m, s = divmod(sec, 60)
    if m == 0: return f"{s} secondi"
    base = "1 minuto" if m == 1 else f"{m} minuti"
    return base + (f" e {s} secondi" if s else "")
CAL = [('convulsioni','2026-11-10'),('incidente-stradale','2026-11-13'),('svenimento','2026-11-17'),('soffocamento-lattante','2026-11-20'),
       ('rianimazione-bambino','2026-11-24'),('fratture','2026-11-27'),('freddo','2026-12-01'),('monossido','2026-12-04'),
       ('asma','2026-12-08'),('batterie','2026-12-11'),('cadute-anziani','2026-12-15'),('botti','2026-12-18'),('cassetta','2026-12-22')]
EXTRA = {
 'convulsioni': ("Convulsioni: cosa fare e cosa non fare", "Crisi convulsiva: spazio intorno, niente in bocca, proteggere la testa, guardare l'orologio e quando chiamare il 112. Poi, su un fianco."),
 'incidente-stradale': ("Incidente stradale: come aiutare in sicurezza", "Nella settimana della Giornata in ricordo delle vittime della strada: quattro frecce, giubbotto, triangolo, 112, non spostare i feriti e non togliere il casco."),
 'svenimento': ("Svenimento: sdraiato e gambe su", "I segni che annunciano uno svenimento, le contromanovre per evitarlo, cosa fare se la persona sviene e quando chiamare il 112."),
 'soffocamento-lattante': ("Soffocamento nel lattante: 5 pacche e 5 compressioni", "Nella Giornata dei diritti dell'infanzia: come riconoscere il soffocamento in un bambino sotto l'anno e le manovre giuste, mostrate con i disegni animati."),
 'rianimazione-bambino': ("Rianimazione nel bambino e nel lattante", "Cinque soffi, due pollici o una mano, 30 compressioni e 2 soffi, il defibrillatore anche nei bambini, e la simulazione a tempo delle compressioni."),
 'fratture': ("Fratture e distorsioni: ferma, non raddrizzare", "Come riconoscere una frattura, perché non raddrizzare l'arto, il ghiaccio nel panno, la frattura esposta e quando chiamare il 112."),
 'freddo': ("Ipotermia e congelamento: cosa fare", "I segni dell'ipotermia, come scaldare una persona in modo sicuro, perché niente alcol, il congelamento e chi rischia di più."),
 'monossido': ("Monossido di carbonio: il pericolo che non si sente", "Stufe, camini e caldaie: i segni dell'intossicazione da monossido, cosa fare subito e come prevenirla con controlli e rilevatore."),
 'asma': ("Crisi d'asma: cosa fare", "I segni della crisi d'asma, la posizione giusta, come aiutare con lo spray e quando chiamare il 112."),
 'batterie': ("Batterie a bottone e calamite: un'emergenza", "Se un bambino ingoia una batteria a bottone o delle calamite: perché basta il dubbio per correre in ospedale, cosa non fare e come prevenire."),
 'cadute-anziani': ("Se un anziano cade: cosa fare", "Non tirarlo su subito, le domande da fare, quando chiamare il 112, come rialzarsi a tappe e come rendere la casa più sicura."),
 'botti': ("Botti di Capodanno: prevenzione e primo soccorso", "Fuochi solo a norma CE, mai raccogliere petardi inesplosi, e cosa fare per ustioni, ferite alla mano, dita staccate e lesioni agli occhi."),
 'cassetta': ("La cassetta di primo soccorso di casa e auto", "Cosa mettere nella cassetta di primo soccorso, i numeri utili, cosa tenere in auto, le scadenze, e gli auguri di buone feste."),
}
def passi(v):
    out = []
    for sc in v['scene'][1:-1]:
        h = re.sub(r'^\d+ · ', '', sc['chip']); t = sc.get('sub') or sc['voce']
        out.append(f"### {h}\n\n{t}")
    return '\n\n'.join(out)
for i, (k, data) in enumerate(CAL, 1):
    v = contenuti.V[k]; tit, desc = EXTRA[k]; dur = fmt(durata(REPO/f'static/video/primo-soccorso-{k}.mp4'))
    extra = ("\n\n**Nel video c'è la simulazione delle compressioni a tempo:** 110 al minuto, con il conteggio da 1 a 30 e la musica allo stesso ritmo." if k == 'rianimazione-bambino' else '')
    social = f"🩺 Primo soccorso passo passo · 2ª serie {i}/13 — {v['nome']}. {desc} 📞 In ogni emergenza chiama il 112. Per imparare davvero, vieni ai corsi di primo soccorso, BLSD e P-BLSD: 348 4068657."
    testo = f'''---
title: "{tit}"
titoloSeo: "{v['nome']}: cosa fare passo passo (linee guida ERC/IRC 2025)"
date: {data}
slug: "primo-soccorso-{k}"
description: "{desc}"
immagine: "/img/news/primo-soccorso-{k}-grafica.jpg"
social_video: "/video/primo-soccorso-{k}.mp4"
social_video_copertina: 1
social_testo: {json.dumps(social, ensure_ascii=False)}
italianoSemplice: |
  **{v['nome']}: un video con i disegni che spiega cosa fare, passo dopo passo.**

  È il numero {i} della seconda serie della nostra rubrica sul primo soccorso.

  In ogni emergenza chiama il **112**.
---

![{v['nome']}: una scena del video «Primo soccorso passo passo» della Misericordia di Ariccia](/img/news/primo-soccorso-{k}-grafica.jpg)

**Primo soccorso passo passo** torna con la **seconda serie**: tredici video di approfondimento con disegni animati, fino a Natale. Oggi il numero **{i} di 13**: **{v['nome'].lower()}**.{extra}

{{{{< video src="video/primo-soccorso-{k}.mp4" poster="img/video/primo-soccorso-{k}.jpg" verticale="si" titolo="{v['nome']}: primo soccorso passo passo" descrizione="{desc}" data="{data}" didascalia="Il video dura circa {dur}, con disegni animati, voce narrante e sottotitoli." >}}}}

## Passo passo

{passi(v)}

Trovi la scheda riassuntiva, insieme alle altre 22, nel dossier **[Primo soccorso passo passo](/dossier/primo-soccorso/#{k})**.

## Impara con noi

Queste sono informazioni generali e **non sostituiscono un corso**: le manovre si imparano davvero provando, con un istruttore accanto. Organizziamo [corsi di primo soccorso, BLSD e P-BLSD](/servizi/formazione/) aperti a tutti. Chiama o scrivi su WhatsApp al **[348 4068657](tel:+393484068657)**.

**In ogni emergenza, chiama sempre il [112](tel:112).**

*Fonte: [Linee guida RCP 2025, Italian Resuscitation Council](https://www.ircouncil.it/linee-guida-rcp-2025/) ed [European Resuscitation Council](https://www.erc.edu/).*
'''
    scrivi(REPO/f'content/news/{data}-primo-soccorso-{k}.md', testo)
    print('ok', data, k, dur)
# speciale volontariato
k = 'giornata-volontariato'; dur = fmt(durata(REPO/f'static/video/{k}.mp4'))
desc = "Il 5 dicembre è la Giornata internazionale del volontariato: grazie ai volontari della Misericordia di Ariccia. Trasporti, famiglie, eventi: c'è posto anche per te, dai 16 agli 80 anni."
social = "🤝 5 dicembre, Giornata internazionale del volontariato. Grazie ai volontari della Misericordia di Ariccia: che Iddio ve ne renda merito! Vuoi unirti a noi? Dai 16 agli 80 anni, nessuna competenza richiesta: la formazione la facciamo insieme. Iscrizioni 328 8105399 · info 348 4068657."
testo = f'''---
title: "Giornata del volontariato: grazie, e c'è posto anche per te"
titoloSeo: "Giornata internazionale del volontariato: diventa volontario ad Ariccia"
date: 2026-12-05
slug: "giornata-volontariato-2026"
description: "{desc}"
immagine: "/img/news/{k}-grafica.jpg"
social_video: "/video/{k}.mp4"
social_video_copertina: 1
social_testo: {json.dumps(social, ensure_ascii=False)}
italianoSemplice: |
  **Il 5 dicembre è la Giornata del volontariato.**

  Diciamo grazie ai nostri volontari.

  Anche tu puoi diventare volontario: dai 16 agli 80 anni. Impari tutto con noi.

  Chiama il **328 8105399**.
---

![Giornata internazionale del volontariato: una scena del video della Misericordia di Ariccia](/img/news/{k}-grafica.jpg)

Il **5 dicembre** è la **Giornata internazionale del volontariato**. Per noi è l'occasione per dire una parola semplice: **grazie**. Grazie ai volontari della Misericordia di Ariccia, che ogni giorno regalano il loro tempo a chi ha bisogno.

{{{{< video src="video/{k}.mp4" poster="img/video/{k}.jpg" verticale="si" titolo="Giornata del volontariato: grazie, e c'è posto anche per te" descrizione="{desc}" data="2026-12-05" didascalia="Il video dura circa {dur}, con disegni animati, voce narrante e sottotitoli." >}}}}

## Cosa fanno i nostri volontari

- **[Trasporti sanitari e sociali](/trasporto-infermi/)**: accompagnano chi deve curarsi, in ambulanza, in auto o con i [mezzi attrezzati per la sedia a rotelle](/trasporto-disabili-castelli-romani/).
- **Centro di Ascolto e Banco Alimentare**: accolgono le famiglie in difficoltà.
- **[Assistenza sanitaria agli eventi](/assistenza-eventi/)**: a gare, feste e manifestazioni dei Castelli Romani.
- **[Formazione](/servizi/formazione/)**: i corsi di primo soccorso, BLSD e P-BLSD.

## C'è posto anche per te

Possono diventare volontari **donne e uomini dai 16 agli 80 anni**. Non servono competenze: **la formazione la facciamo insieme**, passo dopo passo. Tutti i dettagli sono nella pagina **[Diventa volontario](/diventa-volontario/)**.

**Iscrizioni: [328 8105399](tel:+393288105399)** · Telefono e WhatsApp: [348 4068657](tel:+393484068657).

A tutti i volontari, con l'antico motto delle Misericordie: **«Che Iddio ve ne renda merito»**.
'''
scrivi(REPO/'content/news/2026-12-05-giornata-volontariato.md', testo)
print('ok speciale', dur)
