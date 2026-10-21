#!/usr/bin/env bash
# Prepara l'ambiente di Codex Cloud (ChatGPT) per questo repository: strumenti dei controlli, identità git, skill di Alessandro.
# Si imposta una volta sola: Codex → Impostazioni → Ambienti → questo repository → «Script di configurazione» = bash scripts/ambiente-codex.sh
# Identico in tutti i repository di Alessandro (copia di riferimento: assistente-personale). Non fallisce mai: ciò che non installa lo scrive e va avanti.
# Prova senza installare nulla: bash scripts/ambiente-codex.sh --prova
set -u
PROVA=0; [ "${1:-}" = "--prova" ] && PROVA=1
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 0
REPO="$(basename "$PWD")"
log() { printf '[ambiente %s] %s\n' "$REPO" "$*"; }
if [ "$(id -u)" -eq 0 ]; then SUDO=""; elif command -v sudo >/dev/null 2>&1; then SUDO="sudo"; else SUDO=""; fi
trova() { grep -rqsE --exclude=ambiente-codex.sh "$1" scripts .github/workflows 2>/dev/null; }

APT_PRONTO=0
apt_metti() {
  command -v apt-get >/dev/null 2>&1 || { log "apt-get non c'è: salto $*"; return 0; }
  for p in "$@"; do
    if dpkg -s "$p" >/dev/null 2>&1; then continue; fi
    if [ "$PROVA" -eq 1 ]; then log "installerei (apt) $p"; continue; fi
    if [ "$APT_PRONTO" -eq 0 ]; then $SUDO apt-get update -qq >/dev/null 2>&1 && APT_PRONTO=1; fi
    if $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$p" >/dev/null 2>&1; then log "apt: $p"; else log "apt: $p NON installato"; fi
  done
}
pip_metti() {
  for p in "$@"; do
    if [ "$PROVA" -eq 1 ]; then log "installerei (pip) $p"; continue; fi
    if python3 -m pip install -q "$p" >/dev/null 2>&1 || python3 -m pip install -q --break-system-packages "$p" >/dev/null 2>&1; then log "pip: $p"; else log "pip: $p NON installato"; fi
  done
}

# 1. Moduli Python usati dagli script e dai workflow del repository (modulo:pacchetto).
for coppia in yaml:pyyaml requests:requests PIL:pillow fitz:pymupdf pypdf:pypdf bs4:beautifulsoup4 feedparser:feedparser segno:segno \
              weasyprint:weasyprint playwright:playwright spylls:spylls yt_dlp:yt-dlp boto3:boto3 pptx:python-pptx fontTools:fonttools \
              brotli:brotli nacl:pynacl openpyxl:openpyxl docx:python-docx lxml:lxml; do
  m="${coppia%%:*}"; p="${coppia#*:}"
  if trova "^[[:space:]]*(import|from)[[:space:]]+$m([.[:space:]]|$)" || [ "$m" = "yaml" ]; then
    python3 -c "import $m" >/dev/null 2>&1 || pip_metti "$p"
  fi
done

# 2. Programmi di sistema che servono ai controlli.
trova "pdftotext|pdfinfo|pdftoppm" && apt_metti poppler-utils
trova "hunspell|spylls|check-refusi" && apt_metti hunspell-it
trova "liblouis|import louis" && apt_metti python3-louis liblouis-data
trova "ffmpeg|ffprobe" && apt_metti ffmpeg
trova "weasyprint" && apt_metti libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0
trova "Liberation|fonts-liberation" && apt_metti fonts-liberation

# 3. Hugo extended, nella versione dei workflow di pubblicazione.
VER="$(grep -rhoE "hugo-version: *['\"]?[0-9]+\.[0-9]+\.[0-9]+" .github/workflows 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)"
if [ -n "$VER" ] && ! hugo version 2>/dev/null | grep -q "v$VER"; then
  case "$(uname -m)" in aarch64|arm64) A=arm64 ;; *) A=amd64 ;; esac
  URL="https://github.com/gohugoio/hugo/releases/download/v$VER/hugo_extended_${VER}_linux-$A.tar.gz"
  if [ "$PROVA" -eq 1 ]; then log "installerei Hugo extended $VER da $URL"
  else
    T="$(mktemp -d)"
    if curl -fsSL "$URL" -o "$T/hugo.tgz" && tar -xzf "$T/hugo.tgz" -C "$T" hugo && $SUDO install -m 0755 "$T/hugo" /usr/local/bin/hugo; then log "Hugo extended $VER"; else log "Hugo $VER NON installato ($URL)"; fi
    rm -rf "$T"
  fi
fi

# 4. Browser per i controlli di stampa, accessibilità e grafiche (Playwright).
if trova "playwright"; then
  if [ "$PROVA" -eq 1 ]; then log "installerei Chromium per Playwright"
  elif python3 -c "import playwright" >/dev/null 2>&1; then
    if python3 -m playwright install --with-deps chromium >/dev/null 2>&1 || python3 -m playwright install chromium >/dev/null 2>&1; then
      B="$(find "$HOME/.cache/ms-playwright" -type f -name chrome -path '*chrome-linux*' 2>/dev/null | head -1)"
      [ -n "$B" ] && $SUDO ln -sfn "$B" /usr/local/bin/chromium && log "Chromium: /usr/local/bin/chromium"
    else log "Chromium NON installato"; fi
  fi
fi

# 5. Dipendenze Node degli script che le dichiarano.
for pj in scripts/*/package.json; do
  [ -f "$pj" ] || continue
  d="$(dirname "$pj")"
  if [ "$PROVA" -eq 1 ]; then log "installerei le dipendenze Node di $d"
  elif (cd "$d" && { [ -f package-lock.json ] && npm ci --silent >/dev/null 2>&1 || npm install --silent >/dev/null 2>&1; }); then log "npm: $d"; else log "npm: $d NON installato"; fi
done

# 6. Identità git di Alessandro e hook che toglie le righe di firma degli strumenti.
if [ "$PROVA" -eq 0 ] && [ -f scripts/imposta-identita-git.sh ]; then
  bash scripts/imposta-identita-git.sh >/dev/null 2>&1 || true
  log "identità git: $(git config user.name 2>/dev/null) <$(git config user.email 2>/dev/null)>, hook: $(git config core.hooksPath 2>/dev/null)"
fi

# 7. Skill di Alessandro e indice delle routine (solo se nell'ambiente c'è il segreto AP_TOKEN, lettura del repository assistente-personale).
mkdir -p "$HOME/.agents"
if [ "$REPO" = "assistente-personale" ]; then
  [ "$PROVA" -eq 0 ] && ln -sfn "$PWD/.agents/skills" "$HOME/.agents/skills" && log "skill: $HOME/.agents/skills"
elif [ -n "${AP_TOKEN:-}" ]; then
  D="$HOME/assistente-personale"
  if [ "$PROVA" -eq 1 ]; then log "clonerei assistente-personale in $D"
  else
    rm -rf "$D"
    if git clone -q --depth 1 "https://x-access-token:${AP_TOKEN}@github.com/SviluppoItaliaDigitale/assistente-personale.git" "$D" >/dev/null 2>&1; then
      git -C "$D" remote set-url origin https://github.com/SviluppoItaliaDigitale/assistente-personale.git
      ln -sfn "$D/.agents/skills" "$HOME/.agents/skills"
      log "skill e ROUTINE.md di assistente-personale in $D"
    else log "assistente-personale NON clonato: controlla il segreto AP_TOKEN"; fi
  fi
fi

HV="assente"; command -v hugo >/dev/null 2>&1 && HV="$(hugo version | cut -d' ' -f2)"
log "pronto — Hugo: $HV, Python: $(python3 --version 2>&1 | cut -d' ' -f2), Node: $(node --version 2>/dev/null || echo assente)"
exit 0
