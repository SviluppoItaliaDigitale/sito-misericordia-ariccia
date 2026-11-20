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
]
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
        # «25-26 gradi», «da 5 a 7»: ogni pezzo deve stare nelle fonti.
        pezzi = re.findall(r"\d+", m.group(0))
        if len(pezzi) > 1 and all(x in numeri_fonte or x == "112" for x in pezzi):
            continue
        problemi.append(f"numero assente dalle fonti «{m.group(0).strip()}»: …{contesto(m)}…")

    # Telefoni: qualunque numero di sei o più cifre (anche a gruppi separati da
    # spazi o punti) è vietato, anche se sta nelle fonti; resta solo il 112.
    for m in re.finditer(r"(?<![\d,])\d{2,}(?:[ .]\d{2,})*(?![\d,])", testo):
        num = re.sub(r"[ .]", "", m.group(0))
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
