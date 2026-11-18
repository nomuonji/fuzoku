"""#013 timeline: earbud battery dies on the train home."""
import json, pathlib, subprocess

D = pathlib.Path(__file__).resolve().parent
SPEED = 1.08
(D / "vo_fast").mkdir(exist_ok=True)

SUB = {
    0: "左の耳から、\nラジオの女の人の声が、\n消えた。",
    1: "火曜の二十二時十八分。\n帰りの電車で、俺は、\n深夜のラジオを聴いている。",
    2: "二年二か月前に、\n一万四千八百円で買ったイヤホン。\nその左の電池が、切れた。",
    3: "電池は、使うほど弱る。",
    4: "ただ、このイヤホンの電池は、\n客には替えられない。",
    5: "メーカーに送れば、\n電池の交換は八千二百円。\n新品は、一万四千八百円だ。",
    6: "その値段なら、\n新品を買う人が多い。\n値段を決める人も、\nそれは分かっている。",
    7: "引き出しには、\n電池の切れたイヤホンが、\nもう二つある。",
    8: "うちの会社の製品も同じだ。\n先月、その仕様の確認欄に、\n俺が判を押した。",
    9: "物が壊れる日は、\n次の売上の日として、\nはじめから予定に入っている。",
    10: "俺はその予定の中で、\n給料をもらって、\n予定どおりに買っている。",
    11: "右の耳には、まだ低い声が残っている。\n耳のすぐそばで、\n息をするような声だ。",
    12: "電池を替えられれば、\n声は、左にも戻ってくる。",
    13: "替えられないから、\n新品が届くまで、左は静かだ。",
    14: "隣に女の人が立った。\n吊り革を握る手の隣から、\n石けんの匂いが、した。",
    15: "電池も、新品も要らない体温が、\n俺の手の隣にあった。"
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
shot("dead", 2)
events.append(["cut", round(shots[-1][0] + 0.2, 3)])
shot("fade", 3)
shot("lock", 4)
shot("mech", 5)
shot("choose", 6)
shot("drawer", 7)
shot("stampdoc", 8)
events.append(["stamp", round(shots[-1][0] + 1.6, 3)])
shot("punchline", 9, lead=0.22, tail=0.35)
shot("plan", 10)
shot("rightear", 11)
shot("leftear", 12)
shot("silent", 13)
shot("smell12", 14)
s = shot("warm", 15, tail=0.1)
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
