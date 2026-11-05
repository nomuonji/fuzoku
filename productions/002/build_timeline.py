"""#002 timeline: 3-second cold open (the shower stops), neon series title, then the story. No VO on the punchline.

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
    0: "二十三時四十一分。\nフロントの明かりは、\n二十二時で消えている。",
    1: "「QRコードを、\nかざしてください」。\n画面の中で、\n絵の女が頭を下げた。",
    2: "「おかえりなさいませ」。\n初めて泊まるホテルだ。",
    3: "この系列にするのは、\n誰とも目を合わせずに\n済むからだ。",
    4: "出てきたカードキーは、\nまだ機械の熱で温かい。",
    5: "枕は二つ。\n片方は、朝まで誰も使わない。",
    6: "隣の部屋で、\nシャワーの音が止まった。",
    7: "機械は、おかえりとは言う。\n誰も、待ってはいない。",
    8: "シーツは、糊が利いて冷たい。\n指に、もう温かさは\n残っていない。",
    9: "部屋を出た。\nエレベーターに、\n知らない女の香水が\n残っていた。",
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


# ---- cold open: the wall, the shower stops
ev["shower_teaser"] = 0.0
end = say(6, 0.5, 0.35)
ev["shower_stop_teaser"] = 0.5 + L[6] * 0.55
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


ev["lobby"] = t
shot("lobby", 0, lead=0.2)
s = shot("kiosk", 1)
ev["qr_beep"] = s + L[1] * 0.42
s = shot("welcome", 2, lead=0.1)
ev["chime"] = s + 0.05
shot("side", 3)
s = shot("card", 4)
ev["card_out"] = s + 0.1
ev["roomlight"] = t + 0.35
shot("room", 5, lead=0.4)
ev["shower"] = t
s = shot("wall", 6, lead=0.3, tail=0.25)
ev["shower_stop"] = s + 0.3 + L[6] * 0.55
shot("face", 7, lead=0.3, tail=0.4)
shot("sheet", 8, lead=0.1)
ev["elevator"] = t + 0.1
shot("elevator", 9, lead=0.35, tail=0.3)
ev["heels"] = t + 0.4
shots.append([t, t + 2.2, "woman"]); t += 2.2
ev["glance"] = t + 0.3
shots.append([t, t + 1.1, "eyes"]); t += 1.1
ev["outside"] = t
shots.append([t, t + 2.0, "flyer"]); t += 2.0
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
