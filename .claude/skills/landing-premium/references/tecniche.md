# Tecniche — implementazione collaudata

Tutte le pagine condividono lo **scaffold comune** (§1). Le tecniche (§2-§6)
sono varianti di cosa viene renderizzato e pilotato.

## Indice
1. Scaffold comune scroll-driven
2. Exploded view 3D (teardown)
3. Scrollytelling cinematografico con foto AI
4. Video scrubbato dallo scroll
5. Sciame di cubi WebGL (monocromo)
6. Vetrina scura premium
7. Illuminazione e materiali "premium" (Three r128)
8. Etichette 3D→2D con clamp

---

## 1. Scaffold comune scroll-driven

Struttura: canvas/media `position:fixed` a tutto schermo (z 0-2), overlay
tipografici `position:fixed` (z 4+), e un `#scroller` fatto di `.spacer` alti
100vh (uno per capitolo) che genera solo l'altezza di scroll.

```js
let target=0, prog=0;
function readScroll(){
  const max=document.body.scrollHeight-innerHeight;
  target=max>0?Math.min(Math.max(scrollY/max,0),1):0;
}
addEventListener('scroll',readScroll,{passive:true});
// nel loop rAF: prog += (target-prog)*(reduced? .25 : .07);
```

Capitoli come range di progress con rampe smoothstep:

```js
const R={hero:[0,.12], c1:[.16,.30], c2:[.34,.50], /* ... */};
const sstep=(a,b,x)=>{const t=Math.min(Math.max((x-a)/(b-a),0),1);return t*t*(3-2*t);};
function weight(k,p){const r=R[k];
  return Math.min(sstep(r[0]-.03,r[0]+.02,p), 1-sstep(r[1]-.02,r[1]+.03,p));}
```

- **Camera per capitolo**: keyframe `{pos,tgt}` per capitolo, media pesata dai
  weight normalizzati, poi `camera.position.lerp(camPos,.06)` + lookAt su un
  target anch'esso lerpato (micro-drift `sin(t*.22)*.14` se non reduced).
- **Overlay**: ogni capitolo un contenitore `.chap` fixed che prende `.show`
  quando `weight>.25`; dentro: eyebrow mono ("02 // TITOLO"), H2 gigante
  (Anton per il taglio cinematografico, Titillium/Playfair per gli
  istituzionali), paragrafo breve, chip `.stats` mono su sfondo opaco.
- **Parola fantasma**: testo enorme in outline dietro i titoli
  (`color:transparent; -webkit-text-stroke:1.5px rgba(...,.10)`).
- **Rail di avanzamento** a sinistra (dot + label mono), nascosta su mobile.
- Grana pellicola: canvas 220×220 di rumore in overlay `mix-blend-mode:overlay`,
  vignettatura radiale fissa.

## 2. Exploded view 3D (teardown)

Ogni parte registra posizione base (assemblata) ed esplosa; un fattore
`ex = min(sstep(apri), 1-sstep(chiudi))` le interpola. Le **sub-esplosioni**
(componente che contiene componenti: kit primo soccorso, modulo camera, zaino
sanitario) sono gruppi con lo stesso meccanismo su un range interno.

```js
function part(mesh,base,expl){ mesh.userData.base=new THREE.Vector3(...base);
  mesh.userData.expl=new THREE.Vector3(...expl); /* add + push */ }
// nel loop: m.position.lerpVectors(m.userData.base, m.userData.expl, ex);
```

- Rotazioni di apertura (patte, tetti): `userData.rotE` interpolata con `ex`.
- Sagome credibili: profilo 2D con `THREE.Shape` (quadraticCurveTo) →
  `ExtrudeGeometry` con bevel — un furgone/oggetto con silhouette vera batte
  qualsiasi composizione di box.
- Mossa scenica forte: **guscio intero che si solleva** rivelando l'interno.
- Scritte/livree: canvas texture su piani "decal" appoggiati alle superfici
  (mai UV-mappare l'estrusione); per il lato specchiato ridisegnare il canvas
  con `scale(-1,1)`.

## 3. Scrollytelling cinematografico con foto AI

Capitoli narrativi (es. "L'intervento": chiamata → uscita → sul posto →
rientro → CTA). La resa 3D fa da base; quando arrivano le foto:

```js
const PHOTOS={hero:'',c1:'', /* ... */}; // percorsi da riempire
// layer div.photo per scena: opacity = weight; Ken Burns:
el.style.transform='scale('+(1.06+local*.09)+')'; // local = progress nel range
```

Trucchi di scena in tempo reale che reggono anche senza foto: pioggia a
Points, nebbia bassa a Sprite radiali, coni di luce additivi dai lampeggianti,
ruote che girano + texture strada con `offset.x` scorrevole = mezzo in
viaggio, oggetti che appaiono con `scale` legata al weight.

## 4. Video scrubbato dallo scroll

La tecnica dei siti "picchiata dallo spazio" / subacquei: un video
pre-renderizzato (AI o stock) riavvolto dallo scroll.

```html
<video id="bg" muted playsinline preload="auto" src="dive.mp4"></video>
```
```js
const v=document.getElementById('bg');
// nel loop rAF (mai nell'evento scroll):
if(v.duration) v.currentTime = prog * (v.duration-.05);
```

- **Encoding critico**: ogni frame deve essere keyframe, altrimenti lo scrub
  scatta. `ffmpeg -i in.mp4 -vf scale=1920:-2 -an -c:v libx264 -g 1 -crf 23 out.mp4`
- 8-12 s di clip bastano: lo scroll li dilata.
- Poster/primo frame come fallback; su `prefers-reduced-motion` mostrare 3-4
  fotogrammi statici in dissolvenza invece dello scrub continuo.
- iOS: `muted` + `playsinline` obbligatori; fare un `v.play().then(()=>v.pause())`
  al primo touch per sbloccare il seeking.

## 5. Sciame di cubi WebGL (monocromo)

Stile "Quai Network": migliaia di cubi che migrano tra formazioni.

- `THREE.InstancedMesh(boxGeo, mat, N)` con N 1500-4000 (mobile: ridurre).
- Formazioni = array di `N` posizioni target precalcolate (anello, logo/sigla
  campionata da canvas 2D, skyline a blocchi, circuito). Per il logo:
  disegnare il glifo su canvas, campionare i pixel accesi.
- Ogni frame: per ogni istanza `pos = lerp(formA[i], formB[i], wCapitolo)` +
  rumore `sin(t+i)` per il brulichio; `setMatrixAt` + `instanceMatrix.needsUpdate`.
- Monocromo: un solo hue (es. arancio emergenza), materiale emissivo +
  qualche istanza più luminosa; sfondo quasi nero, fog forte, grana.
- Costo: niente ombre, niente env map; è la tecnica più pesante — testare su
  mobile e degradare N via `navigator.hardwareConcurrency` o larghezza schermo.

## 6. Vetrina scura premium

Web design classico curato (stile gelateria/ristorante): tema scuro, display
serif con corsivi d'accento, card prodotto/servizio con hover, sezione hero
con soggetto fotografico grande, badge, form contatti, footer completo.
Niente WebGL: `IntersectionObserver` per le reveal, `transform` e `opacity`
soltanto. Le foto qui sono l'80% del risultato: pretendere foto vere
(mezzi, divise, esercitazioni) prima di ripiegare su AI.

## 7. Illuminazione e materiali premium (Three r128, cdnjs)

Il salto di qualità visiva sta qui, non nella geometria:

```js
renderer.outputEncoding=THREE.sRGBEncoding;
renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=1.1;
renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
```

- **Softbox virtuale** per i riflessi (r128 non ha RoomEnvironment):
  scena env con 3-4 PlaneGeometry emissivi (alto bianco forte, laterali nei
  colori brand) → `scene.environment = new THREE.PMREMGenerator(renderer)
  .fromScene(envScene,.04).texture`.
- Vernice auto: `MeshPhysicalMaterial{clearcoat:1, clearcoatRoughness:.08}`;
  vetri: roughness .05 + envMapIntensity 1.8-2; cromo: metalness 1,
  roughness .12.
- Luci: key direzionale con ombra 2048 + rim colorata brand + point/spot di
  scena; lampeggianti = materiale emissivo pulsante + PointLight sincronizzata
  + cono additivo (`AdditiveBlending, depthWrite:false`) per il volumetrico.
- r128 gotchas: niente OrbitControls/CapsuleGeometry/RoomEnvironment;
  `rotateOnWorldAxis` disponibile; CanvasTexture con `encoding=sRGBEncoding`.

## 8. Etichette 3D→2D con clamp

```js
obj.getWorldPosition(v3); v3.project(camera);
if(v3.z>1){el.classList.remove('on');return;}      // dietro la camera
let x=(v3.x*.5+.5)*innerWidth, y=(-v3.y*.5+.5)*innerHeight;
const flip=x>innerWidth*.55, lw=el.offsetWidth||170;
x = flip? Math.min(Math.max(x,lw+30),innerWidth-10)
        : Math.min(Math.max(x,10),innerWidth-lw-30);
y = Math.min(Math.max(y,84),innerHeight-94);
```

Stile: puntino colore brand + linea, box testo con **sfondo opaco scuro**,
testo bianco, bordo chiaro, ombra. Mai sfondo semitrasparente sopra scene
chiare. Attive solo nel range del capitolo pertinente.
