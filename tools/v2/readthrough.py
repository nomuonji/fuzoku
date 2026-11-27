#!/usr/bin/env python3
"""Non-publishing VOICEVOX table read. Both endings share exact same audio takes."""
import json, pathlib, subprocess, sys, tempfile, wave, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from vo import tts, DEFAULT, FX

def ff(*args):
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",*map(str,args)],check=True)

def frames(path):
    with wave.open(str(path),"rb") as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(48000,1,2)
        return f.getnframes()

def stamp(n):
    ms=round(n*1000/48000)
    return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"

def main():
    manifest=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2])
    m=json.loads(manifest.read_text(encoding="utf-8")); out.mkdir(parents=True,exist_ok=True)
    speakers=json.load(urllib.request.urlopen("http://127.0.0.1:50021/speakers",timeout=10))
    cast={}
    for who,v in m["cast"].items():
        p=next(s for s in speakers if s["name"]==v["speaker"])
        style=next(s for s in p["styles"] if s["name"]==v["style"])
        cast[who]={**DEFAULT,**v,"speaker":style["id"]}
    labels={"worker":"部下","boss":"課長","home":"家族（電話）"}
    with tempfile.TemporaryDirectory() as tmp:
        d=pathlib.Path(tmp); takes={}
        def take(who,text):
            key=(who,text)
            if key not in takes:
                n=len(takes); raw=d/f"raw{n}.wav"; cooked=d/f"take{n}.wav"
                raw.write_bytes(tts(text,cast[who]))
                fx=FX+(",highpass=f=350,lowpass=f=3400" if who=="home" else "")
                ff("-i",raw,"-af",fx,"-ar",48000,"-ac",1,"-c:a","pcm_s16le",cooked)
                takes[key]=cooked
            return takes[key]
        stats={}
        for variant,ending in m["variants"].items():
            rows=m["common"]+ending; cursor=0; subtitles=[]; timeline=[]
            target=out/f"{variant}.wav"
            with wave.open(str(target),"wb") as f:
                f.setparams((1,2,48000,0,"NONE","not compressed"))
                for i,(who,text,pause,shot) in enumerate(rows,1):
                    p=take(who,text); n=frames(p); end=cursor+n
                    with wave.open(str(p),"rb") as src: f.writeframes(src.readframes(n))
                    subtitles.append(f"{i}\n{stamp(cursor)} --> {stamp(end)}\n{labels[who]}：{text}\n\n")
                    timeline.append({"speaker":who,"start":cursor/48000,"end":end/48000,"shot":shot})
                    gap=round(pause*48000); f.writeframes(bytes(gap*2)); cursor=end+gap
            (out/f"{variant}.srt").write_text("".join(subtitles),encoding="utf-8")
            (out/f"{variant}.timeline.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding="utf-8")
            ff("-i",target,"-c:a","libmp3lame","-b:a","128k",out/f"{variant}.mp3")
            stats[variant]={"duration_seconds":frames(target)/48000,"lines":len(rows),"shared_lines":len(m["common"])}
        # Verify the actual common PCM prefix, not only the declared inputs.
        common_frames=sum(frames(take(w,t))+round(p*48000) for w,t,p,_ in m["common"])
        with wave.open(str(out/"A.wav"),"rb") as a,wave.open(str(out/"B.wav"),"rb") as b:
            assert a.readframes(common_frames)==b.readframes(common_frames)
        (out/"report.json").write_text(json.dumps({"stats":stats,"identical_common_pcm":True,"voices":{k:v["speaker"] for k,v in cast.items()}},indent=2),encoding="utf-8")
        print(json.dumps(stats),flush=True)
if __name__=="__main__": main()
