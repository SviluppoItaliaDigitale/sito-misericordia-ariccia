#!/usr/bin/env bash
# giro-automatico.sh — Lancia senza finestra il giro giornaliero del podcast della
# Misericordia di Ariccia (adattato da quello della Protezione Civile di Genzano).
# Lo avvia la crontab dell'utente sul PC ogni ora dalle 8:11 alle 21:11; parte davvero
# solo una volta al giorno e solo se le puntate in calendario sono meno di 8: Claude Code
# con Chrome, in una copia di lavoro separata da main, segue scripts/podcast-auto/README.md.
# Chrome e NotebookLM sono gli stessi del podcast della Protezione Civile: i due giri
# non devono mai lavorare insieme, quindi questo prende il blocco comune
# ~/.cache/podcast-chrome.lock e, se è occupato, esce e riprova all'ora successiva.
# Uso: giro-automatico.sh            (giro vero)
#      giro-automatico.sh --prova    (controlla solo il collegamento a Chrome)
set -euo pipefail

REPO="$HOME/sito-misericordia-ariccia"
LAVORO="$HOME/podcast-lavoro-misericordia"
COPIA="$LAVORO/copia-sito"
LOG="$LAVORO/log/$(date +%Y-%m-%d-%H%M).log"
BLOCCO_CHROME="$HOME/.cache/podcast-chrome.lock"
mkdir -p "$LAVORO/log" "$(dirname "$BLOCCO_CHROME")"

# Ambiente della sessione grafica: dalla crontab mancano e senza di loro
# Claude Code non trova l'estensione di Chrome.
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
export DISPLAY="${DISPLAY:-:0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
# Con GNOME su Wayland Chrome vuole anche l'autorizzazione di Xwayland, che cambia nome a ogni
# avvio del PC (19/11/2026: da SSH Chrome non partiva, «Missing X server or $DISPLAY»).
if [ -z "${XAUTHORITY:-}" ]; then
  XAUTHORITY=$(ls -t "$XDG_RUNTIME_DIR"/.mutter-Xwaylandauth.* 2>/dev/null | head -1 || true)
  [ -n "$XAUTHORITY" ] && export XAUTHORITY
fi

# Un solo giro della Misericordia alla volta.
exec 9>"$LAVORO/.giro.lock"
flock -n 9 || { echo "Un giro è già in corso." >>"$LOG"; exit 0; }

# Blocco comune con il podcast della Protezione Civile (stesso Chrome, stesso NotebookLM).
exec 8>"$BLOCCO_CHROME"
flock -n 8 || { echo "Chrome è occupato da un altro giro del podcast: riprovo all'ora successiva." >>"$LOG"; exit 0; }

if [ "${1:-}" = "--prova" ]; then
  cd "$REPO"
  echo "Usa tabs_context_mcp di Claude in Chrome (caricalo con ToolSearch) e rispondi solo «CHROME OK» se risponde, altrimenti «CHROME NO»." \
    | timeout 300 claude -p --chrome --allowedTools "ToolSearch,mcp__claude-in-chrome__tabs_context_mcp" 2>&1 \
    | grep -v '^Permission allow rule' | tee -a "$LOG"
  exit 0
fi

# Si parte solo se serve: un giro riuscito al giorno, e solo con il magazzino
# sotto le 8 puntate (controllo gratuito, su origin/main appena scaricato).
FATTO="$LAVORO/.giro-fatto-$(date +%Y-%m-%d)"
[ -f "$FATTO" ] && exit 0
git -C "$REPO" fetch -q origin main
git -C "$REPO" show origin/main:scripts/podcast-auto/controlla-magazzino.py >/dev/null 2>&1 || exit 0
TMPD=$(mktemp -d)
git -C "$REPO" archive origin/main content/podcast scripts/podcast-auto | tar -x -C "$TMPD"
if TZ=Europe/Rome python3 "$TMPD/scripts/podcast-auto/controlla-magazzino.py" --minimo 8 >/dev/null 2>&1; then
  rm -rf "$TMPD"; touch "$FATTO"; exit 0
fi
rm -rf "$TMPD"
echo "Giro avviato $(date)" >>"$LOG"

# Senza l'estensione di Chrome collegata il giro non può produrre nulla: non si
# segna come fatto e riprova all'ora successiva (guasto del 19/11/2026: il giro
# delle 8:11 trovò Chrome scollegato, uscì «riuscito» e saltò il resto del giorno).
CHROME=$(cd "$REPO" && echo "Usa tabs_context_mcp di Claude in Chrome (caricalo con ToolSearch) e rispondi solo «CHROME OK» se risponde, altrimenti «CHROME NO»." \
  | timeout 300 claude -p --chrome --allowedTools "ToolSearch,mcp__claude-in-chrome__tabs_context_mcp" 2>&1 | grep -v '^Permission allow rule')
echo "Controllo Chrome: $CHROME" >>"$LOG"
if ! printf '%s' "$CHROME" | grep -q "CHROME OK"; then
  echo "Estensione di Chrome non collegata: niente giro, riprovo all'ora successiva." >>"$LOG"
  exit 0
fi

# Copia di lavoro pulita, allineata a origin/main.
if [ -d "$COPIA" ]; then
  git -C "$REPO" worktree remove --force "$COPIA" >>"$LOG" 2>&1 || rm -rf "$COPIA"
  git -C "$REPO" worktree prune
fi
git -C "$REPO" worktree add -q --detach "$COPIA" origin/main >>"$LOG" 2>&1
cd "$COPIA"
bash scripts/imposta-identita-git.sh >>"$LOG" 2>&1 || true

PROMPT="Giro giornaliero del podcast automatico della Misericordia di Ariccia, senza nessuno davanti allo schermo. \
Conta le puntate in calendario con: python3 scripts/podcast-auto/controlla-magazzino.py --minimo 8. \
Se sono 8 o più, scrivi «Magazzino pieno» ed esci. Altrimenti produci nuove puntate seguendo alla lettera \
scripts/podcast-auto/README.md (fonti con trova-fonti.py, NotebookLM nel Chrome in schede nuove, trascrizione, \
controllo dei fatti rigoroso, pubblicazione con pubblica-puntata.py, ramo claude/podcast-…, PR, squash merge \
a controlli verdi, verifica del deploy) finché il magazzino torna a 8, la coda finisce o NotebookLM rifiuta altre \
generazioni. Ogni puntata che supera il controllo va subito online nella sezione Podcast del sito (una PR per \
puntata, unita appena i controlli sono verdi) e nel calendario dei social, il primo mercoledì o sabato libero \
(social_data, lo scrive pubblica-puntata.py): dopo il deploy controlla che la pagina /podcast/<file>/ risponda, \
che il lettore carichi l'audio e che la puntata sia nel feed /podcast/index.xml (regola di Alessandro del \
21/11/2026). Una puntata con anche un solo errore non si pubblica. Alla fine scrivi un resoconto breve e, se hai \
prodotto o scartato qualcosa, manda una notifica ad Alessandro. Se a un certo punto l'estensione di Chrome non \
risponde più, fermati e scrivi come ultima riga GIRO-SENZA-CHROME."

if echo "$PROMPT" | timeout 5h claude -p --chrome --permission-mode auto >>"$LOG" 2>&1; then
  if grep -q "GIRO-SENZA-CHROME" "$LOG"; then
    echo "Chrome si è scollegato durante il giro: riprovo all'ora successiva." >>"$LOG"
  else
    touch "$FATTO"
  fi
else
  echo "Giro terminato con errore $? (riprova all'ora successiva)" >>"$LOG"
fi
