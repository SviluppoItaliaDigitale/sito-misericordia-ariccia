// Carosello della Parola della domenica: node rendi.js SCHEDA.json CARTELLA_USCITA [OPERA.jpg]
// Crea AAAA-MM-GG-1.jpg … (JPEG 1080×1350, qualità 88): con l'opera la 1 è la copertina,
// poi una pagina per ogni versetto della scheda. Esce con errore se un testo non entra
// o se una scritta tocca ornamenti, stemma, filetti o opera; si rifiuta se manca il Vangelo.
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
  for (let k = 0; k < n; k++) {
    const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
    await p.goto('file://' + path.join(__dirname, 'grafica.html'));
    const esito = k < conOpera
      ? await p.evaluate(([s, img, n]) => window.copertina(s, img, n), [s, 'file://' + path.resolve(opera), n])
      : await p.evaluate(([s, i, n, primo]) => window.versetto(s, i, n, primo), [s, k - conOpera, n, conOpera + 1]);
    const file = path.join(cartella, `${s.data}-${k + 1}.jpg`);
    await p.screenshot({ path: file, type: 'jpeg', quality: 88 });
    console.log(`${file}${esito.corpo ? ` (versetto a ${esito.corpo}px)` : ''}`);
    if (esito.trabocca) { console.error(`ATTENZIONE: nella pagina ${k + 1} il testo non entra`); errori++; }
    for (const x of esito.sovrapposizioni || []) { console.error(`ATTENZIONE: nella pagina ${k + 1} ${x}`); errori++; }
    await p.close();
  }
  await b.close();
  process.exit(errori ? 2 : 0);
})();
