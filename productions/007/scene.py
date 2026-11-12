"""#007 visual builder: late train, phone usage report, quit-your-phone videos with ads, autoplay."""
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
function windows(){let w='';for(let i=0;i<3;i++)w+=rect(40+i*350,330,300,520,"#16161b",14)+'<rect x="'+(40+i*350)+'" y="330" width="300" height="520" fill="url(#window)" opacity=".35"/>';return w}
function straps(){let s='';for(let i=0;i<6;i++){let x=90+i*180;s+='<path d="M'+x+' 120 V250" stroke="#45454b" stroke-width="7"/><circle cx="'+x+'" cy="282" r="34" fill="none" stroke="#77777d" stroke-width="10"/>'}return rect(0,100,1080,18,"#2a2a2e")+s}
function car(){return rect(0,0,1080,1920,"#121216")+windows()+straps()+rect(0,860,1080,120,"#1d1d22")+rect(0,1500,1080,420,"#0d0d10")}
function glow(x,y,r){return '<circle cx="'+x+'" cy="'+y+'" r="'+r+'" fill="#e9e6df" opacity=".12" filter="url(#blur)"/>'}
function vid(x,y,w,h,label,sub){return rect(x,y,w,h,"#1b1b20",8)+txt(x+w/2,y+h/2+12,label,Math.round(w/14),"#d8d5ce",'text-anchor="middle" font-weight="700"')+(sub?txt(x+w/2,y+h/2+60,sub,Math.round(w/24),"#8a8a90",'text-anchor="middle"'):'')}
function bar(x,y,w,p,marks){let m='';(marks||[]).forEach(v=>m+=rect(x+w*v-4,y-6,8,20,"#e9e6df",2));return rect(x,y,w,8,"#77777d",4)+rect(x,y,w*p,8,"#e9e6df",4)+m}
function train(t,k){return base(car()+glow(600,1000,220)+cam(man("front","0 0 400 1000",240,430,600,1500),1.0,540,1000,0,0)+'<path d="M455 470 V280" stroke="#77777d" stroke-width="10"/>'+txt(540,1640,"23:32",28,"#777",'text-anchor="middle" letter-spacing="10"'))}
function notify(){return base(car()+'<g opacity=".5">'+cam(man("side","0 0 400 1000",380,420,500,1250),1,540,1000)+'</g>'+phone(rect(300,420,480,190,"#f0eee9",24)+txt(330,470,"使用時間",22,"#555")+txt(330,520,"先週より12%増加",30,"#111",'font-weight="700"')+txt(330,570,"1日平均 5時間48分",26,"#333"),260,380))}
function report(){let b='';let h=[150,210,190,260,240,300,330];h.forEach((v,i)=>b+=rect(345+i*58,1180-v,38,v,i==6?"#252529":"#9a978f",4));return base(phone(txt(540,470,"週間レポート",32,"#111",'text-anchor="middle" font-weight="700"')+txt(540,580,"1日平均",26,"#555",'text-anchor="middle"')+txt(540,690,"5時間48分",72,"#111",'text-anchor="middle" font-weight="700"')+txt(540,760,"先週より 12% 増加",28,"#333",'text-anchor="middle"')+b+rect(335,1180,420,4,"#555")))}
function preroll(t,k){let c=Math.max(1,5-Math.floor(k*5));return base(car()+phone(vid(282,460,516,300,"広告","")+rect(600,700,190,48,"#000",4,'opacity=".7"')+txt(695,733,"スキップまで "+c,20,"#eee",'text-anchor="middle"')+bar(282,770,516,0,[.5])+txt(300,850,"スマホをやめる方法",30,"#111",'font-weight="700"')+txt(300,895,"12:04",22,"#555")+rect(300,960,480,120,"#c8c5bd",10)+rect(300,1110,480,120,"#c8c5bd",10),260,280))}
function speed(t,k){return base(phone(vid(282,460,516,300,"やめる方法","")+bar(282,770,516,.15+k*.8,[.5])+txt(300,850,"スマホをやめる方法",30,"#111",'font-weight="700"')+rect(300,960,480,330,"#f0eee9",14,'stroke="#77777d" stroke-width="3"')+txt(330,1010,"再生速度",24,"#555")+["1.0","1.25","1.5","2.0"].map((v,i)=>txt(350,1065+i*58,v,28,v=="1.5"?"#111":"#777",v=="1.5"?'font-weight="700"':''))+rect(318,1132,10,10,"#111",5),260,280))}
function autoplay(t,k){return base(car()+phone(vid(282,460,516,300,"次の動画",'')+rect(282,460,516*Math.min(1,k*1.5),6,"#e9e6df")+txt(300,850,"寝る前のスマホをやめる、",28,"#111",'font-weight="700"')+txt(300,895,"たった一つの習慣",28,"#111",'font-weight="700"')+txt(300,950,"まもなく再生",22,"#555")+rect(300,1010,480,120,"#c8c5bd",10)+rect(300,1160,480,120,"#c8c5bd",10),260,280))}
function watching(){return base(rect(0,0,1080,1920,"#0e0e11")+glow(540,1150,300)+cam(man("blank","0 0 300 320",-40,240,1160,1240),1,540,850))}
function free(){return base(phone(txt(540,470,"動画アプリ",32,"#111",'text-anchor="middle" font-weight="700"')+txt(540,560,"無料",86,"#111",'text-anchor="middle" font-weight="700"')+vid(300,640,480,270,"広告","")+vid(300,960,480,270,"動画","")+rect(300,960,480,6,"#e9e6df"),260,280))}
function money(t,k){let s='';let n=Math.floor(k*9);for(let i=0;i<9;i++){s+=rect(140+i*90,600,70,110,i<n?"#45454b":"#25252a",6)+(i<n?txt(175+i*90,672,"広告",18,"#ddd",'text-anchor="middle"'):'')}
let c='';for(let i=0;i<Math.min(n,8);i++){c+='<circle cx="'+(300+(i%4)*40)+'" cy="'+(1110-Math.floor(i/4)*30)+'" r="26" fill="#d8d5ce" stroke="#77777d" stroke-width="4"/>';c+='<circle cx="'+(700+(i%4)*40)+'" cy="'+(1110-Math.floor(i/4)*30)+'" r="22" fill="#b4b2ac" stroke="#77777d" stroke-width="4"/>'}
return base(txt(540,480,"見た時間",34,"#c8c5bd",'text-anchor="middle"')+s+'<path d="M540 760 V880 M540 880 L360 960 M540 880 L720 960" stroke="#77777d" stroke-width="6" fill="none"/>'+c+txt(360,1240,"アプリ",34,"#e9e6df",'text-anchor="middle"')+txt(760,1240,"作った人",34,"#e9e6df",'text-anchor="middle"'))}
function feed(t,k){let y=-k*500,s='';for(let i=0;i<7;i++)s+=vid(300,440+i*300+y,480,250,"おすすめ","");return base(phone('<g clip-path="url(#ph)">'+s+'</g>',260,280).replace('<g clip-path="url(#ph)">','<defs><clipPath id="ph"><rect x="282" y="315" width="516" height="1092" rx="40"/></clipPath></defs><g clip-path="url(#ph)">'))}
function thumbs(){let a=["スマホをやめる方法","寝る前のスマホをやめる","スマホ時間を半分に","デジタルデトックス","やめられない人へ","スマホ断ち30日"],s='';a.forEach((v,i)=>{let x=80+(i%2)*470,y=330+Math.floor(i/2)*400;s+=rect(x,y,450,250,"#1b1b20",10)+txt(x+225,y+140,v,26,"#d8d5ce",'text-anchor="middle" font-weight="700"')+txt(x,y+300,(["128万","94万","210万","56万","73万","41万"][i])+"回視聴",24,"#8a8a90")});return base(s)}
function adloop(t,k){return base(car()+cam(man("side","0 0 400 1000",380,420,500,1250),1,540,1000)+'<g transform="translate(110 820) scale(.5) translate(-260 -280)">'+phone(vid(282,460,516,300,"広告","")+bar(282,770,516,.6,[.5,.8]),260,280)+'</g>')}
function punchline(){return base(rect(0,0,1080,1920,"#0c0c0f")+glow(560,1250,260)+cam(man("distant","0 0 300 320",-100,180,1280,1370),1.07,540,850))}
function platform(){let l='';for(let i=0;i<8;i++)l+=rect(0,1180+i*90,1080,4,"#2a2a2e");return base(rect(0,0,1080,1920,"#101014")+rect(0,300,1080,600,"#1b1b20")+windows()+l+rect(0,1150,1080,30,"#9a978f")+cam(man("back","0 0 400 1000",290,420,500,1250),1,540,1000))}
function finger(){return base(rect(0,0,1080,1920,"#0c0c0f")+rect(200,500,680,900,"#25252a",60)+glow(540,950,260)+'<path d="M330 1500 C340 1150 420 980 470 900 C500 860 560 870 560 930 L540 1150 C600 1080 680 1090 690 1150 L700 1500 Z" fill="#cfcac0"/><path d="M470 900 C500 860 560 870 560 930" stroke="#77777d" stroke-width="4" fill="none"/>'+rect(200,1400,680,520,"#45454b"))}
function street(){let b='';for(let i=0;i<5;i++)b+='<circle cx="'+(120+i*220)+'" cy="'+(420+(i%2)*140)+'" r="90" fill="#d8d5ce" opacity=".09" filter="url(#blur)"/>';let g='';for(let i=0;i<4;i++)g+=rect(160+i*210,1000,40,300,"#45454b",6)+rect(200+i*210,1080,120,30,"#2a2a2e",4);return base('<rect width="1080" height="1920" fill="url(#street)"/>'+b+txt(540,300,"改札",34,"#888",'text-anchor="middle" letter-spacing="14"')+g+'<path d="M0 1300 L1080 1300 V1920 H0Z" fill="#121216"/>'+cam(man("back","0 0 400 1000",270,560,520,1050),1,540,1050))}
function teaser(t,k){let c=Math.max(1,5-Math.floor(k*5));return base(rect(0,0,1080,1920,"#0c0c0f")+'<g opacity=".8">'+cam(man("blank","0 0 300 320",-60,60,1200,1280),1,540,850)+'</g>'+glow(540,1200,300)+'<g transform="translate(250 820) scale(.62) translate(-260 -280)">'+phone(vid(282,460,516,300,"広告","")+rect(600,700,190,48,"#000",4,'opacity=".7"')+txt(695,733,"スキップまで "+c,20,"#eee",'text-anchor="middle"')+txt(300,850,"スマホをやめる方法",30,"#111",'font-weight="700"'),260,280)+'</g>')}
function woman(t,k){let x=-620+(1560+620)*Math.max(0,Math.min(1,k));return base('<rect width="1080" height="1920" fill="#0a0a0c"/><rect x="0" y="1120" width="1080" height="800" fill="#202025"/><g transform="translate('+(x-360)+' 740) scale(1.3)">'+S.woman+'</g>')}
function eyes(t,k,start){let key=t<start+.15?"blank":t<start+.85?"glance":"resolve";return base('<svg x="120" y="800" width="840" height="330" viewBox="80 145 140 55" preserveAspectRatio="xMidYMid meet">'+S[key]+'</svg>')}
function flyer(){return base('<rect width="1080" height="1920" fill="#09090b"/><rect x="220" y="-120" width="640" height="2200" fill="#202025"/><g transform="translate(290 210) rotate(-3)"><image href="../../assets/flyers/flyer_a.png" width="440" height="620"/></g><g transform="translate(420 850) rotate(3)"><image href="../../assets/flyers/flyer_c.png" width="430" height="620"/></g><rect width="1080" height="1920" fill="#000" opacity=".22"/>')}
const SCN={teaser:teaser,train:train,notify:notify,report:report,preroll:preroll,speed:speed,autoplay:autoplay,watching:watching,free:free,money:money,feed:feed,thumbs:thumbs,adloop:adloop,punchline:punchline,platform:platform,finger:finger,street:street,woman:woman,eyes:eyes,flyer:flyer,neon:function(){return base("")},black:function(){return base("")}};
function render(t){
let sh=TL.shots.find(s=>t>=s[0]&&t<s[1])||TL.shots[TL.shots.length-1],k=(t-sh[0])/Math.max(.001,sh[1]-sh[0]);
let art=document.getElementById("art");art.innerHTML=SCN[sh[2]](t,k,sh[0]);
if(sh[2]==="black"||sh[2]==="neon"){
let final=sh[2]==="neon",d=t-sh[0],f=[1,0,1,1,0,0,1,0,1,1,1,1],on=d<.65?f[Math.floor(d/.05)%f.length]:1;
let tag=final?"くだらない世界　#007":"#007　やめ方の動画";
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
