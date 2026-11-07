#!/usr/bin/env bash
# Avvio delle sessioni (hook SessionStart, identico in tutti i repository, dal 07/11/2026): prepara ciò che
# serve ai plugin ufficiali attivi in .claude/settings.json, sul PC e nelle sessioni cloud dell'app.
# Oggi installa pyright (per pyright-lsp) se manca: npm, poi pip. Non stampa nulla se è già tutto pronto.

pronto() { command -v pyright-langserver >/dev/null 2>&1; }
pronto && exit 0

if command -v npm >/dev/null 2>&1; then
  npm install -g pyright >/dev/null 2>&1 || npm install -g --prefix "$HOME/.local" pyright >/dev/null 2>&1
fi
if ! pronto && command -v pip3 >/dev/null 2>&1; then
  pip3 install --user --quiet pyright >/dev/null 2>&1 || pip3 install --user --quiet --break-system-packages pyright >/dev/null 2>&1
fi
export PATH="$HOME/.local/bin:$PATH"

if pronto; then
  echo "Plugin: pyright installato per il controllo degli script Python."
else
  echo "Plugin: pyright non si è installato (né npm né pip): il controllo degli script Python resta spento in questa sessione."
fi
exit 0
