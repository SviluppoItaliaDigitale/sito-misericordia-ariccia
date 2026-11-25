#!/usr/bin/env python3
"""Controlla che i post delle giornate e delle ricorrenze siano usciti davvero.

Legge le schede .github/social/giornate/AAAA-MM-GG.json e il registro .github/social/pubblicati.json:
  - la scheda di oggi deve essere nel registro (voce «giornata-AAAA-MM-GG», con Facebook e Instagram)
    da mezzogiorno in poi, ora italiana;
  - le schede dei tre giorni prima devono esserci tutte.
Nasce il 25/11/2026: i post del 15/11 (Giornata dei poveri) e del 20/11 (infanzia) non sono mai usciti,
perché GitHub aveva avviato il giro nel pomeriggio, fuori dalla finestra 8-12, e il giro chiudeva in verde.

Uso:  controlla_giornate.py [--oggi AAAA-MM-GG] [--ora HHMM] [--radice CARTELLA]   esce 0 (a posto) o 1 (manca)
      controlla_giornate.py --autotest
Stampa una riga «stato=ok» oppure «stato=manca:…» e, se serve, l'elenco in chiaro per la issue.
"""
import datetime as dt
import json
import pathlib
import sys
import tempfile
import zoneinfo

RETI = ("facebook", "instagram")
GIORNI_INDIETRO = 3
DA_QUANDO = 1200  # ora italiana (HHMM) da cui la scheda di oggi deve essere uscita


def mancanti(radice, oggi, ora):
    """Elenco di (giorno, reti che mancano) per oggi (da mezzogiorno) e per i tre giorni prima."""
    cartella = pathlib.Path(radice) / ".github/social/giornate"
    registro = json.loads((pathlib.Path(radice) / ".github/social/pubblicati.json").read_text(encoding="utf-8"))
    fuori = []
    for indietro in range(GIORNI_INDIETRO, -1, -1):
        giorno = oggi - dt.timedelta(days=indietro)
        if not (cartella / f"{giorno.isoformat()}.json").exists():
            continue
        if indietro == 0 and ora < DA_QUANDO:
            continue
        voce = registro.get(f"giornata-{giorno.isoformat()}", {})
        manca = [r for r in RETI if r not in voce]
        if manca:
            fuori.append((giorno.isoformat(), manca))
    return fuori


def autotest():
    oggi = dt.date(2026, 11, 25)
    casi = 0
    with tempfile.TemporaryDirectory() as t:
        r = pathlib.Path(t)
        (r / ".github/social/giornate").mkdir(parents=True)
        reg = r / ".github/social/pubblicati.json"

        def scrivi(schede, registro):
            for f in (r / ".github/social/giornate").glob("*.json"):
                f.unlink()
            for g in schede:
                (r / ".github/social/giornate" / f"{g}.json").write_text("{}", encoding="utf-8")
            reg.write_text(json.dumps(registro), encoding="utf-8")

        def atteso(schede, registro, ora, risultato, nome):
            nonlocal casi
            scrivi(schede, registro)
            avuto = mancanti(r, oggi, ora)
            assert avuto == risultato, f"{nome}: atteso {risultato}, avuto {avuto}"
            casi += 1

        piena = {"facebook": "1", "instagram": "2"}
        atteso([], {}, 1500, [], "nessuna scheda")
        atteso(["2026-11-25"], {}, 900, [], "oggi, prima di mezzogiorno")
        atteso(["2026-11-25"], {}, 1200, [("2026-11-25", ["facebook", "instagram"])], "oggi, da mezzogiorno, non uscita")
        atteso(["2026-11-25"], {"giornata-2026-11-25": piena}, 1500, [], "oggi, uscita")
        atteso(["2026-11-25"], {"giornata-2026-11-25": {"facebook": "1"}}, 1500, [("2026-11-25", ["instagram"])], "oggi, solo Facebook")
        atteso(["2026-11-24"], {}, 800, [("2026-11-24", ["facebook", "instagram"])], "ieri non uscita, anche di mattina")
        atteso(["2026-11-22"], {}, 800, [("2026-11-22", ["facebook", "instagram"])], "tre giorni fa non uscita")
        atteso(["2026-11-21"], {}, 2300, [], "quattro giorni fa: fuori dal controllo")
        atteso(["2026-11-20", "2026-11-25", "2026-12-03"], {"giornata-2026-11-25": piena}, 2300, [], "il caso del 20/11 visto il 25/11, e una scheda futura")
        atteso(["2026-11-20"], {}, 1600, [], "il 20/11 visto il 25/11")
        # il guasto vero: scheda del 20/11 mai uscita, vista il 21/11
        avuto = mancanti(r, dt.date(2026, 11, 21), 900); casi += 1
        assert avuto == [("2026-11-20", ["facebook", "instagram"])], avuto
    print(f"Autotest del controllo delle giornate: {casi} casi su {casi} come atteso.")
    return 0


def main():
    a = sys.argv[1:]
    if "--autotest" in a:
        return autotest()

    def valore(nome, predefinito=None):
        return a[a.index(nome) + 1] if nome in a else predefinito

    adesso = dt.datetime.now(zoneinfo.ZoneInfo("Europe/Rome"))
    oggi = dt.date.fromisoformat(valore("--oggi", adesso.date().isoformat()))
    ora = int(valore("--ora", adesso.strftime("%H%M")))
    fuori = mancanti(valore("--radice", pathlib.Path(__file__).resolve().parents[2]), oggi, ora)
    if not fuori:
        print("stato=ok")
        return 0
    print("stato=manca:" + ";".join(f"{g}({','.join(m)})" for g, m in fuori))
    for g, m in fuori:
        print(f"- {g}: non risulta su {' e '.join(m)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
