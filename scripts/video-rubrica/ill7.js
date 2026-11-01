// ===== Disegni della 3ª serie: morso di vipera, colpo di calore, annegamento =====
// Aiuti e costanti con il prefisso s7 (tutti gli ill*.js finiscono in un solo script: niente nomi doppi).
const S7_VIP='#a68d62', S7_VIPD='#4b3b28', S7_SASSO='#8f96a8', S7_SASSOD='#6b7288', S7_ERBA='#4f9a5a',
  S7_ACQUA='#1d86c9', S7_ACQUAL='#7fd0f0', S7_SABBIA='#e9d3a8', S7_LEGNO='#8a5a3a', S7_PANNO='#bfe6f5';

// vipera vista dall'alto, testa a destra; (x,y) = centro, s = scala, u = tempo
function s7Vipera(x,y,s,u){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  const N=64, P=[]; for(let i=0;i<=N;i++){ const t=i/N; P.push([-300+t*560, Math.sin(t*TAU*1.5-u*3.2)*58*Math.pow(Math.sin(Math.PI*Math.min(1,t*1.05)),.7)]); }
  const W=t=>8+38*Math.sin(Math.PI*clamp(t*.86+.03));
  for(const pass of [0,1]) for(let i=0;i<N;i++){ const t=i/N; ln([P[i],P[i+1]],pass?S7_VIP:S7_VIPD,W(t)*2+(pass?0:8)); }
  const Z=[]; for(let i=2;i<N-2;i++){ const a=Math.atan2(P[i+1][1]-P[i-1][1],P[i+1][0]-P[i-1][0]), o=(i%2?1:-1)*W(i/N)*.45; Z.push([P[i][0]-Math.sin(a)*o,P[i][1]+Math.cos(a)*o]); }
  ln(Z,S7_VIPD,9);
  const [hx,hy]=P[N], a=Math.atan2(P[N][1]-P[N-3][1],P[N][0]-P[N-3][0]);
  ctx.save(); ctx.translate(hx,hy); ctx.rotate(a);
  const testa=()=>{ ctx.beginPath(); ctx.moveTo(-14,-24); ctx.quadraticCurveTo(30,-56,70,-30); ctx.quadraticCurveTo(100,-12,104,0); ctx.quadraticCurveTo(100,12,70,30); ctx.quadraticCurveTo(30,56,-14,24); ctx.closePath(); };
  ctx.fillStyle=S7_VIPD; ctx.save(); ctx.scale(1.08,1.12); testa(); ctx.fill(); ctx.restore(); ctx.fillStyle=S7_VIP; testa(); ctx.fill();
  ln([[8,-16],[52,0],[8,16]],S7_VIPD,8);                              // segno a V sulla testa
  [-1,1].forEach(sd=>{ fe(62,sd*27,13,10,'#e8a73a'); fe(62,sd*27,2.6,8,'#0d1226'); });   // occhi con la pupilla verticale
  const fl=(u*1.3)%1; if(fl<.25){ const e=Math.sin(fl/.25*Math.PI)*34; ln([[102,0],[102+e,0]],'#c0392b',4); ln([[102+e,0],[110+e,-8]],'#c0392b',3); ln([[102+e,0],[110+e,8]],'#c0392b',3); }
  ctx.restore(); ctx.restore(); }
function s7Sasso(x,y,rx,ry){ fe(x,y,rx,ry,S7_SASSOD); fe(x-rx*.12,y-ry*.18,rx*.86,ry*.78,S7_SASSO); fe(x-rx*.35,y-ry*.4,rx*.25,ry*.15,'rgba(255,255,255,.25)'); }
function s7Ciuffo(x,y,s){ for(let i=-2;i<=2;i++) ln([[x+i*6*s,y],[x+i*14*s,y-(36-Math.abs(i)*7)*s]],S7_ERBA,6*s); }
// flaconcino di vetro con il tappo
function s7Flacone(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-34,-60,68,110,14,'rgba(223,243,251,.9)'); box(-34,-10,68,60,12,'#9fd8f0');
  box(-20,-84,40,28,6,'#aab3cc'); box(-26,-30,52,30,4,'#fff'); ctx.restore(); }
// zaino da escursione
function s7Zaino(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); arc(0,-110,40,Math.PI,0,'#2b5a46',14);
  box(-95,-110,190,240,50,'#3a8d6c'); box(-70,10,140,100,26,'#2f7559'); ln([[-60,30],[60,30]],'#24604a',6); box(-95,-110,190,70,40,'#2f7559'); ctx.restore(); }
// tondo scuro con il disegno ritagliato dentro
function s7Tondo(r,fn){ fc(0,0,r,C.tile); ctx.save(); ctx.beginPath(); ctx.arc(0,0,r-4,0,TAU); ctx.clip(); fn(); ctx.restore(); }
// figurina che cammina
function s7Cammina(x,y,s,u){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); const a=Math.sin(u*6)*.5;
  ln([[0,60],[Math.sin(a)*68,60+Math.cos(a)*68]],PANT,20); ln([[0,60],[-Math.sin(a)*68,60+Math.cos(a)*68]],'#262f5a',20);
  ln([[0,-20],[0,60]],VS,40); ln([[0,-8],[-Math.sin(a)*50,-8+Math.cos(a)*50]],VSD,16); ln([[0,-8],[Math.sin(a)*50,-8+Math.cos(a)*50]],VS,16);
  fc(0,-62,26,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(0,-62,27,Math.PI,0); ctx.fill(); ctx.restore(); }
// figurina seduta (di profilo, rivolta a destra): (x,y) = seduta
function s7Seduto(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  ln([[0,0],[50,0],[54,62]],PANT,20); ln([[0,0],[0,-80]],VS,38); ln([[0,-70],[34,-30]],VSD,15);
  fc(4,-120,26,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(4,-120,27,Math.PI,0); ctx.fill(); ctx.restore(); }
// sole con i raggi che girano
function s7Sole(x,y,r,u){ ctx.save(); ctx.translate(x,y); ctx.rotate(u*.4); for(let i=0;i<12;i++){ const a=i/12*TAU; ln([[Math.cos(a)*r*1.25,Math.sin(a)*r*1.25],[Math.cos(a)*r*1.6,Math.sin(a)*r*1.6]],C.giallo,10); } ctx.restore();
  fc(x,y,r*1.15,'rgba(242,228,51,.2)'); fc(x,y,r,C.giallo); }
// onde di calore che salgono
function s7Calore(x,y,w,h,u,n=4,col='rgba(255,170,110,.75)'){ for(let i=0;i<n;i++){ const xx=x+(n>1?i*w/(n-1):0), f=(u*.6+i*.27)%1; ctx.save(); ctx.globalAlpha*=Math.sin(f*Math.PI);
  const pts=[]; for(let j=0;j<=12;j++){ const yy=y-f*40-j*h/12; pts.push([xx+Math.sin(j*.9+u*4+i)*12,yy]); } ln(pts,col,7); ctx.restore(); } }
// acqua vista di lato, con la superficie che ondeggia: da y (superficie) a yb (fondo)
function s7Acqua(x0,x1,y,yb,u,o={}){ ctx.save(); ctx.globalAlpha*=o.alpha??.94; ctx.fillStyle=o.col||S7_ACQUA; ctx.beginPath(); ctx.moveTo(x0,yb);
  for(let x=x0;x<=x1+1;x+=10) ctx.lineTo(x,y+Math.sin(x*.035+u*3)*5); ctx.lineTo(x1,yb); ctx.closePath(); ctx.fill(); ctx.restore();
  for(let i=0;i<3;i++){ const yy=y+22+i*28; if(yy>yb-8) break; const off=(u*30*(1+i*.3))%90; ctx.strokeStyle='rgba(127,208,240,.55)'; ctx.lineWidth=4; ctx.beginPath();
    for(let x=x0+20-off+(i%2)*45;x<x1-40;x+=90){ if(x<x0+10) continue; ctx.moveTo(x,yy); ctx.quadraticCurveTo(x+15,yy-7,x+30,yy); } ctx.stroke(); } }
// testa di chi è in acqua: la testa ondeggia, l'acqua la copre fino alla bocca (la disegna chi chiama)
function s7Testa(x,y,r,u,o={}){ const b=Math.sin(u*(o.vel||2.4))*(o.amp??8); head(x,y+b,r,{mouth:o.mouth||'o',hairCol:o.hairCol}); return b; }
function s7Cerchi(x,y,u,n=3,w=150){ for(let i=0;i<n;i++){ const f=(u*.5+i/n)%1; ctx.strokeStyle=`rgba(255,255,255,${.7*(1-f)})`; ctx.lineWidth=5; ctx.beginPath(); ctx.ellipse(x,y,30+f*w,8+f*w*.18,0,0,TAU); ctx.stroke(); } }
// salvagente bianco e rosso
function s7Salvagente(x,y,r,rot=0){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); for(let i=0;i<8;i++) arc(0,0,r,i*TAU/8,(i+1)*TAU/8,i%2?'#fff':RED,r*.55); ctx.restore(); }
// impacco: ghiaccio avvolto in un panno
function s7Impacco(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-46,-26,92,52,22,'#f4f6fb'); ctx.globalAlpha*=.9; cube(0,-6,.5,'#dff3fb'); ctx.globalAlpha=1;
  ctx.strokeStyle='rgba(27,34,63,.18)'; ctx.lineWidth=3; ctx.beginPath(); ctx.moveTo(-40,-6); ctx.lineTo(-20,20); ctx.moveTo(40,-6); ctx.lineTo(20,20); ctx.stroke(); ctx.restore(); }
// panno bagnato che gocciola
function s7Panno(x,y,w,h,u,a=1){ if(a<=0) return; ctx.save(); ctx.globalAlpha*=clamp(a); box(x,y,w,h,h/2.4,S7_PANNO); ln([[x+14,y+h*.35],[x+w-14,y+h*.35]],'rgba(0,131,176,.35)',4);
  for(let i=0;i<3;i++){ const f=(u*1.3+i/3)%1; drop(x+w*(.25+i*.25),y+h+6+f*34,.22,`rgba(0,165,220,${1-f})`); } ctx.restore(); }
// ventaglio che fa aria
function s7Ventaglio(x,y,s,u){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.rotate(Math.sin(u*6)*.35);
  ctx.fillStyle='#fff'; ctx.beginPath(); ctx.moveTo(0,0); ctx.arc(0,0,130,-Math.PI*.85,-Math.PI*.15); ctx.closePath(); ctx.fill();
  for(let i=0;i<=6;i++){ const a=-Math.PI*.85+i*(Math.PI*.7/6); ln([[0,0],[Math.cos(a)*128,Math.sin(a)*128]],'#cfd6e8',4); }
  arc(0,0,128,-Math.PI*.85,-Math.PI*.15,C.ciano,8); box(-10,-6,20,70,8,S7_LEGNO); ctx.restore(); }
// bottiglia d'alcol rosa (alcol denaturato)
function s7Alcol(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-40,-60,80,140,18,'rgba(232,138,168,.9)'); box(-16,-96,32,40,6,'rgba(232,138,168,.9)'); box(-20,-112,40,20,6,'#fff'); box(-30,-14,60,40,6,'#fff'); ctx.restore(); }
// bicchiere di vino (alcol da bere)
function s7Calice(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  ctx.fillStyle='#9b2c45'; ctx.beginPath(); ctx.moveTo(-46,-30); ctx.quadraticCurveTo(-46,40,0,44); ctx.quadraticCurveTo(46,40,46,-30); ctx.closePath(); ctx.fill();
  ctx.strokeStyle='#fff'; ctx.lineWidth=7; ctx.beginPath(); ctx.moveTo(-52,-80); ctx.quadraticCurveTo(-58,44,0,48); ctx.quadraticCurveTo(58,44,52,-80); ctx.stroke();
  ln([[0,48],[0,110]],'#fff',8); ln([[-40,112],[40,112]],'#fff',8); ctx.restore(); }

Object.assign(ILL, {
// ---------- Morso di vipera ----------
vipera({u,A}){
  ground(222);
  s7Sasso(-380,200,70,40); s7Sasso(-250,215,50,26); s7Ciuffo(-160,222,1.2); s7Sasso(330,205,80,42); s7Ciuffo(420,222,1);
  s7Vipera(-40,120,1,u);
  s7Sasso(-120,222,46,24); s7Sasso(90,226,60,28); s7Ciuffo(210,226,1.1);
  // lente sull'occhio: testa triangolare e pupilla verticale
  grp(300,-160,1,A(.45),()=>{ fc(0,0,120,C.tile); arc(0,0,120,0,TAU,C.giallo,8);
    ctx.save(); ctx.beginPath(); ctx.arc(0,0,112,0,TAU); ctx.clip();
    ctx.fillStyle=S7_VIP; ctx.beginPath(); ctx.moveTo(-140,60); ctx.lineTo(-30,-70); ctx.quadraticCurveTo(60,-90,140,-20); ctx.lineTo(140,140); ctx.lineTo(-140,140); ctx.closePath(); ctx.fill();
    ln([[-40,-56],[40,-74],[120,-30]],S7_VIPD,10); fe(20,-10,44,36,'#e8a73a'); fe(20,-10,8,30,'#0d1226'); fc(6,-24,6,'rgba(255,255,255,.7)'); ctx.restore(); });
  const k=A(.45); if(k>0){ ctx.save(); ctx.globalAlpha*=clamp(k); ctx.setLineDash([12,10]); ln([[215,-75],[205,95]],'rgba(242,228,51,.75)',5); ctx.restore(); }
},
'morso-vipera'({u,p,A}){
  ctx.save(); ctx.translate(60,0);
  const g=clamp(A(.65)), b=clamp(A(.85));
  fe(-80,40,80+48*g,120+50*g,SK);                                      // gonfiore
  box(-160,-310,160,420,70,SK); box(-185,80,390,130,62,SK); fe(-35,85,26,22,SKD);   // gamba e piede
  for(let i=0;i<4;i++) fc(196,104+i*26,15,SK);
  fe(-80,40,80+48*g,120+50*g,SK);
  if(g>0) fe(-80,40,(80+48*g)*.8,(120+50*g)*.8,`rgba(217,71,61,${.18*g})`);
  if(b>0) fe(-80,30,22+84*b,20+90*b,`rgba(96,72,160,${.5*b})`);           // livido bluastro
  box(-182,-320,204,96,20,PANT);                                        // orlo dei pantaloni
  const d=A(.2); if(d>0){ fc(-104,20,9,'#7a1f1a'); fc(-56,20,9,'#7a1f1a');
    grp(-80,-24,1,d,()=>{ ln([[-24,0],[24,0]],C.giallo,5); ln([[-24,-10],[-24,10]],C.giallo,5); ln([[24,-10],[24,10]],C.giallo,5); }); }
  const pa=A(.45); if(pa>0){ ctx.save(); ctx.globalAlpha*=clamp(pa); const f=(u*1.4)%1;
    for(let i=0;i<2;i++){ const ff=(f+i/2)%1; ctx.strokeStyle=`rgba(217,71,61,${1-ff})`; ctx.lineWidth=7; ctx.beginPath(); ctx.ellipse(-80,20,40+ff*120,30+ff*100,0,0,TAU); ctx.stroke(); }
    [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([sx,sy])=>{ const r0=150, x0=-80+sx*r0, y0=20+sy*r0*.8; ln([[x0,y0],[x0+sx*24,y0+sy*4],[x0+sx*14,y0+sy*22],[x0+sx*40,y0+sy*28]],C.giallo,7); });
    ctx.restore(); }
  ctx.restore();
},
'vipera-fermo'({u,p,A}){
  lying(-80,225,.8,{rise:Math.sin(u*1.4)*4});
  const a=A(.2); if(a>0){ ctx.save(); ctx.globalAlpha*=clamp(a); ctx.setLineDash([16,12]); ctx.strokeStyle=C.giallo; ctx.lineWidth=6; rr(ctx,-80+180*.8,225-150*.8,360*.8,140*.8,40); ctx.stroke(); ctx.restore();
    fc(-80+430*.8,225-80*.8,6,'#7a1f1a'); fc(-80+446*.8,225-80*.8,6,'#7a1f1a'); }
  const c=A(.4); if(c>0) grp(-200,128,1,c,()=>handTop(0,0,.55,{sleeve:DIV}));   // una mano sulla spalla: calmo
  grp(250,-130,1,A(.8),()=>{ s7Tondo(130,()=>s7Cammina(0,-8,1.05,u)); vieto(0,0,118,A(.86)); });
},
'vipera-no'({u,A}){
  const it=[
    [-330,.15,()=>{ ln([[-100,10],[-40,10]],VS,50); ln([[-44,10],[46,10]],SK,40); fe(60,10,24,21,SK);
      box(-12,-16,24,52,6,S7_LEGNO); ln([[0,-14],[-22,-46]],S7_LEGNO,9); ln([[0,-14],[22,-46]],S7_LEGNO,9); fc(0,-14,9,'#6f4729'); }],
    [-110,.35,()=>{ ctx.rotate(-.6); poly([[-70,-8],[50,-22],[60,-6],[50,12],[-70,12]],'#cfd6e8'); ln([[-62,4],[48,-6]],'#fff',3); box(-130,-14,62,32,10,S7_LEGNO); }],
    [110,.55,()=>{ ln([[-100,52],[100,52]],SK,40); fc(-42,46,5,'#7a1f1a'); fc(-22,46,5,'#7a1f1a');
      fc(10,-22,46,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(10,-24,48,Math.PI*.95,Math.PI*2.05); ctx.fill(); fc(-16,-14,5,C.navy); fe(52,-12,9,12,SKD);
      fe(-30,24,13,10,'#c4575a'); fe(-30,24,5,4,'#5a1f24'); }],
    [330,.8,()=>{ cube(0,-4,1.5,'#dff3fb'); }],
  ];
  it.forEach(([x,t,f])=>grp(x,-90,1,A(t),()=>{ s7Tondo(100,f); vieto(0,0,90,A(t+.06)); }));
  grp(0,145,1,A(.9),()=>{ s7Tondo(82,()=>{ ctx.save(); ctx.translate(-14,18); ctx.rotate(-.25); box(-34,-40,68,82,26,'#e8702a'); box(-12,-58,24,20,6,'#c25a1e'); ln([[-20,-10],[20,-10]],'rgba(255,255,255,.4)',5); ln([[-20,8],[20,8]],'rgba(255,255,255,.4)',5); ctx.restore();
    s7Calore(28,-10,30,40,u,2,'rgba(255,170,110,.95)'); }); vieto(0,0,72,A(.96)); });
},
siero({u,A}){
  // ospedale: il siero c'è, decide il medico
  box(-430,-190,420,420,16,'#e3e7f1'); box(-300,-262,160,82,16,'#fff'); cross(-220,-221,.5,RED);
  box(-404,-160,368,370,12,'#24305c');
  bust(-300,150,.42,{shirt:'#f4f6fb',shirtD:'#cfd6e8',head:{mouth:'smile',glasses:true},over(){ steto(0,40,.7); }});
  box(-190,120,150,90,8,'#cfd6e8'); s7Flacone(-115,80,.9);
  spunta(-90,-110,46,A(.85));
  // fuori dall'ospedale: niente siero nello zaino
  grp(240,30,1,A(.5),()=>{ fc(0,0,175,C.tile); s7Zaino(0,30,.9); s7Flacone(40,-90,.75); vieto(0,0,160,A(.56)); });
},
sentiero({u,A}){
  // gambe sul sentiero: scarponcini e pantaloni lunghi
  ctx.save(); ctx.translate(-230,0);
  poly([[-200,240],[-60,30],[60,30],[200,240]],S7_SABBIA); s7Ciuffo(-150,180,1); s7Ciuffo(160,200,1.1); s7Sasso(-120,236,40,18);
  const st=Math.sin(u*3)*10;
  [[-55,'#262f5a',st],[55,PANT,-st]].forEach(([x,col,o])=>{ ln([[x*.6,-300],[x,170+o*.3]],col,78);
    box(x-48,150+o*.3,104,68,22,'#6b4a2e'); box(x-48,198+o*.3,108,20,8,'#2e2218'); for(let i=0;i<3;i++) ln([[x-18,166+i*12+o*.3],[x+18,166+i*12+o*.3]],'#e9d3a8',3); });
  const sc=A(.25); if(sc>0){ ctx.save(); ctx.globalAlpha*=clamp(sc); ctx.strokeStyle=C.giallo; ctx.lineWidth=7; ctx.beginPath(); ctx.ellipse(0,190,150,58,0,0,TAU); ctx.stroke(); ctx.restore(); spunta(165,120,34,sc); }
  const pl=A(.45); if(pl>0){ ctx.save(); ctx.globalAlpha*=clamp(pl); ctx.setLineDash([12,10]); ln([[-110,-290],[-110,120]],C.giallo,6); ln([[110,-290],[110,120]],C.giallo,6); ctx.restore(); spunta(150,-180,34,pl); }
  ctx.restore();
  // muretto al sole: non sederti
  grp(230,-160,1,A(.7),()=>{ box(-185,-110,370,220,26,C.tile); ctx.save(); rr(ctx,-185,-110,370,220,26); ctx.clip();
    s7Sole(110,-55,34,u); for(let r=0;r<3;r++) for(let c=0;c<5;c++) box(-170+c*70+(r%2)*35,10+r*34,64,30,6,r%2?'#b9a07a':'#c9b08a');
    s7Seduto(-105,8,1.25); ctx.restore(); vieto(0,0,100,A(.76)); });
  // mani fuori da sassi e cespugli
  grp(230,95,1,A(.9),()=>{ box(-185,-110,370,220,26,C.tile); ctx.save(); rr(ctx,-185,-110,370,220,26); ctx.clip();
    fc(-90,40,70,S7_ERBA); fc(-30,20,60,'#3f8a4c'); s7Sasso(60,70,80,45); s7Sasso(-10,95,60,30); hand(40,-10,.55,Math.PI*.85); ctx.restore(); vieto(0,0,100,A(.95)); });
},
// ---------- Colpo di calore ----------
'termometro-caldo'({u}){
  s7Sole(-230,-150,95,u); s7Calore(-400,230,320,110,u,5);
  const r=outCubic(clamp(u/2.6)), top=-240, bot=150, h=lerp(40,bot-top,r);
  box(110,-270,80,430,40,'#fff'); box(126,-254,48,90,20,'rgba(217,71,61,.25)'); fc(150,180,80,'#fff'); fc(150,180,60,RED);
  box(130,bot-h,40,h+30,20,RED);
  for(let i=0;i<9;i++) ln([[190,-230+i*40],[220,-230+i*40]],i<3?RED:'#cfd6e8',5);
},
'caldo-segni'({u,p,A}){
  const f=A(.15), c=A(.5), cv=A(.75), nr=A(.9)>.5;
  const jx=(cv>.5&&!nr)?Math.sin(u*38)*6:(c>.5&&!nr?Math.sin(u*5)*4:0);
  ctx.save(); if(nr){ ctx.translate(0,190); ctx.rotate(.08); ctx.translate(0,-190); }
  bust(0,190,.8,{jx,head:{mouth:nr?'flat':(c>.5?'o':'sad'),closed:nr},over(){
    if(f>0){ ctx.save(); ctx.globalAlpha*=clamp(f); fe(0,-200,92,88,'rgba(217,71,61,.22)'); fe(-58,-168,28,17,'rgba(217,71,61,.55)'); fe(58,-168,28,17,'rgba(217,71,61,.55)'); ctx.restore(); }
    if(c>0&&!nr){ ctx.save(); ctx.globalAlpha*=clamp(c); [[-80,-360],[80,-360]].forEach(([x,y],i)=>{ ctx.strokeStyle=C.giallo; ctx.lineWidth=8; ctx.beginPath(); for(let a=0;a<12;a+=.25){ const r=a*3.4; ctx.lineTo(x+Math.cos(a+u*(i?-3:3))*r,y+Math.sin(a+u*(i?-3:3))*r); } ctx.stroke(); }); ctx.restore(); }
  }});
  ctx.restore();
  if(f>0){ ctx.save(); ctx.globalAlpha*=clamp(f); s7Calore(-300,60,600,90,u,6); ctx.restore(); }
  if(cv>0&&!nr){ ctx.save(); ctx.globalAlpha*=clamp(cv); [-1,1].forEach(s=>{ for(let i=0;i<3;i++) ln([[s*(150+i*22),-30+i*30],[s*(170+i*22),-10+i*30]],'#fff',6); }); ctx.restore(); }
},
ombra({u,p,A}){
  ground(226);
  s7Sole(-330,-190,70,u); fe(-260,226,200,16,'rgba(242,228,51,.25)');
  fe(190,226,260,22,'rgba(8,20,50,.45)');
  box(315,-60,56,290,14,S7_LEGNO); [[280,-170,115],[370,-200,100],[335,-90,100],[230,-90,85],[405,-110,70]].forEach(([x,y,r],i)=>fc(x,y,r,i%2?'#3fa35f':'#2f8a4f'));
  const t=inOut(clamp((p-.08)/.24)), x=lerp(-240,120,t), s=.55;
  if(t>0&&t<1){ ctx.save(); ctx.setLineDash([14,12]); arrow(-120,120,40,120,'rgba(242,228,51,.7)',7); ctx.restore(); }
  lying(x,226,s,{});
  const v=clamp(A(.75));
  ctx.save(); ctx.translate(x,226); ctx.scale(s,s);
  if(v<1){ ctx.save(); ctx.globalAlpha*=1-v; box(-220,-124,360,82,40,'#8a5a3a'); ln([[-150,-40],[60,-34]],'#6f4729',32); fc(78,-34,18,SK); box(508,-126,36,92,12,'#1a1f36'); ctx.restore(); }
  if(v>0){ ctx.save(); ctx.globalAlpha*=v; box(508,-126,40,92,16,SK); ctx.restore(); }
  ctx.restore();
  grp(-180,212,1,A(.75),()=>{ box(-70,-22,120,30,10,'#8a5a3a'); box(-60,-34,100,16,8,'#6f4729'); box(64,-14,56,24,10,'#1a1f36'); box(84,-6,56,24,10,'#1a1f36'); });
},
'vasca-fredda'({u,p,A}){
  // vasca in sezione: la testa fuori, il corpo sott'acqua dal collo in giù
  const b=Math.sin(u*1.5)*3;
  box(-404,40,528,166,30,'#e3e7f1');
  box(-330,10+b,40,40,10,SKD); box(-300,30+b,240,70,34,VS); ln([[-80,64+b],[110,40],[110,150]],PANT,52); box(84,150,52,30,12,SK);
  head(-310,-34+b,58,{mouth:'flat'});
  ctx.save(); ctx.globalAlpha*=.62; box(-404,16,528,190,30,S7_ACQUAL); ctx.restore();
  sbox(-412,10,544,204,36,'#f4f6fb',16); box(-410,212,40,24,8,'#cfd6e8'); box(90,212,40,24,8,'#cfd6e8');
  for(let i=0;i<4;i++) cube(-200+i*80,14+Math.sin(u*2+i)*3,.45,'#eef9fd');
  const n=A(.35); if(n>0){ ctx.save(); ctx.globalAlpha*=clamp(n); ctx.setLineDash([14,10]); ln([[-440,12],[160,12]],C.giallo,6); ctx.restore(); arrow(170,0,170,110,C.giallo,9); }
  // la doccia fredda, in alternativa
  grp(310,-150,1,A(.75),()=>{ fc(0,0,120,C.tile); ln([[60,-90],[60,-70],[20,-70]],'#cfd6e8',10); fe(10,-66,30,12,'#cfd6e8');
    for(let i=0;i<9;i++){ const yy=-50+((u*200+i*25)%110); fe(-10+((i%3)-1)*16,yy,4,9,S7_ACQUAL); } stick(-6,10,.65,{}); });
  // termometro che scende
  ctx.save(); ctx.translate(320,120); ctx.scale(.42,.42);
  const r=clamp(p*1.1), h=lerp(330,110,r); box(-40,-260,80,400,40,'#fff'); fc(0,170,80,'#fff'); fc(0,170,60,r>.6?C.ciano:RED); box(-20,140-h,40,h+30,20,r>.6?C.ciano:RED);
  arrow(110,-160,110,40,C.ciano,16); ctx.restore();
},
raffredda({u,p,k,A}){
  const due=((SCENE[k]&&SCENE[k].tags)||[]).some(t=>/operatore/i.test(t[0]));
  const X=-40, Y=228, S=.78, L=(lx,ly)=>[X+lx*S,Y+ly*S];
  lying(X,Y,S,{rise:Math.sin(u*2)*3});
  const a1=due?1:A(.2), a2=due?1:A(.45), a3=due?1:A(.7), a4=due?1:A(.9);
  ctx.save(); ctx.translate(X,Y); ctx.scale(S,S); s7Panno(-180,-146,260,34,u,a1); s7Panno(270,-104,190,28,u,a1); ctx.restore();
  const P=[L(-205,-98),L(-160,-52),L(190,-82)];
  if(a3>0){ const f=(u*1.2)%1; P.forEach(([x,y])=>{ ctx.save(); ctx.globalAlpha*=clamp(a3)*(1-f); arc(x,y,40+f*40,0,TAU,C.giallo,6); ctx.restore(); }); }
  P.forEach(([x,y],i)=>grp(x,y,1,a2,()=>s7Impacco(0,0,i?.8:.62)));
  grp(-60,due?20:-60,1,a4,()=>{ s7Ventaglio(0,0,due?.75:1,u); for(let i=0;i<3;i++){ const f=(u*1.5+i/3)%1; ctx.save(); ctx.globalAlpha*=1-f; ln([[-50+i*50,30+f*60],[-40+i*50,60+f*60]],'#fff',5); ctx.restore(); } });
  if(due){
    grp(-330,-185,1,A(.2),()=>{ fc(0,0,88,C.tile); phone(0,0,.36,{num:'112',ring:true,u}); });
    grp(-110,-185,1,A(.5),()=>{ fc(0,0,88,C.tile); glass(0,0,.62,.55); });
    grp(110,-185,1,A(.75),()=>{ fc(0,0,88,C.tile); pill(0,0,.8); vieto(0,0,78,A(.81)); });
    grp(330,-185,1,A(.9),()=>{ fc(0,0,88,C.tile); s7Alcol(0,8,.62); vieto(0,0,78,A(.96)); });
  }
},
'caldo-previeni'({u,A}){
  grp(-200,-140,1,A(.15),()=>{ fc(0,0,115,C.tile); clockFace(0,0,78,7,0); arc(0,0,92,Math.PI*.5,Math.PI*.83,C.ciano,12); arc(0,0,92,-Math.PI*.5,-Math.PI*.17,C.ciano,12); });
  grp(200,-140,1,A(.35),()=>{ fc(0,0,115,C.tile); box(-36,-60,72,130,22,'rgba(159,216,240,.85)'); box(-36,-10,72,80,20,'#5fb7e5'); box(-18,-86,36,30,8,'#fff'); box(-36,-40,72,26,4,'#fff'); });
  grp(-200,115,1,A(.6),()=>{ fc(0,0,115,C.tile); phone(-42,4,.3,{num:'',label:'',ring:true,u}); head(42,-6,36,{hairCol:GRAYH,glasses:true}); box(10,30,64,60,24,'#bfc8de'); });
  grp(200,115,1,A(.9),()=>{ fc(0,0,115,C.tile); s7Sole(52,-58,22,u); car(-25,42,.5,'#cfd6e8'); fc(-44,2,12,SK); ctx.fillStyle='#8a6a4a'; ctx.beginPath(); ctx.arc(-44,0,13,Math.PI,0); ctx.fill(); vieto(0,0,100,A(.95)); });
},
// ---------- Annegamento ----------
annega({u}){
  const y=60, b=Math.sin(u*2.1)*22;
  head(0,y-36+b,70,{mouth:'o'});
  s7Acqua(-440,440,y,240,u);
  s7Cerchi(0,y+4,u,3,260);
},
riva({u,p,A}){
  poly([[-440,150],[-80,150],[0,240],[-440,240]],S7_SABBIA);
  s7Testa(300,104,42,u,{amp:10});
  s7Acqua(-100,440,140,240,u);
  s7Cerchi(300,142,u,2,90);
  const ch=A(.55)>.5, tel=A(.85)>.5;
  ctx.save(); ctx.translate(-270,0); ctx.scale(-1,1);
  sideFig(0,22,.6,{mouth:ch&&!tel?'o':'flat',frontArm(){
    if(tel){ ln([[-10,-260],[-60,-330],[-40,-390]],VSD,40); box(-60,-430,28,60,8,'#0d1226'); fc(-44,-388,22,SK); }
    else if(ch){ ln([[-10,-260],[-80,-300],[-80,-360]],VSD,40); fc(-80,-362,22,SK); }
    else ln([[-10,-260],[-20,-120]],VSD,40); }});
  ctx.restore();
  if(ch&&!tel){ for(let i=0;i<3;i++){ const f=(u*1.4+i/3)%1; arc(-226,-200,30+f*60,-1.2,-.2,`rgba(255,255,255,${1-f})`,6); arc(-226,-200,30+f*60,Math.PI+.2,Math.PI+1.2,`rgba(255,255,255,${1-f})`,6); } }
  const r=A(.3); if(r>0){ ctx.save(); ctx.globalAlpha*=clamp(r); ctx.setLineDash([14,12]); arrow(-200,110,40,110,'rgba(242,228,51,.8)',7); ctx.restore(); vieto(-40,60,70,r); }
  grp(-80,-180,1,A(.85),()=>phone(0,0,.38,{num:'112',ring:true,u}));
},
salvagente({u,p,A}){
  poly([[-440,150],[-80,150],[0,240],[-440,240]],S7_SABBIA);
  s7Testa(300,104,42,u,{amp:8});
  const t=clamp((p-.14)/.22), ex=210, ey=128;
  const H=[-215,-150], q=outCubic(t), sx=lerp(H[0],ex,q), sy=lerp(H[1],ey,q)-Math.sin(q*Math.PI)*110;
  s7Acqua(-100,440,140,240,u);
  s7Cerchi(300,142,u,2,90);
  ctx.save(); ctx.translate(-280,0); ctx.scale(-1,1);
  sideFig(0,22,.6,{frontArm(){ if(t>0) ln([[-10,-260],[-90,-300],[-150,-330]],VSD,40); else ln([[-10,-260],[40,-200],[90,-190]],VSD,40); }});
  ctx.restore();
  const hand=t>0?[-280+150*.6,22-330*.6]:[-280-90*.6,22-190*.6];
  ctx.save(); ctx.setLineDash([10,8]); ctx.strokeStyle='#e9d3a8'; ctx.lineWidth=5; ctx.beginPath(); ctx.moveTo(hand[0],hand[1]); ctx.quadraticCurveTo((hand[0]+sx)/2,Math.max(hand[1],sy)+40,sx,sy); ctx.stroke(); ctx.restore();
  fc(hand[0],hand[1],13,SK);
  const bob=t>=1?Math.sin(u*2.4)*5:0; s7Salvagente(sx,sy+bob,32,q*6);
  grp(135,-195,1,A(.55),()=>{ fc(0,0,100,C.tile); ctx.save(); ctx.beginPath(); ctx.arc(0,0,96,0,TAU); ctx.clip(); ctx.scale(1.12,1.12);
    box(-60,-34+Math.sin(u*2)*3,64,70,10,'#f4f6fb'); box(-44,-50,22,18,4,'#f4f6fb'); fc(38,4+Math.sin(u*2+1)*3,30,C.giallo); ln([[10,4],[66,4]],'#e8702a',5); s7Acqua(-90,90,24,90,u); ctx.restore(); });
  grp(350,-195,1,A(.85),()=>{ fc(0,0,100,C.tile); ctx.save(); ctx.beginPath(); ctx.arc(0,0,96,0,TAU); ctx.clip(); ctx.scale(1.12,1.12);
    ln([[-80,-50],[50,30]],S7_LEGNO,10); head(56,22,20,{mouth:'flat'}); s7Acqua(-90,90,40,90,u); arc(-40,40,22,0,TAU,'#e9d3a8',6); arc(-40,40,12,0,TAU,'#e9d3a8',5); ctx.restore(); });
},
'acqua-sicura'({u,A}){
  const T=(x,y,t,fn,no)=>grp(x,y,1,A(t),()=>{ box(-200,-115,400,230,26,C.tile); ctx.save(); rr(ctx,-200,-115,400,230,26); ctx.clip(); fn(); ctx.restore(); if(no) vieto(0,0,100,A(t+.06)); });
  // bambino in acqua con un adulto vicino, piscina con la recinzione
  T(-215,-150,.2,()=>{ for(let i=0;i<9;i++) ln([[-180+i*45,-100],[-180+i*45,-10]],'#cfd6e8',6); ln([[-200,-90],[200,-90]],'#cfd6e8',6); ln([[-200,-40],[200,-40]],'#cfd6e8',6);
    box(-200,44,170,80,0,'#cfd6e8'); stick(-105,-34,.75,{shirt:'#f2a541'}); s7Testa(20,26,26,u,{mouth:'smile',hairCol:'#8a6a4a',amp:3}); s7Acqua(-30,200,44,115,u);
    ctx.save(); ctx.setLineDash([8,8]); ln([[-72,-30],[-6,10]],C.giallo,5); ctx.restore(); });
  // mai da soli: due nuotatori insieme
  T(215,-150,.45,()=>{ [[-60,0],[60,.9]].forEach(([x,ph])=>{ const a=u*3+ph; ln([[x,20],[x+Math.cos(a)*54,20-Math.abs(Math.sin(a))*50]],SK,14); s7Testa(x,10,26,u,{mouth:'smile',amp:3}); });
    s7Acqua(-200,200,34,115,u); });
  // niente alcol prima di entrare in acqua
  T(-215,105,.7,()=>{ s7Calice(-10,-10,.85); s7Acqua(-200,200,80,115,u); },true);
  // impara a nuotare: bambino con la tavoletta
  T(215,105,.9,()=>{ box(-120,-6,80,22,10,'#e8702a'); ln([[-40,10],[60,16]],'#f2a541',24); ln([[60,16],[110,8+Math.sin(u*10)*10]],SK,12); ln([[60,20],[110,28-Math.sin(u*10)*10]],SK,12);
    s7Testa(-62,-10,24,u,{mouth:'smile',hairCol:'#8a6a4a',amp:2}); s7Acqua(-200,200,14,115,u,{alpha:.75});
    for(let i=0;i<3;i++){ const f=(u*2+i/3)%1; fc(130+f*30,0-f*30,6+f*4,`rgba(255,255,255,${1-f})`); } });
},
});
