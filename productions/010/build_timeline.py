"""#010 timeline: Sunday afternoon at a discount pile of the narrator's own company's fans. No spoken punchline."""
import json, pathlib, subprocess

D = pathlib.Path(__file__).resolve().parent
SPEED = 1.08
(D / "vo_fast").mkdir(exist_ok=True)

SUB = {
    0: "俺の会社の扇風機が、\n三百九十八円で、\n山になっていた。",
    1: "日曜の十六時四十分。\n郊外の量販店の、\n通路の端だ。",
    2: "「在庫一掃」の札の下に、\n首にかける扇風機の箱が、\n積んである。",
    3: "定価は二千九百八十円。\n去年の夏に出した、\nうちの会社の製品だ。",
    4: "いまは十一月だ。\nそれでも客は、安いからと、\n箱をカゴに入れていく。",
    5: "俺は会社で、売上の集計をしている。\nこの山がここにある理由も、\n数字で知っている。",
    6: "うちの売上は、\n店に納めた日に立つ。\n客が買った日ではない。",
    7: "売れ残った分は、店が\n札を貼り替えて、安く売り切る。\n売り切れば、店はまた注文をくれる。",
    8: "買った客の家では、扇風機は\n来年の夏まで、押し入れに\nしまわれたままになる。\n使われなくても、売上は売上だ。",
    9: "その売上から、\n俺の給料が出ている。",
    10: "俺の給料は、\n誰かがいらないのに買った物で、\nできている。",
    11: "俺は、一番上の箱の札が\n見えるように、向きを直した。\nそれから、自分でも一台、\nカゴに入れた。",
    12: "家には、もう二台ある。",
    13: "レジを待つ間、\nカゴの箱が、\n手の甲に冷たかった。",
    14: "前に並んでいた\n女の人の、コートから、\n石けんの匂いがした。",
    15: "外に出ると、\n駐車場は、もう暗かった。"
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

shot("aisle", 1, lead=0.18, tail=0.28)
shot("pile", 2)
shot("tag", 3)
shot("nov", 4)
shot("sheet", 5)
shot("day", 6)
shot("chain", 7)
shot("closet", 8)
shot("pay", 9)
shot("punchline", 10, lead=0.22, tail=0.45)
shot("fix", 11)
shot("home", 12)
s = shot("queue", 13)
events.append(["beep", round(s + 1.9, 3)])
shot("scent", 14)
s = shot("lot", 15, tail=0.1)
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
