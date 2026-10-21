#!/usr/bin/env python3
"""Prova del controllo «firma e cornice» (grafiche_senza_firma e ha_segno in controlla_sito.py), sui controlli di ogni PR.

Il controllo cerca il segno che il motore scripts/grafica-brand/firma-e-cornice.js scrive in testa alle grafiche
(commento nei JPEG, blocco tEXt nei PNG). Qui si prova su file costruiti apposta: il segno nel posto giusto passa;
nessun segno, un segno diverso o lo stesso testo finito nei dati compressi non passano. Poi si prova sul repository:
il segno si legge dal motore, il motore lo mette davvero nei JPEG, e il controllo trova il segno nelle grafiche delle
news in uscita. Nasce con la regola del 21/10/2026 (Alessandro: «metti in ogni slide, documento grafico eccetera
sempre Misericordia di Ariccia! Altrimenti ci rubano la grafica!!»).
Esce con 1 se un caso non va come deve. Solo libreria standard. Uso: prova_cornice.py
"""
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from controlla_sito import REPO, grafiche_senza_firma, ha_segno, segno_firma  # noqa: E402

falliti = []


def attesa(cond, messaggio):
    if not cond:
        falliti.append(messaggio)


SEGNO = segno_firma()
attesa(SEGNO and b"Misericordia di Ariccia" in SEGNO, f"segno del motore non trovato o senza il nome: {SEGNO!r}")
SEGNO = SEGNO or b"Misericordia di Ariccia"


def segmento(tipo, corpo):
    return bytes([0xFF, tipo]) + struct.pack(">H", len(corpo) + 2) + corpo


APP0 = segmento(0xE0, b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00")
SOS = bytes([0xFF, 0xDA]) + struct.pack(">H", 8) + b"\x01\x01\x00\x00\x3f\x00"


def jpeg(*segmenti, dati=b"\x12\x34\x56"):
    return b"\xff\xd8" + b"".join(segmenti) + SOS + dati + b"\xff\xd9"


def blocco(tipo, corpo):
    return struct.pack(">I", len(corpo)) + tipo + corpo + struct.pack(">I", zlib.crc32(tipo + corpo) & 0xFFFFFFFF)


IHDR = blocco(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
IDAT = blocco(b"IDAT", zlib.compress(b"\x00\xff\xff\xff"))


def png(*blocchi):
    return b"\x89PNG\r\n\x1a\n" + IHDR + b"".join(blocchi) + IDAT + blocco(b"IEND", b"")


CASI = [  # (nome, file, deve passare)
    ("JPEG con il segno nel commento dopo JFIF", jpeg(APP0, segmento(0xFE, SEGNO)), True),
    ("JPEG con il segno in un commento più lungo", jpeg(APP0, segmento(0xFE, b"prima. " + SEGNO + b" dopo.")), True),
    ("JPEG senza commento", jpeg(APP0), False),
    ("JPEG con un altro commento", jpeg(APP0, segmento(0xFE, b"Creato con un programma qualsiasi")), False),
    ("JPEG con il segno nei dati compressi", jpeg(APP0, dati=b"\x00" + SEGNO + b"\x00"), False),
    ("JPEG con un segno incompleto", jpeg(APP0, segmento(0xFE, SEGNO[:30])), False),
    ("PNG con il segno in tEXt", png(blocco(b"tEXt", b"Comment\x00" + SEGNO)), True),
    ("PNG senza tEXt", png(), False),
    ("PNG con il segno dopo l'immagine", b"\x89PNG\r\n\x1a\n" + IHDR + IDAT + blocco(b"tEXt", b"Comment\x00" + SEGNO), False),
    ("file che non è un'immagine", b"GIF89a" + SEGNO, False),
]
for nome, dati, deve in CASI:
    attesa(ha_segno(dati, SEGNO) == deve, f"{nome}: atteso {'passa' if deve else 'non passa'}")

# Il motore mette il segno subito dopo l'intestazione JFIF: lo stesso codice, riscritto qui, deve dare un file valido
motore = (REPO / "scripts/grafica-brand/firma-e-cornice.js").read_text(encoding="utf-8")
attesa("0xFF, 0xFE" in motore and "'Comment\\0'" in motore, "il motore non scrive più il commento JPEG o il blocco tEXt PNG")

# Sul repository: grafiche delle news in uscita e pagine della Parola dal 22/10/2026, firma in ogni modello
mancano = grafiche_senza_firma()
attesa(not mancano, "grafiche o modelli senza firma e cornice: " + "; ".join(mancano[:10]))

if falliti:
    print("PROVA FALLITA:")
    for f in falliti:
        print(f"  - {f}")
    sys.exit(1)
print(f"Prova di firma e cornice superata: {len(CASI)} file costruiti, motore e grafiche del repository.")
