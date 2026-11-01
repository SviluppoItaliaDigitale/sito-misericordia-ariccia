// Solo il disegno di una scena, per la grafica della news (modello nazionale «post con fascia», campo foto): fotogramma
// della scena S a frazione F (0-1) di out/KEY/video.html, senza scritte, etichette, sottotitoli, scheda e cornice
// (la cornice la mette rendi.py), ritagliato 1080x1350 con il disegno in alto al centro -> out/KEY/disegno.png.
// Uso (da out/): KEY=dae S=0 F=0.8 node ../disegno.js  (Y = dove parte il ritaglio, 230 di base: il disegno resta sotto la fascia)
const { chromium } = require('playwright-core');
(async () => {
  const K = process.env.KEY, S = Number(process.env.S || 0), F = Number(process.env.F || 0.85);
  const b = await chromium.launch({ executablePath: require('./chrome')() });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + process.cwd() + '/' + K + '/video.html?render=1'); await p.waitForFunction('window.__ready === true');
  await p.evaluate(`(()=>{ const t=START[${S}]+PRE+DUR[${S}]*${F}; window.renderFrame(t);
    for (const id of ['chip','title','tags','card','sos','motto','fonte','sub','fx','cornice']) { const e=document.getElementById(id); if(e) e.style.visibility='hidden'; }
    // fascia, stemma e firma del video stanno sul fondo (#bg) in alto: si coprono prolungando verso l'alto la sfumatura
    const g=document.getElementById('bg').getContext('2d'), riga=g.getImageData(0,360,1080,1); for(let y=0;y<360;y++) g.putImageData(riga,0,y); })()`);
  await p.screenshot({ path: `${K}/disegno.png`, clip: { x: 0, y: Number(process.env.Y || 230), width: 1080, height: 1350 } });
  await b.close(); console.log(`${K}/disegno.png`);
})();
