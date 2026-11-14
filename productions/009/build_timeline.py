"""#009 timeline: a Saturday night scrolling a shopping app, nothing wanted. No spoken punchline."""
import json, pathlib, subprocess

D = pathlib.Path(__file__).resolve().parent
SPEED = 1.08
(D / "vo_fast").mkdir(exist_ok=True)

SUB = {
    0: "一時間も画面を触り続けて、\n触りたい物は、一つもなかった。",
    1: "土曜の二十二時十二分。\nベッドで、通販アプリを開いた。\n欲しい物は、特にない。",
    2: "給料は先週入った。金はある。\n親指で、おすすめを\n下へ送っていく。",
    3: "腕時計、加湿器、ケーブルバンド。\nどれも嫌ではないが、\n欲しくもない。",
    4: "欲しい物リストには、\n去年から十一個入っている。\n理由は、もう思い出せない。",
    5: "カートに入れては、戻した。\n三回やった。",
    6: "二十三時十五分。\n九百八十円の\nケーブルバンドを注文した。\nまとめるケーブルは、家に二本だ。",
    7: "おすすめの欄は、\n俺が前に見た物から、\n次に売れそうな物を\n選んで並べている。",
    8: "俺は、並んだ物を見て、\nこれが欲しかったのかもしれない、\nと思う。そして買う。",
    9: "並んだ中に欲しい物が\n一つもない夜は、\n俺は何も買えず、\n店も何も売れない。",
    10: "それでは、お互いに困る。\nだから俺は、欲しくない物を買う。\n九百八十円は、その夜を\n終わらせる値段だ。",
    11: "俺の欲しい物は、\n画面に並んだ物の中にしか、\nなかった。",
    12: "画面を消すと、部屋が暗くなった。\n親指だけが、まだ温かかった。",
    13: "眠れなくて、\n上着を着て外に出た。",
    14: "夜の路地で、\n知らない女の香水の\n匂いがした。"
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

shot("bed", 1, lead=0.18, tail=0.28)
s = shot("scroll", 2)
events.append(["swipe", round(s + 0.3, 3)])
shot("items", 3)
shot("wish", 4)
s = shot("cart", 5, tail=0.3)
events.append(["tap", round(s + 0.5, 3)])
s = shot("order", 6)
events.append(["confirm", round(s + 1.6, 3)])
shot("reco", 7)
shot("seen", 8)
shot("both", 9)
shot("price", 10)
shot("punchline", 11, lead=0.22, tail=0.45)
shot("dark", 12)
s = shot("outside", 13)
events.append(["door", round(s + 0.1, 3)])
shot("street", 14, tail=0.1)

events.append(["heels", round(t + 0.35, 3)])
shots.append([round(t, 3), round(t + 2.1, 3), "woman"]); t += 1.7
events.append(["glance", round(t + 0.2, 3)])
shots.append([round(t, 3), round(t + 1.2, 3), "eyes"]); t += 1.2
events.append(["flyer", round(t, 3)])
shots.append([round(t, 3), round(t + 1.6, 3), "flyer"]); t += 1.2
events.append(["resolve", round(t, 3)])
shots.append([round(t, 3), round(t + 1.0, 3), "eyes"]); t += 1.0
events.append(["neon", round(t, 3)])
events.append(["low", round(t + 0.65, 3)])
shots.append([round(t, 3), round(t + 2.4, 3), "neon"]); t += 2.1

meta = json.loads((D / "episode.json").read_text())
timeline = {
    "no": meta["no"], "title": meta["title"], "total": round(t, 3),
    "vo": vo, "shots": shots, "events": events, "subs": subs,
    "teaser_end": round(max(3.0, teaser_end), 3), "main_start": round(main_start, 3),
    "opening_card": OPENING_CARD, "direct": DIRECT
}
(D / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1))
print("total", timeline["total"])
