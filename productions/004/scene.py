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
// ---------- #004 props
const SCR='#d8d5ce';
// the paused film: a dim room, a coat sliding down to the floor, calves and black pumps (no face, nothing above the knee)
function filmFrame(t,paused=true){return `<rect width="1080" height="1920" fill="#121215"/>
 <rect x="0" y="0" width="1080" height="1250" fill="#1a1a1e"/><rect x="620" y="120" width="300" height="760" fill="#e9e6df" opacity=".08"/>
 <rect x="0" y="1250" width="1080" height="670" fill="#0e0e10"/><rect x="0" y="1240" width="1080" height="14" fill="#2a2a2e"/>
 <path d="M560,1290 C620,1180 760,1150 880,1190 C960,1215 1010,1260 1000,1300 C860,1320 700,1318 560,1290 Z" fill="#45454b"/>
 <path d="M640,1250 C700,1205 800,1195 880,1225" stroke="#77777d" stroke-width="5" fill="none" opacity=".6"/>
 <path d="M600,1100 C640,1150 700,1190 720,1240 L640,1260 C610,1210 590,1160 600,1100 Z" fill="#2a2a2e"/>
 <g transform="translate(${470-300*2.4} ${1300-380*2.4}) scale(2.4)">${S.woman}</g>
 <rect width="1080" height="1920" fill="#000" opacity=".08"/>
 ${paused?`<g opacity=".85"><rect x="470" y="560" width="44" height="150" rx="8" fill="#e9e6df"/><rect x="566" y="560" width="44" height="150" rx="8" fill="#e9e6df"/></g>
 <rect x="80" y="1130" width="920" height="10" rx="5" fill="#45454b"/><rect x="80" y="1130" width="${920*0.102}" height="10" rx="5" fill="#e9e6df"/><circle cx="${80+920*0.102}" cy="1135" r="18" fill="#e9e6df"/>
 <text x="80" y="1200" ${JP} font-size="38" fill="#e9e6df">12:04</text><text x="1000" y="1200" text-anchor="end" ${JP} font-size="38" fill="#9a988f">1:58:30</text>`:''}`}
function phone(inner,x,y,s,glow=0){return `<g transform="translate(${x} ${y}) scale(${s})">
 <circle cx="260" cy="520" r="760" fill="url(#glowW)" opacity="${0.18+glow}"/>
 <rect x="-30" y="-40" width="580" height="1120" rx="80" fill="#1d1d21"/><rect x="0" y="0" width="520" height="1040" rx="54" fill="${SCR}"/>
 <svg x="0" y="0" width="520" height="1040" viewBox="0 0 520 1040">${inner}</svg>
 <rect x="200" y="18" width="120" height="30" rx="15" fill="#0e0e10"/></g>`}
function finger(x,y,press=0){return `<g transform="translate(${x} ${y+press*14})"><path d="M-34,0 C-34,-40 34,-40 34,0 L44,520 L-60,520 Z" fill="${SK}"/>
 <path d="M-22,-14 C-22,-30 22,-30 22,-14 L20,30 C10,40 -10,40 -20,30 Z" fill="#e9e6df" opacity=".55"/><path d="M-30,150 C-10,160 10,160 30,150" stroke="${SKS}" stroke-width="4" fill="none"/>
 <path d="M44,200 C120,220 160,320 150,520 L30,520 Z" fill="${SKS}"/></g>`}
function platformBg(t){let s=`<rect width="1080" height="1920" fill="#09090b"/><rect x="0" y="0" width="1080" height="980" fill="#0c0c0f"/>
 ${bokeh(t,14,9,600,950)}
 ${[0,1,2].map(i=>`<rect x="${90+i*340}" y="140" width="220" height="16" rx="8" fill="#f4f2ee" opacity=".85"/><rect x="${90+i*340}" y="156" width="220" height="420" fill="url(#tube)" opacity=".22"/>`).join('')}
 <rect x="0" y="980" width="1080" height="940" fill="#1a1a1e"/>${tiles(980,.45)}
 <rect x="0" y="1010" width="1080" height="34" fill="#77777d" opacity=".55"/>${[...Array(27)].map((_,i)=>`<circle cx="${i*42+20}" cy="1027" r="6" fill="#45454b"/>`).join('')}
 <rect x="0" y="970" width="1080" height="12" fill="#e9e6df" opacity=".35"/>`;return s}
function board(){return `<g transform="translate(640 300)"><rect x="-10" y="-120" width="8" height="120" fill="#45454b"/><rect x="300" y="-120" width="8" height="120" fill="#45454b"/>
 <rect x="-40" y="0" width="380" height="150" rx="8" fill="#141418"/><text x="-14" y="60" ${JP} font-size="40" font-weight="700" fill="#e9e6df">普通</text>
 <text x="300" y="60" text-anchor="end" ${JP} font-size="46" font-weight="700" fill="#e9e6df">23:55</text><text x="-14" y="120" ${JP} font-size="30" fill="#9a988f">最終</text></g>`}
function bench(){return `<rect x="560" y="1180" width="420" height="34" rx="6" fill="#45454b"/><rect x="560" y="1080" width="420" height="80" rx="8" fill="#2a2a2e"/>
 <rect x="590" y="1214" width="20" height="160" fill="#2a2a2e"/><rect x="930" y="1214" width="20" height="160" fill="#2a2a2e"/>`}

// ---------- scenes (#004 サブスク)
const SCN = {
 teaser:(t,k)=>full(cam(filmFrame(t),1.08+0.1*ease(k),540,1000)+`<rect width="1080" height="1920" fill="#000" opacity="${lerp(.6,0,k*4)}"/>`),
 platform:(t,k)=>{const b=EV.buzz, d=t-b, sh=(d>0&&d<0.45)?Math.sin(d*90)*6:0, gl=(d>0)?Math.max(0,0.5-d*0.6):0;
   return full(cam(platformBg(t)+board()+bench()+man('back','0 0 400 1000',240,560,460,1150)+
   `<circle cx="${470+sh}" cy="1180" r="${120+gl*120}" fill="url(#glowW)" opacity="${gl}"/>`,1.0+0.06*ease(k),540,1100))},
 notify:(t,k)=>{const a=ease((t-EV.notify)/0.4);const scr=`<rect width="520" height="1040" fill="#2a2a2e"/>
   <text x="260" y="230" text-anchor="middle" ${JP} font-size="120" font-weight="300" fill="#e9e6df">23:48</text>
   <text x="260" y="285" text-anchor="middle" ${JP} font-size="26" fill="#9a988f">11月7日 土曜日</text>
   <g transform="translate(0 ${lerp(-180,0,a)})" opacity="${a}"><rect x="24" y="340" width="472" height="170" rx="30" fill="#e9e6df" opacity=".94"/>
   <rect x="48" y="366" width="56" height="56" rx="14" fill="#0e0e10"/><polygon points="68,380 68,408 90,394" fill="#e9e6df"/>
   <text x="120" y="388" ${JP} font-size="22" fill="#45454b">動画配信　今</text>
   <text x="48" y="452" ${JP} font-size="28" font-weight="700" fill="#0e0e10">お支払いが完了しました</text>
   <text x="48" y="490" ${JP} font-size="24" fill="#2a2a2e">月額プラン ¥990（税込）</text></g>`;
   return full(`<rect width="1080" height="1920" fill="#0b0b0d"/>`+cam(phone(scr,280,330,1.0,0.05),1.0+0.06*ease(k),540,900))},
 app:(t,k)=>{const scr=`<rect width="520" height="1040" fill="#141418"/><text x="36" y="110" ${JP} font-size="30" font-weight="700" fill="#e9e6df">ホーム</text>
   <text x="36" y="190" ${JP} font-size="26" fill="#e9e6df">続きから再生</text>
   <svg x="36" y="215" width="448" height="252" viewBox="0 280 1080 608" preserveAspectRatio="xMidYMid slice">${filmFrame(t,false)}</svg>
   <rect x="36" y="467" width="448" height="8" fill="#45454b"/><rect x="36" y="467" width="${448*0.102}" height="8" fill="#e9e6df"/>
   <text x="36" y="520" ${JP} font-size="24" fill="#e9e6df">12:04 / 1:58:30</text><text x="484" y="520" text-anchor="end" ${JP} font-size="22" fill="#77777d">最終視聴 7月14日</text>
   <text x="36" y="610" ${JP} font-size="26" fill="#e9e6df">マイリスト</text>
   ${[0,1,2].map(i=>`<rect x="${36+i*156}" y="635" width="136" height="200" rx="8" fill="#2a2a2e"/>`).join('')}
   ${[0,1,2].map(i=>`<rect x="${36+i*156}" y="860" width="136" height="200" rx="8" fill="#2a2a2e"/>`).join('')}`;
   return full(`<rect width="1080" height="1920" fill="#0b0b0d"/>`+cam(phone(scr,280,330,1.0),1.0+0.1*ease(k),540,650,0,40*ease(k)))},
 film:(t,k)=>full(cam(filmFrame(t),1.0+0.06*ease(k),540,1000)),
 settings:(t,k)=>{const step=Math.min(3,Math.floor(Math.max(0,t-EV.taps)/0.75)+ (t>=EV.taps?1:0));
   const rows=['アカウント','メンバーシップ','プランの変更','解約手続き','ヘルプ'];const hi=[ -1,0,1,3][step];
   const scr=`<rect width="520" height="1040" fill="#e9e6df"/><text x="36" y="110" ${JP} font-size="30" font-weight="700" fill="#0e0e10">設定</text>
   ${rows.map((r,i)=>`<rect x="0" y="${170+i*110}" width="520" height="110" fill="${i===hi?'#b4b2ac':'#e9e6df'}"/><text x="36" y="${235+i*110}" ${JP} font-size="30" fill="#0e0e10">${r}</text>
   <text x="480" y="${235+i*110}" text-anchor="end" ${JP} font-size="30" fill="#77777d">›</text><rect x="36" y="${279+i*110}" width="484" height="2" fill="#b4b2ac"/>`).join('')}`;
   const fy=[1500,840,950,1170][step], press=(step>0&&((t-EV.taps)%0.75)<0.18)?1:0;
   return full(`<rect width="1080" height="1920" fill="#0b0b0d"/>`+cam(phone(scr,280,330,1.0)+finger(700,fy,press),1.0+0.05*ease(k),540,900))},
 confirm:(t,k)=>{const bt=EV.back_tap, mv=ease((t-(bt-1.2))/1.0), pr=(t>bt&&t<bt+0.2)?1:0, gone=t>bt+0.25;
   const scr=`<rect width="520" height="1040" fill="#e9e6df"/><rect width="520" height="1040" fill="#0e0e10" opacity=".55"/>
   ${gone?'':`<rect x="30" y="300" width="460" height="470" rx="26" fill="#f4f2ee"/>
   <text x="260" y="380" text-anchor="middle" ${JP} font-size="30" font-weight="700" fill="#0e0e10">本当に解約しますか？</text>
   <text x="260" y="450" text-anchor="middle" ${JP} font-size="24" fill="#2a2a2e">解約すると、マイリストの</text>
   <text x="260" y="490" text-anchor="middle" ${JP} font-size="24" fill="#2a2a2e">37作品が削除されます。</text>
   <rect x="60" y="560" width="400" height="80" rx="12" fill="#45454b"/><text x="260" y="612" text-anchor="middle" ${JP} font-size="26" fill="#e9e6df">解約手続きを続ける</text>
   <rect x="60" y="660" width="400" height="80" rx="12" fill="${pr?'#77777d':'#0e0e10'}"/><text x="260" y="712" text-anchor="middle" ${JP} font-size="28" font-weight="700" fill="#e9e6df">戻る</text>`}`;
   return full(`<rect width="1080" height="1920" fill="#0b0b0d"/>`+cam(phone(scr,280,330,1.0)+finger(lerp(800,560,mv),lerp(1500,1050,mv),pr),1.0+0.06*ease(k),540,900))},
 face:(t,k)=>full(`<rect width="1080" height="1920" fill="#0d0d10"/>`+cam(man('blank','0 0 300 320',-40,250,1160,1240),1.0+0.08*ease(k),540,850)+
   `<rect x="0" y="1100" width="1080" height="820" fill="url(#upglow)" opacity=".5"/>`),
 side:(t,k)=>{const d=t-EV.train;let st='';for(let i=0;i<9;i++){const x=((d*2600+i*420)%3000)-900;st+=`<rect x="${x}" y="${380+hash(i)*900}" width="${300+hash(i*3)*500}" height="${10+hash(i*5)*26}" fill="#e9e6df" opacity="${0.12+0.2*hash(i*7)}" filter="url(#blur3)"/>`}
   const fl=0.08+0.06*Math.sin(d*30);
   return full(`<rect width="1080" height="1920" fill="#151519"/><rect width="1080" height="1920" fill="#e9e6df" opacity="${fl}"/>`+st+
     cam(man('side','100 20 250 380',-60,300,1200,1824),1.0+0.06*ease(k),540,800,-30*ease(k),0))},
 grid:(t,k)=>{let g='';for(let i=0;i<37;i++){const c=i%4,r=Math.floor(i/4);g+=`<rect x="${24+c*122}" y="${140+r*170}" width="108" height="156" rx="8" fill="#2a2a2e"/><rect x="${24+c*122}" y="${282+r*170}" width="108" height="6" fill="#45454b"/>`}
   const scr=`<rect width="520" height="1800" fill="#141418"/><text x="24" y="100" ${JP} font-size="30" font-weight="700" fill="#e9e6df">マイリスト　37</text>${g}`;
   return full(`<rect width="1080" height="1920" fill="#0b0b0d"/>`+cam(phone(`<g transform="translate(0 ${-lerp(0,520,ease(k))})">${scr}</g>`,280,330,1.0),1.0+0.06*ease(k),540,900))},
 distant:(t,k)=>full(`<rect width="1080" height="1920" fill="#0b0b0d"/>`+cam(man('distant','0 0 300 320',-40,250,1160,1240),1.04+0.08*ease(k),540,850)),
 bench:(t,k)=>full(cam(platformBg(t)+board()+bench()+man('back','0 0 400 1000',240,560,460,1150)+`<rect width="1080" height="1920" fill="#000" opacity=".2"/>`,1.08+0.05*ease(k),540,1100,0,-30*ease(k))),
 woman:(t,k)=>{const x=lerp(-420,1500,k);return full(`<rect width="1080" height="1920" fill="#0b0b0d"/>${bokeh(t,12,7,100,700)}<rect x="0" y="900" width="1080" height="1020" fill="#1a1a1e"/>${tiles(900,.5)}
   <rect x="0" y="1560" width="1080" height="34" fill="#77777d" opacity=".5"/>`+
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
