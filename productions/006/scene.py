"""#006 visual builder: new restaurant/receipt/survey scenes drawn as SVG."""
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
function table(){let bars='';for(let i=0;i<4;i++)bars+=rect(225+i*160,300,5,390,"#77777d");return base(rect(0,0,1080,1920,"#101014")+[0,1,2,3].map(i=>rect(0,180+i*210,1080,7,"#29292e")).join("")+rect(90,230,900,540,"#202025",10)+'<rect x="150" y="290" width="780" height="420" fill="url(#window)"/>'+bars+'<ellipse cx="540" cy="1220" rx="430" ry="170" fill="#45454b"/><ellipse cx="540" cy="1185" rx="430" ry="155" fill="#d8d5ce"/><ellipse cx="510" cy="1160" rx="250" ry="75" fill="#aaa69e"/><ellipse cx="510" cy="1140" rx="220" ry="63" fill="#e9e6df"/>'+rect(730,1010,75,150,"#d8d5ce",8)+'<ellipse cx="770" cy="1010" rx="38" ry="10" fill="#f0eee9"/>'+cam(man("back","0 0 400 1000",315,520,450,970),1.05,540,980)+txt(540,180,"DINING",26,"#888",'text-anchor="middle" letter-spacing="14"'))}
function qr(){let c='';for(let y=0;y<21;y++)for(let x=0;x<21;x++){let f=(x<7&&y<7)||(x>13&&y<7)||(x<7&&y>13);let on=f?((x%6===0)||(y%6===0)||(x%6>=2&&x%6<=4&&y%6>=2&&y%6<=4)):Math.sin(x*13.1+y*5.3)*1000%3<1.2;if(on)c+='<rect x="'+(x*12)+'" y="'+(y*12)+'" width="10" height="10" fill="#111"/>'}return c}
function receipt(){return base(rect(270,170,540,1250,"#d8d5ce",12)+txt(540,280,"RECEIPT",32,"#333",'text-anchor="middle" letter-spacing="9"')+txt(340,400,"23:27",24,"#555")+txt(340,495,"夕食　1点",30,"#222")+txt(755,495,"¥1,230",34,"#111",'text-anchor="end"')+'<path d="M330 545 H760" stroke="#555" stroke-width="3" stroke-dasharray="8 8"/>'+txt(340,620,"合計",32,"#222")+txt(755,620,"¥1,230",40,"#111",'text-anchor="end" font-weight="700"')+txt(540,720,"アンケートにご協力ください",23,"#444",'text-anchor="middle"')+'<g transform="translate(414 775)">'+qr()+'</g>'+txt(540,1110,"読み取って回答",24,"#444",'text-anchor="middle"')+cam(man("side","100 20 250 380",-150,970,690,800),1,540,1000))}
function phone(screen,x,y){x=x||260;y=y||280;return rect(x,y,560,1160,"#08080a",70,'stroke="#77777d" stroke-width="12"')+rect(x+22,y+35,516,1092,"#ddd9d0",40)+rect(x+220,y+14,120,12,"#77777d",6)+screen}
function qlist(){let a=["味について","料理が出る速さ","店内の清潔さ","接客について","また来たいですか"];return a.map((v,i)=>txt(355,565+i*125,v,28,"#252529")+txt(740,565+i*125,"○",32,"#444",'text-anchor="end"')).join("")}
function questions(){return base(phone(txt(540,450,"お店アンケート",34,"#111",'text-anchor="middle" font-weight="700"')+txt(540,495,"全5問",22,"#555",'text-anchor="middle"')+qlist()+rect(350,1230,380,70,"#45454b",10)+txt(540,1277,"次へ",29,"#f0eee9",'text-anchor="middle"'))+cam(man("side","100 20 250 380",-180,1110,430,650),.9,540,1000))}
function stars(y){let s='';for(let i=0;i<5;i++)s+='<text x="'+(370+i*82)+'" y="'+y+'" font-size="58" '+JP+' fill="'+(i<5?'#45454b':'#aaa')+'">'+(i<5?'★':'☆')+'</text>';return s}
function foodrating(){return base(phone(txt(540,450,"味について",38,"#111",'text-anchor="middle" font-weight="700"')+txt(540,550,"料理の味はいかがでしたか",23,"#45454b",'text-anchor="middle"')+stars(740)+rect(350,1160,380,74,"#45454b",10)+txt(540,1210,"次へ",29,"#f0eee9",'text-anchor="middle"'))+cam(man("side","100 20 250 380",-120,1110,400,650),.85,540,1000))}
function service(){let a='';for(let i=0;i<3;i++)a+=rect(120+i*310,270,220,700,"#25252a",10)+rect(150+i*310,310,160,550,"#45454b",5);return base(a+txt(540,220,"厨房",30,"#c8c5bd",'text-anchor="middle"')+cam(man("side","100 20 250 380",-70,450,690,1120),1.1,540,980))}
function thumb(){return base(phone(txt(540,450,"店内について",34,"#111",'text-anchor="middle" font-weight="700"')+txt(540,550,"満足度を選んでください",23,"#555",'text-anchor="middle"')+stars(760)+rect(350,1160,380,75,"#45454b",10)+txt(540,1210,"次へ",29,"#f0eee9",'text-anchor="middle"')))}
function returnQuestion(){return base(phone(txt(540,455,"また来たいですか",33,"#111",'text-anchor="middle" font-weight="700"')+rect(330,610,190,105,"#c5c1b9",8,'opacity=".45"')+rect(330,610,190,105,"none",8,'stroke="#77777d" stroke-width="4"')+txt(425,680,"はい",32,"#252529",'text-anchor="middle"')+txt(655,680,"いいえ",32,"#252529",'text-anchor="middle"')))}
function yes(){return base(cam(man("blank","0 0 300 320",-50,190,1180,1260),1,540,850)+phone(txt(540,455,"また来たいですか",31,"#111",'text-anchor="middle"')+rect(330,610,190,105,"#45454b",8)+txt(425,678,"はい",32,"#f3f0e9",'text-anchor="middle"')+rect(560,610,190,105,"#c9c6be",8)+txt(655,678,"いいえ",30,"#444",'text-anchor="middle"')))}
function kitchen(){let a='';for(let i=0;i<4;i++)a+=rect(120+i*220,300,180,520,"#25252a",8);return base(a+txt(540,220,"厨房の奥",32,"#b8b5ad",'text-anchor="middle"')+cam(man("side","100 20 250 380",260,600,590,1020),1,540,1000))}
function feedback(){let dots='';for(let i=0;i<8;i++){let y=500+i*80;dots+='<circle cx="340" cy="'+y+'" r="16" fill="#77777d"/>';for(let j=0;j<5;j++)dots+=rect(400+j*70,y-11,48,22,j<(i%4+2)?"#45454b":"#c8c5bd",4)}return base(rect(160,240,760,1080,"#d8d5ce",12)+txt(540,360,"回答結果",38,"#161618",'text-anchor="middle" font-weight="700"')+dots+txt(540,1430,"料理と接客の見直し",28,"#c8c5bd",'text-anchor="middle"'))}
function coupon(){return base(phone(txt(540,465,"ご回答ありがとうございます",25,"#333",'text-anchor="middle"')+txt(540,590,"次回ご利用時",27,"#555",'text-anchor="middle"')+txt(540,760,"30円引き",60,"#141414",'text-anchor="middle" font-weight="700"')+rect(360,860,360,5,"#77777d")+txt(540,950,"この画面を提示",24,"#555",'text-anchor="middle"')+rect(355,1120,370,70,"#45454b",10)+txt(540,1168,"保存する",29,"#f3f0e9",'text-anchor="middle"')))}
function saveCoupon(){return base(cam(man("blank","0 0 300 320",-70,160,1220,1300),1.02,540,850)+rect(150,1380,780,170,"#1b1b20",12)+txt(540,1450,"次回の割引",27,"#aaa",'text-anchor="middle"')+txt(540,1515,"30円",58,"#e9e6df",'text-anchor="middle" font-weight="700"'))}
function punchline(){return base(cam(man("distant","0 0 300 320",-100,180,1280,1370),1.07,540,850)+txt(540,1690,"レシート",22,"#777",'text-anchor="middle" letter-spacing="8"'))}
function returnPlate(){return base(rect(0,1050,1080,870,"#242429")+ '<ellipse cx="540" cy="1200" rx="380" ry="150" fill="#77777d"/><ellipse cx="540" cy="1185" rx="320" ry="112" fill="#d8d5ce"/><ellipse cx="540" cy="1175" rx="220" ry="72" fill="#b8b5ae"/>'+cam(man("back","0 0 400 1000",290,250,500,1180),1.05,540,1000))}
function waterRing(){return base(rect(140,320,800,1130,"#27272d",28)+'<ellipse cx="560" cy="940" rx="215" ry="105" fill="none" stroke="#d8d5ce" stroke-opacity=".22" stroke-width="12"/><ellipse cx="560" cy="940" rx="170" ry="78" fill="none" stroke="#d8d5ce" stroke-opacity=".12" stroke-width="4"/>'+txt(540,1530,"23:27",23,"#666",'text-anchor="middle" letter-spacing="8"'))}
function street(){let b='';for(let i=0;i<5;i++)b+='<circle cx="'+(120+i*220)+'" cy="'+(420+(i%2)*140)+'" r="90" fill="#d8d5ce" opacity=".09" filter="url(#blur)"/>';return base('<rect width="1080" height="1920" fill="url(#street)"/>'+b+'<path d="M0 1130 L1080 900 V1920 H0Z" fill="#121216"/>'+cam(man("back","0 0 400 1000",270,530,520,1050),1,540,1050))}
function woman(t,k){let x=-620+(1560+620)*Math.max(0,Math.min(1,k));return base('<rect width="1080" height="1920" fill="#0a0a0c"/><rect x="0" y="1120" width="1080" height="800" fill="#202025"/><g transform="translate('+(x-360)+' 740) scale(1.3)">'+S.woman+'</g>')}
function eyes(t,k,start){let key=t<start+.15?"blank":t<start+.85?"glance":"resolve";return base('<svg x="120" y="800" width="840" height="330" viewBox="80 145 140 55" preserveAspectRatio="xMidYMid meet">'+S[key]+'</svg>')}
function flyer(){return base('<rect width="1080" height="1920" fill="#09090b"/><rect x="220" y="-120" width="640" height="2200" fill="#202025"/><g transform="translate(290 210) rotate(-3)"><image href="../../assets/flyers/flyer_a.png" width="440" height="620"/></g><g transform="translate(420 850) rotate(3)"><image href="../../assets/flyers/flyer_c.png" width="430" height="620"/></g><rect width="1080" height="1920" fill="#000" opacity=".22"/>')}
function teaser(){return base(rect(80,250,920,1320,"#d8d5ce",8)+txt(540,400,"ご回答ありがとうございます",26,"#333",'text-anchor="middle"')+txt(540,690,"次回",35,"#333",'text-anchor="middle"')+txt(540,860,"30円引き",95,"#111",'text-anchor="middle" font-weight="700"')+rect(310,1040,460,8,"#77777d")+cam(man("side","100 20 250 380",-150,1120,580,760),.8,540,1000))}
const SCN={teaser:teaser,restaurant:table,receipt:receipt,questions:questions,foodrating:foodrating,service:service,thumb:thumb,return_question:returnQuestion,yes:yes,kitchen:kitchen,feedback:feedback,coupon:coupon,save_coupon:saveCoupon,punchline:punchline,return_plate:returnPlate,water_ring:waterRing,street:street,woman:woman,eyes:eyes,flyer:flyer,neon:function(){return base("")},black:function(){return base("")}};
function render(t){
let sh=TL.shots.find(s=>t>=s[0]&&t<s[1])||TL.shots[TL.shots.length-1],k=(t-sh[0])/Math.max(.001,sh[1]-sh[0]);
let art=document.getElementById("art");art.innerHTML=SCN[sh[2]](t,k,sh[0]);
if(sh[2]==="black"||sh[2]==="neon"){
let final=sh[2]==="neon",d=t-sh[0],f=[1,0,1,1,0,0,1,0,1,1,1,1],on=d<.65?f[Math.floor(d/.05)%f.length]:1;
let tag=final?"くだらない世界　#006":"#006　食後のアンケート";
art.innerHTML+='<foreignObject x="0" y="'+(final?480:620)+'" width="1080" height="1000"><div xmlns="http://www.w3.org/1999/xhtml" style="text-align:center;opacity:'+on+'"><div class="neon" style="font-size:'+(final?145:104)+'px;writing-mode:vertical-rl;display:inline-block;height:'+(final?650:510)+'px">そうだ、風俗行こう。</div><div style="color:#ddd;font-size:34px;letter-spacing:12px;margin-top:28px">'+tag+'</div></div></foreignObject>';
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
