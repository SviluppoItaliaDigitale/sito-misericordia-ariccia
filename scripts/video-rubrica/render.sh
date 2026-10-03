#!/bin/bash
# Montaggio completo di uno o più video, 3 alla volta: out/primo-soccorso-<chiave>.mp4 (speciali: out/<chiave>.mp4)
cd "$(dirname "$0")"; mkdir -p out
printf '%s\n' "$@" | xargs -P 3 -I{} sh -c 'python3 pipeline.py {} > out/rlog-{}.txt 2>&1; tail -1 out/rlog-{}.txt'
