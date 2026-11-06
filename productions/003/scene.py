"""Builds the episode page: render(t) draws the frame at time t (seconds)."""
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

// ---------- #003 shared
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
// ---------- #003 props
// a folded vinyl umbrella on a diagonal; peel 0..1 = the tape band coming off, puff 0..1 = canopy loosening
function folded(peel,puff){const w=60+70*puff;let s=`<g transform="translate(560 960) rotate(-34)">
 <rect x="-14" y="-900" width="28" height="1500" fill="#77777d"/>
 <path d="M0,-760 C${w},-560 ${w*1.25},-120 ${w*0.9},360 L-${w*0.9},360 C-${w*1.25},-120 -${w},-560 0,-760 Z" fill="#e9e6df" opacity=".2"/>
 <path d="M0,-760 C${w},-560 ${w*1.25},-120 ${w*0.9},360" stroke="#f4f2ee" stroke-width="4" fill="none" opacity=".55"/>
 ${[-0.55,-0.2,0.25,0.6].map(f=>`<path d="M0,-740 C${w*f},-500 ${w*f*1.3},-100 ${w*f*0.95},350" stroke="#f4f2ee" stroke-width="2.5" fill="none" opacity=".35"/>`).join('')}
 <rect x="-${w*0.9}" y="340" width="${w*1.8}" height="40" rx="6" fill="#45454b"/>
 <path d="M-14,600 L-14,760 C-14,860 110,860 110,760 L110,720" stroke="#2a2a2e" stroke-width="30" fill="none" stroke-linecap="round"/>`;
 // the tape band: wrapped round the middle, then lifting away
 s+=`<g transform="translate(${lerp(0,110,peel)} ${lerp(-120,-170,peel)}) rotate(${lerp(0,-14,peel)})"><rect x="-${w*1.15}" y="-30" width="${w*2.3}" height="54" rx="10" fill="#f4f2ee" opacity="${lerp(.95,.55,peel)}"/>
 <rect x="${w*0.6}" y="-30" width="${w*0.55}" height="54" rx="10" fill="#cfcac0"/></g></g>`;return s}
function cling(op){ // a loose flap of vinyl lying over the fingers
 return `<path d="M470,880 C560,840 700,860 760,930 C800,990 770,1080 700,1110 C640,1135 560,1090 520,1030 C490,985 455,930 470,880 Z" fill="#f4f2ee" opacity="${0.22*op}"/>
 <path d="M470,880 C560,840 700,860 760,930 C800,990 770,1080 700,1110" stroke="#fff" stroke-width="4" fill="none" opacity="${0.6*op}"/>
 <path d="M540,930 C600,950 660,990 690,1050" stroke="#fff" stroke-width="3" fill="none" opacity="${0.45*op}"/>`}
function vinylShot(t,tp){const peel=ease((t-tp)/1.2), puff=ease((t-tp-0.6)/1.4), cl=ease((t-tp-1.3)/1.2);
 return windowBg(t)+`<rect width="1080" height="1920" fill="#000" opacity=".35"/>`+folded(peel,puff)+
  palm(640,1120,1.15,-28,SK,SKS)+cling(cl)}
function drops(n,seed,op,t){let s='';for(let i=0;i<n;i++){const x=hash(i+seed)*1080,y=hash(i*1.9+seed)*1920,r=5+hash(i*4.3+seed)*16;const slide=(hash(i*7.7)>.85)?((t*60*(hash(i)+.5))%300):0;
 s+=`<g opacity="${op}"><circle cx="${x}" cy="${y+slide}" r="${r}" fill="#0e0e10" opacity=".25"/><circle cx="${x-r*0.3}" cy="${y+slide-r*0.3}" r="${r*0.35}" fill="#fff" opacity=".55"/>
 <circle cx="${x}" cy="${y+slide}" r="${r}" fill="none" stroke="#e9e6df" stroke-width="1.5" opacity=".35"/></g>`}return s}
function ribs(cx,cy,n,op){let s='';for(let i=0;i<n;i++){const a=i/n*Math.PI*2+0.2;s+=`<line x1="${cx}" y1="${cy}" x2="${cx+Math.cos(a)*1600}" y2="${cy+Math.sin(a)*1600}" stroke="#e9e6df" stroke-width="5" opacity="${op}"/>`}return s}
function umbrellaHandles(x0,y0,n,sp,s=1){let o='';for(let i=0;i<n;i++){const x=x0+i*sp, h=hash(i+2)*30;
 o+=`<g transform="translate(${x} ${y0+h}) scale(${s})"><path d="M0,0 L0,-300 C0,-380 90,-380 90,-300" stroke="#2a2a2e" stroke-width="22" fill="none" stroke-linecap="round"/>
 <path d="M-34,40 C-30,200 -20,420 0,520 C20,420 30,200 34,40 Z" fill="#e9e6df" opacity=".22"/><path d="M-34,40 C-30,200 -20,420 0,520" stroke="#f4f2ee" stroke-width="3" fill="none" opacity=".45"/>
 <rect x="-36" y="20" width="72" height="30" rx="8" fill="#f4f2ee" opacity=".8"/></g>`}return o}
function street(t){return `<rect width="1080" height="1920" fill="#0b0b0d"/>${bokeh(t,22,5,200,1000)}<rect x="0" y="1150" width="1080" height="770" fill="#111114"/>
 ${[0,1,2,3,4,5].map(i=>`<rect x="${120+i*170+hash(i)*40}" y="1200" width="${8+hash(i*3)*10}" height="${300+hash(i*5)*400}" fill="#e9e6df" opacity="${0.05+0.05*hash(i*2)}" filter="url(#blur8)"/>`).join('')}
 <g opacity=".8">${rain(t,90,.35,90,0.1,1100,21)}</g>`}

// ---------- scenes (#003 ビニール傘)
const SCN = {
 teaser:(t,k)=>full(cam(vinylShot(t,EV.tape_teaser),1.12+0.1*ease(k),600,1000,0,0)),
 station:(t,k)=>{let s=`<rect width="1080" height="1920" fill="#08080a"/>
   <rect x="120" y="420" width="840" height="1200" fill="#141418"/>${bokeh(t,16,8,500,1200).replace(/cx="(\d+)/g,(m,x)=>`cx="${120+(+x)*0.78}`)}
   <g>${rain(t,120,.55,120,0.04,1500,9).replace(/<line/g,'<line clip-path="url(#door)"')}</g>
   <rect x="0" y="0" width="1080" height="440" fill="#1a1a1e"/><rect x="0" y="420" width="1080" height="24" fill="#2a2a2e"/>
   <rect x="0" y="0" width="140" height="1920" fill="#1a1a1e"/><rect x="940" y="0" width="140" height="1920" fill="#1a1a1e"/>
   <rect x="140" y="100" width="800" height="18" rx="9" fill="#f4f2ee" opacity=".8"/><rect x="140" y="118" width="800" height="300" fill="url(#tube)" opacity=".25"/>
   <rect x="0" y="1600" width="1080" height="320" fill="#1d1d21"/>${tiles(1600,.5)}
   <ellipse cx="540" cy="1640" rx="420" ry="18" fill="#e9e6df" opacity=".08"/>`+man('back','0 0 400 1000',330,880,420,1050);
   return full(`<defs><clipPath id="door"><rect x="140" y="440" width="800" height="1160"/></clipPath></defs>`+cam(s,1.0+0.06*ease(k),540,1100))},
 phone:(t,k)=>{if(t>=EV.side_cut)return full(`<rect width="1080" height="1920" fill="#151519"/><circle cx="1150" cy="620" r="620" fill="url(#glowW)" opacity=".28"/>`+
     cam(man('side','100 20 250 380',-60,300,1200,1824),1.0+0.06*ease(k),540,800,-30*ease(k),0)+`<g opacity=".5">${rain(t,40,.3,90,0.06,1100,4)}</g>`);
   const s=`<rect width="1080" height="1920" fill="#0b0b0d"/><circle cx="540" cy="820" r="700" fill="url(#glowW)" opacity=".18"/>
   <rect x="250" y="260" width="580" height="1140" rx="70" fill="#1d1d21"/><rect x="280" y="310" width="520" height="1040" rx="40" fill="url(#screen)"/>
   <text x="540" y="420" text-anchor="middle" ${JP} font-size="34" fill="#45454b">今日の天気</text>
   <g transform="translate(540 600)"><circle cx="-40" cy="-20" r="70" fill="#77777d"/><circle cx="40" cy="-30" r="85" fill="#77777d"/><rect x="-110" y="-10" width="230" height="70" rx="35" fill="#77777d"/>
   ${[-60,-10,40,90].map((x,i)=>`<line x1="${x}" y1="90" x2="${x-14}" y2="140" stroke="#45454b" stroke-width="8" stroke-linecap="round"/>`).join('')}</g>
   <text x="540" y="850" text-anchor="middle" ${JP} font-size="36" fill="#2a2a2e">降水確率</text>
   <text x="540" y="1000" text-anchor="middle" ${JP} font-size="150" font-weight="900" fill="#0e0e10">70%</text>
   <text x="540" y="1110" text-anchor="middle" ${JP} font-size="30" fill="#45454b">傘を持ってお出かけください</text>`;
   return full(cam(s,1.0+0.05*ease(k),540,900))},
 store:(t,k)=>{const s=`<rect width="1080" height="1920" fill="#0a0a0c"/>
   <rect x="60" y="300" width="960" height="120" fill="#e9e6df" opacity=".85"/><rect x="60" y="300" width="960" height="120" fill="url(#tube)" opacity=".4"/>
   <rect x="60" y="420" width="960" height="1000" fill="#1d1d21"/>
   <rect x="300" y="460" width="480" height="940" fill="#f4f2ee" opacity=".9"/><rect x="536" y="460" width="8" height="940" fill="#9a988f"/>
   <circle cx="540" cy="900" r="700" fill="url(#glowW)" opacity=".35"/>
   ${[0,1,2,3,4,5].map(i=>`<rect x="${320+i*76}" y="${560+hash(i)*60}" width="50" height="${140+hash(i*3)*80}" rx="6" fill="#9a988f" opacity=".35"/>`).join('')}
   <rect x="0" y="1400" width="1080" height="520" fill="#141418"/>
   <ellipse cx="540" cy="1520" rx="520" ry="70" fill="#e9e6df" opacity=".1"/>
   <g transform="translate(780 1000)"><path d="M-110,0 L110,0 L90,330 L-90,330 Z" fill="#45454b"/><rect x="-118" y="-8" width="236" height="22" rx="8" fill="#5a5a60"/>
   ${umbrellaHandles(-80,-20,5,40,0.55)}</g>
   <rect x="690" y="1170" width="180" height="70" rx="6" fill="#e9e6df"/><text x="780" y="1218" text-anchor="middle" ${JP} font-size="34" font-weight="900" fill="#0e0e10">傘あります</text>`;
   return full(cam(s,1.0+0.07*ease(k),700,1200,-30*ease(k),0)+`<g opacity=".85">${rain(t,130,.5,120,0.05,1500,17)}</g>`)},
 price:(t,k)=>{if(t>=EV.genkan_cut){const s=`<rect width="1080" height="1920" fill="#0e0e10"/><rect x="0" y="1250" width="1080" height="670" fill="#1d1d21"/>
     <rect x="0" y="0" width="1080" height="1250" fill="#141418"/><rect x="0" y="1230" width="1080" height="30" fill="#2a2a2e"/>
     <rect x="130" y="760" width="820" height="520" rx="10" fill="#2a2a2e"/><rect x="130" y="760" width="820" height="30" fill="#45454b"/>
     <g transform="translate(250 900)">${umbrellaHandles(0,0,6,116,0.85)}</g>
     <rect x="130" y="1280" width="820" height="40" fill="#0e0e10" opacity=".6"/>
     <path d="M200,1560 C230,1520 330,1520 360,1560 L360,1600 L200,1600 Z" fill="#0e0e10"/><path d="M420,1580 C450,1540 550,1540 580,1580 L580,1620 L420,1620 Z" fill="#0e0e10"/>
     <rect width="1080" height="1920" fill="#000" opacity=".35"/>`;
     return full(cam(s,1.0+0.05*ease((t-EV.genkan_cut)/3),540,1000))}
   const s=`<rect width="1080" height="1920" fill="#0c0c0e"/><circle cx="540" cy="760" r="760" fill="url(#glowW)" opacity=".18"/>
   <g transform="translate(240 470)">${umbrellaHandles(0,0,6,120,1.0)}</g>
   <rect x="300" y="880" width="480" height="300" rx="10" fill="#f4f2ee"/><rect x="300" y="880" width="480" height="60" rx="10" fill="#0e0e10"/>
   <text x="540" y="924" text-anchor="middle" ${JP} font-size="34" font-weight="700" fill="#f4f2ee">ビニール傘 65cm</text>
   <text x="540" y="1090" text-anchor="middle" ${JP} font-size="140" font-weight="900" fill="#0e0e10">737<tspan font-size="64">円</tspan></text>
   <text x="540" y="1150" text-anchor="middle" ${JP} font-size="28" fill="#45454b">（税込）</text>`;
   return full(cam(s,1.0+0.06*ease(k),540,950))},
 lost:(t,k)=>{const s=`<rect width="1080" height="1920" fill="#0d0d10"/><rect x="0" y="0" width="1080" height="900" fill="#16161a"/>${tubes(t)}
   ${[0,1,2,3].map(r=>`<rect x="0" y="${330+r*150}" width="1080" height="10" fill="#2a2a2e"/>`).join('')}
   <g transform="translate(560 640) rotate(8)">${umbrellaHandles(-150,0,7,48,0.9)}
   <path d="M-190,350 C-60,330 120,330 170,350" stroke="#9a988f" stroke-width="10" fill="none"/><path d="M-190,560 C-60,540 120,540 170,560" stroke="#9a988f" stroke-width="10" fill="none"/>
   <g transform="translate(150 360) rotate(-8)"><line x1="0" y1="0" x2="30" y2="70" stroke="#9a988f" stroke-width="4"/><rect x="0" y="70" width="190" height="110" rx="6" fill="#e9e6df"/>
   <text x="95" y="122" text-anchor="middle" ${JP} font-size="34" font-weight="900" fill="#0e0e10">忘れ物</text><text x="95" y="162" text-anchor="middle" ${JP} font-size="22" fill="#45454b">保管 1週間</text></g></g>
   <rect x="0" y="1300" width="1080" height="620" fill="#2a2a2e"/><rect x="0" y="1300" width="1080" height="30" fill="#45454b"/>
   <rect x="80" y="1380" width="380" height="240" rx="8" fill="#1d1d21"/><rect x="100" y="1400" width="340" height="150" rx="6" fill="url(#screen)" opacity=".6"/>`;
   return full(cam(s,1.0+0.07*ease(k),560,900,0,-30*ease(k)))},
 tape:(t,k)=>full(cam(vinylShot(t,EV.tape),1.0+0.08*ease(k),600,1000)),
 face:(t,k)=>full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+cam(man('blank','0 0 300 320',-40,250,1160,1240),1.0+0.08*ease(k),540,850)+
   `<g opacity=".7">${rain(t,40,.25,160,0.0,600,31)}</g>${drops(26,40,.6,t)}`),
 under:(t,k)=>{const br=(t-EV.under)%1.8, puff=Math.max(0,1-br/1.4);
   const s=`<rect width="1080" height="1920" fill="#0a0a0c"/>${bokeh(t,30,12,0,1500)}
   <circle cx="540" cy="700" r="1150" fill="#e9e6df" opacity=".07"/>${ribs(540,700,8,.28)}
   <circle cx="540" cy="700" r="26" fill="#45454b"/>${drops(70,50,.9,t)}
   <ellipse cx="${540+br*30}" cy="${1500-br*160}" rx="${120+br*140}" ry="${60+br*70}" fill="#e9e6df" opacity="${0.18*puff}" filter="url(#blur8)"/>
   <rect x="510" y="700" width="60" height="1300" fill="#45454b"/>`;
   return full(cam(s,1.0+0.05*ease(k),540,800,0,6*Math.sin(t*1.3)))},
 walk:(t,k)=>{const s=street(t)+`<ellipse cx="540" cy="1620" rx="260" ry="26" fill="#e9e6df" opacity=".06"/>`+man('back','0 0 400 1000',290,820,500,1250)+
   `<g transform="translate(540 820)"><path d="M-330,120 C-300,-150 300,-150 330,120 C220,90 110,100 0,120 C-110,100 -220,90 -330,120 Z" fill="#e9e6df" opacity=".2"/>
   <path d="M-330,120 C-300,-150 300,-150 330,120" stroke="#f4f2ee" stroke-width="4" fill="none" opacity=".5"/>
   ${[-200,-70,70,200].map(x=>`<path d="M0,-80 Q${x*0.7},-40 ${x*1.4},110" stroke="#f4f2ee" stroke-width="2.5" fill="none" opacity=".3"/>`).join('')}
   <rect x="-5" y="-110" width="10" height="400" fill="#45454b"/></g>`;
   return full(cam(s,1.0+0.05*ease(k),540,1200,0,-40*ease(k)))},
 woman:(t,k)=>{const x=lerp(-420,1500,k);return full(`<rect width="1080" height="1920" fill="#0b0b0d"/>${bokeh(t,16,7,100,700)}<rect x="0" y="900" width="1080" height="1020" fill="#121215"/>
   ${[0,1,2,3,4].map(i=>`<rect x="${100+i*210}" y="1250" width="14" height="${420+hash(i)*200}" fill="#e9e6df" opacity=".06" filter="url(#blur8)"/>`).join('')}`+
   `<g transform="translate(${x-300*1.9} ${1180-380*1.9}) scale(1.9)">${S.woman}</g>`+
   `<g transform="translate(${x-300*1.9} ${1180+380*1.9}) scale(1.9 -1.9)" opacity=".18">${S.woman}</g><g opacity=".8">${rain(t,90,.35,90,0.1,1100,23)}</g>`)},
 eyes:(t,k)=>{const key=t<EV.glance?'blank':(t<EV.resolve?'glance':'resolve');
  return full(`<rect width="1080" height="1920" fill="#09090b"/>`+cam(man(key,'0 0 300 320',-120,300,1320,1408),1.15+0.12*ease(k),540,1000,0,-40))},
 flyer:(t,k)=>{const fl=(n,x,y,r,s)=>`<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})"><image href="../../assets/flyers/${n}.png" x="0" y="0" width="520" height="${n=='flyer_b'?904:(n=='flyer_a'?720:750)}"/>
   <rect x="200" y="-14" width="120" height="34" fill="#9a988f" opacity=".8" transform="rotate(${r*-1.5} 260 3)"/></g>`;
  return full(`<rect width="1080" height="1920" fill="#08080a"/><circle cx="160" cy="-100" r="900" fill="url(#glowW)" opacity=".16"/>`+
  cam(`<rect x="300" y="-200" width="480" height="2400" fill="#1d1d21"/><rect x="300" y="-200" width="70" height="2400" fill="#141418"/>${[0,1,2,3,4,5,6].map(j=>`<rect x="300" y="${j*300}" width="480" height="8" fill="#0e0e10" opacity=".7"/>`).join('')}
   ${fl('flyer_a',330,260,-4,0.78)}${fl('flyer_c',410,880,5,0.8)}${fl('flyer_b',290,1380,-2,0.62)}
   <rect x="300" y="-200" width="480" height="2400" fill="url(#tube)" opacity=".18"/>`,1.0+0.1*ease(k),540,900,0,lerp(60,-90,ease(k)))+
  `<g opacity=".9">${rain(t,90,.4,110,0.07,1400,13)}</g><rect width="1080" height="1920" fill="#000" opacity=".22"/>`+
  // seen through the vinyl: a pale film, two ribs and the beads of rain on it
  `<rect width="1080" height="1920" fill="#e9e6df" opacity=".07"/>${ribs(540,-500,10,.18)}${drops(60,70,.85,t)}`)},
 black:(t,k,t0)=>{const d=t-t0;const y=lerp(300,1700,Math.min(1,d/0.35));
  return full(`<rect width="1080" height="1920" fill="#050506"/><rect x="0" y="${y}" width="1080" height="${lerp(40,6,d/0.35)}" fill="#e9e6df" opacity="${0.5*Math.max(0,1-d/0.35)}"/>`)},
 neon:(t,k)=>full(`<rect width="1080" height="1920" fill="#0b0b0d"/><g opacity=".55">${rain(t,70,.3,90,0.1,1000,2)}</g>`)
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
