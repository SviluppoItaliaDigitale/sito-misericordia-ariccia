#!/usr/bin/env python3
"""anatomia.py — prepara i modelli anatomici del video 3D sulla rianimazione dall'atlante BodyParts3D.
Scarica (se manca) partof_BP3D_4.0_obj_99, raggruppa le parti (pelle, cuore per camere, valvole, sangue nelle camere,
arterie e vene con la piccola circolazione, polmoni, gabbia toracica, colonna, cervello), le semplifica, calcola per i vasi
la distanza lungo l'albero dal cuore (serve al sangue che scorre) e salva un JSON compatto per la pagina.
Dati: «BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International».
Uso: python3 anatomia.py --cartella LAVORO --uscita anatomia.json
"""
import argparse, base64, collections, json, os, re, subprocess, sys, zipfile
import numpy as np

BASE = 'https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/'

# gruppi: nome -> (concetti FMA da includere, frazione di triangoli da tenere)
GRUPPI = {
    'pelle':        (['FMA7163'], 0.35),
    'cervello':     (['FMA50801'], 0.25),
    'polmoni':      (['FMA7309', 'FMA7310'], 0.5),
    'trachea':      (['FMA7393'], 0.6),
    'costole':      (['FMA7480'], 0.45),     # gabbia toracica: costole, cartilagini, sterno
    'colonna':      (['FMA9140'], 0.5),
    'diaframma':    (['FMA13295'], 0.6),
}
CUORE = {   # parti del cuore, in quest'ordine di precedenza
    'valvole':  ['FMA7234', 'FMA7235', 'FMA7236', 'FMA7246'],
    'sangue_ad': ['FMA11359'], 'sangue_as': ['FMA9465'], 'sangue_vd': ['FMA9291'], 'sangue_vs': ['FMA9466'],
    'atrio_dx': ['FMA9457'], 'atrio_sx': ['FMA9531'], 'papillari': ['FMA9533', 'FMA9556'],
}
# la parete dei due ventricoli (FJ2428, «Wall of ventricle») c'è solo nell'albero IS-A: si prende da lì e si divide
# fra destro e sinistro secondo la cavità più vicina
PARETE_VENTRICOLI = 'FJ2428'

def scarica_parete(cart):
    p = os.path.join(cart, 'isa', PARETE_VENTRICOLI + '.obj')
    if not os.path.exists(p):
        z = os.path.join(cart, 'isa.zip')
        subprocess.run(['curl', '-sL', '-o', z, BASE + 'isa_BP3D_4.0_obj_99.zip'], check=True)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with zipfile.ZipFile(z) as zz, open(p, 'wb') as out:
            out.write(zz.read('isa_BP3D_4.0_obj_99/' + PARETE_VENTRICOLI + '.obj'))
        os.remove(z)
    return p

def scarica(cart):
    z = os.path.join(cart, 'partof.zip')
    for nome in ['partof_parts_list_e.txt', 'partof_element_parts.txt']:
        p = os.path.join(cart, nome)
        if not os.path.exists(p): subprocess.run(['curl', '-sL', '-o', p, BASE + nome], check=True)
    d = os.path.join(cart, 'obj')
    if not os.path.isdir(d):
        if not os.path.exists(z): subprocess.run(['curl', '-sL', '-o', z, BASE + 'partof_BP3D_4.0_obj_99.zip'], check=True)
        zipfile.ZipFile(z).extractall(d)
    return os.path.join(d, 'partof_BP3D_4.0_obj_99')

# tratti del collo che l'atlante non ha: carotide comune -> carotide interna, succlavia -> arteria vertebrale
PONTI = [('FJ3564', 'FJ1682', 'cima'), ('FJ3483', 'FJ1682M', 'cima'),
         ('FJ3585X', None, None)][:2]
PONTI += [('FJ_SUCCL_DX', 'FJ1725', 'vicino'), ('FJ_SUCCL_SX', 'FJ1725M', 'vicino')]

PUNTI = {'vcs': 'FMA4720', 'vci': 'FMA10951', 'cav_ad': 'FMA11359', 'cav_vd': 'FMA9291', 'cav_as': 'FMA9465',
         'cav_vs': 'FMA9466', 'efflusso_vd': 'FMA7216', 'efflusso_vs': 'FMA9473', 'tronco_polm': 'FMA8612',
         'aorta_asc': 'FMA3736', 'arco_aortico': 'FMA3768', 'aorta_disc': 'FMA3784', 'sterno': 'FMA7485',
         'corpo_sterno': 'FMA7487', 'colonna_t': 'FMA9140', 'cuore': 'FMA7088', 'cervello': 'FMA50801',
         'polm_dx': 'FMA7309', 'polm_sx': 'FMA7310', 'vp_dx_sup': 'FMA49914', 'vp_dx_inf': 'FMA49911',
         'vp_sx_sup': 'FMA49916', 'vp_sx_inf': 'FMA49913', 'carotide_dx': 'FMA3941', 'carotide_sx': 'FMA4058',
         'carotide_int_dx': 'FMA3949', 'carotide_int_sx': 'FMA4062', 'costola5_sx': 'FMA8093', 'costola4_sx': 'FMA8148',
         'cartilagine5_sx': 'FMA8112', 'pelle': 'FMA7163', 'tricuspide': 'FMA7234', 'mitrale': 'FMA7235',
         'v_aortica': 'FMA7236', 'v_polmonare': 'FMA7246'}

# Percorsi del sangue per i globuli che scorrono: dall'origine (radice dell'aorta, tronco polmonare, atrio destro, atrio
# sinistro) al punto più lontano di ogni regione, lungo il grafo dei vasi; poi riportati al centro del vaso (media dei
# punti vicini che hanno la stessa distanza lungo l'albero), lisciati e ricampionati ogni 5 mm.
REGIONI = {
    'arterie': {'testa_dx': lambda v: (v[:, 0] < 0) & (v[:, 1] > 1.47), 'testa_sx': lambda v: (v[:, 0] > 0) & (v[:, 1] > 1.47),
                'braccio_dx': lambda v: v[:, 0] < -0.22, 'braccio_sx': lambda v: v[:, 0] > 0.22,
                'gamba_dx': lambda v: (v[:, 0] < 0) & (v[:, 1] < 0.25), 'gamba_sx': lambda v: (v[:, 0] > 0) & (v[:, 1] < 0.25),
                'pancia': lambda v: (np.abs(v[:, 0]) < 0.12) & (v[:, 1] > 0.95) & (v[:, 1] < 1.05)},
    # l'atlante ha le vene del tronco e del collo, non quelle di braccia e gambe: il ritorno parte da lì
    'vene': {'testa_dx': lambda v: (v[:, 1] > 1.33) & (v[:, 0] < 0), 'testa_sx': lambda v: (v[:, 1] > 1.33) & (v[:, 0] > 0),
             'braccio_dx': lambda v: (v[:, 0] < -0.07) & (v[:, 1] > 1.28), 'braccio_sx': lambda v: (v[:, 0] > 0.07) & (v[:, 1] > 1.28),
             'bacino_dx': lambda v: (v[:, 0] < 0) & (v[:, 1] < 0.78), 'bacino_sx': lambda v: (v[:, 0] > 0) & (v[:, 1] < 0.78)},
    'arterie_polm': {'dx_alto': lambda v: (v[:, 0] < -0.03) & (v[:, 1] > 1.25), 'dx_basso': lambda v: (v[:, 0] < -0.03) & (v[:, 1] < 1.22),
                     'sx_alto': lambda v: (v[:, 0] > 0.06) & (v[:, 1] > 1.25), 'sx_basso': lambda v: (v[:, 0] > 0.06) & (v[:, 1] < 1.22)},
    'vene_polm': {'dx_alto': lambda v: (v[:, 0] < -0.03) & (v[:, 1] > 1.25), 'dx_basso': lambda v: (v[:, 0] < -0.03) & (v[:, 1] < 1.22),
                  'sx_alto': lambda v: (v[:, 0] > 0.06) & (v[:, 1] > 1.25), 'sx_basso': lambda v: (v[:, 0] > 0.06) & (v[:, 1] < 1.22)}}

def percorsi(nome, v, dist, pred):
    from scipy.spatial import cKDTree
    albero = cKDTree(v); out = []
    for reg, sel in REGIONI.get(nome, {}).items():
        idx = np.where(sel(v) & np.isfinite(dist))[0]
        if not len(idx): print('   regione vuota', nome, reg); continue
        k = idx[np.argmax(dist[idx])]; cammino = []
        while k >= 0 and len(cammino) < 100000: cammino.append(k); k = pred[k]
        cammino = cammino[::-1]
        P = v[cammino]; C = []
        for i, q in zip(cammino, P):
            vic = albero.query_ball_point(q, 0.012)
            vic = [j for j in vic if abs(dist[j] - dist[i]) < 0.006]
            C.append(v[vic].mean(0) if vic else q)
        C = np.array(C)
        for _ in range(6):                                   # lisciatura
            C[1:-1] = 0.25 * C[:-2] + 0.5 * C[1:-1] + 0.25 * C[2:]
        L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))])
        n = max(2, int(L[-1] / 0.005)); u = np.linspace(0, L[-1], n)
        R = np.stack([np.interp(u, L, C[:, j]) for j in range(3)], 1)
        out.append({'tipo': nome, 'nome': reg, 'lung': round(float(L[-1]), 4), 'punti': R.round(4).tolist()})
        print(f'   percorso {nome}/{reg}: {L[-1]:.2f} m, {n} punti')
    return out

def estremo(v, alto, spess=0.004):
    z = v[:, 1]
    sel = z > z.max() - spess if alto else z < z.min() + spess
    c = v[sel].mean(0)
    sel2 = (z > z.max() - 0.02) & (z < z.max() - 0.008) if alto else (z < z.min() + 0.02) & (z > z.min() + 0.008)
    d = c - v[sel2].mean(0) if sel2.any() else np.array([0, 1.0 if alto else -1.0, 0])
    d /= np.linalg.norm(d)
    rad = np.linalg.norm((v[sel] - c) - np.outer((v[sel] - c) @ d, d), axis=1).mean()
    return c, d, rad

def ponte(va, vb, modo, seg=40, giri=20):
    """Tubo morbido (curva di Hermite) dall'estremo di va all'inizio di vb, con il raggio dei due vasi."""
    c1, d1, r1 = estremo(vb, alto=False); d1 = -d1          # inizio del vaso di arrivo, direzione verso l'alto
    if modo == 'cima':
        c0, d0, r0 = estremo(va, alto=True)
    else:                                                  # dal punto della succlavia più vicino, verso l'alto
        k = np.argmin(np.linalg.norm(va - c1, axis=1)); c0 = va[k] - np.array([0, 0.002, 0]); d0 = np.array([0, 1.0, 0]); r0 = r1
    L = np.linalg.norm(c1 - c0)
    c0 = c0 - d0 * 0.003; c1 = c1 + d1 * 0.003               # piccola sovrapposizione: nessuna fessura
    u = np.linspace(0, 1, seg)[:, None]
    h00, h10, h01, h11 = 2*u**3-3*u**2+1, u**3-2*u**2+u, -2*u**3+3*u**2, u**3-u**2
    P = h00*c0 + h10*d0*L + h01*c1 + h11*d1*L
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True)
    a = np.cross(T[0], [1.0, 0, 0]); a /= np.linalg.norm(a)
    vs = []
    for i in range(seg):
        a = a - T[i] * (a @ T[i]); a /= np.linalg.norm(a); b = np.cross(T[i], a)
        r = r0 + (r1 - r0) * u[i, 0]
        for j in range(giri):
            ang = 2 * np.pi * j / giri
            vs.append(P[i] + r * (np.cos(ang) * a + np.sin(ang) * b))
    vs = np.array(vs); f = []
    for i in range(seg - 1):
        for j in range(giri):
            p0, p1 = i * giri + j, i * giri + (j + 1) % giri
            f += [[p0, p0 + giri, p1], [p1, p0 + giri, p1 + giri]]
    return vs, np.array(f)

def leggi_obj(p):
    v, f, nome = [], [], ''
    for l in open(p):
        if l.startswith('v '): v.append([float(x) for x in l.split()[1:4]])
        elif l.startswith('f '): f.append([int(x.split('/')[0]) - 1 for x in l.split()[1:4]])
        elif l.startswith('# English name'): nome = l.split(':', 1)[1].strip()
    v = np.array(v, dtype=np.float64)
    # mm dell'atlante -> metri di three.js: x = sinistra del paziente, y = in alto, z = davanti
    v = np.stack([v[:, 0], v[:, 2], -v[:, 1]], 1) / 1000.0
    return v, np.array(f, dtype=np.int64), nome

def semplifica(v, f, frazione):
    if frazione >= 0.999 or len(f) < 200: return v, f
    import fast_simplification
    v2, f2 = fast_simplification.simplify(v.astype(np.float32), f.astype(np.int32), target_reduction=1 - frazione)
    return v2.astype(np.float64), f2.astype(np.int64)

def unisci(pezzi):
    vs, fs, n = [], [], 0
    for v, f in pezzi:
        vs.append(v); fs.append(f + n); n += len(v)
    return np.concatenate(vs), np.concatenate(fs)

def normali(v, f):
    n = np.zeros_like(v)
    c = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    for k in range(3): np.add.at(n, f[:, k], c)
    l = np.linalg.norm(n, axis=1, keepdims=True); l[l == 0] = 1
    return n / l

def impacchetta(v, f, extra=None):
    lo, hi = v.min(0), v.max(0); sc = np.maximum(hi - lo, 1e-9)
    q = np.round((v - lo) / sc * 65535).astype(np.uint16)
    nr = np.round(normali(v, f) * 127).astype(np.int8)
    idx = f.astype(np.uint32 if len(v) > 65535 else np.uint16)
    out = {'n': int(len(v)), 't': int(len(f)), 'lo': lo.round(6).tolist(), 'sc': sc.round(6).tolist(),
           'pos': base64.b64encode(q.tobytes()).decode(), 'nor': base64.b64encode(nr.tobytes()).decode(),
           'idx': base64.b64encode(idx.tobytes()).decode(), 'i32': bool(len(v) > 65535)}
    if extra is not None:
        out['flusso'] = base64.b64encode(np.round(np.clip(extra, 0, 1) * 65535).astype(np.uint16).tobytes()).decode()
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cartella', required=True); ap.add_argument('--uscita', required=True)
    a = ap.parse_args()
    d = scarica(a.cartella)
    el = collections.defaultdict(set)
    for l in open(os.path.join(a.cartella, 'partof_element_parts.txt')).read().splitlines()[1:]:
        c, _, fj = l.split('\t'); el[c].add(fj)
    cache = {}
    def obj(fj):
        if fj not in cache:
            p = os.path.join(d, fj + '.obj')
            cache[fj] = leggi_obj(p) if os.path.exists(p) else None
        return cache[fj]
    ris = {'attribuzione': 'BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International',
           'gruppi': {}}
    def gruppo(nome, fjs, fraz):
        pezzi = []
        for fj in sorted(fjs):
            o = obj(fj)
            if o is None or not len(o[1]): continue
            pezzi.append(semplifica(o[0], o[1], fraz))
        if not pezzi: print('vuoto', nome); return None
        v, f = unisci(pezzi)
        print(f'{nome:16s} parti {len(pezzi):4d} vertici {len(v):7d} triangoli {len(f):7d}')
        return v, f
    for nome, (conc, fraz) in GRUPPI.items():
        fjs = set().union(*[el[c] for c in conc])
        g = gruppo(nome, fjs, fraz)
        if g: ris['gruppi'][nome] = impacchetta(*g)
    # cuore: ogni file in un solo gruppo, il resto in «cuore_altro»
    cuore = set(el['FMA7088']); usati = set()
    for nome, conc in CUORE.items():
        fjs = set().union(*[el[c] for c in conc]) & (cuore | set().union(*[el[c] for c in conc])) - usati
        usati |= fjs
        g = gruppo(nome, fjs, 0.7)
        if g: ris['gruppi'][nome] = impacchetta(*g)
    cor = {fj for fj in cuore - usati if obj(fj) is not None and re.search(r'artery|branch', obj(fj)[2], re.I)}
    g = gruppo('coronarie', cor, 0.8)
    if g: ris['gruppi']['coronarie'] = impacchetta(*g)
    g = gruppo('vene_cuore', {fj for fj in cuore - usati - cor if obj(fj) is not None and re.search(r'vein|sinus', obj(fj)[2], re.I)}, 0.8)
    if g: ris['gruppi']['vene_cuore'] = impacchetta(*g)
    # pareti dei ventricoli divise fra destro e sinistro
    from scipy.spatial import cKDTree
    vw, fw, _ = leggi_obj(scarica_parete(a.cartella))
    vw, fw = semplifica(vw, fw, 0.8)
    cav = {k: obj(next(iter(el[c])))[0] for k, c in [('dx', 'FMA9291'), ('sx', 'FMA9466')]}
    cen = vw[fw].mean(1)
    ddx = cKDTree(cav['dx']).query(cen)[0]; dsx = cKDTree(cav['sx']).query(cen)[0]
    for lato, sel in [('dx', ddx < dsx), ('sx', ddx >= dsx)]:
        ff = fw[sel]; usa = np.unique(ff); mappa = -np.ones(len(vw), np.int64); mappa[usa] = np.arange(len(usa))
        v2, f2 = vw[usa], mappa[ff]
        print(f'ventricolo_{lato:6s} vertici {len(v2):7d} triangoli {len(f2):7d}')
        ris['gruppi']['ventricolo_' + lato] = impacchetta(v2, f2)
    # vasi: tutto l'apparato cardiovascolare meno il cuore
    vasi = set(el['FMA7161']) - cuore - usati
    polm_a = re.compile(r'pulmonary (trunk|artery)|segmental artery|lingular artery|lobar artery|basal artery', re.I)
    polm_v = re.compile(r'pulmonary vein|segmental vein|lingular vein|lobar vein|basal vein|apicoposterior vein', re.I)
    classi = {'arterie': [], 'vene': [], 'arterie_polm': [], 'vene_polm': []}
    for fj in sorted(vasi):
        o = obj(fj)
        if o is None: continue
        nm = o[2]
        if re.search(r'hepatovenous segment|lobe of liver', nm, re.I): continue   # volumi del fegato, non vasi
        if polm_a.search(nm): classi['arterie_polm'].append(fj)
        elif polm_v.search(nm): classi['vene_polm'].append(fj)
        elif re.search(r'vein|vena|sinus|venous', nm, re.I): classi['vene'].append(fj)
        else: classi['arterie'].append(fj)
    # succlavie: file con quel nome fra le arterie
    succ = {}
    for fj in classi['arterie']:
        nm = obj(fj)[2].lower()
        if nm in ('right subclavian artery', 'left subclavian artery'):
            k = 'FJ_SUCCL_DX' if nm.startswith('right') else 'FJ_SUCCL_SX'
            succ[k] = np.concatenate([succ[k], obj(fj)[0]]) if k in succ else obj(fj)[0]
    for k, vv in succ.items(): cache[k] = (vv, np.zeros((0, 3), np.int64), k)
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    from scipy.spatial import cKDTree
    # origine del flusso: radice dell'aorta (arterie), tronco polmonare (arterie polmonari);
    # le vene scorrono verso il cuore: distanza dall'atrio (si legge al contrario nella pagina)
    cent = lambda nome: ris['gruppi'][nome]
    def centro(fjs):
        vv = np.concatenate([obj(x)[0] for x in fjs if obj(x) is not None]); return vv.mean(0)
    orig = {'arterie': centro(el['FMA3736']), 'arterie_polm': centro(el['FMA8612']),
            'vene': centro(el['FMA11359']), 'vene_polm': centro(el['FMA9465'])}
    for nome, fjs in classi.items():
        g = gruppo(nome, fjs, 0.6)
        if not g: continue
        v, f = g
        if nome == 'arterie':
            pezzi = [(v, f)]
            for a_fj, b_fj, modo in PONTI:
                tubo = ponte(obj(a_fj)[0], obj(b_fj)[0], modo)
                pezzi.append(tubo)
                print(f'   ponte {obj(a_fj)[2]} -> {obj(b_fj)[2]}: {np.linalg.norm(tubo[0][0]-tubo[0][-1])*1000:.0f} mm')
            v, f = unisci(pezzi)
        # grafo: lati dei triangoli + ponti fra parti vicine (entro 4 mm)
        e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
        pairs = cKDTree(v).query_pairs(0.004, output_type='ndarray')
        e = np.concatenate([e, pairs])
        w = np.linalg.norm(v[e[:, 0]] - v[e[:, 1]], axis=1) + 1e-6
        G = coo_matrix((np.concatenate([w, w]), (np.concatenate([e[:, 0], e[:, 1]]), np.concatenate([e[:, 1], e[:, 0]]))), shape=(len(v), len(v))).tocsr()
        sorg = np.argsort(np.linalg.norm(v - orig[nome], axis=1))[:30]
        from scipy.sparse.csgraph import connected_components
        ncomp, lab = connected_components(G, directed=False)
        # ogni pezzo staccato si aggancia al punto più vicino dei pezzi già raggiunti (gli spazi fra i file dell'atlante)
        raggiunti = set(lab[sorg].tolist()); extra = []
        while len(raggiunti) < ncomp:
            dentro = np.isin(lab, list(raggiunti)); albero = cKDTree(v[dentro]); idx_in = np.where(dentro)[0]
            migliore = None
            for c in set(range(ncomp)) - raggiunti:
                ii = np.where(lab == c)[0]
                dd, jj = albero.query(v[ii])
                k = int(np.argmin(dd))
                if migliore is None or dd[k] < migliore[0]: migliore = (dd[k], ii[k], idx_in[jj[k]], c)
            d0, a0, b0, c0 = migliore
            extra.append((a0, b0, d0 * 1.5 + 1e-6)); raggiunti.add(c0)
        if extra:
            ea = np.array(extra)
            G = G + coo_matrix((np.concatenate([ea[:, 2], ea[:, 2]]), (np.concatenate([ea[:, 0], ea[:, 1]]).astype(int), np.concatenate([ea[:, 1], ea[:, 0]]).astype(int))), shape=G.shape).tocsr()
        dist, pred, _ = dijkstra(G, indices=sorg, min_only=True, return_predecessors=True)
        fin = np.isfinite(dist)
        dist[~fin] = dist[fin].max()
        print(f'   {nome}: pezzi {ncomp}, agganciati {len(extra)}, non raggiunti {100*(~fin).mean():.1f}%, distanza massima {dist.max():.2f} m')
        ris['gruppi'][nome] = impacchetta(v, f, dist / 2.5)   # 0..1 = 0..2,5 m di percorso
        ris.setdefault('percorsi', []).extend(percorsi(nome, v, dist, pred))
        ris['gruppi'][nome]['flussoMax'] = 2.5
    ris['punti'] = {k: (v.round(4).tolist()) for k, v in orig.items()}
    # centri e ingombri delle parti che la pagina usa per la telecamera, il sangue nelle camere e le compressioni
    for nome, c in PUNTI.items():
        fjs = [x for x in el[c] if obj(x) is not None]
        if not fjs: print('punto mancante', nome); continue
        vv = np.concatenate([obj(x)[0] for x in fjs])
        ris['punti'][nome] = vv.mean(0).round(4).tolist()
        ris['punti'][nome + '_min'] = vv.min(0).round(4).tolist(); ris['punti'][nome + '_max'] = vv.max(0).round(4).tolist()
    json.dump(ris, open(a.uscita, 'w'))
    print('scritto', a.uscita, os.path.getsize(a.uscita) // 1024, 'KB')

if __name__ == '__main__':
    main()
