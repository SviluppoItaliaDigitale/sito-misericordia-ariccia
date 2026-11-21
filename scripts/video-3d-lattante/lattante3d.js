/* lattante3d.js — il lattante (4-5 mesi) e le mani di chi soccorre, fatti in codice con three.js per il video 3D
   «Lattante: soffocamento e rianimazione» della Misericordia di Ariccia (scripts/video-3d-lattante/).
   Nessun modello esterno: forme morbide a schema («non in scala»), articolate, con le proporzioni di un lattante di
   pochi mesi (testa grande rispetto al corpo, collo corto, arti corti e paffuti). Uso: const L = creaLattante(THREE); scena.add(L.radice); L.posa('prono');
   le mani: const M = creaMano(THREE, 'destra'). Scritto per Alessandro Cuollo il 20/11/2026. */
(function () {
  'use strict';

  /* ---------- geometria: un «tubo morbido» lungo l'asse y, con sezione ellittica e punte arrotondate ---------- */
  // prof(v) → { y, x, z, rx, rz } per v da 0 a 1; le punte si chiudono da sole con un profilo a cupola (cap = frazione).
  function tubo(THREE, prof, o = {}) {
    const U = o.u || 40, V = o.v || 40, cap0 = o.cap0 ?? 0.18, cap1 = o.cap1 ?? 0.18;
    const pos = [], idx = [];
    const cupola = v => {
      let e = 1;
      if (v < cap0) { const s = 1 - v / cap0; e = Math.sqrt(Math.max(0, 1 - s * s)); }
      if (v > 1 - cap1) { const s = (v - (1 - cap1)) / cap1; e = Math.min(e, Math.sqrt(Math.max(0, 1 - s * s))); }
      return e;
    };
    for (let j = 0; j <= V; j++) {
      const v = j / V, p = prof(v), e = cupola(v);
      for (let i = 0; i <= U; i++) {
        const a = i / U * Math.PI * 2;
        pos.push(p.x + Math.cos(a) * p.rx * e, p.y, p.z + Math.sin(a) * p.rz * e);
      }
    }
    const giu = prof(1).y < prof(0).y;                    // tubo percorso verso il basso: si inverte il verso delle facce
    for (let j = 0; j < V; j++) for (let i = 0; i < U; i++) {
      const a = j * (U + 1) + i, b = a + U + 1;
      if (giu) idx.push(a, a + 1, b, b, a + 1, b + 1); else idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setIndex(idx);
    // cucitura: le normali della prima e dell'ultima colonna si uniscono
    g.computeVertexNormals();
    const n = g.attributes.normal;
    for (let j = 0; j <= V; j++) {
      const a = j * (U + 1), b = a + U, s = new THREE.Vector3(n.getX(a) + n.getX(b), n.getY(a) + n.getY(b), n.getZ(a) + n.getZ(b)).normalize();
      n.setXYZ(a, s.x, s.y, s.z); n.setXYZ(b, s.x, s.y, s.z);
    }
    // le due punte: normale lungo l'asse
    const P = g.attributes.position;
    for (const [j, k] of [[0, 1], [V, V - 1]]) {           // punta: normale dal centro dell'anello vicino verso la punta
      const c = new THREE.Vector3(); for (let i = 0; i < U; i++) c.add(new THREE.Vector3().fromBufferAttribute(P, k * (U + 1) + i));
      c.multiplyScalar(1 / U); const d = new THREE.Vector3().fromBufferAttribute(P, j * (U + 1)).sub(c).normalize();
      for (let i = 0; i <= U; i++) n.setXYZ(j * (U + 1) + i, d.x, d.y, d.z);
    }
    return g;
  }
  const lin = (a, b, v) => a + (b - a) * v;
  // capsula conica fra y0 e y1, raggi r0 → r1, con un leggero rigonfiamento a metà (arti paffuti)
  function arto(THREE, y0, y1, r0, r1, gonfio = 0.08, schiaccia = 1) {
    return tubo(THREE, v => { const r = lin(r0, r1, v) * (1 + gonfio * Math.sin(Math.PI * v)); return { x: 0, y: lin(y0, y1, v), z: 0, rx: r, rz: r * schiaccia }; },
      { cap0: 0.22, cap1: 0.22 });
  }
  function ellissoide(THREE, rx, ry, rz, seg = 40) {
    const g = new THREE.SphereGeometry(1, seg, Math.round(seg * 0.75)); g.scale(rx, ry, rz); return g;
  }

  /* ---------- materiali ---------- */
  function materiali(THREE, o = {}) {
    const m = (c, r = 0.62, extra = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: r, metalness: 0 }, extra));
    return {
      pelle: m(o.pelle || 0xf3cdb0, 0.58),
      guance: m(0xf2b9a0, 0.6),
      body: m(o.body || 0xa9d3f2, 0.8),            // tutina azzurra, come nelle figure delle linee guida IRC
      bordo: m(0x7fb9e6, 0.8),
      occhi: m(0x2a2f3a, 0.25),
      luce: new THREE.MeshBasicMaterial({ color: 0xffffff }),
      bocca: m(0x9a7066, 0.7),
      palpebra: m(0x9c7258, 0.8),
      sopracciglia: m(0xc9a07e, 0.8),
      capelli: m(0xb8875e, 0.85)
    };
  }

  /* ============================================================ il lattante ============================================ */
  function creaLattante(THREE, o = {}) {
    const PARTI_MH = [];
    const M = materiali(THREE, o);
    const mesh = (g, m) => { const x = new THREE.Mesh(g, m); x.castShadow = x.receiveShadow = true; return x; };
    const G = {};                                               // giunti
    const radice = new THREE.Group(); radice.name = 'lattante';
    const bacino = new THREE.Group(); radice.add(bacino); G.bacino = bacino;

    // --- tronco: dal pavimento pelvico (y = -0,035) alle spalle (y = 0,215); pancia tonda, torace un po' più stretto
    const profiloTronco = y => {
      const pancia = Math.exp(-Math.pow((y - 0.05) / 0.07, 2));         // la pancia sporge in avanti
      const torace = Math.exp(-Math.pow((y - 0.14) / 0.05, 2));
      const rx = 0.058 + 0.014 * pancia + 0.004 * torace - 0.014 * Math.max(0, (y - 0.165) / 0.035);
      const rz = 0.049 + 0.013 * pancia + 0.002 * torace - 0.008 * Math.max(0, (y - 0.165) / 0.035);
      return { x: 0, y, z: 0.004 * pancia, rx, rz };
    };
    const CAP_TRONCO = 0.12, Y1_TRONCO = 0.2;
    const tronco = tubo(THREE, v => profiloTronco(lin(-0.045, Y1_TRONCO, v)), { cap0: 0.16, cap1: CAP_TRONCO, u: 48, v: 56 });
    // superficie anteriore del tronco sulla linea mediana (x = 0), con la cupola delle spalle
    const zFronteTronco = y => { const p = profiloTronco(y), v = (y + 0.045) / 0.245; let e = 1;
      if (v > 1 - CAP_TRONCO) { const q = (v - (1 - CAP_TRONCO)) / CAP_TRONCO; e = Math.sqrt(Math.max(0, 1 - q * q)); }
      return p.z + p.rz * e; };
    const busto = mesh(tronco, M.body); bacino.add(busto); G.busto = busto;
    // scollo e polsini della tutina (un filo più scuro)
    const scollo = mesh(new THREE.TorusGeometry(0.031, 0.0045, 10, 36), M.bordo); scollo.rotation.x = Math.PI / 2; scollo.position.set(0, 0.196, 0.002); bacino.add(scollo);

    // --- collo e testa
    const collo = new THREE.Group(); collo.position.set(0, 0.19, 0.002); bacino.add(collo); G.collo = collo;
    collo.add(mesh(arto(THREE, -0.012, 0.022, 0.034, 0.033, 0), M.pelle));
    const testa = new THREE.Group(); testa.position.set(0, 0.006, 0.008); testa.scale.setScalar(1.05); collo.add(testa); G.testa = testa;
    const CT = new THREE.Vector3(0, 0.068, 0.004);
    const OCCHI_APERTI = [], OCCHI_CHIUSI = [];              // centro della testa (cranio)
    // cranio grande e tondo; viso più basso e largo, guance piene (dentro la stessa superficie, niente palline)
    const rTesta = y => {
      const r = 0.067 * Math.sqrt(Math.max(0, 1 - Math.pow((y - 0.072) / 0.075, 2)));
      return r * (1 + 0.075 * Math.exp(-Math.pow((y - 0.036) / 0.024, 2)));
    };
    const vT = y => (y + 0.003) / 0.15, dzT = y => -0.004 * Math.sin(Math.PI * vT(y)) + 0.006 * Math.exp(-Math.pow((y - 0.03) / 0.02, 2));
    const cranio = tubo(THREE, v => {
      const y = lin(-0.003, 0.147, v), r = rTesta(y);
      return { x: 0, y, z: dzT(y), rx: r * 0.95, rz: r * 1.03 };
    }, { cap0: 0.001, cap1: 0.001, u: 64, v: 72 });
    testa.add(mesh(cranio, M.pelle));
    // punto della superficie del viso all'altezza y e di lato x, con la normale (per appoggiarci occhi, naso, bocca)
    const sulViso = (x, y, dentro = 0) => {
      const r = rTesta(y), rx = r * 0.95, rz = r * 1.03, c = Math.max(-1, Math.min(1, x / rx)), sn = Math.sqrt(1 - c * c);
      const n = new THREE.Vector3(c / rx, 0, sn / rz).normalize();
      return { p: new THREE.Vector3(x, y, dzT(y) + sn * rz).addScaledVector(n, -dentro), n };
    };
    const appoggia = (obj, x, y, dentro) => { const s = sulViso(x, y, dentro); obj.position.copy(s.p); obj.lookAt(s.p.clone().add(s.n)); testa.add(obj); return obj; };
    for (const s of [-1, 1]) {
      const orecchio = mesh(ellissoide(THREE, 0.007, 0.016, 0.011), M.pelle); orecchio.position.set(s * 0.061, 0.064, -0.006); orecchio.rotation.z = s * 0.15; testa.add(orecchio);
      // occhi: tondi, scuri, con il riflesso; a metà della testa, come nei lattanti
      const occhio = appoggia(mesh(ellissoide(THREE, 0.0068, 0.0078, 0.004), M.occhi), s * 0.022, 0.064, 0.0012);
      const lucina = mesh(ellissoide(THREE, 0.002, 0.002, 0.0012, 12), M.luce); lucina.position.set(0.002, 0.0024, 0.0034); occhio.add(lucina);
      OCCHI_APERTI.push(occhio);
      // occhi chiusi (lattante che non risponde): palpebra a mezzaluna, ciglia verso il basso
      // palpebra chiusa: un tratto quasi dritto, appena curvo verso il basso
      const chiuso = appoggia(new THREE.Group(), s * 0.022, 0.0635, -0.0004);
      const ARCO = Math.PI * 0.2, RA = 0.026;
      const linea = new THREE.Mesh(new THREE.TorusGeometry(RA, 0.00095, 6, 24, ARCO), M.palpebra);
      linea.rotation.z = -Math.PI / 2 - ARCO / 2; linea.position.set(0, RA, 0); chiuso.add(linea);
      chiuso.visible = false; OCCHI_CHIUSI.push(chiuso);
      const ciglio = new THREE.Mesh(new THREE.TorusGeometry(0.0105, 0.001, 6, 24, Math.PI * 0.6), M.sopracciglia);
      appoggia(ciglio, s * 0.022, 0.071, 0.0004); ciglio.rotateZ(Math.PI * 0.2); OCCHI_APERTI.push(ciglio);   // sopracciglia solo da sveglio
    }
    appoggia(mesh(ellissoide(THREE, 0.0072, 0.0052, 0.0055), M.pelle), 0, 0.051, 0.0022);                     // naso
    // bocca neutra: un tratto piccolo, piatto e scuro (niente sorriso: è una scena di soccorso)
    const bocca = appoggia(mesh(ellissoide(THREE, 0.0048, 0.001, 0.0006, 20), M.bocca), 0, 0.03, 0.0003);
    G.mento = new THREE.Object3D(); G.mento.position.set(0, 0.014, 0.048); testa.add(G.mento);
    G.bocca = new THREE.Object3D(); G.bocca.position.copy(sulViso(0, 0.036).p); testa.add(G.bocca);

    // --- braccia (spalla → gomito → polso), manine chiuse a pugno morbido
    for (const [s, n] of [[1, 'Sx'], [-1, 'Dx']]) {          // +x = lato sinistro del lattante
      const spalla = new THREE.Group(); spalla.position.set(s * 0.062, 0.165, -0.002); bacino.add(spalla); G['spalla' + n] = spalla;
      spalla.add(mesh(ellissoide(THREE, 0.026, 0.026, 0.025), M.body));
      spalla.add(mesh(arto(THREE, 0.006, -0.078, 0.0225, 0.0195, 0.14), M.pelle));
      const manica = mesh(arto(THREE, 0.01, -0.036, 0.0265, 0.025, 0.02), M.body); spalla.add(manica);
      const gomito = new THREE.Group(); gomito.position.set(0, -0.072, 0); spalla.add(gomito); G['gomito' + n] = gomito;
      gomito.add(mesh(ellissoide(THREE, 0.0178, 0.0178, 0.0178), M.pelle));
      gomito.add(mesh(arto(THREE, 0.01, -0.07, 0.019, 0.016, 0.14), M.pelle));
      const polso = new THREE.Group(); polso.position.set(0, -0.066, 0); gomito.add(polso); polso.add(mesh(ellissoide(THREE, 0.0155, 0.014, 0.0145), M.pelle)); G['polso' + n] = polso;
      if (o.mh) {                                     // mano vera a cinque dita (MakeHuman, CC0), in scala da lattante
        const m = attaccaMH(THREE, o.mh, `mano.${s > 0 ? 'L' : 'R'}`, polso, { pelle: o.pelle || 0xf3cdb0, scala: 0.29, asse: new THREE.Vector3(0, -1, 0), palmo: new THREE.Vector3(-s * 0.6, 0, 0.8).normalize(), radice: 'wrist', punta: 'finger3-1' });
        // manina da lattante: dita più corte e più paffute (ossa scalate), morbide e semiflesse, mai ad artiglio
        for (let d = 1; d <= 5; d++) { const o0 = m.ossa[`finger${d}-1.${m.lato}`]; if (o0) o0.scale.set(1.35, d === 1 ? 0.85 : 0.72, 1.35); }
        for (let d = 1; d <= 5; d++) for (let f = 1; f <= 3; f++) m.flessione(`finger${d}-${f}.${m.lato}`, d === 1 ? 0.2 : [0, 0.45, 0.5, 0.35][f], d === 1 ? 0 : (d - 3.5) * -0.04);
        PARTI_MH.push(m);
      } else {
      const palmo = mesh(ellissoide(THREE, 0.0175, 0.022, 0.0135), M.pelle); palmo.position.set(0, -0.019, 0.002); polso.add(palmo);
      const dita = mesh(ellissoide(THREE, 0.016, 0.011, 0.012), M.pelle); dita.position.set(0, -0.034, 0.008); polso.add(dita);
      const pollice = mesh(ellissoide(THREE, 0.0065, 0.011, 0.0065), M.pelle); pollice.position.set(-s * 0.012, -0.024, 0.013); pollice.rotation.z = -s * 0.5; polso.add(pollice);
      }
    }
    // --- gambe (anca → ginocchio → caviglia), cosce paffute
    for (const [s, n] of [[1, 'Sx'], [-1, 'Dx']]) {
      const anca = new THREE.Group(); anca.position.set(s * 0.036, -0.008, 0.006); bacino.add(anca); G['anca' + n] = anca;
      anca.add(mesh(arto(THREE, 0.016, -0.092, 0.037, 0.025, 0.16), M.pelle));
      const coscia = mesh(arto(THREE, 0.02, -0.024, 0.0395, 0.038, 0), M.body); anca.add(coscia);   // orlo della tutina
      const ginocchio = new THREE.Group(); ginocchio.position.set(0, -0.088, 0); anca.add(ginocchio); G['ginocchio' + n] = ginocchio;
      ginocchio.add(mesh(ellissoide(THREE, 0.0232, 0.0232, 0.0232), M.pelle));
      ginocchio.add(mesh(arto(THREE, 0.012, -0.08, 0.025, 0.0185, 0.16), M.pelle));
      const caviglia = new THREE.Group(); caviglia.position.set(0, -0.078, 0); caviglia.add(mesh(ellissoide(THREE, 0.0168, 0.0168, 0.0168), M.pelle)); ginocchio.add(caviglia); G['caviglia' + n] = caviglia;
      const piede = mesh(tubo(THREE, v => ({ x: 0, y: -0.012 - 0.004 * Math.sin(Math.PI * v), z: lin(-0.016, 0.05, v),
        rx: 0.017 * (0.8 + 0.3 * v), rz: 0.0125 }), { cap0: 0.3, cap1: 0.3 }), M.pelle);
      // il tubo va lungo y: lo giro perché il piede vada in avanti
      piede.geometry = (function () {
        const g = tubo(THREE, v => ({ x: 0, y: lin(-0.018, 0.052, v), z: 0, rx: 0.0165 * (0.85 + 0.3 * v), rz: 0.0125 }), { cap0: 0.32, cap1: 0.36 });
        g.rotateX(Math.PI / 2); g.translate(0, -0.012, 0); return g;
      })();
      if (o.mh) {                                     // piede vero a cinque dita (MakeHuman, CC0), in scala da lattante
        const m = attaccaMH(THREE, o.mh, `piede.${s > 0 ? 'L' : 'R'}`, caviglia, { pelle: o.pelle || 0xf3cdb0, scala: 0.33, asse: new THREE.Vector3(0, 0, 1), palmo: new THREE.Vector3(0, -1, 0), radice: 'foot', punta: 'toe3-1', piede: true });
        PARTI_MH.push(m);
      } else caviglia.add(piede);
    }

    // --- punti di riferimento (per schede, mani e controlli)
    const P = {};
    const punto = (nome, padre, x, y, z) => { const p = new THREE.Object3D(); p.position.set(x, y, z); p.name = nome; padre.add(p); P[nome] = p; };
    // sterno: dal giugulo (y 0,183) alla punta (xifoide, y 0,11); la metà inferiore è centrata a y ≈ 0,128
    punto('giugulo', bacino, 0, 0.183, 0.047);
    punto('xifoide', bacino, 0, 0.11, 0.058);
    punto('sternoBasso', bacino, 0, 0.128, 0.058);                 // centro della metà inferiore dello sterno
    punto('scapole', bacino, 0, 0.105, -0.055);                     // fra le scapole, parte alta-media del dorso, lontano dal collo
    punto('nuca', testa, 0, 0.05, -0.062);
    G.punti = P;

    /* ---------- sterno in trasparenza (schema): profilo dal giugulo alla punta dello xifoide, metà inferiore in giallo ---------- */
    const sterno = new THREE.Group(); sterno.visible = false; bacino.add(sterno); G.sterno = sterno;
    (function () {
      const Y0 = 0.183, Y1 = 0.11, YX = 0.098;                       // giugulo, fine del corpo dello sterno, punta dello xifoide
      const largo = y => y > 0.165 ? lin(0.0075, 0.0115, (y - 0.165) / 0.018)            // manubrio, più largo in alto
        : y > Y1 ? 0.0075 : 0.0075 * Math.max(0, (y - YX) / (Y1 - YX));                 // corpo, poi xifoide a punta
      const sopra = 0.0009;
      const punto = (x, y) => { const rx = profiloTronco(y).rx; return new THREE.Vector3(x, y, zFronteTronco(y) * Math.sqrt(Math.max(0, 1 - Math.pow(x / rx, 2))) + sopra - (1 - Math.sqrt(Math.max(0, 1 - Math.pow(x / rx, 2)))) * 0.0); };
      // contorno
      const pts = [];
      for (let k = 0; k <= 40; k++) { const y = lin(Y0, YX, k / 40); pts.push(punto(largo(y), y)); }
      for (let k = 40; k >= 0; k--) { const y = lin(Y0, YX, k / 40); pts.push(punto(-largo(y), y)); }
      pts.push(pts[0].clone());
      const contorno = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 200, 0.0009, 6, false),
        new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.95 }));
      sterno.add(contorno);
      // riempimento: tutto lo sterno appena azzurro, la metà inferiore (fra il centro e la fine del corpo) gialla
      const striscia = (ya, yb, colore, opac) => {
        const pos = [], idx = [], N = 24;
        for (let k = 0; k <= N; k++) { const y = lin(ya, yb, k / N), w = largo(y); for (const x of [-w, w]) { const p = punto(x, y); p.z += 0.0002; pos.push(p.x, p.y, p.z); } }
        for (let k = 0; k < N; k++) { const a = 2 * k; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
        const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx);
        return new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: colore, transparent: true, opacity: opac, side: THREE.DoubleSide, depthWrite: false }));
      };
      const meta = (Y0 + Y1) / 2;                                    // metà dello sterno (senza lo xifoide)
      sterno.add(striscia(Y0, meta, 0xbfe3ff, 0.55), striscia(meta, Y1, 0xfceb0c, 0.85), striscia(Y1, YX, 0xbfe3ff, 0.55));
      G.sternoMeta = meta; G.sternoDati = { Y0, Y1, YX, meta, largo };
      G.sternoGiallo = sterno.children[2];
    })();

    /* ---------- pose ---------- */
    const g = (n, x = 0, y = 0, z = 0) => G[n].rotation.set(x, y, z);
    const POSE = {
      // tenuto in piedi, davanti a noi: braccia morbide, gambe un po' piegate «a ranocchio»
      inPiedi() {
        g('collo'); g('testa', 0.04); g('bacino');
        g('spallaSx', 0.15, 0, 0.42); g('spallaDx', 0.15, 0, -0.42);
        g('gomitoSx', -0.75, 0, 0); g('gomitoDx', -0.75, 0, 0);
        g('polsoSx', 0, 0, 0); g('polsoDx', 0, 0, 0);
        g('ancaSx', -0.55, 0, 0.32); g('ancaDx', -0.55, 0, -0.32);
        g('ginocchioSx', 0.85); g('ginocchioDx', 0.85);
        g('cavigliaSx', -0.3); g('cavigliaDx', -0.3);
      },
      // a pancia in giù sull'avambraccio: gambe a cavalcioni, braccia ai lati, testa diritta (sostenuta dalla mano)
      prono() {
        g('collo', -0.1); g('testa', -0.12); g('bacino');
        g('spallaSx', -1.25, 0, 0.55); g('spallaDx', -1.25, 0, -0.55);
        g('gomitoSx', -0.45); g('gomitoDx', -0.45);
        g('ancaSx', -1.15, 0, 0.62); g('ancaDx', -1.15, 0, -0.62);
        g('ginocchioSx', 1.25); g('ginocchioDx', 1.25);
        g('cavigliaSx', -0.2); g('cavigliaDx', -0.2);
      },
      // supino su un piano rigido, testa in posizione neutra, braccia aperte, gambe rilassate
      supino() {
        g('collo', 0); g('testa', 0); g('bacino');
        g('spallaSx', 0.05, 0, 0.95); g('spallaDx', 0.05, 0, -0.95);
        g('gomitoSx', -0.25, 0, 0); g('gomitoDx', -0.25, 0, 0);
        g('ancaSx', -0.35, -0.3, 0.42); g('ancaDx', -0.35, 0.3, -0.42);
        g('ginocchioSx', 0.6); g('ginocchioDx', 0.6);
        g('cavigliaSx', 0.25); g('cavigliaDx', 0.25);
      }
    };
    // espressione: 'sveglio' (occhi aperti) o 'incosciente' (occhi chiusi)
    function mostraSterno(si) { sterno.visible = !!si; }
    // Controllo automatico (revisione del medico del 20/11/2026): il giallo copre la metà inferiore del corpo dello sterno
    // (50% ± 2% della sua lunghezza, dal punto medio alla fine del corpo, sopra lo xifoide) e ogni punto di contatto dei
    // pollici (vettori del mondo) sta dentro il giallo. Restituisce i problemi nel formato di window.__controlli.
    function controlloSterno(contatti = []) {
      const pr = [], D = G.sternoDati, pos = G.sternoGiallo.geometry.attributes.position;
      let a = Infinity, b = -Infinity; for (let i = 0; i < pos.count; i++) { const y = pos.getY(i); a = Math.min(a, y); b = Math.max(b, y); }
      const quota = (b - a) / (D.Y0 - D.Y1);
      if (Math.abs(quota - 0.5) > 0.02) pr.push({ tipo: 'sterno', dettagli: `il giallo copre il ${(quota * 100).toFixed(1)}% dello sterno, non il 50%` });
      if (Math.abs(a - D.Y1) > 0.0005 || Math.abs(b - D.meta) > 0.0005) pr.push({ tipo: 'sterno', dettagli: `giallo da y ${a.toFixed(4)} a ${b.toFixed(4)}, atteso da ${D.Y1} a ${D.meta.toFixed(4)}` });
      radice.updateMatrixWorld(true);
      contatti.forEach((c, k) => {
        const l = bacino.worldToLocal(c.clone());
        const mezza = D.largo(Math.min(Math.max(l.y, D.Y1), D.meta)) + 0.002;   // dentro il giallo (con 2 mm di tolleranza)
        if (l.y < D.Y1 || l.y > D.meta || Math.abs(l.x) > mezza) pr.push({ tipo: 'pollici', dettagli: `contatto del pollice ${k + 1} fuori dal giallo, la metà inferiore dello sterno (x ${l.x.toFixed(4)}, y ${l.y.toFixed(4)}; ammesso y da ${D.Y1} a ${D.meta.toFixed(4)}, |x| fino a ${mezza.toFixed(4)})` });
      });
      // i due polpastrelli affiancati: a meno di 1 cm l'uno dall'altro (medico, 21/11/2026)
      if (contatti.length >= 2) { const d = contatti[0].distanceTo(contatti[1]); if (d >= 0.01) pr.push({ tipo: 'pollici', dettagli: `polpastrelli dei due pollici a ${(d * 100).toFixed(1)} cm, non affiancati (massimo 1 cm)` }); }
      else if (contatti.length === 1) pr.push({ tipo: 'pollici', dettagli: 'controllato un solo pollice: servono tutti e due' });
      return pr;
    }
    // quanto un punto del mondo sta dentro il tronco: < 1 dentro, 1 sulla pelle (ellisse della sezione a quella altezza)
    function dentroTronco(pw) { const l = bacino.worldToLocal(pw.clone()); if (l.y < -0.045 || l.y > 0.2) return 9;
      const p = profiloTronco(l.y); return Math.hypot(l.x / p.rx, (l.z - p.z) / p.rz); }
    function espressione(nome) { const c = nome === 'incosciente'; OCCHI_APERTI.forEach(o => o.visible = !c); OCCHI_CHIUSI.forEach(o => o.visible = c); }
    return { radice, G, P, PARTI_MH, espressione, mostraSterno, controlloSterno, dentroTronco, sezione: y => profiloTronco(y), posa: nome => { POSE[nome](); radice.updateMatrixWorld(true); }, materiali: M };
  }

  /* ============================================================ la mano dell'adulto ===================================== */
  // Sistema della mano: polso nell'origine, dita verso -z, palmo verso -y, +x a destra (guardando il dorso).
  // lato 'destra' → pollice verso -x; 'sinistra' → pollice verso +x. Ogni dito ha tre falangi che si piegano (piega 0..1).
  function creaMano(THREE, lato = 'destra', o = {}) {
    const s = lato === 'destra' ? -1 : 1;                 // lato del pollice
    const pelle = new THREE.MeshStandardMaterial({ color: o.pelle || 0xd9a07c, roughness: 0.55 });
    const manica = new THREE.MeshStandardMaterial({ color: o.manica || 0x003f85, roughness: 0.75 });
    const mesh = (g, m = pelle) => { const x = new THREE.Mesh(g, m); x.castShadow = x.receiveShadow = true; return x; };
    const radice = new THREE.Group(); radice.name = 'mano-' + lato;
    // avambraccio (va verso +z dal polso), con la manica blu del soccorritore
    const avambraccio = new THREE.Group(); radice.add(avambraccio);
    const ga = arto(THREE, 0.0, 0.25, 0.027, 0.04, 0.05, 0.78); ga.rotateX(Math.PI / 2); avambraccio.add(mesh(ga));
    const gm = arto(THREE, 0.2, 0.42, 0.05, 0.056, 0.0, 0.85); gm.rotateX(Math.PI / 2); avambraccio.add(mesh(gm, manica));
    // palmo: tavoletta morbida
    const palmo = tubo(THREE, v => ({ x: 0, y: lin(0.016, -0.094, v), z: 0, rx: lin(0.029, 0.04, Math.min(1, v * 1.6)),
      rz: lin(0.017, 0.012, v) * (1 + 0.25 * Math.sin(Math.PI * v)) }), { cap0: 0.3, cap1: 0.22, u: 48 });
    palmo.rotateX(Math.PI / 2);                          // da y a -z
    radice.add(mesh(palmo));
    // eminenze del palmo: tenare (sotto il pollice) e ipotenare (lato del mignolo)
    const tenare = mesh(ellissoide(THREE, 0.017, 0.013, 0.03)); tenare.position.set(s * 0.02, -0.006, -0.03); radice.add(tenare);
    const ipotenare = mesh(ellissoide(THREE, 0.013, 0.011, 0.034)); ipotenare.position.set(-s * 0.026, -0.005, -0.05); radice.add(ipotenare);
    const unghia = new THREE.MeshStandardMaterial({ color: 0xf2cfc0, roughness: 0.35 });
    // cinque dita anatomiche: pollice con metacarpo e 2 falangi, le altre quattro con 3 falangi (falange prossimale,
    // media, distale), lunghezze diverse (medio il più lungo, mignolo il più corto), nocche su un arco, unghie
    const dita = [];
    const DITA = [ // nome, x della nocca (+ = lato del pollice), z della nocca, falangi (m), raggio
      { nome: 'indice', x: 0.027, z: -0.09, l: [0.04, 0.024, 0.019], r: 0.009 },
      { nome: 'medio', x: 0.009, z: -0.094, l: [0.045, 0.028, 0.02], r: 0.0094 },
      { nome: 'anulare', x: -0.009, z: -0.091, l: [0.042, 0.026, 0.019], r: 0.0088 },
      { nome: 'mignolo', x: -0.026, z: -0.084, l: [0.033, 0.019, 0.017], r: 0.0078 }
    ];
    const DITI = {};
    for (const d of DITA) {
      const baseDito = new THREE.Group(); baseDito.position.set(s * d.x, 0.0, d.z); baseDito.userData.dito = d.nome; radice.add(baseDito);
      let padre = baseDito; const f = [];
      d.l.forEach((L, k) => {
        const giunto = new THREE.Group(); if (k) giunto.position.set(0, 0, -d.l[k - 1]); padre.add(giunto);
        const r0 = d.r * (1 - 0.08 * k), r1 = d.r * (0.92 - 0.08 * k);
        const gf = arto(THREE, 0.003, -L + (k === 2 ? 0.0 : 0.002), r0, r1, 0, 0.86); gf.rotateX(Math.PI / 2);
        const falange = mesh(gf); falange.userData = { dito: d.nome, falange: k + 1, lunghezza: L }; giunto.add(falange);
        const nocca = mesh(ellissoide(THREE, r0 * 1.0, r0 * 0.9, r0 * 1.0, 20)); giunto.add(nocca);
        if (k === 2) {
          const polpa = mesh(ellissoide(THREE, r1 * 1.0, r1 * 0.88, r1 * 1.05, 20)); polpa.position.z = -L + r1 * 0.6; giunto.add(polpa);
          const u = mesh(ellissoide(THREE, r1 * 0.72, 0.0013, L * 0.36, 16), unghia); u.position.set(0, r1 * 0.8, -L * 0.6); u.userData.unghia = d.nome; giunto.add(u);
        }
        f.push(giunto); padre = giunto;
      });
      dita.push(f); DITI[d.nome] = baseDito;
    }
    // pollice: il metacarpo parte dal lato del polso (lato radiale), poi falange prossimale e distale con l'unghia
    const pBase = new THREE.Group(); pBase.position.set(s * 0.028, -0.004, -0.018); pBase.userData.dito = 'pollice'; radice.add(pBase);
    const met = arto(THREE, 0.0, -0.036, 0.0128, 0.011, 0.05, 0.9); met.rotateX(Math.PI / 2); const metM = mesh(met); metM.userData = { dito: 'pollice', metacarpo: true }; pBase.add(metM);
    const p1 = new THREE.Group(); p1.position.set(0, 0, -0.036); pBase.add(p1);
    const gp1 = arto(THREE, 0.004, -0.025, 0.0106, 0.0098, 0, 0.88); gp1.rotateX(Math.PI / 2);
    const f1 = mesh(gp1); f1.userData = { dito: 'pollice', falange: 1, lunghezza: 0.025 }; p1.add(f1); p1.add(mesh(ellissoide(THREE, 0.0107, 0.0097, 0.0107, 20)));
    const p2 = new THREE.Group(); p2.position.set(0, 0, -0.025); p1.add(p2);
    const gp2 = arto(THREE, 0.004, -0.021, 0.0099, 0.009, 0, 0.85); gp2.rotateX(Math.PI / 2);
    const f2 = mesh(gp2); f2.userData = { dito: 'pollice', falange: 2, lunghezza: 0.022 }; p2.add(f2); p2.add(mesh(ellissoide(THREE, 0.0099, 0.0089, 0.0099, 20)));
    const up = mesh(ellissoide(THREE, 0.0072, 0.0013, 0.009, 16), unghia); up.position.set(0, -0.0086, -0.014); up.userData.unghia = 'pollice'; p2.add(up);   // l'unghia sta sul dorso del pollice
    const puntaPollice = new THREE.Object3D(); puntaPollice.position.set(0, 0, -0.022); p2.add(puntaPollice);
    function piega(quanto, polliceFuori = 0.6, polliceGiu = 0.3, polliceFlesso = 0.15) {
      dita.forEach((f, i) => f.forEach((gi, k) => gi.rotation.set(-quanto * [1.05, 1.35, 0.9][k] * (1 + 0.04 * i), 0, 0)));
      pBase.rotation.set(-polliceGiu, s * polliceFuori, 0);
      p1.rotation.set(-polliceFlesso, 0, 0); p2.rotation.set(-polliceFlesso * 1.3, 0, 0);
    }
    // piega un dito (0 indice … 3 mignolo) con tre angoli, e lo apre di lato (abduzione, radianti)
    function piegaDito(i, a1, a2, a3, apri = 0) { const f = dita[i]; f[0].rotation.set(-a1, s * apri, 0); f[1].rotation.set(-a2, 0, 0); f[2].rotation.set(-a3, 0, 0); }
    function punteDita() { radice.updateMatrixWorld(true); return dita.map((f, i) => f[2].localToWorld(new THREE.Vector3(0, -DITA[i].r * 0.5, -DITA[i].l[2] + 0.002))); }
    // punti lungo ogni dito (per il controllo della compenetrazione)
    function puntiDita() {
      radice.updateMatrixWorld(true); const out = [];
      dita.forEach((f, i) => f.forEach((g, k) => { for (const q of [0.3, 0.7, 1.0]) out.push({ dito: DITA[i].nome, p: g.localToWorld(new THREE.Vector3(0, -DITA[i].r * 0.6, -DITA[i].l[k] * q)) }); }));
      return out;
    }
    // Controllo automatico (21/11/2026, «il corpo umano ha 5 dita per ogni mano»): esattamente 5 dita visibili, il pollice
    // con 2 falangi e le altre con 3, medio il più lungo e mignolo il più corto. Restituisce i problemi per __controlli.
    function controlloDita() {
      const pr = [], conta = {}, lung = {};
      const visibile = o => { for (let x = o; x; x = x.parent) if (!x.visible) return false; return true; };
      radice.traverse(o => { if (o.isMesh && o.userData.falange && visibile(o)) { const n = o.userData.dito; conta[n] = (conta[n] || 0) + 1; lung[n] = (lung[n] || 0) + o.userData.lunghezza; } });
      const nomi = Object.keys(conta);
      if (nomi.length !== 5) pr.push({ tipo: 'dita', dettagli: `${radice.name}: ${nomi.length} dita visibili invece di 5 (${nomi.join(', ') || 'nessuna'})` });
      if (conta.pollice !== 2) pr.push({ tipo: 'dita', dettagli: `${radice.name}: il pollice ha ${conta.pollice || 0} falangi invece di 2` });
      for (const n of ['indice', 'medio', 'anulare', 'mignolo']) if (conta[n] !== 3) pr.push({ tipo: 'dita', dettagli: `${radice.name}: ${n} con ${conta[n] || 0} falangi invece di 3` });
      if (nomi.length === 5 && !(lung.medio > lung.indice && lung.medio > lung.anulare && lung.mignolo < lung.indice && lung.mignolo < lung.anulare))
        pr.push({ tipo: 'dita', dettagli: `${radice.name}: lunghezze delle dita non anatomiche` });
      return pr;
    }
    // punta il pollice verso un punto del mondo (la falange si piega appena); restituisce la distanza che resta
    const LP = 0.036 + 0.025 + 0.022;
    // «verso»: direzione del mondo verso cui si piega il polpastrello (per esempio dentro il torace)
    function mira(bersaglio, flesso = 0.12, verso = new THREE.Vector3(0, -1, 0)) {
      radice.updateMatrixWorld(true);
      const base = pBase.getWorldPosition(new THREE.Vector3());
      const locale = radice.worldToLocal(bersaglio.clone()).sub(pBase.position).normalize();
      const q = radice.getWorldQuaternion(new THREE.Quaternion()).invert();
      const giu = verso.clone().applyQuaternion(q);                          // direzione di flessione, nel sistema della mano
      const z = locale.clone().negate(), y = giu.clone().negate(); y.sub(z.clone().multiplyScalar(y.dot(z))).normalize();
      const x = new THREE.Vector3().crossVectors(y, z);
      pBase.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, y, z));
      p1.rotation.set(-flesso, 0, 0); p2.rotation.set(-flesso * 1.2, 0, 0);
      return base.distanceTo(bersaglio) - LP;
    }
    // pollice a due tratti: il metacarpo punta verso «mcp» (nocca del pollice), le falangi verso «punta»; si piega verso «verso»
    function miraCatena(mcp, punta, verso = new THREE.Vector3(0, -1, 0), flesso = 0.08) {
      const base = (o, dirLocale, giuLocale) => {
        const z = dirLocale.clone().normalize().negate(), y = giuLocale.clone().negate(); y.sub(z.clone().multiplyScalar(y.dot(z))).normalize();
        o.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(new THREE.Vector3().crossVectors(y, z), y, z));
      };
      radice.updateMatrixWorld(true);
      const qR = radice.getWorldQuaternion(new THREE.Quaternion()).invert();
      base(pBase, radice.worldToLocal(mcp.clone()).sub(pBase.position), verso.clone().applyQuaternion(qR));
      pBase.updateMatrixWorld(true);
      const qB = pBase.getWorldQuaternion(new THREE.Quaternion()).invert();
      base(p1, pBase.worldToLocal(punta.clone()).sub(p1.position), verso.clone().applyQuaternion(qB));
      p2.rotation.set(-flesso, 0, 0);
      radice.updateMatrixWorld(true);
      return puntaPollice.getWorldPosition(new THREE.Vector3()).distanceTo(punta);
    }
    // polso: estensione (l'avambraccio sale dal lato del dorso della mano), in radianti
    function polso(angolo = 0) { avambraccio.rotation.set(-angolo, 0, 0); }
    // punto di contatto del polpastrello: 8 mm prima della punta, sul lato della flessione
    function contattoPollice() { p2.updateMatrixWorld(true); return p2.localToWorld(new THREE.Vector3(0, -0.009, -0.014)); }
    return { radice, piega, piegaDito, punteDita, puntiDita, controlloDita, DITI, mira, miraCatena, contattoPollice, polso, dita, pollice: [pBase, p1, p2], puntaPollice, avambraccio, pelle, manica };
  }

  /* ============================================================ parti umane vere da MakeHuman (CC0) ====================== */
  // dati: il JSON di mani_makehuman.py; nome: «braccio.R», «mano.L», «piede.R»… Restituisce una SkinnedMesh con le ossa
  // dello scheletro «default» di MakeHuman (falangi di mani e piedi). flessione(osso, a, apri): piega l'osso di «a»
  // radianti attorno al suo asse di flessione (x a riposo) e lo apre di «apri» (asse z). Vertici in metri.
  function creaParteMH(THREE, dati, nome, o = {}) {
    const P = dati.parti[nome], dec = (s, T) => { const b = atob(s), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return new T(u.buffer); };
    const pos = dec(P.posizioni, Float32Array), idx = dec(P.indici, Uint32Array);
    const si = dec(P.ossaIndici, Uint16Array), sw = dec(P.ossaPesi, Float32Array);
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setIndex(new THREE.BufferAttribute(idx, 1));
    g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(si, 4)); g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));
    g.computeVertexNormals();
    // colore per vertice: pelle, e la manica blu sull'avambraccio oltre una certa distanza dal polso (solo braccio)
    if (o.manica) {
      const polso = P.ossa.find(b => b.nome.startsWith('wrist')), w = new THREE.Vector3(...polso.testa), col = new Float32Array(pos.length);
      const gom = new THREE.Vector3(...P.ossa.find(b => b.nome.startsWith('lowerarm01')).testa), asse = gom.clone().sub(w).normalize();
      const cp = new THREE.Color(o.pelle || 0xd9a07c), cm = new THREE.Color(o.manica);
      for (let i = 0; i < pos.length / 3; i++) { const d = (pos[3 * i] - w.x) * asse.x + (pos[3 * i + 1] - w.y) * asse.y + (pos[3 * i + 2] - w.z) * asse.z; const c = d > o.manicaDa ? cm : cp; col.set([c.r, c.g, c.b], 3 * i); }
      g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    }
    const mat = new THREE.MeshStandardMaterial({ color: o.manica ? 0xffffff : (o.pelle || 0xd9a07c), vertexColors: !!o.manica, roughness: 0.55, side: THREE.DoubleSide });
    const mesh = new THREE.SkinnedMesh(g, mat); mesh.castShadow = mesh.receiveShadow = true; mesh.frustumCulled = false;
    const ossa = {}, riposo = {}, lista = [];
    const qDi = b => new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(new THREE.Vector3(...b.assi[0]), new THREE.Vector3(...b.assi[1]), new THREE.Vector3(...b.assi[2])));
    for (const b of P.ossa) {
      const osso = new THREE.Bone(); osso.name = b.nome; const q = qDi(b), h = new THREE.Vector3(...b.testa);
      if (b.genitore) { const pb = P.ossa.find(x => x.nome === b.genitore), qp = qDi(pb), hp = new THREE.Vector3(...pb.testa);
        osso.position.copy(h.sub(hp).applyQuaternion(qp.clone().invert())); osso.quaternion.copy(qp.clone().invert().multiply(q)); ossa[b.genitore].add(osso); }
      else { osso.position.copy(h); osso.quaternion.copy(q); mesh.add(osso); }
      ossa[b.nome] = osso; riposo[b.nome] = osso.quaternion.clone(); lista.push(osso);
      osso.userData.lunghezza = new THREE.Vector3(...b.coda).distanceTo(new THREE.Vector3(...b.testa));
    }
    mesh.updateMatrixWorld(true);
    mesh.bind(new THREE.Skeleton(lista));
    const flessione = (n, a = 0, apri = 0, torci = 0) => { const o2 = ossa[n]; if (!o2) return;
      o2.quaternion.copy(riposo[n]).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(a, torci, apri, 'XYZ'))); };
    const riposa = () => { for (const n in ossa) ossa[n].quaternion.copy(riposo[n]); };
    // punta (coda) di un osso nel mondo
    const punta = n => { const o2 = ossa[n]; o2.updateWorldMatrix(true, false); return o2.localToWorld(new THREE.Vector3(0, o2.userData.lunghezza, 0)); };
    const testa = n => { const o2 = ossa[n]; o2.updateWorldMatrix(true, false); return o2.getWorldPosition(new THREE.Vector3()); };
    // punta l'osso (il suo asse y) verso un punto del mondo, a partire dalla posa a riposo; «torci» lo gira sul suo asse
    const mira = (n, bersaglio, torci = 0) => { const o2 = ossa[n]; o2.quaternion.copy(riposo[n]); o2.updateWorldMatrix(true, false);
      const qw = o2.getWorldQuaternion(new THREE.Quaternion()), dir = bersaglio.clone().sub(o2.getWorldPosition(new THREE.Vector3())).normalize().applyQuaternion(qw.invert());
      o2.quaternion.multiply(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir)).multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), torci)); };
    // manica chiusa: un tubo blu sulla parte alta dell'avambraccio, che copre il taglio del modello
    if (o.manica) {
      const la = ossa[Object.keys(ossa).find(k => k.startsWith('lowerarm01'))];
      const tubo = new THREE.Mesh(new THREE.CapsuleGeometry(o.manicaRaggio || 0.038, 0.16, 6, 20), new THREE.MeshStandardMaterial({ color: o.manica, roughness: 0.75 }));
      tubo.position.set(0, 0.06, 0); la.add(tubo); tubo.castShadow = true;
    }
    return { mesh, ossa, flessione, riposa, punta, testa, mira, nome, lato: nome.slice(-1) };
  }
  // attacca una parte MakeHuman (mano o piede) a un gruppo del lattante: scala, asse (radice → punta) lungo «asse», palmo o
  // pianta verso «palmo», radice nell'origine del gruppo
  function attaccaMH(THREE, dati, nome, padre, o) {
    const m = creaParteMH(THREE, dati, nome, { pelle: o.pelle });
    const g = new THREE.Group(); g.add(m.mesh); g.scale.setScalar(o.scala); padre.add(g); m.mesh.updateMatrixWorld(true);
    const l = m.lato, r0 = m.testa(`${o.radice}.${l}`), r1 = m.testa(`${o.punta}.${l}`);
    const loc = q => g.worldToLocal(q.clone());
    const a0 = loc(r0), a1 = loc(r1), h = a1.clone().sub(a0).normalize();
    let p;
    if (o.piede) { p = new THREE.Vector3(0, -1, 0); }                                 // pianta del piede: in basso nel modello in piedi
    else { const t0 = loc(m.punta(`finger3-3.${l}`)); m.flessione(`finger3-1.${l}`, 0.6); g.updateMatrixWorld(true); p = loc(m.punta(`finger3-3.${l}`)).sub(t0); m.riposa(); }
    p.sub(h.clone().multiplyScalar(p.dot(h))).normalize();
    const A = new THREE.Matrix4().makeBasis(h, p, h.clone().cross(p)).transpose();
    const pm = o.palmo.clone().sub(o.asse.clone().multiplyScalar(o.palmo.dot(o.asse))).normalize();
    const Bm = new THREE.Matrix4().makeBasis(o.asse, pm, o.asse.clone().cross(pm));
    g.quaternion.setFromRotationMatrix(Bm.multiply(A)); g.updateMatrixWorld(true);
    g.position.sub(padre.worldToLocal(m.testa(`${o.radice}.${l}`)));
    return m;
  }
  // Controllo delle dita di una parte MakeHuman (21/11/2026, «il corpo umano ha 5 dita per ogni mano»): 5 dita visibili,
  // pollice con metacarpo e 2 falangi (finger1-1, 1-2, 1-3), le altre 4 dita con 3 falangi, medio il più lungo e mignolo il
  // più corto; ogni falange deve avere vertici pesati su di sé (il dito si vede davvero).
  function controlloDitaMH(parte, etichetta) {
    const nome = (etichetta || '') + ' ' + parte.nome;
    const pr = [], lato = parte.lato, O = parte.ossa, geo = parte.mesh.geometry;
    const vis = o => { for (let x = o; x; x = x.parent) if (!x.visible) return false; return true; };
    if (!vis(parte.mesh)) return pr;
    const sk = parte.mesh.skeleton, idx = geo.attributes.skinIndex, wgt = geo.attributes.skinWeight, conta = {};
    const soglia = nome.includes('piede') ? 0.12 : 0.3;
    for (let i = 0; i < idx.count; i++) for (let j = 0; j < 4; j++) if (wgt.getComponent(i, j) > soglia) { const b = sk.bones[idx.getComponent(i, j)].name; conta[b] = (conta[b] || 0) + 1; }
    const piede = nome.includes('piede'), pre = piede ? 'toe' : 'finger';
    const lung = {}; let dita = 0;
    for (let d = 1; d <= 5; d++) {
      const fal = piede && d === 1 ? [1, 2] : [1, 2, 3];
      const ok = fal.every(f => O[`${pre}${d}-${f}.${lato}`] && vis(O[`${pre}${d}-${f}.${lato}`]) && (conta[`${pre}${d}-${f}.${lato}`] || 0) >= (piede ? 1 : 4));
      if (ok) dita++; else pr.push({ tipo: 'dita', dettagli: `${nome}: il dito ${d} non ha tutte le falangi visibili` });
      lung[d] = fal.reduce((a, f) => a + (O[`${pre}${d}-${f}.${lato}`] ? O[`${pre}${d}-${f}.${lato}`].userData.lunghezza : 0), 0);
    }
    if (dita !== 5) pr.push({ tipo: 'dita', dettagli: `${nome}: ${dita} dita invece di 5` });
    if (!piede && !(lung[3] > lung[2] && lung[3] > lung[4] && lung[5] < lung[2] && lung[5] < lung[4])) pr.push({ tipo: 'dita', dettagli: `${nome}: lunghezze delle dita non anatomiche` });
    return pr;
  }

  /* ============================================================ pose delle mani MakeHuman sul lattante ===================== */
  // Funzioni dei provini approvati (provino-mani.src.html), condivise con la pagina del video. Valgono con il lattante
  // supino e orizzontale (testa verso -z, pancia in su); «pavimento» è l'altezza sotto cui le dita non vanno (piano, cosce).
  function creaPoseMani(THREE, lat, o = {}) {
    const v = (x, y, z) => new THREE.Vector3(x, y, z), DITA4 = [2, 3, 4, 5];
    let PAV = o.pavimento == null ? 0.009 : o.pavimento;
  // vettori della mano nel sistema della mesh a riposo: asse (polso → nocca del medio) e normale del palmo
  function vettoriMano(b, l) {
    b.riposa(); b.mesh.updateMatrixWorld(true);
    const w = b.testa(`wrist.${l}`), m = b.testa(`finger3-1.${l}`), h = m.clone().sub(w).normalize();
    const t0 = b.punta(`finger3-3.${l}`); b.flessione(`finger3-1.${l}`, 0.6); b.mesh.updateMatrixWorld(true);
    const p = b.punta(`finger3-3.${l}`).sub(t0); p.sub(h.clone().multiplyScalar(p.dot(h))).normalize(); b.riposa();
    return { h, p };
  }
  function orientaParte(b, l, hMondo, pMondo) {    // ruota il gruppo della parte: asse della mano lungo hMondo, palmo verso pMondo
    const g = b.mesh.parent; g.quaternion.identity(); g.position.set(0, 0, 0); g.updateMatrixWorld(true);
    const { h, p } = vettoriMano(b, l);
    hMondo = hMondo.clone().normalize(); pMondo = pMondo.clone().sub(hMondo.clone().multiplyScalar(pMondo.dot(hMondo))).normalize();
    const A = new THREE.Matrix4().makeBasis(h, p, h.clone().cross(p)), Bm = new THREE.Matrix4().makeBasis(hMondo, pMondo, hMondo.clone().cross(pMondo));
    g.quaternion.setFromRotationMatrix(Bm.multiply(A.transpose())); g.updateMatrixWorld(true);
  }
  // centro del palmo nel mondo (polso e nocche di indice, medio e mignolo)
  const centroPalmo = (b, l) => ['wrist', 'finger2-1', 'finger3-1', 'finger5-1'].map(n => b.testa(`${n}.${l}`)).reduce((a, q) => a.add(q), v(0, 0, 0)).multiplyScalar(0.25);
  function posaPollici(b, s, st) {
    // Posa a due pollici (IRC 2025 cap. 9 fig. 11, foto di riferimento).
    // 1) La base del pollice (articolazione trapezio-metacarpale) si mette sul davanti del fianco, a un angolo TH dalla
    //    linea mediana e a 1,2 cm dalla pelle (lo spessore dell'eminenza tenar), alla distanza giusta dalla punta.
    // 2) Il pollice arriva alla sua punta sulla metà inferiore dello sterno con una cinematica inversa a due segmenti
    //    (metacarpo, falangi), inarcato verso l'alto: le falangi corrono quasi parallele allo sterno verso la testa.
    // 3) La mano ruota intorno a quella base: si sceglie la rotazione con il palmo vicino al fianco senza entrarci e il
    //    polso dalla sua parte; poi le dita avvolgono il fianco verso il dorso senza entrare nel torace.
    const X = (typeof window !== "undefined" && window.__PP) || {}, l = b.lato, g = b.mesh.parent;
    const sc = g.scale.x, L1 = b.ossa[`finger1-1.${l}`].userData.lunghezza * sc;
    const L2 = (b.ossa[`finger1-2.${l}`].userData.lunghezza + b.ossa[`finger1-3.${l}`].userData.lunghezza) * sc * 0.98;
    const T = (l === "L" && X.tL) || X.t || [0.0042, 0.011, -0.004], punta = st.clone().add(v(s * T[0], T[1], T[2]));   // X.tL: solo per le prove del controllo
    // sezione del torace all'altezza della base: centro e semiassi dal modello del lattante
    const bac = lat.G.bacino, stL = bac.worldToLocal(st.clone()), sez = lat.sezione(stL.y);
    const TH = (X.th !== undefined ? X.th : 60) * Math.PI / 180, M = X.marg !== undefined ? X.marg : 0.012;
    const cmcLoc = (yl) => { const q = lat.sezione(yl); const px = Math.sin(TH) * q.rx, pz = q.z + Math.cos(TH) * q.rz;
      const nn = new THREE.Vector2(Math.sin(TH) / q.rx, Math.cos(TH) / q.rz).normalize();
      return v(s * (px + nn.x * M), yl, pz + nn.y * M); };
    // la base scende verso i piedi finché la distanza dalla punta è il 92% della lunghezza del pollice
    let yl = stL.y, cmc;
    for (let k = 0; k < 60; k++) { cmc = bac.localToWorld(cmcLoc(yl)); if (cmc.distanceTo(punta) >= (L1 + L2) * (X.re || 0.92)) break; yl -= 0.002; }
    const metti = (a, c, bb) => {
      const f = v(s * a, -1, -c).normalize(), n = v(-s, -bb, 0); n.sub(f.clone().multiplyScalar(n.dot(f))).normalize();
      orientaParte(b, l, f, n);
      g.updateMatrixWorld(true); g.position.add(cmc.clone().sub(b.testa(`finger1-1.${l}`))); g.updateMatrixWorld(true);
      const dv = punta.clone().sub(cmc), d = dv.length(), u = dv.clone().normalize();
      const aa = (L1 * L1 - L2 * L2 + d * d) / (2 * d), hh = Math.sqrt(Math.max(0, L1 * L1 - aa * aa));
      const w = v(0, 1, 0); w.sub(u.clone().multiplyScalar(w.dot(u))).normalize();
      const mcp = cmc.clone().add(u.clone().multiplyScalar(aa)).add(w.multiplyScalar(hh));
      b.mira(`finger1-1.${l}`, mcp); g.updateMatrixWorld(true); b.mira(`finger1-2.${l}`, punta); g.updateMatrixWorld(true); b.flessione(`finger1-3.${l}`, 0.06);
      g.updateMatrixWorld(true);
    };
    const PALMO = X.palmo || 1.2;
    const rapido = () => {
      const cp = centroPalmo(b, l), dp = lat.dentroTronco(cp);
      const nocche = ['wrist', 'finger2-1', 'finger3-1', 'finger4-1', 'finger5-1', 'metacarpal1', 'metacarpal2', 'metacarpal3', 'metacarpal4'].filter(k => b.ossa[`${k}.${l}`]).map(k => b.testa(`${k}.${l}`));
      const dentro = nocche.reduce((x, q) => x + Math.max(0, 1.1 - lat.dentroTronco(q)), 0);
      const lato = Math.max(0, 0.045 - s * (cp.x - st.x)) + Math.max(0, 0.05 - s * (b.testa(`wrist.${l}`).x - st.x));
      return Math.abs(dp - PALMO) * 10 + dentro * 30 + lato * 400;
    };
    const A = X.a || [-0.4, 0, 0.4, 0.8, 1.2], C = X.c || [-0.3, 0, 0.3, 0.6, 0.9], Bb = X.b || [-0.6, -0.3, 0, 0.3, 0.6];
    const cand = [];
    for (const a of A) for (const c of C) for (const bb of Bb) { metti(a, c, bb); cand.push([rapido(), a, c, bb]); }
    cand.sort((p, q) => p[0] - q[0]);
    let best = null, sc0 = 1e9;
    for (const [, a, c, bb] of cand.slice(0, X.top || 6)) {
      metti(a, c, bb); ditaIntorno(b, s); g.updateMatrixWorld(true);
      const pen = compenetrazione(b).reduce((x, p) => x + (+(p.dettagli.match(/: (\d+) punti/) || [0, 1])[1]), 0);
      const avv = DITA4.reduce((x, d) => x + Math.max(0, lat.dentroTronco(b.punta(`finger${d}-3.${l}`)) - 1.1), 0);
      const tot = pen * 10 + avv * 20 + rapido();
      if (tot < sc0) { sc0 = tot; best = [a, c, bb]; }
    }
    metti(...best); ditaIntorno(b, s); g.updateMatrixWorld(true);
    // se palmo o dita toccano ancora dentro il fianco, la mano ruota intorno a un asse che passa per la punta del pollice
    // (la punta resta ferma sul giallo): prima intorno all'asse della mano (il lato del pollice si solleva), poi intorno
    // all'asse del corpo; si tiene la rotazione più piccola senza compenetrazioni
    if (compenetrazione(b, 0.98).length) {   // margine di 3 punti percentuali, perché la mano si muove nelle compressioni
      const p0 = g.position.clone(), q0 = g.quaternion.clone(), o0 = Object.fromEntries(Object.entries(b.ossa).map(([k, o]) => [k, o.quaternion.clone()]));
      const torna = () => { g.position.copy(p0); g.quaternion.copy(q0); for (const k in o0) b.ossa[k].quaternion.copy(o0[k]); g.updateMatrixWorld(true); };
      const asseMano = b.testa(`finger3-1.${l}`).sub(b.testa(`wrist.${l}`)).normalize();
      const assi = X.assi || [asseMano, v(0, 0, 1)], qz = new THREE.Quaternion();
      let trovato = null;
      for (let k = 1; k <= 25 && !trovato; k++) for (const ax of assi) for (const sg of [1, -1]) {
        if (trovato) break;
        torna(); qz.setFromAxisAngle(ax, sg * 0.026 * k);
        g.position.sub(punta).applyQuaternion(qz).add(punta); g.quaternion.premultiply(qz); g.updateMatrixWorld(true);
        ditaIntorno(b, s); g.updateMatrixWorld(true);
        if (!compenetrazione(b, 0.98).length && s * (centroPalmo(b, l).x - st.x) > 0.04) trovato = [ax, sg * 0.026 * k];
      }
      if (!trovato) torna();
    }
    if (typeof window !== 'undefined') (window.__sceltePollici = window.__sceltePollici || {})[l] = { scelta: best, punteggio: +sc0.toFixed(2), palmo: +lat.dentroTronco(centroPalmo(b, l)).toFixed(2), yBase: +yl.toFixed(3) };
  }
  // il pollice si ripunta sulla stessa punta senza muovere la mano: metacarpo verso la punta (un po' sollevato), falangi sulla punta
  function ripuntaPollice(b, punta) {
    const l = b.lato, g = b.mesh.parent;
    b.ossa[`finger1-1.${l}`].quaternion.copy(b.ossa[`finger1-1.${l}`].userData.q0 || b.ossa[`finger1-1.${l}`].quaternion);
    g.updateMatrixWorld(true);
    const base = b.testa(`finger1-1.${l}`), L1 = base.distanceTo(b.testa(`finger1-2.${l}`));
    const mcp = base.clone().add(punta.clone().sub(base).normalize().multiplyScalar(L1)).add(v(0, (window.__PP && window.__PP.alza) || 0.008, 0));
    b.mira(`finger1-1.${l}`, mcp); g.updateMatrixWorld(true); b.mira(`finger1-2.${l}`, punta); g.updateMatrixWorld(true);
  }
  function posaPollici1(b, s, st, rx, lat0, soloMano) {
    const l = b.lato, g = b.mesh.parent;
    // palmo sul fianco, dita verso il basso intorno al torace, avambraccio che arriva dall'alto e di lato (foto di riferimento)
    const X = (typeof window !== 'undefined' && window.__PP) || {};             // solo per le prove di posa
    if (X.rx !== undefined) rx = X.rx; if (X.lat0 !== undefined) lat0 = X.lat0;
    const H = X.h || [0.3, -1, -0.5], Pp = X.p || [-1, -0.6, 0];   // avambraccio che arriva dai piedi e dall'alto (IRC 2025 cap. 9 fig. 11)
    const hM = v(s * H[0], H[1], H[2]).normalize(), pM = v(s * Pp[0], Pp[1], Pp[2]); pM.sub(hM.clone().multiplyScalar(pM.dot(hM))).normalize();
    orientaParte(b, l, hM, pM);
    const bacino = lat.G.bacino, fianco = bacino.localToWorld(v(s * 0.0, 0.118, 0.0));     // centro del torace a quella altezza
    const O = X.o || [0.016, 0.006, 0.06], voluto = fianco.clone().add(v(s * (rx + O[0]), O[1], O[2]));
    g.updateMatrixWorld(true); g.position.add(voluto.sub(centroPalmo(b, l))); g.updateMatrixWorld(true);
    if (soloMano) return;
    // pollici affiancati sulla metà inferiore dello sterno, rivolti verso la testa
    const T = X.t || [0.004, 0.011, -0.004], punta = st.clone().add(v(s * T[0], T[1], T[2]));
    // il metacarpo del pollice va dalla base verso il davanti del torace, le due falangi corrono lungo lo sterno verso la testa
    const L2 = b.ossa[`finger1-2.${l}`].userData.lunghezza + b.ossa[`finger1-3.${l}`].userData.lunghezza;
    const M = X.m || [0.02, 0.85], mcp = punta.clone().add(v(s * lat0, M[0], L2 * M[1]));
    // la mano si sposta finché il metacarpo del pollice, lungo com'è, arriva alla nocca: così la punta tocca lo sterno
    const L1 = b.ossa[`finger1-1.${l}`].userData.lunghezza;
    for (let k = 0; k < 6; k++) { const base = b.testa(`finger1-1.${l}`), dv = mcp.clone().sub(base), dd = dv.length() - L1; g.position.add(dv.normalize().multiplyScalar(dd)); g.updateMatrixWorld(true); }
    b.mira(`finger1-1.${l}`, mcp); g.updateMatrixWorld(true); b.mira(`finger1-2.${l}`, punta); g.updateMatrixWorld(true); b.flessione(`finger1-3.${l}`, 0.08);
    // le altre quattro dita avvolgono il fianco e passano sotto la schiena, senza entrare nel torace né nel piano
    ditaIntorno(b, s);
    g.updateMatrixWorld(true);
  }
  function ditaIntorno(b, s) {
    const l = b.lato, g = b.mesh.parent;
    for (const d of DITA4) {
      // ricerca su due angoli (nocca, falangi): la piega più avvolgente senza compenetrazioni nel torace e nel piano
      const metti = (a1, a2) => { b.flessione(`finger${d}-1.${l}`, a1, (d - 3.5) * 0.08); b.flessione(`finger${d}-2.${l}`, a2); b.flessione(`finger${d}-3.${l}`, a2 * 0.75); g.updateMatrixWorld(true); };
      let best = [0, 0], pen0 = 1e9, avv0 = -1;
      for (let a1 = -0.7; a1 <= 1.2; a1 += 0.1) for (let a2 = 0; a2 <= 1.6; a2 += 0.1) {
        metti(a1, a2);
        const pts = [1, 2, 3].map(f => b.punta(`finger${d}-${f}.${l}`)).concat([2, 3].map(f => b.testa(`finger${d}-${f}.${l}`)));
        const MARG = (window.__PP && window.__PP.marg) || 1.2; const pen = pts.reduce((x, q) => x + Math.max(0, MARG - lat.dentroTronco(q)) + 40 * Math.max(0, PAV - q.y), 0);
        const avv = a1 + a2;                                         // quanto avvolge
        if (pen < pen0 - 1e-4 || (Math.abs(pen - pen0) <= 1e-4 && avv > avv0)) { pen0 = pen; avv0 = avv; best = [a1, a2]; }
      }
      metti(best[0], best[1]);
    }
  }
  function compenetrazione(b, soglia) {          // punte e articolazioni delle dita dentro il torace del lattante (soglia della pelle: 0,95; in posa 0,98)
    const out = [], l = b.lato;
    for (let d = 1; d <= 5; d++) for (let f = 1; f <= 3; f++) { const q = b.punta(`finger${d}-${f}.${l}`), x = lat.dentroTronco(q); if (x < 0.95) out.push({ tipo: 'compenetrazione', dettagli: `${b.mesh.name || 'mano'} ${l}: dito ${d} falange ${f} dentro il torace (${x.toFixed(2)})` }); }
    // anche la pelle della mano e dell'avambraccio (un vertice su tre, con le ossa in posa): il palmo non entra nel torace
    const m = b.mesh, pos = m.geometry.attributes.position, q = new THREE.Vector3(); let n = 0, peggio = 9, ossoP = '';
    m.updateMatrixWorld(true);
    for (let i = 0; i < pos.count; i += ((typeof window !== "undefined" && window.__PP && window.__PP.passoV) || 1)) { m.getVertexPosition(i, q); m.localToWorld(q); const x = lat.dentroTronco(q); if (x < (soglia || (typeof window !== "undefined" && window.__PP && window.__PP.soglia) || 0.95)) { n++; if (x < peggio) { peggio = x; ossoP = m.skeleton.bones[m.geometry.attributes.skinIndex.getX(i)].name; } } }
    if (n > 0) out.push({ tipo: 'compenetrazione', dettagli: `${b.mesh.name || 'mano'} ${l}: ${n} punti della pelle dentro il torace (${peggio.toFixed(2)}, ${ossoP})` });
    return out;
  }
    return { orientaParte, vettoriMano, centroPalmo, posaPollici, ditaIntorno, compenetrazione, pavimento: y => { PAV = y; } };
  }

  // orienta un oggetto (mano) perché le dita vadano lungo «dita» e il palmo guardi verso «palmo» (vettori del mondo)
  function orienta(THREE, obj, dita, palmo) {
    const z = dita.clone().normalize().negate();
    let y = palmo.clone().normalize().negate(); y.sub(z.clone().multiplyScalar(y.dot(z))).normalize();
    const x = new THREE.Vector3().crossVectors(y, z).normalize();
    obj.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, y, z));
  }

  window.Lattante3D = { creaLattante, creaMano, creaParteMH, controlloDitaMH, creaPoseMani, orienta, tubo, arto, ellissoide };
})();
