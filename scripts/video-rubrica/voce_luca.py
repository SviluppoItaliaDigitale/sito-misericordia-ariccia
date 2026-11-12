"""Voce «Luca» (ElevenLabs, «Luca – Warm Italian Narrator», scelta di Alessandro del 1/11/2026) per i video con voce='luca'.

La voce si genera fuori da qui, con il connettore ElevenLabs della sessione (una frase per scena, modello
eleven_multilingual_v2, voice_id 1s5ETcPtsJ9W2cUUQrDb): questo script dice quali frasi mancano e salva quelle
generate in voci-luca/<chiave>/<n>.mp3, con accanto <n>.txt, il testo esatto. pipeline.py usa solo le frasi il
cui testo coincide con quello della scena: se cambia una parola, la frase va rigenerata.

  python3 voce_luca.py elenco CHIAVE...          frasi mancanti o da rifare (numero scena e testo da far leggere)
  python3 voce_luca.py salva CHIAVE N URL         scarica l'mp3 della frase N e scrive il testo accanto
"""
import sys, urllib.request
from pathlib import Path
W = Path(__file__).resolve().parent
sys.path.insert(0, str(W))
import contenuti

VOICE_ID = '1s5ETcPtsJ9W2cUUQrDb'
MODELLO = 'eleven_multilingual_v2'
# Voci dei video a più voci (campo «voce_di» della scena; senza, parla Luca): nome, voice_id e modello. Con eleven_v4 la
# scena può avere «regia», il testo con le indicazioni di recitazione fra parentesi quadre ([softly], [elderly voice]…).
VOCI = {'luca': (VOICE_ID, MODELLO),
        'andrea': ('ERE9g4sDsfBwzFT0GvPh', 'eleven_v4'),     # «Andrea, calm and warm vlogger»: il giovane volontario
        'angelina': ('MLpDWJvrjFIdb63xbJp8', 'eleven_v4')}   # «Angelina - Storyteller»: la signora anziana
CARTELLA = W / 'voci-luca'


def testo(sc):
    """Che cosa è stato fatto leggere: per Luca il testo della scena (come sempre); per le altre voci anche chi parla
    e la regia, così una battuta va rigenerata se cambia la voce o la recitazione."""
    if not sc.get('voce_di') and not sc.get('regia'): return sc['voce'].strip()
    return f"{sc.get('voce_di', 'luca')}\n{(sc.get('regia') or sc['voce']).strip()}"


def stato(key):
    v = contenuti.V[key]; d = CARTELLA / key
    for i, sc in enumerate(v['scene']):
        mp3, txt = d / f'{i}.mp3', d / f'{i}.txt'
        ok = mp3.is_file() and txt.is_file() and txt.read_text(encoding='utf-8') == testo(sc)
        yield i, sc, ok


if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] not in ('elenco', 'salva'): sys.exit(__doc__)
    if sys.argv[1] == 'elenco':
        mancano = 0
        for key in sys.argv[2:]:
            for i, sc, ok in stato(key):
                if ok: continue
                chi = sc.get('voce_di', 'luca'); vid, mod = VOCI[chi]; mancano += 1
                print(f"{key}\t{i}\t{chi} {vid} {mod}\t{(sc.get('regia') or sc['voce']).strip()}")
        print(f'# {mancano} frasi da generare (voce, voice_id e modello accanto a ogni frase)', file=sys.stderr)
    else:
        key, i, url = sys.argv[2], int(sys.argv[3]), sys.argv[4]
        sc = contenuti.V[key]['scene'][i]
        d = CARTELLA / key; d.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=60) as r: dati = r.read()
        if dati[:3] != b'ID3' and dati[:2] not in (b'\xff\xfb', b'\xff\xf3', b'\xff\xf2'): sys.exit(f'{key} {i}: non è un mp3')
        (d / f'{i}.mp3').write_bytes(dati); (d / f'{i}.txt').write_text(testo(sc), encoding='utf-8')
        print(f'salvata {key} {i} ({len(dati)} byte)')
