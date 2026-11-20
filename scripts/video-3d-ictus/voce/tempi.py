# tempi.py — mette in fila le 16 frasi di Damien (voce/voce.json di voce.py scegli) con le pause per le animazioni e
# scrive sottotitoli.json (frasi lunghe divise per periodo, campo «riga») e la parte «voce» di colonna.json.
# La pagina lega ogni animazione all'inizio delle frasi e delle parole: cambiare le pause non sposta nulla di sbagliato.
# Uso (dalla cartella di lavoro con voce/voce.json): python3 tempi.py COLONNA.json SOTTOTITOLI.json
import json, re, sys
v = json.load(open('voce/voce.json'))
# pausa prima di ogni frase (s): tempo per il giro della telecamera, per leggere le schede e i pannelli
PAUSA = [1.0, 1.0, 1.1, 1.4, 1.2, 1.6, 0.9, 1.6, 1.6, 1.6, 1.6, 1.4, 1.4, 1.8, 1.6, 0.7]
assert len(v) == 16, len(v)
inizi, s = [], 0.0
for i, x in enumerate(v):
    s += PAUSA[i]; inizi.append(round(s, 2)); s += x['durata']
sub = []
for i, (s0, x) in enumerate(zip(inizi, v), 1):
    parole = [{'w': p['w'], 't0': round(s0 + p['t0'], 3), 't1': round(s0 + p['t1'], 3)} for p in x['parole']]
    testo = x['schermo']
    pezzi = [testo] if len(testo) <= 95 else [q.strip() for q in re.split(r'(?<=[.?!])\s+', testo) if q.strip()]
    pezzi = [z.strip() for q in pezzi for z in (re.split(r'(?<=:)\s+', q) if len(q) > 95 else [q]) if z.strip()]
    k = 0
    for q in pezzi:
        n = len(q.split()); pw = parole[k:k + n]; k += n
        if not pw: continue
        sub.append({'riga': i, 'inizio': pw[0]['t0'], 'fine': pw[-1]['t1'], 'testo': q, 'parole': pw})
for i, (s0, x) in enumerate(zip(inizi, v), 1):
    ultimo = [f for f in sub if f['riga'] == i][-1]; ultimo['fine'] = round(max(ultimo['fine'], s0 + x['durata'] - 0.15), 3)
json.dump(sub, open(sys.argv[2], 'w'), ensure_ascii=False, indent=0)
try: c = json.load(open(sys.argv[1]))
except FileNotFoundError: c = {}
c['voce'] = [{'file': 'voce/' + x['file'], 'inizio': s0} for s0, x in zip(inizi, v)]
c['durata'] = round(inizi[-1] + v[-1]['durata'] + 2.8, 2)
json.dump(c, open(sys.argv[1], 'w'), indent=1)
for s0, x in zip(inizi, v): print(s0, round(s0 + x['durata'], 2), x['schermo'][:60])
print('durata', c['durata'])
