#!/usr/bin/env python3
"""Consulto fra le intelligenze artificiali gratuite della squadra: il parere di una sola AI, oppure le AI che parlano
fra loro («tutti»: rispondono, leggono le risposte delle altre, si correggono, e una sintesi dice dove concordano e dove no).

Uso:  consulto-ai.py <ai> "domanda"      ai: deepseek, qwen, glm, kimi, gptoss, minimax (Ollama Cloud); gemini (Gemini API);
                                         groq, openrouter, sambanova, nvidia, cloudflare, cohere, zai (dal 07/11/2026)
      consulto-ai.py tutti "domanda" [--ai deepseek,qwen,glm,gemini] [--giri 2]
      consulto-ai.py elenco               quali AI rispondono adesso e con quale modello
Opzioni: --file F (aggiunge il testo di F alla domanda), --json (uscita completa in JSON). Variabili: CONSULTO_ATTESA
(secondi di attesa), CONSULTO_MAX_TOKENS (lunghezza massima della risposta, per esempio 8000 per un audit).
Chiavi gratuite, mai nel repository: OLLAMA_API_KEY (ollama.com/settings/keys) e GEMINI_API_KEY (aistudio.google.com);
sul PC anche in ~/.config/consulto-ai/ollama e ~/.config/gemini-api/chiave; per gli altri servizi la variabile della voce
in SERVIZI_COMPATIBILI o il file in ~/.config/consulto-ai/ (li raccoglie scripts/aggiungi-chiavi-ai.sh). Si sceglie sempre il modello più nuovo che
il servizio elenca. 🔴 Mai dati personali, sanitari, di minori o riservati: lo script toglie comunque email, telefoni,
codici fiscali, IBAN e numeri di carta. Ollama dichiara di non usare i testi per addestrare i modelli. Per la Gemini API
la pagina dei prezzi dice che sul piano gratuito i testi servono a migliorare i prodotti di Google (le condizioni del
17/10/2025, l'ultima versione leggibile, fanno eccezione per lo Spazio economico europeo, la Svizzera e il Regno Unito);
in ogni caso a Gemini non vanno dati personali o riservati: non riceve i file (--file) di un repository privato, o di cui
non si sa se lo sia, e con «tutti» resta fuori da solo. Uscite: 0 c'è almeno una risposta; 2 errore d'uso; 3 nessuna AI raggiungibile.
"""

import concurrent.futures as cf
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

OLLAMA = os.environ.get("CONSULTO_OLLAMA_URL", "https://ollama.com").rstrip("/")
GEMINI = os.environ.get("CONSULTO_GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
ATTESA = int(os.environ.get("CONSULTO_ATTESA", "240"))   # secondi per una risposta (i modelli grandi pensano a lungo)
# Lunghezza massima della risposta, in token. Senza, ogni servizio usa la sua predefinita, e alcune sono corte: Cloudflare
# Workers AI dà 256 token (pagina del modello @cf/openai/gpt-oss-120b, letta il 07/11/2026), quindi un parere si
# interrompeva a metà. CONSULTO_MAX_TOKENS la imposta per tutti (per esempio 8000 per un audit); «uscita» di un servizio
# vale quando la variabile manca.
MAX_TOKENS = int(os.environ.get("CONSULTO_MAX_TOKENS") or 0)

# Famiglie su Ollama Cloud: nome mostrato e inizio del nome del modello nell'elenco del servizio.
OLLAMA_FAMIGLIE = {
    "deepseek": ("DeepSeek", "deepseek"),
    "qwen": ("Qwen", "qwen"),
    "glm": ("GLM", "glm"),
    "kimi": ("Kimi", "kimi"),
    "gptoss": ("GPT-OSS", "gpt-oss"),
    "minimax": ("MiniMax", "minimax"),
    # Altre famiglie dell'elenco di Ollama Cloud letto il 07/11/2026 con la chiave di Alessandro (Qwen lì non c'era:
    # arriva da Groq, OpenRouter e NVIDIA).
    "mistral": ("Mistral", "mistral-large"),
    "gemma": ("Gemma", "gemma"),
    "nemotron": ("Nemotron", "nemotron"),
    "mimo": ("MiMo", "mimo"),
}
# Altri servizi gratuiti con API compatibile OpenAI (/models, /chat/completions), senza carta di pagamento. Ogni voce:
# nome, servizio, indirizzo (sostituibile con CONSULTO_<SIGLA>_URL), variabile della chiave e file sul PC, modelli
# preferiti dal più forte (espressioni regolari sul nome; il primo che il servizio elenca vince), modelli da escludere,
# richieste insieme, e se il servizio può ricevere testi di repository privati (False quando il piano gratuito usa i
# testi per addestrare o li fa leggere a revisori: come Gemini, resta fuori da solo). Fonti e date in
# memoria/ai-automatiche.md.
NON_CHAT = (r"whisper|embed|guard|tts|orpheus|rerank|moderation|audio|image|ocr|safeguard|transcri|vision|-vl|"
            r"parse|reward|clip|retriev|nemoretriever|flux|sdxl|stable-diffusion|bge|e5-")
# Chiave della voce: sigla, nome, servizio, url ({VARIABILE} si legge dall'ambiente o da ~/.config/consulto-ai/<file>),
# variabile e file della chiave, preferiti, esclusi, solo (il nome deve contenerlo, per esempio «:free»), fissi (modelli
# da usare se il servizio non dà l'elenco), insieme, riservati, sito della chiave.
SERVIZI_COMPATIBILI = [
    # Groq: piano gratuito senza carta (console.groq.com/docs/rate-limits, «Free Plan Limits»); «By default, Groq does
    # not retain customer data for inference requests» (console.groq.com/docs/your-data): può ricevere testi riservati.
    dict(sigla="groq", nome="Groq", servizio="Groq (piano gratuito)", url="https://api.groq.com/openai/v1",
         variabile="GROQ_API_KEY", file=".config/consulto-ai/groq",
         preferiti=[r"gpt-oss-120b", r"kimi", r"qwen", r"llama-4", r"llama-3\.3-70b", r"gpt-oss"], esclusi="compound",
         insieme=2, riservati=True, sito="console.groq.com/keys"),
    # OpenRouter: solo i modelli «:free», 20 al minuto e 50 al giorno senza acquisti (openrouter.ai/docs/api-reference/
    # limits). Dietro ogni modello gratuito c'è un fornitore con regole sue sui dati: niente testi riservati.
    dict(sigla="openrouter", nome="OpenRouter", servizio="OpenRouter (modelli gratuiti)",
         url="https://openrouter.ai/api/v1", variabile="OPENROUTER_API_KEY", file=".config/consulto-ai/openrouter",
         # Elenco dei «:free» letto il 07/11/2026: Nemotron 3 Ultra e Gemma 4 i più forti; DeepSeek, Qwen e gli altri
         # restano in lista per quando tornano gratuiti. Esclusi i modelli piccoli o di prova.
         preferiti=[r"nemotron-3-ultra", r"gemma-4-31b", r"deepseek", r"qwen3", r"kimi", r"glm", r"gpt-oss-120b",
                    r"llama-4", r"llama-3\.3-70b", r"nemotron-3\.5-super", r"gemma"],
         esclusi=r"nano|lightning|lfm|mini|omni|preview|flint|xing", solo=":free", insieme=1, riservati=False, sito="openrouter.ai/settings/keys"),
    # SambaNova: «Free Tier» quando non c'è un metodo di pagamento, 20 al minuto, 20 al giorno, 200.000 token al giorno
    # (docs.sambanova.ai, «Rate limits»). Regole sui dati non verificate: niente testi riservati.
    dict(sigla="sambanova", nome="SambaNova", servizio="SambaNova (piano gratuito)", url="https://api.sambanova.ai/v1",
         variabile="SAMBANOVA_API_KEY", file=".config/consulto-ai/sambanova",
         preferiti=[r"deepseek-v3", r"deepseek", r"gpt-oss-120b", r"llama-4", r"llama-3\.3-70b", r"qwen"], esclusi="",
         insieme=1, riservati=False, sito="cloud.sambanova.ai/apis"),
    # NVIDIA (build.nvidia.com): prova gratuita per prototipi e prove, limiti non pubblicati (circa 40 al minuto secondo
    # il forum). Regole sui dati non verificate: niente testi riservati.
    dict(sigla="nvidia", nome="NVIDIA", servizio="NVIDIA build (prova gratuita)", url="https://integrate.api.nvidia.com/v1",
         variabile="NVIDIA_API_KEY", file=".config/consulto-ai/nvidia",
         preferiti=[r"deepseek-ai/deepseek", r"qwen/qwen3", r"moonshotai/kimi", r"z-ai/glm", r"openai/gpt-oss-120b",
                    r"meta/llama-4", r"llama-3\.3-70b"], esclusi=r"coder|math|nemotron-mini|-8b|-1b|-3b",
         insieme=1, riservati=False, sito="build.nvidia.com (Get API Key)"),
    # Cloudflare Workers AI: 10.000 «Neurons» al giorno gratis (developers.cloudflare.com/workers-ai/platform/pricing);
    # indirizzo con l'ID dell'account (CLOUDFLARE_ACCOUNT_ID). Regole sui dati non verificate: niente testi riservati.
    dict(sigla="cloudflare", nome="Cloudflare", servizio="Cloudflare Workers AI (quota gratuita)",
         url="https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/v1",
         variabile="CLOUDFLARE_API_TOKEN", file=".config/consulto-ai/cloudflare",
         preferiti=[r"gpt-oss-120b", r"llama-4", r"llama-3\.3-70b"], esclusi="",
         fissi=["@cf/openai/gpt-oss-120b", "@cf/meta/llama-3.3-70b-instruct-fp8-fast"], insieme=1, riservati=False,
         uscita=4000, sito="dash.cloudflare.com/profile/api-tokens (permesso Workers AI)"),
    # Cohere: chiave di prova gratuita, 20 al minuto e 1.000 chiamate al mese (docs.cohere.com/docs/rate-limits), non
    # per la produzione. Regole sui dati non verificate: niente testi riservati.
    dict(sigla="cohere", nome="Cohere", servizio="Cohere (chiave di prova)", url="https://api.cohere.ai/compatibility/v1",
         variabile="COHERE_API_KEY", file=".config/consulto-ai/cohere", preferiti=[r"command-a", r"command"],
         esclusi=r"light|nightly|vision|translate", fissi=["command-a-03-2025"], insieme=1, riservati=False,
         sito="dashboard.cohere.com/api-keys"),
    # Z.ai: gratuiti GLM-4.7-Flash e GLM-4.5-Flash (docs.z.ai/guides/overview/pricing). Con la chiave vera, il
    # 07/11/2026, glm-5.3-flash rispondeva 1113 «Insufficient balance» (a pagamento) e i due gratuiti non erano
    # nell'elenco /models: si usano i fissi. Regole sui dati non verificate: niente testi riservati.
    dict(sigla="zai", nome="Z.ai GLM", servizio="Z.ai (modelli Flash gratuiti)", url="https://api.z.ai/api/paas/v4",
         variabile="ZAI_API_KEY", file=".config/consulto-ai/zai", preferiti=[r"^glm-4\.7-flash$", r"^glm-4\.5-flash$"], esclusi=r"v-|vision",
         fissi=["glm-4.7-flash", "glm-4.5-flash"], insieme=1, riservati=False, sito="z.ai/manage-apikey/apikey-list"),
]
COMPATIBILI = {v["sigla"]: {"solo": "", "fissi": [], "uscita": 0, **v} for v in SERVIZI_COMPATIBILI}
TUTTE = list(OLLAMA_FAMIGLIE) + ["gemini"] + list(COMPATIBILI)
# Quelle che rispondevano con le chiavi vere il 07/11/2026, più DeepSeek e GLM per quando Ollama torna gratuito.
PREDEFINITE_TUTTI = ["gemini", "openrouter", "cloudflare", "zai", "cohere", "deepseek", "glm"]
# Chi non riceve testi di repository privati (file con --file): Gemini e i servizi con «riservati» False.
SENZA_RISERVATI = {"gemini"} | {k for k, v in COMPATIBILI.items() if not v["riservati"]}

SISTEMA = (
    "Sei {nome} e fai parte della squadra di intelligenze artificiali che lavora per Alessandro Cuollo: siti, comunicazione "
    "e documenti della Protezione Civile di Genzano di Roma, della Misericordia di Ariccia, di Cooprimavera, dell'ARI "
    "Castelli Romani e dell'AGESCI Genzano 2. Rispondi in italiano corretto e chiaro, senza preamboli. Il tuo è un parere "
    "che un'altra intelligenza artificiale verificherà prima di usarlo: non inventare dati, nomi, numeri, date, norme o "
    "link; quando non sei sicuro dillo e indica come verificare su una fonte primaria."
)

# Dati personali che non devono mai uscire verso un servizio esterno.
DATI_PERSONALI = [
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[email tolta]"),
    (re.compile(r"\b[A-Z]{6}\d{2}[A-EHLMPRST]\d{2}[A-Z]\d{3}[A-Z]\b", re.I), "[codice fiscale tolto]"),
    (re.compile(r"\bIT\d{2}[A-Z]\d{10}[0-9A-Z]{12}\b", re.I), "[IBAN tolto]"),
    (re.compile(r"(?<![\d.,])(?:\d[ -]?){12,18}\d(?![\d.,])"), "[numero tolto]"),
    (re.compile(r"(?<![\w+])(?:\+39[\s.-]?)?3\d{2}[\s.-]?\d{3}[\s.-]?\d{3,4}(?!\d)"), "[telefono tolto]"),
    # fissi: 06 9364 1234, 069364123, +39 06-9364-1234 (niente barre né punti fra le cifre: sono date)
    (re.compile(r"(?<![\w+])(?:\+39[\s.-]?)?0\d{1,3}(?:[ -]?\d){5,9}(?!\d)"), "[telefono tolto]"),
]


class Irraggiungibile(Exception):
    """L'AI non ha risposto (chiave mancante, quota finita, servizio fermo): si va avanti con le altre."""


def togli_dati_personali(testo):
    tolti = 0
    for regola, sostituto in DATI_PERSONALI:
        testo, n = regola.subn(sostituto, testo)
        tolti += n
    return testo, tolti


def file_riservato(percorso):
    """True se il file sta in un repository GitHub privato, oppure se non si riesce a saperlo: nel dubbio, riservato."""
    try:
        url = subprocess.run(["git", "-C", str(pathlib.Path(percorso).resolve().parent), "remote", "get-url", "origin"],
                             capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return True
    m = (re.search(r"github\.com[:/]+([^/]+/[^/]+?)(?:\.git)?/?$", url)
         or re.search(r"/git/([^/]+/[^/]+?)(?:\.git)?/?$", url))
    if not m:   # fuori da un repository GitHub riconoscibile
        return True
    try:   # con gh (PC e sessioni): risponde anche per i repository privati
        r = subprocess.run(["gh", "api", f"repos/{m[1]}", "--jq", ".private"], capture_output=True, text=True,
                           timeout=30)
        if r.returncode == 0 and r.stdout.strip() in ("true", "false"):
            return r.stdout.strip() == "true"
    except (OSError, subprocess.SubprocessError):
        pass
    try:   # senza gh: un repository privato, senza credenziali, non si vede (404)
        richiesta = urllib.request.Request(f"https://api.github.com/repos/{m[1]}",
                                           headers={"Accept": "application/vnd.github+json", "User-Agent": "consulto-ai"})
        with urllib.request.urlopen(richiesta, timeout=30) as r:
            return json.loads(r.read() or b"{}").get("private") is not False
    except Exception:
        return True


def leggi_chiave(variabile, *file_pc):
    valore = os.environ.get(variabile, "").strip()
    for f in file_pc:
        p = pathlib.Path.home() / f
        if not valore and p.exists():
            valore = p.read_text().strip()
    return valore


def http_json(url, intestazioni, corpo=None, attesa=ATTESA):
    dati = json.dumps(corpo).encode() if corpo is not None else None
    richiesta = urllib.request.Request(url, data=dati, headers={**intestazioni, "Content-Type": "application/json"})
    with urllib.request.urlopen(richiesta, timeout=attesa) as r:
        return json.loads(r.read() or b"{}")


def numeri(testo):
    return tuple(int(x) for x in re.findall(r"\d+", testo))


def ordina_modelli(nomi, prefisso):
    """Dal più nuovo: versione nel nome (prima dei due punti), poi «pro» prima di flash/mini/lite, poi il più grande."""
    leggeri = re.compile(r"flash|mini|lite|air|small|nano|tiny")

    def chiave(nome):
        base, _, taglia = nome.partition(":")
        resto = base[len(prefisso):]
        qualita = 1 if "pro" in resto else (-1 if leggeri.search(resto) else 0)
        return (numeri(resto), qualita, numeri(taglia))
    return sorted((n for n in nomi if n.lower().startswith(prefisso)), key=chiave, reverse=True)


class Ollama:
    nome_servizio = "Ollama Cloud"

    def __init__(self):
        self.chiave = leggi_chiave("OLLAMA_API_KEY", ".config/consulto-ai/ollama")
        self.blocco = threading.Semaphore(1)   # il piano gratuito ammette una richiesta per volta
        self._modelli = None

    def intestazioni(self):
        return {"Authorization": f"Bearer {self.chiave}"}

    def modelli(self):
        if not self.chiave:
            raise Irraggiungibile("manca OLLAMA_API_KEY (chiave gratuita di ollama.com)")
        if self._modelli is None:
            try:
                dati = http_json(f"{OLLAMA}/api/tags", self.intestazioni(), attesa=60)
            except (urllib.error.URLError, TimeoutError) as e:
                raise Irraggiungibile(f"elenco dei modelli non letto ({getattr(e, 'code', e)})")
            self._modelli = [m.get("name") or m.get("model") for m in dati.get("models", []) if m.get("name") or m.get("model")]
        return self._modelli

    def candidati(self, famiglia):
        prefisso = OLLAMA_FAMIGLIE[famiglia][1]
        scelti = ordina_modelli(self.modelli(), prefisso)
        if not scelti:
            raise Irraggiungibile(f"nessun modello «{prefisso}» nell'elenco di Ollama Cloud")
        return scelti

    def chiedi(self, famiglia, sistema, domanda):
        errori = []
        for modello in self.candidati(famiglia)[:3]:
            for tentativo in range(2):
                try:
                    with self.blocco:
                        dati = http_json(f"{OLLAMA}/api/chat", self.intestazioni(), {
                            "model": modello, "stream": False,
                            "options": {"temperature": 0.3, **({"num_predict": MAX_TOKENS} if MAX_TOKENS else {})},
                            "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": domanda}],
                        })
                    testo = ((dati.get("message") or {}).get("content") or "").strip()
                    if testo:
                        return modello, testo
                    errori.append(f"{modello}: risposta vuota")
                    break
                except urllib.error.HTTPError as e:
                    errori.append(f"{modello}: {e.code}")
                    if e.code == 401:
                        raise Irraggiungibile("chiave di Ollama Cloud non valida (401)")
                    if e.code == 429 and tentativo == 0:
                        time.sleep(20)   # quota del minuto o richiesta già in corso: un secondo tentativo
                        continue
                    break   # 402/403 modello fuori dal piano, 404 sparito, 5xx: si passa al modello successivo
                except (urllib.error.URLError, TimeoutError):
                    errori.append(f"{modello}: nessuna risposta in {ATTESA} s")
                    break
        raise Irraggiungibile("; ".join(errori) or "nessun modello ha risposto")


class Gemini:
    nome_servizio = "Gemini API gratuita"

    def __init__(self):
        self.chiave = leggi_chiave("GEMINI_API_KEY", ".config/gemini-api/chiave")
        self.blocco = threading.Semaphore(2)
        self._modelli = None

    def intestazioni(self):
        return {"x-goog-api-key": self.chiave}   # la chiave mai nell'indirizzo

    def candidati(self, famiglia="gemini"):
        if os.environ.get("GEMINI_MODELLO"):
            return [os.environ["GEMINI_MODELLO"]]
        if not self.chiave:
            raise Irraggiungibile("manca GEMINI_API_KEY (chiave gratuita di aistudio.google.com)")
        if self._modelli is None:
            nomi, token = [], ""
            try:
                while True:
                    pagina = http_json(f"{GEMINI}/models?pageSize=200{'&pageToken=' + token if token else ''}",
                                       self.intestazioni(), attesa=60)
                    nomi += [m["name"].split("/")[-1] for m in pagina.get("models", [])]
                    token = pagina.get("nextPageToken", "")
                    if not token:
                        break
            except urllib.error.HTTPError as e:
                raise Irraggiungibile(f"elenco dei modelli non letto ({e.code})")
            except (urllib.error.URLError, TimeoutError) as e:
                raise Irraggiungibile(f"elenco dei modelli non letto ({e})")
            # Solo i «flash» numerati: sono quelli del piano gratuito (il modello più grande via API è a pagamento).
            flash = [n for n in nomi if re.fullmatch(r"gemini-\d+(?:\.\d+)?-flash", n)]
            self._modelli = sorted(flash, key=numeri, reverse=True)
        if not self._modelli:
            raise Irraggiungibile("nessun modello flash nell'elenco della Gemini API")
        return self._modelli

    def chiedi(self, famiglia, sistema, domanda):
        modelli, errori = self.candidati(), []
        for giro in range(2):   # il piano gratuito è spesso occupato: tutti i modelli, poi un secondo giro dopo una pausa
            if giro:
                time.sleep(30)
            for modello in modelli:
                try:
                    with self.blocco:
                        dati = http_json(f"{GEMINI}/models/{modello}:generateContent", self.intestazioni(), {
                            "systemInstruction": {"parts": [{"text": sistema}]},
                            "contents": [{"role": "user", "parts": [{"text": domanda}]}],
                            "generationConfig": {"temperature": 0.3,
                                                 **({"maxOutputTokens": MAX_TOKENS} if MAX_TOKENS else {})},
                        }, attesa=min(ATTESA, 120))
                    testo = "".join(p.get("text", "") for c in dati.get("candidates", [])
                                    for p in (c.get("content") or {}).get("parts", [])).strip()
                    if testo:
                        return modello, testo
                    errori.append(f"{modello}: risposta vuota")
                except urllib.error.HTTPError as e:
                    errori.append(f"{modello}: {e.code}")
                    if e.code in (400, 401, 403):
                        raise Irraggiungibile(f"la Gemini API rifiuta la richiesta ({e.code})")
                except (urllib.error.URLError, TimeoutError):
                    errori.append(f"{modello}: nessuna risposta")
        raise Irraggiungibile("; ".join(errori) or "nessun modello ha risposto")


def leggi_errore(e):
    try:
        return e.read().decode(errors="replace")[:500]
    except Exception:
        return ""


class Compatibile:
    """Un servizio gratuito con API compatibile OpenAI (Groq, Mistral, OpenRouter, …)."""

    def __init__(self, voce):
        self.v = voce
        self.nome_servizio = voce["servizio"]
        self.url = os.environ.get(f"CONSULTO_{voce['sigla'].upper()}_URL", voce["url"]).rstrip("/")
        self.manca = ""
        for nome in re.findall(r"\{(\w+)\}", self.url):   # per esempio l'ID dell'account di Cloudflare
            valore = leggi_chiave(nome, f".config/consulto-ai/{nome.lower()}")
            if not valore:
                self.manca = nome
            self.url = self.url.replace("{" + nome + "}", valore)
        self.chiave = leggi_chiave(voce["variabile"], voce["file"])
        self.blocco = threading.Semaphore(voce["insieme"])
        self._modelli = None

    def intestazioni(self):
        return {"Authorization": f"Bearer {self.chiave}", "User-Agent": "consulto-ai"}

    def candidati(self, famiglia=None):
        if not self.chiave:
            raise Irraggiungibile(f"manca {self.v['variabile']} (chiave gratuita da {self.v['sito']})")
        if self.manca:
            raise Irraggiungibile(f"manca {self.manca}")
        if self._modelli is None:
            try:
                dati = http_json(f"{self.url}/models", self.intestazioni(), attesa=60)
                elenco_dati = dati.get("data", []) if isinstance(dati, dict) else dati
                nomi = [m.get("id") for m in elenco_dati if isinstance(m, dict) and m.get("id")]
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    raise Irraggiungibile(f"chiave di {self.nome_servizio} non valida (401)")
                if not self.v["fissi"]:
                    raise Irraggiungibile(f"elenco dei modelli non letto ({e.code})")
                nomi = []
            except (urllib.error.URLError, TimeoutError, ValueError) as e:
                if not self.v["fissi"]:
                    raise Irraggiungibile(f"elenco dei modelli non letto ({e})")
                nomi = []
            if self.v["solo"]:
                nomi = [n for n in nomi if self.v["solo"] in n]
            # I modelli gratuiti dichiarati nella pagina dei prezzi valgono anche se l'elenco del servizio non li mostra.
            nomi += [n for n in self.v["fissi"] if n not in nomi]
            escludi = re.compile(f"{NON_CHAT}|{self.v['esclusi']}" if self.v["esclusi"] else NON_CHAT, re.I)
            nomi = [n for n in nomi if not escludi.search(n)]
            scelti = []
            for regola in self.v["preferiti"]:
                trovati = [n for n in nomi if re.search(regola, n, re.I) and n not in scelti]
                scelti += sorted(trovati, key=lambda n: (numeri(n), len(n)), reverse=True)
            self._modelli = scelti
        if not self._modelli:
            raise Irraggiungibile(f"nessun modello adatto nell'elenco di {self.nome_servizio}")
        return self._modelli

    def chiedi(self, famiglia, sistema, domanda):
        errori = []
        for modello in self.candidati()[:3]:
            for tentativo in range(2):
                try:
                    with self.blocco:
                        dati = http_json(f"{self.url}/chat/completions", self.intestazioni(), {
                            "model": modello, "temperature": 0.3, "stream": False,
                            **({"max_tokens": MAX_TOKENS or self.v["uscita"]} if MAX_TOKENS or self.v["uscita"] else {}),
                            "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": domanda}],
                        })
                    scelte = dati.get("choices") or [{}]
                    contenuto = (scelte[0].get("message") or {}).get("content") or ""
                    if isinstance(contenuto, list):   # alcuni servizi rispondono a pezzi
                        contenuto = "".join(p.get("text", "") for p in contenuto if isinstance(p, dict))
                    testo = re.sub(r"<think>.*?</think>", "", contenuto, flags=re.S).strip()
                    if testo:
                        return modello, testo
                    errori.append(f"{modello}: risposta vuota")
                    break
                except urllib.error.HTTPError as e:
                    errori.append(f"{modello}: {e.code}")
                    if e.code == 401:
                        raise Irraggiungibile(f"chiave di {self.nome_servizio} non valida (401)")
                    if e.code == 429 and tentativo == 0 and "1113" not in leggi_errore(e):   # 1113 Z.ai: a pagamento
                        time.sleep(20)
                        continue
                    break   # 402/403 fuori dal piano, 404 sparito, 413 testo troppo lungo, 5xx: modello successivo
                except (urllib.error.URLError, TimeoutError):
                    errori.append(f"{modello}: nessuna risposta in {ATTESA} s")
                    break
        raise Irraggiungibile("; ".join(errori) or "nessun modello ha risposto")


class Squadra:
    def __init__(self):
        self.ollama, self.gemini = Ollama(), Gemini()
        self.altri = {k: Compatibile(v) for k, v in COMPATIBILI.items()}

    def servizio(self, ai):
        if ai in self.altri:
            return self.altri[ai]
        return self.gemini if ai == "gemini" else self.ollama

    def nome(self, ai):
        if ai in COMPATIBILI:
            return COMPATIBILI[ai]["nome"]
        return "Gemini" if ai == "gemini" else OLLAMA_FAMIGLIE[ai][0]

    def chiedi(self, ai, domanda):
        modello, testo = self.servizio(ai).chiedi(ai, SISTEMA.format(nome=self.nome(ai)), domanda)
        return {"ai": ai, "nome": self.nome(ai), "modello": modello, "servizio": self.servizio(ai).nome_servizio,
                "testo": testo}


def taglia(testo, massimo=6000):
    return testo if len(testo) <= massimo else testo[:massimo] + "\n[…tagliato]"


def giro_di_risposte(squadra, ai_elenco, prompt_per):
    risposte, mancate = {}, {}
    with cf.ThreadPoolExecutor(max_workers=max(1, len(ai_elenco))) as ex:
        futuri = {ex.submit(squadra.chiedi, ai, prompt_per(ai)): ai for ai in ai_elenco}
        for f in cf.as_completed(futuri):
            ai = futuri[f]
            try:
                risposte[ai] = f.result()
            except Irraggiungibile as e:
                mancate[ai] = str(e)
    return risposte, mancate


def consulto(squadra, domanda, ai_elenco, giri):
    """Primo giro: ognuna risponde da sola. Giri successivi: ognuna legge le altre e si corregge. Poi la sintesi."""
    storia = []
    risposte, mancate = giro_di_risposte(squadra, ai_elenco, lambda ai: domanda)
    storia.append(risposte)
    for _ in range(1, giri):
        if len(risposte) < 2:
            break

        def revisione(ai, attuali=risposte):
            altre = "\n\n".join(f"[{r['nome']}]\n{taglia(r['testo'])}" for a, r in attuali.items() if a != ai)
            return (f"Domanda di partenza:\n{domanda}\n\nLa tua risposta di prima:\n{taglia(attuali[ai]['testo'])}\n\n"
                    f"Le risposte delle altre intelligenze artificiali della squadra:\n{altre}\n\n"
                    "Rileggi tutto come un revisore severo. Indica gli errori che trovi nelle altre risposte e nella tua, "
                    "dove sei d'accordo e dove no, poi scrivi la tua risposta migliorata. Breve.")
        nuove, perse = giro_di_risposte(squadra, list(risposte), revisione)
        mancate.update({a: m for a, m in perse.items() if a not in mancate})
        risposte = {**risposte, **nuove}
        storia.append(nuove)
    sintesi = None
    if len(risposte) >= 2:
        tutte = "\n\n".join(f"[{r['nome']}, {r['modello']}]\n{taglia(r['testo'])}" for r in risposte.values())
        richiesta = (f"Fai da moderatore. Domanda:\n{domanda}\n\nRisposte finali della squadra:\n{tutte}\n\n"
                     "Scrivi: 1) la risposta consigliata; 2) i punti su cui concordano tutte; 3) i disaccordi e chi ha "
                     "ragione secondo te, con il motivo; 4) che cosa va verificato su una fonte primaria prima di usarla.")
        for moderatore in (["gemini"] if "gemini" in risposte else []) + [a for a in risposte if a != "gemini"]:
            try:
                sintesi = squadra.chiedi(moderatore, richiesta)
                break
            except Irraggiungibile as e:
                mancate.setdefault(f"sintesi-{moderatore}", str(e))
    return {"risposte": risposte, "storia": storia, "sintesi": sintesi, "mancate": mancate}


def elenco(squadra, prova=False):
    """Chi risponde. Con prova=True una domanda minima per servizio (non per famiglia): l'elenco dei modelli da solo
    non basta, perché Ollama e SambaNova lo danno anche quando ogni domanda risponde 402 (07/11/2026)."""
    righe, esito_servizio = [], {}
    for ai in TUTTE:
        try:
            servizio = squadra.servizio(ai)
            modello = servizio.candidati(ai)[0]
            if prova:
                if id(servizio) not in esito_servizio or (ai in OLLAMA_FAMIGLIE and esito_servizio[id(servizio)] is None):
                    try:
                        modello, _ = servizio.chiedi(ai, "Rispondi in una parola.", "Rispondi solo: pronto")
                        esito_servizio[id(servizio)] = None
                    except Irraggiungibile as e:
                        esito_servizio[id(servizio)] = str(e)
                        if "402" in str(e) and ai in OLLAMA_FAMIGLIE:   # un 402 vale per tutto il servizio
                            esito_servizio[id(servizio)] = "a pagamento (402)"
                if esito_servizio[id(servizio)]:
                    raise Irraggiungibile(esito_servizio[id(servizio)])
            righe.append(f"- {squadra.nome(ai)} ({ai}): {modello} · {servizio.nome_servizio}")
        except Irraggiungibile as e:
            righe.append(f"- {squadra.nome(ai)} ({ai}): non raggiungibile ({e})")
        except KeyError:
            pass
    return "\n".join(righe)


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("chi", help=", ".join(TUTTE) + ", tutti oppure elenco")
    p.add_argument("domanda", nargs="?", default="")
    p.add_argument("--file", action="append", default=[], help="aggiunge il testo di un file alla domanda")
    p.add_argument("--ai", default="", help="con «tutti»: le AI da far parlare, separate da virgole")
    p.add_argument("--giri", type=int, default=2, help="con «tutti»: giri di risposte (1 = solo pareri indipendenti)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--prova", action="store_true", help="con «elenco»: una domanda minima per servizio")
    a = p.parse_args(argv)
    chi = a.chi.lower().replace("-", "")
    squadra = Squadra()
    if chi == "elenco":
        print(elenco(squadra, prova=a.prova))
        return 0
    if chi not in TUTTE + ["tutti"]:
        print(f"AI sconosciuta: {a.chi}. Si può chiedere a: {', '.join(TUTTE)}, oppure «tutti» o «elenco».")
        return 2
    domanda = a.domanda
    for f in a.file:
        domanda += f"\n\n--- {f} ---\n" + pathlib.Path(f).read_text(errors="replace")
    if not domanda.strip():
        print("Manca la domanda.")
        return 2
    riservati = [f for f in a.file if file_riservato(f)]
    def perche(chi_resta_fuori):
        return (f"a {chi_resta_fuori} non vanno dati personali o riservati, e "
                + (f"{riservati[0]} è in un repository privato, o non si sa se lo sia" if len(riservati) == 1
                   else f"{', '.join(riservati)} sono in repository privati, o non si sa se lo siano"))
    if riservati and chi in SENZA_RISERVATI:
        print(f"{squadra.nome(chi)} non riceve {'questo file' if len(riservati) == 1 else 'questi file'}: "
              f"{perche(squadra.nome(chi))}. Chiedi a deepseek, qwen, glm o kimi, oppure a «tutti», che lo lascia "
              "fuori da solo.")
        return 2
    domanda, tolti = togli_dati_personali(domanda)
    if tolti:
        print(f"[tolti {tolti} dati personali dalla domanda prima di inviarla]", file=sys.stderr)

    if chi != "tutti":
        try:
            r = squadra.chiedi(chi, domanda)
        except Irraggiungibile as e:
            print(f"{squadra.nome(chi)} non raggiungibile ora: {e}")
            return 3
        print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else f"[{r['modello']} · {r['servizio']}]\n{r['testo']}")
        return 0

    scelte = [x.strip().lower() for x in a.ai.split(",") if x.strip()] or PREDEFINITE_TUTTI
    sconosciute = [x for x in scelte if x not in TUTTE]
    if sconosciute:
        print(f"AI sconosciute: {', '.join(sconosciute)}")
        return 2
    fuori = [x for x in scelte if x in SENZA_RISERVATI] if riservati else []
    if fuori:
        scelte = [x for x in scelte if x not in fuori]
        nomi_fuori = ", ".join(squadra.nome(x) for x in fuori)
        print(f"[{nomi_fuori} {'resta' if len(fuori) == 1 else 'restano'} fuori dal consulto: {perche(nomi_fuori)}]",
              file=sys.stderr)
        if not scelte:
            print(f"Senza {nomi_fuori} non resta nessuna AI: scegli anche deepseek, qwen, glm o kimi.")
            return 2
    esito = consulto(squadra, domanda, scelte, max(1, a.giri))
    if a.json:
        print(json.dumps(esito, ensure_ascii=False, indent=1))
        return 0 if esito["risposte"] else 3
    if not esito["risposte"]:
        print("Nessuna AI raggiungibile ora: " + "; ".join(f"{squadra.nome(k)}: {v}" for k, v in esito["mancate"].items()))
        return 3
    pezzi = [f"## Consulto fra {len(esito['risposte'])} AI ({max(1, a.giri)} giri)"]
    for r in esito["risposte"].values():
        pezzi.append(f"### {r['nome']} ({r['modello']} · {r['servizio']})\n{r['testo']}")
    if esito["sintesi"]:
        s = esito["sintesi"]
        pezzi.append(f"### Sintesi del moderatore: {s['nome']} ({s['modello']})\n{s['testo']}")
    if esito["mancate"]:
        pezzi.append("Non hanno risposto: " + "; ".join(f"{k}: {v}" for k, v in esito["mancate"].items()))
    print("\n\n".join(pezzi))
    return 0


if __name__ == "__main__":
    sys.exit(main())
