// Prova d'impaginazione (vedi prova_impaginazione.py): per ogni scena il fotogramma più a rischio
// con sovrapposta la zona coperta dai comandi di Instagram, in KEY/prova.png.
const { chromium } = require('playwright-core');
(async () => {
  const K = process.env.KEY;
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + process.cwd() + '/' + K + '/video.html?render=1'); await p.waitForFunction('window.__ready === true');
  // Per ogni scena prova dieci istanti della voce e tiene quello con il sottotitolo più alto (frase più lunga),
  // a parità quello che scende di più: è il caso peggiore da confrontare con la zona di Instagram e con le etichette.
  const times = [];
  const n = await p.evaluate('SCENE.length');
  for (let k = 0; k < n; k++) {
    const prove = await p.evaluate(`(()=>{const k=${k},Dv=SCENE[k].conta?CONTA.voce:DUR[k];return [...Array(10)].map((_,i)=>START[k]+PRE+Dv*(i+.5)/10)})()`);
    let migliore = prove[prove.length - 1], fondo = -1;
    for (const t of prove) {
      await p.evaluate(`window.renderFrame(${t})`);
      const b = await p.evaluate(`(()=>{const e=document.getElementById('sub'),c=getComputedStyle(e);if(c.display==='none'||+c.opacity<.5||!e.textContent.trim())return -1;const r=e.firstElementChild.getBoundingClientRect();return r.height*10000+r.bottom})()`);
      if (b > fondo) { fondo = b; migliore = t; }
    }
    times.push(migliore);
  }
  // Zona dei comandi di Instagram (Reels): fascia in basso e colonna dei pulsanti a destra.
  const zona = `const z=document.createElement('div');z.id='zona-ig';z.style.cssText='position:fixed;left:0;right:0;bottom:0;height:380px;background:rgba(255,60,60,.28);z-index:50;pointer-events:none';
    const c=document.createElement('div');c.style.cssText='position:fixed;right:0;bottom:380px;width:150px;height:330px;background:rgba(255,60,60,.22);z-index:50;pointer-events:none';
    document.body.append(z,c);`;
  await p.evaluate(zona);
  const shots = [];
  for (const t of times) { await p.evaluate(`window.renderFrame(${t})`); shots.push((await p.screenshot({ type: 'png' })).toString('base64')); }
  const cols = Math.min(5, shots.length), w = 270, h = 480;
  const html = `<body style="margin:0;background:#000;display:grid;grid-template-columns:repeat(${cols},${w}px);gap:4px">` + shots.map(s => `<img src="data:image/png;base64,${s}" style="width:${w}px;height:${h}px">`).join('') + '</body>';
  const q = await b.newPage({ viewport: { width: cols * (w + 4), height: Math.ceil(shots.length / cols) * (h + 4) } });
  await q.setContent(html); await q.screenshot({ path: K + '/prova.png', fullPage: true });
  console.log('errori:', JSON.stringify(errs.slice(0, 5))); await b.close();
})();
