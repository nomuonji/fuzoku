"""#007 timeline: a train ride watching "how to quit your phone" videos, ads and autoplay. No spoken punchline."""
import json, pathlib, subprocess

D = pathlib.Path(__file__).resolve().parent
SPEED = 1.08
(D / "vo_fast").mkdir(exist_ok=True)

SUB = {
    0: "スマホをやめる方法の動画は、\n五秒の広告から始まった。",
    1: "二十三時三十二分。\n俺は帰りの電車で、\n「スマホをやめる方法」\nという動画を見ている。",
    2: "さっき、スマホの\n使用時間の通知が\n来たからだ。",
    3: "一日平均、五時間四十八分。\n先週より、\n十二パーセント増えていた。",
    4: "動画は十二分。\n始まる前に、\n五秒の広告が流れた。",
    5: "俺は一・五倍速にして、\n最後まで見た。",
    6: "終わると、次の動画が\n勝手に始まった。\n「寝る前のスマホをやめる、\nたった一つの習慣」。",
    7: "それも、最後まで見た。",
    8: "この動画アプリは、\n無料で見られる。\nその代わりに、広告が流れる。",
    9: "客が長く見るほど\n広告が多く流れて、\nアプリと動画を作った人に\n金が入る。",
    10: "だからアプリは、\n客が長く見る動画を、\n次から次へと出してくる。",
    11: "スマホをやめたい人は多いから、\nやめる方法の動画も\nよく見られる。",
    12: "俺がやめる方法を\n見ている間も、広告は\n同じように流れている。",
    13: "スマホをやめる方法を\n見ている時間も、\nアプリの売上になっている。",
    14: "電車を降りた。\n今日いちばん長く\n触っていたのは、この画面だ。",
    15: "指先に、まだ\n画面の熱が残っている。",
    16: "改札を出ると、\n知らない女の香水の\n匂いがした。",
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

# The teaser: the quit-your-phone video opening on an ad.
teaser_end = say(0, 0.18, 0.12)
shots.append([0.0, round(max(3.0, teaser_end), 3), "teaser"])
events.append(["rewind", round(max(3.0, teaser_end), 3)])
t = max(3.0, teaser_end) + 1.55
shots.append([round(max(3.0, teaser_end), 3), round(t, 3), "black"])

shot("train", 1, lead=0.18, tail=0.28)
s = shot("notify", 2)
events.append(["notif", round(s + 0.3, 3)])
shot("report", 3)
s = shot("preroll", 4)
events.append(["ad", round(s + L[4] * 0.45, 3)])
s = shot("speed", 5)
events.append(["tap_fast", round(s + L[5] * 0.3, 3)])
s = shot("autoplay", 6)
events.append(["autoplay", round(s + 0.5, 3)])
shot("watching", 7)
shot("free", 8)
shot("money", 9)
shot("feed", 10)
shot("thumbs", 11)
shot("adloop", 12)
shot("punchline", 13, lead=0.22, tail=0.6)
s = shot("platform", 14)
events.append(["door", round(s + 0.2, 3)])
shot("finger", 15, tail=0.35)
shot("street", 16, tail=0.35)

events.append(["heels", round(t + 0.35, 3)])
shots.append([round(t, 3), round(t + 2.1, 3), "woman"]); t += 2.1
events.append(["glance", round(t + 0.2, 3)])
shots.append([round(t, 3), round(t + 1.2, 3), "eyes"]); t += 1.2
events.append(["flyer", round(t, 3)])
shots.append([round(t, 3), round(t + 1.6, 3), "flyer"]); t += 1.6
events.append(["resolve", round(t, 3)])
shots.append([round(t, 3), round(t + 1.0, 3), "eyes"]); t += 1.0
events.append(["neon", round(t, 3)])
events.append(["low", round(t + 0.65, 3)])
shots.append([round(t, 3), round(t + 3.0, 3), "neon"]); t += 3.0

meta = json.loads((D / "episode.json").read_text())
timeline = {
    "no": meta["no"], "title": meta["title"], "total": round(t, 3),
    "vo": vo, "shots": shots, "events": events, "subs": subs,
    "teaser_end": round(max(3.0, teaser_end), 3)
}
(D / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1))
print("total", timeline["total"])
