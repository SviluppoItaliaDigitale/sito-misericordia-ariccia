#!/usr/bin/env python3
"""ricevitore.py — Riceve dal browser l'audio di NotebookLM e lo salva sul PC.

Chrome chiede dove salvare ogni download e quella finestra di sistema non si
può comandare: la pagina di NotebookLM legge l'audio e lo invia qui. Ascolta
solo su 127.0.0.1, accetta solo l'origine notebook.google.com e scrive solo in
~/podcast-lavoro-misericordia/<id>/audio.m4a. Si chiude dopo il primo file ricevuto
(o dopo --attesa secondi). Uso: ricevitore.py ID [--porta 8798] [--attesa 900]
"""
from __future__ import annotations

import argparse
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ORIGINE = "https://notebook.google.com"
MAX_BYTE = 300 * 1024 * 1024


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--porta", type=int, default=8798)
    ap.add_argument("--attesa", type=int, default=900)
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9-]+", a.id):
        print("ERRORE: id non valido", file=sys.stderr)
        return 1
    dest = Path.home() / "podcast-lavoro-misericordia" / a.id / "audio.m4a"
    dest.parent.mkdir(parents=True, exist_ok=True)
    fatto = threading.Event()

    class Gestore(BaseHTTPRequestHandler):
        def _intestazioni(self) -> None:
            self.send_header("Access-Control-Allow-Origin", ORIGINE)
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Private-Network", "true")

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self._intestazioni()
            self.end_headers()

        def do_POST(self) -> None:  # noqa: N802
            lung = int(self.headers.get("Content-Length", "0"))
            if self.headers.get("Origin") != ORIGINE or not 0 < lung <= MAX_BYTE:
                self.send_response(403)
                self._intestazioni()
                self.end_headers()
                return
            dati = self.rfile.read(lung)
            dest.write_bytes(dati)
            self.send_response(200)
            self._intestazioni()
            self.end_headers()
            self.wfile.write(f"salvati {len(dati)} byte".encode())
            fatto.set()

        def log_message(self, format, *args) -> None:  # noqa: A002
            pass

    server = HTTPServer(("127.0.0.1", a.porta), Gestore)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"In ascolto su 127.0.0.1:{a.porta} per {dest}", flush=True)
    ok = fatto.wait(a.attesa)
    server.shutdown()
    print(f"RICEVUTO {dest} ({dest.stat().st_size} byte)" if ok else "Nessun file ricevuto", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
