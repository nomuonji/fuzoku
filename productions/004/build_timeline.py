"""#004 timeline: 3-second cold open (the film stopped as she takes off her coat), neon series title, then the story. No VO on the punchline.

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
    0: "二十三時四十八分。\nホームで、\nスマホが震えた。",
    1: "「お支払いが\n完了しました」。\n月額、九百九十円。",
    2: "続きから再生。\n最後に開いたのは、\n七月だ。",
    3: "女がコートを\n脱ぐところで、\n止めたままだ。",
    4: "解約の画面までは、\n指が覚えている。\n三回目だ。",
    5: "「三十七作品が、\n削除されます」。\n指が、戻るを押した。",
    6: "見ない映画に、\n払っているんじゃない。\n休みの日に見る、\nいつかの俺の分だ。",
    7: "そいつが来ないように、\n平日の俺が、\n働いている。",
    8: "向こうも知っている。\n来ない客ほど、\n安くつく。",
    9: "働いた給料で、\n来ない休みを、\n毎月買っている。",
    10: "払った時間を、\n最後まで使い切ったことが、\n一度もない。",
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


# ---- cold open: the film stopped where she takes off her coat
end = say(3, 0.35, 0.35)
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


s = shot("platform", 0, lead=0.3)
ev["buzz"] = s + 0.15 + L[0] * 0.8      # 「震えた」
s = shot("notify", 1)
ev["notify"] = s + 0.05
shot("app", 2)
shot("film", 3, lead=0.2)
s = shot("settings", 4)
ev["taps"] = s + 0.5
s = shot("confirm", 5)
ev["back_tap"] = s + 0.15 + L[5] * 0.86
shot("face", 6, lead=0.4)
s = shot("side", 7)
ev["train"] = s
shot("grid", 8)
shot("distant", 9, lead=0.35, tail=0.45)
shot("bench", 10, lead=0.2, tail=0.3)
ev["heels"] = t + 0.4
shots.append([t, t + 2.0, "woman"]); t += 2.0
ev["glance"] = t + 0.3
shots.append([t, t + 1.1, "eyes"]); t += 1.1
ev["outside"] = t
shots.append([t, t + 1.9, "flyer"]); t += 1.9
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
