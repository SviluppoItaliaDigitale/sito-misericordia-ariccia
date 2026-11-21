#!/usr/bin/env python3
"""mani_makehuman.py — avambracci e mani dell'adulto, mani e piedi per il lattante, dal corpo umano di MakeHuman (CC0).

Il video 3D sul lattante (scripts/video-3d-lattante/) usa mani vere a cinque dita (istruzione di Alessandro del
21/11/2026: «Il corpo umano ha 5 dita per ogni mano»; niente mani costruite a forme). Questo script legge tre file del
repository ufficiale di MakeHuman, tutti rilasciati CC0 da Data Collection AB, Joel Palmius e Jonas Hauquier:
  makehuman/data/3dobjs/base.obj          corpo base (CC0, settembre 2020)
  makehuman/data/rigs/default.mhskel      scheletro «default» con le falangi di mani e piedi (CC0)
  makehuman/data/rigs/default_weights.mhw pesi dei vertici sulle ossa (CC0)
(https://github.com/makehumancommunity/makehuman, ramo master) e scrive un JSON con, per ogni parte, vertici, triangoli,
ossa (posizione e orientamento a riposo, genitore) e i 4 pesi più forti di ogni vertice, per costruire in three.js una
SkinnedMesh e mettere le dita in posa con le loro ossa. Nessun codice di MakeHuman viene usato: solo i dati CC0.

Parti: braccio.R / braccio.L (avambraccio e mano dell'adulto), mano.R / mano.L (solo la mano, per il lattante),
piede.R / piede.L (piede con le dita, per il lattante), testa (testa dell'adulto con occhi, mascella, collo e spalle, per i
soffi; aggiunta il 21/11/2026: un volto vero, mai sfere o primitive). Unità: metri (il corpo base è alto circa 1,69 m).
La testa ha anche i colori per vertice («colori», RGB 0-255): pelle, labbra un poco più scure, occhi (globi del modello,
gruppi helper-l-eye e helper-r-eye: bianco, iride castana e pupilla), maglia blu sotto il collo.
Uso: python3 mani_makehuman.py CARTELLA_DATI USCITA.json   (CARTELLA_DATI con i tre file; se mancano li scarica)
Scritto per Alessandro Cuollo il 21/11/2026.
"""
import base64, json, sys, urllib.request
from pathlib import Path
import numpy as np

RADICE = "https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/"
FILE = {"base.obj": "3dobjs/base.obj", "default.mhskel": "rigs/default.mhskel", "default_weights.mhw": "rigs/default_weights.mhw"}
SCALA = 0.1   # decimetri → metri


def scarica(cartella):
    cartella.mkdir(parents=True, exist_ok=True)
    for nome, via in FILE.items():
        f = cartella / nome
        if not f.exists():
            urllib.request.urlretrieve(RADICE + via, f)
    for nome in FILE:                                     # la licenza si controlla nel file stesso
        testo = (cartella / nome).read_text(encoding="utf-8", errors="ignore")
        cc0 = "released as CC0" in testo[:2000] if nome.endswith(".obj") else json.loads(testo).get("license") == "CC0"
        if not cc0:
            sys.exit(f"Errore: {nome} non dichiara la licenza CC0: non lo uso")


def leggi_obj(f, gruppi=("body",)):
    v, facce, gruppo = [], [], None
    for r in f.read_text(encoding="utf-8").splitlines():
        if r.startswith("v "):
            v.append([float(x) for x in r.split()[1:4]])
        elif r.startswith("g "):
            gruppo = r.split()[1]
        elif r.startswith("f ") and gruppo in gruppi:
            facce.append([int(x.split("/")[0]) - 1 for x in r.split()[1:]])
    return np.array(v) * SCALA, facce


def in_ordine(skel, ossa):
    """Ossa con ogni genitore prima dei figli (lo chiede creaParteMH di lattante3d.js)."""
    fuori, resto = [], list(ossa)
    while resto:
        for b in resto:
            p = skel["bones"][b]["parent"]
            if p not in resto or p in fuori:
                fuori.append(b); resto.remove(b); break
    return fuori


def parte(V, facce, skel, pesi, ossa, radice, nome, colori=None):
    """Vertici pesati per almeno metà sulle ossa della parte; i pesi delle altre ossa vanno alla radice."""
    tot = np.zeros(len(V)); per = {}
    for b in ossa:
        for i, w in pesi.get(b, []):
            tot[i] += w; per.setdefault(i, []).append((b, w))
    sel = np.where(tot >= 0.5)[0]; idx = {int(i): k for k, i in enumerate(sel)}
    tri = []
    for f in facce:
        if all(i in idx for i in f):
            q = [idx[i] for i in f]
            tri += [q[0], q[1], q[2]] + ([q[0], q[2], q[3]] if len(q) == 4 else [])
    nomi = [b for b in ossa]; pos_b = {b: k for k, b in enumerate(nomi)}
    si, sw = np.zeros((len(sel), 4), np.uint16), np.zeros((len(sel), 4), np.float32)
    for k, i in enumerate(sel):
        l = sorted(per[int(i)], key=lambda x: -x[1])[:4]
        resto = max(0.0, 1.0 - sum(w for _, w in per[int(i)]))
        l = [(b, w) for b, w in l]
        if resto > 0:
            l.append((radice, resto))
        acc = {}
        for b, w in l:
            acc[b] = acc.get(b, 0) + w
        l = sorted(acc.items(), key=lambda x: -x[1])[:4]
        s = sum(w for _, w in l)
        for j, (b, w) in enumerate(l):
            si[k, j] = pos_b[b]; sw[k, j] = w / s
    # ossa: testa, coda, piano di rotazione → orientamento a riposo (y lungo l'osso, x normale al piano di flessione)
    J = {n: V[np.array(ix)].mean(0) for n, ix in skel["joints"].items()}
    lista = []
    for b in nomi:
        d = skel["bones"][b]; h, t = J[d["head"]], J[d["tail"]]
        p = skel["planes"][d["rotation_plane"]]; a, c, e = (J[x] for x in p)
        y = (t - h) / np.linalg.norm(t - h); n = np.cross(c - a, e - c); n = n - n.dot(y) * y; x = n / np.linalg.norm(n)
        z = np.cross(x, y)
        par = d["parent"] if d["parent"] in pos_b else None
        lista.append({"nome": b, "genitore": par, "testa": h.round(5).tolist(), "coda": t.round(5).tolist(),
                      "assi": np.stack([x, y, z]).round(6).tolist()})
    b64 = lambda a: base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()
    print(f"{nome}: {len(sel)} vertici, {len(tri) // 3} triangoli, {len(nomi)} ossa")
    out = {"posizioni": b64(V[sel].astype(np.float32)), "indici": b64(np.array(tri, np.uint32)),
           "ossaIndici": b64(si), "ossaPesi": b64(sw), "ossa": lista}
    if colori is not None:
        out["colori"] = b64(colori(sel, per).astype(np.uint8))
    return out


def testa_adulto(V, skel, pesi, cartella):
    """Testa, viso, occhi, mascella, collo e spalle dell'adulto (soffi bocca su bocca e naso del lattante)."""
    _, facce = leggi_obj(cartella / "base.obj", ("body", "helper-l-eye", "helper-r-eye"))
    viso = ("head", "jaw", "eye.", "levator", "oculi", "orbicularis", "oris", "risorius", "temporalis", "special", "tongue")
    ossa = [b for b in skel["bones"] if b.startswith(viso) or b in
            ("neck01", "neck02", "neck03", "spine01", "spine02", "clavicle.L", "clavicle.R", "shoulder01.L", "shoulder01.R",
             "breast.L", "breast.R")]
    ossa = in_ordine(skel, ossa)
    J = {n: V[np.array(ix)].mean(0) for n, ix in skel["joints"].items()}
    occhi = {}
    for lato in "LR":                                     # vertici dei globi oculari (gruppi helper-*-eye)
        g = f"helper-{'l' if lato == 'L' else 'r'}-eye"
        ix, dentro = set(), False
        for r in (cartella / "base.obj").read_text(encoding="utf-8").splitlines():
            if r.startswith("g "):
                dentro = r.split()[1] == g
            elif r.startswith("f ") and dentro:
                ix.update(int(x.split("/")[0]) - 1 for x in r.split()[1:])
        c = V[sorted(ix)].mean(0); occhi[lato] = (ix, c, np.ptp(V[sorted(ix)][:, 0]) / 2)
    PELLE, LABBRA, MAGLIA = (217, 160, 124), (184, 118, 104), (0, 63, 133)

    def colori(sel, per):
        col = np.zeros((len(sel), 3))
        for k, i in enumerate(sel):
            i = int(i); w = dict(); [w.__setitem__(b, w.get(b, 0) + x) for b, x in per[i]]
            occhio = next((l for l, (ix, _, _) in occhi.items() if i in ix), None)
            if occhio:                                     # bianco, iride e pupilla sul davanti del globo (asse +z del modello)
                ix, c, r = occhi[occhio]; d = V[i] - c; ang = np.degrees(np.arccos(np.clip(d[2] / (np.linalg.norm(d) + 1e-9), -1, 1)))
                col[k] = (20, 14, 10) if ang < 12 else (92, 62, 40) if ang < 27 else (238, 236, 230)
            elif sum(x for b, x in w.items() if b.startswith(("spine", "clavicle", "shoulder", "breast"))) > 0.5 or V[i][1] < J["neck01____head"][1] - 0.02:
                col[k] = MAGLIA
            elif sum(x for b, x in w.items() if b.startswith("oris")) > 0.55:
                col[k] = LABBRA
            else:
                col[k] = PELLE
        return col
    return parte(V, facce, skel, pesi, ossa, ossa[0], "testa", colori)


def main():
    cartella, uscita = Path(sys.argv[1]), Path(sys.argv[2])
    scarica(cartella)
    V, facce = leggi_obj(cartella / "base.obj")
    skel = json.loads((cartella / "default.mhskel").read_text())
    pesi = {b: l for b, l in json.loads((cartella / "default_weights.mhw").read_text())["weights"].items()}
    out = {"fonte": "MakeHuman (makehumancommunity/makehuman, base.obj, default.mhskel, default_weights.mhw), CC0", "parti": {}}
    for lato in "RL":
        mano = [f"wrist.{lato}"] + [f"metacarpal{i}.{lato}" for i in range(1, 5)] + \
               [f"finger{d}-{f}.{lato}" for d in range(1, 6) for f in range(1, 4)]
        out["parti"][f"braccio.{lato}"] = parte(V, facce, skel, pesi, [f"lowerarm01.{lato}", f"lowerarm02.{lato}"] + mano,
                                                f"lowerarm01.{lato}", f"braccio.{lato}")
        out["parti"][f"mano.{lato}"] = parte(V, facce, skel, pesi, mano, f"wrist.{lato}", f"mano.{lato}")
        piede = [f"foot.{lato}", f"toe1-1.{lato}", f"toe1-2.{lato}"] + [f"toe{d}-{f}.{lato}" for d in range(2, 6) for f in range(1, 4)]
        out["parti"][f"piede.{lato}"] = parte(V, facce, skel, pesi, piede, f"foot.{lato}", f"piede.{lato}")
    out["parti"]["testa"] = testa_adulto(V, skel, pesi, cartella)
    uscita.write_text(json.dumps(out))
    print("scritto", uscita, round(uscita.stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
