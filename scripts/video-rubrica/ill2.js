// ===== Disegni della seconda serie (si aggiungono a ILL) =====
const BABY='#bfe6f5', BABYD='#8fcbe3', GRAYH='#c9ccd4', ORANGE=C.arancio;
function babyFace(x,y,r,o={}){ fc(x,y,r,o.blue?'#b9c4de':SK); ctx.fillStyle=o.hairCol||'#8a6a4a'; ctx.beginPath(); ctx.arc(x,y-r*.55,r*.35,Math.PI,0); ctx.fill();
  if(o.closed){ ln([[x-r*.45,y],[x-r*.2,y]],C.navy,r*.08); ln([[x+r*.2,y],[x+r*.45,y]],C.navy,r*.08); } else { fc(x-r*.32,y,r*.1,C.navy); fc(x+r*.32,y,r*.1,C.navy); }
  if(o.mouth==='o') fe(x,y+r*.42,r*.12,r*.15,C.navy); else { ctx.strokeStyle=C.navy; ctx.lineWidth=r*.07; ctx.beginPath(); ctx.arc(x,y+r*.25,r*.25,.3,Math.PI-.3); ctx.stroke(); }
  if(!o.blue){ fe(x-r*.55,y+r*.3,r*.15,r*.09,'rgba(222,120,110,.35)'); fe(x+r*.55,y+r*.3,r*.15,r*.09,'rgba(222,120,110,.35)'); } }
// lattante sdraiato di profilo (testa a sinistra): (x,y) = petto, d = compressione
function babyLying(x,y,s,d=0,o={}){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  ln([[60,-30],[170,-20]],BABY,46); ln([[60,-50],[160,-70]],BABYD,40);
  box(-90,-90+d,180,90-d,40,BABY); fc(-150,-60,62,SK); ctx.fillStyle='#8a6a4a'; ctx.beginPath(); ctx.arc(-150,-60,64,Math.PI*.6,Math.PI*1.3); ctx.fill();
  ln([[-140,-110],[-122,-108]],C.navy,5); fe(-108,-112,8,7,SKD);
  ln([[-40,-60],[-10,-110]],BABYD,30); fc(-8,-114,13,SK); ctx.restore(); }
function contatore(x,y,u){ const tc=u-(CONTA.at||0), b=CONTA.beat||.545, n=CONTA.n||30;
  const k=Math.floor(tc/b+.5)+1; const num=clamp(k,0,n); const hit=tc>-b/2 && tc<(n-1)*b+b/2;
  fc(x,y,120,C.tile); arc(x,y,110,-Math.PI/2,-Math.PI/2+TAU*(num/n),C.giallo,14);
  if(num>0){ const ph=((tc/b)%1+1)%1; const sc=hit?1+.18*Math.max(0,1-ph*4):1; ctx.save(); ctx.translate(x,y-10); ctx.scale(sc,sc); tx(String(num),0,0,110,'#fff','800'); ctx.restore(); tx('di '+n,x,y+70,30,'#aab3cc','600'); }
  else tx(String(n),x,y,90,'rgba(255,255,255,.35)','800');
  const beatOn=hit && (((tc/b)%1+1)%1)<.2; fc(x,y+240,beatOn?34:26,beatOn?C.giallo:'rgba(242,228,51,.35)'); tx('110/min',x,y+295,30,'#fff','700');
  if(tc>(n-1)*b+b/2) spunta(x,y,60,outBack(clamp((tc-(n-1)*b-b/2)/.4))); }
function gauge(x,y,c,label){ box(x-30,y,60,240,30,C.tile); box(x-24,y+6+228*.82,48,228*.18,0,'rgba(242,228,51,.35)');
  box(x-24,y+6,48,Math.max(8,228*c),24,c>.82?C.giallo:C.ciano); ln([[x-40,y+6+228*.82],[x+40,y+6+228*.82]],'#fff',4); tx(label,x,y+270,28,'#fff','700'); }
function panel(x,y,w,h,on,label){ box(x-w/2,y-h/2,w,h,26,on===false?'rgba(37,46,85,.45)':C.tile); if(label) tx(label,x,y+h/2-30,28,'#fff','700'); }
function stick(x,y,s,o={}){ // figurina semplice in piedi
  ctx.save(); ctx.translate(x,y); ctx.scale(s,s); if(o.rot) ctx.rotate(o.rot);
  ln([[0,-20],[0,60]],o.shirt||VS,40); fc(0,-62,26,SK); if(o.hair!==false){ ctx.fillStyle=o.hairCol||HAIR; ctx.beginPath(); ctx.arc(0,-62,27,Math.PI,0); ctx.fill(); }
  ln([[-12,60],[-18,o.legs||125]],PANT,20); ln([[12,60],[18,o.legs||125]],PANT,20);
  ln([[-24,-10],[-44,o.armY??45]],o.shirt||VS,17); ln([[24,-10],[44,o.armY??45]],o.shirt||VS,17); ctx.restore(); }
function house(x,y,s,col='#55607f'){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-150,-60,300,220,10,col); poly([[-180,-50],[0,-200],[180,-50]],'#6b7491'); box(-40,60,80,100,8,'#24305c'); box(-120,-20,70,60,6,'#9fd8f0'); box(50,-20,70,60,6,'#9fd8f0'); ctx.restore(); }
function snow(u,n=26){ for(let i=0;i<n;i++){ const x=-440+hash(i)*880, y=-300+((u*60+hash(i+9)*600)%600); fc(x,y,3+hash(i+3)*4,'rgba(255,255,255,.75)'); } }
function hand(x,y,s,rot=0,col=SK){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(s,s); box(-60,-50,120,130,46,col); for(let i=0;i<4;i++) box(-56+i*29,-150+Math.abs(i-1.5)*14,26,120,13,col); ctx.save(); ctx.translate(60,20); ctx.rotate(-.7); box(-14,-80,28,86,14,col); ctx.restore(); ctx.restore(); }
function bag(x,y,s,col='#cfe9f5'){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.fillStyle=col; ctx.beginPath(); ctx.moveTo(-80,-80); ctx.lineTo(80,-80); ctx.lineTo(95,100); ctx.lineTo(-95,100); ctx.closePath(); ctx.fill(); box(-84,-96,168,22,8,'#fff'); ctx.restore(); }

Object.assign(ILL, {
convulsione({u}){ const j=Math.sin(u*38)*5, k=Math.cos(u*31)*4; ctx.save(); ctx.translate(j,k); lying(-80,190,.82,{}); ctx.restore();
  for(let i=0;i<3;i++){ const f=(u*2+i/3)%1; arc(-330,40,40+f*40,Math.PI*.8,Math.PI*1.4,`rgba(242,228,51,${1-f})`,6); arc(260,60,40+f*40,-.4,.4,`rgba(242,228,51,${1-f})`,6); } },
'conv-spazio'({u,p}){ const j=Math.sin(u*38)*4; ctx.save(); ctx.translate(j,0); lying(-80,210,.78,{}); ctx.restore();
  const o=clamp(p*1.5); ctx.save(); ctx.translate(-420*o+120,0); ctx.globalAlpha*=1-o*.6; box(-60,-120,20,190,6,'#6b7491'); box(-60,-20,120,20,6,'#6b7491'); box(40,-20,20,90,6,'#6b7491'); ctx.restore();
  ctx.save(); ctx.translate(380*o+150,40); ctx.globalAlpha*=1-o*.6; box(-36,-50,72,90,14,'#fff'); arc(44,-5,24,-1.4,1.4,'#fff',10); ctx.restore();
  if(o>.3){ arrow(-120,-160,-300,-160,C.giallo,9); arrow(180,-160,360,-160,C.giallo,9); } },
'conv-no-tenere'({u,A}){ const j=Math.sin(u*38)*4; ctx.save(); ctx.translate(j,0); lying(-80,210,.78,{}); ctx.restore(); grp(-90,30,1,A(.2),()=>{ handTop(0,0,.7); handTop(160,0,.7); }); vieto(0,-150,90,A(.3)); },
'conv-cuscino'({u,p,A}){ const a=A(.45); lying(-60,210,.8,{}); if(a>0){ ctx.save(); ctx.translate(-300+(1-clamp(a))*-200,175); box(-80,-14,170,40,16,RS); box(-70,-24,150,18,8,'#33b8e6'); ctx.restore(); } grp(-170,-60,1,A(.85),()=>{ arc(0,0,40,.3,2.8,C.giallo,7); }); },
'conv-bocca'({A}){ head(-120,0,170,{mouth:'o'}); grp(170,30,1,A(.2),()=>{ ctx.rotate(-.4); box(-120,-14,180,28,14,'#cfd6e8'); fe(80,0,46,32,'#cfd6e8'); }); vieto(150,30,120,A(.3)); },
timer5c({u,p,A}){ const m=Math.min(5,Math.floor(p*6.5)); timer(-170,0,170,p*1.3,m+'′',{sub:'minuti',size:100}); grp(230,0,1,A(.75),()=>phone(0,0,.85,{ring:true,u})); },
incidente({u}){ const t=clamp(u/1.2); const hit=t>=1; ctx.save(); ctx.translate(lerp(-420,-150,inOut(t)),40); car(0,0,1,'#e0b84a'); ctx.restore();
  ctx.save(); ctx.translate(170,60); ctx.rotate(hit?-.18:0); car(0,0,1,'#6b7491'); ctx.restore();
  if(hit){ const f=Math.min(1,(u-1.2)*2); ctx.save(); ctx.translate(10,-10); ctx.scale(.6+f*.6,.6+f*.6); ctx.beginPath(); for(let i=0;i<16;i++){ const a=i/16*TAU, r=i%2?40:90; ctx.lineTo(Math.cos(a)*r,Math.sin(a)*r);} ctx.closePath(); ctx.fillStyle=C.giallo; ctx.fill(); ctx.restore(); }
  ln([[-440,150],[440,150]],'#3a4570',10); },
giubbotto({u,A}){ car(-200,60,1.1,'#6b7491'); const on=(u*2%1)<.5; if(on){ fc(-355,40,26,'rgba(232,112,42,.9)'); fc(-45,40,26,'rgba(232,112,42,.9)'); fc(-355,40,46,'rgba(232,112,42,.3)'); fc(-45,40,46,'rgba(232,112,42,.3)'); }
  grp(260,40,1,A(.75),()=>{ bust(0,60,.62,{shirt:'#d9e86a',shirtD:'#b8c94a',head:{mouth:'smile'},over(){ ctx.fillStyle='#cfd6e8'; ctx.fillRect(-150,40,300,26); ctx.fillRect(-150,120,300,26); }}); }); },
triangolo({u,p,A}){ ln([[-440,180],[440,180]],'#3a4570',10); for(let i=0;i<6;i++) ln([[-420+i*160,215],[-340+i*160,215]],'rgba(255,255,255,.35)',8);
  car(260,110,.9,'#6b7491'); const a=A(.3); grp(-280,110,1,a,()=>{ poly([[0,-90],[80,40],[-80,40]],RED); poly([[0,-50],[46,26],[-46,26]],C.navy); ln([[0,40],[0,70]],'#cfd6e8',8); });
  const m=A(.6); if(m>0){ ctx.save(); ctx.globalAlpha*=clamp(m); ln([[-280,-40],[260,-40]],C.giallo,6); ln([[-280,-60],[-280,-20]],C.giallo,6); ln([[260,-60],[260,-20]],C.giallo,6); tx('almeno 50 m',-10,-80,40,C.giallo,'800'); ctx.restore(); } },
chiave({u,A}){ fc(-150,0,150,C.tile); arc(-150,0,100,0,TAU,'#55607f',20); const r=-clamp(A(.5))*1.4; ctx.save(); ctx.translate(-150,0); ctx.rotate(r); box(-20,-110,40,150,12,'#cfd6e8'); fc(0,-130,46,'#cfd6e8'); fc(0,-130,18,C.tile); ctx.restore(); tx('OFF',-150,130,34,C.giallo,'800');
  grp(220,0,1,A(.85),()=>{ fc(0,0,130,C.tile); box(-90,-14,160,28,8,'#fff'); box(50,-14,30,28,4,ORANGE); for(let i=0;i<3;i++){ const f=(u*.8+i/3)%1; fc(95+f*20,-30-f*60,8+f*10,`rgba(207,214,232,${1-f})`);} vieto(0,0,110,1); }); },
'telefono-posizione'({u,A}){ phone(-200,0,.95,{ring:true,u}); grp(210,-20,1,A(.35),()=>{ box(-170,-170,340,340,30,'#cfe3d0'); ln([[-170,40],[170,-20]],'#fff',22); ln([[-40,-170],[20,170]],'#fff',18); const b=Math.abs(Math.sin(u*3))*14; ctx.fillStyle=RED; ctx.beginPath(); ctx.arc(0,-40-b,40,Math.PI,0); ctx.lineTo(0,30-b); ctx.closePath(); ctx.fill(); fc(0,-40-b,15,'#fff'); }); },
casco({u,A}){ bust(0,190,.85,{head:{mouth:'flat'},over(){ fc(0,-205,128,'#2b3560'); ctx.save(); ctx.beginPath(); ctx.arc(0,-205,128,0,TAU); ctx.clip(); box(-90,-250,180,110,40,'rgba(159,216,240,.55)'); ctx.restore(); arc(0,-205,128,0,TAU,'#e8702a',10); }}); grp(270,-120,1,A(.3),()=>{ handTop(0,0,.6); vieto(0,-60,100,1); }); },
svenimento({u}){ const ph=(u%3.2)/3.2; const rot=ph<.35?0:Math.min(1,(ph-.35)/.25)*1.45; ctx.save(); ctx.translate(-60,170); ctx.rotate(-rot); stick(0,-130,1.6,{}); ctx.restore(); ground(178); if(ph>.35&&ph<.6){ for(let i=0;i<3;i++) arc(-40,0,60+i*30,-2.4,-1.2,'rgba(242,228,51,.6)',6); } },
'pre-sincope'({u,A}){ const w=Math.sin(u*2)*.06; ctx.save(); ctx.rotate(w); bust(0,190,.82,{head:{mouth:'flat',pale:true,closed:A(.55)>.5},over(){ for(let i=0;i<4;i++){ const yy=-300+((u*90+i*37)%120); drop(-80+i*50,yy,.35,C.ciano);} }}); ctx.restore();
  grp(0,-170,1,A(.55),()=>{ for(let i=0;i<3;i++){ const a=u*2+i*2.1; ctx.fillStyle=C.giallo; ctx.beginPath(); for(let j=0;j<8;j++){const r=j%2?6:16,b=j*Math.PI/4; ctx.lineTo(Math.cos(a)*170+Math.cos(b)*r,-60+Math.sin(a)*30+Math.sin(b)*r);} ctx.fill(); } });
  grp(250,-40,1,A(.85),()=>{ for(let i=0;i<3;i++){ const f=(u*1.5+i/3)%1; arc(-40,0,30+f*60,-.6,.6,`rgba(255,255,255,${1-f})`,6);} }); },
contromanovre({u,A}){ grp(-300,0,1,A(.3),()=>{ panel(0,0,260,420,true,'gambe strette'); ctx.save(); ctx.translate(0,-30); ln([[0,-20],[0,60]],VS,40); fc(0,-62,26,SK); ln([[-12,60],[18,140]],PANT,20); ln([[12,60],[-18,140]],PANT,20); ln([[-24,-10],[-20,50]],VS,17); ln([[24,-10],[20,50]],VS,17); const s=(u*2%1)<.5; if(s) arc(0,100,50,-.5,.5,C.giallo,6); ctx.restore(); });
  grp(0,0,1,A(.6),()=>{ panel(0,0,260,420,true,'accovacciati'); ctx.save(); ctx.translate(0,40); ln([[0,-60],[10,10]],VS,40); fc(0,-102,26,SK); ln([[10,10],[50,30],[30,90]],PANT,20); ln([[-24,-50],[30,0]],VS,17); ctx.restore(); });
  grp(300,0,1,A(.88),()=>{ panel(0,0,260,420,true,'sdraiati'); ctx.save(); ctx.translate(-40,60); ctx.scale(.3,.3); lying(0,0,1,{legsUp:true}); box(400,-170,140,170,12,'#6b7491'); ctx.restore(); }); },
'gambe-su'({u,A}){ box(200,70,130,150,12,'#6b7491'); lying(-120,220,.8,{legsUp:true});
  const a=A(.7); if(a>0){ ctx.save(); ctx.globalAlpha*=clamp(a); const f=(u*.8)%1; ctx.setLineDash([16,14]); ctx.lineDashOffset=-u*60; ctx.strokeStyle=C.giallo; ctx.lineWidth=7; ctx.beginPath(); ctx.moveTo(240,-40); ctx.quadraticCurveTo(0,-160,-330,-20); ctx.stroke(); ctx.restore(); } },
timer1({u,p,A}){ const s=Math.min(60,Math.floor(p*75)); timer(-160,0,170,p*1.25,s+'″',{sub:'secondi',size:96}); grp(240,0,1,A(.8),()=>phone(0,0,.85,{ring:true,u})); },
lattante({u}){ babyFace(0,-20,190); const f=(u*.8)%1; heartP(250,-200,.5); ctx.fillStyle=`rgba(242,228,51,${.5+.5*Math.sin(u*4)})`; ctx.fill(); },
'lattante-blu'({u,p,A}){ const b=A(.8)>.5; babyFace(0,0,180,{blue:b,mouth:'o'}); grp(-260,-150,1,A(.2),()=>{ ln([[-30,-30],[30,30]],C.giallo,10); ln([[30,-30],[-30,30]],C.giallo,10); tx('pianto',0,70,30,'#fff','600'); }); grp(260,-150,1,A(.5),()=>{ ln([[-30,-30],[30,30]],C.giallo,10); ln([[30,-30],[-30,30]],C.giallo,10); tx('respiro',0,70,30,'#fff','600'); }); },
'no-dita'({u,A}){ babyFace(-80,0,170,{mouth:'o'}); grp(170,40,1,A(.5),()=>{ hand(0,0,.8,-1.2); vieto(0,0,130,1); }); for(let i=0;i<3;i++){ const f=(u*1.2+i/3)%1; arc(-80,80,160+f*60,Math.PI*.15,Math.PI*.35,`rgba(255,255,255,${1-f})`,6);} },
'lattante-pacche'({u,A}){ const ph=(u*1.1)%1, hit=ph<.18; ctx.save(); ctx.translate(-30,40); ctx.rotate(-.22);
  ln([[-330,40],[230,40]],RS,90); fe(-360,40,60,52,SK);
  ctx.save(); ctx.translate(-30,-30); box(-150,-50,260,90,40,BABY); fc(-200,-10,60,SK); ctx.fillStyle='#8a6a4a'; ctx.beginPath(); ctx.arc(-200,-10,62,Math.PI*1.2,Math.PI*1.9); ctx.fill(); ln([[90,-20],[200,-10]],BABY,40); ln([[90,20],[180,40]],BABY,40); ctx.restore();
  const hy=hit?-90:-90-80*Math.sin(Math.min(1,(ph-.18)/.82)*Math.PI); ctx.save(); ctx.translate(-20,hy); hand(0,-40,.55,Math.PI); ctx.restore();
  if(hit){ const r=ph/.18; arc(-20,-80,30+r*40,0,TAU,`rgba(242,228,51,${1-r})`,8); } ctx.restore();
  const n=Math.floor(Math.max(0,u-PRE)*1.1)%5+1; grp(360,-180,1,A(.8),()=>{ fc(0,0,70,C.giallo); tx(String(n),0,4,70,C.navy,'800','P'); tx('di 5',0,100,28,'#fff','600'); }); },
'lattante-torace'({u,A}){ const ph=(u*1.0)%1, d=ph<.3?Math.sin(ph/.3*Math.PI)*14:0; ctx.save(); ctx.translate(0,40); ctx.rotate(-.18);
  ln([[-380,70],[260,70]],PANT,120); babyLying(0,30,1.3,d);
  ctx.save(); ctx.translate(-10,-90+d*1.3); box(-80,-30,160,70,30,SK); box(-90,-20,30,90,15,SKD); box(60,-20,30,90,15,SKD); fe(-18,30,14,20,SK); fe(18,30,14,20,SK); ctx.restore(); ctx.restore();
  if(d>3) arrow(-10,-260,-10,-200,C.giallo,9);
  const n=Math.floor(Math.max(0,u-PRE))%5+1; grp(360,-180,1,A(.85),()=>{ fc(0,0,70,C.giallo); tx(String(n),0,4,70,C.navy,'800','P'); tx('di 5',0,100,28,'#fff','600'); }); },
'alterna-lattante'({u}){ const ph=(u%2.4)<1.2?0:1;
  [[-190,'pacche','sulla schiena',0],[190,'compressioni','sul torace',1]].forEach(([x,l,s2,i])=>{ const on=ph===i; fc(x,-40,150,on?C.giallo:C.tile); tx('5',x,-60,190,on?C.navy:C.giallo,'600','P'); tx(l,x,150,40,'#fff','700'); tx(s2,x,200,30,'#aab3cc','500'); });
  arc(0,-40,40,-2.5,.6,C.ciano,8); arc(0,-40,40,.64,3.7,C.ciano,8); },
'rcp-lattante-mini'({u,A}){ const d=12*(0.5+0.5*Math.cos(TAU*u*110/60)); box(-400,90,700,40,10,'#6b7491'); babyLying(-80,90,1.1,d); ctx.save(); ctx.translate(-90,-10+d); box(-70,-26,140,60,26,SK); ctx.restore();
  grp(300,-120,1,A(.5),()=>{ fc(0,0,90,C.tile); tx('5',0,-6,90,C.giallo,'800','P'); tx('soffi',0,60,28,'#fff','600'); }); },
'bimbo-continua'({u,A}){ const d=12*(0.5+0.5*Math.cos(TAU*u*110/60)); box(-400,90,700,40,10,'#6b7491'); babyLying(-80,90,1.1,d); ctx.save(); ctx.translate(-90,-10+d); box(-70,-26,140,60,26,SK); ctx.restore();
  grp(300,-120,1,A(.4),()=>clockFace(0,0,100,(u*2)%12,(u*60)%60)); },
trasporti({u,A}){ ln([[-440,170],[440,170]],'#3a4570',10); for(let i=0;i<6;i++){ const x=((i*180-u*400)%1080+1080)%1080-540; ln([[x,200],[x+80,200]],'rgba(255,255,255,.35)',8); }
  grp(80,90,1,1,()=>ambulance(0,0,1.05,u)); grp(-310,-150,1,A(.75),()=>{ fc(0,0,90,C.tile); fc(0,-30,22,'#fff'); ln([[0,-8],[0,40]],'#fff',16); arc(0,50,36,.2,2.9,'#fff',10); }); },
uva({u,A}){ const s=A(.75); const cx=-170; for(let i=0;i<4;i++){ const a=i*Math.PI/2+Math.PI/4, off=clamp(s)*22; ctx.save(); ctx.translate(cx+Math.cos(a)*off,Math.sin(a)*off); ctx.fillStyle='#7cc46a'; ctx.beginPath(); ctx.moveTo(0,0); ctx.arc(0,0,110,a-Math.PI/4,a+Math.PI/4); ctx.closePath(); ctx.fill(); ctx.restore(); }
  fe(cx-30,-40,20,12,'rgba(255,255,255,.4)'); tx('in 4, per lungo',cx,170,30,'#fff','700');
  grp(220,0,1,A(.25),()=>{ fc(0,0,140,C.tile); fc(-40,-30,30,'#cfd6e8'); fc(40,-20,22,'#e0b84a'); box(-20,30,50,30,8,RED); vieto(0,0,125,1); }); },
'bimbo-cuore'({u}){ stick(-150,60,2,{shirt:'#f2a541',hairCol:'#8a6a4a'}); const b=1+Math.max(0,Math.sin(u*7))*.06; ctx.strokeStyle=C.giallo; ctx.lineWidth=14; heartP(190,-30,1.3*b); ctx.stroke(); },
'respiro-bimbo'({u,p,A}){ ctx.save(); ctx.scale(.9,.9); babyLying(-60,230,1.5,0); ctx.restore(); const s=Math.min(10,Math.floor(p*14)+1); timer(300,-120,110,p*1.4,s+'″',{size:64}); eye(-150,-130,.5,1); },
ventila5({u,p,A}){ const n=Math.min(5,Math.floor(p*6)+1); const rise=Math.max(0,Math.sin(((u-PRE)%1.1)/1.1*Math.PI))*14;
  box(-420,140,600,30,10,'#6b7491'); ctx.save(); ctx.translate(-150,140); box(-60,-110-rise,280,110+rise,40,'#f2a541'); fc(-130,-70,70,SK); ctx.fillStyle='#8a6a4a'; ctx.beginPath(); ctx.arc(-130,-70,72,Math.PI*.55,Math.PI*1.4); ctx.fill(); fe(-92,-132,10,8,SKD); ctx.restore();
  for(let i=0;i<3;i++){ const f=((u*1.2)+i/3)%1; arc(-240,-140,20+f*40,1.2,2.2,`rgba(255,255,255,${1-f})`,6);} grp(310,-140,1,A(.2),()=>{ fc(0,0,90,C.giallo); tx(String(n),0,4,90,C.navy,'800','P'); tx('di 5',0,120,28,'#fff','600'); }); },
'mani-bimbo'({u,A}){ grp(-220,0,1,A(.3),()=>{ panel(0,0,380,480,true,'lattante'); box(-90,-150,180,230,60,BABY); ctx.save(); ctx.translate(0,-20); box(-150,-40,60,110,26,SK); box(90,-40,60,110,26,SK); fe(-20,0,16,26,SKD); fe(20,0,16,26,SKD); ctx.restore(); });
  grp(220,0,1,A(.8),()=>{ panel(0,0,380,480,true,'bambino'); box(-110,-170,220,260,60,'#f2a541'); ctx.save(); ctx.translate(0,-40); ln([[0,-20],[60,-200]],RS,60); box(-46,-30,92,70,30,SK); ctx.restore(); }); },
'rcp-lattante-sim'({u}){ const c=compAt(u), d=c*18; box(-420,170,620,36,10,'#6b7491'); babyLying(-120,170,1.5,d/1.5);
  ctx.save(); ctx.translate(-120,-10+d); box(-100,-36,200,80,32,SK); box(-112,-26,34,110,17,SKD); box(78,-26,34,110,17,SKD); fe(-20,40,16,24,SK); fe(20,40,16,24,SK); ctx.restore(); ln([[-210,-60+d],[-300,-220]],RS,50); ln([[-30,-60+d],[60,-220]],RSD,50);
  contatore(320,-150,u); gauge(-400,-260,c,'≈ 4 cm'); },
'ventila-bimbo'({u,A}){ grp(0,-160,1,A(.15),()=>{ box(-400,-90,800,180,40,C.tile); tx('30',-200,-10,110,C.giallo,'800','P'); tx(':',0,-20,90,'#fff','800'); tx('2',170,-10,110,C.giallo,'800','P'); tx('compressioni',-200,62,26,'#fff','600'); tx('soffi',170,62,26,'#fff','600'); });
  grp(0,40,1,A(.55),()=>{ box(-400,-60,800,120,30,'#fff'); tx('con un corso pediatrico: 15 e 2',0,2,36,C.navy,'700'); });
  grp(0,200,1,A(.88),()=>{ box(-400,-50,800,100,30,'rgba(255,255,255,.12)'); tx('se non riesci a soffiare: solo compressioni',0,2,32,'#fff','600'); }); },
'dae-bimbo'({u,A}){ grp(-260,10,1,A(.2),()=>{ panel(0,0,320,460,true,'davanti'); box(-100,-170,200,280,60,SK); fc(0,-210,60,SK); ctx.save(); ctx.translate(-10,-40); box(-45,-60,90,120,20,'#fff'); bolt(0,0,.8,ORANGE); ctx.restore(); });
  grp(80,10,1,A(.8),()=>{ panel(0,0,320,460,true,'dietro'); box(-100,-170,200,280,60,SK); fc(0,-210,60,'#8a6a4a'); ctx.save(); ctx.translate(0,-80); box(-45,-60,90,120,20,'#fff'); bolt(0,0,.8,ORANGE); ctx.restore(); });
  grp(360,-60,1,A(.4),()=>{ daeBox(0,0,.6,{on:true,u}); box(-60,80,120,50,20,C.giallo); tx('bimbo',0,106,26,C.navy,'800'); }); },
osso({u,p}){ ctx.save(); ctx.rotate(-.35); const k=clamp(u/1.5); box(-260,-34,520,68,34,'#f3ead8'); [[-270,0],[270,0]].forEach(([x,y])=>{ fc(x,y-34,48,'#f3ead8'); fc(x,y+34,48,'#f3ead8'); });
  ctx.strokeStyle=RED; ctx.lineWidth=10; ctx.beginPath(); ctx.moveTo(-10,-40); ctx.lineTo(10,-10*k); ctx.lineTo(-14,10*k); ctx.lineTo(8,40*k); ctx.stroke(); ctx.restore();
  for(let i=0;i<3;i++){ const f=(u*1.4+i/3)%1; arc(0,0,90+f*80,-1.2,-.4,`rgba(242,228,51,${1-f})`,6);} },
'arto-gonfio'({u,p,A}){ forearm(80); const sw=A(.3); fe(60,70,90*(.6+.4*clamp(sw)),56*(.6+.4*clamp(sw)),'rgba(122,90,160,.55)'); const pulse=.5+.5*Math.sin(u*6);
  for(let i=0;i<4;i++){ const a=-Math.PI/2+(i-1.5)*.5; ln([[60+Math.cos(a)*110,70+Math.sin(a)*110],[60+Math.cos(a)*(150+pulse*20),70+Math.sin(a)*(150+pulse*20)]],C.giallo,8); } },
'arto-no'({u,A}){ ctx.save(); ctx.translate(-60,60); ln([[-380,0],[0,0]],VS,110); ln([[0,0],[200,-160]],SK,92); fe(230,-190,56,50,SK); ctx.restore(); grp(160,60,1,A(.3),()=>{ handTop(-60,0,.55); handTop(60,0,.55); }); vieto(170,-160,90,A(.35)); },
fascia({u,A}){ bust(0,190,.85,{R:[[150,110],[10,90]],head:{mouth:'flat'},over(){ const a=A(.6); if(a>0){ ctx.save(); ctx.globalAlpha*=clamp(a); poly([[-130,-60],[110,40],[-60,170]],'#fff'); ln([[-130,-60],[110,40]],'#cfd6e8',10); ctx.restore(); } }}); },
'ghiaccio-arto'({u,p,A}){ forearm(110); grp(60,40,1,A(.3),()=>{ box(-110,-60,220,120,50,'#cfd6e8'); cube(-30,-10,.6,'#dff3fb'); cube(30,-10,.6,'#dff3fb'); }); grp(300,-160,1,A(.8),()=>timer(0,0,100,p,Math.min(20,Math.floor(p*20)+1)+'′',{size:56})); },
esposta({u,A}){ forearm(100); fe(60,90,50,26,RED); const g=A(.3); if(g>0) grp(60,80,1,g,()=>gauze(0,0,190,120)); grp(60,-120,1,A(.6),()=>{ arrow(0,-60,0,20,C.giallo,10); vieto(0,-20,80,1); }); },
distorsione({u,A}){ box(-120,110,360,90,40,'#6b7491'); ln([[-440,40],[60,100]],PANT,110); ln([[60,100],[200,110]],SK,84); box(170,30,80,120,30,SK); grp(140,40,1,A(.3),()=>{ box(-80,-50,160,90,40,'#cfd6e8'); }); grp(-270,-170,1,A(.5),()=>{ arrow(0,60,0,-40,C.giallo,10); }); grp(300,-170,1,A(.85),()=>{ fc(0,0,70,C.tile); steto(0,0,.4); }); },
termometro({u}){ box(-40,-260,80,400,40,'#fff'); fc(0,170,80,'#fff'); fc(0,170,60,C.ciano); box(-20,-40,40,210,20,C.ciano); for(let i=0;i<8;i++) ln([[40,-220+i*40],[70,-220+i*40]],'#cfd6e8',5); snow(u,30); },
brividi({u,A}){ const j=Math.sin(u*40)*5; bust(0,190,.82,{jx:j,head:{mouth:'flat',pale:A(.3)>.5},L:[[-120,90],[60,40]],R:mir([[-120,90],[60,40]])}); snow(u,18); grp(260,-180,1,A(.15),()=>tx('brrr',0,0,56,'#fff','800','P')); },
'casa-caldo'({u,A}){ snow(u,20); house(0,40,1.2); ctx.save(); ctx.globalAlpha*=.5+.3*Math.sin(u*3); fc(-102,40,60,'rgba(242,165,65,.5)'); fc(102,40,60,'rgba(242,165,65,.5)'); ctx.restore(); grp(-330,140,1,A(.3),()=>{ stick(0,0,1.2,{}); arrow(60,0,140,0,C.giallo,8); }); },
tazza({u,A}){ grp(-170,30,1,A(.3),()=>{ box(-90,-80,180,170,30,'#fff'); arc(100,0,40,-1.4,1.4,'#fff',16); box(-80,-70,160,30,10,'#8a5a3a'); for(let i=0;i<3;i++){ const f=(u*.7+i/3)%1; ctx.strokeStyle=`rgba(255,255,255,${1-f})`; ctx.lineWidth=6; ctx.beginPath(); ctx.moveTo(-40+i*40,-100-f*60); ctx.quadraticCurveTo(-20+i*40,-130-f*60,-40+i*40,-160-f*60); ctx.stroke(); } });
  grp(200,30,1,A(.75),()=>{ fc(0,0,130,C.tile); ctx.beginPath(); ctx.moveTo(-50,-80); ctx.lineTo(50,-80); ctx.quadraticCurveTo(50,10,0,20); ctx.quadraticCurveTo(-50,10,-50,-80); ctx.fillStyle='#d9473d'; ctx.fill(); ln([[0,20],[0,80]],'#fff',8); ln([[-40,80],[40,80]],'#fff',8); vieto(0,0,120,1); }); },
'mano-gelo'({u,A}){ hand(-160,40,1.1,0); ctx.save(); ctx.translate(-160,40); ctx.scale(1.1,1.1); for(let i=0;i<4;i++) box(-56+i*29,-150+Math.abs(i-1.5)*14,26,40,13,'#eef2f8'); ctx.restore();
  grp(200,-120,1,A(.3),()=>{ arrow(-60,0,60,0,C.giallo,8); arrow(60,30,-60,30,C.giallo,8); vieto(0,15,80,1); }); grp(200,120,1,A(.55),()=>{ for(let i=0;i<3;i++) drop(-30+i*30,0,.8,ORANGE); vieto(0,0,80,1); }); },
'persone-freddo'({u,A}){ snow(u,24); box(-300,100,420,30,10,'#6b7491'); ln([[-280,130],[-280,200]],'#6b7491',14); ln([[100,130],[100,200]],'#6b7491',14); stick(-90,-10,1.3,{shirt:'#6b7491'}); box(-170,10,170,110,30,ORANGE); grp(300,-60,1,A(.85),()=>phone(0,0,.8,{ring:true,u})); },
co({u}){ house(0,60,1.2); ctx.save(); ctx.setLineDash([14,12]); ctx.strokeStyle='rgba(207,214,232,.7)'; ctx.lineWidth=6; const o=Math.sin(u*1.5)*10; ctx.beginPath(); ctx.ellipse(o,-20,250,120,0,0,TAU); ctx.stroke(); ctx.restore(); tx('CO',o,-20,100,'rgba(255,255,255,.85)','800','P'); },
'co-fonti'({u,A}){ const it=[['stufa',.15],['camino',.22],['caldaia',.3],['braciere',.55],['motore',.85]];
  it.forEach(([k,t],i)=>grp(-360+i*180,0,1,A(t),()=>{ fc(0,0,80,C.tile);
    if(k==='stufa'){ box(-40,-40,80,90,10,'#6b7491'); box(-25,-20,50,40,8,ORANGE); ln([[0,-40],[0,-70]],'#6b7491',12); }
    if(k==='camino'){ box(-50,-50,100,100,6,'#8a5a3a'); box(-30,-10,60,60,6,'#1a1f36'); drop(0,30,.4,ORANGE); }
    if(k==='caldaia'){ box(-35,-55,70,110,12,'#fff'); fc(0,-15,14,C.ciano); box(-20,20,40,8,4,'#aab3cc'); }
    if(k==='braciere'){ fe(0,20,50,22,'#6b7491'); for(let j=0;j<3;j++) drop(-20+j*20,-5,.4,ORANGE); }
    if(k==='motore'){ car(0,10,.3,'#cfd6e8'); }
    tx(k,0,110,24,'#fff','600'); })); },
'co-segni'({u,A}){ bust(-120,200,.75,{head:{mouth:'sad',pale:true,closed:true}}); grp(-120,-150,1,A(.1),()=>{ for(let i=0;i<4;i++){ const a=-Math.PI/2+(i-1.5)*.4; ln([[Math.cos(a)*120,Math.sin(a)*120+20],[Math.cos(a)*150,Math.sin(a)*150+20]],C.giallo,7);} });
  grp(260,60,1,A(.7),()=>{ fe(0,40,110,60,'#c49a6c'); fc(-90,-20,50,'#c49a6c'); fe(-120,-60,18,30,'#8a6a4a',-.4); ln([[-110,-24],[-96,-24]],C.navy,6); for(let i=0;i<2;i++){ const f=(u*.6+i/2)%1; tx('z',-40+f*60,-80-f*80,36,`rgba(255,255,255,${1-f})`,'700'); } }); },
rilevatore({u,A}){ ln([[-440,-260],[440,-260]],'#55607f',16); grp(-150,-170,1,A(.3),()=>{ fe(0,0,130,60,'#fff'); fe(0,-6,100,40,'#eef2f8'); fc(60,0,12,(u*1%1)<.2?'#2fbf71':'#a5e3c2'); tx('CO',-30,0,34,C.navy,'800'); });
  grp(220,70,1,A(.35),()=>{ box(-130,-130,260,250,20,'#fff'); box(-130,-130,260,60,20,RED); tx('1 volta',0,10,44,C.navy,'800'); tx('all\'anno',0,60,32,C.navy,'600'); spunta(110,110,40,1); }); },
'no-braciere'({A}){ [[-300,.2,()=>{ fe(0,20,60,26,'#6b7491'); for(let j=0;j<3;j++) drop(-24+j*24,-5,.45,ORANGE); }],[0,.5,()=>{ box(-60,-50,120,100,12,'#cfd6e8'); box(-40,-30,80,40,6,'#24305c'); fc(-30,70,8,'#6b7491'); }],[300,.85,()=>{ car(0,10,.35,'#cfd6e8'); box(-90,-80,180,20,4,'#6b7491'); }]]
  .forEach(([x,t,f])=>grp(x,0,1,A(t),()=>{ fc(0,0,130,C.tile); f(); vieto(0,0,120,A(t+.06)); })); },
'mani-cuore'({u}){ const b=1+Math.sin(u*3)*.04; ctx.save(); ctx.scale(b,b); ctx.fillStyle=RED; heartP(0,-10,1.6); ctx.fill(); ctx.restore(); hand(-220,140,.9,.9); hand(220,140,.9,-.9); },
grazie({u,A}){ tx('Grazie',0,-180,140,C.giallo,'600','P'); [[-300,'#f3b9c4',{hair:'long'}],[-100,RS,{}],[100,RS,{hairCol:GRAYH}],[300,'#f2a541',{}]].forEach(([x,col,h],i)=>grp(x,120,1,A(.1+i*.1),()=>bust(0,40,.42,{shirt:col,head:{...h,mouth:'smile'}})));
  for(let i=0;i<16;i++){ const f=(u*.4+hash(i))%1; fc(-400+hash(i+2)*800,-300+f*500,6,['#f2e433','#00a5dc','#e8702a'][i%3]); } },
spesa({u,A}){ grp(-170,40,1,A(.75),()=>{ bag(0,0,1.3,'#e9d3a8'); fc(-30,-120,40,RED); box(0,-170,40,100,16,'#e9b871'); box(-70,-140,40,80,10,'#7cc46a'); });
  grp(200,-80,1,A(.4),()=>{ bubble(0,-40,220,110,'',0,-60); for(let i=0;i<3;i++) fc(-50+i*50,-40,12,C.navy); bubble(60,120,200,100,'',0,100); heartP(60,130,.3); ctx.fillStyle=RED; ctx.fill(); }); },
eventi({u,A}){ ground(220); ctx.fillStyle='#fff'; ctx.beginPath(); ctx.moveTo(-280,-60); ctx.lineTo(0,-200); ctx.lineTo(280,-60); ctx.closePath(); ctx.fill(); box(-280,-60,560,30,6,C.ciano); ln([[-260,-30],[-260,220]],'#cfd6e8',12); ln([[260,-30],[260,220]],'#cfd6e8',12); cross(0,60,.9,RED);
  for(let i=0;i<5;i++){ const x=-420+i*30; ln([[x,-280],[x+20,-270]],C.giallo,6);} grp(330,140,1,A(.7),()=>ambulance(0,0,.45,u)); },
persone({A}){ [[-330,'#f3b9c4',{hair:'long'},'16'],[-110,RS,{},''],[110,'#9fd8c0',{},''],[330,RS,{hairCol:GRAYH,glasses:true},'80']].forEach(([x,col,h,l],i)=>grp(x,20,1,A(.1+i*.08),()=>{ bust(0,60,.5,{shirt:col,head:{...h,mouth:'smile'}}); if(l) { fc(0,-230,46,C.giallo); tx(l,0,-228,40,C.navy,'800'); } })); },
passi3({u,A}){ ctx.save(); ctx.setLineDash([16,14]); ln([[-300,0],[300,0]],'rgba(242,228,51,.6)',6); ctx.restore();
  [[-300,.2,'1',()=>phone(0,0,.3,{num:'',label:''})],[0,.5,'2',()=>{ box(-36,-46,72,92,8,'#fff'); for(let i=0;i<4;i++) box(-24,-30+i*18,48,6,3,'#aab3cc'); }],[300,.8,'3',()=>{ stick(0,10,.6,{shirt:RS}); }]].forEach(([x,t,n,f])=>grp(x,0,1,A(t),()=>{ fc(0,0,110,C.tile); f(); fc(80,-80,32,C.giallo); tx(n,80,-78,36,C.navy,'800'); })); },
polmoni({u}){ const b=1+Math.sin(u*2)*.05; ctx.save(); ctx.scale(b,b); [-1,1].forEach(s=>{ ctx.fillStyle='#e48a9a'; ctx.beginPath(); ctx.ellipse(s*120,40,110,190,s*.12,0,TAU); ctx.fill(); }); ctx.restore(); ln([[0,-260],[0,-80]],'#cfd6e8',30); ln([[0,-80],[-80,-20]],'#cfd6e8',20); ln([[0,-80],[80,-20]],'#cfd6e8',20); },
'asma-segni'({u,A}){ bust(0,190,.82,{head:{mouth:'o'},L:[[-150,110],[-10,30]],R:mir(POSE.down)}); const f=(u*1.4)%1; grp(-280,-60,1,A(.3),()=>{ for(let i=0;i<3;i++) arc(0,0,30+((f+i/3)%1)*70,-.6,.6,'rgba(255,255,255,.7)',6); tx('fischi',0,90,30,'#fff','600'); });
  grp(0,190,1,A(.45),()=>{ ctx.save(); ctx.scale(.82,.82); ln([[-150,40],[150,40]],'rgba(217,71,61,.6)',16); ctx.restore(); }); },
'seduto-avanti'({u,A}){ box(60,40,320,24,10,'#6b7491'); ln([[340,64],[340,250]],'#6b7491',16); box(-200,90,200,24,10,'#6b7491'); ln([[-180,114],[-180,250]],'#6b7491',14); ln([[-20,114],[-20,250]],'#6b7491',14);
  ln([[-60,80],[90,90],[90,240]],PANT,56); ctx.save(); ctx.translate(-80,80); ctx.rotate(.45); box(-60,-280,124,300,52,VS); fc(-6,-340,66,SK); ctx.fillStyle=HAIR; ctx.beginPath(); ctx.arc(-6,-340,68,Math.PI*1.25,Math.PI*.45); ctx.fill(); ctx.restore();
  ln([[0,-120],[150,20],[260,30]],VSD,44); ln([[0,-120],[150,20],[260,30]],VS,38); spunta(-300,-200,50,A(.3)); },
'respira-calmo'({u}){ const ph=(Math.sin(u*1.1)+1)/2; fc(0,0,120+ph*90,'rgba(0,165,220,.25)'); fc(0,0,100+ph*70,'rgba(0,165,220,.45)'); tx(ph>.5?'inspira':'espira',0,4,50,'#fff','700'); },
inalatore({u,A}){ ctx.save(); ctx.translate(-60,0); ctx.rotate(-.2); box(-60,-200,120,260,30,C.ciano); box(-70,40,200,90,30,'#3a8ac0'); box(-40,-240,80,60,14,'#2b6c99'); ctx.restore(); const a=A(.3); if(a>0){ for(let i=0;i<5;i++){ const f=(u*1.4+i/5)%1; fc(170+f*160,60-f*30+Math.sin(i)*20,10+f*24,`rgba(220,240,255,${(1-f)*.8})`); } } },
batteria({u}){ fc(0,0,180,'#aab3cc'); fc(0,0,150,'#cfd6e8'); fe(-50,-60,60,30,'rgba(255,255,255,.6)',-.5); tx('+',0,10,140,'#6b7491','800'); tx('3V',0,120,40,'#6b7491','800'); },
esofago({u,A}){ ctx.save(); ctx.translate(-80,0); fc(0,-140,110,SK); ctx.fillStyle='#8a6a4a'; ctx.beginPath(); ctx.arc(0,-140,112,Math.PI*1.1,Math.PI*1.95); ctx.fill(); box(-50,-40,100,280,40,SK); ln([[-10,-80],[-10,260]],'#d98a7a',28); const g=A(.6); fc(-10,80,24,'#aab3cc'); if(g>0){ fc(-10,80,40+Math.sin(u*6)*8,`rgba(217,71,61,${.45*clamp(g)})`); } ctx.restore(); grp(260,-60,1,A(.6),()=>timer(0,0,110,clamp(u/4),'ore',{size:48})); },
'bimbo-dubbio'({u,A}){ babyFace(-80,20,160,{mouth:'flat'}); grp(230,-150,1,A(.2),()=>bubble(0,0,170,110,'?',70,-60)); grp(260,60,1,A(.5),()=>{ for(let i=0;i<3;i++) drop(-30+i*30,0,.5,'#cfe9f5'); }); },
'confezione-batt'({A}){ box(-200,-160,400,320,20,'#fff'); box(-200,-160,400,70,20,C.ciano); tx('CR2032',0,-124,36,'#fff','800'); for(let i=0;i<3;i++){ fc(-120+i*120,40,46,'#cfd6e8'); fc(-120+i*120,40,46,'rgba(255,255,255,.3)'); } grp(320,-60,1,A(.6),()=>{ fc(0,0,60,'#aab3cc'); }); },
calamite({u,A}){ const g=clamp(Math.sin(u*1.5)*.5+.5); [-1,1].forEach(s=>{ ctx.save(); ctx.translate(s*(90+90*g),0); box(-50,-70,100,140,20,s<0?RED:C.ciano); box(-50,-70,100,30,10,'#cfd6e8'); ctx.restore(); });
  for(let i=0;i<3;i++) arc(0,0,40+i*40,-0.5,0.5,'rgba(242,228,51,.5)',5); },
giocattolo({u,A}){ car(-100,40,1.2,'#f2a541'); grp(220,-60,1,A(.3),()=>{ box(-90,-60,180,120,14,'#cfd6e8'); box(-70,-40,140,80,10,'#6b7491'); fc(0,0,16,'#cfd6e8'); ln([[-10,0],[10,0]],C.navy,4); ctx.save(); ctx.rotate(u*2); ln([[0,0],[0,-120]],'#e0b84a',12); ctx.restore(); }); },
caduta({u}){ ground(240); ctx.save(); ctx.translate(-40,240); ctx.rotate(-1.4); stick(0,-130,1.5,{hairCol:GRAYH,shirt:'#bfc8de'}); ctx.restore(); ln([[200,240],[300,60]],'#8a5a3a',14); arc(305,50,26,Math.PI,0,'#8a5a3a',14); },
'no-tirare'({u,A}){ ctx.save(); ctx.translate(-40,240); ctx.rotate(-1.4); stick(0,-130,1.5,{hairCol:GRAYH,shirt:'#bfc8de'}); ctx.restore(); grp(-60,-60,1,A(.3),()=>{ arrow(0,60,0,-80,C.giallo,10); vieto(0,0,110,1); }); },
rialzarsi({u,A}){ [[-300,.3,'su un fianco',()=>{ ctx.save(); ctx.scale(.3,.3); ctx.translate(0,200); pls(0,0,1); ctx.restore(); }],[0,.5,'in ginocchio',()=>{ ctx.save(); ctx.translate(0,40); ln([[0,-60],[30,10]],'#bfc8de',36); fc(-10,-100,24,SK); ln([[30,10],[70,60],[0,70]],PANT,18); ln([[-10,-40],[-40,40]],'#bfc8de',14); ctx.restore(); }],[300,.8,'con la sedia',()=>{ box(30,-10,70,14,6,'#6b7491'); ln([[90,-10],[90,-90]],'#6b7491',10); ln([[40,4],[40,90]],'#6b7491',8); ln([[90,4],[90,90]],'#6b7491',8); stick(-30,0,.75,{hairCol:GRAYH,shirt:'#bfc8de'}); }]]
  .forEach(([x,t,l,f])=>grp(x,0,1,A(t),()=>{ panel(0,0,260,380,true,l); ctx.save(); ctx.translate(0,-30); f(); ctx.restore(); })); },
'ore-dopo'({u,A}){ clockFace(-160,0,170,(u*2)%12,(u*90)%60); grp(220,0,1,A(.4),()=>eye(0,0,1)); },
'casa-sicura'({u,A}){ [[-330,.15,()=>{ box(-70,-20,140,50,10,'#d98a7a'); vieto(0,0,90,1); }],[-110,.3,()=>{ fc(0,-20,40,C.giallo); fc(0,-20,70,'rgba(242,228,51,.25)'); box(-10,20,20,50,4,'#cfd6e8'); }],[110,.45,()=>{ box(-60,-14,120,28,14,'#cfd6e8'); box(-60,-40,20,80,8,'#6b7491'); box(40,-40,20,80,8,'#6b7491'); }],[330,.85,()=>phone(0,0,.32,{num:'112',label:''})]]
  .forEach(([x,t,f])=>grp(x,0,1,A(t),()=>{ fc(0,0,100,C.tile); f(); })); },
petardo({u}){ ctx.save(); ctx.rotate(-.5); box(-50,-180,100,300,20,RED); box(-50,-120,100,30,0,'#fff'); box(-50,40,100,30,0,'#fff'); ctx.restore(); const tip=[110,-190]; ln([[60,-160],tip],'#cfd6e8',6);
  for(let i=0;i<10;i++){ const a=hash(i+Math.floor(u*10))*TAU, r=20+hash(i*3+Math.floor(u*10))*40; ln([tip,[tip[0]+Math.cos(a)*r,tip[1]+Math.sin(a)*r]],C.giallo,4); } },
ce({u,A}){ fc(-160,0,170,'#fff'); tx('CE',-160,10,140,C.navy,'800'); grp(210,0,1,A(.6),()=>{ box(-150,-120,300,240,16,'#55607f'); box(-150,-150,300,50,10,C.ciano); for(let i=0;i<3;i++) box(-110+i*80,-60,50,110,8,[RED,C.giallo,'#7cc46a'][i]); }); },
'petardo-vieto'({u,A}){ ground(160); ctx.save(); ctx.translate(-60,130); ctx.rotate(1.4); box(-30,-90,60,180,14,RED); ctx.restore(); grp(80,-20,1,A(.3),()=>{ hand(0,0,.7,2.6); }); vieto(0,40,180,A(.35)); },
amputazione({u,A}){ fe(0,150,260,70,'#cfd6e8'); for(let i=0;i<8;i++) cube(-200+i*58,120+(i%2)*20,.55,'#dff3fb'); grp(0,-40,1,A(.3),()=>{ bag(0,0,1,'rgba(207,233,245,.85)'); box(-40,-10,80,30,14,SK); }); grp(300,-160,1,A(.85),()=>{ fc(0,0,60,C.tile); tx('!',0,4,70,C.giallo,'800','P'); }); },
'occhio-ferito'({u,A}){ eye(-180,-20,1.2); grp(-180,-200,1,A(.2),()=>{ hand(0,0,.5,Math.PI); vieto(0,30,90,1); }); grp(230,0,1,A(.7),()=>{ fe(0,0,140,100,'#fff'); fe(0,0,110,76,'#eef2f8'); ln([[-150,0],[-260,-30]],'#cfd6e8',14); ln([[150,0],[260,-30]],'#cfd6e8',14); }); },
'bimbi-lontano'({u,A}){ for(let i=0;i<3;i++){ const f=(u*.6+i/3)%1, x=150+i*110, y=-180+i*30; for(let j=0;j<12;j++){ const a=j/12*TAU; ln([[x+Math.cos(a)*f*20,y+Math.sin(a)*f*20],[x+Math.cos(a)*f*90,y+Math.sin(a)*f*90]],[C.giallo,C.ciano,ORANGE][i]+'',5); } }
  ground(200); stick(-300,80,1.3,{shirt:'#f2a541',hairCol:'#8a6a4a'}); stick(-200,80,1.7,{shirt:RS}); const a=A(.5); if(a>0){ ctx.save(); ctx.globalAlpha*=clamp(a); arrow(-120,140,120,140,C.giallo,8); arrow(120,140,-120,140,C.giallo,8); ctx.restore(); } },
cassetta({u}){ const o=clamp(u/1.5); box(-220,-60,440,280,30,'#fff'); cross(0,80,1,RED); ctx.save(); ctx.translate(-220,-60); ctx.rotate(-o*.5); box(0,-60,440,70,24,'#e3e7f1'); ctx.restore(); box(-60,-110,120,40,14,'#6b7491'); },
'cassetta-contenuto'({u,A}){ box(-160,40,320,200,26,'#fff'); cross(0,140,.7,RED);
  [[-330,-150,.1,()=>{ hand(0,0,.45,0,'#7b6fd6'); }],[-120,-220,.25,()=>gauze(0,0,140,90)],[120,-220,.45,()=>{ ln([[-40,-40],[40,40]],'#cfd6e8',12); ln([[40,-40],[-40,40]],'#cfd6e8',12); fc(-50,-50,20,RED); fc(50,-50,20,RED); }],[330,-150,.7,()=>{ box(-60,-50,120,100,16,'#9fd8f0'); tx('ICE',0,4,30,C.navy,'800'); }],[0,-60,.9,()=>{ box(-110,-20,220,40,8,'#e0b84a'); ln([[-110,0],[110,0]],'#f6e27a',6); }]]
  .forEach(([x,y,t,f])=>grp(x,y,1,A(t),()=>{ fc(0,0,90,C.tile); f(); })); },
'foglio-numeri'({u,A}){ box(-200,-250,400,480,20,'#fff'); tx('Numeri utili',0,-190,40,C.navy,'700','P');
  [['112',.3,RED],['Centro Antiveleni',.55,C.navy],['Medico',.85,C.navy]].forEach(([l,t,col],i)=>grp(0,-80+i*110,1,A(t),()=>{ box(-160,-40,320,80,16,'#eef2f8'); tx(l,0,2,l==='112'?54:34,col,'800'); })); },
'auto-kit'({u,A}){ car(-130,40,1.3,'#6b7491'); grp(250,-120,1,A(.55),()=>{ bust(0,60,.4,{shirt:'#d9e86a',shirtD:'#b8c94a',noArms:true,head:{mouth:'smile'}}); }); grp(250,150,1,A(.8),()=>{ poly([[0,-70],[70,50],[-70,50]],RED); poly([[0,-36],[40,32],[-40,32]],C.navy); }); },
scadenza({u,A}){ box(-330,-200,300,320,20,'#fff'); box(-330,-200,300,70,20,RED); tx('12',-180,-20,110,C.navy,'800'); tx('mesi',-180,70,34,C.navy,'600'); grp(200,0,1,A(.4),()=>{ box(-130,-90,260,190,20,'#fff'); cross(0,0,.6,RED); spunta(110,90,46,1); }); },
corso({u}){ const d=20*(0.5+0.5*Math.cos(TAU*u*110/60)); cprScene(-60,230,.6,d); [[-380,'#f3b9c4'],[300,'#9fd8c0']].forEach(([x,c])=>bust(x,90,.42,{shirt:c,head:{mouth:'smile'}})); },
stella({u}){ const r=1+Math.sin(u*3)*.05; ctx.save(); ctx.translate(0,-60); ctx.scale(r,r); ctx.beginPath(); for(let i=0;i<10;i++){ const a=-Math.PI/2+i*Math.PI/5, rr2=i%2?60:150; ctx.lineTo(Math.cos(a)*rr2,Math.sin(a)*rr2);} ctx.closePath(); ctx.fillStyle=C.giallo; ctx.fill(); ctx.restore();
  ctx.save(); ctx.strokeStyle='rgba(242,228,51,.5)'; ctx.lineWidth=8; ctx.beginPath(); ctx.moveTo(60,0); ctx.quadraticCurveTo(250,80,420,260); ctx.stroke(); ctx.restore(); snow(u,30); },
});
