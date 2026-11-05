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

// ---------- scenes (#002 ビジネスホテル)
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
// faceless pictogram of a hotel guide bowing (head is a plain disc, no features)
function picto(x,y,s,bow){return `<g transform="translate(${x} ${y}) scale(${s})">
 <path d="M-40,0 L40,0 L62,150 L-62,150 Z" fill="#45454b"/><rect x="-34" y="150" width="20" height="90" fill="#45454b"/><rect x="14" y="150" width="20" height="90" fill="#45454b"/>
 <g transform="rotate(${bow} 0 10)"><rect x="-34" y="-120" width="68" height="130" rx="18" fill="#45454b"/><circle cx="0" cy="-160" r="38" fill="#45454b"/>
 <path d="M-30,-40 L-14,40 L14,40 L30,-40" fill="none" stroke="#45454b" stroke-width="0"/></g></g>`}
function tiles(y0,op=.5){let s='';for(let i=0;i<9;i++){const y=y0+Math.pow(i/8,1.6)*(1920-y0);s+=`<line x1="0" y1="${y}" x2="1080" y2="${y}" stroke="#2a2a2e" stroke-width="3" opacity="${op}"/>`}
 for(let i=-6;i<=6;i++){s+=`<line x1="${540+i*40}" y1="${y0}" x2="${540+i*260}" y2="1920" stroke="#2a2a2e" stroke-width="3" opacity="${op}"/>`}return s}
function hotelKiosk(t,lines,big){ // a check-in machine, centred
 return `<rect x="290" y="560" width="500" height="1240" rx="22" fill="#2a2a2e"/><rect x="290" y="560" width="110" height="1240" rx="22" fill="#1d1d21"/>
 <rect x="330" y="640" width="420" height="320" rx="10" fill="url(#screen)"/>
 ${lines.map((l,i)=>`<text x="540" y="${780+i*56-(lines.length-1)*28}" text-anchor="middle" ${JP} font-size="${big||34}" font-weight="700" fill="#0e0e10">${l}</text>`).join('')}
 <rect x="390" y="1020" width="300" height="90" rx="10" fill="#0e0e10"/><rect x="420" y="1050" width="240" height="30" rx="4" fill="#45454b"/>
 <rect x="360" y="1190" width="360" height="26" rx="6" fill="#0e0e10"/><text x="540" y="1270" text-anchor="middle" ${JP} font-size="24" fill="#77777d">カードキー</text>
 <rect x="330" y="1400" width="420" height="200" rx="10" fill="#1d1d21"/>
 <circle cx="540" cy="760" r="420" fill="url(#glowW)" opacity=".22"/>`}
function lobbyBg(t){return `<rect width="1080" height="1920" fill="#0d0d10"/><rect x="0" y="1300" width="1080" height="620" fill="#141418"/>${tiles(1300,.6)}
 <rect x="0" y="0" width="1080" height="1300" fill="#111114"/>`}
// a hotel room: wall, headboard, bed with two pillows. lit: 0..1
function roomBg(t,lit){const g=v=>Math.round(v);return `<rect width="1080" height="1920" fill="#16161a"/>
 <rect x="0" y="0" width="1080" height="1150" fill="#3a3a40"/>${[0,1,2,3,4,5,6,7,8].map(i=>`<rect x="${i*130}" y="0" width="2" height="1150" fill="#2f2f35"/>`).join('')}
 <rect x="80" y="620" width="920" height="420" rx="10" fill="#2a2a2e"/>
 <path d="M0,1080 L1080,1080 L1080,1920 L0,1920 Z" fill="#9a988f"/>
 <path d="M0,1080 L1080,1080 L1080,1180 L0,1180 Z" fill="#b4b2ac"/>
 <path d="M0,1400 C300,1370 700,1430 1080,1380 L1080,1920 L0,1920 Z" fill="#cfcac0"/><path d="M0,1400 C300,1370 700,1430 1080,1380" stroke="#e9e6df" stroke-width="10" fill="none"/>
 <rect x="150" y="920" width="360" height="200" rx="60" fill="#e9e6df"/><rect x="150" y="1040" width="360" height="80" rx="40" fill="#cfcac0"/>
 <rect x="570" y="920" width="360" height="200" rx="60" fill="#e9e6df"/><rect x="570" y="1040" width="360" height="80" rx="40" fill="#cfcac0"/>
 <path d="M240,1010 C300,990 380,1000 430,1020" stroke="#b4b2ac" stroke-width="6" fill="none"/>
 <circle cx="1000" cy="560" r="${300}" fill="url(#glowW)" opacity="${0.35*lit}"/><rect x="960" y="480" width="70" height="120" rx="12" fill="#e9e6df" opacity="${0.4+0.6*lit}"/>
 <rect width="1080" height="1920" fill="#000" opacity="${lerp(0.82,0.12,lit)}"/>`}
function waterOnWall(t,stop){let s='';const a=Math.max(0,1-(t-stop)/0.35);for(let i=0;i<14;i++){const x=hash(i+4)*1080, y=((t*260*(0.6+hash(i*7))+hash(i*3)*1100)%1100);
 s+=`<line x1="${x}" y1="${y}" x2="${x}" y2="${y+40}" stroke="#e9e6df" stroke-width="2" opacity="${(0.10*a).toFixed(3)}"/>`}return s}
const SCN = {
 teaser:(t,k,t0)=>full(cam(roomBg(t,0.55)+waterOnWall(t,EV.shower_stop_teaser),1.12+0.12*ease(k),540,900,0,40)+
   `<rect width="1080" height="1920" fill="#000" opacity=".25"/>`),
 lobby:(t,k)=>{let s=lobbyBg(t)+`<rect x="40" y="760" width="520" height="560" fill="#1a1a1e"/><rect x="40" y="740" width="520" height="30" fill="#2a2a2e"/>
   <rect x="120" y="560" width="360" height="110" rx="6" fill="#1d1d21"/><text x="300" y="608" text-anchor="middle" ${JP} font-size="30" font-weight="700" fill="#45454b">フロント</text>
   <text x="300" y="648" text-anchor="middle" ${JP} font-size="24" fill="#45454b">FRONT</text>
   <rect x="170" y="840" width="260" height="120" rx="6" fill="#b4b2ac" opacity=".85"/><text x="300" y="888" text-anchor="middle" ${JP} font-size="24" font-weight="700" fill="#0e0e10">フロント営業時間</text>
   <text x="300" y="930" text-anchor="middle" ${JP} font-size="30" font-weight="900" fill="#0e0e10">7:00〜22:00</text>
   <g transform="translate(470 610) scale(.62)">${hotelKiosk(t,['チェックイン'],46)}</g>
   <circle cx="805" cy="1080" r="520" fill="url(#glowW)" opacity=".16"/>
   <ellipse cx="805" cy="1560" rx="200" ry="40" fill="#e9e6df" opacity=".06"/>`;
   return full(cam(s,1.0+0.06*ease(k),760,1000,-40*ease(k),0))},
 kiosk:(t,k,t0)=>{const d=t-t0;const L1=TL.vo.find(v=>v[0]===1);const bow=lerp(0,40,ease((t-L1[1]-L1[2]*0.62)/0.6));const qx=lerp(1400,800,ease((t-EV.qr_beep+0.9)/0.8));
   const hit=t>EV.qr_beep&&t<EV.qr_beep+0.45;
   let s=`<rect width="1080" height="1920" fill="#0d0d10"/><circle cx="540" cy="760" r="760" fill="url(#glowW)" opacity=".2"/>
   <rect x="110" y="300" width="860" height="1000" rx="26" fill="#2a2a2e"/><rect x="150" y="340" width="780" height="760" rx="14" fill="url(#screen)"/>
   <text x="540" y="470" text-anchor="middle" ${JP} font-size="50" font-weight="700" fill="#0e0e10">QRコードを</text>
   <text x="540" y="540" text-anchor="middle" ${JP} font-size="50" font-weight="700" fill="#0e0e10">かざしてください</text>
   ${picto(540,800,1.0,bow)}
   <rect x="390" y="1150" width="300" height="110" rx="12" fill="#0e0e10"/><rect x="410" y="1170" width="260" height="70" rx="8" fill="${hit?'#f4f2ee':'#45454b'}"/>`;
   s+=`<g transform="translate(${qx} 1000) rotate(-14) scale(.62)"><rect x="-150" y="0" width="300" height="560" rx="36" fill="#1d1d21"/><rect x="-128" y="30" width="256" height="480" rx="14" fill="#e9e6df"/>
   ${[0,1,2,3,4,5,6].map(i=>[0,1,2,3,4,5,6].map(j=>hash(i*7+j+3)>.5||(i<2&&j<2)||(i>4&&j<2)||(i<2&&j>4)?`<rect x="${-98+j*28}" y="${120+i*28}" width="26" height="26" fill="#0e0e10"/>`:'').join('')).join('')}</g>`;
   if(hit)s+=`<rect x="150" y="340" width="780" height="760" rx="14" fill="#fff" opacity="${0.25*(1-(t-EV.qr_beep)/0.45)}"/>`;
   return full(cam(s,1.0+0.05*ease(k),540,800))},
 welcome:(t,k)=>full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+
   cam(`<rect x="120" y="80" width="840" height="420" rx="16" fill="url(#screen)"/><text x="540" y="290" text-anchor="middle" ${JP} font-size="66" font-weight="700" fill="#0e0e10">おかえりなさいませ</text>
   <text x="540" y="370" text-anchor="middle" ${JP} font-size="30" fill="#45454b">カードキーをお取りください</text>
   <circle cx="540" cy="300" r="760" fill="url(#glowW)" opacity=".25"/>`+man('front','70 16 260 420',40,560,1000,1620),1.0+0.05*ease(k),540,900)),
 side:(t,k)=>full(`<rect width="1080" height="1920" fill="#151519"/><circle cx="1150" cy="620" r="620" fill="url(#glowW)" opacity=".3"/>`+cam(man('side','100 20 250 380',-60,300,1200,1824),1.0+0.06*ease(k),540,800,-30*ease(k),0)),
 card:(t,k,t0)=>{const d=t-t0;const out=lerp(0,300,ease((d-0.1)/0.9));const shim=0.5+0.5*Math.sin(t*6);
   return full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+cam(`<rect x="0" y="380" width="1080" height="420" fill="#2a2a2e"/><rect x="240" y="560" width="600" height="40" rx="8" fill="#0e0e10"/>
   <g transform="translate(0 ${out})"><rect x="300" y="300" width="480" height="300" rx="18" fill="#e9e6df"/><rect x="300" y="350" width="480" height="40" fill="#45454b"/>
   <text x="540" y="500" text-anchor="middle" ${JP} font-size="64" font-weight="900" fill="#2a2a2e">817</text>
   ${[0,1,2].map(i=>`<path d="M${420+i*100},290 C${400+i*100},250 ${440+i*100},220 ${420+i*100},180" stroke="#e9e6df" stroke-width="4" fill="none" opacity="${(0.12+0.08*shim)*ease((d-0.6)/0.6)}"/>`).join('')}</g>
   <rect x="0" y="0" width="1080" height="580" fill="#2a2a2e"/><rect x="240" y="560" width="600" height="20" rx="6" fill="#0e0e10"/>`+
   palm(540,1150,1.1,0,SK,SKS),1.0+0.06*ease(k),540,900))},
 room:(t,k)=>{const lit=ease((t-EV.roomlight)/0.25);return full(cam(roomBg(t,lit),1.0+0.05*ease(k),540,1000)+
   `<g opacity="${1-lit}"><rect x="80" y="520" width="140" height="220" rx="10" fill="#2a2a2e"/><rect x="110" y="560" width="80" height="20" rx="4" fill="#0e0e10"/>
   <rect x="120" y="${lerp(420,540,ease((t-EV.roomlight+0.5)/0.4))}" width="60" height="40" fill="#e9e6df"/></g>`)},
 wall:(t,k)=>full(cam(roomBg(t,0.75)+waterOnWall(t,EV.shower_stop),1.25+0.1*ease(k),540,800,0,-40)),
 face:(t,k)=>full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+cam(man('blank','0 0 300 320',-40,250,1160,1240),1.0+0.08*ease(k),540,850)),
 sheet:(t,k)=>full(`<rect width="1080" height="1920" fill="#b4b2ac"/>
   <path d="M0,300 C300,340 600,260 1080,330" stroke="#9a988f" stroke-width="8" fill="none"/><path d="M0,1500 C400,1460 700,1560 1080,1480" stroke="#9a988f" stroke-width="8" fill="none"/>
   <path d="M200,0 C240,500 160,1200 260,1920" stroke="#cfcac0" stroke-width="14" fill="none"/>`+
   cam(palm(560,1000,1.6,-15,SK,SKS),1.0+0.08*ease(k),540,1000,0,2*Math.sin(t*1.5))+`<rect width="1080" height="1920" fill="#000" opacity=".5"/>`),
 elevator:(t,k)=>{const o=lerp(0,230,ease((t-EV.elevator)/1.0));return full(`<rect width="1080" height="1920" fill="#0d0d10"/><rect x="0" y="1500" width="1080" height="420" fill="#1d1d21"/>
   <rect x="250" y="360" width="580" height="1160" fill="#9a988f"/><rect x="250" y="360" width="580" height="1160" fill="url(#tube)" opacity=".5"/>
   <rect x="${310-o}" y="360" width="230" height="1160" fill="#45454b"/><rect x="${540+o}" y="360" width="230" height="1160" fill="#45454b"/>
   <rect x="0" y="0" width="310" height="1920" fill="#1a1a1e"/><rect x="770" y="0" width="310" height="1920" fill="#1a1a1e"/><rect x="0" y="0" width="1080" height="360" fill="#1a1a1e"/>
   <rect x="490" y="250" width="100" height="70" rx="8" fill="#0e0e10"/><text x="540" y="302" text-anchor="middle" ${JP} font-size="46" font-weight="700" fill="#e9e6df">8</text>`+
   man('back','0 0 400 1000',180,700,720,1800))},
 woman:(t,k)=>{const x=lerp(-420,1500,k);return full(lobbyBg(t)+`<circle cx="540" cy="600" r="700" fill="url(#glowW)" opacity=".1"/>`+
   `<g transform="translate(${x-300*1.9} ${1180-380*1.9}) scale(1.9)">${S.woman}</g>`)},
 eyes:(t,k)=>{const key=t<EV.glance?'blank':(t<EV.resolve?'glance':'resolve');
  return full(`<rect width="1080" height="1920" fill="#09090b"/>`+cam(man(key,'0 0 300 320',-120,300,1320,1408),1.15+0.12*ease(k),540,1000,0,-40))},
 flyer:(t,k)=>{const fl=(n,x,y,r,s)=>`<g transform="translate(${x} ${y}) rotate(${r}) scale(${s})"><image href="../../assets/flyers/${n}.png" x="0" y="0" width="520" height="${n=='flyer_b'?904:(n=='flyer_a'?720:750)}"/>
   <rect x="200" y="-14" width="120" height="34" fill="#9a988f" opacity=".8" transform="rotate(${r*-1.5} 260 3)"/></g>`;
  return full(`<rect width="1080" height="1920" fill="#08080a"/><circle cx="160" cy="-100" r="900" fill="url(#glowW)" opacity=".16"/>`+
  cam(`<rect x="300" y="-200" width="480" height="2400" fill="#1d1d21"/><rect x="300" y="-200" width="70" height="2400" fill="#141418"/>${[0,1,2,3,4,5,6].map(j=>`<rect x="300" y="${j*300}" width="480" height="8" fill="#0e0e10" opacity=".7"/>`).join('')}
   ${fl('flyer_a',330,260,-4,0.78)}${fl('flyer_c',410,880,5,0.8)}${fl('flyer_b',290,1380,-2,0.62)}
   <rect x="300" y="-200" width="480" height="2400" fill="url(#tube)" opacity=".18"/>`,1.0+0.1*ease(k),540,900,0,lerp(60,-90,ease(k)))+
  `<g opacity=".9">${rain(t,120,.5,110,0.07,1400,13)}</g><rect width="1080" height="1920" fill="#000" opacity=".22"/>`)},
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
