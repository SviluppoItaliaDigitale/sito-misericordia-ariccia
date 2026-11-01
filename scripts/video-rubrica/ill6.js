// ===== Disegni della 3ª serie: ferite, dente, occhi-chimici, zecche (si aggiungono a ILL) =====
// Funzioni e costanti di questo file hanno il prefisso s6/S6_: tutti gli ill*.js finiscono in un solo script.
const S6_DENTE='#f8f6ee', S6_RADICE='#e2c693', S6_BORDO='#bdb39a', S6_ERBA='#4f8f3e', S6_ERBA2='#7cc46a',
  S6_ZECCA='#5a321f', S6_ZECCAD='#2e1a10', S6_ROSA='#ec9cc0', S6_LATTE='#f6f3ea', S6_ACQUA='#9fd8f0', S6_GUANTO='#7b6fd6';
// scritte dei disegni nel carattere del kit nazionale
function s6Tx(s,x,y,size,col,wt='700'){ ctx.fillStyle=col; ctx.font=`${wt} ${size}px Montserrat, sans-serif`; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText(s,x,y); }
// dente incisivo: corona in basso (bordo a y=130*s), radice in alto lunga L; o.rotto = spigolo scheggiato
function s6Dente(x,y,s,rot=0,o={}){ const L=o.L||190; ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s);
  ctx.beginPath(); ctx.moveTo(-48,12); ctx.quadraticCurveTo(-46,-L*.62,-12,-L); ctx.quadraticCurveTo(0,-L-8,12,-L); ctx.quadraticCurveTo(46,-L*.62,48,12); ctx.closePath();
  ctx.fillStyle=o.radiceCol||S6_RADICE; ctx.fill(); ctx.strokeStyle=S6_BORDO; ctx.lineWidth=4; ctx.stroke();
  ctx.beginPath(); ctx.moveTo(-50,0); ctx.bezierCurveTo(-62,50,-66,100,-60,125);
  if(o.rotto){ ctx.quadraticCurveTo(-25,134,8,133); ctx.lineTo(24,110); ctx.lineTo(40,114); ctx.lineTo(58,90); ctx.bezierCurveTo(64,60,62,30,50,0); }
  else { ctx.quadraticCurveTo(0,140,60,125); ctx.bezierCurveTo(66,100,62,50,50,0); }
  ctx.quadraticCurveTo(0,-14,-50,0); ctx.closePath(); ctx.fillStyle=S6_DENTE; ctx.fill(); ctx.strokeStyle=S6_BORDO; ctx.lineWidth=4; ctx.stroke();
  fe(-22,50,10,34,'rgba(255,255,255,.9)',.1);
  ctx.restore(); }
// il pezzo che manca al dente scheggiato (stesse coordinate di s6Dente)
function s6Scheggia(x,y,s,rot=0){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s);
  ctx.beginPath(); ctx.moveTo(8,133); ctx.lineTo(24,110); ctx.lineTo(40,114); ctx.lineTo(58,90); ctx.bezierCurveTo(63,104,63,116,60,125); ctx.quadraticCurveTo(34,132,8,133); ctx.closePath();
  ctx.fillStyle=S6_DENTE; ctx.fill(); ctx.strokeStyle=S6_BORDO; ctx.lineWidth=4; ctx.stroke(); ctx.restore(); }
// molare stilizzato con la croce: lo studio del dentista
function s6Dentista(x,y,r){ fc(x,y,r,C.tile); ctx.save(); ctx.translate(x,y); ctx.scale(r/130,r/130);
  ctx.fillStyle='#fff'; ctx.beginPath(); ctx.moveTo(-62,-30); ctx.bezierCurveTo(-70,-90,-20,-90,0,-66); ctx.bezierCurveTo(20,-90,70,-90,62,-30);
  ctx.bezierCurveTo(58,10,48,30,40,80); ctx.quadraticCurveTo(30,96,20,80); ctx.lineTo(8,30); ctx.quadraticCurveTo(0,22,-8,30); ctx.lineTo(-20,80); ctx.quadraticCurveTo(-30,96,-40,80); ctx.bezierCurveTo(-48,30,-58,10,-62,-30); ctx.fill();
  cross(70,-70,.32,C.giallo); ctx.restore(); }
// fialetta monodose di soluzione fisiologica (plastica trasparente, tappo da svitare, etichetta 0,9%)
function s6Fiala(x,y,s,rot=0){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s);
  box(-34,-70,68,150,22,'rgba(235,246,252,.95)'); box(-28,-10,56,84,16,'rgba(159,216,240,.75)');
  box(-12,-96,24,30,6,'rgba(235,246,252,.95)'); box(-30,-128,60,34,10,'#e3e7f1'); ln([[-22,-111],[22,-111]],'#cfd6e8',4);
  box(-34,-46,68,40,4,'#fff'); s6Tx('0,9%',0,-26,22,C.ciano,'800'); fe(-16,30,6,22,'rgba(255,255,255,.7)'); ctx.restore(); }
// cronometro che corre
function s6Crono(x,y,r,u){ box(x-r*.18,y-r*1.28,r*.36,r*.24,6,'#cfd6e8'); fc(x,y,r,'#fff'); arc(x,y,r-6,0,TAU,C.navy,8);
  for(let i=0;i<12;i++){ const a=i/12*TAU; ln([[x+Math.cos(a)*r*.72,y+Math.sin(a)*r*.72],[x+Math.cos(a)*r*.84,y+Math.sin(a)*r*.84]],C.navy,4); }
  const a=u*TAU*.5-Math.PI/2; ln([[x,y],[x+Math.cos(a)*r*.7,y+Math.sin(a)*r*.7]],RED,7); fc(x,y,8,C.navy); }
// dito: dalla base alla punta, con l'unghia
function s6Dito(x0,y0,x1,y1,w){ ln([[x0,y0],[x1,y1]],SKD,w+8); ln([[x0,y0],[x1,y1]],SK,w); const a=Math.atan2(y1-y0,x1-x0);
  fe(x1-Math.cos(a)*w*.42,y1-Math.sin(a)*w*.42,w*.36,w*.26,'#f6dccb',a); }
// pinzetta a punte sottili: punte in (x,y), il corpo si allunga verso l'alto ruotato di rot; ap = apertura
function s6Pinzetta(x,y,rot,ap=0,s=1){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s);
  [-1,1].forEach(k=>{ const P=[[k*(3+ap),0],[k*(9+ap*.8),-70],[k*24,-200],[k*8,-330]]; ln(P,'#8f9abb',17); ln(P,'#e6eaf3',11); ln([P[0],P[1]],'#e6eaf3',6); });
  ln([[-8,-330],[8,-330]],'#8f9abb',17); ctx.restore(); }
// zecca vista dall'alto: testa (rostro) verso +y
function s6Zecca(x,y,s,rot=0,o={}){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s*(o.sx||1),s*(o.sy||1));
  const L=[[28,26,58,40,66,74],[30,12,66,14,80,40],[30,-2,68,-10,82,8],[28,-16,60,-34,70,-56]];
  L.forEach(([a,b,c,d,e,f],i)=>{ const w=o.cammina?Math.sin(o.cammina+i*1.6)*6:0; [-1,1].forEach(k=>ln([[k*a,b],[k*c,d+w*k],[k*e,f+w*k]],S6_ZECCAD,6)); });
  box(-9,36,18,26,6,S6_ZECCAD); fe(0,-2,34,44,S6_ZECCA); fe(0,24,26,20,S6_ZECCAD); fe(-10,-14,8,12,'rgba(255,255,255,.18)',.3);
  ctx.restore(); }
// lembo di pelle in sezione: superficie a y=y0
function s6Pelle(y0,x0=-440,x1=440,y1=250){ box(x0,y0,x1-x0,y1-y0,24,SK); box(x0,y0+60,x1-x0,y1-y0-60,0,SKD); for(let i=0;i<7;i++){ const xx=x0+50+i*(x1-x0-100)/6; ln([[xx,y0+2],[xx+8,y0-14]],'#b98a68',3); } }
function s6Termo(x,y,s,lv){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-22,-150,44,210,22,'#fff'); fc(0,70,36,'#fff'); fc(0,70,24,RED);
  box(-9,50-lv*180,18,lv*180+20,9,RED); for(let i=0;i<5;i++) ln([[12,-110+i*34],[22,-110+i*34]],'#aab3cc',4); ctx.restore(); }
function s6Cerotto(x,y,w,h,rot=0,o={}){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); box(-w/2,-h/2,w,h,h/2,'#e7c39a'); box(-w*.2,-h*.36,w*.4,h*.72,8,'#f7efe4');
  for(let i=0;i<3;i++){ fc(-w*.36,-h*.2+i*h*.2,3,'#c9a37a'); fc(w*.36,-h*.2+i*h*.2,3,'#c9a37a'); }
  if(o.sporco){ fe(w*.04,h*.04,w*.12,h*.2,'rgba(140,90,50,.75)',.4); fc(-w*.08,-h*.12,h*.08,'rgba(140,90,50,.6)'); }
  ctx.restore(); }
function s6Cotone(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); [[-30,8,34],[0,-14,38],[30,6,34],[2,18,34],[-14,-2,30]].forEach(([a,b,r])=>fc(a,b,r,'#fbfbf8'));
  ctx.strokeStyle='rgba(255,255,255,.9)'; ctx.lineWidth=3; ctx.beginPath(); ctx.moveTo(56,20); ctx.quadraticCurveTo(80,30,92,14); ctx.moveTo(40,36); ctx.quadraticCurveTo(60,60,84,52); ctx.stroke(); ctx.restore(); }
// bottiglia d'alcol: liquido rosa, etichetta «alcol»
function s6Alcol(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-50,-60,100,160,22,'rgba(255,255,255,.55)'); box(-44,-20,88,114,18,S6_ROSA);
  box(-20,-108,40,52,8,'rgba(255,255,255,.55)'); box(-24,-128,48,26,8,'#fff'); box(-42,6,84,44,6,'#fff'); s6Tx('alcol',0,29,26,C.navy,'800'); ctx.restore(); }
function s6Olio(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.fillStyle='rgba(201,178,58,.95)'; ctx.beginPath(); ctx.moveTo(-40,100); ctx.lineTo(-40,-10); ctx.quadraticCurveTo(-40,-50,-14,-70); ctx.lineTo(-14,-110); ctx.lineTo(14,-110); ctx.lineTo(14,-70); ctx.quadraticCurveTo(40,-50,40,-10); ctx.lineTo(40,100); ctx.closePath(); ctx.fill();
  box(-18,-132,36,26,6,'#3a7d3a'); fe(-20,10,6,40,'rgba(255,255,255,.4)'); box(-32,20,64,40,6,'#f3ead8'); ctx.restore(); }
function s6Tanica(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-70,-60,140,160,16,'#d23b2f'); box(-50,-92,60,40,10,'#d23b2f'); box(-38,-82,36,20,8,C.tile);
  box(28,-86,26,40,6,'#a92a20'); ln([[-50,-10],[50,70]],'rgba(0,0,0,.18)',10); ln([[50,-10],[-50,70]],'rgba(0,0,0,.18)',10); ctx.restore(); }
function s6Fiammifero(x,y,s,u){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.rotate(.35); box(-8,-40,16,150,6,'#e9cf9a'); fe(0,-46,14,18,'#8a2a1a');
  const f=1+Math.sin(u*14)*.08; ctx.save(); ctx.translate(0,-62); ctx.scale(f,1/f); ctx.fillStyle='#f2a541'; ctx.beginPath(); ctx.moveTo(0,-70); ctx.quadraticCurveTo(34,-20,18,8); ctx.quadraticCurveTo(0,22,-18,8); ctx.quadraticCurveTo(-34,-20,0,-70); ctx.fill();
  ctx.fillStyle=C.giallo; ctx.beginPath(); ctx.moveTo(0,-36); ctx.quadraticCurveTo(16,-8,8,6); ctx.quadraticCurveTo(0,12,-8,6); ctx.quadraticCurveTo(-16,-8,0,-36); ctx.fill(); ctx.restore(); ctx.restore(); }
// flacone di detersivo (tappo chiuso) con il simbolo di pericolo
function s6Pericolo(x,y,r){ ctx.save(); ctx.translate(x,y); ctx.rotate(Math.PI/4); box(-r*.7,-r*.7,r*1.4,r*1.4,4,RED); box(-r*.55,-r*.55,r*1.1,r*1.1,2,'#fff'); ctx.restore(); box(x-r*.09,y-r*.5,r*.18,r*.62,r*.08,'#1a1f36'); fc(x,y+r*.4,r*.11,'#1a1f36'); }
function s6Flacone(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-80,-90,160,220,34,'#3fa0d8'); arc(52,-40,44,-1.6,1.4,'#3fa0d8',22); box(-36,-140,60,60,10,'#3fa0d8'); box(-44,-160,76,30,10,'#fff');
  box(-62,-20,124,120,14,'#fff'); s6Pericolo(0,40,46); ctx.restore(); }
function s6Collirio(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-40,-40,80,130,18,'#fff'); box(-40,10,80,40,0,C.ciano); poly([[-22,-40],[22,-40],[6,-110],[-6,-110]],'#fff'); box(-28,-62,56,22,6,'#e3e7f1'); ctx.restore(); }
function s6Guanto(x,y,s,rot=0,flip=false){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(flip?-s:s,s); const col=S6_GUANTO;
  box(-80,-60,160,190,60,col); for(let j=0;j<4;j++) box(-76+j*40,-200+Math.abs(j-1.5)*18,34,170,17,col); ctx.save(); ctx.translate(80,10); ctx.rotate(-.7); box(-18,-110,36,120,18,col); ctx.restore(); box(-90,120,180,70,20,'#6a5ec4'); ctx.restore(); }
function s6Occhiali(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ln([[-170,-6],[-120,-10]],'#3a4570',16); ln([[170,-6],[120,-10]],'#3a4570',16);
  box(-130,-56,260,104,40,'rgba(159,216,240,.75)'); sbox(-130,-56,260,104,40,'#e6eaf3',10); poly([[-18,48],[0,16],[18,48]],C.tile); fe(-60,-26,34,12,'rgba(255,255,255,.6)',-.2); ctx.restore(); }
function s6Scatola(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-90,-60,180,120,10,'#fff'); box(-90,-60,180,30,0,C.ciano); box(-90,-60,180,120,10,'rgba(0,0,0,0)');
  for(let i=0;i<4;i++) fe(-54+i*36,20,13,20,'#cfd6e8'); ctx.restore(); }
function s6Cane(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); const c='#c99a5b', d='#9c7240';
  ln([[-70,-10],[-110,-50]],c,18); [[-60,0],[-30,0],[40,0],[66,0]].forEach(([a],i)=>ln([[a,10],[a+(i%2?4:-4),80]],i%2?d:c,20));
  fe(0,0,90,44,c); fe(96,-56,44,38,c); fe(132,-46,26,20,'#d8ad72'); fc(150,-52,8,'#1a1f36'); fe(80,-80,16,30,d,.3); fc(100,-64,6,'#1a1f36'); ctx.restore(); }
// calendario: griglia di giorni senza numeri
function s6Calendario(x,y,s,sel,cerchio){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-190,-170,380,340,24,'#fff'); box(-190,-170,380,70,24,C.ciano); box(-190,-130,380,30,0,C.ciano);
  for(let i=0;i<2;i++){ box(-110+i*190,-196,24,56,12,'#cfd6e8'); }
  for(let r=0;r<4;r++) for(let c=0;c<6;c++){ const n=r*6+c; box(-170+c*58,-80+r*58,46,46,8,n===sel?'#fdf6b0':'#e3e7f1'); }
  if(cerchio>0){ const c=sel%6, r=Math.floor(sel/6); ctx.save(); ctx.translate(-147+c*58,-57+r*58); ctx.strokeStyle=RED; ctx.lineWidth=7; ctx.lineCap='round'; ctx.beginPath(); ctx.ellipse(0,0,38,34,-.2,-1.9,-1.9+TAU*1.08*clamp(cerchio)); ctx.stroke(); ctx.restore(); }
  ctx.restore(); }
function s6Spilla(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.fillStyle=RED; ctx.beginPath(); ctx.arc(0,-40,40,Math.PI*.8,Math.PI*.2); ctx.lineTo(0,30); ctx.closePath(); ctx.fill(); fc(0,-40,15,'#fff'); ctx.restore(); }
// rubinetto e getto verticale fino a yEnd, sopra il punto x
function s6Getto(x,y0,yEnd,u){ ctx.strokeStyle='#cfd6e8'; ctx.lineWidth=30; ctx.lineCap='round'; ctx.beginPath(); ctx.moveTo(x+150,y0); ctx.lineTo(x+50,y0); ctx.quadraticCurveTo(x,y0,x,y0+40); ctx.stroke(); box(x+70,y0-42,60,26,8,'#cfd6e8');
  for(let i=0;i<10;i++){ const yy=y0+52+((u*380+i*36)%(yEnd-y0-52)); fe(x+((i%3)-1)*6,yy,6,13,C.ciano); } }
// mani che si lavano con il sapone
function s6Lavamani(x,y,s,u){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); const k=Math.sin(u*6)*10;
  hand(-30+k,40,.62,.55); hand(30-k,40,.62,-.55,SK,true);
  for(let i=0;i<7;i++){ const f=(u*.7+i/7)%1; const bx=-70+hash(i)*140, by=-20-f*120; ctx.globalAlpha=1-f; arc(bx,by,10+hash(i+5)*12,0,TAU,'#fff',3); ctx.globalAlpha=1; }
  for(let i=0;i<6;i++){ const f=(u*1.5+i/6)%1; fe(-40+i*16,-170+f*90,5,11,`rgba(0,165,220,${1-f})`); } ctx.restore(); }
// bocca vista di fronte: ap 1 = aperta, 0 = chiusa sul rotolo; manca un dente in alto
function s6Bocca(x,y,s,ap,garza){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  const h=lerp(46,110,ap);
  fe(0,0,250,h+64,'#c9575a'); fe(0,0,210,h+20,'#6b2232');
  ctx.save(); ctx.beginPath(); ctx.ellipse(0,0,210,h+20,0,0,TAU); ctx.clip();
  box(-230,-h-60,460,44,0,'#d98a8a'); box(-230,h+16,460,44,0,'#d98a8a');
  for(let i=0;i<6;i++){ if(i===3) continue; const xx=-150+i*60; box(xx-26,-h-20,52,80-Math.abs(i-2.5)*8,12,S6_DENTE); }
  fe(30,-h-14,24,12,RED);
  for(let i=0;i<6;i++){ const xx=-150+i*60; box(xx-24,h-50+Math.abs(i-2.5)*8,48,70,12,S6_DENTE); }
  if(garza>0){ ctx.save(); ctx.globalAlpha*=clamp(garza); const gy=lerp(-h-150,-h+30,clamp(garza)); box(-12,gy-18,84,lerp(60,h*2-34,clamp(garza))*.6+20,16,'#fff'); ln([[0,gy],[60,gy]],'rgba(27,34,63,.12)',3); ctx.restore(); }
  ctx.restore();
  ctx.strokeStyle='#b14a4e'; ctx.lineWidth=6; ctx.beginPath(); ctx.ellipse(0,0,250,h+64,0,0,TAU); ctx.stroke(); ctx.restore(); }

Object.assign(ILL, {
// ---------- Ferite e tagli ----------
ferita({u,p}){
  ctx.save(); ctx.translate(-20,0); ctx.rotate(-.12);
  box(-90,-260,180,560,90,SK); box(-90,140,180,160,0,SK); fe(0,-170,56,70,'#f6dccb');               // dito e unghia
  ln([[-50,-10],[-34,4],[-16,-6],[4,8],[24,-4],[44,8]],RED,9);                                          // il taglietto
  const c=clamp((p-.4)/.3); if(c<1){ const f=(u*1.2)%1; drop(30,40+f*50,.35,`rgba(217,71,61,${(1-f)*(1-c)})`); }
  if(c>0){ ctx.save(); ctx.translate(lerp(520,0,inOut(c)),0); ctx.rotate(lerp(.6,0,c)); s6Cerotto(0,0,250,96,0); ctx.restore(); }
  ctx.restore();
  if(p>.75) spunta(260,-150,56,outBack(clamp((p-.75)/.15)));
},
disinfetta({u,A}){
  grp(-250,-20,1,A(.3),()=>{ fc(0,0,170,C.tile); bottle(0,40,1,'#e3e7f1','#fff'); s6Tx('senza',0,55,26,C.navy,'800'); s6Tx('alcol',0,85,26,C.navy,'800'); spunta(110,-120,46,A(.38)); });
  grp(130,-110,1,A(.5),()=>{ fc(0,0,120,C.tile); s6Alcol(0,10,.75); vieto(0,0,110,A(.56)); });
  grp(300,130,1,A(.75),()=>{ fc(0,0,110,C.tile); s6Cotone(-10,0,1); vieto(0,0,100,A(.81)); });
},
cerotto({u,p,A}){
  forearm(110);
  const fx=40, fy=96; fe(fx,fy,46,16,'#e58f86'); ln([[fx-34,fy],[fx+34,fy]],RED,6);
  const a=A(.25), b=A(.55);
  if(a>0 && b<.3){ const t=u*3; const gx=fx+Math.cos(t)*95, gy=fy+Math.sin(t)*36; grp(gx,gy-10,.8,a,()=>{ gauze(0,0,80,70); }); }
  if(b>0){ ctx.save(); ctx.globalAlpha*=clamp(b); const yy=lerp(fy-200,fy,clamp(b)); s6Cerotto(fx,yy,230,90,0); ctx.restore(); }
  grp(300,-170,1,A(.85),()=>{ fc(0,0,105,C.tile); s6Cerotto(-40,0,90,40,-.5,{sporco:true}); fc(-40,-36,9,C.ciano); drop(-40,-40,.3,C.ciano);
    arrow(-6,0,26,0,C.giallo,7); s6Cerotto(56,0,90,40,-.5);
    arc(0,0,90,-2.6,-.6,'rgba(242,228,51,.8)',6); arc(0,0,90,.5,2.5,'rgba(242,228,51,.8)',6); });
},
antitetanica({u,p,D,A}){
  grp(-300,-130,1,A(.25),()=>{ fc(0,0,120,C.tile); ctx.save(); ctx.beginPath(); ctx.arc(0,0,120,0,TAU); ctx.clip(); box(-130,-130,260,260,0,SK); ctx.restore();
    ln([[-60,10],[-20,24],[20,6],[60,22]],RED,12); [[-40,-6],[10,40],[44,-4],[-10,46],[70,40]].forEach(([a,b])=>fc(a,b,7,'#6b4a2e')); });
  grp(-40,40,1,A(.45),()=>{ box(-170,-180,340,330,18,'#fff'); ln([[0,-180],[0,150]],'#cfd6e8',4); box(-170,-180,340,40,18,C.ciano); box(-170,-150,340,10,0,C.ciano);
    for(let i=0;i<5;i++){ box(-150,-110+i*48,120,12,6,'#cfd6e8'); box(20,-110+i*48,130-(i%2)*30,12,6,'#cfd6e8'); }
    const h=A(.6); if(h>0){ ctx.save(); ctx.globalAlpha*=clamp(h); box(12,-2+48*0,146,40,8,'rgba(242,228,51,.55)'); ctx.restore(); box(20,10,130,12,6,'#aab3cc'); }
    const q=A(.85); if(q>0) grp(85,16,1,q,()=>{ fc(0,0,46,C.giallo); s6Tx('?',0,3,58,C.navy,'800'); }); });
  const c=A(.6); if(c>0){ const n=Math.floor(clamp((u-PRE-.6*D)/1.4)*5); grp(310,-120,1,c,()=>{ timer(0,0,110,n/5,String(Math.max(1,n)),{sub:'anni',size:62}); }); }
},
'ferita-infetta'({u,p,A}){
  forearm(100);
  const fx=40, fy=86, a=A(.25);
  if(a>0){ const pul=1+Math.sin(u*4)*.06; fe(fx,fy,(80+70*clamp(a))*pul,(36+26*clamp(a))*pul,'rgba(217,71,61,.45)'); fe(fx,fy,60*pul,26*pul,'rgba(217,71,61,.5)');
    for(let i=0;i<3;i++){ const f=(u*.8+i/3)%1; ctx.save(); ctx.globalAlpha*=clamp(a)*(1-f); ctx.strokeStyle='#f2a541'; ctx.lineWidth=6; ctx.beginPath(); const xx=fx-60+i*60, yy=fy-60-f*80; ctx.moveTo(xx,yy); ctx.quadraticCurveTo(xx+14,yy-16,xx,yy-32); ctx.quadraticCurveTo(xx-14,yy-48,xx,yy-64); ctx.stroke(); ctx.restore(); } }
  ln([[fx-36,fy],[fx+36,fy]],'#a8322b',7);
  const pu=A(.55); if(pu>0) fe(fx,fy,22*clamp(pu),10*clamp(pu),'#e8d36a');
  grp(330,-150,1,A(.8),()=>{ fc(0,0,120,C.tile); s6Termo(0,-10,.7,.35+.5*clamp(A(.8))); });
},
// ---------- Dente caduto o rotto ----------
dente({u}){
  const r=Math.sin(u*1.4)*.35, b=Math.sin(u*2)*14; s6Dente(0,-40+b,1.15,r);
  const f=(u*.9)%1; ctx.save(); ctx.globalAlpha*=Math.sin(f*Math.PI); ctx.translate(-70,40+b); ctx.rotate(f); ctx.fillStyle='#fff'; ctx.beginPath();
  for(let j=0;j<8;j++){ const rr2=j%2?8:30,a=j*Math.PI/4; ctx.lineTo(Math.cos(a)*rr2,Math.sin(a)*rr2); } ctx.closePath(); ctx.fill(); ctx.restore();
  ctx.save(); ctx.globalAlpha*=.35; fe(0,250,140,14,'#000'); ctx.restore();
},
'dente-garza'({u,p,A}){
  const g=A(.25), m=A(.5); s6Bocca(-90,-10,.95,1-.75*clamp(m),g);
  grp(300,-160,1,A(.85),()=>{ fc(0,0,115,C.tile); head(0,-6,62,{mouth:'o',hairCol:'#8a6a4a'}); box(-10,30,46,22,8,'#fff'); vieto(0,0,104,A(.9)); });
},
'denti-latte'({u,A}){
  s6Dente(-260,-70,.55,0,{L:60}); s6Dente(60,-30,.95,0);
  const a=A(.35); if(a>0){ ctx.save(); ctx.globalAlpha*=clamp(a); arrow(-270,40,-270,120,C.giallo,10); ctx.restore(); grp(-270,190,1,a,()=>s6Dentista(0,0,80)); }
  grp(300,-30,1,A(.85),()=>s6Crono(0,0,100,u*3));
},
'dente-corona'({u,p,A}){
  const tx0=-150, ty0=-60;
  s6Dente(tx0,ty0,1.05,0);
  const a=A(.3); if(a>0){ const k=clamp(a); const d=(1-k)*140;   // pollice e indice della stessa mano stringono la corona
    ctx.save(); ctx.globalAlpha*=k; ctx.translate(d,d*.6);
    s6Dito(tx0+150,ty0+250,tx0-70,ty0+104,44);
    box(tx0+90,ty0+200,170,130,56,SK); s6Dito(tx0+180,ty0+220,tx0+72,ty0+96,44);
    ln([[tx0+210,ty0+300],[tx0+300,ty0+330]],SK,90); ctx.restore(); }
  const r=A(.6); if(r>0){ ctx.save(); ctx.globalAlpha*=clamp(r); ctx.setLineDash([12,10]); ctx.strokeStyle=C.giallo; ctx.lineWidth=6; rr(ctx,tx0-70,ty0-216,140,236,50); ctx.stroke(); ctx.restore();
    const w=Math.sin(u*3)*14; s6Dito(tx0+330,ty0-160+w,tx0+120,ty0-110+w,42); vieto(tx0+190,ty0-120,74,r); }
  grp(310,150,1,A(.85),()=>{ fc(0,0,96,C.tile); s6Dente(0,-10,.42,0); const k=Math.sin(u*9)*22; box(-44+k,-4,88,30,10,'#e3e7f1'); vieto(0,0,86,A(.9)); });
},
'dente-latte'({u,p,A}){
  const a=A(.25);
  grp(-280,40,1,1,()=>{ fc(0,-40,170,C.tile);
    const dy=lerp(-330,-20,clamp(a)); const lv=-10; // livello del latte (coordinate locali del bicchiere 1.25)
    ctx.save(); ctx.beginPath(); ctx.rect(-200,-400,400,400+lv); ctx.clip(); s6Dente(0,dy,.42,.3); ctx.restore();
    glass(0,40,1.25,.62,'rgba(246,243,234,.9)');
    ctx.save(); ctx.beginPath(); ctx.rect(-200,lv,400,300); ctx.clip(); ctx.globalAlpha*=.35; s6Dente(0,dy,.42,.3); ctx.restore(); });
  grp(30,-90,1,A(.5),()=>{ fc(0,0,120,C.tile); s6Fiala(-34,10,.78,-.12); s6Fiala(36,4,.78,.1); });
  grp(300,60,1,A(.8),()=>{ fc(0,0,120,C.tile); glass(0,8,.75,.7,S6_ACQUA); vieto(0,0,110,A(.86)); });
},
'dente-saliva'({u,p,A}){
  const a=A(.3);
  grp(-200,20,1,1,()=>{ fc(0,0,170,C.tile);
    box(-110,-30,220,130,30,'rgba(255,255,255,.35)'); sbox(-110,-30,220,130,30,'#fff',7); box(-122,-58,244,32,12,'#cfd6e8');
    ctx.save(); ctx.beginPath(); ctx.rect(-110,40,220,60); ctx.clip(); box(-104,46,208,50,22,'rgba(223,238,248,.85)'); for(let i=0;i<5;i++) arc(-70+i*35,62+(i%2)*10,6,0,TAU,'#fff',2); ctx.restore();
    if(a>0){ const dy=lerp(-260,36,clamp(a)); s6Dente(0,dy,.3,1.35); } });
  grp(230,-30,1,A(.75),()=>{ fc(0,0,150,C.tile); head(0,0,90,{mouth:'o',hairCol:'#8a6a4a'}); s6Dente(0,40,.14,1.57); vieto(0,0,140,A(.8)); });
},
'dente-rotto'({u,p,A}){
  s6Dente(-300,-90,1,0,{rotto:true});
  const a=A(.3), b=A(.55);
  const fx0=-130, fy0=180, gx=60, gy=-40;
  if(b<=0){ s6Scheggia(fx0,fy0-100*.8,.8,.6);
    if(a>0) grp(fx0+10+Math.sin(u*2)*30,fy0-20,1,a,()=>{ arc(0,0,58,0,TAU,'#fff',12); ln([[40,40],[96,96]],'#fff',18); }); }
  else { const k=clamp(b); const x=lerp(fx0,gx,k), y=lerp(fy0-80,gy-60,k)-Math.sin(k*Math.PI)*160; if(k<1) s6Scheggia(x-28*k,y-20+8*k,.8,(.6+k*2)*(1-k)); else { ctx.save(); ctx.globalAlpha*=.6; s6Scheggia(gx-28,-12,.8,0); ctx.restore(); } }
  glass(gx,40,1,.6,'rgba(246,243,234,.82)');
  grp(320,-10,1,A(.85),()=>{ s6Dentista(0,0,110); });
  const c=A(.85); if(c>0){ ctx.save(); ctx.globalAlpha*=clamp(c); arrow(140,-10,180,-10,C.giallo,10); ctx.restore(); }
},
// ---------- Sostanze chimiche negli occhi ----------
'occhio-chimico'({u}){
  s6Flacone(-250,30,1.15);
  eye(250,-10,1.25,1);
  const f=(u*.7)%1; for(let i=0;i<6;i++){ const g=clamp(f*1.3-i*.05); if(g<=0||g>=1) continue; const x=lerp(-215,165,g), y=lerp(-120,-10,g)-Math.sin(g*Math.PI)*90;
    fc(x,y,13-i*1.4,`rgba(127,214,90,${1-g*.4})`); }
  if(f>.72){ const r=(f-.72)/.28; arc(250,-10,90+r*70,0,TAU,`rgba(242,228,51,${1-r})`,8); }
},
'occhi-timer'({u,p,A}){
  const hx=-110, hy=50, R=190, th=.42;
  // testa inclinata: l'occhio colpito (a destra) sta più in basso
  ctx.save(); ctx.translate(hx,hy); ctx.rotate(th); head(0,0,R,{mouth:'flat'}); fe(R*.36,R*.08,R*.17,R*.13,'#fff'); fc(R*.36,R*.08,R*.09,'#5b8fb9'); fc(R*.36,R*.08,R*.045,'#0d1226'); ctx.restore();
  const P=(lx,ly)=>[hx+lx*Math.cos(th)-ly*Math.sin(th), hy+lx*Math.sin(th)+ly*Math.cos(th)];
  const inn=P(R*.2,R*.04), out=P(R*.56,R*.06), edge=P(R*1.02,R*.2);
  s6Getto(inn[0],-262,inn[1],u);
  for(let i=0;i<10;i++){ const f=(u*1.3+i/10)%1; let x,y; if(f<.5){ const g=f/.5; x=lerp(inn[0],out[0],g); y=lerp(inn[1],out[1],g)+4; } else { const g=(f-.5)/.5; x=lerp(out[0],edge[0],g)+g*20; y=lerp(out[1],edge[1],g)+g*g*120; }
    fe(x,y,7,10,`rgba(0,165,220,${f<.8?.85:(1-f)*4})`); }
  const s=A(.8); if(s>0){ const oe=P(-R*.36,R*.08); ctx.save(); ctx.globalAlpha*=clamp(s); arc(oe[0],oe[1],46,0,TAU,C.giallo,7); ctx.restore(); spunta(oe[0]-70,oe[1]-80,36,s); }
  grp(310,-130,1,A(.35),()=>timer(0,0,110,p,Math.min(15,Math.floor(p*15)+1)+'′',{sub:'minuti',size:58}));
},
lenti({u,p,A}){
  eye(-80,20,1.5,1);
  for(let i=0;i<10;i++){ const f=(u*1.4+i/10)%1; fe(-200+(i%3)*8,-230+f*200,6,13,`rgba(0,165,220,${1-f*.5})`); }
  const a=A(.5), k=clamp(a);
  const lx=-80+k*230, ly=20+k*150;
  ctx.save(); ctx.globalAlpha*=.9; arc(lx,ly,74,Math.PI*1.08,Math.PI*1.92,'rgba(159,216,240,.95)',8); fe(lx,ly-6,70,62,'rgba(159,216,240,.28)'); ctx.restore();
  if(a>0){ const w=Math.sin(u*2)*6; s6Dito(lx+260,ly+260+w,lx+40,ly+52+w,58); }
},
'no-collirio'({u,A}){
  grp(-300,-20,1,A(.3),()=>{ fc(0,0,130,C.tile); s6Collirio(0,10,1); vieto(0,0,120,A(.36)); });
  grp(0,-20,1,A(.45),()=>{ fc(0,0,130,C.tile); bottle(0,20,.7,'#e0b84a','#fff'); vieto(0,0,120,A(.5)); });
  grp(300,-20,1,A(.7),()=>{ fc(0,0,130,C.tile); drop(0,10,2.2,C.ciano); fe(-18,-10,10,22,'rgba(255,255,255,.5)',-.3); spunta(80,-90,40,A(.76)); });
},
protezioni({u,A}){
  grp(-300,-140,1,A(.2),()=>{ fc(0,0,120,C.tile); s6Guanto(0,20,.48,-.15); });
  grp(-300,140,1,A(.35),()=>{ fc(0,0,120,C.tile); s6Occhiali(0,0,.58); });
  grp(170,0,1,A(.7),()=>{
    box(-40,-110,340,22,8,'#cfd6e8'); ln([[250,-88],[290,-50]],'#aab3cc',10);       // mensola in alto, il flacone chiuso sopra
    s6Flacone(130,-200,.55);
    ctx.save(); ctx.translate(30,190); stick(0,-40,1.15,{shirt:'#f2a541',legs:80}); ctx.restore(); });
},
// ---------- Zecche ----------
zecca({u}){
  const z=1+Math.min(u,8)*.025; ctx.save(); ctx.scale(z,z);
  const fili=[[-340,.18],[-250,-.1],[-140,.06],[-40,-.04],[90,.12],[200,-.08],[310,.1],[390,-.14]];
  fili.forEach(([x,c],i)=>{ const sw=Math.sin(u*1.3+i)*10; ctx.fillStyle=i%2?S6_ERBA:S6_ERBA2; ctx.beginPath(); ctx.moveTo(x-16,260); ctx.quadraticCurveTo(x+c*300,40,x+c*500+sw,-240-hash(i)*60); ctx.quadraticCurveTo(x+c*300+10,40,x+16,260); ctx.fill(); });
  // la zecca sale lungo il quarto filo (x=-40): punto e direzione della curva del filo
  const x0=-40, c0=-.04, sw=Math.sin(u*1.3+3)*10, top=-240-hash(3)*60, t=lerp(.08,.72,clamp(u/8));
  const B=(q,a,b,d)=>(1-q)*(1-q)*a+2*(1-q)*q*b+q*q*d;
  const bx=B(t,x0,x0+c0*300,x0+c0*500+sw), by=B(t,260,40,top), bx2=B(t+.01,x0,x0+c0*300,x0+c0*500+sw), by2=B(t+.01,260,40,top);
  s6Zecca(bx,by,.62,Math.atan2(by2-by,bx2-bx)-Math.PI/2,{cammina:u*8});
  ctx.restore();
},
'zecca-vestiti'({u,A}){
  ctx.save(); ctx.translate(-210,0);
  ln([[-30,40],[-36,230]],'#e6dcc8',58); ln([[30,40],[36,230]],'#e6dcc8',58); box(-74,226,64,26,12,'#6b4a2e'); box(10,226,64,26,12,'#6b4a2e');
  box(-80,-110,160,170,46,'#f3f5f9'); ln([[-70,-90],[-110,30]],'#f3f5f9',38); ln([[70,-90],[110,30]],'#f3f5f9',38); fc(-112,40,18,SK); fc(112,40,18,SK);
  box(-18,-140,36,36,8,SKD); head(0,-200,62,{});
  const a=A(.2); if(a>0){ ctx.save(); ctx.globalAlpha*=clamp(a); ctx.setLineDash([12,10]); ctx.strokeStyle=C.giallo; ctx.lineWidth=5; rr(ctx,-128,-122,256,196,40); ctx.stroke(); ctx.restore(); }
  const b=A(.4); if(b>0){ ctx.save(); ctx.globalAlpha*=clamp(b); ctx.setLineDash([12,10]); ctx.strokeStyle=C.giallo; ctx.lineWidth=5; rr(ctx,-78,30,156,234,30); ctx.stroke(); ctx.restore(); }
  ctx.restore();
  grp(30,60,1,A(.65),()=>{ box(-36,-60,72,150,22,'#7cc46a'); box(-22,-96,44,40,8,'#7cc46a'); box(-40,-120,70,30,10,'#fff'); box(-70,-118,34,14,6,'#fff');
    for(let i=0;i<8;i++){ const f=(u*1.2+i/8)%1; fc(-80-f*120,-110+f*90+Math.sin(i*2)*20,6+f*14,`rgba(255,255,255,${(1-f)*.6})`); } });
  grp(300,-30,1,A(.9),()=>{ fc(0,0,140,C.tile); ctx.save(); ctx.beginPath(); ctx.arc(0,0,140,0,TAU); ctx.clip();
    for(let i=0;i<9;i++){ const x=-120+i*30, sw=Math.sin(u*1.5+i)*8; ctx.fillStyle=i%2?S6_ERBA:S6_ERBA2; ctx.beginPath(); ctx.moveTo(x-10,150); ctx.quadraticCurveTo(x,0,x+sw,-110+hash(i)*30); ctx.quadraticCurveTo(x+6,0,x+10,150); ctx.fill(); } ctx.restore();
    vieto(0,0,128,A(.95)); });
},
'zecca-controllo'({u,A}){
  ctx.save(); ctx.translate(-240,0); const c='#cfd6e8';
  fc(0,-230,52,c); box(-20,-186,40,30,8,c); box(-70,-160,140,200,40,c); ln([[-62,-140],[-100,20]],c,34); ln([[62,-140],[100,20]],c,34);
  ln([[-30,30],[-36,240]],c,52); ln([[30,30],[36,240]],c,52);
  const pts=[[0,-232,.2],[0,-170,.28],[-34,150,.45],[34,150,.47],[-72,-10,.55],[72,-10,.57]];
  pts.forEach(([x,y,t])=>{ const a=A(t); if(a<=0) return; const pul=1+Math.sin(u*5)*.15; fc(x,y,24*pul*clamp(a),'rgba(242,228,51,.45)'); fc(x,y,11*clamp(a),C.giallo); });
  ctx.restore();
  grp(90,-120,1,A(.7),()=>{ const w=Math.sin(u*10)*.25; ctx.save(); ctx.rotate(w); box(-80,-50,160,130,24,'#f3f5f9'); ln([[-70,-40],[-110,30]],'#f3f5f9',34); ln([[70,-40],[110,30]],'#f3f5f9',34); ctx.restore();
    arc(-130,0,40,-.6,.6,C.giallo,6); arc(130,0,40,Math.PI-.6,Math.PI+.6,C.giallo,6); for(let i=0;i<4;i++){ const f=(u*1.2+i/4)%1; fc(-40+i*26,90+f*90,4,`rgba(255,255,255,${1-f})`); } });
  grp(250,150,1,A(.9),()=>{ s6Cane(-30,10,.85); arc(80,-30,46,0,TAU,'#fff',9); ln([[112,2],[150,40]],'#fff',13); });
},
'zecca-pinzetta'({u,p,A}){
  const y0=60;
  s6Zecca(-20,y0-62,1.15,0);
  s6Pelle(y0); box(-36,y0,32,14,4,SK);
  grp(-330,-170,1,A(.2),()=>s6Crono(0,0,72,u*3));
  const a=A(.5), b=A(.85);
  if(a>0){ const k=clamp(a), g=clamp(b); const tx0=lerp(330,-20,k*.75+g*.25), ty0=lerp(-220,y0+6,k*.6+g*.4);
    ctx.save(); ctx.globalAlpha*=k; s6Pinzetta(tx0,ty0,.95,lerp(16,0,g),1); ctx.restore(); }
  if(b>0){ ctx.save(); ctx.globalAlpha*=clamp(b); arc(-20,y0+4,40,0,TAU,C.giallo,6); ctx.restore(); }
},
'zecca-tira'({u,p,A}){
  const y0=100; const k=clamp((p-.15)/.6); const up=inOut(k)*170;
  const tent=k<.45? Math.sin(k/.45*Math.PI*.5)*20 : 0;
  s6Pelle(y0); if(tent>0){ fe(-20,y0,40,tent,SK); }
  s6Zecca(-20,y0-62-up-tent,1.15,0);
  s6Pinzetta(-20,y0+6-up-tent,.95,0,1);
  const a=A(.35); if(a>0){ ctx.save(); ctx.globalAlpha*=clamp(a); const f=(u*.5)%1; arrow(-175,y0-40-f*40,-175,y0-200-f*40,C.giallo,10); ctx.restore(); }
  grp(-330,-140,1,A(.8),()=>{ fc(0,0,110,C.tile); s6Zecca(0,20,.8,0,{sx:1.35,sy:.7}); s6Pinzetta(0,4,Math.PI/2,0,.4); vieto(0,0,100,A(.86)); });
},
'zecca-no'({u,A}){
  const it=[[-330,.15,()=>s6Alcol(0,10,.7)],[-110,.35,()=>s6Olio(0,10,.8)],[110,.55,()=>s6Tanica(0,20,.75)],[330,.85,()=>s6Fiammifero(0,40,.85,u)]];
  it.forEach(([x,t,f])=>grp(x,-70,1,A(t),()=>{ fc(0,0,100,C.tile); f(); vieto(0,0,92,A(t+.06)); }));
  ctx.save(); ctx.beginPath(); ctx.arc(0,170,90,0,TAU); ctx.clip(); fc(0,170,90,SK); ctx.restore(); s6Zecca(0,150,.5,0); arc(0,170,90,0,TAU,'rgba(255,255,255,.4)',4);
},
'zecca-dopo'({u,A}){
  grp(-250,-130,1,A(.2),()=>{ box(-170,-120,340,240,40,C.tile); s6Lavamani(0,-6,1.05,u); });
  grp(130,-150,1,A(.5),()=>{ fc(0,0,100,C.tile); ctx.save(); ctx.globalAlpha*=.9; box(-38,-40,76,110,18,'rgba(255,255,255,.35)'); box(-32,0,64,64,14,'rgba(223,238,248,.6)'); box(-16,-72,32,34,6,'rgba(255,255,255,.5)'); box(-20,-88,40,18,6,'#fff'); ctx.restore(); spunta(70,-70,34,A(.56)); });
  grp(340,-150,1,A(.55),()=>{ fc(0,0,90,C.tile); box(-30,-20,60,80,14,'#7a3412'); box(-12,-48,24,30,6,'#5a2a10'); box(-20,-62,40,16,6,'#3a1a08'); vieto(0,0,82,A(.6)); });
  grp(220,140,1,A(.85),()=>{ box(-200,-90,400,180,40,C.tile); ctx.save(); ctx.beginPath(); ctx.arc(-100,0,70,0,TAU); ctx.clip(); fc(-100,0,70,SK); ctx.restore(); fc(-100,0,7,S6_ZECCAD); arc(-100,0,26,0,TAU,C.giallo,5);
    arrow(-14,0,30,0,C.giallo,8); ctx.save(); ctx.translate(110,0); ctx.scale(.55,.55); cross(0,0,1,RED); ctx.restore(); steto(150,-10,.3); });
},
calendario({u,D,A}){
  const c=A(.35); s6Calendario(-130,30,1.05,9,c>0?clamp((u-PRE-.35*D+.1)/1):0);
  grp(-130+(-147+3*58)*1.05+70,30+(-57+58)*1.05-60,1,c,()=>s6Spilla(0,0,.7));
  grp(300,-80,1,A(.8),()=>{ fc(0,0,130,C.tile); const bl=(u%3)<.12; eye(0,0,.85,1); if(bl){ box(-100,-60,200,120,50,SK); ln([[-90,0],[90,0]],C.navy,8); } });
},
'zecca-alone'({u,A}){
  const a=A(.2);
  ctx.save(); ctx.beginPath(); ctx.arc(-200,0,200,0,TAU); ctx.clip(); fc(-200,0,200,SK);
  if(a>0){ const g=clamp(a)*(.6+.4*clamp((u-PRE)/4)); const R=60+120*g; ctx.lineWidth=R*.32; ctx.strokeStyle='rgba(217,71,61,.55)'; ctx.beginPath(); ctx.arc(-200,0,R*.82,0,TAU); ctx.stroke(); fc(-200,0,R*.32,'rgba(217,71,61,.35)'); }
  fc(-200,0,8,'#8a2a1a'); ctx.restore(); arc(-200,0,200,0,TAU,'rgba(255,255,255,.35)',5);
  grp(140,-150,1,A(.4),()=>{ fc(0,0,100,C.tile); s6Termo(0,-6,.55,.75); });
  grp(350,-150,1,A(.6),()=>{ fc(0,0,100,C.tile); ln([[-70,-30],[0,10]],PANT,40); ln([[0,10],[-24,80]],SK,30); fe(-36,88,24,12,'#1a1f36'); fc(4,8,22,SK);
    for(let i=0;i<3;i++){ const ang=-1.2+i*.9; const f=(Math.sin(u*6)+1)/2; ln([[Math.cos(ang)*(30+f*6),10+Math.sin(ang)*(30+f*6)],[Math.cos(ang)*(56+f*6),10+Math.sin(ang)*(56+f*6)]],C.giallo,7); } });
  grp(250,120,1,A(.9),()=>{ fc(0,0,115,C.tile); s6Scatola(0,0,.85); vieto(0,0,106,A(.95)); });
},
});
