"""#012 timeline: smell ad on the train home."""
import json, pathlib, subprocess

D = pathlib.Path(__file__).resolve().parent
SPEED = 1.08
(D / "vo_fast").mkdir(exist_ok=True)

SUB = {
    0: "自分の匂いが気になったのは、\n今夜の広告を見てからだった。",
    1: "木曜の二十一時四十分。\n帰りの電車で、\n俺は吊り革につかまっている。",
    2: "目の前の中吊りに、\n大きく書いてある。\n「その匂い、周りはもう\n気づいています」",
    3: "襟用の消臭シートの広告だ。\n三十枚入りで、六百八十円。",
    4: "俺はそっと、襟に鼻を寄せた。\n洗剤と、夕方の汗の匂いが、\n少しした。",
    5: "さっきまで\n気にもしていなかったのに、\nもう気になっている。",
    6: "広告は、まず不安を作る。\n気にする人が増えるほど、\n消臭シートは売れるからだ。",
    7: "誰が気づいているのかは、\n書いていない。書かなくても、\n客は周りを疑う。",
    8: "鞄には、もう二箱ある。\n去年の夏にも、\n同じ広告を見て買った。",
    9: "今夜も、駅前の薬局で、\n三箱目を買うつもりだ。",
    10: "一日座って働けば、\nシャツは汗をかく。\nその匂いを消す物を、帰りに買う。",
    11: "俺は、気にしなくてよかった匂いを、\n匂うほど働いた金で、\n消している。",
    12: "隣に、女の人が立った。\n髪から、石けんのような\n匂いがした。",
    13: "吊り革の手が、俺の手の隣にある。\n指先の体温が、\n伝わってくる気がした。",
    14: "俺は、襟が気になって、\n半歩、離れた。",
    15: "離れたのに、石けんの匂いは、\n駅を出ても\n鼻の先に残っていた。"
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

def shot(name, k, lead=0.12, tail=0.12):
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

shot("train", 1, lead=0.18, tail=0.16)
shot("ad", 2)
shot("pack", 3)
s = shot("sniff", 4)
events.append(["sniff", round(s + 0.9, 3)])
shot("doubt", 5)
shot("mech", 6)
shot("who", 7)
shot("bag", 8)
shot("third", 9)
shot("work", 10)
shot("punchline", 11, lead=0.22, tail=0.35)
shot("smell12", 12)
shot("hands", 13)
shot("step", 14)
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
