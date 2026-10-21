#!/usr/bin/env bash
# Prepara l'ambiente di Codex Cloud (ChatGPT) per questo repository: identità git, skill di Alessandro, strumenti dei controlli e delle skill.
# Lo lancia la prima riga dello «Script di installazione» di ogni ambiente (Impostazioni → Codex Cloud → «…» → Modifica → «Modifica ambiente»), su tutti i repository in /workspace: vedi memoria/piano-b-chatgpt.md di assistente-personale.
# Quando questo file cambia, si ripubblica ogni ambiente (Modifica → «Salva bozza» → «Pubblica»): i lavori nuovi partono da ciò che
# l'ambiente ha preparato alla pubblicazione, e l'aggiornamento del repository non rifà l'installazione.
# Identico in tutti i repository di Alessandro (copia di riferimento: assistente-personale). Non fallisce mai: ciò che non installa lo scrive e va avanti.
# Prova senza installare nulla: bash scripts/ambiente-codex.sh --prova
set -u
PROVA=0; [ "${1:-}" = "--prova" ] && PROVA=1
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 0
REPO="$(basename "$PWD")"
log() { printf '[ambiente %s] %s\n' "$REPO" "$*"; }
if [ "$(id -u)" -eq 0 ]; then SUDO=""; elif command -v sudo >/dev/null 2>&1; then SUDO="sudo"; else SUDO=""; fi

# 1. Identità git di Alessandro e hook che toglie le righe di firma degli strumenti. Vengono per prime:
#    se la configurazione si interrompe a metà, la firma dei commit è già a posto.
if [ "$PROVA" -eq 0 ] && [ -f scripts/imposta-identita-git.sh ]; then
  bash scripts/imposta-identita-git.sh >/dev/null 2>&1 || true
  log "identità git: $(git config user.name 2>/dev/null) <$(git config user.email 2>/dev/null)>, hook: $(git config core.hooksPath 2>/dev/null)"
fi

# 2. Skill di Alessandro e indice delle routine, prima delle dipendenze: servono anche quelle delle skill.
#    Dove l'ambiente contiene assistente-personale (il suo e «tutti-i-repository», con tutti e cinque i repository)
#    sono già nel repository: le skill si collegano in ~/.agents/skills e il repository in ~/assistente-personale,
#    lo stesso percorso del PC. Negli ambienti di un solo sito serve il token AP_TOKEN (sola lettura del repository
#    assistente-personale) e se ne scaricano solo skill, routine e file della radice, non i dati personali.
#    Si cancella e si riscarica solo una copia fatta da questo script (segno in .git): mai una copia di lavoro, come quella del PC.
AP="$HOME/assistente-personale"
SEGNO="$AP/.git/copia-degli-ambienti"
[ "$PROVA" -eq 0 ] && mkdir -p "$HOME/.agents"
if [ "$REPO" = "assistente-personale" ]; then
  if [ "$PROVA" -eq 1 ]; then log "collegherei le skill in $HOME/.agents/skills e, se lì non c'è niente, il repository in $AP"
  else
    ln -sfn "$PWD/.agents/skills" "$HOME/.agents/skills" && log "skill: $HOME/.agents/skills"
    # Solo se lì non c'è niente: una cartella vera, come la copia di lavoro del PC, non si tocca.
    [ -e "$AP" ] || { ln -sfn "$PWD" "$AP" && log "repository: $AP"; }
  fi
elif [ -n "${AP_TOKEN:-}" ]; then
  if [ "$PROVA" -eq 1 ]; then log "clonerei in $AP skill, routine e file della radice di assistente-personale"
  elif [ -e "$AP" ] && [ ! -e "$SEGNO" ]; then
    log "$AP c'è già (copia di lavoro o repository dell'ambiente): la lascio com'è"
    [ -d "$AP/.agents/skills" ] && ln -sfn "$AP/.agents/skills" "$HOME/.agents/skills"
  else
    rm -rf "$AP"
    if git clone -q --depth 1 --filter=blob:none --sparse \
         "https://x-access-token:${AP_TOKEN}@github.com/SviluppoItaliaDigitale/assistente-personale.git" "$AP" >/dev/null 2>&1 \
       && git -C "$AP" sparse-checkout set .agents/skills .claude/skills/landing-premium routine >/dev/null 2>&1; then
      git -C "$AP" remote set-url origin https://github.com/SviluppoItaliaDigitale/assistente-personale.git
      touch "$SEGNO"
      ln -sfn "$AP/.agents/skills" "$HOME/.agents/skills"
      log "skill e ROUTINE.md di assistente-personale in $AP"
    else
      rm -rf "$AP"
      log "assistente-personale NON clonato: controlla AP_TOKEN (con un segreto di rete non è ancora stato provato: vedi memoria/piano-b-chatgpt.md di assistente-personale)"
    fi
  fi
fi

# Dove si cerca che cosa serve: script e workflow del repository, skill del repository e skill di Alessandro.
DOVE=(scripts .github/workflows)
[ -e .agents/skills ] && DOVE+=(.agents/skills)
if [ "$REPO" != "assistente-personale" ]; then
  if [ -d "$AP/.agents/skills" ]; then DOVE+=("$AP/.agents/skills")
  elif [ "$PROVA" -eq 1 ] && [ -d ../assistente-personale/.agents/skills ]; then DOVE+=(../assistente-personale/.agents/skills)
  elif [ "$PROVA" -eq 1 ]; then log "in prova non conto le dipendenze delle skill di Alessandro: qui non ce n'è una copia"
  fi
fi
trova() { grep -RqsIE --exclude=ambiente-codex.sh "$1" "${DOVE[@]}" 2>/dev/null; }

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
PIP_VISTI=" "
pip_metti() {
  for p in "$@"; do
    case "$PIP_VISTI" in *" $p "*) continue ;; esac   # due moduli dello stesso pacchetto (fitz e pymupdf): una volta sola
    PIP_VISTI="$PIP_VISTI$p "
    if [ "$PROVA" -eq 1 ]; then log "installerei (pip) $p"; continue; fi
    if python3 -m pip install -q "$p" >/dev/null 2>&1 || python3 -m pip install -q --break-system-packages "$p" >/dev/null 2>&1; then log "pip: $p"; else log "pip: $p NON installato"; fi
  done
}

# 3. Moduli Python usati da script, workflow e skill (modulo:pacchetto).
for coppia in yaml:pyyaml requests:requests PIL:pillow fitz:pymupdf pymupdf:pymupdf pypdf:pypdf bs4:beautifulsoup4 feedparser:feedparser \
              segno:segno weasyprint:weasyprint playwright:playwright spylls:spylls yt_dlp:yt-dlp boto3:boto3 pptx:python-pptx \
              fontTools:fonttools brotli:brotli nacl:pynacl openpyxl:openpyxl docx:python-docx lxml:lxml numpy:numpy \
              matplotlib:matplotlib cartopy:cartopy netCDF4:netCDF4 rasterio:rasterio imageio_ffmpeg:imageio-ffmpeg \
              pdf2image:pdf2image pdfplumber:pdfplumber jsonschema:jsonschema defusedxml:defusedxml websockets:websockets \
              ortools:ortools kokoro_onnx:kokoro-onnx faster_whisper:faster-whisper piper:piper-tts; do
  m="${coppia%%:*}"; p="${coppia#*:}"
  if trova "^[[:space:]]*(import|from)[[:space:]]+$m([.[:space:]]|$)" || [ "$m" = "yaml" ]; then
    python3 -c "import $m" >/dev/null 2>&1 || pip_metti "$p"
  fi
done

# 4. Programmi di sistema che servono ai controlli, agli script e alle skill.
command -v gh >/dev/null 2>&1 || apt_metti gh
trova "pdftotext|pdfinfo|pdftoppm|pdf2image" && apt_metti poppler-utils
trova "hunspell|spylls|check-refusi" && apt_metti hunspell-it
if trova "liblouis|import louis"; then
  apt_metti python3-louis liblouis-data
  # Il modulo di apt è per il Python di sistema: se python3 è un altro (pyenv), lo si collega fra i suoi pacchetti.
  if [ "$PROVA" -eq 0 ] && ! python3 -c "import louis" >/dev/null 2>&1 && [ -d /usr/lib/python3/dist-packages/louis ]; then
    SP="$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])' 2>/dev/null)"
    if [ -n "$SP" ]; then
      mkdir -p "$SP" 2>/dev/null || $SUDO mkdir -p "$SP"
      ln -sfn /usr/lib/python3/dist-packages/louis "$SP/louis" 2>/dev/null || $SUDO ln -sfn /usr/lib/python3/dist-packages/louis "$SP/louis"
    fi
  fi
  if [ "$PROVA" -eq 0 ]; then
    if python3 -c "import louis" >/dev/null 2>&1; then log "louis: python3 lo importa"; else log "louis: python3 NON lo importa"; fi
  fi
fi
trova "ffmpeg|ffprobe" && apt_metti ffmpeg
trova "weasyprint" && apt_metti libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0
trova "Liberation|fonts-liberation" && apt_metti fonts-liberation

# 5. Hugo extended, nella versione dei workflow di pubblicazione (la versione standard, senza «extended», non basta).
VER="$(grep -rhoE "hugo-version: *['\"]?[0-9]+\.[0-9]+\.[0-9]+" .github/workflows 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)"
if [ -n "$VER" ] && ! hugo version 2>/dev/null | grep -q "v$VER.*extended"; then
  case "$(uname -m)" in aarch64|arm64) A=arm64 ;; *) A=amd64 ;; esac
  URL="https://github.com/gohugoio/hugo/releases/download/v$VER/hugo_extended_${VER}_linux-$A.tar.gz"
  if [ "$PROVA" -eq 1 ]; then log "installerei Hugo extended $VER da $URL"
  else
    T="$(mktemp -d)"
    if curl -fsSL "$URL" -o "$T/hugo.tgz" && tar -xzf "$T/hugo.tgz" -C "$T" hugo && $SUDO install -m 0755 "$T/hugo" /usr/local/bin/hugo; then log "Hugo extended $VER"; else log "Hugo $VER NON installato ($URL)"; fi
    rm -rf "$T"
  fi
fi

# 6. Dipendenze Node degli script che le dichiarano (prima del browser: playwright-core arriva da qui).
for pj in scripts/*/package.json; do
  [ -f "$pj" ] || continue
  d="$(dirname "$pj")"
  if [ "$PROVA" -eq 1 ]; then log "installerei le dipendenze Node di $d"
  elif (cd "$d" && { [ -f package-lock.json ] && npm ci --silent >/dev/null 2>&1 || npm install --silent >/dev/null 2>&1; }); then log "npm: $d"; else log "npm: $d NON installato"; fi
done

# 7. Browser per i controlli di stampa, accessibilità e grafiche. Gli script Python usano Playwright; quelli Node usano
#    playwright-core, che non scarica il browser: lo si installa in /opt/pw-browsers, come nelle sessioni di Claude,
#    e si creano i percorsi fissi che gli script si aspettano.
if trova "playwright"; then
  if [ "$PROVA" -eq 1 ]; then log "installerei Chromium per Playwright (Python e Node)"
  else
    C=""
    if python3 -c "import playwright" >/dev/null 2>&1; then
      python3 -m playwright install --with-deps chromium >/dev/null 2>&1 || python3 -m playwright install chromium >/dev/null 2>&1
      C="$(find "${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}" -type f -name chrome -path '*chrome-linux*' 2>/dev/null | sort -V | tail -1)"
    fi
    for cli in scripts/*/node_modules/playwright-core/cli.js; do
      [ -f "$cli" ] || continue
      $SUDO mkdir -p /opt/pw-browsers && $SUDO chown "$(id -u)" /opt/pw-browsers
      PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node "$cli" install --with-deps chromium >/dev/null 2>&1 \
        || PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node "$cli" install chromium >/dev/null 2>&1
      B="$(find /opt/pw-browsers -type f -name chrome -path '*chrome-linux*' 2>/dev/null | sort -V | tail -1)"
      [ -n "$B" ] && C="$B"
      break
    done
    if [ -n "$C" ]; then
      $SUDO ln -sfn "$C" /usr/local/bin/chromium 2>/dev/null
      [ -e /opt/pw-browsers/chromium ] || { $SUDO mkdir -p /opt/pw-browsers 2>/dev/null && $SUDO ln -sfn "$C" /opt/pw-browsers/chromium 2>/dev/null; }
      for p in $(grep -RhoIE --exclude=ambiente-codex.sh '/opt/pw-browsers/chromium-[0-9]+/chrome-linux/chrome' "${DOVE[@]}" 2>/dev/null | sort -u); do
        [ -e "$p" ] || { $SUDO mkdir -p "$(dirname "$p")" 2>/dev/null && $SUDO ln -sfn "$C" "$p" 2>/dev/null; }
      done
      L="$C"
      [ -e /usr/local/bin/chromium ] && L="$L, /usr/local/bin/chromium"
      [ -e /opt/pw-browsers/chromium ] && L="$L, /opt/pw-browsers/chromium"
      log "Chromium: $L"
    else log "Chromium NON installato"; fi
  fi
fi

HV="assente"; command -v hugo >/dev/null 2>&1 && HV="$(hugo version | cut -d' ' -f2)"
log "pronto — Hugo: $HV, Python: $(python3 --version 2>&1 | cut -d' ' -f2), Node: $(node --version 2>/dev/null || echo assente), gh: $(command -v gh >/dev/null 2>&1 && echo presente || echo assente)"
exit 0
