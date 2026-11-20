#!/usr/bin/env python3
"""anatomia_ictus.py — prepara l'anatomia del video 3D «Ictus: il tempo è cervello».
Parte dall'anatomia del video sulla rianimazione (scripts/video-3d-rcp/anatomia.py: pelle, cuore, arterie e vene con il
sangue che scorre) e aggiunge dall'atlante BodyParts3D: i due emisferi del cervello, il resto dell'encefalo, le arterie
del cervello (carotidi interne, poligono di Willis, cerebrali anteriori, medie e posteriori, basilare) con i percorsi del
sangue, e per l'emisfero sinistro tre zone (parola, braccio, territorio dell'arteria cerebrale media) per le scene.
L'atlante ha solo l'arteria cerebrale media destra (tratto sfenoidale e rami centrali): la sinistra si ottiene
specchiandola, come fa l'atlante stesso per molte parti sinistre (file «…M»).
Dati: «BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International».
Uso: python3 anatomia_ictus.py --cartella BP3D --base ANATOMIA_RCP.json --uscita anatomia-ictus.json
"""
import argparse, base64, collections, json, os, sys
import numpy as np
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'video-3d-rcp'))
import anatomia as A   # noqa: E402  (funzioni comuni: lettura, semplificazione, impacchettamento, percorsi)

ACM_DX = ['FJ1662', 'FJ1663', 'FJ1692']             # arteria cerebrale media destra (tratto sfenoidale, rami centrali)
CONC_ART = ['FMA3949', 'FMA4062', 'FMA50542', 'FMA50584', 'FMA50585', 'FMA50029', 'FMA50030', 'FMA50082',
            'FMA50085', 'FMA50086', 'FMA50169', 'FMA3958', 'FMA4066']   # carotidi interne, Willis, basilare, vertebrali


def grafo_distanze(v, f, sorgenti):
    """Distanza lungo i vasi dalle sorgenti (come anatomia.py): lati dei triangoli, ponti entro 4 mm, pezzi staccati
    agganciati al più vicino."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra, connected_components
    from scipy.spatial import cKDTree
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]], cKDTree(v).query_pairs(0.0025, output_type='ndarray')])
    w = np.linalg.norm(v[e[:, 0]] - v[e[:, 1]], axis=1) + 1e-6
    n = len(v)
    G = coo_matrix((np.concatenate([w, w]), (np.concatenate([e[:, 0], e[:, 1]]), np.concatenate([e[:, 1], e[:, 0]]))), shape=(n, n)).tocsr()
    ncomp, lab = connected_components(G, directed=False)
    raggiunti = set(lab[sorgenti].tolist()); extra = []
    while len(raggiunti) < ncomp:
        dentro = np.isin(lab, list(raggiunti)); albero = cKDTree(v[dentro]); idx_in = np.where(dentro)[0]; best = None
        for c in set(range(ncomp)) - raggiunti:
            ii = np.where(lab == c)[0]; dd, jj = albero.query(v[ii]); k = int(np.argmin(dd))
            if best is None or dd[k] < best[0]: best = (dd[k], ii[k], idx_in[jj[k]], c)
        extra.append((best[1], best[2], best[0] * 1.5 + 1e-6)); raggiunti.add(best[3])
    if extra:
        ea = np.array(extra)
        G = G + coo_matrix((np.concatenate([ea[:, 2], ea[:, 2]]), (np.concatenate([ea[:, 0], ea[:, 1]]).astype(int), np.concatenate([ea[:, 1], ea[:, 0]]).astype(int))), shape=G.shape).tocsr()
    dist, pred, _ = dijkstra(G, indices=sorgenti, min_only=True, return_predecessors=True)
    fin = np.isfinite(dist); dist[~fin] = dist[fin].max()
    return dist, pred


def b8(x):
    return base64.b64encode(np.round(np.clip(x, 0, 1) * 255).astype(np.uint8).tobytes()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cartella', required=True); ap.add_argument('--base', required=True); ap.add_argument('--uscita', required=True)
    a = ap.parse_args()
    d = os.path.join(a.cartella, 'obj', 'partof_BP3D_4.0_obj_99')
    el = collections.defaultdict(set)
    for l in open(os.path.join(a.cartella, 'partof_element_parts.txt')).read().splitlines()[1:]:
        c, _, fj = l.split('\t'); el[c].add(fj)
    obj = lambda fj: A.leggi_obj(os.path.join(d, fj + '.obj'))
    base = json.load(open(a.base))
    tieni = ['pelle', 'atrio_dx', 'atrio_sx', 'ventricolo_dx', 'ventricolo_sx', 'valvole', 'coronarie', 'vene_cuore', 'papillari', 'arterie', 'vene', 'colonna']
    ris = {'attribuzione': base['attribuzione'], 'gruppi': {k: base['gruppi'][k] for k in tieni if k in base['gruppi']},
           'punti': base['punti'], 'percorsi': [p for p in base['percorsi'] if p['tipo'] == 'arterie' and p['nome'] in ('testa_dx', 'testa_sx')]}
    # --- encefalo: emisferi e resto
    def gruppo(fjs, fraz):
        pezzi = [A.semplifica(*obj(fj)[:2], fraz) for fj in sorted(fjs) if os.path.exists(os.path.join(d, fj + '.obj'))]
        return A.unisci(pezzi)
    sx, dx = el['FMA61819'], el['FMA67292']
    vs, fs = gruppo(sx, 0.32); vd, fd = gruppo(dx, 0.32); vr, fr = gruppo(el['FMA50801'] - sx - dx, 0.3)
    print('emisferi', len(vs), len(vd), 'resto', len(vr))
    # zone dell'emisfero sinistro (pesi 0..1 per vertice, sfumati sui bordi)
    from scipy.spatial import cKDTree
    def vicino_a(concetti, raggio):
        vv = np.concatenate([obj(fj)[0] for c in concetti for fj in el[c]])
        dd = cKDTree(vv).query(vs)[0]
        return np.clip(1 - (dd - 0.002) / raggio, 0, 1)
    ins = np.concatenate([obj(fj)[0] for fj in el['FMA72978']]).mean(0)       # insula sinistra: centro della zona della parola
    parola = np.clip(1 - (np.linalg.norm((vs - ins) * [0.7, 1.0, 1.0], axis=1) - 0.018) / 0.014, 0, 1) * (vs[:, 0] > 0.03)
    prec = vicino_a(['FMA72662'], 0.006)                                       # giro precentrale sinistro
    braccio = prec * np.clip((vs[:, 1] - 1.575) / 0.012, 0, 1) * np.clip((1.618 - vs[:, 1]) / 0.012, 0, 1) * (vs[:, 0] > 0.035)
    # territorio dell'arteria cerebrale media: faccia laterale dell'emisfero (frontale, parietale, temporale), non il polo occipitale
    lat = np.clip((vs[:, 0] - 0.028) / 0.018, 0, 1)
    zona = lat * np.clip((vs[:, 2] - 0.0) / 0.03, 0, 1) * np.clip((0.165 - vs[:, 2]) / 0.025, 0, 1) * np.clip((1.627 - vs[:, 1]) / 0.012, 0, 1)
    gS = A.impacchetta(vs, fs); gS.update({'parola': b8(parola), 'braccio': b8(braccio), 'zona': b8(zona)})
    ris['gruppi']['emisfero_sx'] = gS
    ris['gruppi']['emisfero_dx'] = A.impacchetta(vd, fd)
    ris['gruppi']['encefalo_resto'] = A.impacchetta(vr, fr)
    # --- arterie del cervello: atlante + arteria cerebrale media sinistra specchiata
    fjs = set().union(*[el[c] for c in CONC_ART])
    pezzi = []
    for fj in sorted(fjs):
        if not os.path.exists(os.path.join(d, fj + '.obj')): continue
        v, f, nm = obj(fj)
        if 'vertebral' in nm.lower(): v_keep = v[:, 1] > 1.36       # solo il tratto della testa e del collo alto
        else: v_keep = None
        if v_keep is not None:
            ok = v_keep[f].all(1); f = f[ok]
            if not len(f): continue
        pezzi.append(A.semplifica(v, f, 0.8))
    acm = []
    for fj in ACM_DX:
        v, f, _ = obj(fj); m = v * [-1, 1, 1]
        acm.append(A.semplifica(m, f[:, ::-1].copy(), 0.9))
    va, fa = A.unisci(pezzi + acm)
    acm_v, acm_f = A.unisci(acm)
    print('arterie del cervello', len(va), 'arteria cerebrale media sinistra', len(acm_v))
    # flusso nella rete (bagliori): distanza dal fondo delle carotidi interne e delle vertebrali
    dist, pred = grafo_distanze(va, fa, np.where(va[:, 1] < 1.44)[0])
    ris['gruppi']['arterie_cervello'] = A.impacchetta(va, fa, dist / 0.35); ris['gruppi']['arterie_cervello']['flussoMax'] = 0.35
    ris['gruppi']['acm_sx'] = A.impacchetta(acm_v, acm_f)
    # percorsi dei globuli: una catena di vasi per volta (niente scorciatoie fra vasi vicini), dal fondo del primo
    # vaso all'estremo dell'ultimo
    def mesh(fjs, specchio=()):
        pz = []
        for fj in fjs:
            v, f, _ = obj(fj)
            if fj in specchio: v, f = v * [-1, 1, 1], f[:, ::-1].copy()
            pz.append((v, f))
        return A.unisci(pz)
    basilare = sorted(el['FMA50542'] - el['FMA50584'] - el['FMA50585'])
    CATENE = {
        'media_sx': (['FJ1682M', 'FJ1692'], ('FJ1692',), lambda v: v[:, 0]),
        'media_dx': (['FJ1682', 'FJ1692'], (), lambda v: -v[:, 0]),
        'anteriore_sx': (['FJ1682M', 'FJ1654M'], (), lambda v: v[:, 1] + 0.3 * v[:, 2]),
        'anteriore_dx': (['FJ1682', 'FJ1654'], (), lambda v: v[:, 1] + 0.3 * v[:, 2]),
        'posteriore_sx': (basilare + sorted(el['FMA50585']), (), lambda v: -v[:, 2] + 0.5 * v[:, 0]),
        'posteriore_dx': (basilare + sorted(el['FMA50584']), (), lambda v: -v[:, 2] - 0.5 * v[:, 0])}
    for nome, (fjs, sp, chiave) in CATENE.items():
        v, f = mesh(fjs, sp)
        if nome.startswith('media_sx'): pass
        prima = obj(fjs[0])[0]; sorg = np.where(np.isin(np.arange(len(v)), np.arange(len(prima))) & (v[:, 1] < prima[:, 1].min() + 0.003))[0]
        dd, pp = grafo_distanze(v, f, sorg)
        q = v[np.argmax(chiave(v))]
        A.REGIONI['catena'] = {nome: (lambda q: lambda w: np.linalg.norm(w - q, axis=1) < 0.004)(q)}
        for r in A.percorsi('catena', v, dd, pp):
            r['tipo'] = 'arterie_cervello'; ris['percorsi'].append(r)
    # punto del coagulo: sul tratto sfenoidale specchiato, a circa un terzo dall'inizio
    sf = obj('FJ1692')[0] * [-1, 1, 1]
    asse = sf[np.argsort(sf[:, 0])]
    k = int(0.38 * len(asse)); ris['punti']['coagulo'] = asse[max(0, k - 40):k + 40].mean(0).round(4).tolist()
    for nome, vv in [('emisfero_sx', vs), ('emisfero_dx', vd)]:
        ris['punti'][nome] = vv.mean(0).round(4).tolist(); ris['punti'][nome + '_min'] = vv.min(0).round(4).tolist(); ris['punti'][nome + '_max'] = vv.max(0).round(4).tolist()
    ris['punti']['parola'] = vs[parola > 0.5].mean(0).round(4).tolist(); ris['punti']['braccio_cervello'] = vs[braccio > 0.5].mean(0).round(4).tolist()
    ris['punti']['zona'] = vs[zona > 0.6].mean(0).round(4).tolist()
    # emorragia (solo accenno): vicino a un ramo centrale dell'arteria cerebrale media destra, in profondità
    rc = obj('FJ1662')[0]; ris['punti']['emorragia'] = rc[np.argmax(rc[:, 1])].round(4).tolist()
    print({k: ris['punti'][k] for k in ['coagulo', 'parola', 'braccio_cervello', 'zona', 'emorragia']},
          'pesi >0.5:', int((parola > .5).sum()), int((braccio > .5).sum()), int((zona > .5).sum()), 'di', len(vs))
    json.dump(ris, open(a.uscita, 'w'))
    print('scritto', a.uscita, os.path.getsize(a.uscita) // 1024, 'KB')


if __name__ == '__main__':
    main()
