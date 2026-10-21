#!/bin/bash
# Copia nel sito video, copertina (fotogramma a 1,8 s) e grafica 1080x1350 senza sottotitolo (grafica.js) dei video montati; poi crea i .webp.
cd "$(dirname "$0")"; R=$(cd ../.. && pwd)
ERR=0
FF=$(python3 -c "import sys; sys.path.insert(0,'.'); from comune import FF; print(FF)")
for k in "$@"; do
  n="primo-soccorso-$k"; [ -f "out/$n.mp4" ] || n="$k"
  [ -f "out/$n.mp4" ] || { echo "manca out/$n.mp4"; continue; }
  cp "out/$n.mp4" "$R/static/video/$n.mp4"
  [ -f "out/$n.vtt" ] && cp "out/$n.vtt" "$R/static/video/$n.vtt"   # sottotitoli (pipeline.py --sottotitoli)
  rm -f "$R/static/img/video/$n.webp"
  $FF -v error -y -ss 1.8 -i "out/$n.mp4" -frames:v 1 -q:v 3 "$R/static/img/video/$n.jpg"
  # grafica: stesso fotogramma ma senza sottotitolo (grafica.js), altrimenti la striscia finisce tagliata in fondo
  if [ -f "out/$k/video.html" ] && (cd out && KEY="$k" PATH="/opt/node22/bin:$PATH" node ../grafica.js); then
    rm -f "$R/static/img/news/$n-grafica.webp"
    $FF -v error -y -i "out/$k/grafica.png" -vf "crop=1080:1350:0:10" -q:v 3 "$R/static/img/news/$n-grafica.jpg"
    # firma «Misericordia di Ariccia» in basso, allineata al titolo, e cornice di microtesto (regola del 21/10/2026)
    python3 "$R/.claude/skills/grafiche-modelli-nazionali/rendi.py" --cornice "$R/static/img/news/$n-grafica.jpg" \
      --firma basso-sinistra --firma-carattere Jost --firma-margine 96 --firma-basso 80 --firma-corpo 34 --firma-colore '#FFFFFF' \
      || { echo "ERRORE: firma e cornice non messe sulla grafica di $n"; ERR=1; }
  else echo "ERRORE: grafica di $n non rifatta (manca out/$k/video.html o errore): resta quella di prima"; ERR=1; fi
  echo "copiato $n"
done
python3 "$R/scripts/ottimizza-immagini.py" "$R/static/img/video" | tail -1
python3 "$R/scripts/ottimizza-immagini.py" "$R/static/img/news" | tail -1
exit $ERR   # grafica non rifatta: uscita con errore, così non passa inosservata
