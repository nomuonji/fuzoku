"""Integration smoke test with synthetic fixtures only (not an editorial demo)."""
import json, pathlib, subprocess, tempfile
from render import render, run, duration
with tempfile.TemporaryDirectory() as tmp:
    d=pathlib.Path(tmp)
    run("-f","lavfi","-i","testsrc2=size=640x360:rate=30:duration=4","-c:v","libx264","-threads","2",d/"clip.mp4")
    run("-f","lavfi","-i","color=red:size=500x500","-frames:v",1,"-threads",1,d/"still.png")
    run("-f","lavfi","-i","sine=frequency=440:duration=1",d/"tone.wav")
    def item(src,**kw): return {"src":src,"provenance":"synthetic ffmpeg fixture",**kw}
    m={"shots":[item("clip.mp4",kind="video",seconds=1.5,speed=2),item("still.png",kind="image",seconds=1.5,motion="push")],"audio":[item("tone.wav",at=1,seconds=1,gain=.25)],"captions":[{"start":.2,"end":1.2,"text":"字幕 / TEST"}]}
    (d/"m.json").write_text(json.dumps(m))
    render(d/"m.json",d/"out.mp4",540,960)
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-of","json",str(d/"out.mp4")],text=True))
    v=next(s for s in probe["streams"] if s["codec_type"]=="video")
    assert (v["width"],v["height"],int(v["nb_frames"]))==(540,960,90),v
    assert any(s["codec_type"]=="audio" for s in probe["streams"])
    assert abs(duration(d/"out.mp4")-3)<.12
    m["shots"][0]["seconds"]=5
    (d/"m.json").write_text(json.dumps(m))
    try: render(d/"m.json",d/"bad.mp4",540,960)
    except ValueError: pass
    else: raise AssertionError("short source accepted")
    print("render smoke passed")
