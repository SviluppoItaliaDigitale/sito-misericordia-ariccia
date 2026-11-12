// ===== Disegni di «Che cosa le ha insegnato la vita?» (novembre 2026): l'intervista immaginata fra Matteo, giovane
// volontario in divisa, e Maria, 87 anni (contenuti6.py). Nomi con il prefisso s8 per non urtare gli altri file. =====
const s8Maria = (o={}) => ({shirt:'#f3b9c4', shirtD:'#d995a4', under:()=>fc(0,-292,44,GRAYH), ...o, head:{hairCol:GRAYH, glasses:true, mouth:'smile', ...(o.head||{})}});
const s8Matteo = (o={}) => ({divisa:true, ...o, head:{hairCol:'#5a3a22', mouth:'smile', ...(o.head||{})}});
function s8Tavolo(){ box(-110,150,220,22,10,'#e3e7f1'); ln([[0,172],[0,250]],'#cfd6e8',12); }
function s8Posto(x,y,a){ if(a<=0.001) return; ctx.save(); ctx.globalAlpha*=clamp(a); fe(x,y,92,40,'#cfd6e8'); fe(x,y-5,92,40,'#fff'); fe(x,y-5,58,24,'#e9edf5');
  ln([[x-128,y-24],[x-128,y+20]],'#aab3cc',7); ln([[x+128,y-24],[x+128,y+20]],'#aab3cc',7); box(x+150,y-58,34,46,8,'rgba(159,216,240,.75)'); ctx.restore(); }
Object.assign(ILL, {
// la domanda: i due seduti uno di fronte all'altra, parla Matteo
'int-domanda'({u,A}){ ground(250); s8Tavolo();
  grp(-240,40,1,1,()=>bust(0,40,.55,s8Matteo({R:[[110,90],[150,150]]})));
  grp(240,40,1,1,()=>bust(0,40,.55,s8Maria({L:[[-110,90],[-150,150]]})));
  grp(-240,-262,1,A(.05),()=>{ bubble(0,0,170,104,'',0,30); const b=1+.08*Math.sin(u*3); ctx.save(); ctx.scale(b,b); tx('?',0,4,74,C.navy,'800'); ctx.restore(); }); },
// «Una mano sulla spalla»: Maria, il braccio di Matteo che le si posa sulla spalla, e la domanda che conta
'cose-piccole'({u,A}){ ground(250);
  grp(130,30,1,1,()=>bust(0,40,.66,s8Maria()));
  const k=outCubic(clamp(A(.38))); if(k>0){ ctx.save(); ctx.globalAlpha*=clamp(k*1.4);
    arm(-330,262,[[-190,70-(1-k)*40],[44-(1-k)*90,2+(1-k)*30]],'#6f86d6',DIV,50); ctx.restore(); }
  grp(-215,-205,1,A(.62),()=>bubble(0,0,330,104,'Come stai?',46,90));
  const f=(u*.5)%1; ctx.save(); ctx.globalAlpha*=clamp(A(.45))*(1-f); ctx.fillStyle=RED; heartP(-40,10-f*50,.26); ctx.fill(); ctx.restore(); },
// «Adesso che il tempo ce l'ho»: Maria, l'orologio che va piano e la sedia vuota accanto a lei
'tempo-vuoto'({u,A}){ ground(250);
  grp(-250,40,1,1,()=>bust(0,40,.55,s8Maria({head:{mouth:'flat'}})));
  grp(0,-165,1,A(.05),()=>{ fc(0,0,96,'#fff'); arc(0,0,96,0,TAU,C.giallo,10);
    for(let i=0;i<12;i++){ const a=i/12*TAU; ln([[Math.cos(a)*74,Math.sin(a)*74],[Math.cos(a)*84,Math.sin(a)*84]],C.navy,i%3?4:7); }
    const m=u*.35, h=2.2+u*.03; ln([[0,0],[Math.sin(h)*44,-Math.cos(h)*44]],C.navy,10); ln([[0,0],[Math.sin(m)*70,-Math.cos(m)*70]],C.ciano,7); fc(0,0,9,C.navy); });
  grp(250,60,1,A(.7),()=>{ box(-78,-190,156,220,26,'#6b7491'); box(-60,-172,120,184,18,'#55607f'); box(-96,30,192,34,12,'#7d87a6'); ln([[-80,64],[-80,190]],'#55607f',14); ln([[80,64],[80,190]],'#55607f',14);
    ctx.save(); ctx.setLineDash([12,12]); arc(0,-250,46,0,TAU,'rgba(255,255,255,.45)',5); ctx.restore(); }); },
// «Apparecchio ancora per due… e tolgo un piatto»: la tavola sotto la lampada, due posti, poi uno solo
'tavola-due'({u,p}){
  ln([[0,-320],[0,-250]],'#8f9abb',6); poly([[-70,-190],[70,-190],[40,-250],[-40,-250]],C.giallo);
  const g=ctx.createLinearGradient(0,-190,0,120); g.addColorStop(0,'rgba(252,235,12,.30)'); g.addColorStop(1,'rgba(252,235,12,0)');
  ctx.fillStyle=g; ctx.beginPath(); ctx.moveTo(-70,-190); ctx.lineTo(70,-190); ctx.lineTo(330,120); ctx.lineTo(-330,120); ctx.closePath(); ctx.fill();
  [-215,215].forEach(x=>{ box(x-74,-120,148,150,22,'#6b7491'); box(x-58,-104,116,118,14,'#55607f'); });   // le due sedie
  fe(0,96,430,112,'#c3cbe0'); fe(0,84,430,112,'#eef1f8');   // la tovaglia
  s8Posto(-215,70,1);
  const t=clamp((p-.66)/.2), k=inOut(t);   // «tolgo un piatto»: il secondo posto si alza e svanisce
  ctx.save(); ctx.translate(0,-k*70); s8Posto(215,70,1-k); ctx.restore();
  if(k>0){ ctx.save(); ctx.globalAlpha*=k; ctx.setLineDash([14,14]); ctx.strokeStyle='rgba(143,154,187,.9)'; ctx.lineWidth=5; ctx.beginPath(); ctx.ellipse(215,65,92,40,0,0,TAU); ctx.stroke(); ctx.restore(); } },
// «Mi hai dato tutto»: le mani che si tengono sopra il tavolo e il cuore che sale
insieme({u,A}){ ground(250); s8Tavolo();
  grp(-215,40,1,1,()=>bust(0,40,.55,s8Matteo({R:[[150,120],[330,205]]})));
  grp(215,40,1,1,()=>bust(0,40,.55,s8Maria({head:{closed:true}, L:[[-150,120],[-330,205]]})));
  fc(0,150,26,SKD); fc(-10,146,20,SK); fc(12,148,20,'#efd3bd');
  for(let i=0;i<3;i++){ const f=(u*.45+i/3)%1; ctx.save(); ctx.globalAlpha*=clamp(A(.3))*Math.sin(f*Math.PI); ctx.fillStyle=RED; heartP(Math.sin(i*2.1+f*3)*26,70-f*250,.3+.12*i); ctx.fill(); ctx.restore(); } },
// «La sua solitudine, no»: il paese di sera, tante finestre spente e una sola accesa, con qualcuno dietro
'finestra-accesa'({u,A}){ ctx.save(); rr(ctx,-440,-300,880,550,30); ctx.clip(); ctx.fillStyle='#0b2550'; ctx.fillRect(-440,-300,880,550);
  fc(300,-215,44,'#f6f1c8'); fc(318,-226,38,'#0b2550');
  for(let i=0;i<26;i++){ const a=.35+.65*Math.abs(Math.sin(u*.9+i*1.7)); fc(-430+hash(i)*860,-290+hash(i+40)*150,2.2,`rgba(255,255,255,${a*.8})`); }
  [[-440,250,-40],[-180,330,-130],[160,280,-70]].forEach(([x,w,top],j)=>{ box(x,top,w,300-top,0,j===1?'#1d3a70':'#17305f');
    const cols=Math.floor(w/90), rows=Math.floor((250-top)/100);
    for(let r=0;r<rows;r++) for(let c=0;c<cols;c++){ const wx=x+28+c*((w-56-54)/Math.max(1,cols-1)), wy=top+36+r*96, lit=j===1&&r===1&&c===1;
      if(lit){ const al=clamp(A(.3)); box(wx-6,wy-6,66,82,6,`rgba(252,235,12,${.25*al})`); box(wx,wy,54,70,4,al>0?`rgba(252,235,12,${.35+.65*al})`:'#0e2247');
        if(al>0){ ctx.save(); ctx.globalAlpha*=al; fc(wx+27,wy+34,13,'#17305f'); box(wx+9,wy+46,36,24,10,'#17305f'); ctx.restore(); } }
      else box(wx,wy,54,70,4,'#0e2247'); } });
  ctx.restore(); },
});
