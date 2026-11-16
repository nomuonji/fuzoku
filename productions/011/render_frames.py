import json, os, pathlib, sys
from playwright.sync_api import sync_playwright

D = pathlib.Path(__file__).resolve().parent
N = int(json.loads((D / "timeline.json").read_text())["total"] * 30)
a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, N)
SCALE = float(os.environ.get("SCALE", 4 / 3))
Q = int(os.environ.get("JPEG_Q", 95))
(D / "frames").mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=SCALE)
    page.goto((D / "ep.html").as_uri())
    page.wait_for_timeout(800)
    for frame in range(a, min(b, N)):
        page.evaluate(f"render({frame / 30})")
        page.screenshot(path=str(D / f"frames/{frame:05d}.jpg"), type="jpeg", quality=Q)
    browser.close()
