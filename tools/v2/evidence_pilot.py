#!/usr/bin/env python3
"""One-off evidence-led edit, using the V2 compositor. No posting."""
import sys, pathlib, json, math, urllib.request, subprocess, hashlib
from PIL import Image, ImageOps, ImageDraw, ImageFont
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from vo import tts, DEFAULT, FX
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from render import render,duration
W,H=1080,1920
OUT=pathlib.Path(sys.argv[1]).resolve(); OUT.mkdir(parents=True,exist_ok=True)
BASE="https://media.springernature.com/full/springer-static/image/art%3A10.1007%2Fs43615-025-00618-z/MediaObjects/43615_2025_618_Fig{}_HTML.jpg"
credit="Morell-Delgado et al. (2025) · CC BY 4.0"
doi="doi:10.1007/s43615-025-00618-z"
font="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
bold="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def F(s,b=False): return ImageFont.truetype(bold if b else font,s,index=0)
def fetch(n):
    path=OUT/f"source_fig{n}.jpg"
    urls=[BASE.format(n),BASE.replace("/full/","/lw685/").format(n)]
    for u in urls:
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=30) as r: data=r.read()
            path.write_bytes(data)
            with Image.open(path) as im: im.verify()
            print("verified source",n,len(data),hashlib.sha256(data).hexdigest(),flush=True)
            return Image.open(path).convert("RGB")
        except Exception as e: print("source retrieval failed",n,type(e).__name__,flush=True)
    raise RuntimeError("Licensed evidence unavailable; do not substitute synthetic images")
def write(img,name):
    p=OUT/name;img.save(p);return p.name
def base(k,tag):
    im=Image.new("RGB",(W,H),(16,17,18));d=ImageDraw.Draw(im)
    d.rectangle((64,108,78,195),fill=(220,220,215))
    d.text((100,112),"記録 /  "+tag,font=F(41,True),fill="white")
    d.text((100,177),f"FIELD NOTES   /   {k:02}",font=F(25),fill=(170,170,170))
    return im
def photo(im,pic,box,tag):
    # Keep all panels visible and avoid passing cropped contextual images as a single photograph.
    x,y,w,h=box
    src=ImageOps.grayscale(pic).convert("RGB")
    contained=ImageOps.contain(src,(w,h),method=Image.Resampling.LANCZOS)
    im.paste(contained,(x+(w-contained.width)//2,y+(h-contained.height)//2))
    d=ImageDraw.Draw(im)
    d.text((64,y+h+30),tag,font=F(34),fill=(220,220,220))
    d.text((64,y+h+88),credit,font=F(25),fill=(160,160,160))
    d.text((64,y+h+125),doi,font=F(23),fill=(160,160,160))
def headline(im,lines,y=1360):
    d=ImageDraw.Draw(im)
    for i,s in enumerate(lines): d.text((64,y+i*100),s,font=F(76,True),fill="white")
def card(k,pic,tag,label,words):
    im=base(k,tag)
    photo(im,pic,(64,310,952,850),label)
    headline(im,words,1390)
    return write(im,f"card{k}.png")
def flow(k,stage):
    im=base(k,"流通の模式図")
    d=ImageDraw.Draw(im); white=(237,237,230); grey=(135,135,135)
    d.text((68,324),"海外から届く古着",font=F(58,True),fill=white)
    d.rounded_rectangle((74,475,1000,655),radius=18,outline=grey,width=4)
    for i in range(8):
        x=110+i*108
        d.rounded_rectangle((x,517,x+78,611),radius=8,fill=(204,204,198))
        d.line((x+5,548,x+73,548),fill=(40,40,40),width=3)
    d.line((540,655,540,760),fill=white,width=6)
    d.line((260,760,820,760),fill=white,width=6)
    for x in [260,820]:
        d.line((x,760,x,862),fill=white,width=6)
        d.polygon([(x-16,843),(x+16,843),(x,870)],fill=white)
    for x,t1,t2,on in [(65,"売れる服","市場へ",True),(575,"売れない服","処分の問題",stage>=2)]:
        c=white if on else grey
        d.rounded_rectangle((x,885,x+440,1160),radius=20,outline=c,width=4)
        d.text((x+28,920),t1,font=F(49,True),fill=c)
        d.text((x+28,1010),t2,font=F(45),fill=c)
    d.text((65,1240),"量を表す図ではありません",font=F(31),fill=grey)
    headline(im,["売れない服も","一緒に届く"],1400)
    return write(im,f"flow{k}.png")
def wav(i,line):
    raw=OUT/f"raw{i}.wav";p=OUT/f"vo{i}.wav"
    raw.write_bytes(tts(line,dict(DEFAULT,speed=1.08)))
    subprocess.run(["ffmpeg","-v","error","-y","-i",str(raw),"-af",FX,"-ar","48000",str(p)],check=True)
    raw.unlink()
    return p
def main():
    dump=fetch(5); market=fetch(3)
    pics=[card(1,dump,"チリ・2023年4月","現地調査写真／Fig. 5",["砂漠に捨てられた","服。"]),
          card(2,market,"古着市場","現地調査写真／Fig. 3（チリ・ボリビア）",["売れる服には","買い手がいる"]),
          flow(3,2),
          card(4,dump,"チリ・2023年4月","現地調査写真／Fig. 5",["売れない服の","行き先"]),
          card(5,dump,"チリ・2023年4月","現地調査写真／Fig. 5",["手放した服は、","どこへ？"])]
    lines=["砂漠に捨てられているのは、服です。","ここはチリ。海外から古着が集まります。","売れる服は市場へ。でも、売れない服も一緒に届きます。","売るのも、処分するのも難しい服は、砂漠に捨てられることがあります。","服を捨てた側では、もう見えなくなった問題です。"]
    shots=[];audio=[];cursor=0
    for i,(pic,line) in enumerate(zip(pics,lines)):
        p=wav(i,line); a=duration(p)
        n=math.ceil((a+0.28)*30)
        shots.append(dict(src=pic,kind="image",seconds=n/30,motion="none",provenance="CC BY field photos / original schematic"))
        audio.append(dict(src=p.name,at=cursor,seconds=a,gain=1,provenance="VOICEVOX 青山龍星"))
        cursor+=n/30
    m={"shots":shots,"audio":audio}
    (OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
    (OUT/"credits.txt").write_text("Photos: Morell-Delgado, G., Talens Peiró, L. & Toboso-Chavero, S. (2025), The Journey of a Discarded T-shirt: From the Global North to the Atacama Dumpsite, Fig. 3 and Fig. 5. https://doi.org/10.1007/s43615-025-00618-z\nCC BY 4.0 https://creativecommons.org/licenses/by/4.0/ ; resized, desaturated and placed in graphic layout. VOICEVOX: 青山龍星.\nHistorical field photos, not contemporary footage.\n",encoding="utf-8")
    render(OUT/"manifest.json",OUT/"pilot.mp4",540,960)
    print("PILOT_DURATION",cursor,flush=True)
if __name__=="__main__": main()
