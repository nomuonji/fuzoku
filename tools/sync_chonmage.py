"""公開済みの話を chonmage-ja の /souda/ に載せる。

    python tools/sync_chonmage.py ../chonmage-ja

productions/*/episode.json のうち status が ready / published の話を
（youtube_id が入っていれば埋め込み、無ければ「近日公開」として）
chonmage-ja/src/data/souda-episodes.json に書き出し、still.jpg を
chonmage-ja/public/souda/<no>.jpg に複製する。そのあと chonmage-ja 側で build → push。

YouTube 側から chonmage-ja へリンクは張らない（AGENTS.md「公開と誘導」）。
つながりは、こちら（chonmage-ja）から YouTube への一方向だけ。
"""
import json, pathlib, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
site = pathlib.Path(sys.argv[1]).resolve()
eps = []
for m in sorted(ROOT.glob("productions/[0-9]*/episode.json")):
    e = json.loads(m.read_text())
    if e.get("status") not in ("ready", "published") and not e.get("youtube_id"):
        continue
    still = m.parent / "still.jpg"
    img = ""
    if still.exists():
        (site / "public/souda").mkdir(parents=True, exist_ok=True)
        shutil.copy(still, site / f"public/souda/{e['no']}.jpg")
        img = f"/souda/{e['no']}.jpg"
    eps.append({k: e.get(k, "") for k in ("no", "title", "scene", "line", "escape", "youtube_id", "published")} | {"still": img})
out = site / "src/data/souda-episodes.json"
out.write_text(json.dumps(eps, ensure_ascii=False, indent=2) + "\n")
print(f"{len(eps)}話 → {out}")
