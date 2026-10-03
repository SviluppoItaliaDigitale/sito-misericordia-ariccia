// ===== Disegni dei video dei servizi: accompagnamento sociale e «L'ultimo viaggio» =====
function wheelchair(x,y,s,o={}){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  arc(0,40,46,0,TAU,'#cfd6e8',9); fc(0,40,8,'#cfd6e8'); fc(56,78,12,'#cfd6e8');
  ln([[-36,-10],[40,-10],[56,74]],'#cfd6e8',9); ln([[-36,-10],[-44,-80]],'#cfd6e8',9);
  ln([[-30,-24],[-30,-80]],o.shirt||'#bfc8de',30); fc(-30,-110,22,SK); ctx.fillStyle=o.hairCol||GRAYH; ctx.beginPath(); ctx.arc(-30,-110,23,Math.PI,0); ctx.fill();
  ln([[-30,-14],[30,-14],[36,40]],PANT,18); ln([[-24,-60],[10,-36]],o.shirt||'#bfc8de',12); ctx.restore(); }
function elder(x,y,s){ stick(x,y,s,{hairCol:GRAYH,shirt:'#bfc8de'}); ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ln([[44,45],[60,125]],'#8a5a3a',7); ctx.restore(); }
function volunteer(x,y,s){ stick(x,y,s,{shirt:RS}); ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.fillStyle=C.giallo; ctx.fillRect(-20,22,40,8); ctx.restore(); }
function miseCar(x,y,s){ car(x,y,s,'#fff'); ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.fillStyle=C.ciano; ctx.fillRect(-150,-6,300,12); ctx.fillStyle=C.giallo; ctx.fillRect(-150,6,300,6); ctx.restore(); }
function cart(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.strokeStyle='#cfd6e8'; ctx.lineWidth=8; ctx.lineJoin='round';
  ctx.beginPath(); ctx.moveTo(-110,-70); ctx.lineTo(-80,-70); ctx.lineTo(-50,30); ctx.lineTo(80,30); ctx.lineTo(100,-40); ctx.lineTo(-64,-40); ctx.stroke();
  for(let i=0;i<4;i++) ln([[-50+i*40,-40],[-38+i*36,30]],'rgba(207,214,232,.6)',4); fc(-30,56,13,'#cfd6e8'); fc(60,56,13,'#cfd6e8'); ctx.restore(); }
function sea(u,o={}){ const g=ctx.createLinearGradient(0,-300,0,60); g.addColorStop(0,'#2a3463'); g.addColorStop(.6,'#e8702a'); g.addColorStop(1,'#f2c14e');
  ctx.save(); rr(ctx,-440,-300,880,560,30); ctx.clip(); ctx.fillStyle=g; ctx.fillRect(-440,-300,880,360);
  const sy=o.sunY??-10; fc(o.sunX||120,sy,90,'rgba(242,228,51,.95)'); fc(o.sunX||120,sy,130,'rgba(242,228,51,.18)');
  ctx.fillStyle='#16325a'; ctx.fillRect(-440,60,880,200);
  for(let i=0;i<7;i++){ const yy=80+i*24, off=(u*40*(1+i*.2))%120; ctx.strokeStyle=`rgba(242,193,78,${.55-i*.06})`; ctx.lineWidth=5; ctx.beginPath(); for(let x=-440-off;x<460;x+=120){ ctx.moveTo(x,yy); ctx.quadraticCurveTo(x+30,yy-10,x+60,yy); } ctx.stroke(); }
  for(let i=0;i<3;i++){ const gx=-300+((u*30+i*140)%700), gy=-180+i*30+Math.sin(u*3+i)*8; ctx.strokeStyle='#1b223f'; ctx.lineWidth=5; ctx.beginPath(); ctx.moveTo(gx-18,gy); ctx.quadraticCurveTo(gx-8,gy-10,gx,gy); ctx.quadraticCurveTo(gx+8,gy-10,gx+18,gy); ctx.stroke(); }
  if(o.promenade){ ctx.fillStyle='#d9c8a3'; ctx.fillRect(-440,190,880,70); } ctx.restore(); }
function stretcher(x,y,s,o={}){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  ln([[-140,0],[140,0]],'#cfd6e8',10); ln([[-110,0],[-110,60]],'#cfd6e8',8); ln([[110,0],[110,60]],'#cfd6e8',8); fc(-110,70,12,'#6b7491'); fc(110,70,12,'#6b7491');
  box(-150,-28,300,30,12,'#fff'); ctx.save(); ctx.translate(-120,-30); ctx.rotate(-.35); box(-30,-28,90,30,12,'#fff'); ctx.restore();
  box(-60,-62,190,44,22,o.blanket||C.arancio); fc(-130,-72,26,SK); ctx.fillStyle=GRAYH; ctx.beginPath(); ctx.arc(-136,-76,27,Math.PI*.8,Math.PI*1.8); ctx.fill(); ctx.restore(); }
function village(x,y,s,u){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  ctx.fillStyle='#2f6b4f'; ctx.beginPath(); ctx.moveTo(-440,200); ctx.quadraticCurveTo(-200,-20,0,40); ctx.quadraticCurveTo(220,-60,440,180); ctx.lineTo(440,260); ctx.lineTo(-440,260); ctx.fill();
  [[-180,10],[-110,-10],[-40,0],[40,-20],[110,0],[170,20]].forEach(([hx,hy],i)=>{ box(hx-30,hy-40,60,60,4,['#e9d3a8','#f3ead8','#e0b84a','#f3ead8','#e9b871','#e9d3a8'][i]); poly([[hx-36,hy-40],[hx,hy-70],[hx+36,hy-40]],'#c4573a'); box(hx-8,hy-20,16,16,2,'#24305c'); });
  box(-10,-190,40,170,4,'#f3ead8'); poly([[-16,-190],[10,-240],[36,-190]],'#c4573a'); ctx.save(); ctx.translate(10,-160); ctx.rotate(Math.sin(u*3)*.35); fe(0,10,12,16,C.giallo); ctx.restore(); ctx.restore(); }
function church(x,y,s){ ctx.save(); ctx.translate(x,y); ctx.scale(s,s); box(-70,-60,140,140,4,'#f3ead8'); poly([[-80,-60],[0,-130],[80,-60]],'#e9d3a8'); box(-20,10,40,70,20,'#8a5a3a'); fc(0,-30,16,'#9fd8f0'); ln([[0,-130],[0,-180]],'#f3ead8',8); ln([[-16,-162],[16,-162]],'#f3ead8',8); ctx.restore(); }

Object.assign(ILL, {
mani({u,p}){ box(-440,-60,880,260,40,'#e9edf6'); ln([[-440,40],[440,40]],'rgba(27,34,63,.08)',40);
  // mano anziana: dal polso a sinistra, dita verso il centro
  ln([[-440,60],[-235,60]],'#bfc8de',74);
  ctx.save(); ctx.translate(-150,60); ctx.rotate(Math.PI/2); hand(0,0,1.15,0,'#efd3bd'); ctx.restore();
  ctx.save(); ctx.strokeStyle='rgba(160,110,80,.35)'; ctx.lineWidth=3; for(let i=0;i<4;i++){ ctx.beginPath(); ctx.moveTo(-205+i*14,40); ctx.lineTo(-198+i*14,80); ctx.stroke(); } ctx.restore();
  // mano giovane: arriva da destra, dita verso sinistra, si posa sulla mano anziana
  const t=clamp(p*1.6), x=lerp(420,40,outCubic(t));
  ln([[x+85,30],[x+700,30]],RS,74);
  ctx.save(); ctx.translate(x,30); ctx.rotate(-Math.PI/2); hand(0,0,1.08,0,SKD,true); ctx.restore();
  if(t>=1){ const b=1+Math.sin(u*2.5)*.06; ctx.save(); ctx.translate(-40,-210); ctx.scale(b,b); ctx.fillStyle=RED; heartP(0,0,.55); ctx.fill(); ctx.restore(); } },
'tramonto-finale'({u}){ sea(u,{promenade:true,sunX:0,sunY:40+Math.min(25,u*4)});
  ctx.save(); ctx.globalAlpha=.92; ctx.fillStyle='#141a33';
  ctx.translate(-60,150); ctx.fillRect(-150,0,300,14); ctx.fillRect(-120,14,10,56); ctx.fillRect(110,14,10,56); ctx.beginPath(); ctx.arc(-115,76,12,0,TAU); ctx.arc(115,76,12,0,TAU); ctx.fill();
  rr(ctx,-160,-30,320,34,14); ctx.fill(); ctx.beginPath(); ctx.arc(-130,-50,26,0,TAU); ctx.fill();
  ctx.translate(230,0); ctx.beginPath(); ctx.arc(0,-150,26,0,TAU); ctx.fill(); rr(ctx,-24,-120,48,110,20); ctx.fill(); ctx.fillRect(-20,-14,16,90); ctx.fillRect(4,-14,16,90);
  ctx.lineWidth=14; ctx.lineCap='round'; ctx.strokeStyle='#141a33'; ctx.beginPath(); ctx.moveTo(-14,-100); ctx.lineTo(-120,-40); ctx.stroke(); ctx.restore();
  const f=(u*.25)%1; ctx.save(); ctx.globalAlpha=1-f; ctx.translate(40,60-f*220); ctx.fillStyle=C.giallo; heartP(0,0,.25); ctx.fill(); ctx.restore(); },
'auto-casa'({u,A}){ house(-250,40,1.05); const t=clamp(u/1.6); miseCar(lerp(520,200,outCubic(t)),150,.9);
  grp(-60,90,1,A(.5),()=>{ elder(0,0,1.1); volunteer(70,0,1.1); ln([[30,0],[60,10]],RS,12); }); },
supermercato({u,A}){ box(-430,-260,560,400,16,'#55607f'); box(-430,-260,560,70,16,C.ciano); cart(-370,-228,.4); tx('Supermercato',-140,-225,36,'#fff','700');
  box(-380,-160,200,240,8,'rgba(159,216,240,.5)'); box(-150,-160,240,240,8,'rgba(159,216,240,.5)'); ground(220);
  const x=lerp(-260,120,clamp((u-.4)/3)); elder(x-90,90,1.05); volunteer(x,90,1.05); cart(x+110,140,.8);
  grp(340,40,1,A(.85),()=>{ bag(-40,40,.6,'#e9d3a8'); bag(50,50,.55,'#e9d3a8'); fc(-50,-30,20,RED); box(30,-40,26,60,10,'#7cc46a'); }); },
'posta-banca'({u,A}){ grp(-220,0,1,A(.2),()=>{ panel(0,0,380,460,true,'posta'); box(-120,-90,240,160,12,C.giallo); ln([[-120,-90],[0,0],[120,-90]],C.navy,8); const f=(u*.8)%1; box(-60,90-f*0,120,30,8,'#fff'); });
  grp(220,0,1,A(.6),()=>{ panel(0,0,380,460,true,'banca'); poly([[-130,-90],[0,-160],[130,-90]],'#cfd6e8'); for(let i=0;i<4;i++) box(-110+i*66,-80,28,150,4,'#cfd6e8'); box(-140,70,280,22,4,'#cfd6e8'); [[-50,130],[0,120],[50,130]].forEach(([cx,cy],i)=>fc(cx,cy-Math.abs(Math.sin(u*3+i))*10,22,'#e0b84a')); }); },
farmacia({u,A}){ const on=(u*1.5%1)<.6; box(-200,-260,400,80,16,'#2b3560'); cross(0,-220,.45,on?'#2fbf71':'#1f7a4a'); box(-200,-180,400,330,16,'#55607f'); box(-160,-140,140,200,8,'rgba(159,216,240,.5)'); box(20,-140,140,200,8,'rgba(159,216,240,.5)');
  grp(-300,120,1,A(.3),()=>{ box(-80,-110,160,210,10,'#fff'); for(let i=0;i<4;i++) box(-56,-70+i*36,112-i*20,10,5,'#cfd6e8'); tx('Ricetta',0,-88,24,C.navy,'700'); });
  grp(310,110,1,A(.75),()=>{ box(-70,-50,140,100,14,'#fff'); box(-70,-50,140,30,12,'#2fbf71'); pill(0,20,.45,0); }); },
'piccole-gioie'({u,A}){ grp(-300,0,1,A(.45),()=>{ fc(0,0,120,C.tile); ctx.save(); ctx.rotate(Math.sin(u*4)*.15); ln([[-40,-40],[40,40]],'#cfd6e8',10); ln([[40,-40],[-40,40]],'#cfd6e8',10); arc(-48,48,18,0,TAU,'#cfd6e8',8); arc(48,48,18,0,TAU,'#cfd6e8',8); ctx.restore(); });
  grp(0,0,1,A(.65),()=>{ fc(0,0,120,C.tile); church(0,20,.6); });
  grp(300,0,1,A(.88),()=>{ fc(0,0,120,C.tile); box(-24,10,48,60,8,'#cfd6e8'); [[-26,-30,RED],[0,-46,C.giallo],[26,-30,'#f3b9c4']].forEach(([fx,fy,c])=>{ ln([[0,10],[fx,fy]],'#7cc46a',5); fc(fx,fy,16,c); }); }); },
visita({u,A}){ grp(-90,20,1,1,()=>bust(0,80,.5,{shirt:'#bfc8de',head:{hairCol:GRAYH,mouth:'smile'}})); grp(90,20,1,A(.3),()=>bust(0,80,.5,{shirt:'#f3b9c4',head:{hair:'long',mouth:'smile'}}));
  const b=1+Math.sin(u*4)*.08; ctx.save(); ctx.translate(0,-220); ctx.scale(b,b); ctx.fillStyle=RED; heartP(0,0,.5); ctx.fill(); ctx.restore();
  grp(340,-120,1,A(.85),()=>{ box(-70,-80,140,160,8,'#cfd6e8'); for(let i=0;i<3;i++) for(let j=0;j<2;j++) box(-50+j*60,-60+i*45,40,30,4,'#9fd8f0'); cross(0,-100,.3,RED); }); },
'porta-a-porta'({u,p,A}){ house(-330,20,.6); box(240,-60,170,150,8,'#55607f'); box(240,-80,170,30,8,C.ciano);
  ctx.save(); ctx.setLineDash([16,14]); ctx.lineDashOffset=-u*40; ln([[-250,100],[260,100]],'rgba(242,228,51,.7)',6); ctx.restore();
  const ph=(u%6)/6; const x= ph<.4? lerp(-250,200,inOut(ph/.4)) : ph<.6? 200 : lerp(200,-250,inOut((ph-.6)/.4)); ctx.save(); ctx.translate(x,90); if(ph>=.6) ctx.scale(-1,1); miseCar(0,0,.45); ctx.restore();
  grp(0,-150,1,A(.45),()=>{ clockFace(0,0,70,10,(u*60)%60); tx('ti aspettiamo',0,100,28,'#fff','700'); });
  grp(0,220,1,A(.85),()=>{ box(-170,-40,260,90,16,'#fff'); poly([[90,40],[200,60],[200,70],[90,50]],'#cfd6e8'); wheelchair(-60,-10,.45,{}); }); },
'chi-serve'({u,A}){ grp(-300,20,1,A(.2),()=>{ panel(0,0,260,400,true,'anziani soli'); elder(0,-40,1.2); });
  grp(0,20,1,A(.4),()=>{ panel(0,0,260,400,true,'disabilità'); wheelchair(10,-30,1,{}); });
  grp(300,20,1,A(.85),()=>{ panel(0,0,260,400,true,'senza passaggio'); car(0,-40,.4,'#6b7491'); vieto(0,-40,80,1); }); },
prenota({u,A}){ ctx.save(); ctx.translate(-170,0); box(-100,-190,200,380,34,'#0d1226'); sbox(-100,-190,200,380,34,'#3a4570',6); box(-84,-170,168,320,20,'#24305c'); tx('Misericordia',0,-110,24,'#aab3cc','600'); tx('348',0,-60,56,'#fff','800'); tx('4068657',0,0,48,'#fff','800'); fc(0,90,36,'#2fbf71'); ctx.save(); ctx.translate(0,90); ctx.rotate(-.6); box(-20,-8,40,16,8,'#fff'); ctx.restore();
  for(let i=0;i<3;i++){ const r=((u*1.2+i/3)%1); arc(120,-150,30+r*70,-0.9,0.4,`rgba(242,228,51,${1-r})`,8); } ctx.restore();
  grp(220,-40,1,A(.4),()=>{ fc(0,0,110,'#25d366'); bubble(0,-4,120,84,'',0,-20); for(let i=0;i<3;i++) fc(-30+i*30,-4,9,'#25d366'); });
  if(CFG.nome==='Accompagnamento sociale') grp(220,190,1,A(.9),()=>{ box(-170,-40,340,80,16,'#fff'); tx('qualche giorno prima',0,2,28,C.navy,'700'); }); },
mare({u}){ sea(u,{sunY:-20+Math.min(30,u*6)}); },
'mare-barella'({u,A}){ sea(u,{promenade:true,sunX:80}); stretcher(-40,170,1.1); grp(220,140,1,A(.3),()=>volunteer(0,0,1.2)); grp(-350,140,1,A(.6),()=>{ for(let i=0;i<4;i++){ const f=(u*.8+i/4)%1; arc(0,-40,20+f*50,-1.2,-.3,`rgba(255,255,255,${1-f})`,5); } }); },
paese({u,A}){ ctx.save(); rr(ctx,-440,-300,880,560,30); ctx.clip(); ctx.fillStyle='#24305c'; ctx.fillRect(-440,-300,880,560); fc(300,-200,50,'rgba(242,228,51,.9)'); village(0,0,1,u); ctx.restore(); },
'casa-giardino'({u,p}){ ground(220); house(-120,60,1); const g=clamp(p*1.4);
  for(let i=0;i<7;i++){ const fx=-380+i*110+(i>2?260:0), h=60*g; if(fx>-200&&fx<60) continue; ln([[fx,220],[fx,220-h]],'#7cc46a',6); fc(fx,218-h,14*g,[RED,C.giallo,'#f3b9c4'][i%3]); }
  ln([[300,220],[300,40]],'#8a5a3a',24); fc(300,0,90,'#3f8a5f'); fc(250,40,60,'#3f8a5f'); fc(350,40,60,'#3f8a5f'); },
festa({u,A}){ arc(-55,0,90,0,TAU,'#e0b84a',22); arc(55,0,90,0,TAU,'#f2e433',22); fc(70,-95,18,'#cfe9f5');
  for(let i=0;i<26;i++){ const f=(u*.3+hash(i))%1; ctx.save(); ctx.translate(-420+hash(i+2)*840,-300+f*560); ctx.rotate(u*2+i); ctx.fillStyle=[C.giallo,C.ciano,'#f3b9c4',ORANGE][i%4]; ctx.fillRect(-6,-10,12,20); ctx.restore(); } },
passioni({u,A}){ grp(-300,0,1,A(.25),()=>{ fc(0,0,120,C.tile); church(0,30,.65); });
  grp(0,0,1,A(.55),()=>{ fc(0,0,120,C.tile); ctx.save(); ctx.rotate(u*1.5); fc(0,0,50,'#fff'); for(let i=0;i<5;i++){ const a=i/5*TAU; fc(Math.cos(a)*30,Math.sin(a)*30,12,C.navy); } fc(0,0,14,C.navy); ctx.restore(); });
  grp(300,0,1,A(.85),()=>{ fc(0,0,120,C.tile); const b=Math.abs(Math.sin(u*2.5))*10; ctx.fillStyle=RED; ctx.beginPath(); ctx.arc(0,-20-b,40,Math.PI,0); ctx.lineTo(0,50-b); ctx.closePath(); ctx.fill(); fc(0,-20-b,15,'#fff'); }); },
barella({u,p,A}){ ground(240); ctx.save(); ctx.translate(-60,60); box(-220,-150,330,190,20,'#fff'); box(110,-110,90,150,10,'#fff'); box(110,-110,70,60,6,'#cfe9f5'); ctx.fillStyle=C.arancio; ctx.fillRect(-220,-40,420,20); ctx.fillStyle=C.ciano; ctx.fillRect(-220,-20,420,12);
  fc(-140,50,32,'#1a1f36'); fc(120,50,32,'#1a1f36'); box(-232,-150,16,190,4,'#e3e7f1'); ctx.restore();
  const x=lerp(-150,-430,1-clamp((p-.2)/.5)); stretcher(x-110,200,.9,{blanket:C.ciano});
  grp(140,150,1,A(.85),()=>{ volunteer(0,0,1.1); volunteer(110,0,1.1); }); },
famiglia({u,A}){ stretcher(-40,150,1.3); grp(-280,0,1,A(.3),()=>bust(0,60,.45,{shirt:'#f3b9c4',head:{hair:'long',mouth:'smile'}})); grp(260,0,1,A(.5),()=>bust(0,60,.45,{shirt:RS,head:{mouth:'smile'}}));
  const b=1+Math.sin(u*3)*.06; ctx.save(); ctx.translate(-10,-200); ctx.scale(b,b); ctx.fillStyle=RED; heartP(0,0,.6); ctx.fill(); ctx.restore(); },
});
function firma(x,y,w,k,col=C.navy){ ctx.save(); ctx.strokeStyle=col; ctx.lineWidth=6; ctx.lineCap='round'; ctx.lineJoin='round'; ctx.beginPath(); const N=60;
  for(let i=0;i<=N*clamp(k);i++){ const t=i/N, px=x+t*w, py=y+Math.sin(t*18)*18*Math.exp(-t*1.2)-Math.sin(t*5)*8; i?ctx.lineTo(px,py):ctx.moveTo(px,py); } ctx.stroke(); ctx.restore(); }
function penna(x,y,rot=-.6){ ctx.save(); ctx.translate(x,y); ctx.rotate(rot); box(-12,-150,24,140,10,C.ciano); poly([[-12,-10],[12,-10],[0,16]],'#f3ead8'); fc(0,14,4,C.navy); ctx.restore(); }
Object.assign(ILL, {
'cinque-mille'({u}){ tx('5x1000',0,-60,190,C.giallo,'800'); const k=clamp((u-.5)/2.2); firma(-260,120,520,k,'#fff');
  if(k>0&&k<1){ const t=k, px=-260+t*520, py=120+Math.sin(t*18)*18*Math.exp(-t*1.2)-Math.sin(t*5)*8; penna(px,py); } },
'tasse-scelta'({u,p,A}){ [[-40,40],[0,40],[40,40],[-20,10],[20,10],[0,-20]].forEach(([cx,cy])=>{ fe(cx,cy+60,40,14,'#c9a23a'); fe(cx,cy+52,40,14,'#e0b84a'); });
  grp(-300,-40,1,1,()=>{ ctx.globalAlpha*=p>.45?.35:1; poly([[-90,-40],[0,-100],[90,-40]],'#cfd6e8'); for(let i=0;i<4;i++) box(-75+i*44,-30,20,100,4,'#cfd6e8'); box(-100,70,200,18,4,'#cfd6e8'); tx('se non firmi',0,130,28,'#fff','600'); });
  grp(300,-40,1,A(.6),()=>{ fc(0,10,110,C.tile); ctx.fillStyle=RED; heartP(0,20,.6); ctx.fill(); tx('se firmi',0,160,28,C.giallo,'700'); });
  const f=clamp((p-.6)/.35); if(f>0){ const x=lerp(0,300,f), y=60-Math.sin(f*Math.PI)*160; fe(x,y,30,11,'#e0b84a'); } },
'tre-firme'({u,A}){ [['8x1000',-300,.6],['5x1000',0,.25],['2x1000',300,.75]].forEach(([l,x,t],i)=>grp(x,-20,1,A(t),()=>{ box(-130,-150,260,300,20,i===1?'#fff':'#e3e7f1'); tx(l,0,-95,40,C.navy,'800'); ln([[-90,40],[90,40]],'#aab3cc',4); firma(-90,10,180,clamp((u-PRE-t*3)/1.5)); if(i===1) sbox(-130,-150,260,300,20,C.giallo,8); }));
  grp(0,230,1,A(.25),()=>{ box(-150,-40,300,80,40,C.giallo); tx('0 € in più',0,2,40,C.navy,'800'); }); },
moduli({u,A}){ [['730',-300,.2],['Redditi',0,.4],['CU',300,.8]].forEach(([l,x,t])=>grp(x,0,1,A(t),()=>{ ctx.rotate((x/300)*.05); box(-120,-160,240,320,14,'#fff'); poly([[60,-160],[120,-160],[120,-100]],'#cfd6e8'); tx(l,0,-90,l.length>3?46:64,C.navy,'800'); for(let i=0;i<5;i++) box(-80,-20+i*30,160-(i%2)*40,10,5,'#cfd6e8'); box(-80,130,160,16,4,'rgba(242,228,51,.7)'); })); },
'firma-riquadro'({u,p,A}){ box(-400,-250,800,470,20,'#fff'); box(-400,-250,800,70,20,C.ciano); tx('Sostegno degli enti del Terzo settore',0,-215,30,'#fff','700');
  tx('FIRMA',-340,-120,26,'#6b7491','700','Jost','left'); sbox(-360,-100,720,120,12,'#aab3cc',4); firma(-300,-40,520,clamp((p-.45)/.3));
  tx('Codice fiscale del beneficiario',-340,70,24,'#6b7491','700','Jost','left'); const cf='90031910582', n=Math.floor(clamp((p-.8)/.18)*11);
  for(let i=0;i<11;i++){ sbox(-350+i*64,95,56,80,8,'#aab3cc',3); if(i<n) tx(cf[i],-322+i*64,137,48,C.navy,'800'); } },
'codice-fiscale'({u,p}){ const cf='90031910582', n=Math.min(11,Math.floor(clamp((p-.2)/.72)*11)+ (p>.2?1:0));
  for(let i=0;i<11;i++){ const x=-400+i*80, on=i<n; box(x-34,-70,68,110,12,on?C.giallo:C.tile); if(on){ const k=outBack(clamp((p-.2-i*.065)/.06)); ctx.save(); ctx.translate(x,-14); ctx.scale(k,k); tx(cf[i],0,0,74,C.navy,'800'); ctx.restore(); } }
  tx('Codice fiscale',0,-150,36,'#aab3cc','600'); if(n>=11){ const f=(u*1.2)%1; sbox(-450-f*10,-90-f*10,900+f*20,150+f*20,24,`rgba(242,228,51,${1-f})`,6); } },
castelli({u,A}){ ctx.fillStyle='#2f6b4f'; ctx.beginPath(); ctx.moveTo(-440,240); ctx.quadraticCurveTo(-250,-60,-40,80); ctx.quadraticCurveTo(160,-80,440,200); ctx.lineTo(440,250); ctx.lineTo(-440,250); ctx.fill();
  fe(-60,150,120,40,'#3a8ac0'); tx('lago',-60,150,24,'#cfe9f5','600');
  [[-260,40],[-200,20],[40,20],[100,0],[200,40]].forEach(([hx,hy])=>{ box(hx-20,hy-26,40,40,3,'#f3ead8'); poly([[hx-24,hy-26],[hx,hy-46],[hx+24,hy-26]],'#c4573a'); });
  const b=Math.abs(Math.sin(u*2.5))*14; grp(0,-120,1,A(.35),()=>{ ctx.fillStyle=C.giallo; ctx.beginPath(); ctx.arc(0,-40-b,46,Math.PI,0); ctx.lineTo(0,40-b); ctx.closePath(); ctx.fill(); fc(0,-40-b,17,C.navy); tx('Ariccia',0,-130-b,40,'#fff','800'); });
  const f=(u*.6)%1; arc(0,-80,120+f*160,0,TAU,`rgba(242,228,51,${.5*(1-f)})`,5); },
'cosa-diventa'({u,A}){ [[-330,.2,()=>ambulance(0,10,.35,u)],[-110,.45,()=>wheelchair(0,0,.75,{})],[110,.65,()=>{ bag(0,0,.6,'#e9d3a8'); fc(-20,-60,18,RED); box(10,-70,20,46,8,'#7cc46a'); }],[330,.88,()=>{ steto(-10,-10,.55); }]]
  .forEach(([x,t,f])=>grp(x,0,1,A(t),()=>{ fc(0,0,100,C.tile); f(); })); },
passaparola({u,A}){ [[-300,'#f3b9c4',{hair:'long'},.1],[0,RS,{},.45],[300,'#bfc8de',{hairCol:GRAYH,glasses:true},.85]].forEach(([x,c,h,t])=>{ grp(x,40,1,A(t),()=>bust(0,80,.45,{shirt:c,head:{...h,mouth:'smile'}})); grp(x+60,-200,1,A(t+.05),()=>bubble(0,0,200,90,'5x1000!',36,-50)); }); },
});
