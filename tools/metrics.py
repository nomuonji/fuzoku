"""YouTube Studio の数字を話ごとに記録し、実験（docs/experiments.md）の比較表を作る。

    # Studio の数字を貼り付けて記録（手入力。Studio の Analytics API は使えないため）
    python tools/metrics.py add 007 --window 48h --views 77 --hours 0.2 --feed 72 --stayed 40 --subs 0
    python tools/metrics.py table            # 比較表を表示
    python tools/metrics.py table --write    # docs/experiments.md の表（マーカー間）を書き換える

記録先は productions/<話数>/metrics.json（配列。追記のみ。消さない）。
  --views  視聴回数            --hours  総再生時間（時間）
  --feed   Shorts フィード経由の視聴回数
  --stayed 「視聴を続けた割合」%（Studio のエンゲージメントタブ）
  --avgpct 平均視聴率 %（平均視聴時間 ÷ 動画の長さ）   --subs  登録者の増減
  --window 計測の窓（48h / 7d / snapshot など）。話どうしを比べるときは同じ窓だけを使う
平均視聴秒数は hours×3600÷views で計算する（Studio の hours は小数1桁なので粗い目安）。
"""
import argparse, datetime, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "productions"
DOC = ROOT / "docs/experiments.md"
BEGIN, END = "<!-- metrics-table:begin -->", "<!-- metrics-table:end -->"


def load(no):
    f = P / no / "metrics.json"
    return json.loads(f.read_text()) if f.exists() else []


def episode(no):
    d = P / no
    meta = json.loads((d / "episode.json").read_text()) if (d / "episode.json").exists() else {}
    tl = json.loads((d / "timeline.json").read_text()) if (d / "timeline.json").exists() else {}
    shots = [s[2] for s in tl.get("shots", [])]
    return {
        "no": no, "title": meta.get("title", ""),
        "length": round(tl.get("total", 0), 1),
        "card": ("black" in shots) if shots else None,
        "exp": meta.get("variant", {}).get("experiment", "-"),
    }


def table(window):
    rows = ["| 話 | 題 | 尺(秒) | 冒頭カード | 実験 | 窓 | 視聴 | フィード% | 平均視聴(秒) | 平均視聴率 | 視聴を続けた% | 登録 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for d in sorted(p.name for p in P.iterdir() if p.is_dir() and re.fullmatch(r"\d{3}", p.name)):
        e = episode(d)
        ms = [m for m in load(d) if window in (None, m.get("window"))]
        for m in ms or [None]:
            v = m.get("views") if m else None
            avg = round(m["hours"] * 3600 / v, 1) if m and m.get("hours") is not None and v else None
            apct = m.get("avgpct") if m and m.get("avgpct") is not None else (
                round(avg / e["length"] * 100) if avg and e["length"] else None)
            feed = round(m["feed"] / v * 100) if m and m.get("feed") is not None and v else None
            f = lambda x: "-" if x is None else x
            rows.append(f"| {d} | {e['title']} | {e['length'] or '-'} | {'あり' if e['card'] else ('なし' if e['card'] is False else '-')} | {e['exp']} | "
                        f"{f(m.get('window') if m else None)} | {f(v)} | {f(feed)} | {f(avg)} | {f(apct)} | {f(m.get('stayed') if m else None)} | {f(m.get('subs') if m else None)} |")
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("no"); a.add_argument("--window", required=True)
    a.add_argument("--views", type=int, required=True)
    a.add_argument("--hours", type=float); a.add_argument("--feed", type=int)
    a.add_argument("--stayed", type=float); a.add_argument("--avgpct", type=float)
    a.add_argument("--subs", type=int); a.add_argument("--note", default="")
    t = sub.add_parser("table")
    t.add_argument("--window"); t.add_argument("--write", action="store_true")
    args = ap.parse_args()
    if args.cmd == "add":
        rec = {k: v for k, v in vars(args).items() if k not in ("cmd", "no") and v not in (None, "")}
        rec["recorded"] = datetime.date.today().isoformat()
        f = P / args.no / "metrics.json"
        data = load(args.no) + [rec]
        f.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
        print(f"記録: {f.relative_to(ROOT)}  {rec}")
    else:
        out = table(args.window)
        if args.write:
            s = DOC.read_text()
            if BEGIN not in s:
                sys.exit(f"{DOC} に {BEGIN} がない")
            s = re.sub(re.escape(BEGIN) + ".*?" + re.escape(END), BEGIN + "\n" + out + "\n" + END, s, flags=re.S)
            DOC.write_text(s); print("docs/experiments.md を更新")
        else:
            print(out)


main()
