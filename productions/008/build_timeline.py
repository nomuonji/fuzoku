"""#008 timeline: a late office, a 4-minute macro run, and the next job arriving. No spoken punchline."""
import json, pathlib, subprocess

D = pathlib.Path(__file__).resolve().parent
SPEED = 1.08
(D / "vo_fast").mkdir(exist_ok=True)

SUB = {
    0: "四分で終わった仕事の後に、\n次の仕事が届いた。",
    1: "十九時五十八分。\n会社の席で、月末の\n売上集計を終えた。\nかかった時間は、四分だ。",
    2: "以前は二時間四十分かかった。\n残業中に、\n自分でマクロを組んだ。",
    3: "今日は早く帰れる。\nネクタイを緩めて、\n椅子にもたれた。",
    4: "課長からチャットが来た。\n「早いね。ついでに、\n先月との比較表を、\n明日の朝までに」。",
    5: "その表は毎月作っているが、\n読む人を、\n俺は見たことがない。",
    6: "俺は「承知しました」と返した。\n比較表には、二時間かかった。",
    7: "会社を出たのは、二十二時二分。\n帰る時間は、\nいつもと同じだった。",
    8: "会社は、一人が一日に\nこなせる量を見て、\n人数と給料を決めている。",
    9: "俺が速くなると、\n同じ給料のまま、\nこなせる量が増えたことになる。",
    10: "空いた時間は、俺のものにはならない。\n次の仕事を入れていい時間として、\n数えられる。",
    11: "入れられる仕事は、\n読む人のいない比較表のような\nものだ。",
    12: "速くなる工夫をしたのも、\n空いた時間を埋める仕事を\n引き受けたのも、俺だ。",
    13: "俺が作った時間は、\n会社の次の仕事に使われる。",
    14: "ビルを出ると、夜風が、\n首筋の汗を冷やした。",
    15: "駅へ歩く途中、\n知らない女の香水の\n匂いがした。"
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

def say(k, start, tail=0.16):
    vo.append([k, round(start, 3), round(L[k], 3)])
    subs.append([round(start, 3), round(start + L[k] + 0.12, 3), SUB[k]])
    return start + L[k] + tail

def shot(name, k, lead=0.14, tail=0.16):
    global t
    start = t
    end = say(k, start + lead, tail)
    shots.append([round(start, 3), round(end, 3), name])
    t = end
    return start

# 実験フラグ（docs/experiments.md）。episode.json の variant で冒頭の作りを切り替える。
#   opening = "direct"   … 先出しの一言から巻き戻し・暗転・シリーズ名カードなしで本編へ続ける（E1、2026-11-13〜）
#   opening_card = false … 先出しのあと、シリーズ名カードを出さず短い暗転だけで本編へ（旧E2案）
#   どちらも無いとき       … 従来（先出し→巻き戻し→シリーズ名カード→本編。#001〜#008 の再現のため）
# 実測（api-d2の維持率）：離脱は先出し→カード→本編の切り替わり5〜10秒に集中していた。
_meta = json.loads((D / "episode.json").read_text())
_var = _meta.get("variant", {})
DIRECT = _var.get("opening") == "direct"
OPENING_CARD = False if DIRECT else _var.get("opening_card", True)

# The teaser: the strongest line first.
teaser_end = say(0, 0.18, 0.12)
if DIRECT:
    t = teaser_end + 0.12
    shots.append([0.0, round(t, 3), "teaser"])
else:
    shots.append([0.0, round(max(3.0, teaser_end), 3), "teaser"])
    events.append(["rewind", round(max(3.0, teaser_end), 3)])
    if OPENING_CARD:
        t = max(3.0, teaser_end) + 1.4
        shots.append([round(max(3.0, teaser_end), 3), round(t, 3), "black"])
    else:
        t = max(3.0, teaser_end) + 0.3
        shots.append([round(max(3.0, teaser_end), 3), round(t, 3), "cut"])
main_start = t

shot("desk", 1, lead=0.18, tail=0.28)
s = shot("old", 2)
events.append(["keys", round(s + 0.2, 3)])
shot("loosen", 3)
s = shot("chat", 4)
events.append(["notif", round(s + 0.25, 3)])
shot("table", 5)
shot("reply", 6)
s = shot("exit", 7)
shot("firm", 8)
shot("faster", 9)
shot("empty", 10)
shot("unread", 11)
shot("mine", 12)
shot("punchline", 13, lead=0.22, tail=0.45)
s = shot("outside", 14)
events.append(["door", round(s + 0.1, 3)])
shot("street", 15, tail=0.35)

events.append(["heels", round(t + 0.35, 3)])
shots.append([round(t, 3), round(t + 2.1, 3), "woman"]); t += 1.9
events.append(["glance", round(t + 0.2, 3)])
shots.append([round(t, 3), round(t + 1.2, 3), "eyes"]); t += 1.2
events.append(["flyer", round(t, 3)])
shots.append([round(t, 3), round(t + 1.6, 3), "flyer"]); t += 1.4
events.append(["resolve", round(t, 3)])
shots.append([round(t, 3), round(t + 1.0, 3), "eyes"]); t += 1.0
events.append(["neon", round(t, 3)])
events.append(["low", round(t + 0.65, 3)])
shots.append([round(t, 3), round(t + 2.4, 3), "neon"]); t += 2.4

meta = json.loads((D / "episode.json").read_text())
timeline = {
    "no": meta["no"], "title": meta["title"], "total": round(t, 3),
    "vo": vo, "shots": shots, "events": events, "subs": subs,
    "teaser_end": round(max(3.0, teaser_end), 3), "main_start": round(main_start, 3),
    "opening_card": OPENING_CARD, "direct": DIRECT
}
(D / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1))
print("total", timeline["total"])
