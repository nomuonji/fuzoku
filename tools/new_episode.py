"""新しい話の作業場所を作る。

    python tools/new_episode.py 002 biyoushitsu

productions/_template/ の台本・メタデータの雛形と、直近の話の画・音のコード
（build_timeline.py / scene.py / audio.py / render_frames.py）を複製する。
コードは「たたき台」で、場面ごとに書き換える前提。
"""
import pathlib, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
no, slug = sys.argv[1], sys.argv[2]
dst = ROOT / "productions" / no
if dst.exists():
    sys.exit(f"{dst} はもうある")
dst.mkdir(parents=True)
for f in (ROOT / "productions/_template").iterdir():
    (dst / f.name).write_text(f.read_text().replace("NO", no).replace("SLUG", slug))
# 画と音のコードは直近の話から複製する（variant の旗に対応した最新版。2026-11-13から）
prev = sorted(p for p in (ROOT / "productions").iterdir()
              if p.name.isdigit() and p != dst and (p / "scene.py").exists())[-1]
for f in ("build_timeline.py", "scene.py", "audio.py", "render_frames.py"):
    shutil.copy(prev / f, dst / f)
print(f"コードの複製元: {prev.name}")
voices = ROOT / f"docs/research/voices/{no}-{slug}.md"
if not voices.exists():
    voices.write_text(f"# #{no} {slug} — 生の声から学んだ感情の型\n\n> 引用・言い換え・エピソードの流用はしない。抽象化した型だけ残す。\n\n- \n")
print(f"作成: {dst.relative_to(ROOT)}  /  {voices.relative_to(ROOT)}")
print("次: script.md を書く → Yutoのチェック → lines.json → tools/vo.py → build_timeline.py と scene.py を場面に合わせて書き換え → tools/make.py")
