# tempi.py — mette in fila le 16 frasi di Damien (voce/voce.json di voce.py scegli) con le pause che servono alle
# animazioni e alla lettura delle schede, e scrive sottotitoli.json (frasi lunghe divise per periodo, campo «riga»),
# la parte «voce» di colonna.json e la durata totale. La pagina lega le scene all'inizio di ogni frase.
# Uso (dalla cartella di lavoro con voce/voce.json): python3 tempi.py COLONNA.json SOTTOTITOLI.json
import glob, json, os, re, sys
# tempi delle parole a schermo («112») da quelli delle parole lette («uno uno due»): voce.py della skill colonna-sonora
sys.path.insert(0, os.environ.get('VOCE_PY') or glob.glob('/root/.claude/skills/synced/*/colonna-sonora/scripts')[0])
from voce import tempi_schermo  # noqa: E402
v = json.load(open('voce/voce.json'))
assert len(v) == 16, 'servono 16 frasi'
# pausa dopo ogni frase (s): tempo per il tuffo nella coronaria, il coagulo, la lettura delle schede delle azioni
PAUSA = [1.3, 1.6, 0.9, 1.7, 0.8, 1.2, 0.7, 1.0, 1.0, 1.5, 1.5, 1.5, 1.6, 1.2, 1.4, 0]
inizi, s = [], 1.0
for x, p in zip(v, PAUSA):
    inizi.append(round(s, 2)); s += x['durata'] + p
fine = inizi[-1] + v[-1]['durata']
sub = []
for i, (s0, x) in enumerate(zip(inizi, v), 1):
    testo = x['schermo']
    parole = [{'w': p['w'], 't0': round(s0 + p['t0'], 3), 't1': round(s0 + p['t1'], 3)} for p in tempi_schermo(testo, x['parole'], x['durata'])]
    pezzi = [testo] if len(testo) <= 95 else [q.strip() for q in re.split(r'(?<=[.?!])\s+', testo) if q.strip()]
    pezzi = [z.strip() for q in pezzi for z in (re.split(r'(?<=:)\s+', q) if len(q) > 95 else [q]) if z.strip()]
    pezzi = [z.strip() for q in pezzi for z in (re.split(r'(?<=,)\s+(?=anche|oppure|spesso)', q) if len(q) > 95 else [q]) if z.strip()]
    k = 0
    for q in pezzi:
        n = len(q.split()); pw = parole[k:k + n]; k += n
        if not pw: continue
        sub.append({'riga': i, 'inizio': pw[0]['t0'], 'fine': pw[-1]['t1'], 'testo': q, 'parole': pw})
    assert k == len(parole), f'frase {i}: parole a schermo {k} contro {len(parole)}'
for i, (s0, x) in enumerate(zip(inizi, v), 1):
    ultimo = [f for f in sub if f['riga'] == i][-1]; ultimo['fine'] = round(max(ultimo['fine'], s0 + x['durata'] - 0.15), 3)
json.dump(sub, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
try: c = json.load(open(sys.argv[1]))
except FileNotFoundError: c = {}
c['voce'] = [{'file': 'voce/' + x['file'], 'inizio': s0} for s0, x in zip(inizi, v)]
c['durata'] = round(fine + 2.8, 2)
json.dump(c, open(sys.argv[1], 'w'), indent=1)
for s0, x in zip(inizi, v): print(s0, round(s0 + x['durata'], 2), x['schermo'][:60])
print('durata', c['durata'])
