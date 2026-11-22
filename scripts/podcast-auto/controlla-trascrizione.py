#!/usr/bin/env python3
"""controlla-trascrizione.py — Primo filtro automatico su una puntata trascritta.

Viene dal podcast della Protezione Civile di Genzano, dove blocca gli errori già visti
nelle puntate scartate del 15/11/2026: numeri che le fonti non contengono, riferimenti
al lavoro sulle fonti («i documenti», «i manuali»), parole assolute o intensificazioni.
Per la Misericordia di Ariccia blocca anche ogni numero di telefono diverso dal 112,
anche se sta nelle fonti (l'unico numero da dire è il 112), e segnala, senza bloccare,
le frasi in cui si chiama la Misericordia: in emergenza si chiama il 112, la Misericordia
fa trasporti programmati. Non sostituisce il controllo frase per frase (README, passo 5).
Uso: controlla-trascrizione.py ID   → esce con 1 se trova anche un solo problema.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LAVORO = Path.home() / "podcast-lavoro-misericordia"

# Parole che non devono mai comparire (processo, strumenti, intensificazioni).
VIETATE = [
    r"\bdocument[io]\b", r"\bmanual[ei]\b", r"\blinee guida\b", r"\bfont[ei]\b",
    r"\bnotebook", r"intelligenza artificiale", r"\bgarantit", r"in assoluto",
    r"per nessun motivo", r"caratteri cubitali", r"\bmateriali che\b",
    r"esplorazione profonda", r"\bdeep dive\b", r"\bpodcast generat",
    # Dal 19/11/2026 (puntate chi-siamo e kit-emergenze scartate): le voci leggono le regole
    # («il 112, che si pronuncia…») e rafforzano le cautele delle pagine.
    r"si pronuncia", r"\brigorosamente\b", r"in alcun modo", r"\bassolutamente\b",
    # Dal 20/11/2026 (chiamare-il-112, generazione 1): chiusa morale che le pagine non contengono.
    r"ogni gesto conta", r"minuti cruciali", r"proteggere (le nostre|la nostra) comunit",
    # Dal 20/11/2026 (emorragia-ustioni scartata): cautele rafforzate e reazioni attribuite.
    r"\brigoros\w*", r"fa (davvero |proprio )?la differenza", r"\bsbirci\w*", r"\bimpuls[oi]\b",
    # Dal 20/11/2026 (trasporti-sanitari, generazione 1): «avviso vitale», «il 112, detto 112».
    r"\bvital[ei]\b", r"\bdetto (il |l')?(112|uno)",
    # Dal 20/11/2026 (opere-di-misericordia, generazione 1): «seguendo il testo».
    r"\b(seguendo|secondo|come dice) il testo\b",
    # Dal 20/11/2026 (diventa-volontario, generazione 1): chiusa morale e giudizi delle voci.
    r"da meditare", r"mi ha colpit\w*",
    # Dal 21/11/2026 (trauma-convulsioni-svenimento, generazione 1): «come dicono i testi».
    r"\b(come|secondo) (dicono |indicano |riportano )?(i|questi|nei) test[io]\b",
    # Dal 21/11/2026 (prevenzione-stagionale, generazione 1): istruzioni lette ad alta voce e
    # commenti sui numeri che la pagina non fa.
    r"indicazione (è )?complet\w*", r"divieto esplicito", r"\bviene precisat\w*", r"numeri (altissim|enorm|impression|pazzesc)\w*",
    # Dal 21/11/2026 (prevenzione-stagionale, ritirata dopo la pubblicazione): regole lette ad alta voce.
    r"la regola dice", r"precisare la regola",
    # Dal 22/11/2026 (servizi-sociali, generazione 2): il motto del piè di pagina («nella tradizione
    # delle Misericordie, al fianco del prossimo dal 1244») attribuito alla Misericordia di Ariccia,
    # nata nel 1994. Il motto non si adatta e non si legge nelle puntate.
    r"fianco del prossimo",
]
# Dal 21/11/2026 (puntate ritirate al ricontrollo): parole che le fonti precisano sempre.
# Se la fonte ha la forma completa e la trascrizione dice la parola senza, è un errore:
# «spray nasale» senza «di adrenalina» vale per qualunque spray.
DA_NON_SPEZZARE = [
    (r"spray nasale", r"spray nasale di adrenalina"),
    (r"(difficoltà a deglutire|deglutire) o gonfiore|gonfiore o difficoltà", r"gonfiore del viso o della gola"),
    (r"succede a chi ha il diabete", r"succede soprattutto a chi ha il diabete"),
]
# Dal 21/11/2026 (storia-delle-misericordie: «670.000 iscritti» senza «circa»): un numero che
# nelle fonti è accompagnato da una di queste parole (anche una volta sola: le tabelle dei numeri
# lo scrivono nudo) deve averla anche nella puntata.
QUALIFICA_NUMERI = r"(circa|oltre|più di|quasi|almeno|fino a|meno di|intorno a|sopra i|sotto i)\s+$"
# Frasi da guardare a mano: la Misericordia non si chiama in emergenza.
DA_GUARDARE = [r"chiam\w* (direttamente |subito |proprio )?(la|alla) misericordia", r"misericordia in emergenza",
               r"pronto soccorso della misericordia", r"\b118\b",
               # Dal 19/11/2026: «l'istinto spinge a…» (ictus-infarto) e i recapiti letti dalle regole.
               r"\bistint\w*", r"\brecapit\w*",
               # Dal 20/11/2026: le condizioni si perdono («non dare farmaci» senza «se non te lo dice
               # l'operatore»; «la posizione arriva in automatico» senza «se chiami da un cellulare»).
               r"\bfarmac\w*", r"posizione arriva",
               # Dal 20/11/2026 (emorragia-ustioni): l'ordine dei passi cambiato («la primissima cosa
               # da fare» non era quella della scheda), esempi aggiunti («tipo un ginocchio») e
               # «cautela obbligatoria».
               r"\b(primissim\w*|prima) cosa\b", r"\bpunt\w* (importante|fondamentale|chiave)", r"\btipo (un|una|il|la)\b", r"\bobbligatori\w*",
               # Dal 20/11/2026 (opere-di-misericordia): giudizi delle voci.
               r"\bessenzial\w*", r"\battual[ei]\b", r"\bmi sembr\w*",
               # Regole lette ad alta voce e righe inventate dal riconoscitore nei silenzi (da togliere).
               r"indicazion\w* (esatt|chiar|precis)\w*", r"amara\.org", r"sottotitoli"]
# Parole assolute: ammesse solo se presenti anche nelle fonti.
ASSOLUTE = [r"\bsempre\b", r"\bmai\b", r"\bcertamente\b", r"\binevitabilmente\b"]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower())


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    cartella = LAVORO / sys.argv[1]
    testo = norm((cartella / "trascrizione-grezza.txt").read_text(encoding="utf-8"))
    fonte = norm((cartella / "fonte.md").read_text(encoding="utf-8"))
    problemi: list[str] = []

    def contesto(m: re.Match) -> str:
        return testo[max(0, m.start() - 60):m.end() + 60]

    for pat in VIETATE:
        for m in re.finditer(pat, testo):
            # La «copia dei documenti» del kit di emergenza è un consiglio, non il processo.
            if "document" in pat and re.search(r"cop(ia|ie) de(i|gli) $", testo[max(0, m.start() - 12):m.start()]):
                continue
            # Dal 20/11/2026 (kit-bambini-neonati): «documenti sanitari», «farmaci, documenti» sono
            # contenuto dei kit, non il processo: si accettano se la parola con le vicine sta identica nelle fonti.
            if "document" in pat:
                prima = re.findall(r"[\w']+", testo[max(0, m.start() - 25):m.start()])[-1:]
                dopo = re.findall(r"[\w']+", testo[m.end():m.end() + 25])[:1]
                articoli = {"i", "gli", "dei", "degli", "ai", "agli", "nei", "dai", "sui", "le", "tali", "questi"}
                vicine = [" ".join([m.group(0)] + dopo)]
                if prima and prima[0] not in articoli:
                    vicine.append(" ".join(prima + [m.group(0)]))
                if any(re.search(r"\b" + re.escape(v).replace(r"\ ", r"\W+") + r"\b", fonte) for v in vicine if " " in v):
                    continue
                # Documenti storici («il documento è del 1321»): un anno delle fonti entro 20 parole.
                seguito = " ".join(re.findall(r"[\w']+", testo[m.end():m.end() + 160])[:20])
                if any(a in fonte for a in re.findall(r"\b1[0-9]{3}\b|\b20[0-9]{2}\b", seguito)):
                    continue
            problemi.append(f"parola vietata «{m.group(0)}»: …{contesto(m)}…")
    for pat in ASSOLUTE:
        n_t, n_f = len(re.findall(pat, testo)), len(re.findall(pat, fonte))
        if n_t and not n_f:
            for m in re.finditer(pat, testo):
                problemi.append(f"parola assoluta assente dalle fonti «{m.group(0)}»: …{contesto(m)}…")
    # Numeri: ogni numero di due o più cifre (anche spezzato da trattini o spazi,
    # come i telefoni) deve comparire nelle fonti. Il 112 è sempre ammesso.
    # Dal 20/11/2026: il numero deve stare nelle fonti come numero a sé (o come gruppo intero),
    # non come pezzo di cifre incollate: «110 compressioni al minuto» passava perché «110»
    # compariva dentro altre cifre della pagina (rianimazione-soffocamento, generazione 1).
    numeri_fonte = set(re.findall(r"\d+", fonte))
    numeri_fonte |= {re.sub(r"[ .\-]", "", g) for g in re.findall(r"\d[\d .\-]*\d", fonte)}
    for m in re.finditer(r"\d[\d .\-]*\d", testo):
        num = re.sub(r"[ .\-]", "", m.group(0))
        if re.fullmatch(r"(112)+", num) or num in numeri_fonte:
            continue
        secoli = {"200": "duecento", "300": "trecento", "400": "quattrocento", "500": "cinquecento",
                  "600": "seicento", "700": "settecento", "800": "ottocento", "900": "novecento"}
        if num in secoli and secoli[num] in fonte:
            continue
        # Dal 21/11/2026: «anni 90» detto dalle voci quando la fonte scrive «anni Novanta»
        # (dalla-barella-all-ambulanza, generazione 1). Vale solo dopo «anni».
        decenni = {"20": "venti", "30": "trenta", "40": "quaranta", "50": "cinquanta",
                   "60": "sessanta", "70": "settanta", "80": "ottanta", "90": "novanta"}
        if (num in decenni and testo[max(0, m.start() - 5):m.start()].endswith("anni ")
                and f"anni {decenni[num]}" in fonte):
            continue
        # «25-26 gradi», «da 5 a 7»: ogni pezzo deve stare nelle fonti.
        pezzi = re.findall(r"\d+", m.group(0))
        if len(pezzi) > 1 and all(x in numeri_fonte or x == "112" for x in pezzi):
            continue
        problemi.append(f"numero assente dalle fonti «{m.group(0).strip()}»: …{contesto(m)}…")

    # Numeri «circa»: se la fonte accompagna il numero con «circa», «oltre»…,
    # la puntata deve dirlo con una di quelle parole.
    for m in re.finditer(r"\d[\d.]*\d|\d", testo):
        num = m.group(0)
        if len(num) < 3 or re.fullmatch(r"(112)+|1[0-9]{3}|20[0-9]{2}", num):
            continue  # cifre singole, 112 e anni
        in_fonte = [f for f in re.finditer(r"(?<![\d.,])" + re.escape(num) + r"(?![\d,]|\.\d)", fonte)]
        if re.search(r"(nell|dell|all|dall)'$", testo[max(0, m.start() - 5):m.start()]):
            continue  # secoli: «nell'800»
        if not in_fonte or not any(re.search(QUALIFICA_NUMERI, fonte[max(0, f.start() - 14):f.start()]) for f in in_fonte):
            continue
        if not re.search(QUALIFICA_NUMERI, testo[max(0, m.start() - 14):m.start()]):
            problemi.append(f"numero senza «circa/oltre…» che le fonti gli danno «{num}»: …{contesto(m)}…")
    for corta, completa in DA_NON_SPEZZARE:
        if not re.search(completa, fonte):
            continue
        for m in re.finditer(corta, testo):
            if not re.match(completa, testo[m.start():]) and not re.search(completa, testo[max(0, m.start() - 40):m.end() + 40]):
                problemi.append(f"manca la precisazione delle fonti («{completa}»): …{contesto(m)}…")

    # Telefoni: qualunque numero di sei o più cifre (anche a gruppi separati da
    # spazi o punti) è vietato, anche se sta nelle fonti; resta solo il 112.
    for m in re.finditer(r"(?<![\d,])\d{2,}(?:[ .]\d{2,})*(?![\d,])", testo):
        num = re.sub(r"[ .]", "", m.group(0))
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", m.group(0).strip()):
            continue  # quantità («670.000 iscritti»): il controllo dei numeri sopra vuole che stia nelle fonti
        if len(num) >= 6 and not re.fullmatch(r"(112)+", num):
            problemi.append(f"numero di telefono diverso dal 112 «{m.group(0).strip()}»: …{contesto(m)}…")
    avvisi = [f"da guardare a mano «{m.group(0)}»: …{contesto(m)}…"
              for pat in DA_GUARDARE for m in re.finditer(pat, testo)]
    for a in avvisi:
        print(" ! ", a)

    if problemi:
        print(f"{len(problemi)} problemi nella trascrizione di {sys.argv[1]}:")
        for p in problemi:
            print(" -", p)
        return 1
    print(f"Nessun problema automatico in {sys.argv[1]}: ora il controllo frase per frase.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
