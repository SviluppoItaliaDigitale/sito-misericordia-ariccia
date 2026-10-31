#!/usr/bin/env python3
"""Calendario della «Parola»: le domeniche e le feste in cui il carosello esce sui social.

Scelta di Alessandro del 31/10/2026: oltre alle domeniche, le feste di precetto, la Settimana santa
(Mercoledì delle Ceneri, Giovedì santo, Venerdì santo), la Commemorazione dei defunti, Santo Stefano
e tutte le solennità che cadono in settimana. Le date vengono dal calendario liturgico italiano di
LitCal (stessa fonte della Liturgia del giorno), che applica già gli spostamenti (es. l'Annunciazione
del 2027 passa al 5 aprile). Le feste sono salvate in calendario.json accanto a questo file, così il
workflow di pubblicazione non dipende dalla rete; le domeniche si contano da sole.

  calendario.py aggiorna [ANNO …]   → riscrive calendario.json (senza anni: quest'anno e i due dopo)
  calendario.py oggi [AAAA-MM-GG]   → stampa il giorno della Parola ed esce con 0, con 1 se non lo è
  calendario.py prossimi [GIORNI]   → i giorni della Parola da oggi ai prossimi GIORNI (7), in JSON
  calendario.py copertura           → ultimo giorno coperto da calendario.json
Solo libreria standard.
"""

import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from liturgia_cei import scarica  # noqa: E402

FILE = Path(__file__).resolve().parent / "calendario.json"
LITCAL = "https://litcal.johnromanodorazio.com/api/dev/calendar/nation/IT/{anno}?year_type=CIVIL"
# oltre alle solennità (grado 6 di LitCal): grado 7 scelti e Santo Stefano; restano fuori i giorni
# della Settimana santa e dell'Ottava di Pasqua non scelti, la Messa del Crisma e la Veglia pasquale
GRADO_7 = {"Epiphany", "Christmas", "AshWednesday", "HolyThurs", "GoodFri"}
ALTRE = {"StStephenProtomartyr"}
# nei giorni penitenziali e nel ricordo dei defunti non si parla di «festa»
DEL_GIORNO = {"AshWednesday", "HolyThurs", "GoodFri", "AllSouls"}
DOMENICA, FESTA, GIORNO = "La Parola della domenica", "La Parola della festa", "La Parola del giorno"


def feste_litcal(anno):
    """Feste dell'anno (non di domenica) da LitCal: {data: {chiave, nome, titolo}}."""
    eventi = json.loads(scarica(LITCAL.format(anno=anno), "MisericordiaAriccia-Parola/1.0"))["litcal"]
    feste = {}
    for e in eventi:
        if e.get("is_vigil_mass") or e.get("year") != anno:
            continue
        data = dt.date.fromisoformat(e["date"][:10])
        chiave = e["event_key"]
        if data.isoweekday() == 7:
            continue
        if not (e["grade"] == 6 or chiave in GRADO_7 or chiave in ALTRE):
            continue
        feste[data.isoformat()] = {"chiave": chiave, "nome": e["name"],
                                   "titolo": GIORNO if chiave in DEL_GIORNO else FESTA}
    return feste


def carica():
    return json.loads(FILE.read_text(encoding="utf-8"))


def giorno_della_parola(giorno, cal=None):
    """Il giorno della Parola di quella data ({titolo, nome}), o None."""
    festa = (cal or carica())["feste"].get(giorno.isoformat())
    if festa:
        return {"data": giorno.isoformat(), "titolo": festa["titolo"], "nome": festa["nome"]}
    if giorno.isoweekday() == 7:
        return {"data": giorno.isoformat(), "titolo": DOMENICA, "nome": "domenica"}
    return None


def copertura(cal=None):
    return dt.date((max((cal or carica())["anni"])), 12, 31)


def oggi_roma():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("Europe/Rome")).date()
    except Exception:  # noqa: BLE001 — senza tzdata: UTC+1 basta per la data
        return (dt.datetime.utcnow() + dt.timedelta(hours=1)).date()


def main():
    comando = sys.argv[1] if len(sys.argv) > 1 else "prossimi"
    if comando == "aggiorna":
        anni = [int(a) for a in sys.argv[2:]] or [oggi_roma().year + k for k in range(3)]
        feste = {}
        for anno in anni:
            feste.update(feste_litcal(anno))
        cal = {"nota": "Generato da scripts/parola-domenica/calendario.py aggiorna: non modificare a mano.",
               "fonte": LITCAL.format(anno="AAAA"), "aggiornato": oggi_roma().isoformat(),
               "anni": anni, "feste": dict(sorted(feste.items()))}
        FILE.write_text(json.dumps(cal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{FILE.name}: {len(feste)} feste per gli anni {', '.join(map(str, anni))}")
        return 0
    cal = carica()
    if comando == "oggi":
        giorno = dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else oggi_roma()
        if giorno > copertura(cal):
            print(f"calendario.json non copre il {giorno}: lanciare «calendario.py aggiorna»", file=sys.stderr)
            return 2
        g = giorno_della_parola(giorno, cal)
        print(json.dumps(g, ensure_ascii=False) if g else f"{giorno}: niente Parola")
        return 0 if g else 1
    if comando == "prossimi":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        oggi = oggi_roma()
        giorni = [g for k in range(n + 1) if (g := giorno_della_parola(oggi + dt.timedelta(days=k), cal))]
        print(json.dumps(giorni, ensure_ascii=False, indent=1))
        return 0
    if comando == "copertura":
        print(copertura(cal).isoformat())
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
