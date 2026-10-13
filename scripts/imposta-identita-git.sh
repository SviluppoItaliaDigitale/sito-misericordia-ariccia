#!/usr/bin/env bash
# imposta-identita-git.sh
#
# Garantisce che i commit di QUALSIASI sessione risultino del Gruppo e mai di
# uno strumento automatico. Gira come hook SessionStart, prima che si possa
# fare il primo commit.
#
# Perche' esiste (31/08/2026): alcuni container cloud partono con l'identita'
# git impostata sullo strumento (`noreply@anthropic.com`). Le conseguenze sono
# due, entrambe vietate dalla regola "nessun riferimento a strumenti automatici"
# di CLAUDE.md:
#   1. ogni commit risulta firmato dallo strumento come AUTORE, visibile su
#      GitHub;
#   2. allo squash-merge GitHub aggiunge DA SOLO il trailer `Co-authored-by`
#      ricavandolo proprio da quell'autore, anche quando il messaggio di commit
#      ne e' privo. L'impostazione `includeCoAuthoredBy: false` non lo previene:
#      agisce sul client, non sul server GitHub.
#
# Il 31/08/2026 un commit e' arrivato su `main` firmato dallo strumento e col
# trailer aggiunto da GitHub. Affidarsi al fatto che la sessione "si ricordi" di
# controllare l'identita' non basta: qui il controllo e' deterministico.
#
# Comportamento (conservativo: non sovrascrive un'identita' legittima):
#   - esce silenziosamente se non siamo in un repo git;
#   - imposta l'identita' del repo SOLO se quella corrente e' assente oppure
#     riconducibile a uno strumento automatico;
#   - scrive la config a livello LOCALE del repo, cosi' non tocca le altre
#     cartelle della macchina.
#
# Per disabilitare temporaneamente: PCGENZANO_SKIP_IDENTITA=1 nell'env.

set -u

[ "${PCGENZANO_SKIP_IDENTITA:-0}" = "1" ] && exit 0

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

# --- Hook dei messaggi di commit -------------------------------------------
# Stessa regola dell'identita', applicata al testo: nessun messaggio di commit
# deve rimandare a uno strumento automatico. Git non attiva da solo gli hook
# versionati, quindi qui si punta `core.hooksPath` alla cartella .githooks del
# repo. Idempotente: se e' gia' impostato non fa nulla.
#
# Perche' serve (21/09/2026): un censimento ha trovato 170 commit su main, dal
# 19 giugno, con la riga di sessione nel messaggio. Nessuna sessione lo faceva
# apposta: la regola c'era, ma era affidata alla memoria.
if [ -d "$(git rev-parse --show-toplevel 2>/dev/null)/.githooks" ]; then
  if [ "$(git config core.hooksPath 2>/dev/null || true)" != ".githooks" ]; then
    git config core.hooksPath .githooks 2>/dev/null \
      && echo "[identita-git] Hook dei messaggi di commit attivati (.githooks)." >&2
  fi
fi

# Identita' canonica del repository: il nome della persona che cura il sito.
# L'email resta quella `noreply` di GitHub: e' il campo con cui GitHub collega
# il commit al profilo, quindi cambiarla scollegherebbe i commit dall'account.
NOME_OK="Alessandro Cuollo"
EMAIL_OK="65465537+SviluppoItaliaDigitale@users.noreply.github.com"

NOME_ORA="$(git config user.name 2>/dev/null || true)"
EMAIL_ORA="$(git config user.email 2>/dev/null || true)"

# Da correggere in tre casi:
#   a) identita' assente;
#   b) identita' riconducibile a uno strumento automatico;
#   c) stessa email dell'account del repo ma nome diverso (allinea le sigle
#      storiche al nome della persona, senza toccare l'identita' di altri);
#   d) nome uguale a quello dell'account GitHub del repo (con qualunque email:
#      e' la stessa persona che scrive da una macchina configurata con la sua
#      email personale). Senza questo caso, l'email privata finisce in chiaro
#      su ogni commit pubblico: la forma `noreply` esiste per evitarlo.
#      Un collaboratore diverso ha un altro nome e non viene toccato.
da_correggere=0
[ -z "$NOME_ORA" ] || [ -z "$EMAIL_ORA" ] && da_correggere=1
printf '%s %s' "$NOME_ORA" "$EMAIL_ORA" | grep -qiE 'claude|anthropic|\bbot\b|assistant' && da_correggere=1
[ "$EMAIL_ORA" = "$EMAIL_OK" ] && [ "$NOME_ORA" != "$NOME_OK" ] && da_correggere=1
[ "$NOME_ORA" = "SviluppoItaliaDigitale" ] && da_correggere=1

[ "$da_correggere" -eq 0 ] && exit 0

git config user.name "$NOME_OK" 2>/dev/null || exit 0
git config user.email "$EMAIL_OK" 2>/dev/null || exit 0

echo "[identita-git] Identita' dei commit impostata su ${NOME_OK} (era: ${NOME_ORA:-vuota} <${EMAIL_ORA:-vuota}>)." >&2

exit 0
