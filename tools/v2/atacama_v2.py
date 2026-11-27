#!/usr/bin/env python3
"""Evidence-led animated vertical cut. Original graphics are labelled explanatory.
No publishing. Actual narration durations determine editing time.
"""
import sys, pathlib, json, math, subprocess, random, wave
from PIL import Image, ImageOps, ImageDraw, ImageFont
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from vo import tts, DEFAULT, FX
import evidence_pilot as ep
W,H,FPS=720,1280,24
OUT=pathlib.Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
ep.OUT=OUT
BG=(19,21,22); INK=(244,241,230); MUT=(159,164,161); PINK=(255,77,144)
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
fonts={}
def font(n,b=False):
    k=(n,b)
    if k not in fonts: fonts[k]=ImageFont.truetype(BOLD if b else FONT,n,index=0)
    return fonts[k]
def txt(d,pos,s,n=28,c=INK,b=False,anchor=None):
    d.text(pos,s,font=font(n,b),fill=c,anchor=anchor)
def line(d,xy,c=MUT,width=2):d.line(xy,fill=c,width=width)
def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def mix(a,b,t):return a+(b-a)*t
def rect(d,xy,fill,outline=None,width=1,r=0):
    xy=tuple(round(v) for v in xy)
    if r:d.rounded_rectangle(xy,radius=r,fill=fill,outline=outline,width=width)
    else:d.rectangle(xy,fill=fill,outline=outline,width=width)
def ff(*a):subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",*map(str,a)],check=True)
def duration(p):return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(p)],text=True))
def grain():
    rng=np.random.default_rng(17)
    n=rng.normal(0,3,(H,W,1)); a=np.clip(np.array(BG)[None,None,:]+n,0,255).astype("uint8")
    return Image.fromarray(a)
paper=grain()
def base(chapter,tag,progress):
    im=paper.copy();d=ImageDraw.Draw(im)
    txt(d,(38,48),"くだらない世界",22,MUT,True)
    txt(d,(680,48),chapter,21,INK,True,"ra")
    line(d,[(38,91),(682,91)],(86,90,90),1)
    txt(d,(40,107),tag,22,MUT)
    rect(d,(40,1140,680,1144),(75,78,77))
    rect(d,(40,1140,40+640*progress,1144),PINK)
    return im,d
def credit(d,fig):
    txt(d,(40,1170),f"出典：Morell-Delgado et al. (2025) Fig. {fig}",16,MUT)
    txt(d,(40,1198),"CC BY 4.0 ｜ 色調・配置を調整",16,MUT)
    txt(d,(40,1224),"doi:10.1007/s43615-025-00618-z",16,MUT)
def photo(im,pic,box,zoom=1,dx=0):
    # Use the complete published figure, not unverified individual panel crops.
    x,y,w,h=box
    p=ImageOps.contain(pic,(w,h),Image.Resampling.LANCZOS)
    p=ImageOps.colorize(ImageOps.grayscale(p),(14,17,20),(246,243,236))
    # Pan only inside separately framed photo; at zoom=1 entire figure is visible.
    if zoom>1:
        p=p.resize((round(p.width*zoom),round(p.height*zoom)),Image.Resampling.LANCZOS)
        if p.width>w or p.height>h:
            l=max(0,min(p.width-w,round((p.width-w)/2+dx)))
            t=max(0,(p.height-h)//2)
            p=p.crop((l,t,min(p.width,l+w),min(p.height,t+h)))
    im.paste(p,(x+(w-p.width)//2,y+(h-p.height)//2))
def caption(d,rows,y=985,size=41):
    for j,s in enumerate(rows):txt(d,(40,y+j*(size+13)),s,size,INK,True)
def cloth(d,x,y,w,h,kind=0):
    # Editorial illustration, not a simulated photograph; folds/creases move with garment.
    colors=[(126,140,142),(184,176,156),(89,103,108),(175,153,139),(109,111,108)]
    c=colors[kind%len(colors)]
    pts=[(x+w*.22,y),(x+w*.4,y+h*.07),(x+w*.6,y+h*.07),(x+w*.78,y),(x+w,y+h*.26),(x+w*.8,y+h*.39),(x+w*.73,y+h*.25),(x+w*.73,y+h),(x+w*.27,y+h),(x+w*.27,y+h*.25),(x+w*.2,y+h*.39),(x,y+h*.26)]
    d.polygon(pts,fill=c,outline=(29,30,30),width=2)
    line(d,[(x+w*.3,y+h*.7),(x+w*.68,y+h*.73)],tuple(max(0,k-33) for k in c),2)
    line(d,[(x+w*.38,y+h*.13),(x+w*.5,y+h*.2),(x+w*.62,y+h*.13)],(41,42,42),2)
    if kind==4:
        d.polygon([(x+w*.48,y+h*.54),(x+w*.53,y+h*.61),(x+w*.44,y+h*.65)],fill=BG)
        line(d,[(x+w*.29,y+h*.82),(x+w*.68,y+h*.88)],(73,72,69),4)
def bale(d,x,y,w,h,fill=0.8,bad=False):
    # Cutaway viewed head-on; progress is qualitative, not measured proportions.
    rect(d,(x+9,y+10,x+w+9,y+h+10),(5,6,6),r=12)
    rect(d,(x,y,x+w,y+h),(56,58,55),outline=(146,145,137),width=3,r=9)
    rows=5
    for k in range(rows):
        yy=y+h-12-(k+1)*(h-20)/rows
        if k/rows<fill:
            col=(111+k*11,115+k*8,111+k*5)
            if bad and k==4:col=(127,95,98)
            rect(d,(x+11,yy,x+w-11,yy+(h-20)/rows-4),col,r=5)
            line(d,[(x+23,yy+6),(x+w-31,yy+11)],(60,65,64),2)
    for f in (.25,.73):
        xx=x+w*f;rect(d,(xx-5,y,xx+5,y+h),(205,205,190))
def gauge(d,y,amount):
    rect(d,(140,y,580,y+102),(36,39,38),outline=(110,116,111),width=2,r=12)
    txt(d,(162,y+14),"重量（模式図）",20,MUT)
    rect(d,(163,y+58,557,y+78),(65,68,66),r=4)
    rect(d,(163,y+58,163+394*amount,y+78),PINK,r=4)
lines=[
("ジーンズ、四十五キロで二十万チリペソ。","01","チリの卸売店・調査時の表示"),
("古着は、一着ずつではなく、重さで取引されます。","02","古着の卸売"),
("仕分け前の荷物には、品質の低い服も混じります。","03","未仕分けの荷物／模式図"),
("現地調査では、一部の業者が、そんな服を販売用の梱包の隙間に詰めていました。","04","別の取引慣行／模式図"),
("重さで売るからです。","05","重量売買／模式図"),
("市場で再利用される服もある。でも、処分先が足りない服もあります。","06","古着市場・調査写真"),
("二千二十三年四月、研究者が砂漠で見つけたのは、捨てられた服と、燃えた跡でした。","07","アタカマ砂漠・2023年4月27日")
]
def main():
    figs={i:ep.fetch(i) for i in (2,3,5)}
    meta=[]
    for i,(s,_,_) in enumerate(lines):
        raw=OUT/f"raw{i}.wav"; p=OUT/f"vo{i}.wav"
        raw.write_bytes(tts(s,dict(DEFAULT,speed=1.13,pitch=-.03,intonation=.96)))
        ff("-i",raw,"-af",FX,"-ar","48000","-ac","1","-c:a","pcm_s16le",p);raw.unlink()
        n=math.ceil((duration(p)+(.65 if i==6 else .15))*FPS)
        meta.append({"text":s,"frames":n,"voice":p.name})
    total=sum(x["frames"] for x in meta);cursor=0
    video=OUT/"picture.mp4"
    proc=subprocess.Popen(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",str(video)],stdin=subprocess.PIPE)
    timeline=[]
    for i,m in enumerate(meta):
        start=cursor/FPS; n=m["frames"]; timeline.append(dict(start=start,end=(cursor+n)/FPS,**m))
        for f in range(n):
            u=f/max(1,n-1);t=f/FPS; e=smooth(t/.28)
            im,d=base(lines[i][1],lines[i][2],(cursor+f)/total)
            if i==0:
                photo(im,figs[2],(38,170,644,505)); d=ImageDraw.Draw(im)
                # Hard-cut visual emphasis on the real offer, not a claim about contents.
                txt(d,(40,715),"ジーンズ",32,MUT,True)
                txt(d,(40,763),"45",130,INK,True);txt(d,(264,850),"kg",51,INK,True)
                rect(d,(40,924,680,928),PINK)
                txt(d,(40,958),"200,000",62,PINK,True);txt(d,(435,990),"CLP",31,INK,True)
                credit(d,2)
            elif i==1:
                photo(im,figs[2],(38,174,644,600),1.0+.12*smooth(u))
                d=ImageDraw.Draw(im); txt(d,(40,817),"一着  →  一梱包",46,INK,True)
                caption(d,["重さで取引される"],995);credit(d,2)
            elif i==2:
                txt(d,(40,199),"開封・仕分け",52,INK,True)
                bale(d,230,350,260,220,.95)
                for k in range(5):
                    v=smooth((u-k*.075)*2.2)
                    x=mix(310,65+k*130,v); y=mix(404,720+25*math.sin(k),v)-125*math.sin(math.pi*v)
                    cloth(d,x,y,115,136,k)
                txt(d,(360,925),"品質の異なる服",34,INK,True,"ma")
                caption(d,["仕分け前には","低品質の衣類も混じる"],995,34)
                txt(d,(40,1190),"解説用イラスト・割合を示すものではありません",18,MUT)
            elif i==3:
                txt(d,(40,190),"販売用の梱包",52,INK,True)
                # One garment moves from the rejected pile into the remaining gap.
                v=smooth((u-.14)/.55)
                bale(d,220,430,280,300,.79 if v<.86 else 1,bad=v>=.86)
                if v<.86:
                    x=mix(68,298,v); y=mix(785,451,v)-180*math.sin(math.pi*v)
                    cloth(d,x,y,117,140,4)
                txt(d,(60,770),"低品質品",27,PINK,True)
                gauge(d,830,.79+.21*v)
                caption(d,["一部の業者は","隙間を埋めるために使う"],985,36)
                txt(d,(40,1190),"取引慣行の模式図・実物の再現ではありません",18,MUT)
            elif i==4:
                txt(d,(40,202),"なぜ詰める？",55,INK,True)
                bale(d,218,362,284,290,1,True)
                gauge(d,704,1)
                txt(d,(360,877),"重さで売るから。",48,PINK,True,"ma")
                txt(d,(40,1190),"重量と内容の比率は例示（実測ではない）",18,MUT)
            elif i==5:
                photo(im,figs[3],(38,172,644,636),1.0)
                d=ImageDraw.Draw(im);txt(d,(40,830),"再利用される服",39,INK,True)
                caption(d,["しかし、処分先が","足りない服もある"],985,37)
                credit(d,3)
            else:
                # Original field evidence includes three separately labelled panels.
                # Preserve context and avoid a fake aerial image or current-state claim.
                photo(im,figs[5],(38,180,644,690),1+.08*smooth(u));d=ImageDraw.Draw(im)
                txt(d,(40,873),"捨てられた服。焼け跡。",39,INK,True)
                txt(d,(40,973),"2023.04.27",54,PINK,True)
                credit(d,5)
            if f==0 or f==n//2:
                im.resize((360,640),Image.Resampling.LANCZOS).save(OUT/f"review-{i+1:02}-{f:04}.jpg",quality=88)
            proc.stdin.write(im.tobytes())
        cursor+=n
    proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError("video encode failed")
    # Lay out the actual VOICEVOX takes at exact cut boundaries, with short pauses.
    sr=48000
    audio=np.zeros(round(total/FPS*sr),dtype=np.float64)
    for i,m in enumerate(timeline):
        with wave.open(str(OUT/m["voice"]),"rb") as f:
            assert f.getframerate()==sr and f.getnchannels()==1 and f.getsampwidth()==2
            a=np.frombuffer(f.readframes(f.getnframes()),dtype="<i2")/32768.
        start=round(m["start"]*sr)
        audio[start:start+len(a)]+=a*.87
        # quiet self-generated percussive cut accents, never purported location audio
        if i in (0,2,3,6):
            l=round(.11*sr); x=np.arange(l)/sr
            tone=.045*np.sin(2*np.pi*(96*x-130*x*x))*np.exp(-x*42)
            audio[start:start+l]+=tone
    ap=OUT/"mix.wav"
    with wave.open(str(ap),"wb") as f:f.setparams((1,2,sr,0,"NONE","not compressed"));f.writeframes((np.clip(audio,-1,1)*32767).astype("<i2").tobytes())
    ff("-i",video,"-i",ap,"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k","-movflags","+faststart",OUT/"atacama-v2.mp4")
    result=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(OUT/"atacama-v2.mp4")],text=True))
    v=next(s for s in result["streams"] if s["codec_type"]=="video")
    assert (v["width"],v["height"],int(v["nb_frames"]))==(W,H,total)
    assert any(s["codec_type"]=="audio" for s in result["streams"])
    assert abs(float(result["format"]["duration"])-total/FPS)<.1
    # Contact sheet of first/middle frames of every shot.
    imgs=sorted(OUT.glob("review-*.jpg"));sheet=Image.new("RGB",(7*180,2*320),BG)
    for j,p in enumerate(imgs):sheet.paste(Image.open(p).resize((180,320)),(j//2*180,j%2*320))
    sheet.save(OUT/"contact-sheet.jpg",quality=90)
    (OUT/"timeline.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding="utf-8")
    (OUT/"credits.txt").write_text("Morell-Delgado, G., Talens Peiró, L., Toboso-Chavero, S. (2025). The Journey of a Discarded T-shirt: From the Global North to the Atacama Dumpsite. Figs. 2,3,5. https://doi.org/10.1007/s43615-025-00618-z\nCC BY 4.0 https://creativecommons.org/licenses/by/4.0/ ; desaturated, resized, reframed. Original illustrations and synthesized sound accents. VOICEVOX 青山龍星. Photographs are historical. Fig.2(c) depicts a specific first-quality offer; no claim that it contained low-quality goods. Fig.3 includes Bolivia. No individual garment tracked.\n",encoding="utf-8")
    print("VERIFIED",W,H,total,total/FPS,flush=True)
if __name__=="__main__":main()
