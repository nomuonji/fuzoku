"""#006 timeline: a receipt QR survey, five ratings, and the next-visit coupon. No spoken punchline."""
import json, pathlib, subprocess

D = pathlib.Path(__file__).resolve().parent
SPEED = 1.08
(D / "vo_fast").mkdir(exist_ok=True)

SUB = {
    0: "五問答えれば、\n次回は三十円引きだ。",
    1: "二十三時二十七分。\n俺は駅前の食堂で、\n千二百三十円の夕飯を食べた。",
    2: "レシートのQRから、\n店のアンケートに\n答えている。",
    3: "質問は五つ。\n味、料理の速さ、店内、\n接客、また来たいか。",
    4: "味は最高にした。\n料理の味は、\nもう思い出せない。",
    5: "接客も最高にした。\n店員とは、注文のときしか\n話していない。",
    6: "迷ったら、一番上を押す。\n早く終わるからだ。",
    7: "最後は、\n「また来たいですか」だった。",
    8: "俺は「はい」を押した。",
    9: "店は回答を集めて、\n料理や接客を直す所を\n探している。",
    10: "答えた客の意見を見て、\n次の営業のやり方を\n変える。",
    11: "アンケートが終わると、\n次回の割引が\n表示された。",
    12: "俺は三十円引きを使うために、\nまたこの店に来る。",
    13: "俺は三十円引きを受け取り、\n店は俺の感想と次の来店を\n受け取っている。",
    14: "俺はスマホをしまい、\n食器の返却口に\n皿を置いた。",
    15: "テーブルには、\n飲み残した水の輪が\n残っていた。",
    16: "外に出ると、雨の匂いに\n知らない女の香水が\n混じっていた。",
}

def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True
    ).stdout
    return float(out.strip())

L = {}
for k in SUB:
    src, dst = D / f"vo/{k}.wav", D / f"vo_fast/{k}.wav"
    if not src.exists():
        raise FileNotFoundError(f"missing voice: {src}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", f"atempo={SPEED}", str(dst)], check=True)
    L[k] = duration(dst)

vo, shots, subs, events = [], [], [], []
t = 0.0

def say(k, start, tail=0.22):
    vo.append([k, round(start, 3), round(L[k], 3)])
    subs.append([round(start, 3), round(start + L[k] + 0.12, 3), SUB[k]])
    return start + L[k] + tail

def shot(name, k, lead=0.16, tail=0.22):
    global t
    start = t
    end = say(k, start + lead, tail)
    shots.append([round(start, 3), round(end, 3), name])
    t = end
    return start

# The teaser is a short preview of the completed coupon.
teaser_end = say(0, 0.18, 0.12)
shots.append([0.0, round(max(3.0, teaser_end), 3), "teaser"])
events.append(["rewind", round(max(3.0, teaser_end), 3)])
t = max(3.0, teaser_end) + 1.55
shots.append([round(max(3.0, teaser_end), 3), round(t, 3), "black"])

shot("restaurant", 1, lead=0.18, tail=0.28)
s = shot("receipt", 2)
events.append(["qr", round(s + 0.5, 3)])
shot("questions", 3)
shot("foodrating", 4)
shot("service", 5)
s = shot("thumb", 6)
events.append(["tap_fast", round(s + L[6] * 0.55, 3)])
shot("return_question", 7)
s = shot("yes", 8)
events.append(["tap_yes", round(s + L[8] * 0.55, 3)])
shot("kitchen", 9)
shot("feedback", 10)
s = shot("coupon", 11)
events.append(["coupon", round(s + 0.4, 3)])
shot("save_coupon", 12)
shot("punchline", 13, lead=0.22, tail=0.6)
shot("return_plate", 14)
shot("water_ring", 15, tail=0.35)
shot("street", 16, tail=0.35)

events.append(["heels", round(t + 0.35, 3)])
shots.append([round(t, 3), round(t + 2.1, 3), "woman"]); t += 2.1
events.append(["glance", round(t + 0.2, 3)])
shots.append([round(t, 3), round(t + 1.2, 3), "eyes"]); t += 1.2
events.append(["flyer", round(t, 3)])
shots.append([round(t, 3), round(t + 1.8, 3), "flyer"]); t += 1.8
events.append(["resolve", round(t, 3)])
shots.append([round(t, 3), round(t + 1.0, 3), "eyes"]); t += 1.0
events.append(["neon", round(t, 3)])
events.append(["low", round(t + 0.65, 3)])
shots.append([round(t, 3), round(t + 3.2, 3), "neon"]); t += 3.2

meta = json.loads((D / "episode.json").read_text())
timeline = {
    "no": meta["no"], "title": meta["title"], "total": round(t, 3),
    "vo": vo, "shots": shots, "events": events, "subs": subs,
    "teaser_end": round(max(3.0, teaser_end), 3)
}
(D / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1))
print("total", timeline["total"])
