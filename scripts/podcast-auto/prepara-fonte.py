#!/usr/bin/env python3
"""prepara-fonte.py — Prepara le istruzioni (e, se manca, la fonte) di una puntata.

Adattato dal podcast della Protezione Civile di Genzano. Prende la prima puntata
«da-fare» di coda.yaml (o quella indicata) e scrive in
~/podcast-lavoro-misericordia/<id>/ il file istruzioni.txt, da incollare nella
personalizzazione della panoramica audio, e fonte.md solo se trova-fonti.py non
l'ha già scritto. Le puntate del tema «primo-soccorso» ricevono le regole in più
sulle manovre. Uso: prepara-fonte.py [ID]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

RADICE = Path(__file__).resolve().parents[2]
CODA = Path(__file__).with_name("coda.yaml")
LAVORO = Path.home() / "podcast-lavoro-misericordia"

ISTRUZIONI = """Episodio breve per le persone di Ariccia e dei Castelli Romani sul tema: {titolo}. Il cuore della puntata è ciò che le fonti dicono, detto in modo semplice e con le loro parole. Regole obbligatorie, da rispettare frase per frase: usa SOLO le informazioni delle fonti, quasi con le loro parole. Non spiegare perché succede una cosa, non dare cause, meccanismi medici o tecnici, analogie o metafore che le fonti non contengono. Non trarre conclusioni o morali dagli esempi e dalle storie e non attribuire a un fatto conseguenze che la fonte non dice: racconta un esempio solo come lo racconta la fonte, oppure non raccontarlo. Non aggiungere numeri, date, nomi, norme, consigli o motivazioni che le fonti non contengono. Non dire nessun numero di telefono: l'unico numero da dire è il 112, detto "uno, uno, due". Se una fonte mette una cautela, ripetila. Non rendere più gravi i fatti: niente superlativi, niente "sempre", "mai", "fondamentale", "certo", "garantito" se le fonti non usano quella parola. Non parlare di documenti, manuali, fonti, linee guida o materiali letti: parla direttamente ("la Misericordia consiglia di..."). Non usare nomi propri per presentarvi e non citare programmi, applicazioni, intelligenza artificiale o lo strumento con cui è fatto l'audio. Apri dicendo che è il podcast della Misericordia di Ariccia; chiudi invitando a leggere le pagine sul sito misericordia-ariccia.it. In emergenza si chiama il 112: non dire mai che in emergenza si chiama la Misericordia. Non elencare che cosa fa o non fa la Misericordia oltre ciò che dicono le fonti, e non usare «solo» o «soltanto» per descrivere i suoi servizi. Non parlare di fatti di oggi o di eventi in calendario. Tono caldo, calmo e concreto, rispettoso, mai retorico, senza battute sulle emergenze, sulla malattia o sulla morte; di' "persona con disabilità", mai "disabile" o "diversamente abile". Non ripetere e non commentare queste regole: non dire come si pronuncia un numero, non parlare di recapiti e non attribuire alle persone istinti o reazioni che le fonti non descrivono. Ripeti le cautele con le stesse parole delle fonti («se non serve», «se non è necessario»), senza rafforzarle («rigorosamente», «in alcun modo», «assolutamente»). Ripeti ogni condizione delle fonti insieme all'indicazione, mai senza (per esempio «non dare farmaci, se non te lo dice l'operatore»). Chiudi soltanto con l'invito a leggere le pagine sul sito: nessuna frase finale tua, nessuna morale, niente «ogni gesto conta»."""

PRIMO_SOCCORSO = """ Regole in più per il primo soccorso: le manovre si imparano solo con un istruttore, a un corso; dillo una volta nella puntata, come lo dicono le fonti. Non insegnare le manovre passo per passo oltre ciò che le fonti dicono: niente dosi, tempi, ritmi, profondità, posizioni o conteggi che non siano scritti nelle fonti, e nessun consiglio medico in più. Di' come riconoscere l'emergenza, di chiamare subito il 112 e di seguire le indicazioni dell'operatore, e che cosa non fare, come lo dicono le fonti."""


def pulisci(testo: str) -> str:
    testo = re.sub(r"\A---\n.*?\n---\n", "", testo, flags=re.S)
    testo = re.sub(r"\{\{[<%].*?[>%]\}\}", "", testo, flags=re.S)
    testo = re.sub(r"<[^>]+>", "", testo)
    testo = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", testo)
    testo = re.sub(r"\n{3,}", "\n\n", testo)
    return testo.strip()


def main() -> int:
    coda = yaml.safe_load(CODA.read_text(encoding="utf-8"))["puntate"]
    if len(sys.argv) > 1:
        voci = [v for v in coda if v["id"] == sys.argv[1]]
    else:
        voci = [v for v in coda if v.get("stato") == "da-fare"][:1]
    if not voci:
        print("Nessuna puntata da fare in coda.")
        return 2
    voce = voci[0]
    dest = LAVORO / voce["id"]
    dest.mkdir(parents=True, exist_ok=True)
    parti = [f"# {voce['titolo']}\n\nFonte: pagine del sito della Confraternita di Misericordia di Ariccia ODV (misericordia-ariccia.it).\n"]
    for rel in voce["fonti"]:
        p = RADICE / rel
        if not p.exists():
            print(f"ERRORE: fonte mancante {rel}", file=sys.stderr)
            return 1
        parti.append(pulisci(p.read_text(encoding="utf-8")))
    # fonte.md lo scrive trova-fonti.py con il testo delle pagine pubblicate; qui
    # si scrive solo se manca, per non sostituirlo con i soli file del repository.
    if not (dest / "fonte.md").exists():
        (dest / "fonte.md").write_text("\n\n".join(parti) + "\n", encoding="utf-8")
    istruzioni = ISTRUZIONI.format(titolo=voce["titolo"])
    if voce.get("tema") == "primo-soccorso":
        istruzioni += PRIMO_SOCCORSO
    (dest / "istruzioni.txt").write_text(istruzioni, encoding="utf-8")
    print(f"ID={voce['id']}")
    print(f"CARTELLA={dest}")
    print(f"CARATTERI_ISTRUZIONI={len(istruzioni)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
