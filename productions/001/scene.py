"""Builds ep001 page: render(t) draws the frame at time t (seconds)."""
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
#fade{position:absolute;inset:0;background:#000;opacity:0}
.neon{writing-mode:vertical-rl;font-weight:700;letter-spacing:.06em;line-height:1;color:#ffe3f0;-webkit-text-stroke:3px #ff2e88;
 text-shadow:0 0 6px #ff7ab4,0 0 18px #ff2e88,0 0 42px #ff2e88,0 0 90px rgba(255,46,136,.8),0 0 160px rgba(255,46,136,.5)}
</style></head><body><div id="st"><div id="scene"></div><img id="grain" src="grain/g0.png"><div id="vig"></div><div id="sub"></div><div id="fade"></div></div>
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

// ---------- scenes (v4)
const TL = __TL__;
const EV = Object.fromEntries(TL.events.map(e=>[e[0],e[1]]));
const SK='#CFCAC0', SKS='#8E8A83';
function palm(x,y,s,r,fill,shade,inner=''){return `<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})">
 ${[0,1,2,3].map(i=>`<rect x="${-100+i*50}" y="${-215+Math.abs(i-1.5)*18}" width="44" height="${190-Math.abs(i-1.5)*22}" rx="22" fill="${fill}"/>`).join('')}
 <path d="M120,-20 C190,-50 225,-120 205,-150 C188,-170 162,-150 152,-118 C142,-88 122,-70 104,-58 Z" fill="${fill}"/>
 <path d="M-112,-50 C-125,60 -60,140 20,140 C105,140 140,70 128,-40 C110,-70 -95,-80 -112,-50 Z" fill="${fill}"/>
 <path d="M-90,10 C-40,30 40,20 100,-10" stroke="${shade}" stroke-width="5" fill="none"/><path d="M-80,60 C-20,80 50,60 95,30" stroke="${shade}" stroke-width="4" fill="none"/>
 <path d="M30,-60 C0,0 -10,60 0,120" stroke="${shade}" stroke-width="4" fill="none" opacity=".7"/>${inner}</g>`}
function screenBtn(t,label,pressed){return `<rect x="140" y="420" width="800" height="560" rx="18" fill="url(#screen)"/>
 <text x="540" y="560" text-anchor="middle" font-family="Noto Sans CJK JP" font-size="44" font-weight="700" fill="#2a2a2e">お支払い方法を選択してください</text>
 <rect x="300" y="700" width="480" height="150" rx="16" fill="${pressed?'#0e0e10':'#45454b'}"/><text x="540" y="795" text-anchor="middle" font-family="Noto Sans CJK JP" font-size="54" font-weight="700" fill="#e9e6df">${label}</text>`}
const SCN = {
 touch:(t,k)=>{const fy=lerp(1900,860,ease(k/0.25));const hit=t>EV.beep+0.05&&t<EV.beep+0.5;
  return full(`<rect width="1080" height="1920" fill="#0d0d10"/><circle cx="540" cy="700" r="700" fill="url(#glowW)" opacity=".18"/>`+cam(screenBtn(t,'お会計',hit)+
  (hit?`<circle cx="540" cy="775" r="${lerp(20,160,(t-EV.beep)/0.45)}" fill="none" stroke="#f4f2ee" stroke-width="4" opacity="${1-(t-EV.beep)/0.45}"/>`:'')+
  `<g transform="translate(560 ${fy})"><rect x="-38" y="-80" width="76" height="420" rx="38" fill="${SK}"/><rect x="-26" y="-70" width="52" height="60" rx="20" fill="#e2ddd3"/>
   <path d="M-38,140 C-140,150 -170,420 -120,700 L160,700 C200,420 150,180 38,150 Z" fill="${SK}"/><path d="M38,160 C80,170 110,230 100,330" stroke="${SKS}" stroke-width="5" fill="none"/>
   <path d="M-120,700 C-110,600 -80,520 -40,480 L-60,700 Z" fill="#2a2a2e"/></g>`,1.02+0.06*ease(k),540,800))},
 four:(t,k)=>{let s=`<rect width="1080" height="1920" fill="#0f0f12"/>${tubes(t)}<rect x="0" y="1500" width="1080" height="420" fill="#141418"/>`;
   const xs=[-250,90,430,770];
   xs.forEach((x,i)=>{s+=`<g transform="translate(${x+lerp(0,-40,ease(k))} 640) scale(0.55)">${kiosk(t+i*0.37,['ご利用ありがとう','ございます',34])}</g>`});
   s+=`<rect x="380" y="520" width="320" height="70" rx="8" fill="#2a2a2e"/><text x="540" y="568" text-anchor="middle" font-family="Noto Sans CJK JP" font-size="34" font-weight="700" fill="#b4b2ac">セルフレジ</text>
   <g transform="translate(0 170)"><rect x="60" y="0" width="960" height="260" fill="#1d1d21"/><path d="M80,60 Q300,130 540,60 Q780,130 1000,60" stroke="#77777d" stroke-width="10" fill="none" stroke-dasharray="22 10"/>
   <rect x="420" y="80" width="240" height="90" rx="8" fill="#e9e6df"/><text x="540" y="138" text-anchor="middle" font-family="Noto Sans CJK JP" font-size="34" font-weight="700" fill="#0e0e10">休止中</text></g>`;
   return full(cam(s,1.02+0.04*ease(k),540,900))},
 basket:(t,k)=>{let grid='';for(let i=0;i<12;i++)grid+=`<rect x="${160+i*64}" y="1080" width="30" height="520" fill="#1d1d21"/>`;
  return full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+cam(`<path d="M110,980 L970,980 L900,1650 L180,1650 Z" fill="#2a2a2e"/>${grid}<rect x="110" y="960" width="860" height="40" rx="10" fill="#45454b"/>
  <g transform="rotate(-6 380 800)"><rect x="260" y="420" width="230" height="600" rx="30" fill="#b4b2ac"/><rect x="260" y="420" width="70" height="600" rx="30" fill="#77777d"/><ellipse cx="375" cy="440" rx="115" ry="24" fill="#cfcac0"/>
   <rect x="262" y="600" width="226" height="200" fill="#e9e6df" opacity=".85"/><circle cx="375" cy="700" r="70" fill="none" stroke="#45454b" stroke-width="10"/>${[0,1,2,3,4,5].map(i=>`<line x1="375" y1="700" x2="${375+70*Math.cos(i*Math.PI/3)}" y2="${700+70*Math.sin(i*Math.PI/3)}" stroke="#45454b" stroke-width="6"/>`).join('')}</g>
  <g transform="rotate(4 720 900)"><rect x="520" y="760" width="420" height="260" rx="16" fill="#e9e6df" opacity=".9"/><rect x="540" y="780" width="380" height="220" rx="12" fill="#77777d"/>
   ${[0,1].map(i=>`<line x1="560" y1="${840+i*90}" x2="900" y2="${820+i*90}" stroke="#cfcac0" stroke-width="8"/>${[0,1,2,3].map(j=>`<ellipse cx="${620+j*75}" cy="${833+i*90-j*5}" rx="32" ry="24" fill="#45454b"/>`).join('')}`).join('')}
   <rect x="600" y="730" width="200" height="90" rx="6" fill="#e9e6df" stroke="#0e0e10" stroke-width="3" transform="rotate(-8 700 775)"/><text x="700" y="790" text-anchor="middle" font-family="Noto Sans CJK JP" font-size="40" font-weight="900" fill="#0e0e10" transform="rotate(-8 700 775)">2割引</text>
   <circle cx="790" cy="800" r="${lerp(0,78,ease((t-TL.vo[2][1]-2.4)/0.25))}" fill="#f4f2ee" stroke="#0e0e10" stroke-width="4"/><text x="790" y="818" text-anchor="middle" font-family="Noto Sans CJK JP" font-size="${lerp(0,48,ease((t-TL.vo[2][1]-2.4)/0.25))}" font-weight="900" fill="#0e0e10">半額</text></g>`,1.0+0.07*ease(k),540,900))},
 bust:(t,k)=>full(`<rect width="1080" height="1920" fill="#0f0f12"/>${shelves()}${tubes(t)}`+cam(man('front','70 16 260 420',-20,330,1120,1810),1.0+0.05*ease(k),540,900,0,2*Math.sin(t*1.3))),
 side:(t,k)=>full(`<rect width="1080" height="1920" fill="#1a1a1f"/><rect x="900" y="0" width="180" height="1920" fill="#e9e6df" opacity=".07"/>
  <circle cx="1150" cy="640" r="600" fill="url(#glowW)" opacity=".28"/>`+cam(man('side','100 20 250 380',-60,300,1200,1824),1.0+0.06*ease(k),540,800,-30*ease(k),0)),
 coins:(t,k)=>{const touch=ease((k-0.25)/0.3)-ease((k-0.75)/0.25);
  return full(`<rect width="1080" height="1920" fill="#16161a"/><circle cx="540" cy="900" r="800" fill="url(#glowW)" opacity=".22"/>`+
  `<g filter="url(#blur3)">`+cam(palm(540,1150,1.6,0,SK,SKS,`<circle cx="-30" cy="40" r="34" fill="#b4b2ac" stroke="#77777d" stroke-width="5"/><circle cx="35" cy="25" r="28" fill="#9a988f" stroke="#77777d" stroke-width="5"/><circle cx="10" cy="80" r="24" fill="#b4b2ac" stroke="#77777d" stroke-width="5"/>`)+
  `<g transform="translate(${lerp(760,640,touch)} ${lerp(520,700,touch)}) rotate(160)"><rect x="-30" y="-40" width="60" height="320" rx="30" fill="#e2ddd3"/><rect x="-22" y="-34" width="44" height="50" rx="18" fill="#efebe4"/><rect x="40" y="-20" width="56" height="300" rx="28" fill="#e2ddd3"/></g>`,1.0+0.05*ease(k),540,1000)+`</g>`+
  `<rect width="1080" height="1920" fill="#e9e6df" opacity=".05"/>`)},
 warn:(t,k)=>full(windowBg(t)+cam(kiosk(t,['袋に入れていない','商品があります',42],true),1.6,540,600)),
 clerk:(t,k,t0)=>{const hx=lerp(1400,700,ease((t-EV.clerkin)/0.9));const press=(t>EV.clerkin+1.0&&t<EV.clerkin+1.25)?12:0;
  return full(windowBg(t)+cam(kiosk(t,['袋に入れていない','商品があります',42],t<EV.clerkin+1.1)+palm(250,1110,0.5,-125,SK,SKS)+
  `<g transform="translate(${hx} ${930+press})"><path d="M0 0 C20 -18 60 -20 90 -8 L520 40 L520 140 L80 90 C40 86 10 60 0 40 Z" fill="#2a2a2e"/>
  <path d="M-80,-6 C-55,-24 -10,-20 6,-2 L18,36 C0,62 -36,62 -62,48 L-96,36 C-112,26 -104,0 -80,-6 Z" fill="${SK}"/>
  <path d="M-80,-6 L-170,-2 C-186,2 -186,18 -170,20 L-86,20 Z" fill="${SK}"/><path d="M-60,40 L-140,52 C-152,56 -150,68 -138,68 L-58,58 Z" fill="${SK}"/></g>`,1.7,540,800))},
 clerk2:(t,k)=>{const hx=lerp(700,1400,ease((t-EV.clerkout)/0.6));
  return full(windowBg(t)+cam(kiosk(t,['ご利用ありがとう','ございました',44])+palm(250,1110,0.5,-125,SK,SKS)+
  `<g transform="translate(${hx} 930)"><path d="M0 0 C20 -18 60 -20 90 -8 L520 40 L520 140 L80 90 C40 86 10 60 0 40 Z" fill="#2a2a2e"/>
  <path d="M-80,-6 C-55,-24 -10,-20 6,-2 L18,36 C0,62 -36,62 -62,48 L-96,36 C-112,26 -104,0 -80,-6 Z" fill="${SK}"/>
  <path d="M-80,-6 L-170,-2 C-186,2 -186,18 -170,20 L-86,20 Z" fill="${SK}"/><path d="M-60,40 L-140,52 C-152,56 -150,68 -138,68 L-58,58 Z" fill="${SK}"/></g>`,1.7,540,800))},
 face:(t,k)=>full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+cam(man('blank','0 0 300 320',-40,250,1160,1240),1.0+0.08*ease(k),540,850)),
 receipt:(t,k,t0)=>{const kk=t-t0;const h=lerp(0,900,ease(kk/1.8));const lines=[['セルフレジ 2番',40,0],['レモンサワー 500ml',38,0],['¥198',40,1],['焼き鳥（2本）半額',38,0],['¥149',40,1],['合計',44,0],['¥347',60,1]];
  let txt='';lines.forEach((l,i)=>{const y=420+i*110;txt+=`<text x="${l[2]?780:300}" y="${y}" text-anchor="${l[2]?'end':'start'}" font-family="Noto Sans CJK JP" font-size="${l[1]}" font-weight="${l[1]>50?900:500}" fill="#2a2a2e">${l[0]}</text>`});
  return full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+cam(`<rect x="200" y="1180" width="680" height="220" rx="16" fill="#2a2a2e"/><rect x="250" y="1170" width="580" height="20" rx="6" fill="#0e0e10"/>
  <clipPath id="rc"><rect x="270" y="${1180-h}" width="540" height="${h}"/></clipPath><g clip-path="url(#rc)"><rect x="270" y="280" width="540" height="900" fill="#e9e6df"/><g transform="translate(0 ${900-h})">${txt}</g></g>`,1.0+0.06*ease(k),540,900))},
 hand:(t,k)=>full(`<rect width="1080" height="1920" fill="#0b0b0d"/><circle cx="540" cy="200" r="900" fill="url(#glowW)" opacity=".12"/>`+cam(palm(540,1150,1.7,0,SK,SKS),1.0+0.1*ease(k),540,1000,0,3*Math.sin(t*2))),
 door:(t,k,t0)=>{const d=t-t0;const o=lerp(0,330,ease(d/1.2));const walk=ease((d-0.6)/4.6);
  return full(`<rect width="1080" height="1920" fill="#0d0d10"/>
  <rect x="150" y="300" width="780" height="1500" fill="#16161a"/>${bokeh(t,18,9,350,1300)}<g>${rain(t,120,.55,110,0.08,1300,5)}</g>
  <rect x="150" y="1500" width="780" height="300" fill="#1d1d21"/>`+
  man('back','0 0 400 1000',lerp(340,410,walk),lerp(700,860,walk),lerp(400,260,walk),lerp(1000,650,walk))+
  `<rect x="${150-o}" y="300" width="390" height="1500" fill="#2a2a2e" opacity=".55"/><rect x="${540+o}" y="300" width="390" height="1500" fill="#2a2a2e" opacity=".55"/>
  <rect x="${150-o}" y="300" width="8" height="1500" fill="#77777d"/><rect x="${922+o}" y="300" width="8" height="1500" fill="#77777d"/>
  <rect x="0" y="0" width="150" height="1920" fill="#0b0b0d"/><rect x="930" y="0" width="150" height="1920" fill="#0b0b0d"/><rect x="0" y="0" width="1080" height="300" fill="#0b0b0d"/>`)},
 woman:(t,k)=>{const x=lerp(-420,1500,k);return full(`<rect width="1080" height="1920" fill="#0b0b0d"/>${bokeh(t,14,21,200,1000)}
  <rect x="0" y="1180" width="1080" height="740" fill="#141418"/>${rain(t,90,.5,90,0.05,1400,8)}
  <g opacity=".35">${bokeh(t,10,33,1250,1800)}</g>`+`<g transform="translate(${x-300*1.9} ${1180-380*1.9}) scale(1.9)">${S.woman}</g>`)},
 eyes:(t,k)=>{const key=t<EV.glance?'blank':(t<EV.resolve?'glance':'resolve');
  return full(`<rect width="1080" height="1920" fill="#09090b"/>`+cam(man(key,'0 0 300 320',-120,300,1320,1408),1.15+0.12*ease(k),540,1000,0,-40))},
 flyer:(t,k)=>{const fl=(n,x,y,r,s)=>`<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})"><image href="../../assets/flyers/${n}.png" x="0" y="0" width="520" height="${n=='flyer_b'?904:(n=='flyer_a'?720:750)}"/>
   <rect x="200" y="-14" width="120" height="34" fill="#9a988f" opacity=".8" transform="rotate(${r*-1.5} 260 3)"/></g>`;
  return full(`<rect width="1080" height="1920" fill="#08080a"/><circle cx="160" cy="-100" r="900" fill="url(#glowW)" opacity=".16"/>`+
  cam(`<rect x="300" y="-200" width="480" height="2400" fill="#1d1d21"/><rect x="300" y="-200" width="70" height="2400" fill="#141418"/>${[0,1,2,3,4,5,6].map(j=>`<rect x="300" y="${j*300}" width="480" height="8" fill="#0e0e10" opacity=".7"/>`).join('')}
   ${fl('flyer_c',330,260,-5,0.78)}${fl('flyer_a',410,860,4,0.8)}${fl('flyer_b',290,1330,-3,0.62)}
   <rect x="300" y="-200" width="480" height="2400" fill="url(#tube)" opacity=".18"/>`,1.0+0.1*ease(k),540,900,0,lerp(60,-90,ease(k)))+
  `<g opacity=".9">${rain(t,120,.5,110,0.07,1400,13)}</g><rect width="1080" height="1920" fill="#000" opacity=".22"/>`)},
 teaser:(t,k,t0)=>{const d=t-t0;const hx=lerp(1050,520,ease(d/1.5));
  return full(windowBg(t)+cam(kiosk(t,['袋に入れていない','商品があります',42],true)+palm(250,1110,0.5,-125,SK,SKS)+
  `<g transform="translate(${hx} 1000)"><path d="M0 0 C20 -18 60 -20 90 -8 L520 40 L520 140 L80 90 C40 86 10 60 0 40 Z" fill="#2a2a2e"/>
  <path d="M-80,-6 C-55,-24 -10,-20 6,-2 L18,36 C0,62 -36,62 -62,48 L-96,36 C-112,26 -104,0 -80,-6 Z" fill="${SK}"/>
  <path d="M-80,-6 L-170,-2 C-186,2 -186,18 -170,20 L-86,20 Z" fill="${SK}"/><path d="M-60,40 L-140,52 C-152,56 -150,68 -138,68 L-58,58 Z" fill="${SK}"/></g>`,1.95+0.25*ease(k),380,1040,170,-60))},
 black:(t,k,t0)=>{const d=t-t0;const y=lerp(300,1700,Math.min(1,d/0.35));const o=lerp(0,1,(d-0.15)/0.2)*lerp(1,0,(d-1.0)/0.25);
  return full(`<rect width="1080" height="1920" fill="#050506"/><rect x="0" y="${y}" width="1080" height="${lerp(40,6,d/0.35)}" fill="#e9e6df" opacity="${0.5*Math.max(0,1-d/0.35)}"/>
  <g opacity="${o}"><text x="540" y="900" text-anchor="middle" font-family="Noto Serif CJK JP" font-size="92" font-weight="700" letter-spacing="28" fill="#ece9e2">くだらない世界</text>
  <line x1="380" y1="975" x2="700" y2="975" stroke="#77777d" stroke-width="2"/>
  <text x="540" y="1060" text-anchor="middle" font-family="Noto Serif CJK JP" font-size="48" letter-spacing="10" fill="#b4b2ac">#${TL.no}　${TL.title}</text></g>`)},
 neon:(t,k)=>full(`<rect width="1080" height="1920" fill="#0b0b0d"/><g opacity=".55">${rain(t,70,.3,90,0.1,1000,2)}</g>`)
};
function render(t){
 const sh=TL.shots.find(s=>t>=s[0]&&t<s[1])||TL.shots[TL.shots.length-1];
 const k=(t-sh[0])/(sh[1]-sh[0]);
 const sc=document.getElementById('scene'); sc.innerHTML=SCN[sh[2]](t,k,sh[0]);
 if(t>=EV.neon){const kk=t-EV.neon;const fl=[1,0,1,1,0,0,1,0,1,1,1,1];const on=kk>0.6?1:fl[Math.floor(kk/0.05)%fl.length];
  sc.innerHTML+=`<div style="position:absolute;left:0;right:0;top:560px;display:flex;justify-content:center;gap:40px;opacity:${on}">
  <div class="neon" style="font-size:150px">風俗行こう。</div><div class="neon" style="font-size:110px">そうだ、</div></div>
  <div style="position:absolute;left:0;right:0;top:1570px;text-align:center;color:#d9d9d9;font-size:34px;letter-spacing:.5em;opacity:${lerp(0,.8,(kk-1.6)/0.8)}">くだらない世界<div style="font-size:26px;letter-spacing:.3em;margin-top:18px;opacity:.7">#001</div></div>
  <div style="position:absolute;left:0;right:0;top:0;height:1920px;background:radial-gradient(ellipse 70% 45% at 50% 42%,rgba(255,46,136,${0.16*on}),rgba(0,0,0,0) 70%)"></div>`}
 const s=TL.subs.find(x=>t>=x[0]&&t<x[1]);const sb=document.getElementById('sub');sb.textContent=s?s[2]:'';sb.style.fontSize=t<TL.teaser_end?'62px':'52px';sb.style.top=t<TL.teaser_end?'1300px':'1360px';
 document.getElementById('grain').src='grain/g'+(Math.floor(t*24)%6)+'.png';
 let f=0; if(t>TL.total-0.6)f=(t-(TL.total-0.6))/0.6; document.getElementById('fade').style.opacity=f;
}
window.render=render;

</script></body></html>"""

html = HTML.replace("__SVGS__", json.dumps(svgs)).replace("__TL__", json.dumps(tl, ensure_ascii=False))
(D / "ep001.html").write_text(html, encoding="utf-8")
print("ok")
