import json, os, pathlib, sys
from playwright.sync_api import sync_playwright
D = pathlib.Path(__file__).resolve().parent
N = int(json.loads((D / "timeline.json").read_text())["total"] * 30)
a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, N)
# 画は 1080x1920 で組み、SCALE 倍で撮る。既定 4/3 → 1440x2560（YouTubeが高画質の形式で配信する解像度）
SCALE = float(os.environ.get("SCALE", 4 / 3))
Q = int(os.environ.get("JPEG_Q", 95))
(D / "frames").mkdir(exist_ok=True)
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=SCALE)
    pg.goto((D / "ep.html").as_uri()); pg.wait_for_timeout(800)
    for i in range(a, min(b, N)):
        pg.evaluate(f"render({i/30})"); pg.screenshot(path=str(D / f"frames/{i:05d}.jpg"), type="jpeg", quality=Q)
    br.close()
