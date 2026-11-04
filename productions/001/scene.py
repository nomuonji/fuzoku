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

subs = json.loads((D / "timeline.json").read_text())["subs"]

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
const SUBS = __SUBS__;
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

// ---------- scenes
const SC=[];
function add(a,b,f){SC.push([a,b,f])}
// S1 kiosk wide 0-5
add(0,5,t=>{const k=t/5;return full(windowBg(t)+cam(kiosk(t,['ご利用ありがとうございます','バーコードをスキャンしてください']),1.0+0.07*ease(k),540,800))});
// S2 bust under tubes 5-10.2
add(5,10.2,t=>{const k=(t-5)/5.2;return full(`<rect width="1080" height="1920" fill="#0f0f12"/>${shelves()}${tubes(t)}`+
 cam(man('front','70 16 260 420',-20,330,1120,1810),1.0+0.05*ease(k),540,900,0,2*Math.sin(t*1.3)))});
// S3 can & scanner 10.2-17
add(10.2,17,t=>{const k=(t-10.2)/6.8;const rot=t*0.9;let bands='';
 for(let i=0;i<10;i++){const ph=((i/10+rot)%1);const x=380+Math.sin(ph*Math.PI*2)*170;const vis=Math.cos(ph*Math.PI*2);if(vis<0)continue;
  bands+=`<rect x="${x-14*vis}" y="640" width="${28*vis}" height="560" fill="${i%3?'#77777d':'#e9e6df'}" opacity="${0.3+0.6*vis}"/>`}
 const bc=((0.2+rot)%1);const bx=540+Math.sin(bc*Math.PI*2)*170,bv=Math.cos(bc*Math.PI*2);
 const flash=(t>10.55&&t<10.75)?1:0;
 return full(`<rect width="1080" height="1920" fill="#0d0d10"/><rect x="0" y="1300" width="1080" height="620" fill="#1d1d21"/>
 <rect x="160" y="1330" width="760" height="160" rx="10" fill="#0e0e10"/><line x1="180" y1="1410" x2="900" y2="1410" stroke="#f4f2ee" stroke-width="${3+flash*6}" opacity="${0.45+flash*0.5}"/>
 ${flash?'<rect x="160" y="1330" width="760" height="160" rx="10" fill="#fff" opacity=".18"/>':''}`+
 cam(`<g transform="rotate(${-8+4*Math.sin(t*0.8)} 540 920)"><rect x="370" y="600" width="340" height="640" rx="40" fill="#b4b2ac"/>
 <rect x="370" y="600" width="90" height="640" rx="40" fill="#77777d"/><rect x="370" y="600" width="340" height="60" rx="30" fill="#cfcac0"/>
 <g clip-path="none">${bands.replace(/x="(\S+)"/g,(m,v)=>`x="${(+v+160).toFixed(1)}"`)}</g>
 ${bv>0?`<g opacity="${bv}"><rect x="${bx-60*bv}" y="1050" width="${120*bv}" height="90" fill="#e9e6df"/>${[...Array(12)].map((_,j)=>`<rect x="${bx-55*bv+j*9*bv}" y="1058" width="${(2+(j%3))*bv}" height="74" fill="#0e0e10"/>`).join('')}</g>`:''}
 <path d="M300 760 C250 820 250 980 300 1040 L380 1030 L380 770 Z" fill="#8e8a83"/><path d="M780 780 C840 840 830 990 770 1050 L700 1040 L700 790 Z" fill="#cfcac0"/></g>`,1.0+0.06*ease(k),540,950))});
// S4a warning 17-19.6
add(17,19.6,t=>{const on=Math.floor((t-17)*2.5)%2===0;return full(windowBg(t)+cam(kiosk(t,[on?'袋に入れていない':'',on?'商品があります':'',40]),1.9,540,780))});
// S4b side profile 19.6-27
add(19.6,27,t=>{const k=(t-19.6)/7.4;return full(`<rect width="1080" height="1920" fill="#1a1a1f"/><rect x="900" y="0" width="180" height="1920" fill="#e9e6df" opacity=".07"/>
 <circle cx="1150" cy="640" r="600" fill="url(#glowW)" opacity=".28"/>`+cam(man('side','100 20 250 380',-60,300,1200,1824),1.0+0.06*ease(k),540,800,-30*ease(k),0))});
// S5a age lamp 27-29.4
add(27,29.4,t=>full(windowBg(t)+cam(kiosk(t,['年齢確認が必要です','係員をお呼びしています',40],true),1.55,540,560)));
// S5b face blank 29.4-36
add(29.4,36,t=>{const k=(t-29.4)/6.6;const lampOn=Math.floor(t*2.2)%2===0;return full(`<rect width="1080" height="1920" fill="#0d0d10"/>
 ${lampOn?'<circle cx="540" cy="80" r="700" fill="url(#glowW)" opacity=".22"/>':''}`+cam(man('blank','0 0 300 320',-40,250,1160,1240),1.0+0.08*ease(k),540,1000))});
// S6 staff hand 36-39.8
add(36,39.8,t=>{const k=(t-36);const hx=lerp(1350,640,ease((k-0.3)/1.1));const press=(t>37.6&&t<37.9)?14:0;const pressed=t>37.7;
 return full(windowBg(t)+cam(kiosk(t,[pressed?'確認しました':'年齢確認が必要です',pressed?'':'係員をお呼びしています',40],!pressed,pressed?'on':'off')+
 `<g transform="translate(${hx} ${930+press})"><path d="M0 0 C20 -18 60 -20 90 -8 L420 40 L420 140 L80 90 C40 86 10 60 0 40 Z" fill="#2a2a2e"/>
 <path d="M-90 -10 C-60 -30 -10 -24 6 -4 L20 40 C0 70 -40 70 -70 54 L-110 40 C-130 30 -120 0 -90 -10 Z" fill="#cfcac0"/>
 <path d="M-90 -10 L-160 -4 C-176 0 -176 18 -160 20 L-96 22 Z" fill="#cfcac0"/></g>`,1.6,540,800))});
// S6b face 39.8-43.2
add(39.8,43.2,t=>{const k=(t-39.8)/3.4;return full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+cam(man('distant','0 0 300 320',-40,250,1160,1240),1.08+0.05*ease(k),540,850,0,-20))});
// S7 receipt 43.2-49
add(43.2,49,t=>{const k=t-43.2;const h=lerp(0,900,ease(k/1.9));const lines=[['セルフレジ 3番',40,0],['缶チューハイ',40,0],['¥162',40,1],['合計',44,0],['¥162',44,1],['今回のポイント',44,0],['2P',96,1]];
 let txt='';lines.forEach((l,i)=>{const y=420+i*110;if(y>1180-h+60){} txt+=`<text x="${l[2]?780:300}" y="${y}" text-anchor="${l[2]?'end':'start'}" font-family="Noto Sans CJK JP" font-size="${l[1]}" font-weight="${l[1]>60?900:500}" fill="#2a2a2e">${l[0]}</text>`});
 return full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+cam(`<rect x="200" y="1180" width="680" height="220" rx="16" fill="#2a2a2e"/><rect x="250" y="1170" width="580" height="20" rx="6" fill="#0e0e10"/>
 <clipPath id="rc"><rect x="270" y="${1180-h}" width="540" height="${h}"/></clipPath>
 <g clip-path="url(#rc)"><rect x="270" y="280" width="540" height="900" fill="#e9e6df"/><g transform="translate(0 ${900-h})">${txt}</g></g>`,1.0+0.08*ease(k/5.8),540,900))});
// S8 door 49-53
add(49,53,t=>{const k=t-49;const o=lerp(0,330,ease(k/1.2));const walk=ease((k-0.6)/3.4);
 return full(`<rect width="1080" height="1920" fill="#0d0d10"/>
 <rect x="150" y="300" width="780" height="1500" fill="#16161a"/>${'<g>'+bokeh(t,18,9,350,1300)+'</g>'}<g>${rain(t,120,.55,110,0.08,1300,5)}</g>
 <rect x="150" y="1500" width="780" height="300" fill="#1d1d21"/>`+
 man('back','0 0 400 1000',lerp(340,410,walk),lerp(700,860,walk),lerp(400,260,walk),lerp(1000,650,walk))+
 `<rect x="${150-o}" y="300" width="390" height="1500" fill="#2a2a2e" opacity=".55"/><rect x="${540+o}" y="300" width="390" height="1500" fill="#2a2a2e" opacity=".55"/>
 <rect x="${150-o}" y="300" width="8" height="1500" fill="#77777d"/><rect x="${922+o}" y="300" width="8" height="1500" fill="#77777d"/>
 <rect x="0" y="0" width="150" height="1920" fill="#0b0b0d"/><rect x="930" y="0" width="150" height="1920" fill="#0b0b0d"/><rect x="0" y="0" width="1080" height="300" fill="#0b0b0d"/>`)});
// S9 woman 53-55.6
add(53,55.6,t=>{const k=(t-53)/2.6;const x=lerp(-420,1500,k);return full(`<rect width="1080" height="1920" fill="#0b0b0d"/>${bokeh(t,14,21,200,1000)}
 <rect x="0" y="1180" width="1080" height="740" fill="#141418"/>${rain(t,90,.5,90,0.05,1400,8)}
 <g opacity=".35">${bokeh(t,10,33,1250,1800)}</g>`+`<g transform="translate(${x-300*1.9} ${1180-380*1.9}) scale(1.9)">${S.woman}</g>`)});
// S10 glance -> resolve 55.6-58.4
add(55.6,58.4,t=>{const key=t<55.9?'blank':(t<57.0?'glance':'resolve');const k=(t-55.6)/2.8;
 return full(`<rect width="1080" height="1920" fill="#09090b"/>`+cam(man(key,'0 0 300 320',-120,300,1320,1408),1.15+0.12*ease(k),540,1000,0,-40))});
// S11 neon 58.4-64
add(58.4,64.2,t=>{return full(`<rect width="1080" height="1920" fill="#0b0b0d"/><g opacity=".55">${rain(t,70,.3,90,0.1,1000,2)}</g>`)});

function render(t){
 let cur=SC.find(s=>t>=s[0]&&t<s[1])||SC[SC.length-1];
 document.getElementById('scene').innerHTML=cur[2](t);
 // neon overlay
 const sc=document.getElementById('scene');
 if(t>=58.4){const k=t-58.4;const fl=[1,0,1,1,0,0,1,0,1,1,1,1];const on=k>0.6?1:fl[Math.floor(k/0.05)%fl.length];
  sc.innerHTML+=`<div style="position:absolute;left:0;right:0;top:560px;display:flex;justify-content:center;gap:40px;opacity:${on}">
  <div class="neon" style="font-size:150px">風俗行こう。</div><div class="neon" style="font-size:110px">そうだ、</div></div>
  <div style="position:absolute;left:0;right:0;top:1570px;text-align:center;color:#d9d9d9;font-size:34px;letter-spacing:.5em;opacity:${lerp(0,.8,(k-1.2)/0.8)}">くだらない世界<div style="font-size:26px;letter-spacing:.3em;margin-top:18px;opacity:.7">#001</div></div>
  <div style="position:absolute;left:0;right:0;top:0;height:1920px;background:radial-gradient(ellipse 70% 45% at 50% 42%,rgba(255,46,136,${0.16*on}),rgba(0,0,0,0) 70%)"></div>`}
 // subtitle
 const s=SUBS.find(x=>t>=x[0]&&t<x[1]);document.getElementById('sub').textContent=s&&t<58.4?s[2]:'';
 document.getElementById('grain').src='grain/g'+(Math.floor(t*24)%6)+'.png';
 // cut fades: dip at start/end
 let f=0; if(t>63.6)f=(t-63.6)/0.6; document.getElementById('fade').style.opacity=f;
}
window.render=render;
</script></body></html>"""

html = HTML.replace("__SVGS__", json.dumps(svgs)).replace("__SUBS__", json.dumps(subs))
(D / "ep001.html").write_text(html, encoding="utf-8")
print("ok")
