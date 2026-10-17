#!/usr/bin/env python3
"""Prova d'impaginazione senza voce: per ogni scena un fotogramma intero (1080x1920) con la
zona che Instagram copre con i suoi comandi, per controllare titoli, etichette e sottotitoli
prima del montaggio. Tempi stimati dalla lunghezza dei testi, audio muto.
Uso: python3 prova_impaginazione.py chiave [...]  ->  out/<chiave>/prova.png"""
import base64, json, os, subprocess, sys
from pathlib import Path
import contenuti
W = Path(__file__).resolve().parent; REPO = W.parents[1]; OUT = W / 'out'; F = REPO / 'static' / 'fonts'
b64 = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
sys.path.insert(0, str(W)); from comune import FF
ORD = ['ictus','infarto','emorragia','rianimazione','soffocamento','anafilassi','ustioni','ipoglicemia','avvelenamento','trauma-cranico']
for key in sys.argv[1:]:
    v = dict(contenuti.V[key]); v.setdefault('num', ORD.index(key) + 1 if key in ORD else 0)
    d = OUT / key; d.mkdir(parents=True, exist_ok=True)
    D = [round(max(2.5, len(sc['voce']) / 14), 3) for sc in v['scene']]
    conta = {}
    for k, sc in enumerate(v['scene']):
        if sc.get('conta'):
            conta = dict(voce=D[k], at=D[k] + 0.8, beat=60 / v.get('bpm', 110), n=sc['conta'])
            D[k] = round(conta['at'] + sc['conta'] * conta['beat'] + 0.6, 3)
    T = sum(0.3 + x + 0.45 for x in D) + 2.5
    muto = d / 'muto.mp3'
    subprocess.run([FF, '-v', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', f'{T:.2f}', '-b:a', '32k', str(muto)], check=True)
    s = (W / 'appro.src.html').read_text()
    fonts = (f"@font-face{{font-family:'Playfair Display';font-weight:600;src:url(data:font/woff2;base64,{b64(F/'playfair-600-latin.woff2')}) format('woff2')}}"
             f"@font-face{{font-family:'Jost';font-weight:100 900;src:url(data:font/woff2;base64,{b64(F/'jost-latin.woff2')}) format('woff2')}}")
    s = s.replace('/*FONTS*/', fonts).replace('/*LOGO*/', 'data:image/png;base64,' + b64(REPO / 'static' / 'img' / 'loghi' / 'mise-triangolo.png'))
    s = s.replace('/*ILL*/', '\n'.join((W / f).read_text() for f in ('ill.js', 'ill2.js', 'ill3.js')))
    s = s.replace('/*DUR*/[]', json.dumps(D)).replace('/*CONTA*/{}', json.dumps(conta)).replace('/*CFG*/{}', json.dumps(v, ensure_ascii=False))
    s = s.replace('src="/*AUDIO*/"', 'src="data:audio/mpeg;base64,' + b64(muto) + '"')
    (d / 'video.html').write_text(s)
    env = {**os.environ, 'KEY': key, 'PATH': '/opt/node22/bin:' + os.environ.get('PATH', '/usr/bin:/bin')}
    (d / 'prova.png').unlink(missing_ok=True)  # mai guardare per sbaglio la prova di un giro precedente
    r = subprocess.run(['node', str(W / 'prova_impaginazione.js')], cwd=OUT, env=env, capture_output=True, text=True)
    print(r.stdout[-1500:], r.stderr[-1500:], flush=True)
    if r.returncode or not (d / 'prova.png').exists():
        sys.exit(f'{key}: prova non riuscita (codice {r.returncode})')
