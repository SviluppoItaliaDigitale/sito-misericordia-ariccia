# Strumenti del progetto

Registro degli strumenti creati per questo repo (vedi `.claude/rules/strumenti.md`).

| Nome | Scopo | Data | Origine |
|---|---|---|---|
| `scripts/controlla_giallo_ciano.py` + `.github/workflows/controlla-giallo-ciano.yml` | Ogni sera confronta la pagina nazionale di Giallo Ciano con la nostra: aggiunge i numeri nuovi, aggiorna i link cambiati, segnala con una issue GitHub numeri nuovi e link rotti | 30/09/2026 | Su misura (richiesta di Alessandro), solo libreria standard Python + `gh` di GitHub Actions |
| `scripts/video-rubrica/` (generatore dei video «Primo soccorso passo passo») | Crea i video verticali della rubrica: disegni animati in canvas, voce sintetica, sottotitoli, musica originale, simulazione a tempo delle compressioni; copia video e grafiche nel sito e genera le news programmate. Guida: `scripts/video-rubrica/README.md` | 03/10/2026 | Su misura (richiesta di Alessandro). Esterni, solo invocati e non copiati nel repo: **Piper TTS** `piper-tts` 1.8.0 (pip, OHF-voice/piper1-gpl, GPL-3.0-or-later); voce **it_IT-paola-medium** (rhasspy/piper-voices su Hugging Face, modello MIT, dataset paolapersico1/Voice-Dataset-Italian); **playwright-core** 1.63.0 (npm, Microsoft, Apache-2.0) con il Chromium già presente; **imageio-ffmpeg** 0.6.0 (pip, BSD-2, binario ffmpeg LGPL/GPL); **numpy** (BSD). Versioni fissate, nessun aggiornamento automatico |
