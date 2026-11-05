#!/usr/bin/env bash
# Accesso della riserva automatica nelle GitHub Actions: lo ripristina prima dell'avvio, salva cifrata la copia
# aggiornata dopo, tiene solo le ultime copie in cache e pulisce. Lo usa .github/workflows/riserva-automatica.yml.
#
# L'accesso è un collegamento a parte, fatto da Alessandro con scripts/collega-riserva.sh e salvato nel segreto
# RISERVA_ACCESSO (file dell'accesso in base64); per ChatGPT automatico (dal 05/11/2026) con scripts/collega-ai-automatiche.sh
# nel segreto CHATGPT_ACCESSO, con NOME_SEGRETO e CACHE_PREFISSO impostati dal workflow lavoratore-ai.yml. A ogni uso il programma può rinnovarlo e quello vecchio smette di
# valere: per questo la copia rinnovata si salva cifrata (AES256) nella cache del repository e la volta dopo si
# riparte da lì, non dal segreto. La chiave di cifratura deriva dal segreto: con un collegamento nuovo la copia
# vecchia non si apre più e si riparte dal segreto nuovo, come deve essere.
#
# Comandi: ripristina | salva | sfoltisci | pulisci
# Variabili: SEME (il segreto), CODEX_HOME (cartella dell'accesso del programma), RISERVA_CACHE (cartella della
# cache, predefinita riserva-cache), RUNNER_TEMP, GITHUB_OUTPUT; per sfoltisci anche GH_TOKEN e GH_REPO.
set -euo pipefail
umask 077

CACHE="${RISERVA_CACHE:-riserva-cache}"
NOME_SEGRETO="${NOME_SEGRETO:-RISERVA_ACCESSO}"   # anche CHATGPT_ACCESSO, per le AI automatiche
PREFISSO="${CACHE_PREFISSO:-riserva-}"              # inizio delle chiavi della cache di questo accesso
TEMP="${RUNNER_TEMP:-${TMPDIR:-/tmp}}"
SEGNI="$TEMP/riserva-segni"          # impronte di inizio run e origine dell'accesso, fuori dalla cache
MARCATORE="$TEMP/riserva-accesso"    # «valido» oppure il motivo per cui l'accesso non c'è
COPIE_DA_TENERE=3

uscita() { if [ -n "${GITHUB_OUTPUT:-}" ]; then echo "$1=$2" >> "$GITHUB_OUTPUT"; else echo "$1=$2"; fi; }

frase() {   # chiave di cifratura: deriva dal segreto, non si scrive mai su disco
  printf 'riserva-automatica|%s' "$SEME" | sha256sum | cut -d' ' -f1
}

impronta_file() { if [ -f "$1" ]; then sha256sum < "$1" | cut -d' ' -f1; else echo assente; fi; }

# Controlla un file dell'accesso: accesso con l'account (non a consumo), con il codice di rinnovo.
# Con «--maschera» stampa anche i comandi che nascondono i valori nei registri.
controlla_accesso() {
  python3 - "$1" "${2:-}" <<'PY'
import base64, json, sys
percorso, maschera = sys.argv[1], sys.argv[2] == "--maschera"
try:
    dati = json.load(open(percorso))
except (OSError, ValueError):
    sys.exit("non è un file dell'accesso leggibile")
gettoni = dati.get("tokens") or {}
if dati.get("OPENAI_API_KEY"):
    sys.exit("contiene una chiave a consumo: la riserva usa solo l'accesso con l'account")
if str(dati.get("auth_mode") or "chatgpt").lower() != "chatgpt":
    sys.exit("non è un accesso con l'account")
if not isinstance(gettoni.get("refresh_token"), str) or not gettoni["refresh_token"]:
    sys.exit("manca il codice di rinnovo")
if maschera:
    valori = [gettoni.get(k) for k in ("access_token", "refresh_token", "id_token", "account_id")]
    try:
        corpo = gettoni.get("id_token", "").split(".")[1]
        rivendicazioni = json.loads(base64.urlsafe_b64decode(corpo + "=" * (-len(corpo) % 4)))
        dettagli = rivendicazioni.get("https://api.openai.com/auth") or {}
        valori += [rivendicazioni.get("email"), rivendicazioni.get("sub"),
                   dettagli.get("chatgpt_user_id"), dettagli.get("chatgpt_account_id"), dettagli.get("user_id")]
    except Exception:
        pass
    for v in valori:
        if isinstance(v, str) and len(v) >= 6:
            print(f"::add-mask::{v}")
PY
}

gpg_temporaneo() {  # gpg con una cartella usa e getta, chiave letta da un canale (mai da file)
  local casa esito=0; casa="$(mktemp -d)"
  GNUPGHOME="$casa" gpg --batch --yes --quiet --no-symkey-cache --pinentry-mode loopback \
    --passphrase-fd 3 "$@" 3< <(frase) || esito=$?
  GNUPGHOME="$casa" gpgconf --kill gpg-agent 2>/dev/null || true
  rm -rf "$casa"
  return "$esito"
}

cifra() { gpg_temporaneo --symmetric --cipher-algo AES256 --output "$2" "$1"; }          # $1 → $2
decifra() { gpg_temporaneo --decrypt --output "$2" "$1" 2>/dev/null; }                     # $1 → $2

ripristina() {
  : "${CODEX_HOME:?serve CODEX_HOME}"
  mkdir -p "$SEGNI" "$CODEX_HOME" "$CACHE"
  chmod 700 "$CODEX_HOME"
  printf 'cli_auth_credentials_store = "file"\n' > "$CODEX_HOME/config.toml"
  rm -f "$CODEX_HOME/auth.json" "$MARCATORE"
  impronta_file "$CACHE/stato.json" > "$SEGNI/stato-iniziale"
  echo nessuna > "$SEGNI/origine"

  if [ -z "${SEME:-}" ]; then
    echo "il segreto $NOME_SEGRETO non è impostato" > "$MARCATORE"
    echo "::warning::Accesso non collegato (segreto $NOME_SEGRETO vuoto)."
    uscita valido false; return 0
  fi
  echo "::add-mask::$(frase)"

  local lavoro scelta="" origine="" motivo_seme=""
  lavoro="$(mktemp -d)"
  # 1. La copia rinnovata dell'ultima volta, se si apre con la chiave di questo segreto.
  if [ -f "$CACHE/auth.json.gpg" ]; then
    if decifra "$CACHE/auth.json.gpg" "$lavoro/dalla-cache.json" \
        && controlla_accesso "$lavoro/dalla-cache.json" --maschera > "$lavoro/maschera"; then
      cat "$lavoro/maschera"
      scelta="$lavoro/dalla-cache.json"; origine=cache
    else
      echo "La copia in cache non si apre con questo segreto (collegamento nuovo o copia rovinata): riparto dal segreto."
    fi
  fi
  # 2. Altrimenti il segreto.
  if [ -z "$scelta" ]; then
    if printf '%s' "$SEME" | base64 -d > "$lavoro/dal-segreto.json" 2>/dev/null \
        && motivo_seme="$(controlla_accesso "$lavoro/dal-segreto.json" --maschera 2>&1 > "$lavoro/maschera")"; then
      cat "$lavoro/maschera"
      scelta="$lavoro/dal-segreto.json"; origine=seme
    else
      motivo_seme="${motivo_seme:-non è un testo in base64}"
      echo "il segreto $NOME_SEGRETO non contiene un accesso valido: $motivo_seme" > "$MARCATORE"
      echo "::warning::$(cat "$MARCATORE")"
      rm -rf "$lavoro"
      uscita valido false; return 0
    fi
  fi

  install -m 600 "$scelta" "$CODEX_HOME/auth.json"
  impronta_file "$CODEX_HOME/auth.json" > "$SEGNI/accesso-iniziale"
  echo "$origine" > "$SEGNI/origine"
  echo valido > "$MARCATORE"
  rm -rf "$lavoro"
  if [ "$origine" = cache ]; then echo "Accesso pronto: preso dalla copia cifrata in cache."
  else echo "Accesso pronto: preso dal segreto."; fi
  uscita valido true
}

salva() {
  local cambiato=false origine
  origine="$(cat "$SEGNI/origine" 2>/dev/null || echo nessuna)"
  if [ "$origine" != nessuna ] && [ -n "${CODEX_HOME:-}" ] && [ -f "$CODEX_HOME/auth.json" ]; then
    local maschere
    if maschere="$(controlla_accesso "$CODEX_HOME/auth.json" --maschera 2>/dev/null)"; then
      printf '%s\n' "$maschere"   # nasconde nei registri anche i valori rinnovati
      if [ "$origine" != cache ] || [ "$(impronta_file "$CODEX_HOME/auth.json")" != "$(cat "$SEGNI/accesso-iniziale")" ]; then
        mkdir -p "$CACHE"
        cifra "$CODEX_HOME/auth.json" "$CACHE/auth.json.gpg.nuovo"
        mv "$CACHE/auth.json.gpg.nuovo" "$CACHE/auth.json.gpg"
        cambiato=true
        echo "Accesso $( [ "$origine" = cache ] && echo 'rinnovato' || echo 'nuovo' ): salvo la copia cifrata."
      fi
    else
      echo "::warning::Il file dell'accesso dopo l'uso non è leggibile: tengo la copia precedente."
    fi
  fi
  if [ "$(impronta_file "$CACHE/stato.json")" != "$(cat "$SEGNI/stato-iniziale" 2>/dev/null || echo assente)" ]; then
    cambiato=true
  fi
  uscita cambiato "$cambiato"
}

sfoltisci() {   # tiene le ultime copie per ramo (la cache è separata per ramo)
  : "${GH_REPO:?serve GH_REPO}"
  local elenco
  elenco="$(gh api "repos/$GH_REPO/actions/caches?key=$PREFISSO&sort=created_at&direction=desc&per_page=100")"
  printf '%s' "$elenco" | python3 -c '
import json, sys
tenute = {}
for c in json.load(sys.stdin)["actions_caches"]:
    if not c["key"].startswith(sys.argv[2]):
        continue
    tenute[c["ref"]] = tenute.get(c["ref"], 0) + 1
    if tenute[c["ref"]] > int(sys.argv[1]):
        print(c["id"])
' "$COPIE_DA_TENERE" "$PREFISSO" | while read -r numero; do
    gh api -X DELETE "repos/$GH_REPO/actions/caches/$numero" > /dev/null && echo "Tolta la copia vecchia $numero."
  done
}

pulisci() {
  if [ -n "${CODEX_HOME:-}" ]; then rm -rf "$CODEX_HOME"; fi
  rm -rf "$SEGNI" "$MARCATORE"
  echo "Pulizia fatta."
}

case "${1:-}" in
  ripristina) ripristina ;;
  salva) salva ;;
  sfoltisci) sfoltisci ;;
  pulisci) pulisci ;;
  *) echo "uso: $0 ripristina|salva|sfoltisci|pulisci" >&2; exit 2 ;;
esac
