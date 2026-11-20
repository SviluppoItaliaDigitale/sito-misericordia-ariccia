#!/usr/bin/env python3
"""anatomia_infarto.py — aggiunge all'anatomia del video sulla rianimazione (scripts/video-3d-rcp/anatomia.py) ciò che
serve al video «Infarto: che cosa succede nel cuore»: le linee centrali delle coronarie vere dell'atlante (discendente
anteriore, circonflessa, coronaria destra) per i globuli che le percorrono, il punto del blocco sulla discendente
anteriore e, per ogni vertice delle pareti dei ventricoli, quanto dipende dal tratto a valle del blocco (zona che si
scurisce). Dati: «BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International».
Uso: python3 anatomia_infarto.py --cartella ATLANTE --anatomia anatomia.json --uscita anatomia-infarto.json
"""
import argparse, base64, collections, json, os, sys
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'video-3d-rcp'))
from anatomia import leggi_obj  # noqa: E402  (stessa lettura e stesso sistema di coordinate)

RAMI = {   # linea centrale: dall'origine sull'aorta al punto più lontano dei file con questi nomi
    'iva': ['trunk of left coronary artery', 'trunk of anterior interventricular branch of left coronary artery'],
    'cx': ['trunk of left coronary artery', 'circumflex branch of left coronary artery'],
    'dx': ['trunk of right coronary artery', 'posterior interventricular branch of right coronary artery'],
}
BLOCCO = 0.30          # il coagulo chiude la discendente anteriore a questa frazione del suo percorso
RAGGIO_ZONA = {'ventricolo_sx': 0.024, 'ventricolo_dx': 0.011, 'papillari': 0.024}   # pareti vicine al tratto a valle:
# muscolo che resta senza sangue (la discendente anteriore irrora soprattutto la parete anteriore del ventricolo sinistro)

def decodifica(g):
    q = np.frombuffer(base64.b64decode(g['pos']), np.uint16).reshape(-1, 3).astype(np.float64)
    return np.array(g['lo']) + q / 65535 * np.array(g['sc'])

def linea(v, f, origine):
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]], cKDTree(v).query_pairs(0.002, output_type='ndarray')])
    w = np.linalg.norm(v[e[:, 0]] - v[e[:, 1]], axis=1) + 1e-6
    G = coo_matrix((np.r_[w, w], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(len(v), len(v))).tocsr()
    s = np.argsort(np.linalg.norm(v - origine, axis=1))[:10]
    d, pred, _ = dijkstra(G, indices=s, min_only=True, return_predecessors=True)
    d[~np.isfinite(d)] = -1
    k = int(np.argmax(d)); cam = []
    while k >= 0: cam.append(k); k = pred[k]
    cam = cam[::-1]; albero = cKDTree(v); C = []
    for i in cam:   # centro del vaso: media dei punti vicini alla stessa distanza lungo il vaso
        vic = [j for j in albero.query_ball_point(v[i], 0.006) if d[j] >= 0 and abs(d[j] - d[i]) < 0.0025]
        C.append(v[vic].mean(0) if vic else v[i])
    C = np.array(C)
    for _ in range(8): C[1:-1] = 0.25 * C[:-2] + 0.5 * C[1:-1] + 0.25 * C[2:]
    L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]
    u = np.linspace(0, L[-1], max(2, int(L[-1] / 0.001)))
    return np.stack([np.interp(u, L, C[:, j]) for j in range(3)], 1), float(L[-1])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cartella', required=True); ap.add_argument('--anatomia', required=True); ap.add_argument('--uscita', required=True)
    a = ap.parse_args()
    A = json.load(open(a.anatomia))
    d = os.path.join(a.cartella, 'obj', 'partof_BP3D_4.0_obj_99')
    per_nome = collections.defaultdict(set)
    for l in open(os.path.join(a.cartella, 'partof_element_parts.txt')).read().splitlines()[1:]:
        _, nome, fj = l.split('\t'); per_nome[nome.lower()].add(fj)
    origine = np.array(A['punti']['aorta_asc'])
    A['percorsi_cor'] = []
    for ramo, nomi in RAMI.items():
        pezzi = [leggi_obj(os.path.join(d, fj + '.obj')) for n in nomi for fj in sorted(per_nome[n])]
        if not pezzi: sys.exit('mancano i file di ' + ramo)
        vs, fs, k = [], [], 0
        for v, f, _ in pezzi: vs.append(v); fs.append(f + k); k += len(v)
        P, lung = linea(np.concatenate(vs), np.concatenate(fs), origine)
        A['percorsi_cor'].append({'nome': ramo, 'lung': round(lung, 4), 'punti': P.round(5).tolist()})
        print(f'coronaria {ramo}: {lung * 1000:.0f} mm, {len(P)} punti')
        if ramo == 'iva':
            i = int(BLOCCO * (len(P) - 1))
            tan = P[min(i + 3, len(P) - 1)] - P[max(i - 3, 0)]; tan /= np.linalg.norm(tan)
            A['punti']['blocco'] = P[i].round(5).tolist(); A['punti']['blocco_tan'] = tan.round(5).tolist()
            a_valle = P[i + 4:]
    # zona del muscolo a valle del blocco: 1 vicino alla discendente anteriore oltre il coagulo, 0 lontano
    albero = cKDTree(a_valle)
    for nome in ['ventricolo_sx', 'ventricolo_dx', 'papillari']:
        g = A['gruppi'][nome]; v = decodifica(g)
        dist = albero.query(v)[0]
        z = np.exp(-np.square(dist / RAGGIO_ZONA[nome]))
        g['zona'] = base64.b64encode(np.round(np.clip(z, 0, 1) * 255).astype(np.uint8).tobytes()).decode()
        print(f'zona {nome}: {100 * (z > 0.5).mean():.0f}% dei vertici')
    json.dump(A, open(a.uscita, 'w'))
    print('scritto', a.uscita, os.path.getsize(a.uscita) // 1024, 'KB')

if __name__ == '__main__':
    main()
