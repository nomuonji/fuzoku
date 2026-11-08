"""#005: Builds the episode page: render(t) draws the frame at time t (seconds)."""
import json, pathlib, re
import numpy as np
from PIL import Image

D = pathlib.Path(__file__).resolve().parent
A = D.parent.parent / "assets" / "character"

def inner(p):
    s = (A / p).read_text()
    return re.sub(r"^<svg[^>]*>|</svg>$", "", s.strip())

svgs = {k: inner(v) for k, v in {
    "front": "man/front.svg", "side": "man/side.svg", "back": "man/back.svg",
    "blank": "man/face_blank.svg", "distant": "man/face_distant.svg",
    "glance": "man/face_glance.svg", "resolve": "man/face_resolve.svg", "woman": "woman_pass.svg"}.items()}

# film grain plates
(D / "grain").mkdir(exist_ok=True)
rng = np.random.default_rng(7)
for i in range(6):
    n = (rng.normal(128, 38, (960, 540))).clip(0, 255).astype(np.uint8)
    Image.fromarray(n, "L").save(D / f"grain/g{i}.png")

tl = json.loads((D / "timeline.json").read_text())

HTML = r"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#000}
#st{position:relative;width:1080px;height:1920px;overflow:hidden;background:#0b0b0d;font-family:"Noto Serif CJK JP",serif}
#scene,#scene svg.full{position:absolute;left:0;top:0;width:1080px;height:1920px}
#grain{position:absolute;inset:0;width:1080px;height:1920px;opacity:.13;mix-blend-mode:screen;image-rendering:pixelated}
#vig{position:absolute;inset:0;background:radial-gradient(ellipse 75% 60% at 50% 45%,rgba(0,0,0,0) 45%,rgba(0,0,0,.82) 100%)}
#sub{position:absolute;left:60px;right:120px;top:1360px;white-space:pre-line;text-align:center;color:#ece9e2;font-size:52px;font-weight:500;letter-spacing:.06em;line-height:1.55;
 text-shadow:0 2px 12px rgba(0,0,0,.95),0 0 3px rgba(0,0,0,.9)}
#subbg{position:absolute;left:0;right:0;top:1180px;height:620px;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.42) 35%,rgba(0,0,0,.42) 70%,rgba(0,0,0,0));opacity:0}
#fade{position:absolute;inset:0;background:#000;opacity:0}
.neon{writing-mode:vertical-rl;font-weight:700;letter-spacing:.06em;line-height:1;color:#ffe3f0;-webkit-text-stroke:3px #ff2e88;
 text-shadow:0 0 6px #ff7ab4,0 0 18px #ff2e88,0 0 42px #ff2e88,0 0 90px rgba(255,46,136,.8),0 0 160px rgba(255,46,136,.5)}
</style></head><body><div id="st"><div id="scene"></div><img id="grain" src="grain/g0.png"><div id="vig"></div><div id="subbg"></div><div id="sub"></div><div id="fade"></div></div>
<script>
const S = __SVGS__;
const W=1080,H=1920;
const lerp=(a,b,x)=>a+(b-a)*Math.max(0,Math.min(1,x));
const ease=x=>{x=Math.max(0,Math.min(1,x));return x<.5?2*x*x:1-Math.pow(-2*x+2,2)/2};
function hash(i){let x=Math.sin(i*127.1)*43758.5453;return x-Math.floor(x)}
function rain(t,n,opac,len,slant,speed,seed){let s='';for(let i=0;i<n;i++){const x0=hash(i+seed)*1300-110;const ph=hash(i*3.7+seed);
 const y=((t*speed*(0.7+ph*0.6)+ph*2200)%2300)-200;const x=x0+y*slant;
 s+=`<line x1="${x.toFixed(1)}" y1="${y.toFixed(1)}" x2="${(x+len*slant).toFixed(1)}" y2="${(y+len).toFixed(1)}" stroke="#d9d9de" stroke-opacity="${(opac*(0.4+ph*0.6)).toFixed(2)}" stroke-width="${(1+ph*1.6).toFixed(1)}"/>`}return s}
function bokeh(t,n,seed,y0,y1){let s='';for(let i=0;i<n;i++){const x=hash(i+seed)*W, y=y0+hash(i*2.3+seed)*(y1-y0), r=14+hash(i*5.1+seed)*46;
 const o=0.06+0.12*hash(i*9.1+seed)*(0.8+0.2*Math.sin(t*0.7+i));s+=`<circle cx="${x}" cy="${y}" r="${r}" fill="#e9e6df" opacity="${o.toFixed(3)}"/>`}return s}
function man(key,vb,x,y,w,h){return `<svg x="${x}" y="${y}" width="${w}" height="${h}" viewBox="${vb}" preserveAspectRatio="xMidYMid meet">${S[key]}</svg>`}
function full(inner){return `<svg class="full" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg"><defs>
<radialGradient id="glowW"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".25" stop-color="#e9e6df" stop-opacity=".35"/><stop offset="1" stop-color="#e9e6df" stop-opacity="0"/></radialGradient>
<linearGradient id="screen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d6d3cc"/><stop offset="1" stop-color="#a9a6a0"/></linearGradient>
<linearGradient id="tube" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="upglow" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#e9e6df" stop-opacity=".5"/><stop offset="1" stop-color="#e9e6df" stop-opacity="0"/></linearGradient>
<filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter><filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>
</defs>${inner}</svg>`}
function cam(inner,s,cx,cy,dx=0,dy=0){return `<g transform="translate(${cx+dx} ${cy+dy}) scale(${s}) translate(${-cx} ${-cy})">${inner}</g>`}

// ---------- shared props
function kiosk(t,msg,lamp,btn){ // self-checkout, centred
 const blink = lamp ? (Math.floor(t*2.2)%2===0) : false;
 let s=`<rect x="250" y="520" width="580" height="1250" rx="18" fill="#2a2a2e"/>
 <rect x="250" y="520" width="140" height="1250" rx="18" fill="#1d1d21"/>
 <rect x="300" y="610" width="480" height="380" rx="8" fill="url(#screen)"/>
 <rect x="300" y="610" width="480" height="380" rx="8" fill="#fff" opacity="${lamp&&blink?0.10:0}"/>
 <rect x="320" y="1060" width="440" height="40" rx="6" fill="#0e0e10"/>
 <rect x="330" y="1072" width="420" height="4" fill="#77777d"/>
 <rect x="270" y="1140" width="540" height="200" rx="10" fill="#45454b"/>
 <rect x="300" y="1170" width="480" height="140" rx="8" fill="#0e0e10"/>
 <line x1="320" y1="1240" x2="760" y2="1240" stroke="#e9e6df" stroke-width="2" opacity="${0.25+0.15*Math.sin(t*9)}"/>
 <rect x="520" y="260" width="16" height="260" fill="#45454b"/>
 <rect x="490" y="200" width="76" height="90" rx="12" fill="${blink?'#f4f2ee':'#5a5a60'}"/>`;
 if(blink) s+=`<circle cx="528" cy="245" r="220" fill="url(#glowW)" opacity=".75"/>`;
 s+=`<text x="540" y="${msg[1]?770:810}" text-anchor="middle" font-family="Noto Sans CJK JP" font-size="${msg[2]||36}" font-weight="700" fill="#0e0e10">${msg[0]}</text>`;
 if(msg[1]) s+=`<text x="540" y="840" text-anchor="middle" font-family="Noto Sans CJK JP" font-size="30" fill="#2a2a2e">${msg[1]}</text>`;
 if(btn) s+=`<rect x="420" y="890" width="240" height="70" rx="10" fill="${btn==='on'?'#0e0e10':'#45454b'}"/><text x="540" y="938" text-anchor="middle" font-family="Noto Sans CJK JP" font-size="32" font-weight="700" fill="#e9e6df">確認</text>`;
 return s}
function windowBg(t){return `<rect width="1080" height="1920" fill="#101013"/><rect x="0" y="0" width="1080" height="1100" fill="#16161a"/>${bokeh(t,26,3,80,1050)}
 <g opacity=".85">${rain(t,70,.35,90,0.12,900,11)}</g><rect x="0" y="1100" width="1080" height="820" fill="#0e0e10"/>`}
function tubes(t){const f=0.92+0.08*Math.sin(t*37)*Math.sin(t*3.1);return `<rect x="140" y="70" width="800" height="22" rx="11" fill="#f4f2ee" opacity="${f}"/>
 <rect x="140" y="92" width="800" height="700" fill="url(#tube)" opacity="${0.35*f}"/>`}
function shelves(){let s='';for(let r=0;r<6;r++){const y=500+r*170;s+=`<rect x="0" y="${y}" width="1080" height="10" fill="#2a2a2e"/>`;
 for(let i=0;i<14;i++){const h=60+hash(r*31+i)*80;s+=`<rect x="${i*80+hash(i+r)*20}" y="${y-h}" width="${50+hash(i*2+r)*20}" height="${h}" rx="4" fill="#1f1f23"/>`}}return s}

// ---------- #004 shared
const TL = __TL__;
const EV = Object.fromEntries(TL.events.map(e=>[e[0],e[1]]));
const SK='#CFCAC0', SKS='#8E8A83';
function palm(x,y,s,r,fill,shade,inner=''){return `<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})">
 ${[0,1,2,3].map(i=>`<rect x="${-100+i*50}" y="${-215+Math.abs(i-1.5)*18}" width="44" height="${190-Math.abs(i-1.5)*22}" rx="22" fill="${fill}"/>`).join('')}
 <path d="M120,-20 C190,-50 225,-120 205,-150 C188,-170 162,-150 152,-118 C142,-88 122,-70 104,-58 Z" fill="${fill}"/>
 <path d="M-112,-50 C-125,60 -60,140 20,140 C105,140 140,70 128,-40 C110,-70 -95,-80 -112,-50 Z" fill="${fill}"/>
 <path d="M-90,10 C-40,30 40,20 100,-10" stroke="${shade}" stroke-width="5" fill="none"/><path d="M-80,60 C-20,80 50,60 95,30" stroke="${shade}" stroke-width="4" fill="none"/>
 <path d="M30,-60 C0,0 -10,60 0,120" stroke="${shade}" stroke-width="4" fill="none" opacity=".7"/>${inner}</g>`}
const JP='font-family="Noto Sans CJK JP"';
function tiles(y0,op=.5){let s='';for(let i=0;i<9;i++){const y=y0+Math.pow(i/8,1.6)*(1920-y0);s+=`<line x1="0" y1="${y}" x2="1080" y2="${y}" stroke="#2a2a2e" stroke-width="3" opacity="${op}"/>`}
 for(let i=-6;i<=6;i++){s+=`<line x1="${540+i*40}" y1="${y0}" x2="${540+i*260}" y2="1920" stroke="#2a2a2e" stroke-width="3" opacity="${op}"/>`}return s}
const SCR='#d8d5ce';
function phone(inner,x,y,s,glow=0){return `<g transform="translate(${x} ${y}) scale(${s})">
 <circle cx="260" cy="520" r="760" fill="url(#glowW)" opacity="${0.18+glow}"/>
 <rect x="-30" y="-40" width="580" height="1120" rx="80" fill="#1d1d21"/><rect x="0" y="0" width="520" height="1040" rx="54" fill="${SCR}"/>
 <svg x="0" y="0" width="520" height="1040" viewBox="0 0 520 1040">${inner}</svg>
 <rect x="200" y="18" width="120" height="30" rx="15" fill="#0e0e10"/></g>`}
function finger(x,y,press=0){return `<g transform="translate(${x} ${y+press*14})"><path d="M-34,0 C-34,-40 34,-40 34,0 L44,520 L-60,520 Z" fill="${SK}"/>
 <path d="M-22,-14 C-22,-30 22,-30 22,-14 L20,30 C10,40 -10,40 -20,30 Z" fill="#e9e6df" opacity=".55"/><path d="M-30,150 C-10,160 10,160 30,150" stroke="${SKS}" stroke-width="4" fill="none"/>
 <path d="M44,200 C120,220 160,320 150,520 L30,520 Z" fill="${SKS}"/></g>`}
// ---------- #005 props (栄養ドリンク)
const GL='#5a5a60', GLD='#2f2f34';
// a small brown-glass drink bottle (rendered grey). origin = bottom centre, ~ 90 x 300 at s=1
function bottle(x,y,s,lab=true,r=0,capOff=0){return `<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})">
 <path d="M-45,0 L-45,-190 C-45,-215 -22,-225 -20,-245 L-20,-262 L20,-262 L20,-245 C22,-225 45,-215 45,-190 L45,0 Q45,8 37,8 L-37,8 Q-45,8 -45,0 Z" fill="${GL}"/>
 <path d="M-34,-10 L-34,-185" stroke="#e9e6df" stroke-width="7" opacity=".28"/><path d="M28,-20 L28,-180" stroke="${GLD}" stroke-width="9" opacity=".6"/>
 ${lab?`<rect x="-45" y="-170" width="90" height="120" fill="#e9e6df"/><rect x="-45" y="-170" width="90" height="12" fill="#0e0e10"/><rect x="-45" y="-62" width="90" height="12" fill="#0e0e10"/>
 <text x="0" y="-122" text-anchor="middle" ${JP} font-size="23" font-weight="900" fill="#0e0e10">滋養強壮</text>
 <text x="0" y="-96" text-anchor="middle" ${JP} font-size="8.6" fill="#2a2a2e">肉体疲労時の栄養補給</text>
 <text x="0" y="-74" text-anchor="middle" ${JP} font-size="7.6" fill="#45454b">指定医薬部外品　100mL</text>`:''}
 <g transform="translate(0 ${-capOff*40}) rotate(${capOff*25})"><rect x="-24" y="-292" width="48" height="34" rx="5" fill="#b4b2ac"/>${[0,1,2,3,4,5].map(i=>`<rect x="${-20+i*8}" y="-290" width="3" height="30" fill="#77777d"/>`).join('')}</g></g>`}
function fridgeGlow(t){return `<rect width="1080" height="1920" fill="#0d0d10"/><rect x="0" y="0" width="1080" height="1920" fill="#e9e6df" opacity="${0.05+0.01*Math.sin(t*41)}"/>`}
// glass-door chilled case full of bottles, price tags per shelf (top to bottom: 980, 498, 298, 158)
const PRICES=['980','498','298','158'];
function fridge(t,hi=-1,take=0){let s=`<rect x="60" y="80" width="960" height="1700" rx="14" fill="#1d1d21"/><rect x="90" y="110" width="900" height="1640" fill="#26262b"/>
 <rect x="90" y="110" width="900" height="30" fill="#f4f2ee" opacity=".8"/><rect x="90" y="140" width="900" height="600" fill="url(#tube)" opacity=".3"/>`;
 for(let r=0;r<4;r++){const y=470+r*370;s+=`<rect x="90" y="${y}" width="900" height="14" fill="#45454b"/>`;
  for(let i=0;i<9;i++){if(r===1&&i===4&&take>0)continue; s+=bottle(150+i*98,y-2,1.0-r*0.05,true)}
  s+=`<rect x="420" y="${y+16}" width="240" height="64" rx="4" fill="${r===hi?'#f4f2ee':'#d8d5ce'}"/><text x="540" y="${y+64}" text-anchor="middle" ${JP} font-size="44" font-weight="900" fill="#0e0e10">¥${PRICES[r]}</text>`}
 s+=`<rect x="530" y="110" width="20" height="1640" fill="#141418"/><rect x="90" y="110" width="900" height="1640" fill="#e9e6df" opacity=".05"/>
 <path d="M140,110 L330,110 L150,1750 L90,1750 Z" fill="#fff" opacity=".04"/>`;return s}
function grip(x,y,s,r=0){return `<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})">
 <path d="M38,-60 C80,-58 110,-20 112,40 L120,170 L40,170 Z" fill="${SKS}"/>
 ${[0,1,2,3].map(i=>`<rect x="-58" y="${-58+i*17}" width="104" height="17" rx="8.5" fill="${SK}"/><path d="M-50,${-46+i*17} L30,${-46+i*17}" stroke="${SKS}" stroke-width="1.5" opacity=".6"/>`).join('')}
 <rect x="-62" y="-112" width="20" height="62" rx="10" fill="${SK}"/><path d="M-58,-60 L-46,-60" stroke="${SKS}" stroke-width="2"/></g>`}

function storeFront(t,shut=0){return `<rect width="1080" height="1920" fill="#08080a"/>${bokeh(t,16,4,100,700)}
 <rect x="80" y="560" width="920" height="900" fill="#e9e6df" opacity=".9"/><rect x="80" y="420" width="920" height="140" fill="#1d1d21"/>
 <text x="540" y="515" text-anchor="middle" ${JP} font-size="80" font-weight="900" fill="#e9e6df" letter-spacing="30">くすり</text>
 <g opacity=".55">${shelvesIn(560,1460)}</g>
 <rect x="380" y="760" width="320" height="700" fill="#cfcac0" opacity=".5"/><rect x="538" y="760" width="4" height="700" fill="#77777d"/>
 <rect x="820" y="610" width="150" height="60" rx="6" fill="#0e0e10"/><text x="895" y="655" text-anchor="middle" ${JP} font-size="40" font-weight="700" fill="#e9e6df">22:51</text>
 <rect x="110" y="620" width="230" height="110" fill="#f4f2ee"/><text x="225" y="663" text-anchor="middle" ${JP} font-size="26" fill="#0e0e10">営業時間</text><text x="225" y="708" text-anchor="middle" ${JP} font-size="30" font-weight="700" fill="#0e0e10">9:00〜23:00</text>
 <rect x="80" y="560" width="920" height="${900*shut}" fill="#45454b"/>${[...Array(Math.floor(30*shut))].map((_,i)=>`<rect x="80" y="${560+i*30}" width="920" height="3" fill="#2a2a2e"/>`).join('')}
 <rect x="0" y="1460" width="1080" height="460" fill="#141417"/><rect x="80" y="1460" width="920" height="300" fill="#e9e6df" opacity="${0.12*(1-shut)}" filter="url(#blur8)"/>`}
function shelvesIn(y0,y1){let s='';for(let r=0;r<5;r++){const y=y0+120+r*(y1-y0-120)/5;s+=`<rect x="80" y="${y}" width="920" height="8" fill="#45454b"/>`;
 for(let i=0;i<18;i++){const h=30+hash(r*17+i)*50;s+=`<rect x="${90+i*51}" y="${y-h}" width="${36+hash(i+r)*10}" height="${h}" fill="#77777d"/>`}}return s}
function street(t){return `<rect width="1080" height="1920" fill="#0b0b0d"/>${bokeh(t,22,5,200,1000)}<rect x="0" y="1150" width="1080" height="770" fill="#111114"/>
 ${[0,1,2,3,4,5].map(i=>`<rect x="${120+i*170+hash(i)*40}" y="1200" width="${8+hash(i*3)*10}" height="${300+hash(i*5)*400}" fill="#e9e6df" opacity="${0.05+0.05*hash(i*2)}" filter="url(#blur8)"/>`).join('')}`}
function bag(x,y,s){return `<g transform="translate(${x} ${y}) scale(${s})"><path d="M-60,0 L60,0 L70,170 Q0,190 -70,170 Z" fill="#e9e6df" opacity=".55"/>
 <path d="M-40,0 C-40,-60 40,-60 40,0" stroke="#e9e6df" stroke-width="8" fill="none" opacity=".6"/><g opacity=".7">${bottle(0,165,0.45,false)}</g></g>`}

// ---------- scenes (#005 栄養ドリンク)
const SCN = {
 teaser:(t,k)=>full(cam(fridgeGlow(t)+`<circle cx="760" cy="760" r="700" fill="url(#glowW)" opacity=".25"/>`+
   `<g opacity=".9">${man('blank','0 0 300 320',-260,60,1000,1066)}</g>`+bottle(700,1240,2.6,true,-6)+grip(700,1240,2.6,-6),1.05+0.08*ease(k),640,900)+
   `<rect width="1080" height="1920" fill="#000" opacity="${lerp(.6,0,k*4)}"/>`),
 storefront:(t,k)=>full(cam(storeFront(t)+man('back','0 0 400 1000',350,820,380,950),1.0+0.06*ease(k),540,1000)),
 aisle:(t,k)=>full(cam(`<rect width="1080" height="1920" fill="#e9e6df" opacity=".85"/><rect width="1080" height="1920" fill="#16161a" opacity=".55"/>${tubes(t)}
   ${shelvesIn(500,1700)}<g transform="translate(780 260)"><circle r="70" fill="#d8d5ce"/><circle r="56" fill="#b4b2ac"/>${[...Array(5)].map((_,i)=>`<rect x="-46" y="${-34+i*16}" width="92" height="5" fill="#77777d"/>`).join('')}</g>
   <g transform="translate(780 260)" opacity="${0.4+0.3*Math.sin(t*6)}">${[1,2,3].map(i=>`<path d="M${-60-i*36},${110+i*20} Q0,${150+i*40} ${60+i*36},${110+i*20}" stroke="#0e0e10" stroke-width="5" fill="none" opacity="${0.5/i}"/>`).join('')}</g>`+
   man('side','100 20 250 380',-80,520,700,1064),1.0+0.05*ease(k),540,900)),
 fridge:(t,k)=>{const tk=ease((t-EV.case_open-0.6)/1.4);return full(cam(fridge(t,1,tk)+bottle(150+4*98,838-tk*260,0.95,true)+(tk>0?grip(150+4*98,838-tk*260,0.95):`<g opacity="${ease((t-EV.case_open)/0.6)}">${grip(150+4*98,838,0.95)}</g>`),1.0+0.08*ease(k),540,840))},
 sidebottle:(t,k)=>full(`<rect width="1080" height="1920" fill="#101013"/><circle cx="1100" cy="700" r="700" fill="url(#glowW)" opacity=".22"/>`+
   cam(man('side','100 20 250 380',-60,300,1200,1824)+bottle(760,1250,1.4,true,4)+grip(760,1250,1.4,4),1.0+0.05*ease(k),540,800)),
 prices:(t,k)=>full(cam(fridge(t),1.25+0.1*ease(k),540,900,0,lerp(-120,60,ease(k)))),
 tracing:(t,k)=>{const d=t-EV.trace, y=lerp(530,900,ease(d/2.4)), hi=d<1.2?0:1;
   return full(cam(fridge(t,hi)+finger(680,y,0),1.25,540,900,0,0))},
 label:(t,k)=>full(cam(fridgeGlow(t)+`<circle cx="540" cy="760" r="700" fill="url(#glowW)" opacity=".22"/>`+bottle(540,1300,3.6,true,0)+grip(540,1300,3.6,0),1.0+0.06*ease(k),540,900)),
 register:(t,k)=>{const bp=(t>EV.beep&&t<EV.beep+0.18)?1:0;const scr=`<rect width="520" height="1040" fill="#e9e6df"/>
   <text x="260" y="140" text-anchor="middle" ${JP} font-size="30" font-weight="700" fill="#0e0e10">ポイントカード</text>
   ${[...Array(34)].map((_,i)=>`<rect x="${60+i*12}" y="260" width="${hash(i)*8+2}" height="220" fill="#0e0e10"/>`).join('')}
   <text x="260" y="530" text-anchor="middle" ${JP} font-size="24" fill="#2a2a2e">2948 1173 0062</text>
   <text x="260" y="640" text-anchor="middle" ${JP} font-size="26" fill="#45454b">本日 ポイント2倍</text>`;
   return full(`<rect width="1080" height="1920" fill="#0e0e10"/><rect x="0" y="1100" width="1080" height="820" fill="#2a2a2e"/>
   <g transform="translate(120 160)"><rect width="420" height="300" rx="14" fill="#1d1d21"/><rect x="24" y="24" width="372" height="200" rx="6" fill="#d8d5ce"/>
   <text x="210" y="110" text-anchor="middle" ${JP} font-size="28" font-weight="700" fill="#0e0e10">ポイントカードは</text><text x="210" y="160" text-anchor="middle" ${JP} font-size="28" font-weight="700" fill="#0e0e10">お持ちですか</text></g>
   <rect x="600" y="140" width="300" height="70" rx="10" fill="#45454b"/><rect x="610" y="150" width="280" height="50" fill="#e9e6df" opacity="${0.4+bp*0.6}"/>`+
   cam(phone(scr,420,600,0.85,bp*0.3),1.0+0.05*ease(k),540,1000)+palm(700,1560,1.0,-15,SK,SKS))},
 face:(t,k)=>full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+cam(man('blank','0 0 300 320',-40,250,1160,1240),1.0+0.08*ease(k),540,850)+
   `<rect x="0" y="1100" width="1080" height="820" fill="url(#upglow)" opacity=".4"/>`),
 side:(t,k)=>full(`<rect width="1080" height="1920" fill="#151519"/><circle cx="1150" cy="620" r="620" fill="url(#glowW)" opacity=".24"/>`+
   cam(man('side','100 20 250 380',-60,300,1200,1824),1.0+0.06*ease(k),540,800,-30*ease(k),0)),
 plan:(t,k)=>{const a=ease(k*2);return full(`<rect width="1080" height="1920" fill="#0e0e10"/>
   <g transform="translate(140 200)"><rect width="800" height="1000" fill="none" stroke="#77777d" stroke-width="6"/>
   ${[0,1,2,3].map(i=>`<rect x="${60+i*110}" y="80" width="60" height="560" fill="#2a2a2e"/>`).join('')}
   <rect x="560" y="80" width="200" height="300" fill="#45454b"/><text x="660" y="230" text-anchor="middle" ${JP} font-size="34" fill="#e9e6df">化粧品</text>
   <rect x="540" y="700" width="220" height="200" fill="#77777d"/><text x="650" y="815" text-anchor="middle" ${JP} font-size="40" font-weight="700" fill="#0e0e10">レジ</text>
   <rect x="440" y="700" width="90" height="200" fill="#e9e6df" opacity="${0.5+0.5*a}"/><text x="485" y="800" text-anchor="middle" ${JP} font-size="28" font-weight="700" fill="#0e0e10" writing-mode="vertical-rl">冷蔵</text>
   <rect x="300" y="1000" width="200" height="10" fill="#0e0e10"/><text x="400" y="1070" text-anchor="middle" ${JP} font-size="30" fill="#9a988f">入口</text>
   <path d="M400,990 L400,${990-260*a} L430,${990-260*a}" stroke="#e9e6df" stroke-width="5" fill="none" stroke-dasharray="14 12" opacity=".7"/></g>`)},
 receipt:(t,k)=>{const p=ease((t-EV.print)/2.2);const h=60+620*p;return full(`<rect width="1080" height="1920" fill="#0b0b0d"/><rect x="300" y="200" width="480" height="110" rx="10" fill="#1d1d21"/>
   <g><rect x="340" y="300" width="400" height="${h}" fill="#e9e6df"/><svg x="340" y="300" width="400" height="${h}" viewBox="0 ${680-h} 400 ${h}">
   <text x="200" y="70" text-anchor="middle" ${JP} font-size="24" fill="#2a2a2e">毎度ありがとうございます</text>
   <text x="200" y="120" text-anchor="middle" ${JP} font-size="22" fill="#45454b">2026年11月　22:52</text>
   <text x="30" y="220" ${JP} font-size="30" fill="#0e0e10">ドリンク剤</text><text x="370" y="220" text-anchor="end" ${JP} font-size="30" fill="#0e0e10">¥498</text>
   <rect x="30" y="260" width="340" height="3" fill="#0e0e10"/>
   <text x="30" y="330" ${JP} font-size="36" font-weight="700" fill="#0e0e10">合計</text><text x="370" y="330" text-anchor="end" ${JP} font-size="36" font-weight="700" fill="#0e0e10">¥498</text>
   <text x="30" y="420" ${JP} font-size="24" fill="#45454b">今回ポイント　8P</text><text x="30" y="560" ${JP} font-size="22" fill="#77777d">領収書が必要な方は…</text></svg></g>`)},
 stack:(t,k)=>{const n=Math.min(21,Math.floor(ease((t-EV.stack)/2.6)*21)+1);let g='';let c=0;
   for(let w=0;w<5;w++)for(let d=0;d<7;d++){const day=w*7+d;if(day<0||day>=30)continue;const wk=d>=1&&d<=5;const x=120+d*120,y=380+w*170;
    let on=false;if(wk){c++;on=c<=n}
    g+=`<rect x="${x}" y="${y}" width="104" height="150" rx="6" fill="${on?'#d8d5ce':'#1d1d21'}"/><text x="${x+10}" y="${y+34}" ${JP} font-size="26" fill="${on?'#0e0e10':'#45454b'}">${day+1}</text>`+(on?bottle(x+52,y+140,0.32,false):'')}
   const sum=Math.min(n,21)*498;
   return full(`<rect width="1080" height="1920" fill="#0b0b0d"/><text x="120" y="320" ${JP} font-size="44" font-weight="700" fill="#e9e6df">11月</text>${g}
   <text x="960" y="1290" text-anchor="end" ${JP} font-size="72" font-weight="900" fill="#e9e6df">¥${sum.toLocaleString()}</text>`)},
 distant:(t,k)=>full(`<rect width="1080" height="1920" fill="#0b0b0d"/>`+cam(man('distant','0 0 300 320',-40,250,1160,1240),1.04+0.08*ease(k),540,850)),
 shutter:(t,k)=>{const sh=ease((t-EV.shutter)/3.2)*0.85;return full(cam(storeFront(t,sh)+man('back','0 0 400 1000',330,880,420,1050)+bag(650,1350,0.9),1.0+0.04*ease(k),540,1100))},
 walk:(t,k)=>full(cam(street(t)+`<ellipse cx="540" cy="1620" rx="260" ry="26" fill="#e9e6df" opacity=".06"/>`+man('back','0 0 400 1000',290,820,500,1250)+bag(690,1380,0.8),1.0+0.05*ease(k),540,1200,0,-40*ease(k))),
 woman:(t,k)=>{const x=lerp(-420,1500,k);return full(`<rect width="1080" height="1920" fill="#0b0b0d"/>${bokeh(t,12,7,100,700)}<rect x="0" y="900" width="1080" height="1020" fill="#141417"/>${tiles(900,.35)}`+
   `<g transform="translate(${x-300*1.9} ${1180-380*1.9}) scale(1.9)">${S.woman}</g>`+
   `<g transform="translate(${x-300*1.9} ${1180+380*1.9}) scale(1.9 -1.9)" opacity=".12">${S.woman}</g>`)},
 eyes:(t,k)=>{const key=t<EV.glance?'blank':(t<EV.resolve?'glance':'resolve');
  return full(`<rect width="1080" height="1920" fill="#09090b"/>`+cam(man(key,'0 0 300 320',-120,300,1320,1408),1.15+0.12*ease(k),540,1000,0,-40))},
 flyer:(t,k)=>{const fl=(n,x,y,r,s)=>`<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})"><image href="../../assets/flyers/${n}.png" x="0" y="0" width="520" height="${n=='flyer_b'?904:(n=='flyer_a'?720:750)}"/>
   <rect x="200" y="-14" width="120" height="34" fill="#9a988f" opacity=".8" transform="rotate(${r*-1.5} 260 3)"/></g>`;
  return full(`<rect width="1080" height="1920" fill="#08080a"/><circle cx="160" cy="-100" r="900" fill="url(#glowW)" opacity=".16"/>`+
  cam(`<rect x="300" y="-200" width="480" height="2400" fill="#1d1d21"/><rect x="300" y="-200" width="70" height="2400" fill="#141418"/>${[0,1,2,3,4,5,6].map(j=>`<rect x="300" y="${j*300}" width="480" height="8" fill="#0e0e10" opacity=".7"/>`).join('')}
   ${fl('flyer_a',330,260,-4,0.78)}${fl('flyer_c',410,880,5,0.8)}${fl('flyer_b',290,1380,-2,0.62)}
   <rect x="300" y="-200" width="480" height="2400" fill="url(#tube)" opacity=".18"/>`,1.0+0.1*ease(k),540,900,0,lerp(60,-90,ease(k)))+
  `<rect width="1080" height="1920" fill="#000" opacity=".25"/>`)},
 cap:(t,k)=>{const c=ease((t-EV.cap)/0.25);return full(`<rect width="1080" height="1920" fill="#0b0b0d"/><circle cx="540" cy="700" r="600" fill="url(#glowW)" opacity=".12"/>`+
   cam(bottle(540,1350,3.2,true,0,c)+grip(540,1350,3.2,0),1.0+0.05*ease(k),540,800))},
 black:(t,k,t0)=>{const d=t-t0;const y=lerp(300,1700,Math.min(1,d/0.35));
  return full(`<rect width="1080" height="1920" fill="#050506"/><rect x="0" y="${y}" width="1080" height="${lerp(40,6,d/0.35)}" fill="#e9e6df" opacity="${0.5*Math.max(0,1-d/0.35)}"/>`)},
 neon:(t,k)=>full(`<rect width="1080" height="1920" fill="#0b0b0d"/>`)
};
function render(t){
 const sh=TL.shots.find(s=>t>=s[0]&&t<s[1])||TL.shots[TL.shots.length-1];
 const k=(t-sh[0])/(sh[1]-sh[0]);
 const sc=document.getElementById('scene'); sc.innerHTML=SCN[sh[2]](t,k,sh[0]);
 if(sh[2]==='black'){const d=t-sh[0];const fl=[1,0,1,1,0,0,1,0,1,1,1,1];const on=d<0.2?0:(d<0.75?fl[Math.floor((d-0.2)/0.05)%fl.length]:1);
  const out=lerp(1,0,(d-(sh[1]-sh[0])-(-0.25))/0.25);
  sc.innerHTML+=`<div style="position:absolute;left:0;right:0;top:760px;text-align:center;opacity:${on*out}">
  <div class="neon" style="writing-mode:horizontal-tb;font-size:96px;letter-spacing:.04em">そうだ、風俗行こう。</div>
  <div style="margin-top:46px;color:#d9d9d9;font-size:40px;letter-spacing:.3em">#${TL.no}　${TL.title}</div></div>
  <div style="position:absolute;left:0;right:0;top:0;height:1920px;background:radial-gradient(ellipse 70% 30% at 50% 42%,rgba(255,46,136,${0.14*on*out}),rgba(0,0,0,0) 70%)"></div>`}
 if(t>=EV.neon){const kk=t-EV.neon;const fl=[1,0,1,1,0,0,1,0,1,1,1,1];const on=kk>0.6?1:fl[Math.floor(kk/0.05)%fl.length];
  sc.innerHTML+=`<div style="position:absolute;left:0;right:0;top:560px;display:flex;justify-content:center;gap:40px;opacity:${on}">
  <div class="neon" style="font-size:150px">風俗行こう。</div><div class="neon" style="font-size:110px">そうだ、</div></div>
  <div style="position:absolute;left:0;right:0;top:1570px;text-align:center;color:#d9d9d9;font-size:34px;letter-spacing:.5em;opacity:${lerp(0,.8,(kk-1.6)/0.8)}">くだらない世界<div style="font-size:26px;letter-spacing:.3em;margin-top:18px;opacity:.7">#${TL.no}</div></div>
  <div style="position:absolute;left:0;right:0;top:0;height:1920px;background:radial-gradient(ellipse 70% 45% at 50% 42%,rgba(255,46,136,${0.16*on}),rgba(0,0,0,0) 70%)"></div>`}
 const s=TL.subs.find(x=>t>=x[0]&&t<x[1]);const sb=document.getElementById('sub');sb.textContent=s?s[2]:'';document.getElementById('subbg').style.opacity=s?1:0;sb.style.fontSize=t<TL.teaser_end?'62px':'52px';sb.style.top=t<TL.teaser_end?'1300px':'1360px';
 document.getElementById('grain').src='grain/g'+(Math.floor(t*24)%6)+'.png';
 let f=0; if(t>TL.total-0.6)f=(t-(TL.total-0.6))/0.6; document.getElementById('fade').style.opacity=f;
}
window.render=render;

</script></body></html>"""

html = HTML.replace("__SVGS__", json.dumps(svgs)).replace("__TL__", json.dumps(tl, ensure_ascii=False))
(D / "ep.html").write_text(html, encoding="utf-8")
print("ok")
