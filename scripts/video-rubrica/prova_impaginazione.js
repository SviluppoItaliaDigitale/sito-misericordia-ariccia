// Prova d'impaginazione (vedi prova_impaginazione.py): per ogni scena il fotogramma più a rischio
// con sovrapposta la zona coperta dai comandi di Instagram (in rosso) e la firma (in verde), in KEY/prova.png.
// Esce con 1 se manca la firma o la cornice, se una scritta o un disegno tocca la firma, o se un'email o un sito va a
// capo a metà.
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
      // Controllo numerico: sottotitolo nella fascia bassa, sopra le etichette, etichette sotto i pulsanti a destra.
      const guai = await p.evaluate(`(()=>{const g=[],s=document.getElementById('sub'),r=s.firstElementChild.getBoundingClientRect(),vis=getComputedStyle(s).display!=='none'&&+s.style.opacity>.5&&s.textContent.trim();
        if(vis&&r.bottom>1540)g.push('sottotitolo nella fascia bassa');
        document.querySelectorAll('#tags .tag').forEach(e=>{if(+e.style.opacity<.5)return;const q=e.getBoundingClientRect();
          if(vis&&q.bottom>r.top&&q.top<r.bottom&&q.right>r.left&&q.left<r.right)g.push("sottotitolo sopra un'etichetta");
          if(q.right>930&&q.bottom>1210)g.push('etichetta sotto i pulsanti')});return [...new Set(g)]})()`);
      if (guai.length) console.log('ATTENZIONE scena', k + 1, 'a', t.toFixed(1), 's:', guai.join(', '));
      // Firma «Misericordia di Ariccia» (regola del 21/10/2026): c'è, è grande abbastanza, sta fuori dalle zone di
      // Instagram e nessuna scritta o disegno la tocca; il titolo resta sopra la zona dei disegni (505 px).
      const firma = await p.evaluate(`(()=>{ const g=[], f=window.FIRMA_BOX; if(!f) return ['firma assente'];
        if(f.corpo<24) g.push('firma più piccola di 24 px'); if(f.y<150) g.push('firma nella fascia alta');
        if(f.y+f.h>1540) g.push('firma nella fascia bassa di Instagram'); if(f.x+f.w>930&&f.y+f.h>1210) g.push('firma sotto i pulsanti di Instagram');
        const m=8, fr={l:f.x-m,t:f.y-m,r:f.x+f.w+m,b:f.y+f.h+m};
        for(const s of ['#chip','#title .in','#tags .tag','#sub span','#card','#sos','#motto','#fonte']) for(const e of document.querySelectorAll(s)){
          if(!e.offsetParent&&getComputedStyle(e).position!=='fixed') continue; let op=1; for(let x=e;x&&x.nodeType===1;x=x.parentElement) op*=+getComputedStyle(x).opacity; if(op<.05) continue;
          for(const q of e.getClientRects()) if(q.width>0&&q.height>0&&q.right>fr.l&&q.left<fr.r&&q.bottom>fr.t&&q.top<fr.b) g.push('una scritta tocca la firma ('+s+')'); }
        const d=cv.getContext('2d').getImageData(f.x-m,f.y-m,f.w+2*m,f.h+2*m).data; for(let i=3;i<d.length;i+=4) if(d[i]>20){ g.push('un disegno tocca la firma'); break; }
        if(document.getElementById('title').getBoundingClientRect().bottom>505) g.push('titolo nella zona dei disegni (oltre 505 px)');
        return [...new Set(g)]; })()`);
      if (firma.length) { console.log('ERRORE scena', k + 1, 'a', t.toFixed(1), 's:', firma.join(', ')); process.exitCode = 1; }
    }
    times.push(migliore);
  }
  // Email e siti interi sulla stessa riga, nella chiusura con tutto in vista (il 21/10/2026 la fonte della Giornata del
  // volontariato andava a capo dentro «sede@misericordia-ariccia.it»).
  await p.evaluate('window.renderFrame(TOTAL-0.05)');
  const spezzati = await p.evaluate(`(()=>{ const out=[], w=document.createTreeWalker(document.getElementById('stage'),NodeFilter.SHOW_TEXT); let n;
    while((n=w.nextNode())){ const re=/\\S+@\\S+|[\\w.-]+\\.(?:it|org|com|eu)\\b/g; let m;
      while((m=re.exec(n.data))){ const r=document.createRange(); r.setStart(n,m.index); r.setEnd(n,m.index+m[0].length);
        if(new Set([...r.getClientRects()].filter(q=>q.width>0).map(q=>Math.round(q.top))).size>1) out.push(m[0]); } }
    return out; })()`);
  if (spezzati.length) { console.log('ERRORE indirizzo spezzato a capo:', spezzati.join(', ')); process.exitCode = 1; }
  // Cornice di microtesto: c'è su tutti e quattro i lati (strato #cornice del motore firma-e-cornice.js).
  const cornice = await p.evaluate(`(()=>{ const e=window.CORNICE_ESITO; if(!e) return 'cornice assente';
    const c=document.getElementById('cornice').getContext('2d'), W=1080, H=1920, s=e.striscia;
    const conta=(x,y,w,h)=>{ const d=c.getImageData(x,y,w,h).data; let n=0; for(let i=3;i<d.length;i+=4) if(d[i]>0) n++; return n; };
    const vuoti=Object.entries({alto:conta(0,0,W,s), basso:conta(0,H-s,W,s), sinistra:conta(0,0,s,H), destra:conta(W-s,0,s,H)}).filter(([,n])=>n<500).map(([k])=>k);
    return vuoti.length ? 'cornice mancante sul lato '+vuoti.join(', ') : ''; })()`);
  if (cornice) { console.log('ERRORE', cornice); process.exitCode = 1; }
  // Zona dei comandi di Instagram (Reels): fascia in basso e colonna dei pulsanti a destra; in verde la firma.
  const zona = `const z=document.createElement('div');z.id='zona-ig';z.style.cssText='position:fixed;left:0;right:0;bottom:0;height:380px;background:rgba(255,60,60,.28);z-index:50;pointer-events:none';
    const c=document.createElement('div');c.style.cssText='position:fixed;right:0;bottom:380px;width:150px;height:330px;background:rgba(255,60,60,.22);z-index:50;pointer-events:none';
    const f=window.FIRMA_BOX, v=document.createElement('div');v.style.cssText='position:fixed;left:'+(f.x-4)+'px;top:'+(f.y-4)+'px;width:'+(f.w+8)+'px;height:'+(f.h+8)+'px;outline:3px solid #2bd14b;z-index:50;pointer-events:none';
    document.body.append(z,c,v);`;
  await p.evaluate(zona);
  const shots = [];
  for (const t of times) { await p.evaluate(`window.renderFrame(${t})`); shots.push((await p.screenshot({ type: 'png' })).toString('base64')); }
  const cols = Math.min(5, shots.length), w = 270, h = 480;
  const html = `<body style="margin:0;background:#000;display:grid;grid-template-columns:repeat(${cols},${w}px);gap:4px">` + shots.map(s => `<img src="data:image/png;base64,${s}" style="width:${w}px;height:${h}px">`).join('') + '</body>';
  const q = await b.newPage({ viewport: { width: cols * (w + 4), height: Math.ceil(shots.length / cols) * (h + 4) } });
  await q.setContent(html); await q.screenshot({ path: K + '/prova.png', fullPage: true });
  console.log('errori:', JSON.stringify(errs.slice(0, 5))); await b.close();
})();
