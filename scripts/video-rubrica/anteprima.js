// foglio di anteprima: per ogni scena un fotogramma a fine voce (ridotto), in KEY/foglio.png
const { chromium } = require('playwright-core');
(async () => {
  const K = process.env.KEY;
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const errs=[]; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if(m.type()==='error') errs.push(m.text()); });
  await p.goto('file://' + process.cwd() + '/' + K + '/video.html?render=1'); await p.waitForFunction('window.__ready === true');
  const times = await p.evaluate(`START.map((s,k)=>s+PRE+(SCENE[k].conta?CONTA.at+CONTA.beat*16.2:DUR[k]*.92))`);
  const shots=[];
  for (const t of times){ await p.evaluate(`window.renderFrame(${t})`); shots.push((await p.screenshot({type:'png', clip:{x:0,y:100,width:1080,height:1500}})).toString('base64')); }
  const cols=4, w=270, h=375;
  const html = `<body style="margin:0;background:#000;display:grid;grid-template-columns:repeat(${cols},${w}px);gap:4px">`+shots.map(s=>`<img src="data:image/png;base64,${s}" style="width:${w}px;height:${h}px">`).join('')+'</body>';
  const q = await b.newPage({ viewport: { width: cols*(w+4), height: Math.ceil(shots.length/cols)*(h+4) } });
  await q.setContent(html); await q.screenshot({ path: K + '/foglio.png', fullPage:true });
  console.log('errori:', JSON.stringify(errs.slice(0,10))); await b.close();
})();
