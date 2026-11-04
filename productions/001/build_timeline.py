"""v5 timeline: 3-second cold open (the best moment), then the story. No VO on the punchline.

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
    1: "二十三時十四分。有人レジには、\nもう鎖が掛かっている。",
    2: "レモンサワーのロング缶と、\n二割引きの上から半額を\n重ね貼りされた焼き鳥。",
    3: "シールが貼られる時間は、\n知っている。",
    4: "昔は、釣り銭と一緒に、\n指先が一瞬だけ触れた。",
    5: "それだけで、\n一日でいちばん人肌に近かった。",
    6: "ランプが点くと、\n夜勤の女が小走りで来る。\n俺の手の横を、\n細い指が通り過ぎる。",
    7: "「大丈夫ですよ」。三秒で、\n彼女は戻っていった。",
    8: "次は、\nわざと間違えようかと思った。",
    9: "手間が省けた、と世の中は言う。",
    10: "省かれたのは、手間じゃない。\n手だ。",
    11: "自動ドアが開く。雨の匂いに、\n知らない女の香水が混じった。",
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


# ---- cold open: the clerk's fingers + the line that makes you stay
ev["alarm_teaser"] = 0.0
ev["clerkin_teaser"] = 0.0
end = say(8, 0.45, 0.25)
subs[-1][2] = "次は、わざと\n間違えようかと思った。"
shots.append([0.0, end, "teaser"])
ev["rewind"] = end
t = end + 1.25                      # 暗転＋巻き戻しの音＋シリーズ名（何の動画かをここで示す）
shots.append([end, t, "black"])

# ---- story
def shot(name, k, lead=0.15, tail=0.15):
    global t
    s = t
    e = say(k, s + lead, tail)
    shots.append([round(s, 3), round(e, 3), name])
    t = e

shot("four", 1)
shot("basket", 2)
shot("side", 3)
shot("coins", 4)
shot("bust", 5, tail=0.2)
ev["alarm"] = t + 0.1
shots.append([t, t + 1.0, "warn"]); t += 1.0
ev["clerkin"] = t + 0.1
shot("clerk", 6, lead=0.1)
ev["clerkout"] = t + 1.2
shot("clerk2", 7)
shot("face", 8, tail=0.25)
ev["printer"] = t
shot("receipt", 9, lead=0.1, tail=0.05)
shot("hand", 10, lead=0.1, tail=0.3)
ev["door"] = t + 0.1
shot("door", 11, lead=0.3, tail=0.4)
ev["heels"] = t + 0.4
shots.append([t, t + 2.2, "woman"]); t += 2.2
ev["glance"] = t + 0.3
shots.append([t, t + 1.1, "eyes"]); t += 1.1
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
