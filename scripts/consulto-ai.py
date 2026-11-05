#!/usr/bin/env python3
"""Consulto fra le intelligenze artificiali gratuite della squadra: il parere di una sola AI, oppure le AI che parlano
fra loro («tutti»: rispondono, leggono le risposte delle altre, si correggono, e una sintesi dice dove concordano e dove no).

Uso:  consulto-ai.py <ai> "domanda"      ai: deepseek, qwen, glm, kimi, gptoss, minimax (Ollama Cloud); gemini (Gemini API)
      consulto-ai.py tutti "domanda" [--ai deepseek,qwen,glm,gemini] [--giri 2]
      consulto-ai.py elenco               quali AI rispondono adesso e con quale modello
Opzioni: --file F (aggiunge il testo di F alla domanda), --json (uscita completa in JSON).
Chiavi gratuite, mai nel repository: OLLAMA_API_KEY (ollama.com/settings/keys) e GEMINI_API_KEY (aistudio.google.com);
sul PC anche in ~/.config/consulto-ai/ollama e ~/.config/gemini-api/chiave. Si sceglie sempre il modello più nuovo che
il servizio elenca. 🔴 Mai dati personali, sanitari, di minori o riservati: lo script toglie comunque email, telefoni,
codici fiscali, IBAN e numeri di carta. Ollama dichiara di non usare i testi per addestrare i modelli; il piano gratuito
della Gemini API sì. Uscite: 0 c'è almeno una risposta; 2 errore d'uso; 3 nessuna AI raggiungibile.
"""

import concurrent.futures as cf
import json
import os
import pathlib
import re
import sys
import threading
import time
import urllib.error
import urllib.request

OLLAMA = os.environ.get("CONSULTO_OLLAMA_URL", "https://ollama.com").rstrip("/")
GEMINI = os.environ.get("CONSULTO_GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
ATTESA = int(os.environ.get("CONSULTO_ATTESA", "240"))   # secondi per una risposta (i modelli grandi pensano a lungo)

# Famiglie su Ollama Cloud: nome mostrato e inizio del nome del modello nell'elenco del servizio.
OLLAMA_FAMIGLIE = {
    "deepseek": ("DeepSeek", "deepseek"),
    "qwen": ("Qwen", "qwen"),
    "glm": ("GLM", "glm"),
    "kimi": ("Kimi", "kimi"),
    "gptoss": ("GPT-OSS", "gpt-oss"),
    "minimax": ("MiniMax", "minimax"),
}
TUTTE = list(OLLAMA_FAMIGLIE) + ["gemini"]
PREDEFINITE_TUTTI = ["deepseek", "qwen", "glm", "gemini"]

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
                            "model": modello, "stream": False, "options": {"temperature": 0.3},
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
                            "generationConfig": {"temperature": 0.3},
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


class Squadra:
    def __init__(self):
        self.ollama, self.gemini = Ollama(), Gemini()

    def servizio(self, ai):
        return self.gemini if ai == "gemini" else self.ollama

    def nome(self, ai):
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


def elenco(squadra):
    righe = []
    for ai in TUTTE:
        try:
            modello = squadra.servizio(ai).candidati(ai)[0]
            righe.append(f"- {squadra.nome(ai)} ({ai}): {modello} · {squadra.servizio(ai).nome_servizio}")
        except Irraggiungibile as e:
            righe.append(f"- {squadra.nome(ai)} ({ai}): non raggiungibile ({e})")
        except KeyError:
            pass
    return "\n".join(righe)


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("chi", help="deepseek, qwen, glm, kimi, gptoss, minimax, gemini, tutti oppure elenco")
    p.add_argument("domanda", nargs="?", default="")
    p.add_argument("--file", action="append", default=[], help="aggiunge il testo di un file alla domanda")
    p.add_argument("--ai", default="", help="con «tutti»: le AI da far parlare, separate da virgole")
    p.add_argument("--giri", type=int, default=2, help="con «tutti»: giri di risposte (1 = solo pareri indipendenti)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    chi = a.chi.lower().replace("-", "")
    squadra = Squadra()
    if chi == "elenco":
        print(elenco(squadra))
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
