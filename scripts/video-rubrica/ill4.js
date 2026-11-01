// ===== Disegni della campagna volontari «Esci dal post. Entra nella squadra» (novembre 2026) =====
// ascolto: una volontaria in divisa ascolta una persona seduta di fronte, al tavolo; sportello: le tre cose del Centro di Ascolto.
Object.assign(ILL, {
ascolto({u,A}){ ground(250);
  box(-200,150,400,26,10,'#e3e7f1'); ln([[-160,176],[-160,250]],'#cfd6e8',12); ln([[160,176],[160,250]],'#cfd6e8',12);   // tavolo
  grp(-250,40,1,A(.05),()=>bust(0,40,.5,{divisa:true,head:{hair:'long',hairCol:'#8a4a2a',mouth:'smile'},L:POSE.down,R:[[110,90],[150,150]]}));
  grp(250,40,1,A(.2),()=>bust(0,40,.5,{shirt:'#bfc8de',shirtD:'#9aa6c4',head:{hairCol:GRAYH,mouth:'flat'},L:[[-110,90],[-150,150]]}));
  grp(250,-250,1,A(.35),()=>{ bubble(0,0,220,100,'',0,-40); for(let i=0;i<3;i++){ const b=Math.max(0,Math.sin(u*5-i*.9))*10; fc(-50+i*50,-b,13,C.navy); } });
  const f=(u*.7)%1; ctx.globalAlpha*=clamp(A(.6)); ctx.fillStyle=RED; heartP(0,-60-f*40,.35+.05*Math.sin(u*4)); ctx.fill(); ctx.globalAlpha=1; },
sportello({u,A}){
  // 1 · la bolletta
  grp(-310,-10,1,A(.45),()=>{ fc(0,0,130,C.tile); box(-70,-95,140,180,12,'#fff'); tx('€',0,-35,70,C.navy,'800'); for(let i=0;i<3;i++) box(-48,20+i*24,96-(i%2)*30,10,5,'#cfd6e8'); });
  // 2 · la questione legale: un foglio con il timbro
  grp(0,-10,1,A(.65),()=>{ fc(0,0,130,C.tile); box(-70,-95,140,180,12,'#fff'); for(let i=0;i<4;i++) box(-48,-65+i*24,96-(i%2)*24,10,5,'#cfd6e8');
    ctx.strokeStyle=RED; ctx.lineWidth=7; ctx.beginPath(); ctx.arc(20,45,30,0,TAU); ctx.stroke(); tx('✓',20,46,34,RED,'800'); });
  // 3 · gli aiuti alimentari
  grp(310,-10,1,A(.88),()=>{ fc(0,0,130,C.tile); bag(0,20,.6,'#e9d3a8'); fc(-20,-48,18,RED); box(8,-64,20,46,8,'#7cc46a'); });
  // il filo che li unisce: una persona alla volta
  const k=clamp((u-.3)/1.4); if(k>0){ ctx.save(); ctx.setLineDash([14,12]); ln([[-310,190],[-310+620*k,190]],'rgba(242,228,51,.7)',6); ctx.restore(); } },
// tempo-cuore: un orologio che gira e un cuore che batte («Tempo e cuore»)
'tempo-cuore'({u,A}){
  grp(-210,0,1,A(.3),()=>{ fc(0,0,150,'#fff'); arc(0,0,150,0,TAU,C.giallo,14);
    for(let i=0;i<12;i++){ const a=i/12*TAU; ln([[Math.cos(a)*118,Math.sin(a)*118],[Math.cos(a)*134,Math.sin(a)*134]],C.navy,i%3?5:9); }
    const m=u*1.2, h=u*.1; ln([[0,0],[Math.sin(h)*70,-Math.cos(h)*70]],C.navy,14); ln([[0,0],[Math.sin(m)*110,-Math.cos(m)*110]],C.ciano,9); fc(0,0,12,C.navy); });
  grp(220,0,1,A(.05),()=>{ const b=1+Math.sin(u*3)*.05; ctx.save(); ctx.scale(b,b); ctx.fillStyle=RED; heartP(0,10,1.15); ctx.fill(); ctx.restore(); });
  tx('+',5,0,90,C.giallo,'800'); },
});
