import json, subprocess, urllib.request, urllib.parse, sys
lines=["午後十一時。この街で一番明るいのは、レジだ。","店員はいない。レジは四台。全部、客が打つ。","誰にも命令されていない。だから、文句の言いようがない。","昔、働くには雇い主が要った。今は、ボタンがあればいい。","機械は俺を疑い、俺は機械に従う。給料は、お互いに出ない。","礼を言われる筋合いはない。働いたのは、俺だ。","それでも、少し安心している自分がいる。誰とも話さずに済むからだ。","外は雨だった。この街では、雨だけがタダで降ってくる。","そうだ、風俗行こう。"]
sid=int(sys.argv[1]); speed=float(sys.argv[2]); pitch=float(sys.argv[3]); out=sys.argv[4]
gaps=[1.2,0.9,1.1,1.6,1.4,1.6,1.3,4.0,0]
parts=[]
for i,t in enumerate(lines):
    q=json.load(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:50021/audio_query?speaker={sid}&text="+urllib.parse.quote(t),method="POST")))
    q["speedScale"]=speed; q["pitchScale"]=pitch; q["intonationScale"]=0.85 if i<8 else 0.7; q["prePhonemeLength"]=0.05; q["postPhonemeLength"]=0.1
    q["outputSamplingRate"]=48000
    w=urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:50021/synthesis?speaker={sid}",data=json.dumps(q).encode(),headers={"Content-Type":"application/json"})).read()
    fn=f"vo_{sid}_{i:02d}.wav"; open(fn,"wb").write(w); parts.append((fn,gaps[i]))
# concat with silences
inputs=[];flt=[]
for k,(fn,g) in enumerate(parts):
    inputs+=["-i",fn]; flt.append(f"[{k}:a]aresample=48000,apad=pad_dur={g}[a{k}]")
flt.append("".join(f"[a{k}]" for k in range(len(parts)))+f"concat=n={len(parts)}:v=0:a=1[v]")
subprocess.run(["ffmpeg","-v","error","-y",*inputs,"-filter_complex",";".join(flt),"-map","[v]","nar.wav"],check=True)
subprocess.run(["ffmpeg","-v","error","-y","-i","nar.wav","-i","bgm.mp3","-filter_complex",
 "[0:a]highpass=f=70,acompressor=threshold=-20dB:ratio=2.5,aecho=0.8:0.4:35:0.08,volume=1.0[n];[1:a]volume=0.12,afade=t=out:st=46.5:d=2[b];[n][b]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5",
 "-c:a","libmp3lame","-b:a","192k",out],check=True)
print(out, subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",out]).decode().strip())
