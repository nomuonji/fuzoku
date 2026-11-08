"""#005 timeline: 3-second cold open (the cold bottle, 滋養強壮), neon series title, then the story. No VO on the punchline.

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
    0: "二十二時五十一分。\n駅前のドラッグストアは、\nあと九分で閉まる。",
    1: "天井から、\n閉店の放送が\n流れている。",
    2: "レジの横の冷蔵ケースから、\n栄養ドリンクを一本取る。\n四百九十八円だ。",
    3: "明日の朝、\n会社に入る前に\n飲む分だ。",
    4: "ケースの瓶は、\n百五十八円から、\n九百八十円まである。",
    5: "俺は、疲れ具合で\n値段を選ぶ。\n今夜は、上から二番目だ。",
    6: "冷たい瓶のラベルに、\n滋養強壮と\n書いてある。",
    7: "「ポイントカードは\nお持ちですか」。\n俺は、アプリの\nバーコードを出す。",
    8: "これを飲んでも、\n疲れが消えるわけではない。\n明日の夕方まで、\n体がもつだけだ。",
    9: "体がもつから、\nまた働ける。\n働くから、また疲れて、\nこの店に来る。",
    10: "店も、それを分かっている。\nだから、このケースは、\nレジのすぐ横にある。",
    11: "会社は、\nこの四百九十八円を、\n一円も出さない。",
    12: "平日に毎晩買えば、\nひと月で\n一万円を超える。",
    13: "俺は、\n会社のために働く元気を、\n自分の給料で買っている。",
    14: "外に出ると、\nレジ袋の中で、\n瓶がひとつだけ冷たい。",
    15: "この元気を使うのは、\n明日の朝九時からの\n会社だ。",
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


# ---- cold open: the cold bottle, 滋養強壮 on the label
end = say(6, 0.35, 0.35)
shots.append([0.0, end, "teaser"])
ev["rewind"] = end
t = end + 1.65                      # 暗転＋巻き戻しの音＋ネオンのシリーズ名
shots.append([end, t, "black"])


def shot(name, k, lead=0.15, tail=0.12):
    global t
    s = t
    e = say(k, s + lead, tail)
    shots.append([round(s, 3), round(e, 3), name])
    t = e
    return s


s = shot("storefront", 0, lead=0.3)
ev["door"] = s + 0.2
s = shot("aisle", 1)
ev["announce"] = s + 0.1
s = shot("fridge", 2)
ev["case_open"] = s + 0.4
shot("sidebottle", 3)
shot("prices", 4)
s = shot("tracing", 5)
ev["trace"] = s + 0.15
shot("label", 6, lead=0.2)
s = shot("register", 7)
ev["beep"] = s + 0.15 + L[7] * 0.82
shot("face", 8, lead=0.3)
shot("side", 9)
shot("plan", 10)
s = shot("receipt", 11)
ev["print"] = s + 0.1
s = shot("stack", 12)
ev["stack"] = s
shot("distant", 13, lead=0.35, tail=0.4)
s = shot("shutter", 14, lead=0.2)
ev["shutter"] = s + 0.3
shot("walk", 15, tail=0.3)
ev["heels"] = t + 0.4
shots.append([t, t + 2.0, "woman"]); t += 2.0
ev["glance"] = t + 0.3
shots.append([t, t + 1.1, "eyes"]); t += 1.1
ev["outside"] = t
shots.append([t, t + 1.7, "flyer"]); t += 1.7
ev["resolve"] = t
shots.append([t, t + 1.0, "eyes"]); t += 1.0
ev["cap"] = t + 0.45
shots.append([t, t + 1.1, "cap"]); t += 1.1
ev["neon"] = t
ev["low"] = t + 0.65
shots.append([t, t + 3.2, "neon"]); t += 3.2

meta = json.loads((D / "episode.json").read_text())
tl = {"no": meta["no"], "title": meta["title"], "total": round(t, 3), "vo": vo, "shots": [[round(a, 3), round(b, 3), n] for a, b, n in shots],
      "events": [[k, round(v, 3)] for k, v in ev.items()], "subs": subs, "teaser_end": round(end, 3)}
(D / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1))
print("total", tl["total"])
