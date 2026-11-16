"""書き出したコマを、カット1枚ずつ並べた確認用の画像にする（目で確かめる用）。

    python tools/sheet.py productions/010            # → productions/010/sheet.jpg（.gitignore 対象）

make.py のあと（frames/ が残っているうち）に使う。各カットの真ん中の1コマを7列で並べる。
見るところは docs/factory.md「書き出しの確認」。
"""
import json, pathlib, sys
from PIL import Image

ep = pathlib.Path(sys.argv[1]).resolve()
tl = json.loads((ep / "timeline.json").read_text())
fps, W, H, COLS = 30, 270, 480, 7
picks = [(s[2], int(min((s[0] + s[1]) / 2, tl["total"] - 0.1) * fps)) for s in tl["shots"]]
rows = -(-len(picks) // COLS)
im = Image.new("RGB", (COLS * W, rows * H))
for i, (name, f) in enumerate(picks):
    p = ep / f"frames/{f:05d}.jpg"
    if not p.exists():
        sys.exit(f"{p} が無い。先に make.py を回す")
    im.paste(Image.open(p).resize((W, H)), ((i % COLS) * W, (i // COLS) * H))
out = ep / "sheet.jpg"
im.save(out, quality=85)
print(f"{out}  カット{len(picks)}  尺{tl['total']}秒  直接入り={tl.get('direct')}")
