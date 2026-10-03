// ===== Disegni animati: coordinate locali centrate su (CX,CY), area circa ±450 x ±300 =====
const SK='#eac4a6', SKD='#d3a07c', HAIR='#3b2f2b', VS='#d5dcec', VSD='#a9b4cf', RS=C.ciano, RSD='#0083b0', PANT='#2d3768', RED='#d9473d', GREY='#8f9abb';
const TAU=Math.PI*2;
function fc(x,y,r,col){ctx.fillStyle=col;ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.fill();}
function fe(x,y,rx,ry,col,rot=0){ctx.fillStyle=col;ctx.beginPath();ctx.ellipse(x,y,rx,ry,rot,0,TAU);ctx.fill();}
function ln(pts,col,w){ctx.strokeStyle=col;ctx.lineWidth=w;ctx.lineCap='round';ctx.lineJoin='round';ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]);ctx.stroke();}
function poly(pts,col){ctx.fillStyle=col;ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]);ctx.closePath();ctx.fill();}
function box(x,y,w,h,r,col){ctx.fillStyle=col;rr(ctx,x,y,w,h,r);ctx.fill();}
function sbox(x,y,w,h,r,col,lw){ctx.strokeStyle=col;ctx.lineWidth=lw;rr(ctx,x,y,w,h,r);ctx.stroke();}
function tx(s,x,y,size,col,wt='600',fam='Jost',al='center'){ctx.fillStyle=col;ctx.font=`${wt} ${size}px ${fam==='P'?'"Playfair Display"':'Jost'}`;ctx.textAlign=al;ctx.textBaseline='middle';ctx.fillText(s,x,y);}
function arc(x,y,r,a0,a1,col,w){ctx.strokeStyle=col;ctx.lineWidth=w;ctx.lineCap='round';ctx.beginPath();ctx.arc(x,y,r,a0,a1);ctx.stroke();}
function arrow(x1,y1,x2,y2,col,w=10){ln([[x1,y1],[x2,y2]],col,w);const a=Math.atan2(y2-y1,x2-x1),h=w*2.6;poly([[x2+Math.cos(a)*h*.6,y2+Math.sin(a)*h*.6],[x2+Math.cos(a+2.3)*h,y2+Math.sin(a+2.3)*h],[x2+Math.cos(a-2.3)*h,y2+Math.sin(a-2.3)*h]],col);}
function grp(x,y,s,a,fn){ if(a<=0.001) return; ctx.save(); ctx.translate(x,y); const k=Math.max(0,s*(.55+.45*a)); ctx.scale(k,k); ctx.globalAlpha*=clamp(a); fn(); ctx.restore(); }
function vieto(x,y,r,a=1){ if(a<=0) return; ctx.save(); ctx.translate(x,y); ctx.scale(.6+.4*a,.6+.4*a); ctx.globalAlpha*=clamp(a);
  ctx.strokeStyle=C.navy; ctx.lineWidth=34; ctx.beginPath(); ctx.arc(0,0,r,0,TAU); ctx.moveTo(-r*.7,-r*.7); ctx.lineTo(r*.7,r*.7); ctx.stroke();
  ctx.strokeStyle=C.giallo; ctx.lineWidth=20; ctx.beginPath(); ctx.arc(0,0,r,0,TAU); ctx.moveTo(-r*.7,-r*.7); ctx.lineTo(r*.7,r*.7); ctx.stroke(); ctx.restore(); }
function spunta(x,y,r,a=1){ if(a<=0) return; grp(x,y,1,a,()=>{ fc(0,0,r,C.giallo); ln([[-r*.45,0],[-r*.1,r*.35],[r*.5,-r*.35]],C.navy,r*.22); }); }
function ground(y,x0=-440,x1=440){ ln([[x0,y],[x1,y]],'rgba(143,154,187,.45)',6); }
function heartP(x,y,s){ ctx.beginPath(); ctx.moveTo(x,y+60*s); ctx.bezierCurveTo(x-130*s,y-20*s,x-70*s,y-130*s,x,y-60*s); ctx.bezierCurveTo(x+70*s,y-130*s,x+130*s,y-20*s,x,y+60*s); }
function bolt(x,y,s,col){ poly([[x+8*s,y-40*s],[x-18*s,y+6*s],[x,y+6*s],[x-10*s,y+40*s],[x+20*s,y-8*s],[x+2*s,y-8*s]],col); }

// ---------- testa e busto ----------
function head(x,y,r,o={}){
  if(o.hair==='long'){ fe(x,y+r*.35,r*1.12,r*1.2,o.hairCol||HAIR); }
  fc(x-r*.98,y+r*.12,r*.2,SKD); fc(x+r*.98,y+r*.12,r*.2,SKD);
  fc(x,y,r,o.pale?'#f1dccd':SK);
  ctx.fillStyle=o.hairCol||HAIR; ctx.beginPath(); ctx.arc(x,y,r*1.03,Math.PI,0); ctx.bezierCurveTo(x+r*.95,y-r*.3,x-r*.3,y-r*.75,x-r*1.03,y); ctx.fill();
  if(o.glasses){ ctx.strokeStyle=C.navy; ctx.lineWidth=r*.06; ctx.beginPath(); ctx.arc(x-r*.36,y+r*.08,r*.2,0,TAU); ctx.moveTo(x+r*.56,y+r*.08); ctx.arc(x+r*.36,y+r*.08,r*.2,0,TAU); ctx.moveTo(x-r*.16,y+r*.08); ctx.lineTo(x+r*.16,y+r*.08); ctx.stroke(); }
  const d=o.droop||0;
  if(o.closed){ ln([[x-r*.48,y+r*.08],[x-r*.24,y+r*.08]],C.navy,r*.07); ln([[x+r*.24,y+r*.08],[x+r*.48,y+r*.08]],C.navy,r*.07); }
  else { fc(x-r*.36,y+r*.08,r*.085,C.navy); fc(x+r*.36,y+r*.08,r*.085,C.navy);
    if(d>0){ ctx.fillStyle=o.pale?'#f1dccd':SK; ctx.fillRect(x-r*.5,y+r*.08-r*.12,r*.28,r*.12*d*1.4); } }
  ctx.strokeStyle=C.navy; ctx.lineWidth=r*.07; ctx.lineCap='round';
  const m=o.mouth||'smile';
  if(m==='smile'){ ctx.beginPath(); ctx.moveTo(x-r*.34,y+r*.42+d*r*.3); ctx.quadraticCurveTo(x+d*r*.14,y+r*.72-d*r*.12,x+r*.34,y+r*.42); ctx.stroke(); }
  if(m==='flat'){ ctx.beginPath(); ctx.moveTo(x-r*.24,y+r*.52); ctx.lineTo(x+r*.24,y+r*.52); ctx.stroke(); }
  if(m==='sad'){ ctx.beginPath(); ctx.moveTo(x-r*.26,y+r*.6); ctx.quadraticCurveTo(x,y+r*.4,x+r*.26,y+r*.6); ctx.stroke(); }
  if(m==='o'){ fe(x,y+r*.52,r*.13,r*.17,C.navy); }
  if(m==='lips'){ fe(x,y+r*.5,r*(.22+.12*(o.swell||0)),r*(.08+.08*(o.swell||0)),'#c4575a'); }
  if(!o.pale){ fe(x-r*.58,y+r*.36,r*.13,r*.08,'rgba(222,120,110,.28)'); fe(x+r*.58,y+r*.36,r*.13,r*.08,'rgba(222,120,110,.28)'); }
}
function arm(sx,sy,pts,col,dk,w,hand=true){ const P=[[sx,sy],...pts]; ln(P,dk,w+8); ln(P,col,w); if(hand){ const h=pts[pts.length-1]; fc(h[0],h[1],w*.52,SKD); fc(h[0],h[1],w*.46,SK);} }
const POSE={ down:[[-170,80],[-168,215]], up:[[-200,-150],[-195,-320]], chest:[[-150,110],[-10,30]], throat:[[-150,40],[-34,-112]], mouth:[[-160,40],[-40,-170]], hip:[[-170,80],[-168,215]] };
function mir(p){ return p.map(q=>[-q[0],q[1]]); }
// busto frontale: (x,y) = centro del petto
function bust(x,y,s,o={}){
  const sh=o.shirt||VS, sd=o.shirtD||VSD;
  ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  if(o.jx) ctx.translate(o.jx,0);
  box(-30,-140,60,70,10,SKD);
  ctx.fillStyle=sh; ctx.beginPath(); ctx.moveTo(-150,280); ctx.lineTo(-150,-20); ctx.quadraticCurveTo(-150,-85,-85,-88); ctx.lineTo(85,-88); ctx.quadraticCurveTo(150,-85,150,-20); ctx.lineTo(150,280); ctx.closePath(); ctx.fill();
  poly([[-34,-88],[0,-40],[34,-88]],SKD);
  if(o.under) o.under();
  head(0,-205,100,o.head||{});
  const L=o.L||POSE.down, R=o.R||mir(POSE.down);
  if(!o.noArms){ arm(-122,-50,L,sh,sd,54); arm(122,-50,R,sh,sd,54); }
  if(o.over) o.over();
  ctx.restore();
}
// persona sdraiata supina, (x,y): x = petto, y = terreno
function lying(x,y,s,o={}){
  ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  const d=o.d||0, rise=o.rise||0;
  const legEnd = o.legsUp? [470,-215] : [500,-48];
  ln([[190,-58],legEnd],PANT,84);
  ctx.save(); ctx.translate(legEnd[0],legEnd[1]); ctx.rotate(o.legsUp?-0.45:0); box(8,-78,36,92,12,'#1a1f36'); ctx.restore();
  box(110,-112,130,104,30,PANT);
  box(-215,-118+d-rise,350,110-d+rise,40,o.shirt||VS);
  box(-262,-82,60,46,12,SKD);
  fc(-290,-66,66,SK);
  ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(-290,-66,69,Math.PI*.5,Math.PI*1.38); ctx.bezierCurveTo(-330,-110,-345,-40,-290,3); ctx.fill();
  fc(-300,-62,13,SKD);
  fe(-262,-134,12,10,SK);
  ln([[-276,-104],[-256,-106]],C.navy,6); ln([[-246,-80],[-236,-62]],'rgba(27,34,63,.55)',5);
  ln([[-150,-40],[60,-34]],o.shirtD||VSD,30); fc(78,-34,18,SK);
  if(o.blanket){ const b=o.blanket; ctx.save(); ctx.beginPath(); ctx.rect(560-b*800,-250,b*800+40,260); ctx.clip();
    ctx.fillStyle=C.arancio; rr(ctx,-190,-150,760,148,40); ctx.fill(); ctx.fillStyle='rgba(255,255,255,.25)'; for(let i=0;i<6;i++) ctx.fillRect(-150+i*120,-150,24,148); ctx.restore(); }
  ctx.restore();
}
// soccorritore visto di fronte, dietro la vittima: braccia tese al petto (hx,hy)
function rescuerBack(hx,hy,s,d,o={}){
  const sx=hx, sy=hy-250*s+d;
  ctx.save(); ctx.translate(sx,sy); ctx.scale(s,s);
  box(-30,-105,60,60,10,SKD);
  ctx.fillStyle=o.shirt||RS; ctx.beginPath(); ctx.moveTo(-135,260); ctx.lineTo(-135,10); ctx.quadraticCurveTo(-135,-60,-80,-62); ctx.lineTo(80,-62); ctx.quadraticCurveTo(135,-60,135,10); ctx.lineTo(135,260); ctx.closePath(); ctx.fill();
  ctx.fillStyle=C.giallo; ctx.fillRect(-135,120,270,22); ctx.fillStyle='#fff'; ctx.fillRect(-135,142,270,8);
  head(0,-170,86,o.head||{mouth:'flat'});
  ctx.restore();
}
function rescuerArms(hx,hy,s,d,o={}){
  const sy=hy-250*s+d;
  arm(hx-105*s,sy-20*s,[[hx-40*s,lerp(sy,hy,.55)],[hx-6*s,hy-14*s]],o.shirt||RS,o.shirtD||RSD,48*s,false);
  arm(hx+105*s,sy-20*s,[[hx+40*s,lerp(sy,hy,.55)],[hx+6*s,hy-14*s]],o.shirt||RS,o.shirtD||RSD,48*s,false);
  fe(hx,hy-10*s,44*s,24*s,SKD); fe(hx,hy-20*s,40*s,22*s,SK);
}
function cprScene(x,y,s,d,o={}){
  const hy=y-118*s+d*s;
  rescuerBack(x,hy,s,d*s,o);
  lying(x,y,s,{d,shirt:o.vShirt});
  rescuerArms(x,hy,s,d*s,o);
}
// posizione laterale di sicurezza
function pls(x,y,s,breath=0){
  ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  ln([[-200,-30],[-400,-22]],VS,46); fc(-410,-22,22,SK);
  ln([[140,-46],[440,-34]],PANT,70); box(430,-80,34,70,10,'#1a1f36');
  box(-235,-150-breath,330,140+breath,50,VS);
  box(60,-140,140,128,36,PANT);
  ln([[150,-100],[290,-10],[400,-70]],'#3a4580',72);
  box(-300,-110,56,48,12,SKD);
  fc(-330,-100,62,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(-330,-100,64,Math.PI*1.05,Math.PI*1.95); ctx.fill();
  ln([[-352,-92],[-330,-92]],C.navy,6); ln([[-308,-92],[-290,-92]],C.navy,6);
  ln([[-160,-120],[-230,-60],[-300,-44]],VSD,52); ln([[-160,-120],[-230,-60],[-300,-44]],VS,44); fc(-305,-42,24,SK);
  ctx.restore();
}
// figura in piedi di profilo (rivolta a sinistra)
function sideFig(hx,hy,s,o={}){
  const lean=o.lean||0, sh=o.shirt||VS, sd=o.shirtD||VSD;
  ctx.save(); ctx.translate(hx,hy); ctx.scale(s,s);
  ln([[0,0],[-10,200]],PANT,58); ln([[16,0],[24,200]],'#262f5a',58); box(-50,190,70,26,12,'#1a1f36'); box(-10,192,62,24,12,'#1a1f36');
  ctx.rotate(-lean);
  if(o.backArm) o.backArm();
  box(-62,-300,124,320,52,sh);
  box(-26,-345,52,60,10,SKD);
  fc(-6,-400,72,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(-6,-400,74,Math.PI*1.25,Math.PI*0.45); ctx.fill();
  fc(-50,-405,8,C.navy); fe(-82,-392,10,8,SKD);
  if(o.mouth==='o') fe(-62,-368,9,11,C.navy); else ln([[-66,-370],[-48,-372]],C.navy,6);
  if(o.frontArm) o.frontArm();
  ctx.restore();
}
// ---------- oggetti ----------
function phone(x,y,s,o={}){
  ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  box(-100,-190,200,380,34,'#0d1226'); sbox(-100,-190,200,380,34,'#3a4570',6);
  box(-84,-170,168,320,20,'#24305c');
  const num=o.num??'112'; tx(num,0,-80,78,'#fff','800');
  tx(o.label||'Chiamata in corso',0,-20,22,'#aab3cc','500');
  fc(0,90,36,'#2fbf71'); ctx.save(); ctx.translate(0,90); ctx.rotate(-0.6); box(-20,-8,40,16,8,'#fff'); ctx.restore();
  if(o.ring){ for(let i=0;i<3;i++){ const r=((o.u*1.2+i/3)%1); arc(120,-150,30+r*70,-0.9,0.4,`rgba(242,228,51,${1-r})`,8);} }
  if(o.speaker){ grp(0,30,1,o.speaker,()=>{ poly([[-34,-14],[-18,-14],[0,-30],[0,30],[-18,14],[-34,14]],C.giallo); arc(6,0,20,-0.8,0.8,C.giallo,5); arc(6,0,34,-0.8,0.8,C.giallo,5); }); }
  ctx.restore();
}
function timer(x,y,r,frac,label,o={}){
  fc(x,y,r,C.tile); arc(x,y,r-10,0,TAU,'rgba(242,228,51,.2)',14);
  arc(x,y,r-10,-Math.PI/2,-Math.PI/2+TAU*clamp(frac),C.giallo,14);
  box(x-14,y-r-26,28,22,6,C.giallo);
  tx(label,x,y+(o.sub?-10:4),o.size||r*.5,'#fff','800');
  if(o.sub) tx(o.sub,x,y+r*.36,r*.2,'#aab3cc','600');
}
function clockFace(x,y,r,h,m){
  fc(x,y,r,'#fff'); arc(x,y,r-6,0,TAU,C.navy,8);
  for(let i=0;i<12;i++){ const a=i/12*TAU; ln([[x+Math.cos(a)*r*.78,y+Math.sin(a)*r*.78],[x+Math.cos(a)*r*.88,y+Math.sin(a)*r*.88]],C.navy,5); }
  const ah=(h%12+m/60)/12*TAU-Math.PI/2, am=m/60*TAU-Math.PI/2;
  ln([[x,y],[x+Math.cos(ah)*r*.5,y+Math.sin(ah)*r*.5]],C.navy,10); ln([[x,y],[x+Math.cos(am)*r*.72,y+Math.sin(am)*r*.72]],C.navy,7); fc(x,y,9,C.arancio);
}
function daeBox(x,y,s,o={}){
  ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  box(-110,-90,220,180,30,C.giallo); box(-90,-70,180,95,16,'#fff');
  ctx.fillStyle=RED; heartP(-30,-18,.42); ctx.fill(); bolt(-30,-24,.7,'#fff');
  tx('DAE',40,-22,44,C.navy,'800');
  fc(-50,58,16,o.on?'#2fbf71':'#6b7491'); box(0,46,70,24,10,C.navy);
  if(o.on&&o.u!=null&&(o.u*2%1)<.5) fc(-50,58,24,'rgba(47,191,113,.35)');
  ctx.restore();
}
function glass(x,y,s,fill=.7,col='#9fd8f0'){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  ctx.save(); ctx.beginPath(); ctx.moveTo(-50,-80); ctx.lineTo(50,-80); ctx.lineTo(40,80); ctx.lineTo(-40,80); ctx.closePath(); ctx.clip(); ctx.fillStyle=col; ctx.fillRect(-60,80-160*fill,120,170); ctx.restore();
  ctx.strokeStyle='#fff'; ctx.lineWidth=8; ctx.lineJoin='round'; ctx.beginPath(); ctx.moveTo(-50,-80); ctx.lineTo(-40,80); ctx.lineTo(40,80); ctx.lineTo(50,-80); ctx.stroke(); ctx.restore(); }
function pill(x,y,s,rot=-.6){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s); box(-70,-28,140,56,28,'#fff'); ctx.save(); ctx.beginPath(); ctx.rect(0,-30,80,60); ctx.clip(); box(-70,-28,140,56,28,C.ciano); ctx.restore(); ctx.restore(); }
function sandwich(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-80,-40,160,40,20,'#e9b871'); box(-86,-6,172,14,7,'#7cc46a'); box(-84,6,168,16,8,'#d9655a'); box(-80,20,160,36,18,'#e9b871'); ctx.restore(); }
function gauze(x,y,w,h,col='#fff'){ box(x-w/2,y-h/2,w,h,10,col); ctx.strokeStyle='rgba(27,34,63,.12)'; ctx.lineWidth=3; for(let i=1;i<4;i++){ ctx.beginPath(); ctx.moveTo(x-w/2+i*w/4,y-h/2); ctx.lineTo(x-w/2+i*w/4,y+h/2); ctx.stroke(); } }
function forearm(y,o={}){ ln([[-430,y],[260,y]],o.sleeve||VS,110); ln([[-60,y],[300,y+4]],SK,96); fe(330,y+8,62,52,SK); ln([[340,y-30],[400,y-34]],SK,30); }
function handTop(x,y,s,o={}){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ln([[0,-60],[0,-230]],o.sleeve||RS,86); box(-62,-80,124,110,44,o.glove||SK);
  for(let i=0;i<4;i++) box(-58+i*30,-6,26,74-Math.abs(i-1.5)*10,13,o.glove||SK); box(54,-60,26,64,13,o.glove||SK); ctx.restore(); }
function drop(x,y,s,col=RED){ ctx.fillStyle=col; ctx.beginPath(); ctx.moveTo(x,y-40*s); ctx.bezierCurveTo(x+30*s,y-5*s,x+30*s,y+28*s,x,y+28*s); ctx.bezierCurveTo(x-30*s,y+28*s,x-30*s,y-5*s,x,y-40*s); ctx.fill(); }
function car(x,y,s,col='#6b7491'){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-150,-50,300,80,24,col); poly([[-90,-50],[-55,-110],[60,-110],[100,-50]],col); poly([[-75,-55],[-48,-98],[0,-98],[0,-55]],'#cfe9f5'); poly([[12,-55],[12,-98],[52,-98],[82,-55]],'#cfe9f5'); fc(-85,32,30,'#1a1f36'); fc(85,32,30,'#1a1f36'); fc(-85,32,12,'#aab3cc'); fc(85,32,12,'#aab3cc'); ctx.restore(); }
function ambulance(x,y,s,u){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  box(-200,-150,280,180,20,'#fff'); poly([[80,-110],[150,-110],[200,-40],[200,30],[80,30]],'#fff'); poly([[96,-96],[146,-96],[184,-44],[96,-44]],'#cfe9f5');
  ctx.fillStyle=C.arancio; ctx.fillRect(-200,-30,400,22); ctx.fillStyle=C.ciano; ctx.fillRect(-200,-8,400,14);
  box(-110,-120,60,60,8,RED); ctx.fillStyle='#fff'; ctx.fillRect(-88,-112,16,44); ctx.fillRect(-102,-98,44,16);
  const on=(u*3%1)<.5; box(-40,-176,70,28,10,on?'#3aa0ff':'#24305c'); if(on) fc(-5,-162,46,'rgba(58,160,255,.25)');
  fc(-120,36,34,'#1a1f36'); fc(120,36,34,'#1a1f36'); fc(-120,36,14,'#aab3cc'); fc(120,36,14,'#aab3cc'); ctx.restore(); }
function bottle(x,y,s,col='#3a8d6c',lab='#fff'){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-60,-70,120,170,24,col); box(-24,-120,48,56,8,col); box(-30,-140,60,26,8,'#fff'); box(-46,-20,92,60,8,lab); ctx.restore(); }
function eye(x,y,s,pup=1,o={}){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.fillStyle='#fff'; ctx.beginPath(); ctx.moveTo(-110,0); ctx.quadraticCurveTo(0,-90,110,0); ctx.quadraticCurveTo(0,90,-110,0); ctx.fill();
  fc(0,0,46,o.iris||'#5b8fb9'); fc(0,0,18*pup,'#0d1226'); fc(14,-14,8,'#fff'); ctx.strokeStyle=C.navy; ctx.lineWidth=8; ctx.beginPath(); ctx.moveTo(-110,0); ctx.quadraticCurveTo(0,-90,110,0); ctx.quadraticCurveTo(0,90,-110,0); ctx.stroke(); ctx.restore(); }
function steto(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.strokeStyle='#cfd6e8'; ctx.lineWidth=14; ctx.lineCap='round';
  ctx.beginPath(); ctx.moveTo(-60,-120); ctx.lineTo(-60,-30); ctx.quadraticCurveTo(-60,40,0,40); ctx.quadraticCurveTo(60,40,60,-30); ctx.lineTo(60,-120); ctx.moveTo(0,40); ctx.quadraticCurveTo(0,140,90,130); ctx.stroke(); fc(110,130,34,'#cfd6e8'); fc(110,130,18,C.navy); ctx.restore(); }
function cross(x,y,s,col=C.giallo){ ctx.fillStyle=col; ctx.fillRect(x-18*s,y-56*s,36*s,112*s); ctx.fillRect(x-56*s,y-18*s,112*s,36*s); }
function leg(x,y,s,o={}){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ln([[-420,0],[40,0]],o.col||PANT,150); ln([[40,0],[380,20]],o.col||PANT,118); box(360,-60,90,110,26,'#1a1f36'); ctx.restore(); }
function cube(x,y,s,col='#fff'){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); poly([[-40,-20],[0,-40],[40,-20],[0,0]],col); poly([[-40,-20],[0,0],[0,46],[-40,26]],'#e3e7f1'); poly([[40,-20],[0,0],[0,46],[40,26]],'#c3cadc'); ctx.restore(); }
function bubble(x,y,w,h,txt,size,tailX){ box(x-w/2,y-h/2,w,h,30,'#fff'); poly([[tailX-20,y+h/2-4],[tailX+20,y+h/2-4],[tailX-30,y+h/2+40]],'#fff'); if(txt) tx(txt,x,y,size,C.navy,'600'); }

// ---------- metronomo RCP ----------
function compAt(u){ // profondità 0..1 della compressione al tempo u della scena
  if(!CONTA.beat) return 0.5+0.5*Math.cos(TAU*(u*110/60));
  const tc=u-CONTA.at, b=CONTA.beat, n=CONTA.n;
  if(tc<-b/2 || tc>(n-1)*b+b/2) return 0;
  return 0.5+0.5*Math.cos(TAU*tc/b);
}

const ILL = {
fine(){},
cervello({u}){
  const c=ctx; ctx.strokeStyle='#fff'; ctx.lineWidth=14; ctx.lineCap='round';
  c.beginPath(); c.arc(-70,-30,130,Math.PI*.55,Math.PI*1.95); c.stroke(); c.beginPath(); c.arc(60,-35,130,Math.PI*1.05,Math.PI*.45); c.stroke();
  c.beginPath(); c.moveTo(-5,-160); c.bezierCurveTo(-30,-80,25,-30,-5,80); c.stroke();
  c.beginPath(); c.moveTo(-150,-40); c.quadraticCurveTo(-95,-70,-75,-15); c.moveTo(120,-55); c.quadraticCurveTo(70,-30,80,25); c.stroke();
  const f=(u*2)%1; fc(-40,-60,16+f*40,`rgba(242,228,51,${.6*(1-f)})`); fc(-40,-60,14,C.giallo);
  const ox=170, oy=140; fc(ox,oy,95,C.navy); arc(ox,oy,95,0,TAU,C.giallo,12); ln([[ox-18,oy-118],[ox+18,oy-118]],C.giallo,12);
  const an=-Math.PI/2+u*1.2; ln([[ox,oy],[ox+Math.cos(an)*68,oy+Math.sin(an)*68]],C.giallo,12);
},
viso({u,p,A}){
  const d=clamp((p-.55)/.25); bust(0,170,.95,{head:{mouth:'smile',droop:d},noArms:false});
  if(d>.3){ const r=30+Math.sin(u*6)*4; ctx.save(); ctx.translate(0,170); ctx.scale(.95,.95); arc(-34,-205+42+30,r+20,0,TAU,C.giallo,7); ctx.restore();
    grp(-300,-40,1,A(.75),()=>{ arrow(0,0,190,110,C.giallo,10); }); }
},
braccia({u,p}){
  const d=clamp((p-.55)/.3);
  const L=[[lerp(-200,-215,d),lerp(-150,-40,d)],[lerp(-195,-245,d),lerp(-320,-150,d)]];
  bust(0,210,.82,{L, R:mir(POSE.up), head:{mouth:'flat'}});
  if(d>.15){ ctx.save(); ctx.setLineDash([16,14]); arc(-120,0,190,-Math.PI*.62-0.7*d,-Math.PI*.62,C.giallo,7); ctx.restore(); }
},
parola({u,p}){
  bust(-250,190,.7,{head:{mouth:(u*5%1)<.5?'o':'flat'}});
  const bad=p>.5; const frase=bad?'Oggi è ... bel ... gior...':'Oggi è una bella giornata';
  const wob=bad?Math.sin(u*14)*5:0;
  bubble(150+wob,-120,500,170,'',0,30);
  ctx.save(); ctx.beginPath(); ctx.rect(-100,-200,500,170); ctx.clip();
  const shown=frase.slice(0,Math.floor(clamp((p%.5)/.3)*frase.length+1));
  tx(bad?shown.replace(/[aeiou]/g,(m,i)=>hash(i+Math.floor(u*6))>.6?'?':m):shown,150+wob,-120,40,bad?RED:C.navy,'600');
  ctx.restore();
},
'altri-ictus'({u,A}){
  [[-300,.2],[0,.45],[300,.7]].forEach(([x,t],i)=>grp(x,0,1,A(t),()=>{
    fc(0,0,130,C.tile); arc(0,0,130,0,TAU,C.giallo,6);
    if(i===0){ eye(0,0,.9); ctx.save(); ctx.beginPath(); ctx.rect(-110,-80,110,160); ctx.clip(); fc(0,0,120,'rgba(13,18,38,.85)'); ctx.restore(); }
    if(i===1){ ctx.save(); ctx.rotate(Math.sin(u*3)*.35); ln([[0,60],[0,-20]],'#fff',22); fc(0,-50,24,SK); ln([[-50,10],[0,-10],[50,10]],'#fff',16); ln([[0,60],[-25,100]],'#fff',16); ln([[0,60],[25,100]],'#fff',16); ctx.restore(); ln([[-80,105],[80,105]],GREY,6); }
    if(i===2){ fc(0,10,70,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(0,10,72,Math.PI,0); ctx.fill(); ln([[-26,24],[-12,20]],C.navy,6); ln([[12,20],[26,24]],C.navy,6); ln([[-14,52],[14,48]],C.navy,6); const f=(u*3%1)<.5; bolt(40,-70,f?1.3:1.1,C.giallo); }
  }));
},
'telefono-ora'({u,p,A}){
  phone(-200,0,1,{num:'112'.slice(0,Math.min(3,Math.floor(p*12))),ring:p>.3,u});
  grp(190,-40,1,A(.6),()=>{ clockFace(0,0,120,10,42); box(-120,150,240,70,20,'#fff'); tx('Iniziato alle 10:42',0,185,26,C.navy,'700'); });
},
'no-bocca'({A}){
  [[-300,.15,()=>sandwich(0,0,1.1)],[0,.3,()=>glass(0,0,1)],[300,.5,()=>pill(0,0,1.1)]].forEach(([x,t,f])=>grp(x,0,1,A(t),()=>{ fc(0,0,130,C.tile); f(); vieto(0,0,115,A(t+.08)); }));
},
pls({u,A}){ pls(30,150,1,Math.sin(u*2.4)*5); grp(-260,-170,1,A(.6),()=>{ for(let i=0;i<3;i++){ const r=(u*.8+i/3)%1; arc(0,0,20+r*60,-0.6,0.6,`rgba(0,165,220,${1-r})`,6);} }); },
cuore({u}){
  const b=1+Math.max(0,Math.sin(u*7))*.06; ctx.strokeStyle=C.giallo; ctx.lineWidth=16; heartP(0,0,1.9*b); ctx.stroke();
  ctx.save(); ctx.beginPath(); ctx.rect(-320,-200,640*clamp(u/1.4),400); ctx.clip();
  ln([[-320,10],[-110,10],[-70,-80],[-30,100],[20,-160],[60,10],[320,10]],C.ciano,12); ctx.restore();
},
dolore({u,p,A}){
  bust(0,190,.8,{R:[[150,110],[14,40]],head:{mouth:'sad',sweat:0}});
  const pulse=.5+.5*Math.sin(u*6);
  ctx.save(); ctx.translate(0,190); ctx.scale(.8,.8);
  fc(-30,20,70+pulse*30,`rgba(217,71,61,${.35+.2*pulse})`); fc(-30,20,40,'rgba(217,71,61,.85)');
  const Z=[[.55,[-230,120],'arm'],[.65,[0,-140],'jaw'],[.75,[-110,200],'back'],[.85,[40,170],'stom']];
  Z.forEach(([t,[x,y]])=>{ const a=A(t); if(a<=0) return; ctx.save(); ctx.globalAlpha*=clamp(a);
    ctx.setLineDash([14,12]); ln([[-30,20],[x,y]],'rgba(242,228,51,.8)',6); ctx.setLineDash([]); fc(x,y,(26+pulse*10)*a,'rgba(217,71,61,.75)'); ctx.restore(); });
  ctx.restore();
},
sudore({u,A}){
  const pale=A(.5)>0.3;
  bust(0,190,.8,{head:{mouth:'sad',pale},over(){ for(let i=0;i<5;i++){ const yy=-300+((u*90+i*37)%120); drop(-90+i*45,yy,.35,C.ciano); } }});
  grp(250,-80,1,A(.4),()=>{ ctx.strokeStyle='#7cc46a'; ctx.lineWidth=8; ctx.beginPath(); for(let a=0;a<14;a+=.2){ const r=a*4; ctx.lineTo(Math.cos(a+u*3)*r,Math.sin(a+u*3)*r);} ctx.stroke(); });
  grp(-260,-80,1,A(.6),()=>{ for(let i=0;i<3;i++){ const f=(u*1.5+i/3)%1; arc(60-f*80,0,30+i*14,Math.PI*.7,Math.PI*1.3,`rgba(255,255,255,${1-f})`,6);} });
},
'tre-persone'({A}){
  grp(-300,40,1,A(.2),()=>bust(0,40,.55,{head:{hair:'long',mouth:'flat'},shirt:'#f3b9c4',shirtD:'#d98fa0'}));
  grp(0,40,1,A(.3),()=>bust(0,40,.55,{head:{hairCol:'#c9ccd4',glasses:true,mouth:'flat'},shirt:'#bfc8de'}));
  grp(300,40,1,A(.42),()=>{ bust(0,40,.55,{head:{mouth:'flat'},shirt:'#9fd8c0',shirtD:'#6fb89a'}); box(70,90,90,120,16,'#fff'); box(82,104,66,44,8,'#24305c'); tx('LO',115,126,26,C.giallo,'800'); });
},
'telefono-timer'({u,p,A}){
  const m=Math.min(5,Math.floor(p*9)); timer(-190,0,150,p*1.6,m+'′',{sub:'minuti'});
  grp(200,0,1,A(.55),()=>phone(0,0,.95,{ring:true,u}));
},
ambulanza({u,A}){
  ln([[-440,170],[440,170]],'#3a4570',10); for(let i=0;i<6;i++){ const x=((i*180-u*400)%1080+1080)%1080-540; ln([[x,200],[x+80,200]],'rgba(255,255,255,.35)',8); }
  grp(-250,-120,1,A(.1),()=>{ car(0,0,.8); vieto(0,-30,120,A(.2)); });
  grp(170,90,1,A(.5),()=>ambulance(0,0,1,u));
},
seduto({u,A}){
  ctx.save(); ctx.translate(40,70); ctx.scale(.82,.82);
  box(-120,60,260,30,12,'#6b7491'); box(110,-200,30,260,12,'#6b7491'); ln([[-100,90],[-100,250]],'#6b7491',16); ln([[120,90],[120,250]],'#6b7491',16);
  ln([[60,30],[-120,40],[-130,230]],PANT,64); box(-180,220,80,28,12,'#1a1f36');
  ctx.save(); ctx.translate(60,40); ctx.rotate(.18); box(-60,-300,124,320,52,VS); box(-26,-345,52,60,10,SKD);
  fc(-6,-400,72,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(-6,-400,74,Math.PI*1.25,Math.PI*.45); ctx.fill(); fc(-50,-405,8,C.navy); fe(-82,-392,10,8,SKD); ln([[-66,-370],[-48,-372]],C.navy,6);
  grp(-20,-270,1,A(.45),()=>{ arc(0,0,40,.3,2.8,C.giallo,7); });
  ln([[-10,-250],[-60,-120],[-130,-90]],VSD,50); ln([[-10,-250],[-60,-120],[-130,-90]],VS,42); fc(-136,-88,22,SK);
  ctx.restore();
  if(CFG.nome==='Infarto') grp(-320,-150,1,A(.85),()=>{ phone(0,0,.55,{num:'112',label:'Operatore'}); });
  const b=(u*.6)%1; arc(-110,-280,30+b*40,Math.PI*.8,Math.PI*1.2,`rgba(255,255,255,${1-b})`,6);
  ctx.restore();
},
'rcp-mini'({u,A}){
  const d=24*(0.5+0.5*Math.cos(TAU*u*110/60));
  cprScene(-60,220,.62,d);
  grp(330,120,1,A(.75),()=>daeBox(0,0,.75,{on:true,u}));
},
goccia({u}){
  const f=(u*1.2)%1; drop(0,-20,4.2); fe(-40,-60,18,34,'rgba(255,255,255,.35)',-.4);
  drop(0,170+f*80,.9*(1-f*.3),`rgba(217,71,61,${1-f})`);
},
guanti({p,A}){
  [[-170,-.15],[170,.15]].forEach(([x,r],i)=>{ ctx.save(); ctx.translate(x,40); ctx.rotate(r); ctx.scale(i?-1:1,1);
    const g=clamp((p-i*.15)/.5);
    const draw=(col)=>{ box(-80,-60,160,190,60,col); for(let j=0;j<4;j++) box(-76+j*40,-200+Math.abs(j-1.5)*18,34,170,17,col); ctx.save(); ctx.translate(80,10); ctx.rotate(-.7); box(-18,-110,36,120,18,col); ctx.restore(); };
    draw(SK); ctx.save(); ctx.beginPath(); ctx.rect(-200,250-g*470,400,470); ctx.clip(); draw('#7b6fd6'); ctx.restore();
    box(-90,120,180,90,20,'#7b6fd6'); ctx.restore(); });
},
premi({u,p,A}){
  forearm(120);
  const g=A(.3), pr=A(.7); const push=pr>0? 8+Math.sin(u*5)*6:0;
  if(g<.5){ fe(60,110,44,26,RED); const f=(u*1.5)%1; drop(60,170+f*60,.6,`rgba(217,71,61,${1-f})`); }
  if(g>0) grp(60,100,1,g,()=>gauze(0,0,170,110));
  if(pr>0) grp(60,90+push,1,pr,()=>{ handTop(0,0,1); });
  if(pr>.5){ arrow(-120,-170,-120,-80,C.giallo,10); arrow(240,-170,240,-80,C.giallo,10); }
},
'premi-timer'({u,p,A}){
  ctx.save(); ctx.translate(-170,40); ctx.scale(.7,.7); forearm(120); gauze(60,100,170,110); handTop(60,98+Math.sin(u*5)*6,1); ctx.restore();
  timer(250,-20,150,p,Math.min(10,Math.floor(p*10)+1)+'′',{sub:'minuti'});
  vieto(250,-20,0,0);
},
garze({u,p,A}){
  forearm(120); gauze(60,100,170,110); ctx.save(); ctx.globalAlpha*=clamp(p*3); fe(60,100,50+p*40,30+p*20,'rgba(217,71,61,.55)'); ctx.restore();
  const g2=A(.45); if(g2>0){ ctx.save(); ctx.translate(70,85-(1-clamp(g2))*200); ctx.rotate(.12); gauze(0,0,180,115); ctx.restore(); }
  const pr=A(.75); if(pr>0) grp(65,80+Math.sin(u*5)*6,1,pr,()=>handTop(0,0,1));
},
oggetto({u,A}){
  forearm(130); fe(40,120,40,24,RED);
  ctx.save(); ctx.translate(40,110); ctx.rotate(-.5); box(-10,-180,20,190,6,'#aab3cc'); ctx.restore();
  const g=A(.4); if(g>0){ grp(-50,115,1,g,()=>gauze(0,0,80,90)); grp(130,115,1,g,()=>gauze(0,0,80,90)); }
  const pr=A(.75); if(pr>0){ const s=Math.sin(u*5)*5; grp(-60,100+s,.8,pr,()=>handTop(0,0,.8)); grp(140,100+s,.8,pr,()=>handTop(0,0,.8)); }
  vieto(300,-140,80,A(.3)); ctx.save(); ctx.globalAlpha*=clamp(A(.3)); ctx.translate(300,-140); ctx.rotate(-.5); box(-6,-50,12,100,4,'#aab3cc'); ctx.restore(); vieto(300,-140,80,A(.3));
},
'telefono-premi'({u,p,A}){
  ctx.save(); ctx.translate(-190,60); ctx.scale(.6,.6); forearm(120); gauze(60,100,170,110); handTop(60,98+Math.sin(u*5)*6,1); ctx.restore();
  phone(230,0,.95,{ring:true,u,speaker:A(.6)});
},
laccio({u,p,A}){
  leg(-30,60,1,{col:SK});
  fe(150,40,40,26,RED);
  const b=A(.3); if(b>0) grp(-60,60,1,b,()=>{ box(-36,-90,72,180,16,'#1a1f36'); ctx.save(); ctx.rotate(Math.min(1,p*2)*Math.PI*1.5); box(-90,-10,180,20,8,'#cfd6e8'); ctx.restore(); });
  const m=A(.7); if(m>0) grp(45,-110,1,m,()=>{ ln([[-90,0],[90,0]],C.giallo,6); ln([[-90,-16],[-90,16]],C.giallo,6); ln([[90,-16],[90,16]],C.giallo,6); tx('5-7 cm',0,-40,36,C.giallo,'700'); });
  const n=A(.9); if(n>0) grp(-290,-170,1,n,()=>{ box(-110,-40,220,80,16,'#fff'); tx('Ore 10:42',0,0,34,C.navy,'800'); });
},
coperta({u,p,A}){ lying(-90,200,.82,{blanket:clamp((p-.45)/.4),rise:Math.sin(u*2.4)*4}); },
'cuore-ecg'({u}){
  const b=1+Math.max(0,Math.sin(u*7))*.04; ctx.strokeStyle=C.giallo; ctx.lineWidth=16; heartP(0,-30,1.7*b); ctx.stroke();
  ctx.save(); ctx.beginPath(); ctx.rect(-400,0,800*clamp(u/2),300); ctx.clip();
  const pts=[]; for(let x=-400;x<=400;x+=8){ const t=(x+400)/800; let y; if(t<.35){ const ph=(t*6)%1; y=ph>.4&&ph<.5?-80:(ph>.5&&ph<.56?50:0);} else if(t<.75) y=Math.sin(t*90)*30*hash(Math.floor(t*40)); else y=0; pts.push([x,180+y]); }
  ln(pts,C.ciano,9); ctx.restore();
},
sicurezza({u,A}){
  [[-300,.3,'auto'],[0,.5,'bolt'],[300,.7,'fumo']].forEach(([x,t,k])=>grp(x,-20,1,A(t),()=>{
    poly([[0,-130],[140,110],[-140,110]],C.giallo); poly([[0,-95],[110,92],[-110,92]],C.navy);
    if(k==='auto') car(0,40,.42,'#fff'); if(k==='bolt') bolt(0,30,1.6,C.giallo);
    if(k==='fumo'){ for(let i=0;i<3;i++){ const f=(u*.6+i/3)%1; fc(-20+i*20,60-f*80,22+f*16,`rgba(207,214,232,${1-f})`);} }
  }));
  spunta(0,230,50,A(.95));
},
scuoti({u,p,A}){
  const sh=p<.7? Math.sin(u*16)*8 : 0;
  const hy=220-118*.72;
  ctx.save(); ctx.translate(-40,0);
  rescuerBack(-120,hy-40,.72,0,{head:{mouth:(u*4%1)<.5?'o':'flat'}});
  lying(-60+sh*.3,220,.72,{});
  arm(-120-80,hy-40-250*.72+10,[[-260,hy-60],[-250+sh,hy-30]],RS,RSD,36);
  arm(-120+80,hy-40-250*.72+10,[[-130,hy-60],[-160+sh,hy-30]],RS,RSD,36);
  ctx.restore();
  grp(130,-200,1,A(.15),()=>bubble(0,0,300,120,'Mi senti?',46,-80));
  grp(380,40,1,A(.85),()=>{ fc(0,0,60,C.giallo); tx('?',0,4,80,C.navy,'800','P'); });
},
respiro({u,p,A}){
  lying(-60,230,.8,{});
  const s=Math.min(10,Math.floor(p*14)+1); timer(300,-120,110,p*1.4,s+'″',{size:64});
  ctx.save(); ctx.setLineDash([12,12]); ln([[-160,40],[-160,-60]],'rgba(242,228,51,.6)',5); ctx.restore();
  eye(-160,-110,.55,1);
  const g=A(.8); if(g>0){ const f=(u*.7)%1; grp(-330,-60,1,g,()=>{ arc(0,0,30+f*30,-.8,.8,`rgba(255,255,255,${1-f})`,6); tx('?',60,-60,60,C.giallo,'800','P'); }); }
},
'telefono-dae'({u,A}){
  phone(-210,0,.95,{ring:true,u,speaker:A(.45)});
  grp(200,0,1,A(.85),()=>{ daeBox(0,0,1.15,{on:true,u}); const f=(u*1.2)%1; arrow(-120-f*20,180,-260-f*20,180,C.giallo,10); });
},
mani({u,p,A}){
  ctx.fillStyle=VS; ctx.beginPath(); ctx.moveTo(-250,300); ctx.lineTo(-250,-150); ctx.quadraticCurveTo(-250,-250,-150,-260); ctx.lineTo(150,-260); ctx.quadraticCurveTo(250,-250,250,-150); ctx.lineTo(250,300); ctx.fill();
  box(-55,-320,110,80,20,SKD); poly([[-55,-262],[0,-185],[55,-262]],SKD);
  ctx.save(); ctx.setLineDash([10,10]); ln([[0,-185],[0,150]],'rgba(27,34,63,.35)',6); ctx.restore();
  fe(-110,-20,16,12,'rgba(27,34,63,.25)'); fe(110,-20,16,12,'rgba(27,34,63,.25)');
  const pl=(u*1.5)%1; arc(0,40,60+pl*50,0,TAU,`rgba(242,228,51,${1-pl})`,8); fc(0,40,14,C.giallo);
  const h=A(.4); if(h>0){ const y=lerp(-260,40,clamp(h)); ctx.save(); ctx.globalAlpha*=clamp(h*2);
    ln([[-20,y-60],[-70,y-330]],RSD,74); ln([[20,y-60],[70,y-330]],RS,74);
    box(-70,y-60,140,120,50,SKD); for(let i=0;i<4;i++) box(-64+i*32,y+30,28,56,14,SKD); box(-92,y-50,30,70,15,SKD);
    box(-62,y-78,140,110,50,SK); for(let i=0;i<4;i++) box(-58+i*32,y-20,28,46,14,SK); box(62,y-70,28,64,14,SK);
    ctx.restore(); }
  const b=A(.8); if(b>0) grp(370,-150,1,b,()=>{ fc(0,0,90,C.tile); fc(0,-50,20,SK); ln([[0,-28],[0,30]],RS,26); ln([[-22,-20],[-22,70]],RS,14); ln([[22,-20],[22,70]],RS,14); ln([[-44,74],[44,74]],GREY,6); tx('tese',0,118,30,'#fff','700'); });
},
'rcp-sim'({u}){
  const c=compAt(u), d=c*30;
  cprScene(-110,250,.86,d);
  // contatore
  const tc=u-(CONTA.at||0), b=CONTA.beat||.545, n=CONTA.n||30;
  const k=Math.floor(tc/b+.5)+1; const num=clamp(k,0,n);
  const hit=tc>-b/2 && tc<(n-1)*b+b/2;
  fc(320,-150,120,C.tile); arc(320,-150,110,-Math.PI/2,-Math.PI/2+TAU*(num/n),C.giallo,14);
  if(num>0){ const ph=((tc/b)%1+1)%1; const sc=hit?1+.18*Math.max(0,1-ph*4):1; ctx.save(); ctx.translate(320,-160); ctx.scale(sc,sc); tx(String(num),0,0,110,'#fff','800'); ctx.restore(); tx('di '+n,320,-80,30,'#aab3cc','600'); }
  else tx('30',320,-150,90,'rgba(255,255,255,.35)','800');
  // profondità: si riempie verso il basso, fascia gialla = 5-6 cm
  box(-430,-210,60,240,30,C.tile); box(-424,-204+228*.82,48,228*.18,0,'rgba(242,228,51,.35)');
  box(-424,-204,48,Math.max(8,228*c),24,c>.82?C.giallo:C.ciano);
  ln([[-440,-204+228*.82],[-360,-204+228*.82]],'#fff',4); tx('5-6 cm',-400,60,28,'#fff','700');
  // battito
  const beatOn=hit && (((tc/b)%1+1)%1)<.2; fc(320,90,beatOn?34:26,beatOn?C.giallo:'rgba(242,228,51,.35)'); tx('110/min',320,145,30,'#fff','700');
  if(tc>(n-1)*b+b/2) spunta(320,-150,60,outBack(clamp((tc-(n-1)*b-b/2)/.4)));
},
ventila({u,p,A}){
  grp(0,-130,1,A(.1),()=>{ box(-400,-110,800,220,40,C.tile);
    tx('30',-210,-6,130,C.giallo,'800','P'); tx('compressioni',-210,76,28,'#fff','600');
    tx(':',0,-16,110,'#fff','800'); tx('2',170,-6,130,C.giallo,'800','P'); tx('ventilazioni',170,76,28,'#fff','600');
    for(let i=0;i<3;i++){ const f=(u*1.2+i/3)%1; arc(300,-10,20+f*50,-.7,.7,`rgba(255,255,255,${1-f})`,6); } });
  grp(0,150,1,A(.6),()=>{ box(-400,-90,800,180,40,'#fff'); tx('oppure',-310,0,30,GREY,'600'); const f=(u*110/60)%1; fc(-225,0,12+Math.max(0,1-f*4)*8,C.arancio);
    tx('solo compressioni, senza fermarti',-190,0,36,C.navy,'700','Jost','left'); });
},
dae({u,p,A}){
  ctx.fillStyle=VS; ctx.beginPath(); ctx.moveTo(-340,300); ctx.lineTo(-340,-120); ctx.quadraticCurveTo(-340,-220,-230,-230); ctx.lineTo(70,-230); ctx.quadraticCurveTo(180,-220,180,-120); ctx.lineTo(180,300); ctx.fill();
  box(-140,-290,120,70,20,SKD);
  ctx.fillStyle=SK; ctx.beginPath(); ctx.moveTo(-300,300); ctx.lineTo(-300,-110); ctx.quadraticCurveTo(-300,-190,-220,-195); ctx.lineTo(60,-195); ctx.quadraticCurveTo(140,-190,140,-110); ctx.lineTo(140,300); ctx.fill();
  fe(-170,30,10,8,SKD); fe(10,30,10,8,SKD);
  const a1=A(.45), a2=A(.55);
  const pad=(x,y,r,a)=>{ if(a<=0) return; grp(x,y,1,a,()=>{ ctx.rotate(r); box(-55,-80,110,160,24,'#fff'); sbox(-55,-80,110,160,24,C.navy,6); bolt(0,0,1,C.arancio); }); };
  if(a1>0){ ctx.save(); ctx.globalAlpha*=clamp(a1); ctx.strokeStyle='#e8702a'; ctx.lineWidth=7; ctx.beginPath(); ctx.moveTo(-200,-110); ctx.bezierCurveTo(-100,-250,250,-200,300,40); ctx.stroke(); ctx.restore(); }
  if(a2>0){ ctx.save(); ctx.globalAlpha*=clamp(a2); ctx.strokeStyle='#e8702a'; ctx.lineWidth=7; ctx.beginPath(); ctx.moveTo(110,130); ctx.quadraticCurveTo(220,200,300,80); ctx.stroke(); ctx.restore(); }
  pad(-200,-100,0,a1); pad(100,140,-.4,a2);
  daeBox(330,40,.85,{on:true,u});
  const w=A(.85); if(w>0){ const f=(u*2)%1; grp(-80,40,1,w,()=>{ arc(0,0,300+f*40,0,TAU,`rgba(242,228,51,${.8*(1-f)})`,10); box(-200,-40,400,80,40,C.giallo); tx('Non toccate!',0,2,42,C.navy,'800'); }); }
},
cambio({u,p,A}){
  const sw=Math.floor(u/3)%2; const d=24*(0.5+0.5*Math.cos(TAU*u*110/60));
  cprScene(-120,230,.66,d,{shirt:sw?C.arancio:RS,shirtD:sw?'#c25a1e':RSD});
  grp(300,-80,1,A(.85),()=>{ timer(0,0,120,(u%3)/3,'2′',{sub:'cambio'}); arc(0,0,150,-2.6,-1.2,C.giallo,8); arc(0,0,150,.5,1.9,C.giallo,8); });
},
gola({u}){
  bust(0,190,.85,{L:POSE.throat,R:mir(POSE.throat),head:{mouth:'o'},jx:Math.sin(u*9)*3});
  const f=(u*1.4)%1; ctx.save(); ctx.translate(0,190); ctx.scale(.85,.85); arc(0,-110,90+f*60,Math.PI*1.1,Math.PI*1.9,`rgba(217,71,61,${1-f})`,8); arc(0,-110,90+f*60,Math.PI*.1,Math.PI*.9,`rgba(217,71,61,${1-f})`,8); ctx.restore();
},
tosse({u}){
  const ph=(u*1.1)%1, j=ph<.15?Math.sin(ph/.15*Math.PI)*12:0;
  bust(0,190+j,.85,{R:[[150,40],[45,-150]],head:{mouth:ph<.3?'o':'flat'}});
  if(ph<.5){ const f=ph/.5; for(let i=0;i<3;i++) arc(-30,-30,40+f*120+i*20,Math.PI*.85,Math.PI*1.15,`rgba(255,255,255,${(1-f)*.9})`,8); }
},
colpi({u,p,A}){
  const ph=((u*1.1)%1); const hit=ph<.18;
  sideFig(-60,110,.72,{lean:.75,mouth:'o',frontArm(){ ln([[-20,-260],[-80,-170]],VSD,40); }});
  sideFig(170,110,.72,{shirt:RS,shirtD:RSD,
    backArm(){ ln([[-10,-260],[-150,-170],[-235,-150]],RSD,44); fc(-240,-150,24,SK); },
    frontArm(){ const a=hit?0:-.9*Math.sin(Math.min(1,(ph-.18)/.82)*Math.PI); ctx.save(); ctx.translate(0,-270); ctx.rotate(a); ln([[0,0],[-80,40],[-170,30]],RS,46); fc(-178,28,28,SK); ctx.restore(); }});
  if(hit){ const r=ph/.18; arc(-150*.72+170-60,-180*.72+110-40,30+r*40,0,TAU,`rgba(242,228,51,${1-r})`,8); }
  const n=Math.floor(Math.max(0,u-PRE)*1.1)%5+1; grp(360,-170,1,A(.8),()=>{ fc(0,0,70,C.giallo); tx(String(n),0,4,70,C.navy,'800','P'); tx('di 5',0,100,28,'#fff','600'); });
},
addome({u,A}){
  const ph=(u*1.0)%1; const th=ph<.25?Math.sin(ph/.25*Math.PI):0;
  const RX=40, RY=110, S=.72, LEAN=.15;
  sideFig(RX,RY,S,{shirt:RS,shirtD:RSD,lean:LEAN});
  sideFig(-90,RY,S,{lean:.12+th*.05,mouth:'o',frontArm(){ ln([[-20,-260],[-70,-150],[-60,-60]],VSD,40); }});
  ctx.save(); ctx.translate(RX,RY); ctx.scale(S,S); ctx.rotate(-LEAN);
  ln([[-10,-260],[-120,-190],[-250-th*25,-150-th*25]],RSD,54); ln([[-10,-260],[-120,-190],[-250-th*25,-150-th*25]],RS,46); fc(-258-th*25,-152-th*25,30,SK); fc(-248-th*25,-160-th*25,24,SKD);
  ctx.restore();
  if(th>.1) arrow(-310,40,-270-th*10,-20-th*20,C.giallo,10);
  const n=Math.floor(Math.max(0,u-PRE))%5+1; grp(360,-170,1,A(.9),()=>{ fc(0,0,70,C.giallo); tx(String(n),0,4,70,C.navy,'800','P'); tx('di 5',0,100,28,'#fff','600'); });
},
alterna({u}){
  const ph=(u%2.4)<1.2?0:1;
  [[-190,'colpi','tra le scapole',0],[190,'compressioni','sull’addome',1]].forEach(([x,l,s2,i])=>{ const on=ph===i; fc(x,-40,150,on?C.giallo:C.tile);
    tx('5',x,-60,190,on?C.navy:C.giallo,'600','P'); tx(l,x,150,40,'#fff','700'); tx(s2,x,200,30,'#aab3cc','500'); });
  arc(0,-40,40,-2.5,.6,C.ciano,8); arc(0,-40,40,.64,3.7,C.ciano,8);
},
medico({u,A}){
  box(-170,-220,340,420,30,'#fff'); box(-60,-246,120,50,14,'#aab3cc'); cross(0,-60,1.1,RED);
  for(let i=0;i<3;i++) box(-110,60+i*40,220-i*50,18,9,'#cfd6e8');
  steto(280,-40,.9);
},
adrenalina({u}){
  ctx.save(); ctx.rotate(-0.55+Math.sin(u*2)*.05); ctx.scale(1.4,1.4);
  box(-190,-38,320,76,38,'#fff'); box(100,-42,110,84,30,C.giallo); box(-230,-30,50,60,18,C.arancio); tx('ADRENALINA',-40,2,30,C.navy,'700'); ctx.restore();
},
cause({u,A}){
  grp(-300,0,1,A(.4),()=>{ fc(0,0,130,C.tile); fe(-25,-20,40,52,'#d9a86b',-.5); fe(25,25,40,52,'#d9a86b',-.5); ln([[-40,-30],[-10,-10]],'#b88848',5); });
  grp(0,0,1,A(.6),()=>{ fc(0,0,130,C.tile); const w=Math.sin(u*30)*.4; fe(-20,-40,34,22,'rgba(255,255,255,.7)',-.6+w); fe(20,-40,34,22,'rgba(255,255,255,.7)',.6-w);
    fe(0,10,60,40,C.giallo); ctx.save(); ctx.beginPath(); ctx.ellipse(0,10,60,40,0,0,TAU); ctx.clip(); ctx.fillStyle='#1a1f36'; ctx.fillRect(-20,-40,16,100); ctx.fillRect(14,-40,16,100); ctx.restore(); fc(-60,6,16,'#1a1f36'); });
  grp(300,0,1,A(.8),()=>{ fc(0,0,130,C.tile); pill(0,0,1); });
},
'corpo-segni'({u,p,A}){
  const sw=clamp(p/.2), hv=A(.6), faint=A(.85)>0.5;
  bust(0,190,.82,{head:{mouth:'lips',swell:sw,pale:faint},jx:faint?Math.sin(u*3)*6:0,
    over(){ if(hv>0){ ctx.save(); ctx.globalAlpha*=clamp(hv); for(let i=0;i<22;i++){ const x=-200+hash(i)*400, y=-60+hash(i+5)*300; fe(x,y,14,10,'rgba(217,71,61,.55)'); } ctx.restore(); } }});
  const r=A(.35); if(r>0){ const f=(u*1.4)%1; grp(-280,-60,1,r,()=>{ for(let i=0;i<3;i++) arc(0,0,30+((f+i/3)%1)*70,-.6,.6,'rgba(255,255,255,.7)',6); tx('fischi',0,90,30,'#fff','600'); }); }
},
telefono({u,p}){ phone(0,0,1.05,{num:'112'.slice(0,Math.min(3,Math.floor(p*14))),ring:p>.25,u}); },
penna({u,p,A}){
  leg(-60,80,1);
  const go=A(.4), press=clamp((p-.45)/.1);
  ctx.save(); ctx.translate(-80,-40-(1-press)*90); ctx.globalAlpha*=clamp(go); box(-38,-220,76,230,30,'#fff'); box(-38,-10,76,40,14,C.arancio); box(-38,-230,76,50,20,C.giallo); ctx.restore();
  if(press>=1){ const t=Math.max(0,(p-.55)*12); const n=Math.min(10,Math.floor(t)+1); timer(260,-110,100,t/10,String(n)+'″',{size:56}); tx('tieni premuto',260,30,30,'#fff','600'); }
},
posizioni({u,p,A}){
  const left=p<.45;
  grp(-220,0,1,1,()=>{ box(-200,-250,400,480,30,left?C.tile:'rgba(37,46,85,.45)'); ctx.save(); ctx.scale(.55,.55); ctx.translate(0,60);
    box(-120,60,260,30,12,'#6b7491'); box(110,-200,30,260,12,'#6b7491'); ln([[60,30],[-120,40],[-130,230]],PANT,64);
    ctx.save(); ctx.translate(60,40); ctx.rotate(.1); box(-60,-300,124,320,52,VS); fc(-6,-400,72,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(-6,-400,74,Math.PI*1.25,Math.PI*.45); ctx.fill(); ctx.restore(); ctx.restore();
    tx('respira male',0,190,30,'#fff','700'); });
  grp(220,0,1,1,()=>{ box(-200,-250,400,480,30,!left?C.tile:'rgba(37,46,85,.45)'); ctx.save(); ctx.scale(.36,.36); ctx.translate(-120,240); lying(0,0,1,{legsUp:true}); box(400,-170,140,170,12,'#6b7491'); ctx.restore();
    tx('debole o pallido',0,190,30,'#fff','700'); });
},
'penna-timer'({u,p,A}){ timer(-180,0,150,p*1.3,Math.min(5,Math.floor(p*6.5))+'′',{sub:'minuti'}); grp(200,0,1,A(.6),()=>{ ctx.rotate(-.5); box(-150,-34,240,68,34,'#fff'); box(80,-38,90,76,26,C.giallo); box(-185,-28,44,56,16,C.arancio); tx('2ª dose',-30,2,30,C.navy,'800'); }); },
ustione({u}){
  ctx.save(); ctx.scale(1.3,1.3);
  ln([[-150,-150],[40,-150]],'#cfd6e8',16); ctx.strokeStyle='#cfd6e8'; ctx.lineWidth=16; ctx.beginPath(); ctx.moveTo(40,-150); ctx.quadraticCurveTo(80,-150,80,-100); ctx.lineTo(80,-70); ctx.stroke();
  box(-170,-185,40,70,10,'#cfd6e8'); box(-40,-200,60,30,10,'#cfd6e8');
  for(let i=0;i<9;i++){ const yy=-50+((u*320+i*45)%240); fe(80+((i%3)-1)*14,yy,8,16,C.ciano); }
  timer(-110,90,72,clamp(u/4),'20′',{size:42}); ctx.restore();
},
rotola({u,A}){
  const fig=(rot,fl)=>{ ctx.save(); ctx.rotate(rot); ln([[0,-20],[0,60]],VS,40); fc(0,-60,26,SK); ln([[-14,60],[-20,120]],PANT,22); ln([[14,60],[20,120]],PANT,22); ln([[-30,-10],[-50,50]],VS,18); ln([[30,-10],[50,50]],VS,18);
    if(fl){ for(let i=0;i<3;i++){ const f=(u*2+i/3)%1; drop(-30+i*30,20-f*50,.5+(1-f)*.3,`rgba(232,112,42,${1-f})`); } } ctx.restore(); };
  grp(-300,20,1,A(.35),()=>{ box(-120,-150,240,300,24,C.tile); fig(0,true); tx('fermati',0,175,30,'#fff','700'); });
  grp(0,20,1,A(.5),()=>{ box(-120,-150,240,300,24,C.tile); ctx.translate(0,70); fig(Math.PI/2,true); tx('sdraiati',0,105,30,'#fff','700'); });
  grp(300,20,1,A(.65),()=>{ box(-120,-150,240,300,24,C.tile); ctx.translate(Math.sin(u*2)*30,70); ctx.save(); ctx.scale(1,1); fig(Math.PI/2+Math.sin(u*2)*.0,false); ctx.restore(); arc(0,-40,50,-2.6,-.6,C.giallo,7); tx('rotola',-Math.sin(u*2)*30,105,30,'#fff','700'); });
},
rubinetto({u,p,A}){
  ctx.save(); ctx.translate(-80,0);
  ctx.strokeStyle='#cfd6e8'; ctx.lineWidth=34; ctx.lineCap='round'; ctx.beginPath(); ctx.moveTo(-300,-240); ctx.lineTo(-60,-240); ctx.quadraticCurveTo(0,-240,0,-180); ctx.lineTo(0,-150); ctx.stroke(); box(-120,-290,70,34,10,'#cfd6e8');
  ctx.globalAlpha*=.85; for(let i=0;i<14;i++){ const yy=-140+((u*420+i*28)%220); fe(((i%3)-1)*12,yy,7,15,C.ciano); } ctx.globalAlpha=1;
  ln([[-330,130],[60,110]],VS,96); ln([[-80,120],[90,112]],SK,84); fe(130,112,56,48,SK);
  for(let i=0;i<5;i++){ const f=(u*1.6+i/5)%1; drop(-40+i*30+f*20,170+f*60,.35,`rgba(0,165,220,${1-f})`); }
  ctx.restore();
  timer(300,-70,130,p,Math.min(20,Math.floor(p*20)+1)+'′',{sub:'minuti'});
},
anelli({u,p,A}){
  ctx.save(); ctx.translate(0,60);
  box(-110,-60,220,240,80,SK); for(let i=0;i<4;i++) box(-104+i*54,-260+Math.abs(i-1.5)*24,48,230,24,SK); ctx.save(); ctx.translate(110,40); ctx.rotate(-.7); box(-24,-140,48,150,24,SK); ctx.restore();
  ln([[0,180],[0,320]],SK,190);
  const r=A(.25); const ry=-80-clamp(r)*240; ctx.globalAlpha=clamp(1-(r-.6)*2.5); box(-54+54-25,ry,58,26,12,C.giallo); ctx.globalAlpha=1;
  const w=A(.4); ctx.globalAlpha=clamp(1-w); box(-100,190,200,60,16,'#1a1f36'); fc(0,220,40,'#cfd6e8'); ctx.globalAlpha=1;
  if(r>0) arrow(170,-160,170,-320,C.giallo,10);
  ctx.restore();
},
pellicola({u,p,A}){
  forearm(100);
  fe(40,95,90,40,'rgba(232,112,42,.5)');
  const w=clamp((p-.1)/.6);
  ctx.save(); ctx.beginPath(); ctx.rect(-260,-40,520*w,280); ctx.clip();
  ctx.fillStyle='rgba(220,240,255,.35)'; ctx.fillRect(-260,30,520,140); ctx.strokeStyle='rgba(255,255,255,.75)'; ctx.lineWidth=4;
  for(let i=0;i<9;i++){ ctx.beginPath(); ctx.moveTo(-260+i*60,30); ctx.lineTo(-220+i*60,170); ctx.stroke(); } ctx.restore();
  grp(330,-150,1,A(.35),()=>{ box(-80,-60,160,120,16,'#cfd6e8'); box(-90,-70,180,40,12,C.ciano); tx('pellicola',0,30,28,C.navy,'700'); });
},
'no-rimedi'({A}){
  const it=[[-330,.15,()=>{cube(0,0,1.6,'#dff3fb');}],[-110,.3,()=>{ box(-70,-40,140,80,14,'#f6e27a'); box(-80,-50,160,30,12,'#fff'); }],[110,.45,()=>bottle(0,10,.8,'#e0b84a','#fff')],[330,.6,()=>{ ctx.rotate(-.5); box(-90,-30,170,60,20,'#fff'); box(80,-20,30,40,8,C.ciano); }]];
  it.forEach(([x,t,f])=>grp(x,-60,1,A(t),()=>{ fc(0,0,100,C.tile); f(); vieto(0,0,90,A(t+.06)); }));
  grp(0,180,1,A(.8),()=>{ fe(0,0,120,60,'#f3d4c0'); fc(-20,-10,36,'rgba(255,255,255,.75)'); fc(30,10,24,'rgba(255,255,255,.75)'); vieto(0,0,80,A(.86)); });
},
'coperta-braccio'({u,p,A}){ lying(-90,200,.82,{blanket:clamp(p/.5),rise:Math.sin(u*2.4)*4}); grp(330,-160,1,A(.85),()=>{ fc(0,0,70,C.tile); tx('°C',0,4,56,C.giallo,'800'); }); },
palmo({u,p,A}){
  const g=A(.2); fe(0,20,150+90*clamp(g),190+60*clamp(g),'rgba(232,112,42,.55)');
  ctx.save(); ctx.globalAlpha*=.95; box(-110,-40,220,240,80,SK); for(let i=0;i<4;i++) box(-104+i*54,-240+Math.abs(i-1.5)*24,48,220,24,SK); ctx.save(); ctx.translate(110,60); ctx.rotate(-.7); box(-24,-140,48,150,24,SK); ctx.restore(); ctx.restore();
  ctx.save(); ctx.setLineDash([12,10]); ctx.strokeStyle=C.giallo; ctx.lineWidth=6; rr(ctx,-130,-260,260,480,90); ctx.stroke(); ctx.restore();
},
zucchero({u}){
  ctx.save(); ctx.scale(1.3,1.3);
  ctx.save(); ctx.beginPath(); ctx.moveTo(-30,-150); ctx.lineTo(150,-150); ctx.lineTo(125,140); ctx.lineTo(-5,140); ctx.closePath(); ctx.clip(); ctx.fillStyle=C.giallo; ctx.fillRect(-40,-90+Math.sin(u*2)*4,200,260); ctx.restore();
  ctx.strokeStyle='#fff'; ctx.lineWidth=10; ctx.beginPath(); ctx.moveTo(-30,-150); ctx.lineTo(150,-150); ctx.lineTo(125,140); ctx.lineTo(-5,140); ctx.closePath(); ctx.stroke(); ln([[90,-150],[130,-220]],'#fff',10);
  [[-190,60],[-110,60],[-150,-10]].forEach(([x,y],i)=>box(x,y+Math.sin(u*3+i)*3,70,70,12,'#fff')); ctx.restore();
},
glucometro({u,A}){
  box(-250,-220,260,400,40,'#fff'); box(-220,-180,200,150,20,'#24305c'); const bl=(u*2%1)<.6; tx('55',-140,-110,80,bl?C.giallo:'#6b7491','800'); arrow(-50,-150,-50,-80,C.giallo,7);
  fc(-120,60,40,'#cfd6e8'); fc(-120,60,22,C.navy);
  grp(220,0,1,A(.3),()=>{ ctx.rotate(.5); box(-40,-200,80,330,30,'#cfd6e8'); box(-40,-200,80,70,24,C.ciano); box(-12,130,24,40,6,'#aab3cc'); });
},
tremore({u,p,A}){
  const j=Math.sin(u*40)*4*clamp(p*3);
  bust(0,190,.8,{head:{mouth:'flat',pale:p>.15},jx:j,over(){ for(let i=0;i<4;i++){ const yy=-300+((u*90+i*37)%120); drop(-80+i*50,yy,.35,C.ciano);} }});
  grp(250,-200,1,A(.6),()=>{ for(let i=0;i<3;i++){ const a=u*2+i*2.1; tx('?',Math.cos(a)*50,Math.sin(a)*24,60,C.giallo,'800','P'); } });
},
zuccheri({u,A}){
  grp(-330,0,1,A(.4),()=>{ fc(0,0,105,C.tile); [[-30,-20],[30,-20],[0,30]].forEach(([x,y])=>{ fc(x,y,32,'#fff'); tx('G',x,y+2,26,C.ciano,'800'); }); });
  grp(-110,0,1,A(.6),()=>{ fc(0,0,105,C.tile); glass(0,0,.8,.75,'#f2a541'); });
  grp(110,0,1,A(.62),()=>{ fc(0,0,105,C.tile); box(-38,-70,76,140,20,RED); box(-38,-70,76,18,8,'#cfd6e8'); ctx.strokeStyle='#fff'; ctx.lineWidth=6; ctx.beginPath(); ctx.moveTo(-38,10); ctx.bezierCurveTo(-10,-20,10,40,38,0); ctx.stroke(); });
  grp(330,0,1,A(.9),()=>{ fc(0,0,105,C.tile); cube(-28,10,.9); cube(28,10,.9); cube(0,-30,.9); });
},
timer15({u,p,A}){ timer(0,-10,190,p,Math.min(15,Math.floor(p*15)+1)+'′',{sub:'minuti',size:110}); grp(300,170,1,A(.8),()=>{ arc(0,0,60,-2.8,1.6,C.giallo,12); poly([[30,60],[66,40],[40,20]],C.giallo); }); },
merenda({A}){ grp(-160,0,1,A(.4),()=>{ fc(0,0,150,C.tile); box(-100,-90,200,180,60,'#e9b871'); box(-80,-70,160,140,40,'#f6deb0'); });
  grp(170,0,1,A(.6),()=>{ fc(0,0,150,C.tile); for(let i=0;i<3;i++){ box(-90+i*20,-80+i*30,140,100,12,'#e6b45c'); for(let j=0;j<6;j++) fc(-60+i*20+(j%3)*40,-50+i*30+Math.floor(j/3)*40,5,'#b88838'); } }); },
veleno({u}){
  ctx.save(); ctx.scale(1.25,1.25);
  box(-150,-110,170,240,30,'#3a8d6c'); ctx.fillStyle='#3a8d6c'; ctx.fillRect(-105,-170,80,70); box(-115,-200,100,40,8,'#fff'); box(-130,-40,130,90,10,'#fff');
  poly([[110,-110],[225,90],[-5,90]],C.giallo); tx('!',110,30,120,C.navy,'800'); ctx.restore();
},
casa({u,A}){
  box(-400,-80,520,330,20,'#6b7491'); box(-380,-60,230,290,12,'#55607f'); box(-130,-60,230,290,12,'#55607f');
  ctx.save(); ctx.translate(-380,-60); ctx.scale(-.2+.2*Math.cos(0),1); ctx.restore();
  bottle(-310,120,.6,'#3a8d6c'); bottle(-200,130,.5,C.ciano); bottle(-60,130,.55,'#e0b84a'); box(10,150,70,60,10,'#fff');
  grp(300,60,1,A(.85),()=>{ fc(0,-110,70,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(0,-110,72,Math.PI,0); ctx.fill(); fc(-24,-104,7,C.navy); fc(24,-104,7,C.navy); box(-60,-40,120,180,40,'#f2a541'); const r=Math.sin(u*2)*.2; ctx.save(); ctx.translate(-50,-10); ctx.rotate(-1.2+r); ln([[0,0],[0,-120]],'#f2a541',36); fc(0,-128,20,SK); ctx.restore(); });
},
'no-vomito'({u,A}){
  bust(-60,190,.8,{head:{mouth:'flat'}});
  grp(220,-60,1,A(.4),()=>{ arrow(0,200,0,-120,'#7cc46a',22); vieto(0,40,150,1); });
},
'no-latte'({A}){
  grp(-200,0,1,A(.2),()=>{ fc(0,0,150,C.tile); box(-60,-80,120,170,8,'#fff'); poly([[-60,-80],[0,-130],[60,-80]],'#e3e7f1'); box(-60,-20,120,50,0,C.ciano); vieto(0,0,135,A(.27)); });
  grp(200,0,1,A(.35),()=>{ fc(0,0,150,C.tile); glass(0,0,1); vieto(0,0,135,A(.42)); });
},
cav({u,p,A}){
  phone(-230,0,.95,{num:'112',ring:true,u,label:'o Centro Antiveleni'});
  grp(200,0,1,A(.45),()=>{ box(-170,-200,340,400,40,'#fff'); cross(0,-160,.3,RED); tx('Centri Antiveleni',0,-120,34,C.navy,'700','P'); tx('Roma · 24 ore su 24',0,-80,24,'#006d96','700');
    [['Gemelli','06 3054343',.55],['Umberto I','06 49978000',.7],['Bambino Gesù','06 68593726',.88]].forEach(([n,t,f],i)=>{ ctx.save(); ctx.globalAlpha*=clamp(A(f)); tx(n,0,-20+i*72,24,GREY,'600'); tx(t,0,6+i*72,32,C.navy,'800'); ctx.restore(); }); });
},
confezione({u,A}){
  bottle(-150,40,1.3,'#3a8d6c','#fff'); ctx.save(); ctx.translate(-150,40); ctx.scale(1.3,1.3); for(let i=0;i<3;i++) box(-36,-10+i*14,72-i*16,8,4,'#aab3cc'); ctx.restore();
  const m=(u*.8)%1; grp(-60+Math.sin(u*1.4)*30,-20,1,1,()=>{ arc(0,0,60,0,TAU,'#fff',14); ln([[42,42],[100,100]],'#fff',20); });
  [['Cosa',.55],['Quanto',.7],['Quando',.85]].forEach(([l,t],i)=>grp(260,-150+i*130,1,A(t),()=>{ box(-120,-46,240,92,46,C.giallo); tx(l+'?',0,2,40,C.navy,'800'); }));
},
occhi({u,A}){
  eye(-40,40,1.4);
  ctx.strokeStyle='#cfd6e8'; ctx.lineWidth=30; ctx.lineCap='round'; ctx.beginPath(); ctx.moveTo(380,-260); ctx.lineTo(260,-260); ctx.quadraticCurveTo(200,-260,200,-200); ctx.stroke();
  for(let i=0;i<12;i++){ const f=(u*1.4+i/12)%1; const x=200-f*200, y=-180+f*f*200; fe(x,y,8,12,`rgba(0,165,220,${1-f*.6})`); }
},
finestra({u,p,A}){
  box(-330,-260,420,460,20,'#55607f'); const o=clamp(A(.55));
  ctx.fillStyle='#9fd8f0'; ctx.fillRect(-310,-240,380,420);
  ctx.save(); ctx.translate(-310,-240); ctx.scale(1-o*.8,1); box(0,0,190,420,0,'rgba(207,233,245,.9)'); sbox(0,0,190,420,0,'#fff',12); ctx.restore();
  ctx.save(); ctx.translate(70,-240); ctx.scale(-(1-o*.8),1); box(0,0,190,420,0,'rgba(207,233,245,.9)'); sbox(0,0,190,420,0,'#fff',12); ctx.restore();
  for(let i=0;i<5;i++){ const f=(u*.4+i/5)%1; const x=lerp(-160,o>0?380:0,f), y=-40+Math.sin(f*6+i)*40; fc(x,y,40+f*30,`rgba(150,160,180,${(o>0?1-f:.6)*.8})`); }
},
armadietto({u,A}){
  ctx.save(); ctx.translate(0,70);
  box(-380,-280,440,230,20,'#6b7491'); box(-360,-260,400,190,12,'#55607f'); bottle(-290,-150,.45,'#3a8d6c'); bottle(-180,-150,.45,C.ciano); bottle(-70,-150,.45,'#e0b84a');
  grp(-160,-300,1,A(.45),()=>{ box(-24,-24,48,40,8,C.giallo); arc(0,-26,18,Math.PI,0,C.giallo,8); });
  grp(-170,180,1,A(.45),()=>{ fc(0,-60,50,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(0,-60,52,Math.PI,0); ctx.fill(); box(-44,-10,88,120,30,'#f2a541'); ln([[30,0],[60,-90]],'#f2a541',26); fc(62,-100,14,SK); });
  if(CFG.nome==='Avvelenamento') grp(300,60,1,A(.85),()=>{ box(-40,-150,80,250,30,'rgba(159,216,240,.6)'); box(-20,-200,40,60,10,'rgba(159,216,240,.6)'); box(-40,-50,80,60,0,'#3a8d6c'); vieto(0,-30,150,1); });
  ctx.restore();
},
testa({u}){
  ctx.save(); ctx.scale(1.3,1.3);
  fc(0,-20,150,SK); ctx.fillRect(-50,110,100,90);
  ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(0,-20,152,Math.PI,0); ctx.bezierCurveTo(140,-70,-40,-120,-152,-20); ctx.fill();
  fe(80,-120,40,24,'#d98a7a'); fc(-50,10,12,C.navy); fc(50,10,12,C.navy); ln([[-30,80],[30,80]],C.navy,8);
  for(let i=0;i<3;i++){ const an=u*2+i*2.1; const x=Math.cos(an)*190, y=-190+Math.sin(an)*30; ctx.fillStyle=C.giallo; ctx.beginPath(); for(let j=0;j<8;j++){const r=j%2?7:18,b=j*Math.PI/4; ctx.lineTo(x+Math.cos(b)*r,y+Math.sin(b)*r);} ctx.fill(); }
  ctx.restore();
},
campo({u,A}){
  box(-420,-200,840,420,20,'#2f6b4f'); ln([[0,-200],[0,220]],'rgba(255,255,255,.6)',6); arc(0,10,80,0,TAU,'rgba(255,255,255,.6)',6);
  const x=lerp(0,360,clamp((u-1)/4)); ctx.save(); ctx.translate(x-100,60); ln([[0,-30],[0,60]],'#fff',34); fc(0,-70,28,SK); ln([[-12,60],[-20+Math.sin(u*6)*10,130]],PANT,20); ln([[12,60],[20-Math.sin(u*6)*10,130]],PANT,20); ctx.restore();
  grp(-250,-80,1,A(.3),()=>{ ctx.beginPath(); for(let i=0;i<8;i++){ const a=i/8*TAU+Math.PI/8; ctx.lineTo(Math.cos(a)*90,Math.sin(a)*90);} ctx.closePath(); ctx.fillStyle=RED; ctx.fill(); tx('STOP',0,4,46,'#fff','800'); });
  arrow(200,-130,380,-130,C.giallo,10);
},
domande({u,A}){
  bust(-160,200,.75,{head:{mouth:'flat'}});
  [[150,-200,.2],[260,-60,.45],[170,80,.75]].forEach(([x,y,t])=>grp(x,y,1,A(t),()=>{ bubble(0,0,170,110,'?',70,-60); }));
},
allarme({u,A}){
  head(-60,0,170,{closed:true,mouth:'flat',pale:true});
  const f=(u*1.3)%1; grp(260,-130,1,A(.25),()=>{ poly([[0,-100],[110,90],[-110,90]],C.giallo); tx('!',0,30,100,C.navy,'800'); });
  for(let i=0;i<3;i++){ const ff=(u*.6+i/3)%1; tx('z',150+ff*90,-40-ff*120,40+ff*20,`rgba(255,255,255,${1-ff})`,'700'); }
},
pupille({u,A}){
  eye(-190,-60,1,1); eye(190,-60,1,clamp(1+1.4*A(.6),1,2.4));
  grp(0,180,1,A(.3),()=>{ ctx.fillStyle=SK; ctx.beginPath(); ctx.moveTo(-40,-80); ctx.quadraticCurveTo(-10,30,-70,60); ctx.quadraticCurveTo(0,90,70,60); ctx.quadraticCurveTo(10,30,40,-80); ctx.fill(); const f=(u*.8)%1; drop(-40,80+f*60,.5,`rgba(217,71,61,${1-f})`); });
},
'non-muovere'({u,A}){
  lying(-60,200,.8,{});
  const a=A(.55); if(a>0){ ctx.save(); ctx.globalAlpha*=clamp(a); arc(-60-290*.8,200-66*.8,90,0,TAU,C.giallo,8); ctx.restore(); vieto(0,-130,70,a); arrow(100,-130,200,-130,C.giallo,9); arrow(-100,-130,-200,-130,C.giallo,9); }
},
ghiaccio({u,A}){
  head(-120,40,170,{mouth:'flat'}); fe(-60,-110,46,26,'#d98a7a');
  grp(-20,-170,1,A(.3),()=>{ const k=Math.sin(u*2)*3; box(-110+k,-70,220,140,50,'#cfd6e8'); cube(-30+k,-10,.7,'#dff3fb'); cube(30+k,-10,.7,'#dff3fb'); });
},
notte({u,A}){
  ctx.fillStyle=C.giallo; ctx.beginPath(); ctx.arc(-230,-120,110,0,TAU); ctx.fill(); ctx.fillStyle=C.navy; ctx.beginPath(); ctx.arc(-180,-150,100,0,TAU); ctx.fill();
  timer(150,-100,130,clamp(u/6),'24h',{size:64});
  grp(-140,160,1,A(.55),()=>{ fc(0,0,90,C.tile); glass(0,0,.55,.6,'#d98a7a'); vieto(0,0,80,1); });
  grp(130,160,1,A(.7),()=>{ fc(0,0,90,C.tile); car(0,10,.4,'#cfd6e8'); vieto(0,0,80,1); });
},
};
