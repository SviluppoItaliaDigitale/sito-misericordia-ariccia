/* Firma «Misericordia di Ariccia» e cornice di microtesto per le grafiche della Misericordia di Ariccia.

   Nasce il 21/10/2026 dalla richiesta di Alessandro: «metti in ogni slide, documento grafico eccetera sempre
   Misericordia di Ariccia! Altrimenti ci rubano la grafica!! e se riesci anche un microtesto come filigrana ai
   bordi a mo' di cornice». Riprende l'idea della cornice di microtesto del sito della Protezione Civile di
   Genzano (scripts/microtesto_cornice.py, 01/10/2026), qui nel browser, così usa i caratteri delle grafiche.

   - firmaECornice(sorgente, opzioni), per le immagini: disegna l'immagine, se richiesto scrive la firma
     «Misericordia di Ariccia» (posizione, carattere e colore nelle opzioni; colore automatico chiaro o scuro
     secondo il fondo), poi incide lungo i quattro bordi, in caratteri di pochi pixel, la provenienza della
     grafica. Il tono si adatta al fondo pixel per pixel: schiarisce dove è scuro, scurisce dove è chiaro, con
     opacità bassa. Da lontano non si nota, ingrandendo si legge; chi ritaglia i bordi lascia una grafica
     evidentemente rifilata. Il JPEG o il PNG che esce porta anche un commento (MARCATORE) che i controlli del
     sito cercano (scripts/controlli/controlla_sito.py).
   - corniceVettoriale(opzioni), per i modelli da stampa (biglietto da visita, carta intestata): la stessa
     cornice come testo vettoriale, dentro il margine di stampa, parola per parola chiara sul blu e scura sul
     bianco, con colori pieni (niente trasparenze in tipografia). Dal 21/10/2026 la usa anche rendi.py --cornice
     per i PDF già fatti, con i tratti liberi misurati sulla pagina.
   Le usano .claude/skills/grafiche-modelli-nazionali/rendi.py e scripts/parola-domenica/rendi.js, attraverso
   la pagina firma-e-cornice.html (che carica i caratteri). Nessuna libreria esterna. */
(() => {
  const MARCATORE = 'Misericordia di Ariccia - firma e cornice di microtesto - www.misericordia-ariccia.it';
  const FIRMA = 'Misericordia di Ariccia';
  const CARATTERE = 'Montserrat';
  const testoBase = (anno) => `MISERICORDIA DI ARICCIA · www.misericordia-ariccia.it · grafica della Confraternita di Misericordia di Ariccia ODV · © ${anno} · `;
  const luminanza = (r, g, b) => 0.299 * r + 0.587 * g + 0.114 * b;
  // Toni verso cui si sposta la cornice: bianco sul fondo scuro, blu scuro del marchio sul fondo chiaro.
  const CHIARO = [255, 255, 255], SCURO = [11, 37, 80];
  const tono = (r, g, b) => (luminanza(r, g, b) < 140 ? CHIARO : SCURO);

  // Testo di una striscia lunga `lunghezza` px: i pezzi del testo (separati da «·») interi, ripetuti finché
  // entrano; se in fondo resta posto, il nome o l'indirizzo del sito. Mai una frase tagliata a metà: solo su
  // una striscia più corta del primo pezzo restano le sue parole intere, senza «di» in fondo.
  const riga = (misura, testo, lunghezza) => {
    const pezzi = testo.split('·').map((p) => p.trim()).filter(Boolean), sep = ' · ';
    let r = '', ultimo = null;
    for (let i = 0; i < 1000; i++) {
      const p = pezzi[i % pezzi.length], prova = r ? r + sep + p : p;
      if (misura(prova) > lunghezza) break;
      r = prova; ultimo = p;
    }
    for (const p of pezzi.slice(0, 2)) {
      const prova = r ? r + sep + p : p;
      if (p !== ultimo && misura(prova) <= lunghezza) { r = prova; ultimo = p; }
    }
    if (!r) {
      const parole = pezzi[0].split(' ');
      while (parole.length && (misura(parole.join(' ')) > lunghezza || /^(?:di|DI|della|DELLA)$/.test(parole[parole.length - 1]))) parole.pop();
      r = parole.join(' ');
    }
    return r;
  };

  // Maschera del testo sui quattro bordi (angoli liberi): canale alfa del testo, corpo e spessore della striscia.
  const mascheraCornice = (W, H, o) => {
    const corpo = o.corpo || Math.max(7, Math.round(W * 9 / 1080));
    const s = corpo + 4;                      // spessore della striscia: i primi corpo+4 pixel di ogni bordo
    const testo = o.testo || testoBase(o.anno || new Date().getFullYear());
    const m = document.createElement('canvas'); m.width = W; m.height = H;
    const c = m.getContext('2d');
    c.fillStyle = '#FFFFFF'; c.font = `600 ${corpo}px ${CARATTERE}`; c.textBaseline = 'middle';
    const misura = (t) => c.measureText(t).width;
    const angoli = Math.max(s, o.angoli || 0);  // angoli liberi: almeno lo spessore della striscia, di più se ci sono ornamenti
    const lungO = W - 2 * angoli, lungV = H - 2 * angoli;
    const orizzontale = riga(misura, testo, lungO), verticale = riga(misura, testo, lungV);
    const dO = (lungO - misura(orizzontale)) / 2, dV = (lungV - misura(verticale)) / 2;   // righe centrate
    c.fillText(orizzontale, angoli + dO, s / 2);                                         // alto
    c.fillText(orizzontale, angoli + dO, H - s / 2);                                     // basso
    c.save(); c.translate(s / 2, H - angoli - dV); c.rotate(-Math.PI / 2); c.fillText(verticale, 0, 0); c.restore();  // sinistra, dal basso
    c.save(); c.translate(W - s / 2, angoli + dV); c.rotate(Math.PI / 2); c.fillText(verticale, 0, 0); c.restore();   // destra, dall'alto
    return { maschera: c.getImageData(0, 0, W, H).data, corpo, striscia: s, testo: orizzontale.slice(0, 60) };
  };

  // Cornice raster: maschera del testo, poi tono adattato al fondo pixel per pixel.
  const incidiCornice = (ctx, W, H, o) => {
    const intensita = o.intensita ?? 0.32;
    const { maschera, corpo, striscia, testo } = mascheraCornice(W, H, o);
    const immagine = ctx.getImageData(0, 0, W, H), d = immagine.data;
    for (let i = 0; i < d.length; i += 4) {
      const a = maschera[i + 3];
      if (!a) continue;
      const t = tono(d[i], d[i + 1], d[i + 2]), k = (a / 255) * intensita;
      d[i] += (t[0] - d[i]) * k; d[i + 1] += (t[1] - d[i + 1]) * k; d[i + 2] += (t[2] - d[i + 2]) * k;
    }
    ctx.putImageData(immagine, 0, 0);
    return { corpo, striscia, testo };
  };

  // Firma su un'immagine già fatta (per esempio la copertina tratta da un video). Rifiuta di scrivere sopra
  // disegni o testi: la zona sotto la firma deve essere un fondo uniforme.
  const scriviFirma = async (ctx, W, H, f) => {
    const corpo = f.corpo || Math.round(W * 0.03), peso = f.peso || 600, famiglia = f.carattere || CARATTERE;
    const font = `${peso} ${corpo}px ${famiglia}`;
    await document.fonts.load(font, FIRMA);
    ctx.save();
    ctx.font = font; ctx.textBaseline = 'alphabetic';
    const testo = f.testo || FIRMA, larghezza = ctx.measureText(testo).width;
    const margine = f.margine ?? Math.round(W * 0.06), basso = f.basso ?? Math.round(H * 0.05);
    const x = f.posizione === 'basso-destra' ? W - margine - larghezza
      : f.posizione === 'basso-centro' ? (W - larghezza) / 2 : margine;
    const y = H - basso;                                                                  // linea di base
    const zona = { x: Math.max(0, Math.floor(x - 12)), y: Math.max(0, Math.floor(y - corpo * 1.05 - 10)) };
    zona.w = Math.min(W - zona.x, Math.ceil(larghezza + 24)); zona.h = Math.min(H - zona.y, Math.ceil(corpo * 1.4 + 20));
    const px = ctx.getImageData(zona.x, zona.y, zona.w, zona.h).data;
    let somma = 0, quadrati = 0;
    for (let i = 0; i < px.length; i += 4) { const l = luminanza(px[i], px[i + 1], px[i + 2]); somma += l; quadrati += l * l; }
    const n = px.length / 4, media = somma / n, scarto = Math.sqrt(Math.max(0, quadrati / n - media * media));
    const colore = f.colore && f.colore !== 'auto' ? f.colore : (media < 140 ? '#FFFFFF' : '#0B2550');
    ctx.fillStyle = colore;
    if (f.ombra) { ctx.shadowColor = media < 140 ? 'rgba(0, 0, 0, 0.55)' : 'rgba(255, 255, 255, 0.9)'; ctx.shadowBlur = Math.round(corpo / 4); }
    ctx.fillText(testo, x, y);
    ctx.restore();
    return { testo, x: Math.round(x), y, larghezza: Math.round(larghezza), corpo, colore, fondo: Math.round(media), scarto: Math.round(scarto * 10) / 10 };
  };

  // Commento con MARCATORE: COM dopo l'intestazione JFIF nei JPEG, blocco tEXt «Comment» dopo IHDR nei PNG.
  const crcTabella = (() => { const t = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
  const crc32 = (b) => { let c = 0xFFFFFFFF; for (const x of b) c = crcTabella[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };
  const conMarcatore = (datiURL) => {
    const [testa, b64] = datiURL.split(','), bin = atob(b64), b = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) b[i] = bin.charCodeAt(i);
    const testo = new TextEncoder().encode(MARCATORE);
    let pos, seg;
    if (b[0] === 0xFF && b[1] === 0xD8) {
      pos = (b[2] === 0xFF && b[3] === 0xE0) ? 4 + ((b[4] << 8) | b[5]) : 2;
      seg = new Uint8Array(4 + testo.length);
      seg.set([0xFF, 0xFE, (testo.length + 2) >> 8, (testo.length + 2) & 255]); seg.set(testo, 4);
    } else {
      pos = 8 + 25;                                                  // firma PNG (8) + blocco IHDR (25)
      const corpo = new Uint8Array(8 + testo.length);
      corpo.set(new TextEncoder().encode('Comment\0')); corpo.set(testo, 8);
      const tipo = new TextEncoder().encode('tEXt'), crc = crc32([...tipo, ...corpo]);
      seg = new Uint8Array(12 + corpo.length);
      seg.set([corpo.length >>> 24, (corpo.length >> 16) & 255, (corpo.length >> 8) & 255, corpo.length & 255]);
      seg.set(tipo, 4); seg.set(corpo, 8); seg.set([crc >>> 24, (crc >> 16) & 255, (crc >> 8) & 255, crc & 255], 8 + corpo.length);
    }
    const out = new Uint8Array(b.length + seg.length);
    out.set(b.subarray(0, pos)); out.set(seg, pos); out.set(b.subarray(pos), pos + seg.length);
    let s = '';
    for (let i = 0; i < out.length; i += 0x8000) s += String.fromCharCode.apply(null, out.subarray(i, i + 0x8000));
    return `${testa},${btoa(s)}`;
  };

  window.MARCATORE_FIRMA_CORNICE = MARCATORE;

  // Solo il segno, senza toccare i pixel (il file non si ricomprime): per le grafiche che hanno già firma e cornice
  // disegnate da chi le ha fatte, come le copertine tratte dai video della rubrica. Prima si controlla con
  // verificaCornice che la cornice ci sia davvero (lo fa rendi.py --segno).
  window.aggiungiSegno = (datiURL) => conMarcatore(datiURL);

  // C'è la cornice di microtesto del motore? Si rifà la maschera con le stesse misure e, lato per lato, si misura
  // quanto i punti del testo si staccano dal fondo vicino, con la maschera al suo posto e spostata di 3 px lungo il
  // bordo. Con la cornice il testo al suo posto si stacca molto di più; senza cornice i due valori sono simili.
  // Restituisce per ogni lato i due valori e il loro rapporto. opzioni: quelle della cornice (anno, corpo, testo).
  window.verificaCornice = async (sorgente, o = {}) => {
    await document.fonts.ready;
    await document.fonts.load(`600 9px ${CARATTERE}`, testoBase(2026));
    const im = new Image(); im.src = sorgente; await im.decode();
    const W = im.naturalWidth, H = im.naturalHeight;
    const tela = document.createElement('canvas'); tela.width = W; tela.height = H;
    const c = tela.getContext('2d'); c.drawImage(im, 0, 0);
    const px = c.getImageData(0, 0, W, H).data, { maschera, striscia: s } = mascheraCornice(W, H, o);
    const L = (x, y) => { const i = (y * W + x) * 4; return luminanza(px[i], px[i + 1], px[i + 2]); };
    const A = (x, y) => (x < 0 || y < 0 || x >= W || y >= H ? 0 : maschera[(y * W + x) * 4 + 3]);
    // un lato: punti (u lungo il bordo, v di traverso) → coordinate; finestre di 24 px lungo il bordo
    const lato = (xy, lunghezza, d) => {
      let somma = 0, n = 0;
      for (let u0 = s; u0 < lunghezza - s; u0 += 24) {
        let fondo = 0, nf = 0;
        const testo = [];
        for (let u = u0; u < Math.min(u0 + 24, lunghezza - s); u++) for (let v = 0; v < s; v++) {
          const [x, y] = xy(u, v), [xm, ym] = xy(u - d, v), a = A(xm, ym);
          if (a >= 128) testo.push(L(x, y)); else if (!a) { fondo += L(x, y); nf++; }
        }
        if (!nf) continue;
        fondo /= nf;
        for (const l of testo) { somma += Math.abs(l - fondo); n++; }
      }
      return n ? somma / n : 0;
    };
    const lati = {
      alto: (u, v) => [u, v], basso: (u, v) => [u, H - 1 - v],
      sinistra: (u, v) => [v, u], destra: (u, v) => [W - 1 - v, u],
    };
    const esito = {};
    for (const [nome, xy] of Object.entries(lati)) {
      const lunghezza = nome === 'alto' || nome === 'basso' ? W : H;
      const giusto = lato(xy, lunghezza, 0), spostato = lato(xy, lunghezza, 3);
      esito[nome] = { giusto: Math.round(giusto * 10) / 10, spostato: Math.round(spostato * 10) / 10,
        rapporto: Math.round((giusto / Math.max(spostato, 0.5)) * 100) / 100 };
    }
    return { larghezza: W, altezza: H, lati: esito };
  };

  // Cornice come strato a sé, per le pagine che si muovono (i video della rubrica, scripts/video-rubrica/appro.src.html):
  // sulla tela trasparente `tela` ogni punto del testo prende il tono che la cornice incisa avrebbe sulla tela fissa
  // `fondo`, con la stessa opacità. Messa sopra tutto, sul fondo dà esattamente la cornice incisa e resta visibile
  // anche dove un disegno arriva al bordo: così è in ogni fotogramma e nella copertina tratta dal video.
  window.corniceSovrapposta = (tela, fondo, o = {}) => {
    const W = tela.width, H = tela.height, intensita = o.intensita ?? 0.32;
    const { maschera, corpo, striscia, testo } = mascheraCornice(W, H, o);
    const f = fondo.getContext('2d').getImageData(0, 0, W, H).data;
    const ctx = tela.getContext('2d'), strato = ctx.createImageData(W, H), d = strato.data;
    for (let i = 0; i < d.length; i += 4) {
      const a = maschera[i + 3];
      if (!a) continue;
      const t = tono(f[i], f[i + 1], f[i + 2]);
      d[i] = t[0]; d[i + 1] = t[1]; d[i + 2] = t[2]; d[i + 3] = Math.round(a * intensita);
    }
    ctx.putImageData(strato, 0, 0);
    return { corpo, striscia, testo };
  };

  // opzioni: formato 'jpeg' | 'png', qualita (0.88), firma {posizione, margine, basso, corpo, peso, carattere,
  // colore, ombra}, cornice (false per non inciderla: i modelli da stampa hanno quella vettoriale), marcatore
  // (false per non scrivere il commento: solo nelle prove), corpo e intensita della cornice, angoli (px liberi a
  // ogni capo delle strisce, per non passare sopra ornamenti d'angolo), anno, testo.
  window.firmaECornice = async (sorgente, o = {}) => {
    await document.fonts.ready;
    await document.fonts.load(`600 9px ${CARATTERE}`, testoBase(2026));
    const im = new Image(); im.src = sorgente; await im.decode();
    const W = im.naturalWidth, H = im.naturalHeight;
    const tela = document.createElement('canvas'); tela.width = W; tela.height = H;
    const ctx = tela.getContext('2d'); ctx.drawImage(im, 0, 0);
    const esito = { larghezza: W, altezza: H };
    if (o.firma) esito.firma = await scriviFirma(ctx, W, H, o.firma);
    if (o.cornice !== false) esito.cornice = incidiCornice(ctx, W, H, o);
    const dati = tela.toDataURL(o.formato === 'png' ? 'image/png' : 'image/jpeg', o.qualita ?? 0.88);
    esito.dati = o.marcatore === false ? dati : conMarcatore(dati);
    return esito;
  };

  // Cornice vettoriale nei modelli da stampa. opzioni: margine e corpo in px, lati ('alto', 'basso', 'sinistra',
  // 'destra'; di solito tutti e quattro), intensita, anno, testo. Ogni striscia corre solo sul suo fondo
  // prevalente: dove la attraversa un fondo diverso (per esempio la fascia blu in fondo alla carta intestata) si
  // ferma prima, con un piccolo stacco, e il testo sta intero e centrato nel tratto che resta. Colori pieni, il
  // tono della cornice raster calcolato su quel fondo. Restituisce le parole scritte, le strisce e le scritte o i
  // loghi che la cornice toccherebbe (devono essere zero: lo controlla rendi.py).
  // Per i PDF già fatti (rendi.py --cornice FILE.pdf) la pagina non è nel browser: rendi.py misura i tratti liberi
  // sulla pagina disegnata e li passa in o.strisce ([{lato, inizio, fine, fondo: [R, G, B]}]), con le misure
  // della tavola in o.larghezza e o.altezza; testo, carattere, tono e posto delle righe restano quelli di qui.
  window.corniceVettoriale = (o) => {
    const tavola = document.querySelector('.tavola'), T = tavola.getBoundingClientRect();
    const W = o.larghezza || tavola.clientWidth, H = o.altezza || tavola.clientHeight, corpo = o.corpo, margine = o.margine;
    const lati = o.lati || ['alto', 'basso', 'sinistra', 'destra'];
    const intensita = o.intensita ?? 0.3, s = Math.round(corpo + 4);
    const testo = o.testo || testoBase(o.anno || new Date().getFullYear());
    const misura = (() => { const c = document.createElement('canvas').getContext('2d'); c.font = `600 ${corpo}px ${CARATTERE}`; return (t) => c.measureText(t).width; })();
    // colore del fondo nel punto (x, y) della tavola: il primo elemento con uno sfondo pieno
    const fondo = (x, y) => {
      for (const el of document.elementsFromPoint(T.left + x, T.top + y)) {
        const c = getComputedStyle(el).backgroundColor.match(/[\d.]+/g);
        if (c && (c.length < 4 || +c[3] > 0.5)) return c.slice(0, 3).map(Number);
      }
      return [255, 255, 255];
    };
    // ogni lato: inizio, direzione, lunghezza e linea di mezzo della striscia
    const lungO = W - 2 * (margine + s), lungV = H - 2 * (margine + s);
    const geometria = {
      alto: { x0: margine + s, y0: margine + s / 2, dx: 1, dy: 0, n: lungO },
      basso: { x0: margine + s, y0: H - margine - s / 2, dx: 1, dy: 0, n: lungO },
      sinistra: { x0: margine + s / 2, y0: margine + s, dx: 0, dy: 1, n: lungV },
      destra: { x0: W - margine - s / 2, y0: margine + s, dx: 0, dy: 1, n: lungV },
    };
    const passo = 2, mezzo = s / 2 - 1;
    // colore pieno della riga su un fondo [R, G, B] (il tono della cornice raster) e posto della striscia. Nelle
    // strisce verticali tutto il testo è girato (text-orientation:sideways): con l'impostazione predefinita «©» resta
    // dritto, occupa quasi mezzo corpo in più della misura orizzontale e l'ultima parola usciva dalla striscia.
    const coloreSu = ([R, G, B]) => {
      const t = tono(R, G, B);
      return `rgb(${Math.round(R + (t[0] - R) * intensita)}, ${Math.round(G + (t[1] - G) * intensita)}, ${Math.round(B + (t[2] - B) * intensita)})`;
    };
    const postoDi = (lato, g, inizio, lunghezza) => (g.dx
      ? `left:${g.x0 + inizio}px;top:${g.y0 - s / 2}px;width:${lunghezza}px;height:${s}px`
      : `left:${g.x0 - s / 2}px;top:${g.y0 + inizio}px;width:${s}px;height:${lunghezza}px;writing-mode:vertical-rl;text-orientation:sideways` + (lato === 'sinistra' ? ';transform:rotate(180deg)' : ''));
    const strisce = [];
    if (o.strisce) {
      for (const st of o.strisce) {
        const g = geometria[st.lato], lunghezza = st.fine - st.inizio;
        const testoRiga = g && lunghezza > 0 ? riga(misura, testo, lunghezza) : '';
        if (!testoRiga) continue;
        strisce.push({ lato: st.lato, inizio: Math.round(st.inizio), fine: Math.round(st.fine), testoRiga,
          colore: coloreSu(st.fondo), posto: postoDi(st.lato, g, st.inizio, lunghezza) });
      }
    } else for (const lato of lati) {
      const g = geometria[lato];
      if (!g || g.n <= 0) continue;
      // fondo lungo la striscia: tre letture di traverso (bordo, mezzo, bordo); vale solo se coincidono
      const chiavi = [];
      for (let t = 0; t <= g.n; t += passo) {
        const x = g.x0 + g.dx * t, y = g.y0 + g.dy * t;
        const k = [-mezzo, 0, mezzo].map((d) => fondo(x + g.dy * d, y + g.dx * d).join(','));
        chiavi.push(k.every((v) => v === k[0]) ? k[0] : null);
      }
      const conti = {};
      for (const k of chiavi) if (k) conti[k] = (conti[k] || 0) + 1;
      const prevalente = Object.entries(conti).sort((a, b) => b[1] - a[1])[0]?.[0];
      if (!prevalente) continue;
      // tratto continuo più lungo sul fondo prevalente
      let da = 0, a = 0;
      for (let i = 0; i < chiavi.length;) {
        if (chiavi[i] !== prevalente) { i++; continue; }
        let j = i;
        while (j < chiavi.length && chiavi[j] === prevalente) j++;
        if (j - i > a - da) { da = i; a = j; }
        i = j;
      }
      let inizio = da * passo, fine = Math.min(g.n, (a - 1) * passo);
      if (da > 0) inizio += corpo;                     // stacco dal fondo diverso
      if (a < chiavi.length) fine -= corpo;
      const lunghezza = fine - inizio, testoRiga = riga(misura, testo, lunghezza);
      if (lunghezza <= 0 || !testoRiga) continue;
      strisce.push({ lato, inizio: Math.round(inizio), fine: Math.round(fine), testoRiga,
        colore: coloreSu(prevalente.split(',').map(Number)), posto: postoDi(lato, g, inizio, lunghezza) });
    }
    // scritte (righe di testo, non i loro contenitori) e loghi che la cornice non deve toccare
    const ostacoli = [];
    for (const el of document.querySelectorAll('[data-campo], [data-logo], [data-firma], [data-ostacolo]')) {
      if (!el.getClientRects().length) continue;
      const nome = (el.getAttribute('data-campo') || el.getAttribute('alt') || el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 40);
      if (el.tagName === 'IMG') { ostacoli.push({ nome, q: el.getBoundingClientRect() }); continue; }
      const r = document.createRange(); r.selectNodeContents(el);
      for (const q of r.getClientRects()) if (q.width > 0 && q.height > 0) ostacoli.push({ nome, q });
    }
    const strato = document.createElement('div');
    strato.setAttribute('data-microtesto', '');
    strato.setAttribute('aria-hidden', 'true');
    strato.style.cssText = 'position:absolute;inset:0;pointer-events:none;z-index:9999';
    for (const st of strisce) {
      const el = document.createElement('div');
      el.style.cssText = `position:absolute;white-space:nowrap;text-align:center;overflow:hidden;font:600 ${corpo}px/${s}px ${CARATTERE},sans-serif;letter-spacing:0;color:${st.colore};${st.posto}`;
      for (const [i, p] of st.testoRiga.split(' ').entries()) {
        if (i) el.append(' ');
        const sp = document.createElement('span'); sp.textContent = p; el.append(sp);
      }
      strato.append(el);
    }
    tavola.append(strato);
    // ogni riga sta intera nella sua striscia: se il testo impaginato è più lungo della misura presa sul canvas,
    // il lato finisce fra le «tagliate» (rendi.py si ferma)
    const tagliate = [];
    for (const [i, el] of [...strato.children].entries()) {
      const r = document.createRange(); r.selectNodeContents(el);
      const q = r.getBoundingClientRect(), b = el.getBoundingClientRect();
      const fuori = strisce[i].posto.includes('vertical-rl') ? q.top < b.top - 0.5 || q.bottom > b.bottom + 0.5
        : q.left < b.left - 0.5 || q.right > b.right + 0.5;
      if (fuori) tagliate.push(strisce[i].lato);
    }
    const tocchi = new Set();
    let parole = 0;
    for (const sp of strato.querySelectorAll('span')) {
      const r = sp.getBoundingClientRect();
      parole++;
      for (const { nome, q } of ostacoli)
        if (Math.min(r.right, q.right) - Math.max(r.left, q.left) > 0 && Math.min(r.bottom, q.bottom) - Math.max(r.top, q.top) > 0) tocchi.add(nome);
    }
    return { parole, tocchi: [...tocchi], tagliate, strisce: strisce.map(({ lato, inizio, fine, testoRiga }) => ({ lato, inizio, fine, testo: testoRiga })) };
  };
})();
