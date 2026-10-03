"""Pezzi in comune agli script della rubrica: ffmpeg e scrittura prudente delle news."""
import os, sys
from pathlib import Path

def _ffmpeg():
    if os.environ.get('FF'): return os.environ['FF']
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception: return 'ffmpeg'
FF = _ffmpeg()

def scrivi(path, testo):
    """Scrive la news solo se non esiste: le news già create possono essere state ritoccate a mano
    (in_evidenza_fino, link…). Per rigenerarle davvero: --sovrascrivi."""
    path = Path(path)
    if path.exists() and '--sovrascrivi' not in sys.argv:
        print('salto (esiste già, usa --sovrascrivi):', path.name); return False
    path.write_text(testo); return True
