// fotogrammi singoli per controllo: KEY e T="scena:frazione,..." -> out/KEY/s<i>.png (lanciare da out/)
const { chromium } = require('playwright-core');
(async () => {
  const K = process.env.KEY, L = process.env.T.split(',');
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + process.cwd() + '/' + K + '/video.html?render=1'); await p.waitForFunction('window.__ready === true');
  for (const [i,x] of L.entries()){ const [k,f]=x.split(':').map(Number); const t = await p.evaluate(`START[${k}]+LEN[${k}]*${f}`); await p.evaluate(`window.renderFrame(${t})`); await p.screenshot({path:`${K}/s${i}.png`}); }
  await b.close();
})();
