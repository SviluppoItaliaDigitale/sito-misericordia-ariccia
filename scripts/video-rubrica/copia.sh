#!/bin/bash
# Copia nel sito video, sottotitoli e copertina (fotogramma a 1,8 s) dei video montati; poi crea i .webp.
# La grafica della news NON viene dal video: dal 21/10/2026 si fa col modello nazionale (skill grafiche-modelli-nazionali).
cd "$(dirname "$0")"; R=$(cd ../.. && pwd)
FF=$(python3 -c "import sys; sys.path.insert(0,'.'); from comune import FF; print(FF)")
for k in "$@"; do
  n="primo-soccorso-$k"; [ -f "out/$n.mp4" ] || n="$k"
  [ -f "out/$n.mp4" ] || { echo "manca out/$n.mp4"; continue; }
  cp "out/$n.mp4" "$R/static/video/$n.mp4"
  [ -f "out/$n.vtt" ] && cp "out/$n.vtt" "$R/static/video/$n.vtt"   # sottotitoli (pipeline.py --sottotitoli)
  rm -f "$R/static/img/video/$n.webp"
  $FF -v error -y -ss 1.8 -i "out/$n.mp4" -frames:v 1 -q:v 3 "$R/static/img/video/$n.jpg"
  echo "copiato $n"
done
python3 "$R/scripts/ottimizza-immagini.py" "$R/static/img/video" | tail -1
