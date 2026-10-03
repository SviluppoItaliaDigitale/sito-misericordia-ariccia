#!/usr/bin/env python3
"""Generatore dei video «Primo soccorso passo passo»: voce (Piper) -> tempi -> HTML animato
-> fotogrammi (Chromium) -> musica originale -> MP4 1080x1920. Guida: README.md.
Uso: pipeline.py chiave [...] [--anteprima]  (--anteprima: solo un foglio di fotogrammi chiave in out/<chiave>/foglio.png)"""
import base64, json, os, re, subprocess, sys, wave
from pathlib import Path
import numpy as np
import contenuti
W = Path(__file__).resolve().parent; REPO = W.parents[1]; OUT = W / 'out'
sys.path.insert(0, str(W)); from comune import FF
MODEL = os.environ.get('PIPER_MODEL', str(W / 'voce' / 'it_IT-paola-medium.onnx'))
F = REPO / 'static' / 'fonts'
ORD = ['ictus','infarto','emorragia','rianimazione','soffocamento','anafilassi','ustioni','ipoglicemia','avvelenamento','trauma-cranico']
NUM = 'uno due tre quattro cinque sei sette otto nove dieci undici dodici tredici quattordici quindici sedici diciassette diciotto diciannove venti ventuno ventidue ventitré ventiquattro venticinque ventisei ventisette ventotto ventinove trenta'.split()
b64 = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
SR = 22050
# Parole che la voce legge con l'accento sbagliato: si correggono solo nell'audio, i sottotitoli restano giusti.
PRONUNCIA = {'Iddio': 'Iddìo'}
def pron(text):
    for k, v in PRONUNCIA.items(): text = text.replace(k, v)
    return text
def piper(text, out, ls=1.0, sil=0.25):
    text = pron(text)
    subprocess.run(['python3','-m','piper','-m',MODEL,'--length-scale',str(ls),'--sentence-silence',str(sil),'-f',str(out)], input=text, text=True, capture_output=True, check=True)
def rd(p):
    w = wave.open(str(p)); assert w.getframerate() == SR
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def trim(a, th=0.02):
    i = np.where(np.abs(a) > th)[0]
    return a[max(0, i[0]-200): i[-1]+400] if len(i) else a
def numero(i):  # numero pronunciato, sotto 0,42 s
    (OUT / 'num').mkdir(parents=True, exist_ok=True)
    p = OUT / 'num' / f'c{i}.wav'
    if not p.exists():
        ls = 0.75
        for _ in range(4):
            piper(NUM[i-1], p, ls); a = trim(rd(p)); L = len(a) / SR
            if L <= 0.44: break
            ls *= 0.42 / L
    return trim(rd(p))
ANTE = '--anteprima' in sys.argv
if not Path(MODEL).exists():
    sys.exit(f'Manca la voce Piper: {MODEL}\nScaricala come spiegato in README.md (it_IT-paola-medium.onnx e .onnx.json).')
for key in [a for a in sys.argv[1:] if not a.startswith('--')]:
    v = dict(contenuti.V[key]); v.setdefault('num', ORD.index(key) + 1 if key in ORD else 0)
    d = OUT / key; d.mkdir(parents=True, exist_ok=True)
    bpm = v.get('bpm', 88); beat = 60 / bpm
    PRE, POST, CODA = 0.3, 0.45, 2.5
    voci, D, conta = [], [], {}
    acc = 0.0
    for i, sc in enumerate(v['scene']):
        wav = d / f'v{i}.wav'
        tf = d / f'v{i}.txt'
        if not wav.exists() or not tf.exists() or tf.read_text() != pron(sc['voce']):
            piper(sc['voce'], wav, v.get('voce_lenta', 1.0), 0.6 if v.get('voce_lenta') else 0.25); tf.write_text(pron(sc['voce']))
        a = rd(wav); Dv = len(a) / SR
        if sc.get('conta'):
            n = sc['conta']; b = 60 / bpm
            t_abs = acc + PRE + Dv + 0.5
            t_abs = np.ceil(t_abs / b) * b          # primo battito allineato alla griglia della musica
            at = t_abs - acc                         # rispetto all'inizio scena
            Dk = at - PRE + (n - 1) * b + 0.6
            conta = dict(voce=round(Dv, 3), at=round(at, 3), beat=b, n=n)
            seg = np.zeros(int(Dk * SR) + SR)
            seg[:len(a)] += a
            click = np.sin(2*np.pi*1900*np.arange(int(.03*SR))/SR) * np.exp(-np.arange(int(.03*SR))/SR*160) * .25
            for k in range(n):
                s = int((at - PRE + k * b) * SR)
                nm = numero(k + 1); seg[s:s+len(nm)] += nm * .95
                seg[s:s+len(click)] += click
            voci.append(seg[:int(Dk * SR)]); D.append(round(Dk, 3))
        else:
            voci.append(a); D.append(round(Dv, 3))
        acc += PRE + D[-1] + POST + (CODA if i == len(v['scene']) - 1 else 0)
    T = round(acc, 2)
    track = np.zeros(int(T * SR) + SR); t = 0.0
    for i, a in enumerate(voci):
        s = int((t + PRE) * SR); track[s:s+len(a)] += a
        t += PRE + D[i] + POST + (CODA if i == len(voci) - 1 else 0)
    track = np.clip(track[:int(T * SR)], -1, 1)
    with wave.open(str(d / 'voce.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((track * 32767).astype(np.int16).tobytes())
    subprocess.run(['python3', str(W / 'musica.py'), str(T), str(d / 'musica.wav'), str(bpm), v.get('musica', 'base')], check=True, capture_output=True)
    subprocess.run([FF,'-v','error','-y','-i',str(d/'voce.wav'),'-i',str(d/'musica.wav'),'-filter_complex',
        '[0]aresample=44100,asplit[v][vs];[1]volume=0.30[m];[m][vs]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];[v][md]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5[o]',
        '-map','[o]','-ar','44100','-ac','1','-b:a','128k',str(d/'audio.mp3')],check=True)
    s = (W/'appro.src.html').read_text()
    fonts = (f"@font-face{{font-family:'Playfair Display';font-weight:600;src:url(data:font/woff2;base64,{b64(F/'playfair-600-latin.woff2')}) format('woff2')}}"
             f"@font-face{{font-family:'Jost';font-weight:100 900;src:url(data:font/woff2;base64,{b64(F/'jost-latin.woff2')}) format('woff2')}}")
    s = s.replace('/*FONTS*/', fonts).replace('/*LOGO*/','data:image/png;base64,'+b64(REPO / 'static' / 'img' / 'loghi' / 'mise-triangolo.png'))
    s = s.replace('/*ILL*/', (W/'ill.js').read_text() + '\n' + (W/'ill2.js').read_text() + '\n' + (W/'ill3.js').read_text())
    s = s.replace('/*DUR*/[]', json.dumps(D)).replace('/*CONTA*/{}', json.dumps(conta)).replace('/*CFG*/{}', json.dumps(v, ensure_ascii=False))
    s = s.replace('src="/*AUDIO*/"', 'src="data:audio/mpeg;base64,'+b64(d/'audio.mp3')+'"')
    (d/'video.html').write_text(s)
    env = {**os.environ, 'FF': FF, 'KEY': key, 'PATH': '/opt/node22/bin:' + os.environ.get('PATH', '/usr/bin:/bin')}
    if ANTE:
        r = subprocess.run(['node',str(W/'anteprima.js')],cwd=OUT,env=env,capture_output=True,text=True)
        print(r.stdout[-2000:], r.stderr[-2000:], flush=True); print('ANTEPRIMA', key, T, flush=True); continue
    r = subprocess.run(['node',str(W/'frames.js')],cwd=OUT,env=env,capture_output=True,text=True)
    if r.returncode: print(r.stderr[-3000:]); sys.exit(1)
    out = OUT / (f'primo-soccorso-{key}.mp4' if v['num'] else f'{key}.mp4')
    subprocess.run([FF,'-v','error','-y','-i',str(d/'frames.mp4'),'-i',str(d/'audio.mp3'),'-c:v','copy','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    print('FATTO', key, T, 's', out, flush=True)
