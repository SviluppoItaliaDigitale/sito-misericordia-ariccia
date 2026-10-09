#!/bin/bash
# Copia nel sito video, copertina (fotogramma a 1,8 s) e grafica 1080x1350 dei video montati; poi crea i .webp.
cd "$(dirname "$0")"; R=$(cd ../.. && pwd)
FF=$(python3 -c "import sys; sys.path.insert(0,'.'); from comune import FF; print(FF)")
for k in "$@"; do
  n="primo-soccorso-$k"; [ -f "out/$n.mp4" ] || n="$k"
  [ -f "out/$n.mp4" ] || { echo "manca out/$n.mp4"; continue; }
  cp "out/$n.mp4" "$R/static/video/$n.mp4"
  [ -f "out/$n.vtt" ] && cp "out/$n.vtt" "$R/static/video/$n.vtt"   # sottotitoli (pipeline.py --sottotitoli)
  rm -f "$R/static/img/video/$n.webp" "$R/static/img/news/$n-grafica.webp"
  $FF -v error -y -ss 1.8 -i "out/$n.mp4" -frames:v 1 -q:v 3 "$R/static/img/video/$n.jpg"
  $FF -v error -y -ss 1.8 -i "out/$n.mp4" -frames:v 1 -vf "crop=1080:1350:0:10" -q:v 3 "$R/static/img/news/$n-grafica.jpg"
  echo "copiato $n"
done
python3 "$R/scripts/ottimizza-immagini.py" "$R/static/img/video" | tail -1
python3 "$R/scripts/ottimizza-immagini.py" "$R/static/img/news" | tail -1
