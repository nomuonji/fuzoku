"""#008 visual builder: late office, 4-minute macro run, next job arrives."""
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

function office(extra){return rect(0,0,1080,1920,"#0f0f13")+rect(0,0,1080,330,"#15151a")+'<g opacity=".6">'+[0,1,2,3,4,5].map(i=>rect(60+i*170,60,110,18,"#d8d5ce",3,'opacity=".18"')).join('')+'</g>'+rect(0,1450,1080,470,"#0b0b0d")+(extra||'')}
function monitor(inner,x,y,w,h){x=x||200;y=y||420;w=w||680;h=h||430;return rect(x-14,y-14,w+28,h+28,"#08080a",18,'stroke="#45454b" stroke-width="6"')+rect(x,y,w,h,"#ddd9d0",6)+inner+rect(x+w/2-60,y+h+14,120,70,"#25252a")+rect(x+w/2-170,y+h+84,340,18,"#2a2a2e",8)}
function sheet(x,y,done){let g='';for(let r=0;r<9;r++){g+=rect(x+20,y+80+r*34,640,2,"#aaa")}for(let c=0;c<5;c++)g+=rect(x+20+c*128,y+80,2,300,"#aaa");return g+txt(x+24,y+52,"月次 売上集計",28,"#111",'font-weight="700"')+(done?rect(x+330,y+170,300,90,"#f0eee9",10,'stroke="#111" stroke-width="3"')+txt(x+480,y+212,"完了",30,"#111",'text-anchor="middle" font-weight="700"')+txt(x+480,y+248,"所要時間 0:04",26,"#333",'text-anchor="middle"'):'')}
function glowdesk(){return glow(540,900,320)}
function desk(){return base(office(glowdesk()+monitor(sheet(200,420,true))+txt(540,1560,"19:58",40,"#777",'text-anchor="middle" letter-spacing="12"')+man("front","0 0 400 520",300,930,480,624)))}
function old(t,k){let a=Math.min(1,k*2.2);return base(office('')+txt(540,520,"月次の売上集計",44,"#e9e6df",'text-anchor="middle" font-weight="700"')+txt(120,760,"去年まで",32,"#8a8a90")+rect(120,790,840,64,"#25252a",6)+rect(120,790,840*a,64,"#9a978f",6)+txt(960,834,"2:40",36,"#e9e6df",'text-anchor="end" font-weight="700"')+txt(120,1000,"今",32,"#8a8a90")+rect(120,1030,840,64,"#25252a",6)+rect(120,1030,840*0.026,64,"#e9e6df",6)+txt(960,1074,"0:04",36,"#e9e6df",'text-anchor="end" font-weight="700"')+rect(340,1240,400,110,"#1b1b20",14,'stroke="#77777d" stroke-width="3"')+txt(540,1310,"マクロ（自分で作成）",30,"#cfcac0",'text-anchor="middle"'))}
function loosen(t,k){let z=1.35+0.1*k;return base(rect(0,0,1080,1920,"#0c0c0f")+glow(540,950,330)+cam(man("front","0 0 400 1000",240,300,600,1500),z,540,780,0,150))}
function chat(t,k){let on=k>.28;return base(office(glowdesk()+monitor(rect(220,440,640,390,"#f0eee9",0)+txt(250,490,"チャット",26,"#555")+(on?rect(250,520,500,200,"#fff",16,'stroke="#aaa" stroke-width="3"')+txt(274,568,"課長",24,"#555")+txt(274,616,"早いね。ついでに、",30,"#111",'font-weight="700"')+txt(274,660,"先月との比較表を、",30,"#111",'font-weight="700"')+txt(274,704,"明日の朝までに",30,"#111",'font-weight="700"'):'')+rect(250,760,360,44,"#e0ddd5",10)))+man("front","0 0 400 520",300,930,480,624))}
function table(t,k){let bars='';[120,160,140,210,190,240].forEach((v,i)=>bars+=rect(250+i*90,830-v,56,v,"#9a978f",4));return base(rect(0,0,1080,1920,"#0c0c0f")+rect(150,380,780,980,"#e9e6df",10)+txt(540,470,"先月との比較表",44,"#111",'text-anchor="middle" font-weight="700"')+bars+rect(220,840,640,4,"#555")+txt(540,1000,"毎月　作成",32,"#444",'text-anchor="middle"')+txt(540,1100,"閲覧　0人",40,"#111",'text-anchor="middle" font-weight="700"')+txt(540,1180,"読んだ人の記録はない",26,"#777",'text-anchor="middle"'))}
function reply(t,k){let h=Math.min(2,k*2.4),clk=(19+(59+h*60)/60);let mm=Math.floor(59+h*60),H=19+Math.floor(mm/60),M=mm%60;let tm=H+":"+(M<10?"0":"")+M;return base(office(glowdesk()+monitor(rect(220,440,640,390,"#f0eee9",0)+rect(420,560,400,90,"#111",16)+txt(620,620,"承知しました",34,"#fff",'text-anchor="middle" font-weight="700"')+rect(250,700,360,44,"#e0ddd5",10))+txt(540,1560,tm,40,"#777",'text-anchor="middle" letter-spacing="12"')+man("side","0 0 400 520",300,930,480,624)))}
function exit_(t,k){return base(rect(0,0,1080,1920,"#0c0c0f")+rect(180,300,720,1100,"#1b1b20",12)+rect(220,340,300,1020,"#25252a",8)+rect(560,340,300,1020,"#25252a",8)+txt(540,250,"22:02",52,"#d8d5ce",'text-anchor="middle" letter-spacing="14"')+rect(0,1400,1080,520,"#121216")+cam(man("back","0 0 400 1000",320,720,440,1000),1,540,1100))}
function firm(){return base(txt(540,520,"会社",52,"#e9e6df",'text-anchor="middle" font-weight="700"')+rect(220,600,640,150,"#1b1b20",14,'stroke="#77777d" stroke-width="3"')+txt(540,690,"一人が一日にこなせる量",34,"#d8d5ce",'text-anchor="middle"')+'<path d="M540 760 V880 M540 880 L340 960 M540 880 L740 960" stroke="#77777d" stroke-width="6" fill="none"/>'+rect(180,980,300,140,"#25252a",12)+txt(330,1065,"人数",40,"#e9e6df",'text-anchor="middle"')+rect(600,980,300,140,"#25252a",12)+txt(750,1065,"給料",40,"#e9e6df",'text-anchor="middle"'))}
function faster(t,k){let n=Math.min(1,k*1.6);return base(txt(540,470,"一日にこなせる量",40,"#e9e6df",'text-anchor="middle" font-weight="700"')+rect(200,700,300,300,"#45454b",6)+txt(350,1060,"前",30,"#aaa",'text-anchor="middle"')+rect(580,700-300*0.4*n,300,300+300*0.4*n,"#e9e6df",6)+txt(730,1060,"今",30,"#aaa",'text-anchor="middle"')+rect(200,1180,680,6,"#77777d")+txt(540,1300,"給料　同じ",44,"#d8d5ce",'text-anchor="middle" font-weight="700"'))}
function empty(t,k){let fill=Math.max(0,Math.min(1,(k-.35)*2));let s='';for(let i=0;i<10;i++){let on=i>=7&&fill>0&&(i-7)<fill*3+.01;s+=rect(100+i*88,780,76,200,i<7?"#45454b":(on?"#e9e6df":"#16161b"),6,i>=7?'stroke="#77777d" stroke-width="3" stroke-dasharray="10 8"':'')}return base(txt(540,540,"一日",44,"#e9e6df",'text-anchor="middle" font-weight="700"')+s+txt(580,1080,"空いた時間",32,"#cfcac0",'text-anchor="middle"')+(fill>.2?txt(540,1220,"次の仕事",44,"#e9e6df",'text-anchor="middle" font-weight="700"'):''))}
function unread(t,k){let d='';for(let i=0;i<5;i++)d+='<g transform="translate('+(250+i*8)+' '+(470+i*18)+') rotate('+(i-2)*1.5+')">'+rect(0,0,580,380,"#e9e6df",8,'opacity="'+(0.92-i*.05)+'"')+txt(290,200,"比較表",44,"#111",'text-anchor="middle" font-weight="700"')+'</g>';return base(d+txt(540,1180,"閲覧　0人",54,"#d8d5ce",'text-anchor="middle" font-weight="700"')+txt(540,1260,"来月も作る",32,"#8a8a90",'text-anchor="middle"'))}
function mine(){return base(office(glowdesk()+man("side","0 0 400 520",300,930,480,624))+rect(110,560,420,120,"#1b1b20",14,'stroke="#77777d" stroke-width="3"')+txt(320,610,"マクロを組んだ",30,"#cfcac0",'text-anchor="middle"')+txt(320,655,"俺",40,"#fff",'text-anchor="middle" font-weight="700"')+rect(550,700,420,120,"#1b1b20",14,'stroke="#77777d" stroke-width="3"')+txt(760,750,"仕事を引き受けた",30,"#cfcac0",'text-anchor="middle"')+txt(760,795,"俺",40,"#fff",'text-anchor="middle" font-weight="700"'))}
function punchline(){return base(rect(0,0,1080,1920,"#0c0c0f")+glow(560,1250,260)+cam(man("distant","0 0 300 320",-100,180,1280,1370),1.07,540,850))}
function outside(t,k){let w='';for(let i=0;i<9;i++)w+='<path d="M'+(100+i*120)+' '+(520+((i*97)%5)*70)+' h'+(140+(i%3)*30)+'" stroke="#d8d5ce" stroke-width="3" opacity=".12" stroke-linecap="round"/>';return base(rect(0,0,1080,1920,"#0b0b0d")+rect(0,200,1080,800,"#16161b")+rect(60,260,200,700,"#1d1d22")+rect(820,300,200,660,"#1d1d22")+w+rect(0,1300,1080,620,"#101014")+cam(man("back","0 0 400 1000",290,540,500,1100),1,540,1050))}
function teaser(t,k){return base(rect(0,0,1080,1920,"#0c0c0f")+'<g opacity=".85">'+cam(man("blank","0 0 300 320",-60,60,1200,1280),1,540,850)+'</g>'+glow(540,1200,300)+rect(160,1180,760,380,"#16161b",14,'opacity=".95"')+rect(190,1210,700,320,"#f0eee9",6)+txt(220,1262,"課長",24,"#555")+txt(220,1320,"早いね。ついでに、",34,"#111",'font-weight="700"')+txt(220,1372,"先月との比較表を、",34,"#111",'font-weight="700"')+txt(220,1424,"明日の朝までに",34,"#111",'font-weight="700"'))}
function street(){let b='';for(let i=0;i<5;i++)b+='<circle cx="'+(120+i*220)+'" cy="'+(420+(i%2)*140)+'" r="90" fill="#d8d5ce" opacity=".09" filter="url(#blur)"/>';let g='';for(let i=0;i<4;i++)g+=rect(160+i*210,1000,40,300,"#45454b",6)+rect(200+i*210,1080,120,30,"#2a2a2e",4);return base('<rect width="1080" height="1920" fill="url(#street)"/>'+b+txt(540,300,"改札",34,"#888",'text-anchor="middle" letter-spacing="14"')+g+'<path d="M0 1300 L1080 1300 V1920 H0Z" fill="#121216"/>'+cam(man("back","0 0 400 1000",270,560,520,1050),1,540,1050))}
function woman(t,k){let x=-620+(1560+620)*Math.max(0,Math.min(1,k));return base('<rect width="1080" height="1920" fill="#0a0a0c"/><rect x="0" y="1120" width="1080" height="800" fill="#202025"/><g transform="translate('+(x-360)+' 740) scale(1.3)">'+S.woman+'</g>')}
function eyes(t,k,start){let key=t<start+.15?"blank":t<start+.85?"glance":"resolve";return base('<svg x="120" y="800" width="840" height="330" viewBox="80 145 140 55" preserveAspectRatio="xMidYMid meet">'+S[key]+'</svg>')}
function flyer(){return base('<rect width="1080" height="1920" fill="#09090b"/><rect x="220" y="-120" width="640" height="2200" fill="#202025"/><g transform="translate(290 210) rotate(-3)"><image href="../../assets/flyers/flyer_a.png" width="440" height="620"/></g><g transform="translate(420 850) rotate(3)"><image href="../../assets/flyers/flyer_c.png" width="430" height="620"/></g><rect width="1080" height="1920" fill="#000" opacity=".22"/>')}
const SCN={teaser:teaser,desk:desk,old:old,loosen:loosen,chat:chat,table:table,reply:reply,exit:exit_,firm:firm,faster:faster,empty:empty,unread:unread,mine:mine,punchline:punchline,outside:outside,street:street,woman:woman,eyes:eyes,flyer:flyer,neon:function(){return base("")},black:function(){return base("")},cut:function(){return base("")}};
function render(t){
let sh=TL.shots.find(s=>t>=s[0]&&t<s[1])||TL.shots[TL.shots.length-1],k=(t-sh[0])/Math.max(.001,sh[1]-sh[0]);
let art=document.getElementById("art");art.innerHTML=SCN[sh[2]](t,k,sh[0]);
if(sh[2]==="black"||sh[2]==="neon"){
let final=sh[2]==="neon",d=t-sh[0],f=[1,0,1,1,0,0,1,0,1,1,1,1],on=d<.65?f[Math.floor(d/.05)%f.length]:1;
let tag=final?"くだらない世界　#008":"#008　時短の行き先";
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
