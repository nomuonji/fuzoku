"""#003 timeline: 3-second cold open (the new vinyl clings to the fingers), neon series title, then the story. No VO on the punchline.

Writes vo_fast/*.wav (narration sped up 1.08x) and timeline.json.
"""
import json, pathlib, subprocess

D = pathlib.Path(__file__).resolve().parent
SPEED = 1.08
(D / "vo_fast").mkdir(exist_ok=True)


def dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


SUB = {  # line index -> subtitle with breaks
    0: "二十三時八分。\n改札を出たら、\n降っていた。",
    1: "予報は、朝から七十パーセント。\n傘は、持って出なかった。",
    2: "駅前のコンビニは、\nもう入口に傘を立てている。\n降り出して、まだ五分だ。",
    3: "七百三十七円。\n玄関には、\n同じのが六本ある。",
    4: "レジの奥に、\n忘れ物の傘が束ねてある。\nたぶん、一本は俺のだ。",
    5: "テープを剥がすと、\n新しいビニールが、\n指に吸いついた。",
    6: "店が待っていたのは、\n雨じゃない。\n傘を持たずに出る、俺だ。",
    7: "透明な傘の中には、\n俺の息の温度しかない。",
    8: "この傘も、今夜、\nどこかに置いてくる。",
}
L = {}
for k in SUB:
    src, dst = D / f"vo/{k}.wav", D / f"vo_fast/{k}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", f"atempo={SPEED}", str(dst)], check=True)
    L[k] = dur(dst)

vo, shots, subs, ev = [], [], [], {}
t = 0.0


def say(k, start, tail=0.15):
    vo.append([k, round(start, 3), round(L[k], 3)])
    subs.append([round(start, 3), round(start + L[k] + 0.1, 3), SUB[k]])
    return start + L[k] + tail


# ---- cold open: the tape comes off, the vinyl clings
ev["tape_teaser"] = 0.25
end = say(5, 0.4, 0.3)
shots.append([0.0, end, "teaser"])
ev["rewind"] = end
t = end + 1.65                      # 暗転＋巻き戻しの音＋ネオンのシリーズ名
shots.append([end, t, "black"])


def shot(name, k, lead=0.15, tail=0.15):
    global t
    s = t
    e = say(k, s + lead, tail)
    shots.append([round(s, 3), round(e, 3), name])
    t = e
    return s


ev["station"] = t
shot("station", 0, lead=0.3)
s = shot("phone", 1)
ev["side_cut"] = s + 0.15 + L[1] * 0.52   # 「傘は、」で横顔へ
s = shot("store", 2)
ev["door_chime"] = s + 0.4
s = shot("price", 3)
ev["genkan_cut"] = s + 0.15 + L[3] * 0.40  # 「玄関には、」で玄関へ
shot("lost", 4)
s = shot("tape", 5, lead=0.2)
ev["tape"] = s + 0.1
ev["open"] = t - 0.05
shot("face", 6, lead=0.35, tail=0.4)
ev["under"] = t
shot("under", 7, lead=0.2, tail=0.25)
shot("walk", 8, lead=0.2, tail=0.3)
ev["heels"] = t + 0.4
shots.append([t, t + 2.2, "woman"]); t += 2.2
ev["glance"] = t + 0.3
shots.append([t, t + 1.1, "eyes"]); t += 1.1
ev["outside"] = t
shots.append([t, t + 2.0, "flyer"]); t += 2.0
ev["resolve"] = t
shots.append([t, t + 1.0, "eyes"]); t += 1.0
ev["neon"] = t
ev["low"] = t + 0.65
shots.append([t, t + 3.2, "neon"]); t += 3.2

meta = json.loads((D / "episode.json").read_text())
tl = {"no": meta["no"], "title": meta["title"], "total": round(t, 3), "vo": vo, "shots": [[round(a, 3), round(b, 3), n] for a, b, n in shots],
      "events": [[k, round(v, 3)] for k, v in ev.items()], "subs": subs, "teaser_end": round(end, 3)}
(D / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1))
print("total", tl["total"])
