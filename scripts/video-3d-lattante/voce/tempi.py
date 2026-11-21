# tempi.py — video 3D sul lattante: mette le 18 frasi di Damien in fila con le pause per le animazioni (DOPO, le stesse
# della pagina lattante-3d.src.html), scrive sottotitoli.json (frasi lunghe divise, campo «riga») e colonna.json (voce,
# musica, effetti negli istanti delle pacche, delle compressioni e dei soffi, calcolati come nella pagina).
# Copiato da scripts/video-3d-disostruzione/voce/tempi.py (20/11/2026).
# Uso (dalla cartella di lavoro con voce/voce.json): python3 tempi.py → sottotitoli.json, colonna.json
import json, re
v = json.load(open('voce/voce.json'))
N = 18
DOPO = [0, 1.0, 1.4, 1.0, 1.0, 0.8, 3.2, 0.9, 3.0, 1.4, 0.8, 1.8, 0.8, 3.2, 1.6, 3.6, 1.0, 1.2, 3.6]   # DOPO[15] 3,6 (21/11/2026): placca dietro tenuta e ritorno supino
assert len(v) == N, len(v)
S, E = [0] * (N + 1), [0] * (N + 1)
x = 1.0
for i in range(1, N + 1):
    S[i] = round(x, 2); E[i] = round(x + v[i - 1]['durata'], 3); x = E[i] + DOPO[i]
TOTAL = E[N] + DOPO[N]
sub = []
for i, x in enumerate(v, 1):
    s = S[i]
    lette = [{'w': p['w'], 't0': round(s + p['t0'], 3), 't1': round(s + p['t1'], 3)} for p in x['parole']]
    testo = x['schermo']
    # parole a schermo con i tempi di quelle lette: «112» dura quanto «uno uno due», «328 8105399» quanto le cifre
    norm = lambda w: re.sub(r'[^\wàèéìòù]', '', w.lower())
    import difflib
    sch = testo.split(); A = [norm(w) for w in sch]; B = [norm(p['w']) for p in lette]; parole = [None] * len(sch)
    for op, a0, a1, b0, b1 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if op == 'equal':
            for k in range(a1 - a0): parole[a0 + k] = {'w': sch[a0 + k], 't0': lette[b0 + k]['t0'], 't1': lette[b0 + k]['t1']}
        elif a1 > a0:                            # cifre e sigle: il tratto letto si divide fra le parole a schermo
            if b1 == b0: b0, b1 = max(0, b0 - 1), max(1, b0)
            peso = [max(1, sum(ch.isdigit() for ch in sch[a0 + k])) for k in range(a1 - a0)]; tot = sum(peso); acc = 0
            for k in range(a1 - a0):          # ogni cifra è una parola letta («328» = «tre due otto»)
                q0 = b0 + (b1 - b0) * acc // tot; acc += peso[k]; q1 = max(q0, b0 + (b1 - b0) * acc // tot - 1)
                parole[a0 + k] = {'w': sch[a0 + k], 't0': lette[q0]['t0'], 't1': lette[q1]['t1']}
    pezzi = [testo] if len(testo) <= 72 else [q.strip() for q in re.split(r'(?<=[.?!»])\s+', testo) if q.strip()]
    def taglia(q):                               # oltre 72 caratteri (una riga sola a schermo): prima ai due punti, poi alla virgola più centrale
        if len(q) <= 72: return [q]
        for seg in [r':\s', r',\s']:
            pos = [m.end() for m in re.finditer(seg, q)]
            if pos:
                k = min(pos, key=lambda p: abs(p - len(q) / 2))
                return taglia(q[:k].strip()) + taglia(q[k:].strip())
        return [q]
    pezzi = [z for q in pezzi for z in taglia(q)]
    k = 0
    for q in pezzi:
        n = len(q.split()); pw = parole[k:k + n]; k += n
        if not pw: continue
        sub.append({'riga': i, 'inizio': pw[0]['t0'], 'fine': pw[-1]['t1'], 'testo': q, 'parole': pw})
for i, x in enumerate(v, 1):
    ultimo = [f for f in sub if f['riga'] == i][-1]; ultimo['fine'] = round(max(ultimo['fine'], S[i] + x['durata'] - 0.15), 3)
json.dump(sub, open('sottotitoli.json', 'w'), ensure_ascii=False, indent=0)
dur = lambda i: E[i] - S[i]
PACCHE = [S[6] + min(1.0, dur(6) * 0.25) + k * 0.85 for k in range(5)]
COMPR_G = [S[8] + dur(8) * 0.45 + k * 0.8 for k in range(5)]
SOFFI = [S[11] + 0.4 + k * 1.55 for k in range(5)]
RCP_A, RCP_B, P = S[12] + min(3.4, dur(12) * 0.55), E[14] + 1.2, 60 / 110
eff = []
add = lambda f, t, g=1.0: eff.append({'file': f'sfx/{f}.wav', 'evento': round(t, 3), 'tipo': 'colpo', 'volume': round(20 * __import__('math').log10(g), 1)})
for t in PACCHE: add('colpo', t, 0.6)
for t in COMPR_G: add('soffio', t, 0.4)
for t in SOFFI: add('soffio', t, 0.35)
k = 0
while RCP_A + k * P < RCP_B: add('colpo', RCP_A + k * P + P / 2, 0.3); k += 1
for t in [S[5] - 0.5, S[7] - 0.5, S[10] - 0.5]: add('passaggio', t, 0.7)
add('chiusura', S[18] - 0.3, 0.8)
c = {'durata': round(TOTAL, 2), 'voce': [{'file': 'voce/' + x['file'], 'inizio': S[i]} for i, x in enumerate(v, 1)],
     'musica': [{'file': 'musica.mp3', 'inizio': 0, 'da': max(0.0, round(174.26 - TOTAL, 2)), 'entrata': 1.5, 'uscita': 1.5}],
     'effetti': eff}
json.dump(c, open('colonna.json', 'w'), indent=1)
for i in range(1, N + 1): print(i, S[i], E[i], v[i - 1]['schermo'][:50])
print('durata', c['durata'])
