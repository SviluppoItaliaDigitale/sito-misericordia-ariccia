#!/usr/bin/env bash
# costruisci.sh — costruisce la pagina del video 3D sulla disostruzione: mette nella sorgente il motore della cornice di
# microtesto (scripts/grafica-brand/firma-e-cornice.js) e lo stemma nazionale, poi chiama costruisci.py della skill video-3d
# con l'anatomia (anatomia_disostruzione.py) e i sottotitoli a tempo (voce.py tempi della skill colonna-sonora).
# Uso: bash costruisci.sh ANATOMIA.json SOTTOTITOLI.json USCITA.html
set -euo pipefail
QUI="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$QUI/../.." && pwd)"
SKILL="${SKILL_VIDEO3D:-$(ls -d /root/.claude/skills/synced/*/video-3d 2>/dev/null | head -1)}"
[ -d "$SKILL" ] || { echo "Errore: non trovo la skill video-3d (imposta SKILL_VIDEO3D)"; exit 1; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
python3 - "$QUI/disostruzione-3d.src.html" "$REPO" "$TMP/disostruzione-3d.src.html" <<'PY'
import base64, sys, pathlib
src, repo, out = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
s = pathlib.Path(src).read_text()
s = s.replace('/*CORNICE*/', (repo / 'scripts/grafica-brand/firma-e-cornice.js').read_text())
stemma = repo / 'scripts/grafica-brand/modelli-nazionali/loghi/stemma-misericordie.png'
s = s.replace('/*STEMMA*/', 'data:image/png;base64,' + base64.b64encode(stemma.read_bytes()).decode())
pathlib.Path(out).write_text(s)
PY
python3 "$SKILL/scripts/costruisci.py" "$TMP/disostruzione-3d.src.html" --uscita "$3" --ente misericordia \
  --dato anatomia="$1" --dato sottotitoli="$2"
