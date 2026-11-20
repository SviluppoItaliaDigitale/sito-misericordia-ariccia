# Mette le frasi di Damien sulla scaletta (inizi con le pause per le animazioni) e scrive sottotitoli.json
# (frasi lunghe divise per periodo, campo «riga»), colonna.json (voce) e la durata totale.
import glob, json, os, re, sys
# tempi delle parole a schermo («112», «DAE») da quelli delle parole lette: voce.py della skill colonna-sonora
sys.path.insert(0, os.environ.get('VOCE_PY') or glob.glob('/root/.claude/skills/synced/*/colonna-sonora/scripts')[0])
from voce import tempi_schermo  # noqa: E402
v = json.load(open('voce/voce.json'))
SC = [1.0, 8.6, 13.2, 17.4, 22.0, 28.0, 31.0, 35.4, 40.6, 48.0, 51.4, 59.6, 64.8, 67.8, 74.0, 80.0, 86.5, 94.5, 102.0, 107.8, 111.0, 114.6]
GAP_MIN = 0.55
ser = json.load(open('voce-serena/voce.json'))
inizi = []
for i, x in enumerate(v):
    if i == 0: s = SC[0]
    else:
        pausa = max(GAP_MIN, SC[i] - (SC[i - 1] + ser[i - 1]['durata']))   # pausa della scaletta dopo la frase precedente
        s = inizi[-1] + max(SC[i] - SC[i - 1], v[i - 1]['durata'] + pausa)
    inizi.append(round(s, 2))
fine = inizi[-1] + v[-1]['durata']
sub = []
for i, (s, x) in enumerate(zip(inizi, v), 1):
    testo = x['schermo']
    parole = [{'w': p['w'], 't0': round(s + p['t0'], 3), 't1': round(s + p['t1'], 3)} for p in tempi_schermo(testo, x['parole'], x['durata'])]
    pezzi = [testo] if len(testo) <= 95 else [q.strip() for q in re.split(r'(?<=[.?!])\s+', testo) if q.strip()]
    pezzi = [z.strip() for q in pezzi for z in (re.split(r'(?<=:)\s+', q) if len(q) > 95 else [q]) if z.strip()]
    k = 0
    for q in pezzi:
        n = len(q.split()); pw = parole[k:k + n]; k += n
        if not pw: continue
        sub.append({'riga': i, 'inizio': pw[0]['t0'], 'fine': pw[-1]['t1'], 'testo': q, 'parole': pw})
# la fine di ogni frase è quella dell'audio, non dell'ultima parola riconosciuta (le cifre del telefono finiscono dopo)
for i, (s0, x) in enumerate(zip(inizi, v), 1):
    ultimo = [f for f in sub if f['riga'] == i][-1]; ultimo['fine'] = round(max(ultimo['fine'], s0 + x['durata'] - 0.15), 3)
json.dump(sub, open('sottotitoli.json', 'w'), ensure_ascii=False, indent=0)
c = json.load(open('colonna.json')) if len(sys.argv) < 2 else {}
c['voce'] = [{'file': 'voce/' + x['file'], 'inizio': s} for s, x in zip(inizi, v)]
c['durata'] = round(fine + 2.8, 2)
json.dump(c, open('colonna.json', 'w'), indent=1)
for s, x in zip(inizi, v): print(s, round(s + x['durata'], 2), x['schermo'][:50])
print('durata', c['durata'])
