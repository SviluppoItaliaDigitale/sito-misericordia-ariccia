// grafica della news senza sottotitolo: fotogramma a T secondi (1,8) di out/KEY/video.html -> out/KEY/grafica.png (lanciare da out/)
// Dal 17/10/2026 il sottotitolo sta a 1300 px e finirebbe nel ritaglio 1080x1350 della grafica: qui si nasconde.
const { chromium } = require('playwright-core');
(async () => {
  const K = process.env.KEY, T = Number(process.env.T || 1.8);
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + process.cwd() + '/' + K + '/video.html?render=1'); await p.waitForFunction('window.__ready === true');
  await p.evaluate(`window.renderFrame(${T}); document.getElementById('sub').style.visibility='hidden'`);
  await p.screenshot({ path: `${K}/grafica.png` });
  await b.close();
})();
