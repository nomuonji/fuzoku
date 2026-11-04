import json, pathlib, sys
from playwright.sync_api import sync_playwright
D = pathlib.Path(__file__).resolve().parent
N = int(json.loads((D / "timeline.json").read_text())["total"] * 30)
a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, N)
(D / "frames").mkdir(exist_ok=True)
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto((D / "ep001.html").as_uri()); pg.wait_for_timeout(800)
    for i in range(a, min(b, N)):
        pg.evaluate(f"render({i/30})"); pg.screenshot(path=str(D / f"frames/{i:05d}.jpg"), type="jpeg", quality=90)
    br.close()
