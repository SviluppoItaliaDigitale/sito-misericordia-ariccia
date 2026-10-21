#!/usr/bin/env python3
"""Prova dei tentativi di scarica() (scripts/liturgia_cei.py), sui controlli di ogni PR e dopo ogni deploy.

Un server locale risponde come le fonti delle letture nei guasti del 21/10/2026 (403 senza testo
dal feed Evangelizo, connessione chiusa dalla pagina CEI) e la prova controlla che:
  1. un errore passeggero seguito da una risposta buona non fermi lo scarico, con attese crescenti
     (3 e 6 secondi; qui le attese si registrano, non si aspetta davvero);
  2. un 404 arrivi subito a chi chiama, senza altri tentativi;
  3. un 403 che non passa arrivi a chi chiama dopo cinque tentativi (attese 3, 6, 12, 24);
  4. liturgia_cei.py (Liturgia del giorno) e letture.py (Parola della domenica) usino scarica().
Esce con 1 se un caso non va come deve. Solo libreria standard. Uso: prova_letture.py
"""
import http.server
import importlib.util
import socket
import sys
import threading
import urllib.error
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT))
import liturgia_cei  # noqa: E402

risposte, richieste, attese = {}, {}, []


class Fonte(http.server.BaseHTTPRequestHandler):
    """Per ogni percorso consuma in ordine le risposte della sua lista; l'ultima resta per sempre."""

    def do_GET(self):
        richieste[self.path] = richieste.get(self.path, 0) + 1
        coda = risposte[self.path]
        codice = coda.pop(0) if len(coda) > 1 else coda[0]
        if codice == "chiudi":  # connessione chiusa senza risposta
            self.close_connection = True
            self.connection.shutdown(socket.SHUT_RDWR)
            return
        corpo = b"ok" if codice == 200 else b""
        self.send_response(codice)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *argomenti):
        pass


class Server(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        pass  # la connessione chiusa apposta non è un errore della prova


def codice_errore(funzione):
    """Codice HTTP dell'errore sollevato da funzione(), o None se non solleva nulla."""
    try:
        funzione()
    except urllib.error.HTTPError as e:
        return e.code
    return None


def main():
    server = Server(("127.0.0.1", 0), Fonte)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    liturgia_cei.time.sleep = attese.append  # si registrano le attese invece di aspettare
    spec = importlib.util.spec_from_file_location("letture", SCRIPT / "parola-domenica" / "letture.py")
    letture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(letture)

    def passeggero():
        risposte["/passeggero"], attese[:] = [403, "chiudi", 200], []
        testo = liturgia_cei.scarica(base + "/passeggero", "prova")
        return testo == "ok" and richieste["/passeggero"] == 3 and attese == [3, 6], \
            f"{richieste['/passeggero']} richieste, attese {attese}"

    def sparito():
        risposte["/sparito"] = [404]
        codice = codice_errore(lambda: liturgia_cei.scarica(base + "/sparito", "prova"))
        return codice == 404 and richieste["/sparito"] == 1, f"errore {codice}, {richieste['/sparito']} richieste"

    def sempre403():
        risposte["/sempre403"], attese[:] = [403], []
        codice = codice_errore(lambda: liturgia_cei.scarica(base + "/sempre403", "prova"))
        return codice == 403 and richieste["/sempre403"] == 5 and attese == [3, 6, 12, 24], \
            f"errore {codice}, {richieste['/sempre403']} richieste, attese {attese}"

    def pagina_cei():
        risposte["/cei?d=20261025"] = ["chiudi", 200]
        liturgia_cei.URL = base + "/cei?d={d}"
        righe = liturgia_cei.righe_pagina("20261025")
        return righe == ["ok"] and richieste["/cei?d=20261025"] == 2, f"{richieste['/cei?d=20261025']} richieste"

    def feed_evangelizo():
        risposte["/feed"] = [403, 200]
        testo = letture.leggi(base + "/feed")
        return testo == "ok" and richieste["/feed"] == 2, f"{richieste['/feed']} richieste"

    casi = [("403 e connessione chiusa, poi 200: lo scarico riesce, con attese crescenti", passeggero),
            ("404: arriva subito a chi chiama, senza altri tentativi", sparito),
            ("403 che non passa: arriva a chi chiama dopo cinque tentativi", sempre403),
            ("liturgia_cei.py riprova sulla pagina CEI", pagina_cei),
            ("letture.py riprova sul feed Evangelizo", feed_evangelizo)]
    falliti = 0
    for nome, caso in casi:
        try:
            ok, dettaglio = caso()
        except Exception as e:  # noqa: BLE001  un errore inatteso è un caso non superato
            ok, dettaglio = False, f"errore inatteso: {e!r}"
        print(f"{'✅' if ok else '❌'} {nome} ({dettaglio})")
        falliti += not ok
    server.shutdown()
    print("Tutti i casi superati." if not falliti else f"Casi non superati: {falliti}")
    return 1 if falliti else 0


if __name__ == "__main__":
    sys.exit(main())
