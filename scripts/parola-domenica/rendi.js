// Grafica della Parola della domenica: node rendi.js SCHEDA.json OUT.jpg [OPERA.jpg]
// Riempie grafica.html con la scheda, aspetta font e immagine, salva JPEG 1080×1350 (qualità 88).
const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path');
const [scheda, uscita, opera] = process.argv.slice(2);
if (!scheda || !uscita) { console.error('uso: node rendi.js SCHEDA.json OUT.jpg [OPERA.jpg]'); process.exit(1); }
const chrome = process.env.CHROME || ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome']
  .concat(fs.existsSync('/opt/pw-browsers') ? fs.readdirSync('/opt/pw-browsers').filter(d => /^chromium-\d/.test(d)).map(d => `/opt/pw-browsers/${d}/chrome-linux/chrome`) : [])
  .find(p => fs.existsSync(p));
(async () => {
  const b = await chromium.launch({ executablePath: chrome, args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.goto('file://' + path.join(__dirname, 'grafica.html'));
  const dati = JSON.parse(fs.readFileSync(scheda, 'utf8'));
  const esito = await p.evaluate(([s, img]) => window.riempi(s, img), [dati, opera ? 'file://' + path.resolve(opera) : null]);
  await p.screenshot({ path: uscita, type: 'jpeg', quality: 88 });
  await b.close();
  console.log(`grafica salvata in ${uscita} (corpo del versetto ${esito.corpo}px)`);
  if (esito.trabocca) { console.error('ATTENZIONE: il versetto non entra, accorcialo'); process.exit(2); }
})();
