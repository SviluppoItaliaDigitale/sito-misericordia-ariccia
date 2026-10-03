#!/bin/bash
# Fogli di anteprima (un fotogramma per scena) di uno o più video, 3 alla volta: out/<chiave>/foglio.png
cd "$(dirname "$0")"; mkdir -p out
printf '%s\n' "$@" | xargs -P 3 -I{} sh -c 'python3 pipeline.py {} --anteprima > out/log-{}.txt 2>&1; tail -1 out/log-{}.txt'
