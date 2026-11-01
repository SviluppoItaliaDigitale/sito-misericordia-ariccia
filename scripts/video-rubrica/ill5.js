// ===== Disegni della 3ª serie (gennaio 2027): DAE, posizione laterale di sicurezza, sangue dal naso =====
// Le funzioni di aiuto hanno il prefisso s5 (tutti gli ill*.js finiscono nello stesso script: niente nomi doppi).
const S5_VERDE='#009a49';   // verde di sicurezza del cartello DAE (ILCOR)
// cartello DAE ILCOR: quadrato verde, cuore bianco con il fulmine verde, piccola croce bianca in alto a destra; L = lato
function s5Cartello(x,y,L){ ctx.save(); ctx.translate(x,y);
  box(-L/2,-L/2,L,L,L*.1,S5_VERDE); sbox(-L/2+L*.05,-L/2+L*.05,L*.9,L*.9,L*.07,'#fff',L*.025);
  ctx.fillStyle='#fff'; heartP(-L*.04,L*.06,L/330); ctx.fill(); bolt(-L*.04,-L*.02,L*.0042,S5_VERDE);
  cross(L*.27,-L*.27,L*.0011,'#fff'); ctx.restore(); }
// DAE aperto visto di fronte: schermo, altoparlante, pulsante di accensione (verde) e di scarica (arancione)
// o: lid 0 chiuso…1 aperto, on, ecg (traccia che scorre), shock (lampeggio 0..1), press (pulsante premuto), u
function s5Dae(x,y,s,o={}){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); const u=o.u||0, lid=o.lid??1;
  box(-170,-120,340,240,34,C.giallo); box(-150,-100,300,200,22,'#2b3352');
  box(-132,-84,176,112,12,o.on?'#0f3d4c':'#151a30');
  if(o.on){ ctx.save(); rr(ctx,-132,-84,176,112,12); ctx.clip();
    if(o.ecg){ const pts=[]; for(let i=0;i<=44;i++){ const xx=-132+i*4, t=i*.35+u*9; pts.push([xx,-28+Math.sin(t)*14+Math.sin(t*2.3+1)*9+Math.sin(t*.7)*6]); } ln(pts,'#5fe39a',5); }
    else { box(-112,-62,120,12,6,'rgba(95,227,154,.8)'); box(-112,-38,90,12,6,'rgba(95,227,154,.55)'); box(-112,-14,130,12,6,'rgba(95,227,154,.55)'); }
    ctx.restore(); }
  for(let i=0;i<3;i++) for(let j=0;j<3;j++) fc(72+i*18,-62+j*18,5,'#11162b');
  const pr=o.press?6:0; fc(-80,62,26,'#1a1f36'); fc(-80,62,20-pr*.3,o.on?'#2fbf71':'#59627f');
  if(o.on){ ctx.strokeStyle='#fff'; ctx.lineWidth=4; ctx.beginPath(); ctx.arc(-80,62,9,-1.1,4.2); ctx.moveTo(-80,49); ctx.lineTo(-80,60); ctx.stroke(); }
  const sh=o.shock||0; if(sh>0) fc(60,62,30+22*sh,`rgba(232,112,42,${.45*sh})`);
  fc(60,62,32,'#1a1f36'); fc(60,62,26,o.shockOn?C.arancio:'#8a5a3e'); bolt(60,62,.62,'#fff');
  { ctx.save(); ctx.translate(0,-120); const k=Math.cos(clamp(lid)*Math.PI*.571); ctx.scale(1,k);   // coperchio: da chiuso (k=1) ad aperto all'indietro (k=-0,22)
    box(-170,0,340,240,34,k>0?'#e3d42c':'#c9bb1c'); if(k>0) box(-40,206,80,20,10,'#b8aa18');
    ctx.restore(); }
  ctx.restore(); }
// onde sonore dall'altoparlante, verso destra
function s5Onde(x,y,u,a=1,r0=40){ if(a<=0) return; for(let i=0;i<3;i++){ const f=(u*1.1+i/3)%1; arc(x,y,r0+f*80,-.7,.7,`rgba(242,228,51,${a*(1-f)})`,8); } }
// mano con l'indice teso: punta in (x,y), mano e manica dietro; rot 0 = dito verso l'alto
function s5Dito(x,y,s,rot){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s);
  ln([[0,420],[0,170]],DIVD,96); ln([[0,420],[0,170]],DIV,86); ctx.fillStyle=ARG; ctx.fillRect(-43,196,86,5); ctx.fillStyle=FLUO; ctx.fillRect(-43,203,86,20); ctx.fillStyle=ARG; ctx.fillRect(-43,225,86,5);
  box(-48,62,96,124,38,SKD); box(-44,60,90,120,36,SK);
  for(let i=0;i<3;i++) ln([[-10+i*16,74],[-10+i*16,96]],SKD,4);
  box(-15,-2,30,104,15,SKD); box(-13,0,26,100,13,SK); box(-8,6,16,16,7,'#f3d9c6');
  box(-62,86,28,62,14,SKD); ctx.restore(); }
// mano vista dall'alto che arriva dal basso (soccorritore inginocchiato vicino a chi guarda), dita verso -y; ang ruota
function s5ManoSu(x,y,s,ang=0){ ctx.save(); ctx.translate(x,y); ctx.rotate(ang); ctx.scale(s,s);
  ln([[0,40],[0,700]],DIVD,100); ln([[0,40],[0,700]],DIV,90); ctx.fillStyle=FLUO; ctx.fillRect(-45,150,90,22);
  box(-56,-40,112,110,40,SKD); box(-52,-42,104,104,38,SK);
  for(let i=0;i<4;i++) box(-50+i*26,-104+Math.abs(i-1.5)*8,23,80,11,SK);
  box(46,-30,24,60,12,SK); ctx.restore(); }
// angolo retto disegnato in giallo: vertice (x,y), lati verso (dx1,dy1) e (dx2,dy2) di lunghezza d
function s5Retto(x,y,d,v1,v2,a=1){ if(a<=0) return; ctx.save(); ctx.globalAlpha*=clamp(a);
  ln([[x+v1[0]*d,y+v1[1]*d],[x+v1[0]*d+v2[0]*d,y+v1[1]*d+v2[1]*d],[x+v2[0]*d,y+v2[1]*d]],C.giallo,7); fc(x+(v1[0]+v2[0])*d*.45,y+(v1[1]+v2[1])*d*.45,6,C.giallo); ctx.restore(); }

// ---------- posizione laterale di sicurezza, vista dall'alto ----------
// testa a sinistra, piedi a destra, soccorritore in basso (dalla parte di chi guarda).
// st: near (braccio vicino: 0 lungo il fianco … 1 ad angolo retto), far (altro braccio: 0 lungo il fianco … 1 dorso sulla guancia),
//     knee (ginocchio lontano piegato), roll (rotola sul fianco verso il soccorritore), fix (gamba di sopra ad anca e ginocchio a 90°)
function s5PlsPose(st){ const r=st.roll||0, kn=st.knee||0, fx=st.fix||0, fa=st.far||0, na=st.near||0, L2=(a,b,t)=>[lerp(a[0],b[0],t),lerp(a[1],b[1],t)];
  const P={};
  P.head=[-335,lerp(0,26,r)]; P.tTop=lerp(-88,-14,r); P.tH=lerp(176,112,r);
  P.hipFar=[110,lerp(-38,22,r)]; P.hipNear=[110,lerp(38,44,r)];
  let knee=L2([275,-38],[212,-60],kn), ank=L2([432,-38],[290,-40],kn);
  knee=L2(knee,[185,122],r); ank=L2(ank,[330,132],r); knee=L2(knee,[118,168],fx); ank=L2(ank,[300,168],fx);
  P.knee=knee; P.ank=ank; P.kneeR=30+12*kn*(1-r);
  P.shN=[-232,lerp(90,64,r)]; const a=na*Math.PI/2; P.handN=[P.shN[0]+Math.cos(a)*245,P.shN[1]+Math.sin(a)*245];
  P.shF=[-232,lerp(-90,-8,r)];
  let el=L2([-108,-104],[-116,12],fa), hd=L2([24,-106],[-304,50],fa);
  if(fa>0&&fa<1){ el[1]-=Math.sin(fa*Math.PI)*36; hd[1]-=Math.sin(fa*Math.PI)*60; }
  P.elF=L2(el,[-136,86],r); P.handF=L2(hd,[-318,74],r);
  return P; }
function s5Pls(x,y,s,st){ const P=s5PlsPose(st), r=st.roll||0;
  ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  // braccio vicino: sopra il tronco a pancia in su, sotto quando rotola sul fianco
  const armN=()=>{ ln([P.shN,P.handN],VSD,52); ln([P.shN,P.handN],VS,44); fc(P.handN[0],P.handN[1],25,SKD); fc(P.handN[0],P.handN[1],22,SK); };
  if(r>.5) armN();
  // gamba vicina, distesa
  ln([P.hipNear,[432,P.hipNear[1]+4]],PANT,58); fe(452,P.hipNear[1]+4,24,30,'#1a1f36');
  // bacino e tronco
  box(18,lerp(-82,-16,r),126,lerp(164,116,r),50,PANT);
  box(-286,P.tTop,330,P.tH,lerp(60,46,r),VS);
  if(r<=.5) armN();
  // gamba lontana (di sopra)
  const sa=Math.atan2(P.ank[1]-P.knee[1],P.ank[0]-P.knee[0]);
  fe(P.ank[0]+Math.cos(sa)*22,P.ank[1]+Math.sin(sa)*22,32,21,'#1a1f36',sa);
  ln([P.knee,P.ank],'#3a4580',52); ln([P.hipFar,P.knee],PANT,58); fc(P.knee[0],P.knee[1],P.kneeR,PANT);
  if(st.knee>0&&r<1){ ctx.save(); ctx.globalAlpha*=st.knee*(1-r); fc(P.knee[0]-6,P.knee[1]-6,P.kneeR*.55,'rgba(255,255,255,.14)'); ctx.restore(); }
  // collo e testa (si gira verso il soccorritore rotolando)
  ln([[-300,P.head[1]*.6],[-262,P.head[1]*.6]],SKD,52);
  ctx.save(); ctx.translate(P.head[0],P.head[1]); ctx.rotate(r*Math.PI*.42);
  fc(0,0,64,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.moveTo(4,0); ctx.arc(0,0,66,Math.PI*(.58-.06*r),Math.PI*(1.42+.08*r)); ctx.closePath(); ctx.fill();
  ln([[16,-26],[16,-10]],C.navy,5); ln([[16,10],[16,26]],C.navy,5); fe(32,0,8,12,SKD); ln([[48,-11],[48,11]],C.navy,5);
  ctx.restore();
  // braccio lontano, mano con il dorso sulla guancia
  ln([P.shF,P.elF,P.handF],VSD,50); ln([P.shF,P.elF,P.handF],VS,42); fe(P.handF[0],P.handF[1],27,22,SKD); fe(P.handF[0],P.handF[1],24,19,SK);
  ln([[P.handF[0]-12,P.handF[1]-6],[P.handF[0]+10,P.handF[1]-8]],SKD,4);
  ctx.restore(); return P; }
// punto della posa nelle coordinate della scena
function s5Pt(x,y,s,p){ return [x+p[0]*s,y+p[1]*s]; }
const S5P={x:-30,y:-40,s:.8};

// ---------- sangue dal naso ----------
// testa di profilo rivolta a destra, (x,y) = centro del cranio; tilt > 0 testa in avanti, < 0 indietro (perno sul collo)
// restituisce la posizione della narice nelle coordinate di chi chiama
function s5Profilo(x,y,r,o={}){ const tilt=o.tilt||0, py=r*.72;
  ctx.save(); ctx.translate(x,y);
  if(o.neck!==false){ box(-r*.32,r*.45,r*.62,r*1.05,r*.2,SKD); }
  ctx.translate(0,py); ctx.rotate(tilt); ctx.translate(0,-py);
  fc(0,0,r,SK);
  poly([[r*.5,-r*.82],[r*.84,-r*.46],[r*.93,-r*.14],[r*.92,-r*.03],[r*1.2,r*.25],[r*1.14,r*.34],[r*.97,r*.36],[r*.99,r*.48],[r*.94,r*.55],[r*.98,r*.62],[r*.9,r*.74],[r*.84,r*.9],[r*.52,r*1.0],[r*.1,r*.86],[0,0]],SK);
  ctx.fillStyle=o.hairCol||HAIR; ctx.beginPath(); ctx.moveTo(r*.1,r*.18); ctx.arc(0,0,r*1.04,Math.PI*.6,Math.PI*1.8); ctx.lineTo(r*.52,-r*.66); ctx.quadraticCurveTo(r*.2,-r*.5,r*.1,r*.18); ctx.fill();
  fe(r*.06,r*.14,r*.14,r*.2,SKD); fe(r*.08,r*.14,r*.09,r*.14,SK);
  if(o.closed) ln([[r*.56,-r*.08],[r*.74,-r*.08]],C.navy,r*.06); else fc(r*.66,-r*.08,r*.075,C.navy);
  ln([[r*.56,-r*.24],[r*.78,-r*.25]],o.hairCol||HAIR,r*.06);
  fe(r*1.03,r*.31,r*.065,r*.035,'#9c6a52',.3);
  if(o.mouth==='o') fe(r*.93,r*.55,r*.05,r*.07,C.navy); else ln([[r*.88,r*.55],[r*.96,r*.55]],C.navy,r*.05);
  ctx.restore();
  const nx=r*1.05, ny=r*.36-py, c=Math.cos(tilt), sn=Math.sin(tilt);
  return [x+nx*c-ny*sn, y+py+nx*sn+ny*c]; }
// gocce di sangue che scendono da (x,y) per una caduta di h
function s5Gocce(x,y,h,u,n=2,sc=.4){ for(let i=0;i<n;i++){ const f=(u*1.1+i/n)%1; drop(x+f*4,y+12+f*h,sc*(1-f*.25),`rgba(217,71,61,${1-f*.8})`); } }
// naso visto di fronte (r = raggio della testa), (x,y) = centro della testa
function s5NasoFronte(x,y,r){ const ny=y+r*.2;
  ctx.strokeStyle=SKD; ctx.lineWidth=r*.035; ctx.lineCap='round'; ctx.beginPath(); ctx.moveTo(x-r*.07,ny-r*.18); ctx.quadraticCurveTo(x-r*.1,ny+r*.06,x-r*.14,ny+r*.12); ctx.stroke();
  fc(x-r*.13,ny+r*.15,r*.08,SKD); fc(x+r*.13,ny+r*.15,r*.08,SKD); fc(x-r*.12,ny+r*.14,r*.07,SK); fc(x+r*.12,ny+r*.14,r*.07,SK);
  fe(x,ny+r*.13,r*.1,r*.085,SK); fe(x-r*.06,ny+r*.21,r*.035,r*.02,'#8a5444'); fe(x+r*.06,ny+r*.21,r*.035,r*.02,'#8a5444'); }

Object.assign(ILL, {
// ===== DAE =====
// il DAE con sopra il cartello ILCOR; un cuore che batte e un fulmine che si accende a intervalli
'dae-intro'({u}){
  s5Cartello(-230,-175,140);
  daeBox(-230,105,1.05,{on:true,u});
  const ph=(u*.8)%1, on=ph<.3, k=on?Math.sin(ph/.3*Math.PI):0;
  if(on) fc(210,-10,60+k*110,`rgba(242,228,51,${.22*k})`);
  const b=1+Math.max(0,Math.sin(u*7))*.07; ctx.save(); ctx.translate(210,10); ctx.scale(b,b); ctx.fillStyle=RED; heartP(0,0,1.55); ctx.fill(); ctx.restore();
  if(on) bolt(210,-10,2.3,C.giallo);
},
// il DAE parla: altoparlante con le onde e fumetto con tre puntini; la legge 116/2021 con la spunta
'dae-voce'({u,A}){
  s5Dae(-190,50,.9,{on:true,u});
  const v=A(.4); s5Onde(-30,14,u,v,30);
  grp(-150,-200,1,v,()=>{ bubble(0,0,220,96,'',0,-50); for(let i=0;i<3;i++){ const k=Math.max(0,Math.sin(u*5-i*.9))*9; fc(-50+i*50,-k,13,C.navy); } });
  grp(250,-10,1,A(.85),()=>{ box(-120,-165,240,330,18,'#fff'); tx('Legge',0,-110,34,GREY,'700'); tx('116/2021',0,-62,48,C.navy,'800');
    for(let i=0;i<5;i++) box(-88,-10+i*30,176-(i%2)*44,12,6,'#cfd6e8'); });
  spunta(345,140,48,A(.92));
},
// il cartello ILCOR, la freccia verso la teca a muro che si illumina; se non sai dov'è, il 112
'cartello-dae'({u,A}){
  box(-440,-290,560,530,24,'rgba(37,46,85,.65)');
  const c=A(.4); if(c>0){ const f=(u*1.4)%1; ctx.save(); ctx.globalAlpha*=clamp(c); sbox(-260-f*14,-275-f*14,200+f*28,200+f*28,24,`rgba(242,228,51,${1-f})`,7); ctx.restore(); }
  s5Cartello(-160,-175,150);
  const ar=clamp(A(.5)); if(ar>0){ const k=Math.sin(u*5)*6; ctx.save(); ctx.globalAlpha*=ar; arrow(-160,-80+k,-160,-22+k,C.giallo,11); ctx.restore(); }
  const lit=clamp(A(.58));
  if(lit>0) fc(-160,120,150+lit*20,`rgba(242,228,51,${.14*lit*(.8+.2*Math.sin(u*4))})`);
  box(-280,5,240,230,16,'#cfd6e8'); box(-266,19,212,202,10,lit>0?`rgba(${Math.round(29+60*lit)},${Math.round(37+60*lit)},${Math.round(71+50*lit)},1)`:'#1d2547');
  daeBox(-160,125,.82,{on:lit>.5,u}); box(-266,19,212,202,10,`rgba(255,255,255,${.08+.1*lit})`); ln([[-240,40],[-200,40]],'rgba(255,255,255,.5)',5);
  grp(260,0,1,A(.85),()=>phone(0,0,.72,{num:'112',ring:true,u}));
},
// apri il coperchio, premi l'accensione, lo schermo si accende e parla
'dae-accendi'({u,A}){
  const op=clamp(A(.2)), on=A(.4)>.6, X=-70, Y=85, S=.95;
  s5Dae(X,Y,S,{lid:op,on,u,press:on&&A(.4)<1.05});
  const f=A(.4); if(f>0){ const tip=[X-80*S,Y+62*S]; const push=f<1?(1-clamp(f))*60:0; ctx.save(); ctx.globalAlpha*=clamp(f*1.5); s5Dito(tip[0]+push*.5,tip[1]+push*.8+4,.75,-.55); ctx.restore(); }
  s5Onde(X+90*S+60,Y-40*S,u,A(.8),40);
},
// analisi: traccia sullo schermo, mani alzate lontano dal torace; una mano che si avvicina è vietata
'dae-analisi'({u,A}){
  const up=Math.sin(u*2)*5;
  bust(-150,95+up*.3,.45,{divisa:true,L:POSE.up,R:mir(POSE.up),head:{mouth:'flat'}});   // soccorritore inginocchiato dietro, mani alzate
  lying(-140,215,.6,{});
  box(-210,135,44,30,6,'#fff'); box(-80,140,44,30,6,'#fff');
  ctx.strokeStyle='#e8702a'; ctx.lineWidth=6; ctx.beginPath(); ctx.moveTo(-188,140); ctx.bezierCurveTo(-170,60,80,40,150,60); ctx.moveTo(-58,145); ctx.bezierCurveTo(-30,100,90,110,150,90); ctx.stroke();
  s5Dae(260,40,.75,{on:true,ecg:true,u});
  arrow(-330,-10,-330,-110,C.giallo,8); arrow(40,-10,40,-110,C.giallo,8);
  const n=A(.7); if(n>0){ const k=(Math.sin(u*3)+1)*.5; ctx.save(); ctx.globalAlpha*=clamp(n)*.55; hand(-20,70+k*14,.4,Math.PI,SK); ctx.restore(); vieto(-20,75,68,n); }
},
// scarica: pulsante arancione che lampeggia, tutti con le mani alzate; se lo chiede, il dito lo preme e parte il lampo
'dae-scarica'({u,p,A}){
  const X=-170, Y=30, S=1.05, b=(u*3)%1<.5?1:0;
  const pr=A(.8), pressed=pr>.9;
  s5Dae(X,Y,S,{on:true,u,shock:b,shockOn:true});
  if(pressed){ const f=(u*2)%1; for(let i=0;i<10;i++){ const a=i/10*TAU+u; ln([[X+60*S+Math.cos(a)*50,Y+62*S+Math.sin(a)*50],[X+60*S+Math.cos(a)*(90+f*40),Y+62*S+Math.sin(a)*(90+f*40)]],`rgba(242,228,51,${1-f})`,8); } bolt(X-45*S,Y-30*S,1.4,C.giallo); }
  if(pr>0){ const push=pr<1?(1-clamp(pr))*70:0; ctx.save(); ctx.globalAlpha*=clamp(pr*1.5); s5Dito(X+60*S+push*.6,Y+62*S+push*.6+4,.75,-.75); ctx.restore(); }
  const h=A(.3);
  grp(185,95,1,h,()=>bust(0,0,.42,{divisa:true,L:POSE.up,R:mir(POSE.up),head:{mouth:'flat'}}));
  grp(365,95,1,h,()=>bust(0,0,.42,{shirt:'#bfc8de',shirtD:'#9aa6c4',L:POSE.up,R:mir(POSE.up),head:{mouth:'flat',hair:'long',hairCol:'#8a4a2a'}}));
},
// riprendi le compressioni con il DAE collegato; ogni 2 minuti ricontrolla
'dae-rcp'({u,A}){
  const d=24*(0.5+0.5*Math.cos(TAU*u*110/60)), X=-90, Y=230, S=.62;
  cprScene(X,Y,S,d,{shirt:DIV,shirtD:DIVD});
  box(X-180*S-20,Y-118*S+d*S-14,40,26,6,'#fff');
  ctx.strokeStyle='#e8702a'; ctx.lineWidth=6; ctx.beginPath(); ctx.moveTo(X-180*S,Y-118*S+d*S+10); ctx.bezierCurveTo(X-160*S,Y+20,200,230,300,175); ctx.stroke();
  s5Dae(330,140,.5,{on:true,u});
  grp(300,-150,1,A(.6),()=>{ timer(0,0,110,(u%4)/4,'2′',{size:64}); });
},

// ===== Posizione laterale di sicurezza =====
// 1 · gambe distese, braccio vicino ad angolo retto
'pls-1'({u,p,A}){
  const na=inOut(clamp((p-.42)/.26));
  const P=s5Pls(S5P.x,S5P.y,S5P.s,{near:na});
  const g=A(.2); if(g>0){ ctx.save(); ctx.globalAlpha*=clamp(g); ctx.setLineDash([16,12]); [P.hipFar,P.hipNear].forEach(h=>{ const a=s5Pt(S5P.x,S5P.y,S5P.s,h), b=s5Pt(S5P.x,S5P.y,S5P.s,[440,h[1]]); ln([[a[0],a[1]],[b[0],b[1]]],C.giallo,5); }); ctx.restore(); spunta(410,-140,40,g); }
  if(p>.36){ const h=s5Pt(S5P.x,S5P.y,S5P.s,P.handN); s5ManoSu(h[0]+4,h[1]+20,.42,-.3); }
  const sh=s5Pt(S5P.x,S5P.y,S5P.s,[P.shN[0],88]); s5Retto(sh[0]+30,sh[1],44,[1,0],[0,1],A(.7));
},
// 2 · l'altro braccio sul petto, il dorso della mano sulla guancia, e tienila lì
'pls-2'({u,p,A}){
  const fa=inOut(clamp((p-.25)/.4));
  const P=s5Pls(S5P.x,S5P.y,S5P.s,{near:1,far:fa});
  const g=A(.3); if(g>0){ ctx.save(); ctx.globalAlpha*=clamp(g)*(1-clamp((p-.7)/.1)); ctx.strokeStyle=C.giallo; ctx.lineWidth=9; ctx.lineCap='round'; ctx.beginPath(); ctx.moveTo(10,-150); ctx.quadraticCurveTo(-120,-210,-260,-90); ctx.stroke();
    poly([[-268,-78],[-246,-118],[-292,-104]],C.giallo); ctx.restore(); }
  const t=A(.75); if(t>0){ const h=s5Pt(S5P.x,S5P.y,S5P.s,P.handF); const f=(u*1.2)%1; ctx.save(); ctx.globalAlpha*=clamp(t); arc(h[0],h[1],34+f*26,0,TAU,`rgba(242,228,51,${1-f})`,6); ctx.restore(); grp(h[0]+8,h[1]+30,1,t,()=>s5ManoSu(0,0,.36,.15)); }
},
// 3 · afferra la gamba lontana sopra il ginocchio e piegala, piede a terra
'pls-3'({u,p,A}){
  const kn=inOut(clamp((p-.3)/.35));
  const P=s5Pls(S5P.x,S5P.y,S5P.s,{near:1,far:1,knee:kn});
  const hf=s5Pt(S5P.x,S5P.y,S5P.s,P.handF); s5ManoSu(hf[0]+8,hf[1]+30,.36,.15);
  const g=A(.3); if(g>0){ const th=[lerp(P.hipFar[0],P.knee[0],.72),lerp(P.hipFar[1],P.knee[1],.72)], w=s5Pt(S5P.x,S5P.y,S5P.s,th); grp(w[0],w[1]+26,1,g,()=>s5ManoSu(0,0,.36,-.25)); }
  // riquadro di lato: la gamba si piega e il piede resta a terra
  grp(315,-195,1.2,A(.3),()=>{ fc(0,0,88,C.tile); ln([[-78,48],[78,48]],'rgba(143,154,187,.8)',5);
    const hip=[-56,30], k=[lerp(8,-6,kn),lerp(30,-36,kn)], an=[lerp(58,30,kn),30];
    ln([hip,k],'#5664a6',22); ln([k,an],'#6f7cc0',20); box(an[0]-8,34,40,14,7,'#0d1226'); fc(hip[0],hip[1],14,'#5664a6');
    const f=A(.75); if(f>0){ const q=(u*1.3)%1; ctx.save(); ctx.globalAlpha*=clamp(f); arc(an[0]+12,42,18+q*14,0,TAU,`rgba(242,228,51,${1-q})`,5); ctx.restore(); } });
},
// 4 · tenendo la mano sulla guancia, tira la gamba e fallo rotolare verso di te; poi anca e ginocchio a 90°
'pls-4'({u,p,A}){
  const r=inOut(clamp((p-.18)/.36)), fx=inOut(clamp((p-.62)/.2));
  const P=s5Pls(S5P.x,S5P.y,S5P.s,{near:1,far:1,knee:1,roll:r,fix:fx});
  const hf=s5Pt(S5P.x,S5P.y,S5P.s,P.handF); s5ManoSu(hf[0]+8,hf[1]+30,.36,.15);
  const kp=s5Pt(S5P.x,S5P.y,S5P.s,P.knee), gp=s5Pt(S5P.x,S5P.y,S5P.s,[lerp(P.hipFar[0],P.knee[0],.62),lerp(P.hipFar[1],P.knee[1],.62)]); if(fx<1){ ctx.save(); ctx.globalAlpha*=1-fx; s5ManoSu(gp[0]+4,gp[1]+26+fx*60,.36,-.2); ctx.restore(); }
  const v=A(.5); if(v>0){ const k=Math.sin(u*4)*6; ctx.save(); ctx.globalAlpha*=clamp(v)*(1-clamp((p-.62)/.1)); ctx.strokeStyle=C.giallo; ctx.lineWidth=10; ctx.lineCap='round'; ctx.beginPath(); ctx.arc(-120,-60,110,-Math.PI*.85,-Math.PI*.15); ctx.stroke(); ctx.restore(); }
  const ar=A(.25); if(ar>0&&p<.62){ ctx.save(); ctx.globalAlpha*=clamp(ar); const f=(u*1.4)%1; arrow(kp[0]+60,kp[1]-50+f*16,kp[0]+60,kp[1]+30+f*16,C.giallo,9); ctx.restore(); }
  if(v>0&&p<.62){ ctx.save(); ctx.globalAlpha*=clamp(v); arrow(-20,-170,-20,-95,C.giallo,10); ctx.restore(); }
  const n=A(.85); if(n>0){ const h=s5Pt(S5P.x,S5P.y,S5P.s,P.hipFar); s5Retto(h[0],h[1],34,[-1,0],[0,1],n); s5Retto(kp[0],kp[1],34,[0,-1],[1,0],n); }
},

// ===== Sangue dal naso =====
// viso di profilo, una goccia rossa scende da una narice
naso({u}){
  const n=s5Profilo(-60,-40,150,{mouth:'flat'});
  ln([[n[0]-4,n[1]],[n[0]-2,n[1]+24]],RED,9);
  s5Gocce(n[0],n[1]+18,190,u,2,.55);
},
// seduto, testa leggermente in avanti: il sangue esce dal naso, in avanti, nel fazzoletto
'naso-avanti'({u,p,A}){
  const fw=clamp(A(.6)), tilt=.06+.26*fw, lean=.06+.06*fw;
  ctx.save(); ctx.translate(-30,48); ctx.scale(.82,.82);
  const se=A(.2);
  box(-240,100,210,24,10,se>.5?'#8b95b6':'#6b7491'); box(-252,-120,24,244,10,'#6b7491'); ln([[-222,124],[-222,245]],'#6b7491',14); ln([[-52,124],[-52,245]],'#6b7491',14);
  if(se>0){ ctx.save(); ctx.globalAlpha*=clamp(se); ln([[-236,96],[-36,96]],C.giallo,6); ctx.restore(); }
  ln([[-150,80],[40,86]],PANT,64); ln([[40,86],[52,228]],PANT,56); box(32,216,84,28,12,'#1a1f36');
  ctx.save(); ctx.translate(-150,80); ctx.rotate(lean);
  box(-64,-290,124,300,52,VS);
  const n=s5Profilo(8,-372,78,{tilt,mouth:'flat'});
  const hand=[n[0]+30,n[1]+64];
  ln([[0,-245],[58,-150],[hand[0]-6,hand[1]+12]],VSD,44); ln([[0,-245],[58,-150],[hand[0]-6,hand[1]+12]],VS,36);
  box(hand[0]-48,hand[1]-24,86,40,10,'#fff'); ln([[hand[0]-40,hand[1]-10],[hand[0]+30,hand[1]-10]],'rgba(27,34,63,.12)',3); fe(hand[0]-6,hand[1]-18,16,7,'rgba(217,71,61,.75)');
  fc(hand[0]-6,hand[1]+16,22,SKD); fc(hand[0]-6,hand[1]+14,19,SK);
  s5Gocce(n[0]-2,n[1]-8,hand[1]-n[1]-26,u,2,.32);
  const g=A(.6); if(g>0){ ctx.save(); ctx.globalAlpha*=clamp(g); arrow(n[0]+80,n[1]-30,n[0]+40,n[1]+30,C.giallo,9); arc(-40,-330,60,-.2,1.1,C.giallo,8); poly([[-2,-282],[8,-306],[-22,-298]],C.giallo); ctx.restore(); }
  ctx.restore(); ctx.restore();
},
// mai la testa indietro (il sangue va in gola) e mai sdraiato
'naso-no-indietro'({u,A}){
  box(-440,-240,430,450,30,C.tile); box(10,-240,430,450,30,C.tile);
  const n=s5Profilo(-250,-40,95,{tilt:-.5,mouth:'flat'});
  ctx.save(); ctx.setLineDash([10,10]); ctx.strokeStyle=RED; ctx.lineWidth=7; ctx.lineCap='round'; ctx.beginPath(); ctx.moveTo(n[0]-6,n[1]); ctx.quadraticCurveTo(n[0]-60,n[1]+10,-262,62); ctx.lineTo(-268,118); ctx.stroke(); ctx.restore();
  vieto(-225,-15,175,A(.3));
  lying(205,105,.38,{}); vieto(225,-15,175,A(.7));
},
// pollice e indice stringono la parte morbida, sotto l'osso (tratteggio); si respira con la bocca
'naso-stringi'({u,A}){
  const X=0, Y=-60, R=150;
  head(X,Y,R,{mouth:'none'});
  fe(X,Y+R*.68,R*.12,R*.15,C.navy);
  s5NasoFronte(X,Y,R);
  const so=A(.45); if(so>0){ ctx.save(); ctx.globalAlpha*=clamp(so); ctx.setLineDash([9,8]); ctx.strokeStyle='#fff'; ctx.lineWidth=5; ctx.beginPath(); ctx.moveTo(X-R*.1,Y-R*.02); ctx.lineTo(X-R*.12,Y+R*.24); ctx.lineTo(X+R*.12,Y+R*.24); ctx.lineTo(X+R*.1,Y-R*.02); ctx.stroke(); ctx.restore();
    const f=(u*1.4)%1; fe(X,Y+R*.36,R*(.26+.03*f),R*.14,`rgba(242,228,51,${.35*(1-f*.5)*clamp(so)})`); }
  const g=A(.2); if(g>0){ const sq=(Math.sin(u*3)+1)*.5*R*.015, tipY=Y+R*.34, ax=R*.22-sq;
    ctx.save(); ctx.globalAlpha*=clamp(g*1.4);
    const fin=(pts,w)=>{ ln(pts,SKD,w+7); ln(pts,SK,w); };
    fe(X+R*.42,Y+R*1.32,R*.36,R*.3,SKD); fe(X+R*.42,Y+R*1.3,R*.33,R*.27,SK);
    fin([[X+R*.6,Y+R*1.15],[X+R*.5,Y+R*.75],[X+ax,tipY]],R*.17);
    fin([[X+R*.2,Y+R*1.2],[X-R*.42,Y+R*.82],[X-ax,tipY]],R*.19);
    fe(X+ax+R*.02,tipY,R*.05,R*.06,'#f3d9c6'); ctx.restore(); }
  const b=A(.8); if(b>0){ for(let i=0;i<3;i++){ const f=(u*1.1+i/3)%1; arc(X,Y+R*.68,R*(.24+f*.5),Math.PI*.28,Math.PI*.72,`rgba(255,255,255,${(1-f*.7)*clamp(b)})`,9); } }
},
// niente cotone, garze o fazzoletti nel naso
'naso-no-cotone'({u,A}){
  const item=[
    ()=>{ [[-16,6],[12,0],[0,-14],[-4,14],[16,14]].forEach(([x,y])=>fc(x,y,18,'#fff')); fc(-6,2,14,'#eef1f7'); },
    ()=>gauze(0,0,70,58),
    ()=>{ ctx.rotate(-.25); box(-18,-40,36,80,16,'#fff'); ln([[-12,-18],[12,-28]],'rgba(27,34,63,.15)',3); ln([[-12,8],[12,-2]],'rgba(27,34,63,.15)',3); },
  ];
  [[-300,.3],[0,.6],[300,.85]].forEach(([x,t],i)=>grp(x,-30,1,A(t),()=>{
    fc(0,0,135,C.tile);
    ctx.save(); ctx.beginPath(); ctx.arc(0,0,128,0,TAU); ctx.clip();
    fe(0,-60,120,110,SK); fc(-44,-6,30,SKD); fc(44,-6,30,SKD); fc(-42,-8,27,SK); fc(42,-8,27,SK); fe(0,-14,40,34,SK);
    fe(-20,14,14,8,'#8a5444'); fe(20,14,14,8,'#8a5444'); ctx.restore();
    const k=Math.sin(u*2.4)*8; ctx.save(); ctx.translate(0,78+k); ctx.scale(1.3,1.3); item[i](); ctx.restore();
    vieto(0,0,118,A(t+.06)); }));
},
// per un giorno: niente naso soffiato con forza, niente sforzi, niente bevande calde
'naso-dopo'({u,A}){
  box(-120,-292,240,150,18,'#fff'); box(-120,-292,240,38,18,C.ciano); box(-120,-272,240,18,0,C.ciano); fc(-60,-292,9,'#cfd6e8'); fc(60,-292,9,'#cfd6e8');
  tx('24 ore',0,-196,48,C.navy,'800');
  const it=[
    ()=>{ const n=s5Profilo(-30,-6,44,{neck:false,closed:true}); box(n[0]-6,n[1]-22,40,44,8,'#fff'); for(let i=0;i<3;i++){ const f=(u*2+i/3)%1; arc(n[0]+30,n[1],18+f*36,-.6,.6,`rgba(255,255,255,${1-f})`,5); } },
    ()=>{ fe(0,22,56,50,'#59627f'); arc(0,-26,30,Math.PI*1.05,Math.PI*1.95,'#59627f',16); ln([[-28,-26],[-28,-4]],'#59627f',16); ln([[28,-26],[28,-4]],'#59627f',16); fe(-16,10,12,18,'rgba(255,255,255,.18)'); arrow(70,40,70,-40,C.giallo,7); },
    ()=>{ box(-46,-20,80,80,14,'#fff'); arc(40,18,20,-1.4,1.4,'#fff',10); for(let i=0;i<3;i++){ const k=Math.sin(u*3+i)*5; ctx.strokeStyle='rgba(255,255,255,.75)'; ctx.lineWidth=6; ctx.beginPath(); ctx.moveTo(-26+i*20,-30); ctx.quadraticCurveTo(-36+i*20+k,-50,-26+i*20,-70); ctx.quadraticCurveTo(-16+i*20-k,-88,-26+i*20,-104); ctx.stroke(); } },
  ];
  [[-300,.3],[0,.55],[300,.85]].forEach(([x,t],i)=>grp(x,70,1,A(t),()=>{ fc(0,0,115,C.tile); it[i](); vieto(0,0,102,A(t+.06)); }));
},
});
