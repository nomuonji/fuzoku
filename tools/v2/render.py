#!/usr/bin/env python3
"""Independent, asset-first vertical-video compositor. No publishing side effects."""
import argparse
import json
import math
import pathlib
import subprocess
import tempfile

def run(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-filter_threads", "2", "-filter_complex_threads", "2", *map(str,args)], check=True)

def duration(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(path)], text=True).strip())

def num(value, name, low, high):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{name}: expected {low}..{high}")
    return value

def render(manifest, output, width=1080, height=1920, fps=30):
    manifest=pathlib.Path(manifest).resolve()
    output=pathlib.Path(output).resolve()
    m=json.loads(manifest.read_text(encoding="utf-8"))
    def asset(item):
        p=(manifest.parent / item["src"]).resolve()
        if not p.is_file(): raise FileNotFoundError(p)
        if not item.get("provenance"): raise ValueError(f"missing provenance: {p}")
        return p
    shots=m["shots"]
    if not shots: raise ValueError("no shots")
    prepared=[]
    frames=0
    for s in shots:
        n=round(num(s["seconds"],"seconds",0.25,60)*fps)
        p=asset(s); kind=s["kind"]
        speed=num(s.get("speed",1),"speed",0.25,4)
        start=num(s.get("in",0),"in",0,3600)
        move=s.get("motion","none")
        if kind not in ("image","video") or move not in ("none","push","pull"):
            raise ValueError("unsupported kind or motion")
        if kind=="image" and (speed!=1 or start!=0): raise ValueError("image cannot have trim/speed")
        if kind=="video" and move!="none": raise ValueError("video motion not supported; bake into source")
        if kind=="video" and duration(p)+0.02 < start+n/fps*speed:
            raise ValueError(f"source too short: {p}")
        prepared.append((p,kind,n,speed,start,move))
        frames+=n
    total=frames/fps
    if total>180: raise ValueError("v2 preview limit: 180 seconds")
    audio=[]
    for a in m.get("audio",[]):
        p=asset(a)
        at=num(a.get("at",0),"audio at",0,total)
        length=num(a["seconds"],"audio seconds",0.05,total)
        gain=num(a.get("gain",1),"audio gain",0,2)
        if at+length>total+0.001 or duration(p)+0.02<length:
            raise ValueError(f"audio out of bounds: {p}")
        audio.append((p,at,length,gain))
    overlays=[]
    for o in m.get("overlays",[]):
        p=asset(o)
        start=num(o["start"],"overlay start",0,total)
        end=num(o["end"],"overlay end",start,total)
        if end-start<1/fps: raise ValueError("overlay too short")
        x=num(o["x"],"overlay x",-1,1); y=num(o["y"],"overlay y",-1,1)
        xe=num(o.get("x_end",x),"overlay x_end",-1,1)
        ye=num(o.get("y_end",y),"overlay y_end",-1,1)
        w=num(o["width"],"overlay width",.02,2)
        opacity=num(o.get("opacity",1),"overlay opacity",0,1)
        overlays.append((p,start,end,x,y,xe,ye,w,opacity))
    captions=[]
    for c in m.get("captions",[]):
        a=num(c["start"],"caption start",0,total)
        b=num(c["end"],"caption end",a,total)
        if b<=a or not isinstance(c["text"],str) or not c["text"].strip(): raise ValueError("empty caption")
        captions.append((a,b,c["text"]))
    with tempfile.TemporaryDirectory(prefix="shorts-v2-") as tmp:
        d=pathlib.Path(tmp)
        clips=[]
        scale=f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1"
        for i,(p,kind,n,speed,start,move) in enumerate(prepared):
            clip=d/f"{i:04}.mp4"; clips.append(clip)
            if kind=="image":
                if move=="none":
                    inp=["-loop","1","-framerate",fps,"-i",p]
                    vf=scale+f",fps={fps}"
                else:
                    inp=["-i",p]
                    step=f"0.16*on/{max(1,n-1)}"
                    z=f"1+{step}" if move=="push" else f"1.16-{step}"
                    vf=scale+f",scale={width*2}:{height*2},zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={n}:s={width}x{height}:fps={fps},setsar=1"
            else:
                inp=["-ss",start,"-i",p]
                vf=f"setpts=(PTS-STARTPTS)/{speed},"+scale+f",fps={fps}"
            run(*inp,"-vf",vf,"-frames:v",n,"-an","-c:v","libx264","-threads","2","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",clip)
            count=subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=nb_frames","-of","csv=p=0",str(clip)],text=True).strip()
            if int(count)!=n: raise RuntimeError(f"short render {clip}: {count}/{n}")
        concat=d/"clips.txt"
        concat.write_text("".join(f"file '{p.name}'\n" for p in clips))
        joined=d/"joined.mp4"
        run("-f","concat","-safe","0","-i",concat,"-c","copy",joined)
        def stamp(t):
            cs=round(t*100); return f"{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}"
        ass=d/"captions.ass"
        header=f"[Script Info]\nScriptType: v4.00+\nPlayResX: {width}\nPlayResY: {height}\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Noto Sans CJK JP,{round(width*.065)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,1,2,{round(width*.08)},{round(width*.12)},{round(height*.19)},1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        def safe(t):
            return t.replace("\\","＼").replace("{","｛").replace("}","｝").replace("\r","").replace("\n",r"\N")
        ass.write_text(header+"".join(f"Dialogue: 0,{stamp(a)},{stamp(b)},Default,,0,0,0,,{safe(t)}\n" for a,b,t in captions),encoding="utf-8")
        inp=["-i",joined,"-f","lavfi","-t",total,"-i","anullsrc=r=48000:cl=stereo"]
        filters=["[1:a]aformat=sample_rates=48000:channel_layouts=stereo[base]"]; labels=["[base]"]
        for i,(p,at,length,gain) in enumerate(audio,2):
            inp+=["-i",p]; label=f"a{i}"; delay=round(at*1000)
            filters.append(f"[{i}:a]atrim=duration={length},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume={gain},adelay={delay}:all=1[{label}]")
            labels.append(f"[{label}]")
        filters.append("".join(labels)+f"amix=inputs={len(labels)}:duration=first:normalize=0,alimiter=limit=0.84:level=false[a]")
        vlabel="0:v"
        for i,(p,start,end,x,y,xe,ye,w,opacity) in enumerate(overlays,2+len(audio)):
            inp+=["-loop","1","-framerate",fps,"-i",p]
            layer=f"layer{i}"; nextv=f"v{i}"
            filters.append(f"[{i}:v]scale={max(2,round(w*width/2)*2)}:-2,format=rgba,colorchannelmixer=aa={opacity},trim=duration={end-start},setpts=PTS-STARTPTS+{start}/TB[{layer}]")
            exprx=f"{width}*({x}+({xe-x})*(t-{start})/{end-start})"
            expry=f"{height}*({y}+({ye-y})*(t-{start})/{end-start})"
            filters.append(f"[{vlabel}][{layer}]overlay=x='{exprx}':y='{expry}':eof_action=pass:repeatlast=0:enable='between(t,{start},{end})'[{nextv}]")
            vlabel=nextv
        if captions:
            filters.append(f"[{vlabel}]ass={ass}[captioned]")
            vlabel="captioned"
        video=["-c:v","libx264","-threads","2","-preset","veryfast","-crf","19"] if captions or overlays else ["-c:v","copy"]
        vmap=f"[{vlabel}]" if captions or overlays else "0:v"
        output.parent.mkdir(parents=True,exist_ok=True)
        run(*inp,"-filter_complex",";".join(filters),"-map",vmap,"-map","[a]",*video,"-c:a","aac","-b:a","192k","-t",total,"-movflags","+faststart",output)
    print(f"{output}: {total:.2f}s, {len(shots)} shots")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("manifest",type=pathlib.Path)
    p.add_argument("output",type=pathlib.Path)
    p.add_argument("--preview",action="store_true")
    a=p.parse_args()
    render(a.manifest,a.output,540 if a.preview else 1080,960 if a.preview else 1920)
