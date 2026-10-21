#!/usr/bin/env python3
"""Prova del controllo «firma e cornice» (grafiche_senza_firma e ha_segno in controlla_sito.py), sui controlli di ogni PR.

Il controllo cerca il segno che il motore scripts/grafica-brand/firma-e-cornice.js scrive in testa alle grafiche
(commento nei JPEG, blocco tEXt nei PNG). Qui si prova su file costruiti apposta: il segno nel posto giusto passa;
nessun segno, un segno diverso o lo stesso testo finito nei dati compressi non passano. Le copertine dei video delle
news (fotogramma del social_video, locandine nel corpo) si provano su un piccolo sito finto: quella senza segno di
una news in uscita viene segnalata una volta sola, anche se la usano più news; quella con il segno, quella di una
news già uscita no. Poi si prova sul repository: il segno si legge dal motore, il motore lo mette davvero nei JPEG,
e il controllo trova il segno nelle grafiche e nelle copertine dei video delle news in uscita. Nasce con la regola
del 21/10/2026 (Alessandro: «metti in ogni slide, documento grafico eccetera sempre Misericordia di Ariccia!
Altrimenti ci rubano la grafica!!»).
Esce con 1 se un caso non va come deve. Solo libreria standard. Uso: prova_cornice.py
"""
import datetime as dt
import struct
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from controlla_sito import DAL_FIRMA, REPO, copertine_video, grafiche_senza_firma, ha_segno, segno_firma  # noqa: E402

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

# Copertine dei video di una news: fotogramma del social_video, locandine del corpo, social_video_copertina se è
# un'immagine (se è un numero è il secondo del video usato per il Reel, e non si controlla nel file)
CASI_COPERTINE = [  # (front matter, corpo, copertine attese)
    ('social_video: "/video/primo-soccorso-x.mp4"\nsocial_video_copertina: 1\n', "", ["img/video/primo-soccorso-x.jpg"]),
    ("social_video: /video/x.mp4\n", '{{< video src="video/x.mp4" poster="img/video/x.jpg" >}}', ["img/video/x.jpg"]),
    ('social_video_copertina: "/img/video/altra.jpg"\n', "", ["img/video/altra.jpg"]),
    ('title: "senza video"\n', "testo", []),
    ("", '{{< video src="video/y.mp4" poster="/img/video/y.jpg" >}}', ["img/video/y.jpg"]),
]
for fm, corpo, attese in CASI_COPERTINE:
    trovate = copertine_video(fm, corpo)
    attesa(trovate == attese, f"copertine_video({fm!r}, {corpo!r}) = {trovate}, attese {attese}")

with tempfile.TemporaryDirectory() as cartella:  # piccolo sito finto con quattro news video
    sito = Path(cartella)
    (sito / "content/news").mkdir(parents=True)
    (sito / "static/img/video").mkdir(parents=True)

    def news(nome, giorno, video):
        (sito / "content/news" / nome).write_text(
            f'---\ntitle: "prova"\ndate: {giorno.isoformat()}\nsocial_video: "/video/{video}.mp4"\nsocial_video_copertina: 1\n'
            f'---\n{{{{< video src="video/{video}.mp4" poster="img/video/{video}.jpg" >}}}}\n', encoding="utf-8")

    news("a.md", DAL_FIRMA, "con-segno")
    news("b.md", DAL_FIRMA, "senza-segno")
    news("c.md", DAL_FIRMA - dt.timedelta(days=1), "vecchio")
    news("d.md", DAL_FIRMA + dt.timedelta(days=30), "senza-segno")
    (sito / "static/img/video/con-segno.jpg").write_bytes(jpeg(APP0, segmento(0xFE, SEGNO)))
    (sito / "static/img/video/senza-segno.jpg").write_bytes(jpeg(APP0))
    (sito / "static/img/video/vecchio.jpg").write_bytes(jpeg(APP0))
    trovati = grafiche_senza_firma(sito)
    attesa(len(trovati) == 1 and "senza-segno.jpg" in trovati[0] and "copertina del video" in trovati[0]
           and "b.md" in trovati[0] and "d.md" in trovati[0],
           f"copertine dei video nel sito finto: attesa solo senza-segno.jpg (news b.md e d.md), trovato {trovati}")

# Il motore mette il segno subito dopo l'intestazione JFIF: lo stesso codice, riscritto qui, deve dare un file valido
motore = (REPO / "scripts/grafica-brand/firma-e-cornice.js").read_text(encoding="utf-8")
attesa("0xFF, 0xFE" in motore and "'Comment\\0'" in motore, "il motore non scrive più il commento JPEG o il blocco tEXt PNG")

# Sul repository: grafiche e copertine dei video delle news in uscita e pagine della Parola dal 22/10/2026, firma
# in ogni modello
mancano = grafiche_senza_firma()
attesa(not mancano, "grafiche, copertine o modelli senza firma e cornice: " + "; ".join(mancano[:10]))

if falliti:
    print("PROVA FALLITA:")
    for f in falliti:
        print(f"  - {f}")
    sys.exit(1)
print(f"Prova di firma e cornice superata: {len(CASI)} file costruiti, {len(CASI_COPERTINE)} casi di copertine dei "
      "video, sito finto, motore, grafiche e copertine del repository.")
