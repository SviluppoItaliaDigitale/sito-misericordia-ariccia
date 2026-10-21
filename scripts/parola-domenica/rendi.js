// Carosello della Parola della domenica: node rendi.js SCHEDA.json CARTELLA_USCITA [OPERA.jpg]
// Crea AAAA-MM-GG-1.jpg … (JPEG 1080×1350, qualità 88): con l'opera la 1 è la copertina,
// poi una pagina per ogni versetto della scheda. Esce con errore se un testo non entra
// o se una scritta tocca ornamenti, stemma, filetti o opera; si rifiuta se manca il Vangelo.
// Dal 21/10/2026 (richiesta di Alessandro: «metti in ogni slide … sempre Misericordia di Ariccia!
// Altrimenti ci rubano la grafica!!») ogni pagina deve portare la firma «Misericordia di Ariccia»
// (elemento data-firma, ben visibile) ed esce con la cornice di microtesto lungo i bordi, fatta dal
// motore scripts/grafica-brand/firma-e-cornice.js, che scrive anche nel JPEG il segno che i
// controlli del sito cercano.
const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path');
const [scheda, cartella, opera] = process.argv.slice(2);
if (!scheda || !cartella) { console.error('uso: node rendi.js SCHEDA.json CARTELLA_USCITA [OPERA.jpg]'); process.exit(1); }
const chrome = process.env.CHROME || ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome']
  .concat(fs.existsSync('/opt/pw-browsers') ? fs.readdirSync('/opt/pw-browsers').filter(d => /^chromium-\d/.test(d)).map(d => `/opt/pw-browsers/${d}/chrome-linux/chrome`) : [])
  .find(p => fs.existsSync(p));
(async () => {
  const s = JSON.parse(fs.readFileSync(scheda, 'utf8'));
  if (!s.pagine.some(v => v.lettura === 'Vangelo')) { console.error('manca il Vangelo: ogni carosello deve avere almeno un versetto del Vangelo'); process.exit(1); }
  if (s.opera && !opera) { console.error('la scheda ha un\'opera: passare anche OPERA.jpg'); process.exit(1); }
  const conOpera = s.opera ? 1 : 0, n = s.pagine.length + conOpera;
  fs.mkdirSync(cartella, { recursive: true });
  const b = await chromium.launch({ executablePath: chrome, args: ['--allow-file-access-from-files'] });
  let errori = 0;
  const grafica = process.env.GRAFICA || 'grafica.html';  // GRAFICA=grafica-nazionale.html: proposta nello stile nazionale
  for (let k = 0; k < n; k++) {
    const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
    await p.goto('file://' + path.join(__dirname, grafica));
    const esito = k < conOpera
      ? await p.evaluate(([s, img, n]) => window.copertina(s, img, n), [s, 'file://' + path.resolve(opera), n])
      : await p.evaluate(([s, i, n, primo]) => window.versetto(s, i, n, primo), [s, k - conOpera, n, conOpera + 1]);
    const firma = await p.evaluate(() => {
      const f = [...document.querySelectorAll('[data-firma]')].find(el => el.getClientRects().length > 0);
      if (!f) return null;
      const cs = getComputedStyle(f), r = f.getBoundingClientRect();
      let opacita = 1;
      for (let el = f; el; el = el.parentElement) opacita *= parseFloat(getComputedStyle(el).opacity);
      return { testo: f.innerText.replace(/\s+/g, ' ').trim(), corpo: parseFloat(cs.fontSize), opacita,
               dentro: r.width > 0 && r.left >= 0 && r.top >= 0 && r.right <= 1080 && r.bottom <= 1350 && cs.visibility !== 'hidden' };
    });
    if (!firma || !/misericordia di ariccia/i.test(firma.testo)) { console.error(`ATTENZIONE: nella pagina ${k + 1} manca la firma «Misericordia di Ariccia»`); errori++; }
    else if (firma.corpo < 24 || firma.opacita < 0.8 || !firma.dentro) { console.error(`ATTENZIONE: nella pagina ${k + 1} la firma «Misericordia di Ariccia» non si legge bene (corpo ${firma.corpo}px, opacità ${firma.opacita})`); errori++; }
    const png = await p.screenshot({ type: 'png' });
    const motore = await b.newPage();
    await motore.goto('file://' + path.join(__dirname, '..', 'grafica-brand', 'firma-e-cornice.html'));
    const fatta = await motore.evaluate(([dati, o]) => window.firmaECornice(dati, o),
      // grafica.html ha i gigli negli angoli: la cornice lascia liberi gli 80 px di ogni angolo
      ['data:image/png;base64,' + png.toString('base64'), { formato: 'jpeg', qualita: 0.88, angoli: grafica === 'grafica.html' ? 80 : 0 }]);
    await motore.close();
    const file = path.join(cartella, `${s.data}-${k + 1}.jpg`);
    fs.writeFileSync(file, Buffer.from(fatta.dati.split(',')[1], 'base64'));
    console.log(`${file}${esito.corpo ? ` (versetto a ${esito.corpo}px)` : ''}`);
    if (esito.trabocca) { console.error(`ATTENZIONE: nella pagina ${k + 1} il testo non entra`); errori++; }
    for (const x of esito.sovrapposizioni || []) { console.error(`ATTENZIONE: nella pagina ${k + 1} ${x}`); errori++; }
    await p.close();
  }
  await b.close();
  process.exit(errori ? 2 : 0);
})();
