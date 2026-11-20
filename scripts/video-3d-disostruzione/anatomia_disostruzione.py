#!/usr/bin/env python3
"""anatomia_disostruzione.py — prepara i modelli anatomici del video 3D sulla disostruzione dall'atlante BodyParts3D.
Usa le funzioni di scripts/video-3d-rcp/anatomia.py (lettura, semplificazione, impacchettamento) e raggruppa le parti
delle vie aeree e della deglutizione: pelle, trachea e bronchi, epiglottide e cartilagini della laringe, esofago,
stomaco, lingua, palato molle, mandibola, polmoni, diaframma, gabbia toracica, colonna, scapole e clavicole.
Epiglottide e cartilagini della laringe stanno solo nell'albero IS-A dell'atlante: si leggono da --isa (file FJ*.obj).
Dati: «BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International».
Uso: python3 anatomia_disostruzione.py --cartella BP3D --isa CARTELLA_ISA --uscita anatomia.json
Scritto per Alessandro Cuollo il 20/11/2026.
"""
import argparse, collections, json, os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'video-3d-rcp'))
from anatomia import scarica, leggi_obj, semplifica, unisci, impacchetta   # noqa: E402

GRUPPI = {   # nome -> (concetti FMA dell'albero PART-OF, frazione di triangoli)
    'pelle':      (['FMA7163'], 0.35),
    'trachea':    (['FMA7393'], 0.7),          # albero tracheobronchiale: trachea e bronchi
    'esofago':    (['FMA7131'], 0.8),
    'stomaco':    (['FMA7148'], 0.6),
    'lingua':     (['FMA54640'], 0.7),
    'palato':     (['FMA55021'], 0.8),
    'mandibola':  (['FMA52748'], 0.5),
    'ioide':      (['FMA52749'], 0.8),
    'polmoni':    (['FMA7309', 'FMA7310'], 0.5),
    'diaframma':  (['FMA13295'], 0.6),
    'costole':    (['FMA7480'], 0.45),
    'colonna':    (['FMA9140'], 0.5),
    'scapole':    (['FMA13395', 'FMA13396', 'FMA13322', 'FMA13323'], 0.5),
    'cranio':     (['FMA46565'], 0.3),
}
ISA = {'epiglottide': ['FJ2770'], 'laringe': ['FJ2808', 'FJ2769']}   # tiroide e cricoide

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cartella', required=True); ap.add_argument('--isa', required=True); ap.add_argument('--uscita', required=True)
    a = ap.parse_args()
    d = scarica(a.cartella)
    el = collections.defaultdict(set)
    for l in open(os.path.join(a.cartella, 'partof_element_parts.txt')).read().splitlines()[1:]:
        c, _, fj = l.split('\t'); el[c].add(fj)
    ris = {'attribuzione': 'BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International',
           'gruppi': {}, 'punti': {}}
    vert = {}
    def gruppo(nome, files, fraz):
        pezzi = []
        for p in sorted(files):
            if not os.path.exists(p): print('manca', p); continue
            v, f, _ = leggi_obj(p)
            if len(f): pezzi.append(semplifica(v, f, fraz))
        if not pezzi: print('vuoto', nome); return
        v, f = unisci(pezzi)
        print(f'{nome:12s} parti {len(pezzi):3d} vertici {len(v):7d} triangoli {len(f):7d}')
        ris['gruppi'][nome] = impacchetta(v, f); vert[nome] = v
    for nome, (conc, fraz) in GRUPPI.items():
        fjs = set().union(*[el[c] for c in conc])
        gruppo(nome, [os.path.join(d, x + '.obj') for x in fjs], fraz)
    for nome, fjs in ISA.items():
        gruppo(nome, [os.path.join(a.isa, x + '.obj') for x in fjs], 0.9)
    for nome, v in vert.items():
        ris['punti'][nome] = v.mean(0).round(4).tolist()
        ris['punti'][nome + '_min'] = v.min(0).round(4).tolist(); ris['punti'][nome + '_max'] = v.max(0).round(4).tolist()
    # punti utili: cima della trachea (sotto la laringe), biforcazione, imbocco dell'esofago
    t = vert['trachea']; tr = leggi_obj(os.path.join(d, 'FJ2541.obj'))[0]
    alto = tr[tr[:, 1] > tr[:, 1].max() - 0.01].mean(0); basso = tr[tr[:, 1] < tr[:, 1].min() + 0.01].mean(0)
    e = vert['esofago']; eal = e[e[:, 1] > e[:, 1].max() - 0.01].mean(0)
    ris['punti'].update({'trachea_alto': alto.round(4).tolist(), 'carena': basso.round(4).tolist(), 'esofago_alto': eal.round(4).tolist()})
    print('trachea alto', alto.round(3), 'carena', basso.round(3), 'esofago alto', eal.round(3))
    print('esofago dietro la trachea: z esofago', round(float(e[(e[:, 1] > basso[1]) & (e[:, 1] < alto[1])][:, 2].mean()), 4),
          'z trachea', round(float(tr[:, 2].mean()), 4))
    json.dump(ris, open(a.uscita, 'w'))
    print('scritto', a.uscita, os.path.getsize(a.uscita) // 1024, 'KB')

if __name__ == '__main__':
    main()
