"""#009 visual builder: Saturday night in bed, scrolling a shopping app, nothing wanted."""
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


function room(extra){return rect(0,0,1080,1920,"#0b0b0e")+rect(0,1180,1080,740,"#121216")+rect(0,1160,1080,30,"#1b1b20")+(extra||'')}
function cardsvg(x,y,w,h,inner){return '<svg x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" viewBox="0 0 '+w+' '+h+'">'+inner+'</svg>'}
function prod(y,name,price,tone){return rect(16,y,484,200,"#f4f2ec",14,'stroke="#c9c5bb" stroke-width="2"')+rect(34,y+18,164,164,tone||"#cfcac0",10)+txt(218,y+86,name,38,"#222",'font-weight="700"')+txt(218,y+140,price,34,"#555")}
const PRODS=[["腕時計","¥3,480","#bdb9ae"],["加湿器","¥2,980","#d4d0c6"],["ケーブルバンド","¥980","#b8b4a9"],["マグカップ","¥1,280","#cfcac0"],["ブランケット","¥2,480","#c4c0b5"],["イヤホンケース","¥1,580","#bdb9ae"],["時計スタンド","¥1,980","#d4d0c6"],["収納ボックス","¥1,780","#c4c0b5"]];
function scrollList(off){let g=txt(24,48,"あなたへのおすすめ",34,"#222",'font-weight="700"');PRODS.concat(PRODS).forEach((p,i)=>{g+=prod(80+i*224-off,p[0],p[1],p[2])});return g}
function teaser(t,k){return base(rect(0,0,1080,1920,"#0a0a0d")+'<g opacity=".9">'+cam(man("blank","0 0 300 320",-60,60,1200,1280),1,540,850)+'</g>'+glow(540,1330,380)+rect(300,1330,480,300,"#e9e6df",24,'opacity=".16"')+rect(340,1370,400,34,"#f4f2ec",8,'opacity=".5"')+rect(340,1430,400,34,"#f4f2ec",8,'opacity=".35"')+rect(340,1490,400,34,"#f4f2ec",8,'opacity=".22"'))}
function bed(t,k){return base(room(glow(540,1000,380)+cam(man("front","0 0 400 520",300,640,480,624)+rect(420,1010,240,160,"#f4f2ec",14,'opacity=".92"')+rect(440,1030,200,24,"#cfcac0",6)+rect(440,1070,200,24,"#cfcac0",6,'opacity=".7"'),1.5,540,1000,0,-120)+txt(540,260,"土曜　22:12",44,"#8a8a90",'text-anchor="middle" letter-spacing="10"')))}
function scroll(t,k){let off=k*620;return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,900,420)+phone(cardsvg(282,315,516,1092,scrollList(off))))}
function items(t,k){let a=0;return base(txt(540,330,"おすすめ",44,"#8a8a90",'text-anchor="middle" letter-spacing="14"')+PRODS.slice(0,3).map((p,i)=>'<g transform="translate(150 '+(360+i*290)+') scale(1.56)">'+cardsvg(0,0,500,200,prod(0,p[0],p[1],p[2]))+'</g>').join(''))}
function wish(t,k){let n=Math.min(11,Math.floor(2+k*11)),g=txt(24,48,"欲しい物リスト　11件",34,"#222",'font-weight="700"');for(let i=0;i<11;i++){let y=80+i*92;g+=rect(16,y,484,80,i<n?"#f4f2ec":"#e4e1d9",10)+rect(30,y+12,56,56,i<n?"#bdb9ae":"#d4d0c6",6)+rect(104,y+22,i<n?250:0,14,"#555",4)+rect(104,y+48,i<n?160:0,12,"#aaa",4)+txt(484,y+62,"2025/"+(i%5+7),22,"#888",'text-anchor="end"')}return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,900,420)+phone(cardsvg(282,315,516,1092,g)))}
function cart(t,k){let c=Math.floor(k*6),count=c%2===0?1:0,tap=(k*6)%1<.35;return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,900,400)+phone(cardsvg(282,315,516,1092,txt(24,60,"カート　"+count+"点",42,"#222",'font-weight="700"')+(count?prod(100,"ケーブルバンド","¥980","#b8b4a9"):txt(258,300,"カートは空です",36,"#888",'text-anchor="middle"'))+rect(40,720,436,110,tap?"#222":"#555",18)+txt(258,790,count?"削除":"カートに入れる",38,"#fff",'text-anchor="middle" font-weight="700"')+txt(258,930,c>=5?"3回目":(c>=3?"2回目":"1回目"),30,"#999",'text-anchor="middle"'))))}
function order(t,k){let late=k>.5;let cables='';if(late){cables='<path d="M260 1000 C340 920 420 1080 500 1000" stroke="#9a978f" stroke-width="9" fill="none"/><path d="M580 1000 C660 920 740 1080 820 1000" stroke="#9a978f" stroke-width="9" fill="none"/>'+txt(540,1130,"家のケーブル　2本",40,"#d8d5ce",'text-anchor="middle"')}return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,760,420)+txt(540,230,"23:15",56,"#8a8a90",'text-anchor="middle" letter-spacing="12"')+(late?'':phone(cardsvg(282,315,516,1092,txt(24,60,"ご注文の確定",42,"#222",'font-weight="700"')+prod(100,"ケーブルバンド","¥980","#b8b4a9")+rect(40,720,436,120,"#222",18)+txt(258,796,"注文を確定する",38,"#fff",'text-anchor="middle" font-weight="700"'))))+(late?'<g transform="translate(240 300) scale(1.2)">'+cardsvg(0,0,516,300,prod(0,"ケーブルバンド","¥980","#b8b4a9")+rect(16,230,484,60,"#2a2a2e",12)+txt(258,272,"注文完了",32,"#e9e6df",'text-anchor="middle" font-weight="700"'))+'</g>':'')+cables)}
function reco(t,k){let a=Math.min(1,k*2);return base(txt(540,330,"俺が前に見た物",40,"#cfcac0",'text-anchor="middle"')+[0,1,2].map(i=>rect(150+i*270,380,230,200,"#45454b",10)).join('')+'<path d="M540 620 V800" stroke="#9a978f" stroke-width="8"/><path d="M510 770 L540 810 L570 770" stroke="#9a978f" stroke-width="8" fill="none"/>'+txt(540,900,"次に売れそうな物",40,"#cfcac0",'text-anchor="middle"')+[0,1,2].map(i=>rect(150+i*270,950,230,200,"#e9e6df",10,'opacity="'+(0.35+0.65*a)+'"')).join('')+txt(540,1250,"おすすめ",48,"#e9e6df",'text-anchor="middle" font-weight="700" opacity="'+a+'"'))}
function seen(t,k){let ring=Math.min(1,k*2.2);return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,900,420)+'<g transform="translate(160 520) scale(1.5)">'+cardsvg(0,0,500,200,prod(0,"ケーブルバンド","¥980","#b8b4a9"))+'</g><rect x="150" y="510" width="780" height="330" rx="26" fill="none" stroke="#e9e6df" stroke-width="6" stroke-dasharray="'+(2200*ring)+' 2200"/>'+txt(540,1040,"これだ",64,"#e9e6df",'text-anchor="middle" font-weight="700" opacity="'+Math.min(1,Math.max(0,(k-.45)*3))+'"'))}
function both(t,k){let show=k>.5;return base(rect(110,520,380,360,"#1b1b20",16,'stroke="#77777d" stroke-width="3"')+txt(300,640,"俺",52,"#e9e6df",'text-anchor="middle" font-weight="700"')+txt(300,740,"何も",38,"#cfcac0",'text-anchor="middle"')+txt(300,800,"買えない",44,"#fff",'text-anchor="middle" font-weight="700"')+rect(590,520,380,360,"#1b1b20",16,'stroke="#77777d" stroke-width="3"')+txt(780,640,"店",52,"#e9e6df",'text-anchor="middle" font-weight="700"')+txt(780,740,"何も",38,"#cfcac0",'text-anchor="middle"')+txt(780,800,"売れない",44,"#fff",'text-anchor="middle" font-weight="700"')+rect(300,940,480,220,"#16161b",16,'stroke="#77777d" stroke-width="3" stroke-dasharray="12 10"')+txt(540,1020,"並んだ物の中の",34,"#8a8a90",'text-anchor="middle"')+txt(540,1090,"欲しい物　0",50,"#e9e6df",'text-anchor="middle" font-weight="700"')+(show?txt(540,1250,"お互いに困る",56,"#d8d5ce",'text-anchor="middle" font-weight="700"'):''))}
function price(t,k){return base(rect(0,0,1080,1920,"#0b0b0e")+glow(540,700,360)+'<g transform="translate(540 640) rotate(-6)">'+rect(-300,-170,600,340,"#e9e6df",30)+'<circle cx="-240" cy="0" r="22" fill="#0b0b0e"/>'+txt(30,40,"¥980",150,"#111",'text-anchor="middle" font-weight="800"')+'</g>'+txt(540,980,"欲しい物ではなく",44,"#8a8a90",'text-anchor="middle"')+txt(540,1050,"その夜を終わらせる値段",50,"#e9e6df",'text-anchor="middle" font-weight="700"'))}
function dark(t,k){let g=Math.max(0,1-k*1.2);return base(rect(0,0,1080,1920,"#09090b")+'<g opacity="'+(0.35+0.4*g)+'">'+cam(man("distant","0 0 300 320",-100,180,1280,1370),1.25,540,850,0,100)+'</g>'+glow(540,1500,260*g+40)+'<rect width="1080" height="1920" fill="#000" opacity="'+(0.15+0.45*k)+'"/>')}
function punchline(){return base(rect(0,0,1080,1920,"#0c0c0f")+glow(560,1250,260)+cam(man("distant","0 0 300 320",-100,180,1280,1370),1.07,540,850))}
function outside(t,k){let w='';for(let i=0;i<9;i++)w+='<path d="M'+(100+i*120)+' '+(520+((i*97)%5)*70)+' h'+(140+(i%3)*30)+'" stroke="#d8d5ce" stroke-width="3" opacity=".12" stroke-linecap="round"/>';return base(rect(0,0,1080,1920,"#0b0b0d")+rect(0,200,1080,800,"#16161b")+rect(60,260,200,700,"#1d1d22")+rect(820,300,200,660,"#1d1d22")+w+rect(0,1300,1080,620,"#101014")+cam(man("back","0 0 400 1000",290,540,500,1100),1,540,1050))}
function street(){let b='';for(let i=0;i<5;i++)b+='<circle cx="'+(120+i*220)+'" cy="'+(420+(i%2)*140)+'" r="90" fill="#d8d5ce" opacity=".09" filter="url(#blur)"/>';let g='';for(let i=0;i<4;i++)g+=rect(160+i*210,1000,40,300,"#45454b",6)+rect(200+i*210,1080,120,30,"#2a2a2e",4);return base('<rect width="1080" height="1920" fill="url(#street)"/>'+b+g+'<path d="M0 1300 L1080 1300 V1920 H0Z" fill="#121216"/>'+cam(man("back","0 0 400 1000",270,560,520,1050),1,540,1050))}
function woman(t,k){let x=-620+(1560+620)*Math.max(0,Math.min(1,k));return base('<rect width="1080" height="1920" fill="#0a0a0c"/><rect x="0" y="1120" width="1080" height="800" fill="#202025"/><g transform="translate('+(x-360)+' 740) scale(1.3)">'+S.woman+'</g>')}
function eyes(t,k,start){let key=t<start+.15?"blank":t<start+.85?"glance":"resolve";return base('<svg x="120" y="800" width="840" height="330" viewBox="80 145 140 55" preserveAspectRatio="xMidYMid meet">'+S[key]+'</svg>')}
function flyer(){return base('<rect width="1080" height="1920" fill="#09090b"/><rect x="220" y="-120" width="640" height="2200" fill="#202025"/><g transform="translate(290 210) rotate(-3)"><image href="../../assets/flyers/flyer_a.png" width="440" height="620"/></g><g transform="translate(420 850) rotate(3)"><image href="../../assets/flyers/flyer_c.png" width="430" height="620"/></g><rect width="1080" height="1920" fill="#000" opacity=".22"/>')}
const SCN={teaser:teaser,bed:bed,scroll:scroll,items:items,wish:wish,cart:cart,order:order,reco:reco,seen:seen,both:both,price:price,punchline:punchline,dark:dark,outside:outside,street:street,woman:woman,eyes:eyes,flyer:flyer,neon:function(){return base("")},black:function(){return base("")},cut:function(){return base("")}};
function render(t){
let sh=TL.shots.find(s=>t>=s[0]&&t<s[1])||TL.shots[TL.shots.length-1],k=(t-sh[0])/Math.max(.001,sh[1]-sh[0]);
let art=document.getElementById("art");art.innerHTML=SCN[sh[2]](t,k,sh[0]);
if(sh[2]==="black"||sh[2]==="neon"){
let final=sh[2]==="neon",d=t-sh[0],f=[1,0,1,1,0,0,1,0,1,1,1,1],on=d<.65?f[Math.floor(d/.05)%f.length]:1;
let tag=final?"くだらない世界　#009":"#009　通販アプリ";
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
