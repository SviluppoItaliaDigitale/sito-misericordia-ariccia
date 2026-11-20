# rimappa_effetti.py: porta effetti, suoni delle compressioni e attacco della musica dai tempi della prima versione
# (voce-vecchia/) a quelli nuovi, con la stessa regola della pagina (scaletta fissa, tratti lineari fra le frasi).
import json, wave, numpy as np, os
P = 60 / 110
SC = [0, 1.0, 8.6, 13.2, 17.4, 22.0, 28.0, 31.0, 35.4, 40.6, 48.0, 51.4, 59.6, 64.8, 67.8, 74.0, 80.0, 86.5, 94.5, 102.0, 107.8, 111.0, 114.6, 124.5]
RCP = [[52.4, 74.6], [77.4, 81.6], [84.2, 108.0]]
def veri(fn):
    s = json.load(open(fn)); R = {}
    for x in s: R.setdefault(x['riga'], [x['inizio'], x['fine']]); R[x['riga']][1] = x['fine']
    r = [R[i] for i in sorted(R)]; return [0] + [a for a, b in r] + [r[-1][1] + 2.8]
def interp(x, xs, ys):
    if x <= xs[0]: return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]: return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1])
    return ys[-1] + (x - xs[-1])
O = veri('voce-vecchia/sottotitoli.json'); N = veri('sottotitoli.json')
c = json.load(open('colonna.json')); orig = json.load(open('voce-vecchia/colonna.json'))
c['effetti'] = json.loads(json.dumps(orig['effetti']))
for k, e in enumerate([e for e in c['effetti'] if e['tipo'] == 'ambiente']):
    a, b = [round(interp(x, SC, N), 3) for x in RCP[k]]
    nome = os.path.basename(e['file'])
    w = wave.open('sfx-vecchi/' + nome); sr = w.getframerate(); ch = w.getnchannels(); sw = w.getsampwidth()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch); w.close()
    L = len(x) / sr; k2 = 0
    while L + k2 * P < b - a: k2 += 1
    if k2:
        X = int(round((L / 2) // P * P * sr)); x = np.concatenate([x[:X], x[X - int(round(k2 * P * sr)):X], x[X:]])
    o = wave.open(e['file'], 'wb'); o.setnchannels(ch); o.setsampwidth(sw); o.setframerate(sr); o.writeframes(x.tobytes()); o.close()
    e['inizio'], e['fine'] = a, b
    print(nome, round(L, 3), '->', round(len(x) / sr, 3), 'tratto', a, b)
for e in c['effetti']:
    if 'evento' in e: e['evento'] = round(interp(interp(e['evento'], O, SC), SC, N), 2)
c['musica'] = json.loads(json.dumps(orig['musica'])); c['musica'][0]['da'] = round(orig['musica'][0]['da'] - (N[-1] - O[-1]), 2)
json.dump(c, open('colonna.json', 'w'), indent=1)
print([ (os.path.basename(e['file']), e.get('evento')) for e in c['effetti'] if 'evento' in e], c['musica'], 'totale', N[-1])
