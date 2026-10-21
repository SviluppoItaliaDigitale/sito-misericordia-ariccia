"""Pezzi in comune agli script della rubrica: ffmpeg, pagina animata dei video e scrittura prudente delle news."""
import base64, json, os, re, sys
from pathlib import Path

W = Path(__file__).resolve().parent; REPO = W.parents[1]
MODELLI = REPO / 'scripts' / 'grafica-brand' / 'modelli-nazionali'   # caratteri e loghi dei modelli nazionali
MOTORE = REPO / 'scripts' / 'grafica-brand' / 'firma-e-cornice.js'  # firma e cornice di microtesto

def _ffmpeg():
    if os.environ.get('FF'): return os.environ['FF']
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception: return 'ffmpeg'
FF = _ffmpeg()

b64 = lambda p: base64.b64encode(Path(p).read_bytes()).decode()

# Montserrat dei modelli nazionali (latino ed esteso, come in modelli-nazionali/base.css); Playfair e Jost restano
# per le scritte dentro i disegni, che non cambiano.
_LATINO = ('U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, '
           'U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD')
_ESTESO = ('U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, '
           'U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF')

def caratteri():
    F = REPO / 'static' / 'fonts'
    return (f"@font-face{{font-family:'Playfair Display';font-weight:600;src:url(data:font/woff2;base64,{b64(F/'playfair-600-latin.woff2')}) format('woff2')}}"
            f"@font-face{{font-family:'Jost';font-weight:100 900;src:url(data:font/woff2;base64,{b64(F/'jost-latin.woff2')}) format('woff2')}}"
            f"@font-face{{font-family:'Montserrat';font-weight:100 900;font-display:block;src:url(data:font/woff2;base64,{b64(MODELLI/'font'/'montserrat-latin-ext.woff2')}) format('woff2');unicode-range:{_ESTESO}}}"
            f"@font-face{{font-family:'Montserrat';font-weight:100 900;font-display:block;src:url(data:font/woff2;base64,{b64(MODELLI/'font'/'montserrat-latin.woff2')}) format('woff2');unicode-range:{_LATINO}}}")

def disegni():
    """File dei disegni: ill.js per primo (definisce ILL e le funzioni che usano gli altri), poi ill2.js, ill3.js…
    in ordine di numero. Un illN.js nuovo entra da solo nella pagina, senza registrarlo da nessuna parte."""
    trovati = sorted((int(m.group(1) or 0), f.name) for f in W.glob('ill*.js') if (m := re.fullmatch(r'ill(\d*)\.js', f.name)))
    nomi = [n for _, n in trovati]
    if not nomi or nomi[0] != 'ill.js':
        sys.exit(f'manca ill.js, che definisce ILL: trovati {nomi}')
    return nomi

def pagina(v, D, conta, audio):
    """Pagina animata di un video (appro.src.html) con caratteri, loghi ufficiali dei modelli nazionali, motore di
    firma e cornice, disegni, tempi (D, conta) e dati del video (v). audio: indirizzo dell'audio (data:… o file)."""
    s = (W / 'appro.src.html').read_text()
    s = s.replace('/*FONTS*/', caratteri())
    s = s.replace('/*LOGO*/', 'data:image/png;base64,' + b64(MODELLI / 'loghi' / 'triangolo-misericordie.png'))
    s = s.replace('/*STEMMA*/', 'data:image/png;base64,' + b64(MODELLI / 'loghi' / 'stemma-misericordie.png'))
    s = s.replace('/*CORNICE*/', MOTORE.read_text())
    s = s.replace('/*ILL*/', '\n'.join((W / f).read_text() for f in disegni()))
    s = s.replace('/*DUR*/[]', json.dumps(D)).replace('/*CONTA*/{}', json.dumps(conta)).replace('/*CFG*/{}', json.dumps(v, ensure_ascii=False))
    return s.replace('src="/*AUDIO*/"', f'src="{audio}"')

def scrivi(path, testo):
    """Scrive la news solo se non esiste: le news già create possono essere state ritoccate a mano
    (in_evidenza_fino, link…). Per rigenerarle davvero: --sovrascrivi."""
    path = Path(path)
    if path.exists() and '--sovrascrivi' not in sys.argv:
        print('salto (esiste già, usa --sovrascrivi):', path.name); return False
    path.write_text(testo); return True
