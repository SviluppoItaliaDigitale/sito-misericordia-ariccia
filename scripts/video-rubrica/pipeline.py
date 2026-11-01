#!/usr/bin/env python3
"""Generatore dei video «Primo soccorso passo passo»: voce (Kokoro) -> tempi -> HTML animato
-> fotogrammi (Chromium) -> musica -> MP4 1080x1920. Guida: README.md.
Uso: pipeline.py chiave [...] [--anteprima] [--sottotitoli] [--audio-da VIDEO.mp4]
  --anteprima: solo un foglio di fotogrammi chiave in out/<chiave>/foglio.png
  --sottotitoli: solo voce e tempi, poi out/<nome>.vtt con gli stessi sottotitoli che compaiono nel video
  --audio-da: rifà solo le immagini e riusa tale e quale l'audio di un video già montato (un solo video per volta);
    prima controlla che i tempi siano gli stessi: sottotitoli uguali al .vtt accanto al video e durata entro 0,2 s"""
import base64, os, re, subprocess, sys, wave
from pathlib import Path
import numpy as np
import contenuti
W = Path(__file__).resolve().parent; REPO = W.parents[1]; OUT = W / 'out'
sys.path.insert(0, str(W)); from comune import FF, pagina
MODEL = os.environ.get('PIPER_MODEL', str(W / 'voce' / 'it_IT-paola-medium.onnx'))
ORD = ['ictus','infarto','emorragia','rianimazione','soffocamento','anafilassi','ustioni','ipoglicemia','avvelenamento','trauma-cranico']
NUM = 'uno due tre quattro cinque sei sette otto nove dieci undici dodici tredici quattordici quindici sedici diciassette diciotto diciannove venti ventuno ventidue ventitré ventiquattro venticinque ventisei ventisette ventotto ventinove trenta'.split()
b64 = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
SR = 22050
# Parole che la voce legge con l'accento sbagliato: si correggono solo nell'audio, i sottotitoli restano giusti.
PRONUNCIA = {'Iddio': 'Iddìo', 'CAF': 'Caf'}
def pron(text):
    for k, v in PRONUNCIA.items(): text = text.replace(k, v)
    return text
# Voce: 'nicola' o 'sara' (Kokoro, scelte da Alessandro) oppure 'paola' (Piper). Si sceglie col campo «voce» del video.
VOCE = 'nicola'
KOKORO_PY = os.environ.get('KOKORO_PY', str(W / 'kokoro' / 'venv' / 'bin' / 'python'))
def piper(text, out, ls=1.0, sil=0.25):
    text = pron(text)
    if VOCE == 'paola':
        subprocess.run(['python3','-m','piper','-m',MODEL,'--length-scale',str(ls),'--sentence-silence',str(sil),'-f',str(out)], input=text, text=True, capture_output=True, check=True)
        return
    tmp = Path(str(out) + '.24k.wav')
    subprocess.run([KOKORO_PY, str(W / 'kokoro_voce.py'), VOCE, f'{min(2.0, max(0.5, 1 / ls)):.3f}', str(sil), str(tmp)], input=text, text=True, capture_output=True, check=True)
    subprocess.run([FF,'-v','error','-y','-i',str(tmp),'-ar',str(SR),'-ac','1',str(out)], check=True); tmp.unlink()
def rd(p):
    w = wave.open(str(p)); assert w.getframerate() == SR
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def trim(a, th=0.02):
    i = np.where(np.abs(a) > th)[0]
    return a[max(0, i[0]-200): i[-1]+400] if len(i) else a
def numero(i):  # numero pronunciato, sotto 0,42 s
    (OUT / 'num' / VOCE).mkdir(parents=True, exist_ok=True)
    p = OUT / 'num' / VOCE / f'c{i}.wav'
    if not p.exists():
        ls = 0.75
        for _ in range(4):
            piper(NUM[i-1], p, ls); a = trim(rd(p)); L = len(a) / SR
            if L <= 0.44: break
            ls *= 0.42 / L
    return trim(rd(p))
def fruscio(dur=0.55, vol=0.07):
    """Fruscio morbido di passaggio: rumore filtrato con il filtro che si apre e si richiude, generato qui (nessuna licenza)."""
    n = int(dur * SR); rng = np.random.default_rng(7); x = rng.standard_normal(n)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2; cut = 0.02 + 0.10 * np.sin(np.linspace(0, np.pi, n))
    y = np.zeros(n); acc = 0.0
    for k in range(n): acc += cut[k] * (x[k] - acc); y[k] = acc
    return y / (np.abs(y).max() or 1) * env * vol
def notifica(vol=0.10):
    """Due note brevi, come l'arrivo di un messaggio, generate qui (nessuna licenza)."""
    out = np.zeros(int(0.5 * SR))
    for t0, f in ((0.0, 1318.5), (0.11, 1760.0)):
        n = int(0.32 * SR); tt = np.arange(n) / SR
        nota = (np.sin(2*np.pi*f*tt) + 0.3*np.sin(2*np.pi*2*f*tt)) * np.exp(-tt * 11)
        s0 = int(t0 * SR); out[s0:s0+n] += nota
    return out / np.abs(out).max() * vol
ANTE = '--anteprima' in sys.argv
SUBS = '--sottotitoli' in sys.argv
AUDIO_DA = Path(sys.argv[sys.argv.index('--audio-da') + 1]).resolve() if '--audio-da' in sys.argv else None
CHIAVI = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and sys.argv[i - 1] != '--audio-da']
if AUDIO_DA and len(CHIAVI) != 1: sys.exit('--audio-da vale per un video solo')

def vtt(v, D, conta, PRE, POST, CODA):
    """Sottotitoli WebVTT con le stesse regole di appro.src.html (spezza, subAt): frase per frase,
    tempo diviso in proporzione alla lunghezza; nell'ultima scena spariscono quando compare il motto."""
    def spezza(fr):
        if len(fr) <= 88: return [fr]
        out, cur = [], ''
        for x in re.split(r'(?<=,)\s+', fr):
            if cur and len(cur + ' ' + x) > 80: out.append(cur); cur = x
            else: cur = cur + ' ' + x if cur else x
        return out + ([cur] if cur else [])
    ts = lambda s: f'{int(s//3600):02d}:{int(s%3600//60):02d}:{s%60:06.3f}'
    righe, start, n = ['WEBVTT', ''], 0.0, len(v['scene'])
    for k, sc in enumerate(v['scene']):
        sub = [y for x in re.split(r'(?<=[.?!])\s+', sc.get('sub') or sc['voce']) if x for y in spezza(x)]
        Dv = conta['voce'] if sc.get('conta') else D[k]
        tot, accw, prima = sum(map(len, sub)), 0, -0.1
        for i, frase in enumerate(sub):
            accw += len(frase)
            fine = Dv + (0.2 if k == n - 1 else 0.4) if i == len(sub) - 1 else accw / tot * Dv
            righe += [f'{ts(start + PRE + max(prima, -PRE))} --> {ts(start + PRE + fine)}', frase, '']
            prima = fine
        start += PRE + D[k] + POST + (CODA if k == n - 1 else 0)
    return '\n'.join(righe)

for key in CHIAVI:
    v = dict(contenuti.V[key]); v.setdefault('num', ORD.index(key) + 1 if key in ORD else 0)
    VOCE = v.get('voce', 'nicola')
    if VOCE == 'paola' and not Path(MODEL).exists():
        sys.exit(f'Manca la voce Piper: {MODEL}\nScaricala come spiegato in README.md (it_IT-paola-medium.onnx e .onnx.json).')
    if VOCE not in ('paola', 'luca') and not Path(KOKORO_PY).exists():
        sys.exit('Manca Kokoro: prepara kokoro/ come spiegato in README.md.')
    if VOCE == 'luca':   # voce ElevenLabs: frasi già generate in voci-luca/ (voce_luca.py), con il testo identico
        import voce_luca
        manca = [str(i) for i, sc, ok in voce_luca.stato(key) if not ok]
        if manca: sys.exit(f'{key}: mancano le frasi della voce Luca {", ".join(manca)} (python3 voce_luca.py elenco {key})')
        if any(sc.get('conta') for sc in v['scene']): sys.exit(f'{key}: la voce Luca non ha ancora i numeri del conteggio a tempo')
    d = OUT / key; d.mkdir(parents=True, exist_ok=True)
    bpm = v.get('bpm', 88); beat = 60 / bpm
    PRE, POST, CODA = 0.3, 0.45, 2.5
    voci, D, conta = [], [], {}
    acc = 0.0
    for i, sc in enumerate(v['scene']):
        wav = d / f'v{i}.wav'
        tf = d / f'v{i}.txt'
        if VOCE == 'luca':
            src = W / 'voci-luca' / key / f'{i}.mp3'
            if not wav.exists() or not tf.exists() or tf.read_text() != 'luca|' + sc['voce'].strip():
                subprocess.run([FF,'-v','error','-y','-i',str(src),'-ar',str(SR),'-ac','1',str(wav)], check=True)
                a0 = trim(rd(wav), 0.01)   # niente silenzi lunghi in testa e in coda: i tempi li danno PRE e POST
                with wave.open(str(wav), 'wb') as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a0, -1, 1) * 32767).astype(np.int16).tobytes())
                tf.write_text('luca|' + sc['voce'].strip())
        elif not wav.exists() or not tf.exists() or tf.read_text() != VOCE + '|' + pron(sc['voce']):
            piper(sc['voce'], wav, v.get('voce_lenta', 1.0), 0.6 if v.get('voce_lenta') else 0.25); tf.write_text(VOCE + '|' + pron(sc['voce']))
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
    if SUBS:
        nome = f'primo-soccorso-{key}' if v['num'] else key
        (OUT / f'{nome}.vtt').write_text(vtt(v, D, conta, PRE, POST, CODA)); print('SOTTOTITOLI', nome, T, flush=True); continue
    if AUDIO_DA:
        # Stessi tempi del video da cui si prende l'audio: sottotitoli identici e stessa durata.
        if not AUDIO_DA.is_file(): sys.exit(f'manca {AUDIO_DA}')
        vtt_vecchio = AUDIO_DA.with_suffix('.vtt')
        if not vtt_vecchio.is_file() or vtt_vecchio.read_text() != vtt(v, D, conta, PRE, POST, CODA):
            sys.exit(f'{key}: i tempi non coincidono con {vtt_vecchio.name} (sottotitoli diversi o mancanti): rimonta anche l\'audio')
        r = subprocess.run([FF, '-i', str(AUDIO_DA)], capture_output=True, text=True)
        m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r.stderr)
        durata = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else -1
        if abs(durata - T) > 0.2: sys.exit(f'{key}: {AUDIO_DA.name} dura {durata:.2f} s, i tempi calcolati {T:.2f} s')
    track = np.zeros(int(T * SR) + SR); t = 0.0
    for i, a in enumerate(voci):
        s = int((t + PRE) * SR); track[s:s+len(a)] += a
        t += PRE + D[i] + POST + (CODA if i == len(voci) - 1 else 0)
    if v.get('effetti'):   # effetti sonori leggeri (Alessandro, 1/11/2026): fruscio ai cambi di scena, notifica sul WhatsApp
        t = 0.0
        for i, sc in enumerate(v['scene']):
            if i: s0 = int((t - 0.22) * SR); fx = fruscio(); track[s0:s0+len(fx)] += fx
            if sc['ill'] == 'prenota': s0 = int((t + PRE + 0.15) * SR); fx = notifica(); track[s0:s0+len(fx)] += fx
            t += PRE + D[i] + POST + (CODA if i == len(v['scene']) - 1 else 0)
    track = np.clip(track[:int(T * SR)], -1, 1)
    with wave.open(str(d / 'voce.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((track * 32767).astype(np.int16).tobytes())
    # Musica: un brano scelto da Alessandro (cartella musica/, Kevin MacLeod, CC BY 4.0) oppure, per i video con le
    # compressioni a tempo (bpm 110), la base originale generata da musica.py, che deve restare a tempo con il conteggio.
    brano = v.get('brano', None if bpm == 110 else 'heartwarming')
    if brano:
        subprocess.run([FF,'-v','error','-y','-stream_loop','-1','-i',str(W/'musica'/f'{brano}.mp3'),'-t',f'{T:.3f}','-af',
            f'loudnorm=I=-17:TP=-2,afade=t=in:d=0.5,afade=t=out:st={max(0,T-3):.3f}:d=3','-ar','44100','-ac','1',str(d/'musica.wav')],check=True)
    else:
        subprocess.run(['python3', str(W / 'musica.py'), str(T), str(d / 'musica.wav'), str(bpm), v.get('musica', 'base')], check=True, capture_output=True)
    subprocess.run([FF,'-v','error','-y','-i',str(d/'voce.wav'),'-i',str(d/'musica.wav'),'-filter_complex',
        '[0]aresample=44100,asplit[v][vs];[1]volume=0.30[m];[m][vs]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];[v][md]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5[o]',
        '-map','[o]','-ar','44100','-ac','1','-b:a','128k',str(d/'audio.mp3')],check=True)
    (d/'video.html').write_text(pagina(v, D, conta, 'data:audio/mpeg;base64,' + b64(d/'audio.mp3')))
    env = {**os.environ, 'FF': FF, 'KEY': key, 'PATH': '/opt/node22/bin:' + os.environ.get('PATH', '/usr/bin:/bin')}
    if ANTE:
        r = subprocess.run(['node',str(W/'anteprima.js')],cwd=OUT,env=env,capture_output=True,text=True)
        print(r.stdout[-2000:], r.stderr[-2000:], flush=True); print('ANTEPRIMA', key, T, flush=True); continue
    r = subprocess.run(['node',str(W/'frames.js')],cwd=OUT,env=env,capture_output=True,text=True)
    if r.returncode: print(r.stderr[-3000:]); sys.exit(1)
    out = OUT / (f'primo-soccorso-{key}.mp4' if v['num'] else f'{key}.mp4')
    if AUDIO_DA:   # audio del video già montato, copiato com'è (nessuna nuova codifica)
        subprocess.run([FF,'-v','error','-y','-i',str(d/'frames.mp4'),'-i',str(AUDIO_DA),'-map','0:v','-map','1:a','-c','copy','-shortest','-movflags','+faststart',str(out)],check=True)
    else:
        subprocess.run([FF,'-v','error','-y','-i',str(d/'frames.mp4'),'-i',str(d/'audio.mp3'),'-c:v','copy','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out)],check=True)
    print('FATTO', key, T, 's', out, flush=True)
