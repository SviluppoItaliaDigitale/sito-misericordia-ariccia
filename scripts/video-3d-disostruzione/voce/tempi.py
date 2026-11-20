# tempi.py — mette le 20 frasi di Damien in fila con le pause per le animazioni (DOPO, le stesse della pagina),
# scrive sottotitoli.json (frasi lunghe divise per periodo, campo «riga») e colonna.json (voce, musica, effetti
# negli istanti dei colpi, delle spinte, della tosse e delle compressioni, calcolati come nella pagina).
# Uso (dalla cartella di lavoro con voce/voce.json): python3 tempi.py → sottotitoli.json, colonna.json
import json, re
v = json.load(open('voce/voce.json'))
N = 20
DOPO = [0, 1.2, 1.2, 1.6, 0.8, 1.6, 0.8, 3.6, 3.4, 1.0, 2.6, 2.6, 0.8, 1.2, 1.2, 0.8, 2.6, 2.6, 1.2, 4.6, 3.0]
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
    pezzi = [testo] if len(testo) <= 95 else [q.strip() for q in re.split(r'(?<=[.?!»])\s+', testo) if q.strip()]
    def taglia(q):                               # oltre 95 caratteri: prima ai due punti, poi alla virgola più centrale
        if len(q) <= 95: return [q]
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
COLPI = [S[7] + min(1.6, dur(7) * 0.35) + k * 0.78 for k in range(5)]
SPINTE = [max(S[8] + dur(8) * 0.62, E[8] - 2.4) + k * 0.82 for k in range(5)]
SPINTE_LENTE = [S[9] + 0.9, S[9] + 2.9]
ALT_C = [S[10] + 0.4 + k * 0.62 for k in range(3)]; ALT_S = [S[10] + 2.4 + k * 0.62 for k in range(3)]
T_ESCE = min(E[10] + 1.4, S[11] - 1.0)
RCP_A, RCP_B, P = S[11] + 2.6, E[11] + 2.2, 60 / 110
TOSSI = [S[5] + 0.6, S[5] + 1.5, S[5] + 2.4, E[5] + 0.3]
PACCHE = [S[16] + min(1.4, dur(16) * 0.25) + k * 0.8 for k in range(5)]
POLLICI = [S[17] + min(1.4, dur(17) * 0.3) + k * 0.75 for k in range(5)]
eff = []
add = lambda f, t, g=1.0: eff.append({'file': f'sfx/{f}.wav', 'evento': round(t, 3), 'tipo': 'colpo', 'volume': round(20 * __import__('math').log10(g), 1)})
for t in COLPI + ALT_C: add('colpo', t)
for t in PACCHE: add('colpo', t, 0.6)
for t in SPINTE + ALT_S + SPINTE_LENTE + TOSSI: add('soffio', t, 0.8)
for t in POLLICI: add('soffio', t, 0.4)
add('soffio', T_ESCE - 0.3, 1.0)
k = 0
while RCP_A + k * P < RCP_B: add('colpo', RCP_A + k * P + P / 2, 0.35); k += 1
for t in [S[3] - 0.3, S[7] - 0.3, S[11] - 0.3, S[14] - 0.3]: add('passaggio', t, 0.7)
add('chiusura', S[20] - 0.3, 0.8)
c = {'durata': round(TOTAL, 2), 'voce': [{'file': 'voce/' + x['file'], 'inizio': S[i]} for i, x in enumerate(v, 1)],
     'musica': [{'file': 'musica.mp3', 'inizio': 0, 'da': max(0.0, round(174.26 - TOTAL, 2)), 'entrata': 1.5, 'uscita': 1.5}],
     'effetti': eff}
json.dump(c, open('colonna.json', 'w'), indent=1)
for i in range(1, N + 1): print(i, S[i], E[i], v[i - 1]['schermo'][:50])
print('durata', c['durata'])
