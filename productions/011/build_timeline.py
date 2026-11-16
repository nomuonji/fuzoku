"""#011 timeline: budget burn-off at the office; narrator writes the reasons afterwards."""
import json, pathlib, subprocess

D = pathlib.Path(__file__).resolve().parent
SPEED = 1.08
(D / "vo_fast").mkdir(exist_ok=True)

SUB = {
    0: "まだ使える椅子を、\n四十二脚、\n買い替えることになった。",
    1: "水曜の十七時四十分。\n会社の会議室だ。\n俺は、部の予算を管理している。",
    2: "課長が言った。\n「下期の予算が、あと\n百十一万七千円ある。\n十二月までに使い切ってくれ」",
    3: "いまの椅子は、去年買ったばかりで、\n壊れていない。\n新しい椅子は、\n一脚、二万六千六百円だ。",
    4: "それでも買うのは、\n使い切らないと、残りを\n会社に返すことになるからだ。",
    5: "返すと、来年のうちの部の予算は、\n返した分だけ減らされる。",
    6: "だから、先に金額が決まっていて、\n買う物は、あとから\n探すことになる。",
    7: "俺は、余りそうな月は、\n買う物の候補を、\n先にメモしておく。",
    8: "買う物が決まったら、\n俺が稟議書を書く。購入理由は、\n「座面の劣化により、業務効率に\n影響が出ているため」だ。",
    9: "古い椅子は、お金を払って、\n業者に引き取ってもらう。",
    10: "俺の仕事は、\nいらない物が要る理由を、\n書くことだ。",
    11: "課長は、理由の欄を\n読まずに、判を押した。",
    12: "赤い判の跡は、紙の上で、\nまだ少し濡れていた。",
    13: "稟議書を総務に出すと、\n受け取った女の人の指先が、\n一秒だけ、俺の指に触れた。",
    14: "あたたかい指だった。",
    15: "会社を出ると、\n十一月の風が、\n指先に冷たかった。"
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

shot("room", 1, lead=0.18, tail=0.16)
shot("budget", 2)
shot("chairs", 3)
shot("giveback", 4)
shot("shrink", 5)
shot("order", 6)
shot("memo", 7)
shot("ringi", 8)
shot("disposal", 9)
shot("punchline", 10, lead=0.22, tail=0.35)
s = shot("stamp", 11)
events.append(["stamp", round(s + 2.3, 3)])
shot("ink", 12)
shot("hand", 13)
shot("warm", 14)
s = shot("street", 15, tail=0.1)
events.append(["door", round(s + 0.1, 3)])

events.append(["heels", round(t + 0.35, 3)])
shots.append([round(t, 3), round(t + 2.1, 3), "woman"]); t += 1.5
events.append(["glance", round(t + 0.2, 3)])
shots.append([round(t, 3), round(t + 1.2, 3), "eyes"]); t += 1.2
events.append(["flyer", round(t, 3)])
shots.append([round(t, 3), round(t + 1.6, 3), "flyer"]); t += 1.0
events.append(["resolve", round(t, 3)])
shots.append([round(t, 3), round(t + 1.0, 3), "eyes"]); t += 0.8
events.append(["neon", round(t, 3)])
events.append(["low", round(t + 0.65, 3)])
shots.append([round(t, 3), round(t + 2.4, 3), "neon"]); t += 1.8

meta = json.loads((D / "episode.json").read_text())
timeline = {
    "no": meta["no"], "title": meta["title"], "total": round(t, 3),
    "vo": vo, "shots": shots, "events": events, "subs": subs,
    "teaser_end": round(max(3.0, teaser_end), 3), "main_start": round(main_start, 3),
    "opening_card": OPENING_CARD, "direct": DIRECT
}
(D / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1))
print("total", timeline["total"])
