"""#010 visual builder: Sunday afternoon at a discount pile of the narrator's own company's fans."""
import json, pathlib, re
D=pathlib.Path(__file__).resolve().parent
A=D.parent.parent/"assets"/"character"
def inner(name):
    s=(A/name).read_text(encoding="utf-8")
    return re.sub(r"^<svg[^>]*>|</svg>$","",s.strip(),flags=re.S)
S={k:inner(v) for k,v in {
 "front":"man/front.svg","side":"man/side.svg","back":"man/back.svg",
 "blank":"man/face_blank.svg","distant":"man/face_distant.svg",
 "glance":"man/face_glance.svg","resolve":"man/face_resolve.svg",
 "woman":"woman_pass.svg"}.items()}
TL=json.loads((D/"timeline.json").read_text(encoding="utf-8"))
HTML=r"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#050506}#stage{position:relative;width:1080px;height:1920px;overflow:hidden;background:#0c0c0f;font-family:"Noto Serif CJK JP",serif}
#art{position:absolute;inset:0;width:1080px;height:1920px}
#subbg{position:absolute;left:0;right:0;bottom:90px;height:580px;background:linear-gradient(transparent,rgba(0,0,0,.8) 25%,rgba(0,0,0,.8) 78%,transparent);opacity:0}
#sub{position:absolute;left:45px;right:45px;bottom:175px;text-align:center;white-space:pre-line;color:#f0eee9;font-size:50px;line-height:1.48;letter-spacing:.04em;text-shadow:0 2px 12px #000}
#fade{position:absolute;inset:0;background:#000;opacity:0}
.neon{font-weight:800;letter-spacing:.08em;color:#ffe5f0;-webkit-text-stroke:3px #ff2e88;text-shadow:0 0 7px #ff7ab4,0 0 22px #ff2e88,0 0 55px #ff2e88}
</style></head><body><div id="stage"><svg id="art" viewBox="0 0 1080 1920"></svg><div id="subbg"></div><div id="sub"></div><div id="fade"></div></div>
<script>
const S=__SVGS__,TL=__TL__;
const JP='font-family="Noto Serif CJK JP,serif"';
function rect(x,y,w,h,c,r,extra){return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="'+(r||0)+'" fill="'+(c||"#252529")+'" '+(extra||'')+'/>'}
function txt(x,y,s,size,fill,extra){return '<text x="'+x+'" y="'+y+'" '+JP+' font-size="'+(size||30)+'" fill="'+(fill||"#e9e6df")+'" '+(extra||'')+'>'+s+'</text>'}
function man(k,vb,x,y,w,h){return '<svg x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" viewBox="'+vb+'" preserveAspectRatio="xMidYMid meet">'+S[k]+'</svg>'}
function cam(s,z,cx,cy,dx,dy){return '<g transform="translate('+(540+(dx||0))+' '+(950+(dy||0))+') scale('+(z||1)+') translate('+(-(cx||540))+' '+(-(cy||950))+')">'+s+'</g>'}
function base(s){return '<svg viewBox="0 0 1080 1920" width="1080" height="1920"><defs><linearGradient id="window" x2="0" y2="1"><stop stop-color="#d8d5ce" stop-opacity=".28"/><stop offset="1" stop-color="#d8d5ce" stop-opacity="0"/></linearGradient><linearGradient id="street" x2="0" y2="1"><stop stop-color="#45454b"/><stop offset="1" stop-color="#0b0b0d"/></linearGradient><filter id="blur"><feGaussianBlur stdDeviation="24"/></filter></defs><rect width="1080" height="1920" fill="#0b0b0d"/>'+s+'</svg>'}
function phone(screen,x,y){x=x||260;y=y||280;return rect(x,y,560,1160,"#08080a",70,'stroke="#77777d" stroke-width="12"')+rect(x+22,y+35,516,1092,"#ddd9d0",40)+rect(x+220,y+14,120,12,"#77777d",6)+screen}

function glow(x,y,r){return '<circle cx="'+x+'" cy="'+y+'" r="'+r+'" fill="#e9e6df" opacity=".12" filter="url(#blur)"/>'}
function fbox(x,y,w,h,r){let cx=w/2,cy=h*0.38,rr=h*0.2;return '<g transform="translate('+x+' '+y+') rotate('+(r||0)+' '+(w/2)+' '+(h/2)+')">'+rect(0,0,w,h,"#d8d5ce",6,'stroke="#77777d" stroke-width="3"')+rect(0,h*0.74,w,h*0.26,"#45454b",0)+[0,1,2,3,4].map(i=>'<ellipse cx="'+cx+'" cy="'+(cy-rr*.55)+'" rx="'+(rr*.28)+'" ry="'+(rr*.55)+'" fill="#45454b" transform="rotate('+(i*72+20)+' '+cx+' '+cy+')"/>').join('')+'<circle cx="'+cx+'" cy="'+cy+'" r="'+(rr*.14)+'" fill="#d8d5ce"/></g>'}
function pile(cx,y,bw,bh,rows,from){let g='',n=0;for(let r=0;r<rows;r++){let cnt=rows-r;for(let i=0;i<cnt;i++){let x=cx-cnt*bw/2+i*bw+((r*7+i*5)%3-1)*3,yy=y-(r+1)*bh;if(n++<(from===undefined?99:from))g+=fbox(x,yy,bw-6,bh-4,((r*3+i*2)%5-2)*1.2)}}return g}
function tagcard(x,y,w,h,s,size,dark){return rect(x,y,w,h,dark?"#16161b":"#f4f2ec",10,'stroke="#9a978f" stroke-width="3"')+txt(x+w/2,y+h/2+size*0.35,s,size,dark?"#e9e6df":"#111",'text-anchor="middle" font-weight="800"')}
function shelves(){let g='';for(let i=0;i<2;i++){let x=i?830:0;g+=rect(x,320,250,860,"#16161b",0)+[0,1,2,3].map(j=>rect(x+(i?0:0),420+j*200,250,16,"#2a2a2e")+rect(x+20,340+j*200,60,80,"#202025")+rect(x+110,360+j*200,80,60,"#1d1d22")).join('')}return g}
function lights(){let g='';for(let i=0;i<4;i++)g+=rect(120+i*230,150,160,16,"#e9e6df",6,'opacity=".28"')+rect(60+i*230,150,280,320,"#e9e6df",0,'opacity=".02"');return g}
function teaser(t,k){return base(rect(0,0,1080,1920,"#0a0a0d")+'<g opacity=".9">'+cam(man("blank","0 0 300 320",-60,60,1200,1280),1,540,850)+'</g>'+glow(540,1330,380)+'<g opacity=".6">'+pile(540,1330,170,120,3)+'</g>'+'<g transform="translate(700 1040) rotate(-6)">'+tagcard(0,0,240,110,"¥398",70)+'</g>')}
function aisle(t,k){return base(rect(0,0,1080,1920,"#0b0b0e")+lights()+shelves()+rect(0,1180,1080,740,"#101014")+rect(0,1170,1080,14,"#202025")+glow(640,800,360)+'<rect x="440" y="860" width="520" height="300" rx="10" fill="#1b1b20" stroke="#77777d" stroke-width="6"/>'+pile(700,1140,150,100,3)+cam(man("back","0 0 400 1000",20,340,380,960),1,540,900)+txt(540,250,"日曜　16:40",44,"#8a8a90",'text-anchor="middle" letter-spacing="10"'))}
function pileview(sign,k2){return rect(0,0,1080,1920,"#0b0b0e")+glow(540,760,420)+rect(0,1100,1080,820,"#101014")+'<rect x="180" y="640" width="720" height="470" rx="12" fill="#17171c" stroke="#77777d" stroke-width="6"/>'+pile(540,1100,200,125,4)+(sign?'<path d="M540 500 V640" stroke="#77777d" stroke-width="8"/>'+tagcard(300,330,480,170,"在庫一掃",110):'')}
function pile_(t,k){return base(pileview(k>.15,k))}
function tag(t,k){let strike=Math.min(1,Math.max(0,(k-.2)*3)),show=k>.5;return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,700,380)+txt(540,330,"去年の夏",44,"#8a8a90",'text-anchor="middle" letter-spacing="10"')+'<g transform="translate(540 600) rotate(-4)">'+tagcard(-320,-110,640,220,"¥2,980",130)+'<path d="M-300 0 H'+(-300+600*strike)+'" stroke="#111" stroke-width="12"/></g>'+(show?'<g transform="translate(540 960) rotate(3) scale(1.1)">'+tagcard(-260,-120,520,240,"¥398",160)+'</g>':''))}
function nov(t,k){let n=Math.min(3,Math.floor(k*4));return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,900,400)+rect(340,230,400,230,"#e9e6df",16)+rect(340,230,400,60,"#45454b",16)+txt(540,410,"11月",120,"#111",'text-anchor="middle" font-weight="800"')+'<path d="M300 720 H780 L740 1100 H340 Z" fill="#16161b" stroke="#9a978f" stroke-width="8"/><path d="M360 720 C380 600 700 600 720 720" fill="none" stroke="#9a978f" stroke-width="10"/>'+[0,1,2].map(i=>i<n?fbox(350+i*125,930-(i%2)*40,110,150,i*6-6):'').join('')+rect(300,720,480,10,"#9a978f"))}
function sheet(t,k){let rows='',h=Math.floor(k*9);for(let i=0;i<11;i++){let y=380+i*76,on=i===h;rows+=rect(120,y,840,66,on?"#e9e6df":"#16161b",6)+txt(160,y+46,"11/"+(i+1)+"　納品",32,on?"#111":"#8a8a90")+txt(920,y+46,(3180000+i*271000).toLocaleString(),34,on?"#111":"#cfcac0",'text-anchor="end" font-weight="700"')}return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,760,420)+txt(540,300,"売上集計",54,"#e9e6df",'text-anchor="middle" font-weight="700" letter-spacing="10"')+rows)}
function day(t,k){let ok=Math.min(1,k*2.2);return base(rect(0,0,1080,1920,"#0b0b0e")+txt(540,300,"店に納めた日",56,"#e9e6df",'text-anchor="middle" font-weight="700"')+rect(120,360,300,220,"#1b1b20",14,'stroke="#9a978f" stroke-width="4"')+txt(270,490,"会社",64,"#e9e6df",'text-anchor="middle"')+'<path d="M440 470 H640" stroke="#e9e6df" stroke-width="10"/><path d="M610 435 L650 470 L610 505" stroke="#e9e6df" stroke-width="10" fill="none"/>'+rect(660,360,300,220,"#1b1b20",14,'stroke="#9a978f" stroke-width="4"')+txt(810,490,"店",72,"#e9e6df",'text-anchor="middle"')+rect(300,610,480,110,"#e9e6df",14,'opacity="'+ok+'"')+txt(540,688,"売上　立つ",56,"#111",'text-anchor="middle" font-weight="800" opacity="'+ok+'"')+'<g opacity=".45">'+txt(540,880,"客が買った日",56,"#8a8a90",'text-anchor="middle"')+rect(660,930,300,200,"#16161b",14,'stroke="#45454b" stroke-width="4"')+txt(810,1050,"客",64,"#8a8a90",'text-anchor="middle"')+'<path d="M180 1030 H640" stroke="#45454b" stroke-width="8" stroke-dasharray="14 14"/></g>')}
function chain(t,k){let L=["売れ残り","札を貼り替える","安く売り切る","店がまた注文"],n=Math.min(4,Math.floor(k*5)+1),g='';for(let i=0;i<4;i++){let y=290+i*220;if(i<n){g+=rect(160,y,760,130,i===3?"#e9e6df":"#1b1b20",16,'stroke="#9a978f" stroke-width="4"')+txt(540,y+88,L[i],60,i===3?"#111":"#e9e6df",'text-anchor="middle" font-weight="700"');if(i<3&&i<n-1)g+='<path d="M540 '+(y+140)+' V'+(y+205)+'" stroke="#9a978f" stroke-width="8"/><path d="M515 '+(y+185)+' L540 '+(y+212)+' L565 '+(y+185)+'" stroke="#9a978f" stroke-width="8" fill="none"/>'}}return base(rect(0,0,1080,1920,"#0b0b0e")+g)}
function closet(t,k){let slide=Math.min(1,k*1.6),stamp=k>.6;return base(rect(0,0,1080,1920,"#0b0b0e")+txt(540,300,"来年の夏まで",64,"#e9e6df",'text-anchor="middle" font-weight="700" letter-spacing="8"')+rect(160,380,760,780,"#101014",6,'stroke="#45454b" stroke-width="8"')+rect(160,770,760,12,"#45454b")+pile(540,1150,200,150,2)+pile(540,770,170,120,2)+rect(160,380,380+380*0,780,"#1b1b20",4,'opacity="'+(0.2+0.8*slide)+'" transform="translate('+(380*(1-slide))+' 0) scale(1 1)" ')+rect(540,380,380,780,"#202025",4,'opacity="'+(0.2+0.8*slide)+'"')+(stamp?rect(300,1020,480,110,"#e9e6df",14)+txt(540,1100,"売上　済",64,"#111",'text-anchor="middle" font-weight="800"'):''))}
function pay(t,k){let r='',h=Math.min(1,k*2);for(let i=0;i<5;i++)r+=rect(60,150+i*100,420,22,"#aaa",4)+rect(560,150+i*100,i===0?200:130+i*10,22,"#555",4);return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,760,420)+'<g transform="translate(140 300)">'+rect(0,0,800,900,"#e9e6df",20)+txt(60,100,"給与明細",58,"#111",'font-weight="800"')+r+rect(60,700,680,100,"#111",12)+txt(120,770,"支給額",44,"#fff")+rect(440,730,250,40,"#e9e6df",6,'opacity="'+(0.2+0.8*h)+'"')+'</g>')}
function punchline(){return base(rect(0,0,1080,1920,"#0c0c0f")+glow(560,1250,260)+cam(man("distant","0 0 300 320",-100,180,1280,1370),1.07,540,850))}
function fix(t,k){let tw=Math.min(1,k*2),lift=Math.max(0,Math.min(1,(k-.5)*2));return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,760,380)+rect(0,1100,1080,820,"#101014")+pile(540,1100,200,125,3)+'<g transform="translate(540 560) scale('+(0.15+0.85*tw)+' 1)">'+tagcard(-200,-70,400,140,"¥398",90)+'</g>'+'<path d="M300 1180 H780 L740 1350 H340 Z" fill="#16161b" stroke="#9a978f" stroke-width="6" opacity="'+lift+'"/>'+(lift>0?fbox(450,1000+lift*220,120,150,0):''))}
function home(t,k){let ghost=Math.min(1,k*2);return base(rect(0,0,1080,1920,"#09090b")+glow(540,700,300)+rect(180,620,720,16,"#45454b")+fbox(230,470,170,150,0)+fbox(420,470,170,150,0)+'<rect x="610" y="470" width="170" height="150" fill="none" stroke="#9a978f" stroke-width="5" stroke-dasharray="14 10" opacity="'+ghost+'"/>'+txt(540,820,"家",64,"#8a8a90",'text-anchor="middle" letter-spacing="10"')+txt(540,940,"2台",140,"#e9e6df",'text-anchor="middle" font-weight="800"'))}
function queue(t,k){let z=1+k*.08;return base(rect(0,0,1080,1920,"#0b0b0e")+cam(rect(0,0,1080,1920,"#0b0b0e")+rect(0,1000,1080,920,"#121216")+rect(60,980,960,40,"#2a2a2e")+glow(540,760,360)+rect(700,470,260,330,"#e9e6df",12)+txt(830,560,"お一人様",40,"#111",'text-anchor="middle" font-weight="800"')+txt(830,630,"三点まで",52,"#111",'text-anchor="middle" font-weight="800"')+'<path d="M180 840 H620 L580 1020 H220 Z" fill="#16161b" stroke="#9a978f" stroke-width="7"/><path d="M230 840 C250 760 550 760 570 840" fill="none" stroke="#9a978f" stroke-width="9"/>'+fbox(330,720,150,170,-6),z,540,900))}
function scent(t,k){let c='';for(let i=0;i<3;i++){let ph=(k*1.2+i*.33)%1;c+='<path d="M'+(380+i*150)+' '+(760-ph*260)+' c-40 -50 40 -90 0 -140 c-40 -50 40 -90 0 -140" fill="none" stroke="#e9e6df" stroke-width="7" stroke-linecap="round" opacity="'+(0.55*(1-ph))+'"/>'}return base('<rect width="1080" height="1920" fill="#0a0a0c"/><rect x="0" y="1120" width="1080" height="800" fill="#202025"/><g transform="translate(180 740) scale(1.3)">'+S.woman+'</g>'+c)}
function lot(){let g='';for(let i=0;i<4;i++)g+=rect(60+i*270,1010,200,110,"#1d1d22",30)+rect(100+i*270,950,120,70,"#16161b",16);return base('<rect width="1080" height="1920" fill="url(#street)"/>'+rect(0,380,1080,360,"#202025")+rect(60,420,960,260,"#e9e6df",8,'opacity=".14"')+glow(540,560,300)+g+'<path d="M0 1300 L1080 1300 V1920 H0Z" fill="#121216"/>'+[0,1,2,3].map(i=>rect(70+i*270,1360,140,10,"#45454b",3)).join('')+cam(man("back","0 0 400 1000",270,560,520,1050),1,540,1050))}
function woman(t,k){let x=-620+(1560+620)*Math.max(0,Math.min(1,k));return base('<rect width="1080" height="1920" fill="#0a0a0c"/><rect x="0" y="1120" width="1080" height="800" fill="#202025"/><g transform="translate('+(x-360)+' 740) scale(1.3)">'+S.woman+'</g>')}
function eyes(t,k,start){let key=t<start+.15?"blank":t<start+.85?"glance":"resolve";return base('<svg x="120" y="800" width="840" height="330" viewBox="80 145 140 55" preserveAspectRatio="xMidYMid meet">'+S[key]+'</svg>')}
function flyer(){return base('<rect width="1080" height="1920" fill="#09090b"/><rect x="220" y="-120" width="640" height="2200" fill="#202025"/><g transform="translate(290 210) rotate(-3)"><image href="../../assets/flyers/flyer_a.png" width="440" height="620"/></g><g transform="translate(420 850) rotate(3)"><image href="../../assets/flyers/flyer_c.png" width="430" height="620"/></g><rect width="1080" height="1920" fill="#000" opacity=".22"/>')}
const SCN={teaser:teaser,aisle:aisle,pile:pile_,tag:tag,nov:nov,sheet:sheet,day:day,chain:chain,closet:closet,pay:pay,punchline:punchline,fix:fix,home:home,queue:queue,scent:scent,lot:lot,woman:woman,eyes:eyes,flyer:flyer,neon:function(){return base("")},black:function(){return base("")},cut:function(){return base("")}};
function render(t){
let sh=TL.shots.find(s=>t>=s[0]&&t<s[1])||TL.shots[TL.shots.length-1],k=(t-sh[0])/Math.max(.001,sh[1]-sh[0]);
let art=document.getElementById("art");art.innerHTML=SCN[sh[2]](t,k,sh[0]);
if(sh[2]==="black"||sh[2]==="neon"){
let final=sh[2]==="neon",d=t-sh[0],f=[1,0,1,1,0,0,1,0,1,1,1,1],on=d<.65?f[Math.floor(d/.05)%f.length]:1;
let tag=final?"くだらない世界　#010":"#010　量販店の在庫一掃";
art.innerHTML+='<foreignObject x="0" y="'+(final?330:500)+'" width="1080" height="1400"><div xmlns="http://www.w3.org/1999/xhtml" style="text-align:center;opacity:'+on+'"><div class="neon" style="font-size:'+(final?145:104)+'px;writing-mode:vertical-rl;text-align:start;display:inline-block;height:'+(final?1010:760)+'px">そうだ、<br>風俗行こう。</div><div style="color:#ddd;font-size:34px;letter-spacing:12px;margin-top:28px">'+tag+'</div></div></foreignObject>';
}
let sub=TL.subs.find(s=>t>=s[0]&&t<s[1]);
document.getElementById("sub").textContent=sub?sub[2]:"";
document.getElementById("subbg").style.opacity=sub?"1":"0";
document.getElementById("sub").style.fontSize=t<TL.teaser_end?"62px":"50px";
document.getElementById("fade").style.opacity=t>TL.total-.55?(t-(TL.total-.55))/.55:0;
}
window.render=render;
</script></body></html>"""
html=HTML.replace("__SVGS__",json.dumps(S,ensure_ascii=False)).replace("__TL__",json.dumps(TL,ensure_ascii=False))
(D/"ep.html").write_text(html,encoding="utf-8")
print("scene html written",len(html))
